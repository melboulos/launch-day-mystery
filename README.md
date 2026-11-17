# Launch-Day Mystery

A Snowflake-native AI demo that investigates an 18% launch-day order drop using Cortex Analyst, Cortex Search, and a source-cited incident brief in Streamlit.

It's June 4, 2026. A fictional retailer has just shipped a checkout update. Orders fell from 1,000 to 820 while traffic stayed at 7,000 sessions per hour. The incident lead has to decide whether to disable the feature flag.

## What runs where

| Snowflake product | Role |
|---|---|
| Snowflake SQL | Calculates the checkout funnel from synthetic shopper events |
| Semantic Views and Cortex Analyst | Support natural-language drill-down in Snowsight |
| Cortex Search | Retrieves release notes, operational telemetry, and provider alerts |
| Cortex AI SQL | Generates a structured assessment and next check with source quotes |
| Streamlit in Snowflake | Hosts the funnel and incident investigation |

The seed defines eight cohort-hour targets. Snowflake expands them into synthetic storefront sessions, checkout starts, orders, and observed address-validation timeouts. The app and Cortex Analyst read the event-derived funnel. Each event has a timestamp and session ID, so you can trace a single checkout.

The Streamlit app uses fixed funnel SQL so that every brief starts with the same metrics. Cortex Analyst is a separate live step in Snowsight. The Python code checks each quote against the retrieved source text. You can expand the retrieved notes and assess whether the quotes support the model's claims.

## Deploy

Use a Snowflake account with Cortex Search, Cortex Analyst, and Streamlit available. Configure a [Snowflake CLI connection](https://docs.snowflake.com/en/developer-guide/snowflake-cli/connecting/configure-connections) with a role authorized to create the demo database and warehouse and use the Cortex features. Confirm your account and role support `claude-haiku-4-5` before the live demo. See the [Cortex AI access documentation](https://docs.snowflake.com/en/user-guide/snowflake-cortex/aisql-privileges-and-access).

From the repository root, replace `my_demo_connection` with your connection name.

```bash
snow connection test -c my_demo_connection
bash deploy.sh my_demo_connection
```

The script creates and seeds `LAUNCH_MYSTERY.DEMO`, creates the semantic view and search service, stages the app, and runs smoke queries. Open `INCIDENT_ROOM` from Streamlit in Snowsight. Use the deployment role during rehearsal. After reseeding, allow the existing search service to refresh before rehearsing with changed notes.

## Five-minute interview walkthrough

1. **0:00–0:45 · Frame the decision.** Open the incident room and show the 18% order drop with steady traffic. Ask what the interviewer would investigate first.
2. **0:45–1:45 · Locate the drop.** In Snowsight Cortex Analyst, select `LAUNCH_MYSTERY.DEMO.CHECKOUT_FUNNEL` and ask “What were checkout starts, completed orders, and checkout completion rate by release phase for each iOS cohort?” Inspect the generated SQL. Rollout goes from 60% to 24%, while holdout stays near 60.6%. Back in the app, click **Trace a timed-out iOS checkout** to see the events for one shopper session.
3. **1:45–3:00 · Test the competing explanation.** Run **Payment-provider hypothesis** in Streamlit. Open the evidence panel. The first affected authorization was at or after the provider incident began at 11:20 UTC, after the 10:00–11:00 drop window.
4. **3:00–4:15 · Decide on the next action.** Run **Rollback decision**. The rollout is the leading hypothesis. Propose temporarily disabling the flag and comparing recovery against the holdout. The telemetry sample alone cannot establish how many orders the timeouts affected.
5. **4:15–5:00 · Test the AI.** Run **Missing evidence**. The notes contain no commit ID or author. Look for an explicit statement that the answer is unavailable. Discuss how to test retrieval coverage and whether cited evidence actually entails the generated claim.

## Trial walkthrough with Codex and MCP

If your trial blocks Cortex Search or AI text generation, run the setup, seed, and event scripts in order, then run `sql/06_mcp.sql`. The managed MCP server exposes read-only SQL. Snowflake runs the queries and Codex writes the brief from the rows it retrieves.

1. Grant `LAUNCH_MYSTERY_MCP_READER` to your own Snowflake username. Check the target username with `SELECT CURRENT_USER();`. The role can select the checkout funnel and incident notes.
2. Run `sql/07_codex_oauth.sql` as an admin and copy the returned MCP URL. In Codex desktop, go to **Settings → MCP servers** and add a **Streamable HTTP** server named `launch-day-mystery` using that URL.
3. In Snowsight, run `SELECT SYSTEM$SHOW_OAUTH_CLIENT_SECRETS('LAUNCH_MYSTERY_CODEX_OAUTH');`. Add this block to your personal `~/.codex/config.toml` with the returned client ID and first client secret. Keep the secret outside the repository.

   ```toml
   [mcp_servers.launch-day-mystery.oauth]
   client_id = "YOUR_CLIENT_ID"
   client_secret = "YOUR_CLIENT_SECRET"
   callback_url = "http://127.0.0.1:8765/callback"
   callback_port = 8765
   ```

4. Run `codex mcp login launch-day-mystery --scopes session:role:LAUNCH_MYSTERY_MCP_READER` and check that the displayed role matches before authorizing.
5. Ask Codex to use the MCP tool to compare the iOS cohorts, verify the payment alert timeline, and recommend a reversible action. Ask for the exact commit that caused the timeout to see how it handles missing evidence.

## Verify and clean up

```bash
python3 -m unittest discover -s tests -v
snow sql -c my_demo_connection -f sql/05_smoke.sql
```

The local tests exercise the seeded data, funnel calculations, and citation validation without an account. The Snowflake smoke queries check SQL totals, the semantic view, Search retrieval, and model access. Before an interview, also rehearse all three app prompts and the Cortex Analyst query in Snowsight.

The warehouse auto-suspends after 60 seconds. Cortex Search and AI functions can incur separate usage charges. When done, `snow sql -c my_demo_connection -f sql/99_cleanup.sql` drops the dedicated demo database, warehouse, OAuth integration, and reader role.
