"""
Snowflake MCP Client - Extract Query History
This script connects to a Snowflake MCP server and extracts query history.
"""

import os
import json
from typing import List, Dict, Any
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def connect_to_snowflake_mcp() -> ClientSession:
    """
    Connect to the Snowflake MCP server.
    
    Returns:
        ClientSession: Active MCP client session
    """
    # Configure the Snowflake MCP server connection
    # Adjust the command based on your Snowflake MCP installation
    server_params = StdioServerParameters(
        command="npx",
        args=["-y", "@modelcontextprotocol/server-snowflake"],
        env={
            **os.environ,
            # Add Snowflake credentials from environment
            "SNOWFLAKE_ACCOUNT": os.getenv("SNOWFLAKE_ACCOUNT", ""),
            "SNOWFLAKE_USERNAME": os.getenv("SNOWFLAKE_USERNAME", ""),
            "SNOWFLAKE_PASSWORD": os.getenv("SNOWFLAKE_PASSWORD", ""),
            "SNOWFLAKE_WAREHOUSE": os.getenv("SNOWFLAKE_WAREHOUSE", ""),
            "SNOWFLAKE_DATABASE": os.getenv("SNOWFLAKE_DATABASE", ""),
            "SNOWFLAKE_SCHEMA": os.getenv("SNOWFLAKE_SCHEMA", ""),
            "SNOWFLAKE_ROLE": os.getenv("SNOWFLAKE_ROLE", ""),
        }
    )
    
    print("🔌 Connecting to Snowflake MCP server...")
    
    # Create client session
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the session
            await session.initialize()
            print("✓ Connected to Snowflake MCP server")
            
            yield session


async def list_available_tools(session: ClientSession) -> List[Dict[str, Any]]:
    """
    List all available tools from the Snowflake MCP server.
    
    Args:
        session: Active MCP client session
    
    Returns:
        List of available tools
    """
    print("\n📋 Available Tools:")
    tools_list = await session.list_tools()
    
    for tool in tools_list.tools:
        print(f"  - {tool.name}: {tool.description}")
    
    return tools_list.tools


async def execute_query(session: ClientSession, query: str) -> Dict[str, Any]:
    """
    Execute a SQL query on Snowflake via MCP.
    
    Args:
        session: Active MCP client session
        query: SQL query to execute
    
    Returns:
        Query results
    """
    print(f"\n🔍 Executing query:\n{query}\n")
    
    result = await session.call_tool(
        "query",
        arguments={"sql": query}
    )
    
    return result


async def get_query_history(
    session: ClientSession,
    limit: int = 100,
    user_filter: str = None,
    start_time: str = None,
    end_time: str = None
) -> Dict[str, Any]:
    """
    Extract query history from Snowflake.
    
    Args:
        session: Active MCP client session
        limit: Maximum number of queries to retrieve
        user_filter: Optional username to filter queries
        start_time: Optional start time filter (format: 'YYYY-MM-DD HH:MM:SS')
        end_time: Optional end time filter (format: 'YYYY-MM-DD HH:MM:SS')
    
    Returns:
        Query history results
    """
    # Build the query history SQL
    query = f"""
    SELECT 
        QUERY_ID,
        QUERY_TEXT,
        DATABASE_NAME,
        SCHEMA_NAME,
        QUERY_TYPE,
        SESSION_ID,
        USER_NAME,
        ROLE_NAME,
        WAREHOUSE_NAME,
        WAREHOUSE_SIZE,
        WAREHOUSE_TYPE,
        CLUSTER_NUMBER,
        QUERY_TAG,
        EXECUTION_STATUS,
        ERROR_CODE,
        ERROR_MESSAGE,
        START_TIME,
        END_TIME,
        TOTAL_ELAPSED_TIME,
        BYTES_SCANNED,
        ROWS_PRODUCED,
        COMPILATION_TIME,
        EXECUTION_TIME,
        QUEUED_PROVISIONING_TIME,
        QUEUED_REPAIR_TIME,
        QUEUED_OVERLOAD_TIME,
        TRANSACTION_BLOCKED_TIME,
        OUTBOUND_DATA_TRANSFER_CLOUD,
        OUTBOUND_DATA_TRANSFER_REGION,
        OUTBOUND_DATA_TRANSFER_BYTES,
        INBOUND_DATA_TRANSFER_CLOUD,
        INBOUND_DATA_TRANSFER_REGION,
        INBOUND_DATA_TRANSFER_BYTES,
        CREDITS_USED_CLOUD_SERVICES,
        RELEASE_VERSION,
        EXTERNAL_FUNCTION_TOTAL_INVOCATIONS,
        EXTERNAL_FUNCTION_TOTAL_SENT_ROWS,
        EXTERNAL_FUNCTION_TOTAL_RECEIVED_ROWS,
        EXTERNAL_FUNCTION_TOTAL_SENT_BYTES,
        EXTERNAL_FUNCTION_TOTAL_RECEIVED_BYTES
    FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
    WHERE 1=1
    """
    
    # Add optional filters
    if user_filter:
        query += f"\n    AND USER_NAME = '{user_filter}'"
    
    if start_time:
        query += f"\n    AND START_TIME >= '{start_time}'"
    
    if end_time:
        query += f"\n    AND END_TIME <= '{end_time}'"
    
    query += f"""
    ORDER BY START_TIME DESC
    LIMIT {limit}
    """
    
    print(f"📊 Fetching query history (limit: {limit})...")
    result = await execute_query(session, query)
    
    return result


async def export_query_history_to_file(
    session: ClientSession,
    output_file: str = "query_history.json",
    limit: int = 100,
    **filters
) -> str:
    """
    Export query history to a JSON file.
    
    Args:
        session: Active MCP client session
        output_file: Path to output JSON file
        limit: Maximum number of queries to retrieve
        **filters: Additional filters (user_filter, start_time, end_time)
    
    Returns:
        Path to the exported file
    """
    result = await get_query_history(session, limit=limit, **filters)
    
    # Save to file
    output_path = os.path.join(os.path.dirname(__file__), output_file)
    with open(output_path, 'w') as f:
        json.dump(result, f, indent=2, default=str)
    
    print(f"\n✓ Query history exported to: {output_path}")
    return output_path


async def main():
    """
    Main function to demonstrate Snowflake MCP query history extraction.
    """
    print("=== Snowflake MCP Query History Extractor ===\n")
    
    # Check for required environment variables
    required_vars = [
        "SNOWFLAKE_ACCOUNT",
        "SNOWFLAKE_USERNAME",
        "SNOWFLAKE_PASSWORD"
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        print("⚠️  Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease set these variables before running:")
        print("export SNOWFLAKE_ACCOUNT='your-account'")
        print("export SNOWFLAKE_USERNAME='your-username'")
        print("export SNOWFLAKE_PASSWORD='your-password'")
        print("export SNOWFLAKE_WAREHOUSE='your-warehouse'  # Optional")
        print("export SNOWFLAKE_DATABASE='your-database'    # Optional")
        print("export SNOWFLAKE_SCHEMA='your-schema'        # Optional")
        print("export SNOWFLAKE_ROLE='your-role'            # Optional")
        return
    
    # Connect to Snowflake MCP
    async for session in connect_to_snowflake_mcp():
        # List available tools
        await list_available_tools(session)
        
        # Example 1: Get recent query history
        print("\n" + "="*60)
        print("Example 1: Get last 10 queries")
        print("="*60)
        result = await get_query_history(session, limit=10)
        print(f"Retrieved {len(result.content) if hasattr(result, 'content') else 'N/A'} queries")
        
        # Example 2: Export query history to file
        print("\n" + "="*60)
        print("Example 2: Export query history to JSON")
        print("="*60)
        output_file = await export_query_history_to_file(
            session,
            output_file="snowflake_query_history.json",
            limit=100
        )
        
        # Example 3: Filter by user and time range (commented out - adjust as needed)
        # print("\n" + "="*60)
        # print("Example 3: Filter by user and time range")
        # print("="*60)
        # result = await get_query_history(
        #     session,
        #     limit=50,
        #     user_filter="YOUR_USERNAME",
        #     start_time="2025-01-01 00:00:00",
        #     end_time="2025-12-31 23:59:59"
        # )
        
        print("\n✅ Done!")


if __name__ == "__main__":
    # Check if MCP package is installed
    try:
        import mcp
    except ImportError:
        print("⚠️  MCP package not found. Installing...")
        print("Run: uv pip install mcp")
        print("\nOr add to pyproject.toml dependencies:")
        print('  "mcp>=1.0.0",')
        exit(1)
    
    # Run the async main function
    asyncio.run(main())
