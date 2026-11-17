# Snowflake-managed MCP

This is the hosted alternative to the local MCP server. In the tested self-service trial, Snowflake accepted server creation and OAuth authentication. It rejected SQL tool execution with **`399504: Access denied for trial accounts`**. Use the [local MCP setup](../README.md#local-mcp-setup) for the verified trial connection.

## Register Codex

1. As an admin, run [06_mcp.sql](../sql/06_mcp.sql) after loading the checkout data. It creates the read-only SQL tool and reader grants. Grant `LAUNCH_MYSTERY_MCP_READER` to the Snowflake user who will sign in.
2. Run [07_codex_oauth.sql](../sql/07_codex_oauth.sql). It registers a loopback callback and advertises the reader scope. Copy the resulting MCP server URL.
3. In Codex desktop, open **Settings → MCP servers** and add a **Streamable HTTP** server named `launch-day-mystery`. Paste the Snowflake URL.
4. In Snowsight, retrieve the OAuth credentials as an admin:

   ```sql
   SELECT SYSTEM$SHOW_OAUTH_CLIENT_SECRETS('LAUNCH_MYSTERY_CODEX_OAUTH');
   ```

5. Put the client ID and first client secret in your personal `~/.codex/config.toml`. Keep the credentials outside the Git checkout.

   ```toml
   [mcp_servers.launch-day-mystery.oauth]
   client_id = "YOUR_CLIENT_ID"
   client_secret = "YOUR_CLIENT_SECRET"
   callback_url = "http://127.0.0.1:8765/callback"
   callback_port = 8765
   ```

6. Sign in and confirm that the consent screen shows the demo reader role:

   ```bash
   codex mcp login launch-day-mystery --scopes session:role:LAUNCH_MYSTERY_MCP_READER
   ```

7. Start a new Codex chat and ask it to query `LAUNCH_MYSTERY.DEMO.CHECKOUT_EVENT_FUNNEL` through `launch-day-mystery`. A successful tool result verifies query access.

[Snowflake-managed MCP authentication](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-agents-mcp#set-up-oauth-authentication) · [Codex MCP configuration](https://learn.chatgpt.com/docs/extend/mcp?surface=app)
