import json
from time import perf_counter

import streamlit as st
from snowflake.core import Root
from snowflake.snowpark.context import get_active_session

from incident import (
    COHORT_SQL, COMPLETION_SQL, MODEL, QUESTIONS, SEARCH_LIMIT,
    build_prompt, validate_brief,
)

st.set_page_config(page_title="Launch-day mystery", layout="wide")
st.title("Launch-day mystery")
st.caption("Synthetic retail incident · June 4, 2026 · All times UTC")
st.write("Orders fell on launch morning. Should the incident lead roll back the iOS checkout change?")

session = get_active_session()
try:
    metrics = [row.as_dict() for row in session.sql(COHORT_SQL).collect()]
except Exception as error:
    st.error("Could not load checkout metrics. Check the app role and demo setup.")
    with st.expander("Snowflake error"):
        st.text(str(error))
    st.stop()

if not metrics:
    st.error("Checkout metrics are empty. Run the seed script.")
    st.stop()

before = sum(row["ORDERS"] for row in metrics if row["RELEASE_PHASE"] == "Before")
after = sum(row["ORDERS"] for row in metrics if row["RELEASE_PHASE"] == "After")
before_sessions = sum(row["SESSIONS"] for row in metrics if row["RELEASE_PHASE"] == "Before")
after_sessions = sum(row["SESSIONS"] for row in metrics if row["RELEASE_PHASE"] == "After")
summary = st.columns(3)
summary[0].metric("Orders · 09:00–10:00", f"{before:,}")
summary[1].metric(
    "Orders · 10:00–11:00", f"{after:,}",
    f"{(after - before) / before:+.0%}" if before else None,
)
summary[2].metric("Sessions · 10:00–11:00", f"{after_sessions:,}", f"{after_sessions - before_sessions:+,}")

funnel, investigation = st.tabs(["Checkout funnel", "Investigate"])
with funnel:
    st.dataframe(metrics, hide_index=True, use_container_width=True)
    st.caption("Completion is orders divided by checkout starts. Compare the same cohort before and after.")
    with st.expander("Inspect funnel SQL"):
        st.code(COHORT_SQL.strip(), language="sql")

with investigation:
    case = st.selectbox("Investigation", list(QUESTIONS))
    question = QUESTIONS[case]
    st.write(question)
    if st.button("Run investigation", type="primary"):
        st.session_state.pop("investigation", None)
        started = perf_counter()
        try:
            with st.spinner("Retrieving incident notes and drafting a brief…"):
                service = Root(session).databases["LAUNCH_MYSTERY"].schemas["DEMO"].cortex_search_services["INCIDENT_SEARCH"]
                notes = service.search(
                    query=question, columns=["DOC_ID", "TITLE", "BODY"], limit=SEARCH_LIMIT,
                ).results
                st.session_state["investigation"] = {"case": case, "notes": notes}
                prompt = build_prompt(question, metrics, notes)
                raw = session.sql(COMPLETION_SQL, params=[MODEL, prompt]).collect()[0][0]
                output = json.loads(raw) if isinstance(raw, str) else raw
                brief = validate_brief(output, notes, requires_citation=case != "Missing evidence")
                st.session_state["investigation"].update(
                    brief=brief, elapsed=perf_counter() - started,
                )
        except Exception as error:
            st.error("The investigation could not produce a verified brief.")
            with st.expander("Details"):
                st.text(str(error))

    result = st.session_state.get("investigation")
    if result and result["case"] == case:
        brief = result.get("brief")
        if brief:
            st.subheader("Assessment")
            st.text(brief["assessment"])
            st.subheader("Next check")
            st.text(brief["next_check"])
            for citation in brief["citations"]:
                st.text(f'{citation["doc_id"]} · “{citation["quote"]}”')
            st.caption(f'Cortex Search + {MODEL} · {result["elapsed"]:.1f}s')
        with st.expander("Inspect retrieved evidence"):
            for note in result["notes"]:
                st.text(f'{note["DOC_ID"]} · {note["TITLE"]}')
                st.text(note["BODY"])
            if not result["notes"]:
                st.write("Cortex Search returned no notes.")
