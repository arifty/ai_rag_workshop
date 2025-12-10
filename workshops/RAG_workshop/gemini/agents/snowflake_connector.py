import snowflake.connector
import json

class SnowflakeConnector:
    """
    Handles secure connection and query execution against the Snowflake Data Cloud.
    This component fulfills Phase 2 (Snowflake MCP Setup).
    """

    def __init__(self, config_path="config/snowflake_creds.json"):
        """Initializes the connection using credentials from a config file."""
        try:
            with open(config_path, 'r') as f:
                creds = json.load(f)
            
            # NOTE: Use Key Pair Authentication in production for better security
            self.conn = snowflake.connector.connect(
                user=creds['user'],
                password=creds['password'],
                account=creds['account'],
                warehouse=creds.get('warehouse', 'COMPUTE_WH'),
                role=creds.get('role', 'SNOWFLAKE_MONITOR') # Requires read access to ACCOUNT_USAGE
            )
            print("✅ Snowflake connection established successfully.")
        except Exception as e:
            print(f"❌ Error connecting to Snowflake: {e}")
            self.conn = None

    def get_query_details(self, query_id_list: list) -> list:
        """
        Action 1: Calls the Snowflake MCP to fetch query metrics based on a list of Query IDs.
        """
        if not self.conn:
            return []

        # Format the list of query IDs for the SQL IN clause
        query_ids_str = ', '.join([f"'{qid}'" for qid in query_id_list])

        # Phase 2.2 Example MCP query
        sql_query = f"""
        SELECT 
            QUERY_ID,
            WAREHOUSE_NAME,
            EXECUTION_TIME, -- Time in milliseconds (important detail)
            BYTES_SCANNED,
            CREDITS_USED,
            QUERY_TEXT
        FROM 
            SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
        WHERE 
            QUERY_ID IN ({query_ids_str})
            AND EXECUTION_STATUS = 'SUCCESS'
        ORDER BY 
            EXECUTION_TIME DESC;
        """

        try:
            cursor = self.conn.cursor(snowflake.connector.DictCursor)
            cursor.execute(sql_query)
            results = cursor.fetchall()
            return results
        except Exception as e:
            print(f"❌ Error executing query: {e}")
            return []
        finally:
            cursor.close()

    def close(self):
        """Closes the connection."""
        if self.conn:
            self.conn.close()
            print("✅ Snowflake connection closed.")

# --- End of agents/snowflake_connector.py ---