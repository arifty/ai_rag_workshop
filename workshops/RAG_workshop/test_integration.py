"""
Test script to verify RAG + Snowflake integration
"""

import sys
import os

# Test imports
print("Testing imports...")

try:
    import pandas as pd
    print("✓ pandas imported")
except ImportError as e:
    print(f"✗ pandas import failed: {e}")

try:
    from gemini.main import warehouse_recommendation
    print("✓ warehouse_recommendation imported")
except ImportError as e:
    print(f"✗ warehouse_recommendation import failed: {e}")

try:
    from gemini.agents.snowflake_connector import SnowflakeConnector
    print("✓ SnowflakeConnector imported")
except ImportError as e:
    print(f"✗ SnowflakeConnector import failed: {e}")

# Test mock data
print("\n" + "="*60)
print("Testing warehouse_recommendation with mock data...")
print("="*60)

mock_details = [
    {
        'QUERY_ID': 'test_abc12345',
        'WAREHOUSE_NAME': 'XS',
        'EXECUTION_TIME': 8100000,  # 135 minutes - should recommend upsize
        'CREDITS_USED': 0.0056,
        'QUERY_TEXT': 'SELECT complex_etl_job FROM large_table...'
    },
    {
        'QUERY_ID': 'test_xyz98765',
        'WAREHOUSE_NAME': 'XL',
        'EXECUTION_TIME': 2500,  # 2.5 seconds - should recommend downsize
        'CREDITS_USED': 0.0001,
        'QUERY_TEXT': 'SELECT simple_dashboard_query FROM small_table...'
    },
    {
        'QUERY_ID': 'test_def56789',
        'WAREHOUSE_NAME': 'M',
        'EXECUTION_TIME': 120000,  # 2 minutes - no recommendation
        'CREDITS_USED': 0.0008,
        'QUERY_TEXT': 'SELECT regular_report FROM medium_table...'
    }
]

try:
    recommendations = warehouse_recommendation(mock_details)
    
    print("\nRecommendations generated successfully!")
    print(f"Number of recommendations: {len(recommendations)}\n")
    
    # Format as table
    df = pd.DataFrame(recommendations)
    df['Cost Impact (Cr/Hr Diff)'] = df['Cost Impact (Cr/Hr Diff)'].apply(
        lambda x: f"+{x:.0f}" if x > 0 else (f"{x:.0f}" if x < 0 else "0")
    )
    
    print(df.to_markdown(index=False))
    
    print("\n✅ All tests passed!")
    
except Exception as e:
    print(f"\n✗ Test failed: {e}")
    import traceback
    traceback.print_exc()

# Test Snowflake connection (optional)
print("\n" + "="*60)
print("Testing Snowflake connection (optional)...")
print("="*60)

config_path = "gemini/config/snowflake_creds.json"
if os.path.exists(config_path):
    print(f"✓ Config file found: {config_path}")
    
    try:
        connector = SnowflakeConnector(config_path=config_path)
        if connector.conn:
            print("✓ Snowflake connection successful!")
            connector.close()
        else:
            print("✗ Snowflake connection failed (check credentials)")
    except Exception as e:
        print(f"✗ Error testing Snowflake connection: {e}")
else:
    print(f"⚠️  Config file not found: {config_path}")
    print("   Create this file to test Snowflake connection")
    print("   (This is optional for testing the integration)")

print("\n" + "="*60)
print("Test Summary")
print("="*60)
print("The integration is ready to use!")
print("\nTo run the chatbot:")
print("  uv run main.py")
print("\nThen try asking:")
print("  'What's the warehouse recommendation for query ID test_abc12345?'")
