"""
Mock Snowflake Connector for Testing
This provides sample data without requiring actual Snowflake credentials.
"""

class MockSnowflakeConnector:
    """
    Mock connector that returns sample query data for testing.
    Use this when you don't have Snowflake credentials or want to test offline.
    """
    
    # Sample query data for testing
    MOCK_QUERY_DATA = {
        'test_abc12345': {
            'QUERY_ID': 'test_abc12345',
            'WAREHOUSE_NAME': 'XS',
            'EXECUTION_TIME': 8100000,  # 135 minutes - should recommend upsize
            'BYTES_SCANNED': 1500000000,
            'CREDITS_USED': 0.0056,
            'QUERY_TEXT': 'SELECT * FROM large_table JOIN another_table ON id WHERE date > 2024-01-01 AND complex_condition = TRUE'
        },
        'test_xyz98765': {
            'QUERY_ID': 'test_xyz98765',
            'WAREHOUSE_NAME': 'XL',
            'EXECUTION_TIME': 2500,  # 2.5 seconds - should recommend downsize
            'BYTES_SCANNED': 1000000,
            'CREDITS_USED': 0.0001,
            'QUERY_TEXT': 'SELECT COUNT(*) FROM small_table WHERE status = active'
        },
        'test_def56789': {
            'QUERY_ID': 'test_def56789',
            'WAREHOUSE_NAME': 'M',
            'EXECUTION_TIME': 120000,  # 2 minutes - no recommendation needed
            'BYTES_SCANNED': 500000000,
            'CREDITS_USED': 0.0008,
            'QUERY_TEXT': 'SELECT user_id, SUM(amount) FROM transactions GROUP BY user_id ORDER BY SUM(amount) DESC LIMIT 100'
        },
        'test_gld11223': {
            'QUERY_ID': 'test_gld11223',
            'WAREHOUSE_NAME': 'L',
            'EXECUTION_TIME': 300000,  # 5 minutes - reasonable for L warehouse
            'BYTES_SCANNED': 2000000000,
            'CREDITS_USED': 0.0066,
            'QUERY_TEXT': 'SELECT * FROM fact_table JOIN dim1 ON key1 JOIN dim2 ON key2 WHERE date_range = last_month'
        },
        'abc12345': {  # Without 'test_' prefix for compatibility
            'QUERY_ID': 'abc12345',
            'WAREHOUSE_NAME': 'XS',
            'EXECUTION_TIME': 8100000,
            'BYTES_SCANNED': 1500000000,
            'CREDITS_USED': 0.0056,
            'QUERY_TEXT': 'SELECT complex_etl_job FROM production_table WHERE processing_date >= DATEADD(day, -30, CURRENT_DATE())'
        },
        'xyz98765': {
            'QUERY_ID': 'xyz98765',
            'WAREHOUSE_NAME': 'XL',
            'EXECUTION_TIME': 2500,
            'BYTES_SCANNED': 1000000,
            'CREDITS_USED': 0.0001,
            'QUERY_TEXT': 'SELECT simple_dashboard_query FROM cache_table WHERE id = 123'
        },
        'def56789': {
            'QUERY_ID': 'def56789',
            'WAREHOUSE_NAME': 'M',
            'EXECUTION_TIME': 120000,
            'BYTES_SCANNED': 500000000,
            'CREDITS_USED': 0.0008,
            'QUERY_TEXT': 'SELECT regular_report FROM daily_summary WHERE report_date = CURRENT_DATE()'
        },
        'gld11223': {
            'QUERY_ID': 'gld11223',
            'WAREHOUSE_NAME': 'L',
            'EXECUTION_TIME': 300000,
            'BYTES_SCANNED': 2000000000,
            'CREDITS_USED': 0.0066,
            'QUERY_TEXT': 'SELECT heavy_join_on_L FROM large_fact JOIN multiple_dimensions WHERE year = 2024'
        }
    }

    def __init__(self, config_path=None):
        """Initialize mock connector - always succeeds"""
        self.conn = True  # Simulate successful connection
        print("✅ Mock Snowflake connection established (using sample data).")
        print("   💡 This is a mock connector for testing without real credentials.")

    def get_query_details(self, query_id_list: list) -> list:
        """
        Return mock query details for the given query IDs.
        
        Args:
            query_id_list: List of query IDs to fetch
            
        Returns:
            List of query detail dictionaries
        """
        results = []
        
        for query_id in query_id_list:
            if query_id in self.MOCK_QUERY_DATA:
                results.append(self.MOCK_QUERY_DATA[query_id])
                print(f"   📊 Found mock data for: {query_id}")
            else:
                print(f"   ⚠️  No mock data for: {query_id}")
                # Create a default entry for unknown IDs
                results.append({
                    'QUERY_ID': query_id,
                    'WAREHOUSE_NAME': 'M',
                    'EXECUTION_TIME': 60000,  # 1 minute default
                    'BYTES_SCANNED': 100000000,
                    'CREDITS_USED': 0.0004,
                    'QUERY_TEXT': f'SELECT * FROM table WHERE query_id = {query_id}'
                })
        
        return results

    def close(self):
        """Close the mock connection"""
        self.conn = False
        print("✅ Mock Snowflake connection closed.")

    @staticmethod
    def add_mock_query(query_id: str, warehouse: str, execution_time_ms: int, 
                       query_text: str, bytes_scanned: int = 1000000, 
                       credits_used: float = 0.001):
        """
        Add a new mock query to the dataset.
        
        Args:
            query_id: Unique query identifier
            warehouse: Warehouse size (XS, S, M, L, XL, 2XL)
            execution_time_ms: Execution time in milliseconds
            query_text: The SQL query text
            bytes_scanned: Bytes scanned (optional)
            credits_used: Credits consumed (optional)
        """
        MockSnowflakeConnector.MOCK_QUERY_DATA[query_id] = {
            'QUERY_ID': query_id,
            'WAREHOUSE_NAME': warehouse,
            'EXECUTION_TIME': execution_time_ms,
            'BYTES_SCANNED': bytes_scanned,
            'CREDITS_USED': credits_used,
            'QUERY_TEXT': query_text
        }
        print(f"✅ Added mock query: {query_id}")


# Alias for backward compatibility
SnowflakeConnector = MockSnowflakeConnector
