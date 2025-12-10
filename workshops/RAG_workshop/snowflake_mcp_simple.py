"""
Simple Snowflake MCP Client Example
Extract query history with minimal setup.
"""

import os
import json
import subprocess
from datetime import datetime


def setup_environment():
    """
    Check and setup environment variables for Snowflake connection.
    """
    required_vars = {
        "SNOWFLAKE_ACCOUNT": "your-account.snowflakecomputing.com",
        "SNOWFLAKE_USERNAME": "your-username",
        "SNOWFLAKE_PASSWORD": "your-password",
        "SNOWFLAKE_WAREHOUSE": "COMPUTE_WH",  # Optional
        "SNOWFLAKE_DATABASE": "your-database",  # Optional
        "SNOWFLAKE_SCHEMA": "PUBLIC",  # Optional
    }
    
    print("=== Snowflake Environment Setup ===\n")
    
    missing = []
    for var, example in required_vars.items():
        value = os.getenv(var)
        if not value:
            missing.append((var, example))
            print(f"❌ {var}: Not set")
        else:
            # Mask password
            display_value = "***" if "PASSWORD" in var else value
            print(f"✓ {var}: {display_value}")
    
    if missing:
        print("\n⚠️  Please set the following environment variables:\n")
        for var, example in missing:
            print(f"export {var}='{example}'")
        return False
    
    print("\n✅ All required environment variables are set!")
    return True


def call_snowflake_mcp(query: str) -> dict:
    """
    Call Snowflake MCP server using subprocess.
    This is a simplified approach without async complexity.
    
    Args:
        query: SQL query to execute
    
    Returns:
        Query results as dictionary
    """
    # Prepare the MCP request
    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "query",
            "arguments": {
                "sql": query
            }
        }
    }
    
    # Environment with Snowflake credentials
    env = os.environ.copy()
    
    try:
        # Call the Snowflake MCP server
        # Note: You may need to adjust the command based on your MCP installation
        process = subprocess.Popen(
            ["npx", "-y", "@modelcontextprotocol/server-snowflake"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
            text=True
        )
        
        # Send the request
        stdout, stderr = process.communicate(input=json.dumps(request))
        
        if stderr:
            print(f"⚠️  Stderr: {stderr}")
        
        # Parse response
        response = json.loads(stdout)
        return response
        
    except Exception as e:
        print(f"❌ Error calling Snowflake MCP: {e}")
        return None


def get_query_history_simple(limit: int = 10):
    """
    Simple function to get query history from Snowflake.
    
    Args:
        limit: Number of queries to retrieve
    """
    query = f"""
    SELECT 
        QUERY_ID,
        QUERY_TEXT,
        USER_NAME,
        DATABASE_NAME,
        SCHEMA_NAME,
        WAREHOUSE_NAME,
        EXECUTION_STATUS,
        START_TIME,
        END_TIME,
        TOTAL_ELAPSED_TIME,
        ROWS_PRODUCED,
        BYTES_SCANNED
    FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
    ORDER BY START_TIME DESC
    LIMIT {limit}
    """
    
    print(f"\n📊 Fetching last {limit} queries from QUERY_HISTORY...\n")
    print(f"Query:\n{query}\n")
    
    result = call_snowflake_mcp(query)
    
    if result:
        print("✅ Query executed successfully!")
        print(f"\nResult:\n{json.dumps(result, indent=2)}")
        
        # Save to file
        output_file = f"query_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"\n💾 Saved to: {output_file}")
    else:
        print("❌ Failed to execute query")
    
    return result


def get_query_by_user(username: str, limit: int = 10):
    """
    Get queries filtered by username.
    
    Args:
        username: Snowflake username to filter by
        limit: Number of queries to retrieve
    """
    query = f"""
    SELECT 
        QUERY_ID,
        QUERY_TEXT,
        USER_NAME,
        EXECUTION_STATUS,
        START_TIME,
        TOTAL_ELAPSED_TIME
    FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
    WHERE USER_NAME = '{username}'
    ORDER BY START_TIME DESC
    LIMIT {limit}
    """
    
    print(f"\n📊 Fetching queries for user: {username}\n")
    
    result = call_snowflake_mcp(query)
    return result


def get_failed_queries(limit: int = 10):
    """
    Get failed queries from query history.
    
    Args:
        limit: Number of queries to retrieve
    """
    query = f"""
    SELECT 
        QUERY_ID,
        QUERY_TEXT,
        USER_NAME,
        ERROR_CODE,
        ERROR_MESSAGE,
        START_TIME
    FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
    WHERE EXECUTION_STATUS = 'FAIL'
    ORDER BY START_TIME DESC
    LIMIT {limit}
    """
    
    print(f"\n📊 Fetching last {limit} failed queries...\n")
    
    result = call_snowflake_mcp(query)
    return result


def main():
    """
    Main function - examples of extracting query history.
    """
    print("="*60)
    print("Snowflake MCP - Query History Extractor")
    print("="*60 + "\n")
    
    # Check environment setup
    if not setup_environment():
        return
    
    print("\n" + "="*60)
    print("Choose an option:")
    print("="*60)
    print("1. Get recent query history (last 10 queries)")
    print("2. Get queries by user")
    print("3. Get failed queries")
    print("4. Custom query")
    print("q. Quit")
    
    choice = input("\nEnter your choice: ").strip()
    
    if choice == "1":
        limit = input("How many queries? (default: 10): ").strip() or "10"
        get_query_history_simple(int(limit))
    
    elif choice == "2":
        username = input("Enter username: ").strip()
        limit = input("How many queries? (default: 10): ").strip() or "10"
        get_query_by_user(username, int(limit))
    
    elif choice == "3":
        limit = input("How many failed queries? (default: 10): ").strip() or "10"
        get_failed_queries(int(limit))
    
    elif choice == "4":
        print("\nEnter your SQL query (press Enter twice to finish):")
        query_lines = []
        while True:
            line = input()
            if not line:
                break
            query_lines.append(line)
        
        custom_query = "\n".join(query_lines)
        if custom_query:
            result = call_snowflake_mcp(custom_query)
            if result:
                print(json.dumps(result, indent=2))
    
    elif choice.lower() == "q":
        print("Goodbye!")
    
    else:
        print("Invalid choice!")


if __name__ == "__main__":
    # Check if npx is available (needed for Snowflake MCP)
    try:
        subprocess.run(["npx", "--version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠️  npx is not installed or not in PATH")
        print("Please install Node.js and npm to use the Snowflake MCP server")
        print("Download from: https://nodejs.org/")
        exit(1)
    
    main()
