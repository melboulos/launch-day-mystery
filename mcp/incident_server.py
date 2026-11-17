# /// script
# requires-python = ">=3.12"
# dependencies = ["mcp>=1.9,<2", "snowflake-connector-python>=4,<5"]
# ///
"""Local MCP server for the demo's Snowflake data."""

import os

import snowflake.connector
from mcp.server.fastmcp import FastMCP

server = FastMCP("launch-day-mystery-local")


def query(sql):
    connection_name = os.environ.get("LAUNCH_MYSTERY_CONNECTION", "launch_mystery_oauth")
    with snowflake.connector.connect(
        connection_name=connection_name,
        role="LAUNCH_MYSTERY_MCP_READER",
        warehouse="LAUNCH_MYSTERY_WH",
        login_timeout=30,
        network_timeout=45,
        session_parameters={
            "STATEMENT_TIMEOUT_IN_SECONDS": 30,
            "QUERY_TAG": "launch-day-mystery-local-mcp",
        },
    ) as connection:
        with connection.cursor(snowflake.connector.DictCursor) as cursor:
            cursor.execute(sql)
            return cursor.fetchall()


@server.tool()
def compare_ios_checkout() -> list[dict]:
    """Get iOS orders, checkout completion and timeouts by cohort and release phase."""
    return query("""
        SELECT COHORT, RELEASE_PHASE, CHECKOUT_STARTS, ORDERS,
               ROUND(100.0 * ORDERS / NULLIF(CHECKOUT_STARTS, 0), 1) AS COMPLETION_PCT,
               ADDRESS_TIMEOUTS
        FROM LAUNCH_MYSTERY.DEMO.CHECKOUT_EVENT_FUNNEL
        WHERE PLATFORM = 'iOS'
        ORDER BY COHORT, WINDOW_START_UTC
    """)


@server.tool()
def read_incident_notes() -> list[dict]:
    """Read the synthetic launch notes, release timeline, and payment alert."""
    return query("""
        SELECT DOC_ID, TITLE, BODY
        FROM LAUNCH_MYSTERY.DEMO.INCIDENT_NOTES
        ORDER BY DOC_ID
        LIMIT 20
    """)


if __name__ == "__main__":
    server.run()
