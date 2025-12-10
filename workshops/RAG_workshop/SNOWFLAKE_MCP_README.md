# Snowflake MCP Query History Extractor

This guide shows how to connect to Snowflake via MCP (Model Context Protocol) and extract query history.

## Files Created

1. **snowflake_mcp_client.py** - Full-featured async client with comprehensive query history extraction
2. **snowflake_mcp_simple.py** - Simplified synchronous client with interactive menu

## Prerequisites

### 1. Install Node.js and npx
The Snowflake MCP server requires Node.js:
```bash
# Check if npx is installed
npx --version

# If not, install Node.js from https://nodejs.org/
```

### 2. Install Python Dependencies
```bash
# From the RAG_workshop directory
uv sync

# Or install mcp separately
uv pip install mcp
```

### 3. Set Snowflake Credentials
```bash
export SNOWFLAKE_ACCOUNT='your-account.snowflakecomputing.com'
export SNOWFLAKE_USERNAME='your-username'
export SNOWFLAKE_PASSWORD='your-password'
export SNOWFLAKE_WAREHOUSE='COMPUTE_WH'  # Optional
export SNOWFLAKE_DATABASE='your-database'  # Optional
export SNOWFLAKE_SCHEMA='PUBLIC'  # Optional
export SNOWFLAKE_ROLE='your-role'  # Optional
```

## Usage

### Option 1: Simple Interactive Client (Recommended for beginners)

```bash
uv run snowflake_mcp_simple.py
```

This will show an interactive menu:
```
1. Get recent query history (last 10 queries)
2. Get queries by user
3. Get failed queries
4. Custom query
```

### Option 2: Full Async Client (Advanced)

```bash
uv run snowflake_mcp_client.py
```

This automatically:
- Lists available MCP tools
- Fetches the last 10 queries
- Exports 100 queries to `snowflake_query_history.json`

## What Gets Extracted from QUERY_HISTORY

The scripts extract the following information from `SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY`:

### Basic Info
- `QUERY_ID` - Unique query identifier
- `QUERY_TEXT` - The actual SQL query
- `USER_NAME` - User who ran the query
- `DATABASE_NAME`, `SCHEMA_NAME` - Target database/schema
- `WAREHOUSE_NAME`, `WAREHOUSE_SIZE` - Compute resources used

### Execution Details
- `EXECUTION_STATUS` - SUCCESS, FAIL, etc.
- `START_TIME`, `END_TIME` - When the query ran
- `TOTAL_ELAPSED_TIME` - Total time in milliseconds
- `COMPILATION_TIME`, `EXECUTION_TIME` - Performance breakdown

### Resource Usage
- `BYTES_SCANNED` - Data scanned
- `ROWS_PRODUCED` - Rows returned
- `CREDITS_USED_CLOUD_SERVICES` - Cost metrics

### Errors (if any)
- `ERROR_CODE`, `ERROR_MESSAGE` - Failure details

## Example Queries

### Get Last 10 Queries
```python
result = await get_query_history(session, limit=10)
```

### Filter by User
```python
result = await get_query_history(
    session,
    limit=50,
    user_filter="JOHN_DOE"
)
```

### Filter by Time Range
```python
result = await get_query_history(
    session,
    limit=100,
    start_time="2025-01-01 00:00:00",
    end_time="2025-12-31 23:59:59"
)
```

### Export to JSON File
```python
output_file = await export_query_history_to_file(
    session,
    output_file="my_queries.json",
    limit=100
)
```

## Troubleshooting

### "npx: command not found"
Install Node.js from https://nodejs.org/

### "Import mcp could not be resolved"
```bash
uv sync
# Or
uv pip install mcp
```

### "Missing required environment variables"
Make sure all Snowflake credentials are set as environment variables.

### "Connection refused" or "Authentication failed"
- Verify your Snowflake credentials
- Check if your account URL is correct (should include `.snowflakecomputing.com`)
- Ensure your IP is whitelisted in Snowflake network policies

## Using with GitHub Copilot Chat

You can also add the Snowflake MCP to your `.vscode/mcp.json` to use it directly from Copilot Chat:

```json
{
    "servers": {
        "snowflake": {
            "type": "stdio",
            "command": "npx",
            "args": [
                "-y",
                "@modelcontextprotocol/server-snowflake"
            ],
            "env": {
                "SNOWFLAKE_ACCOUNT": "your-account.snowflakecomputing.com",
                "SNOWFLAKE_USERNAME": "your-username",
                "SNOWFLAKE_PASSWORD": "your-password"
            }
        }
    }
}
```

Then you can ask Copilot Chat: "Query the Snowflake query history for failed queries in the last 24 hours"

## Next Steps

- Customize the query filters in the scripts
- Add more sophisticated error handling
- Create visualization for query performance trends
- Build a dashboard to monitor query patterns
- Set up alerts for failed queries or long-running queries

## References

- [Model Context Protocol (MCP)](https://modelcontextprotocol.io/)
- [Snowflake MCP Server](https://github.com/modelcontextprotocol/servers/tree/main/src/snowflake)
- [Snowflake QUERY_HISTORY View](https://docs.snowflake.com/en/sql-reference/account-usage/query_history)
