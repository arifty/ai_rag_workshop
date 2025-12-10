"""
Demo script to test the mock Snowflake connector
"""

import sys
import os

# Add gemini to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'gemini'))

from agents.mock_snowflake_connector import MockSnowflakeConnector
from main import warehouse_recommendation
import pandas as pd

print("="*70)
print("Mock Snowflake Connector Demo")
print("="*70)

# Initialize mock connector
print("\n1. Creating mock Snowflake connection...")
connector = MockSnowflakeConnector()

# List of query IDs to test
query_ids = ['test_abc12345', 'test_xyz98765', 'test_def56789', 'test_gld11223']

print(f"\n2. Fetching details for {len(query_ids)} queries...")
query_details = connector.get_query_details(query_ids)

print(f"\n3. Got {len(query_details)} query details")
print("\nQuery Details:")
for qd in query_details:
    print(f"  - {qd['QUERY_ID']}: {qd['WAREHOUSE_NAME']} warehouse, "
          f"{qd['EXECUTION_TIME']/60000:.1f} min runtime")

# Get recommendations
print("\n4. Generating warehouse recommendations...")
recommendations = warehouse_recommendation(query_details)

# Format and display
df = pd.DataFrame(recommendations)
df['Cost Impact (Cr/Hr Diff)'] = df['Cost Impact (Cr/Hr Diff)'].apply(
    lambda x: f"+{x:.0f}" if x > 0 else (f"{x:.0f}" if x < 0 else "0")
)

print("\n" + "="*70)
print("Warehouse Optimization Recommendations")
print("="*70)
print(df.to_markdown(index=False))

print("\n" + "="*70)
print("Legend:")
print("="*70)
print("✅ Upsize (XS → M): Long-running queries on small warehouses")
print("   - Cost: Higher per hour, but much faster execution")
print("   - Use case: ETL jobs, complex analytics")
print()
print("⬇️  Downsize (XL → M): Fast queries on large warehouses")
print("   - Cost: Savings per hour, slight performance impact")
print("   - Use case: Simple dashboards, quick lookups")
print()
print("➖ No change (M): Already optimal for the workload")
print("   - Cost: No change")
print("   - Use case: Properly sized queries")

# Close connection
connector.close()

print("\n" + "="*70)
print("Available Mock Query IDs for Testing:")
print("="*70)
for qid in MockSnowflakeConnector.MOCK_QUERY_DATA.keys():
    print(f"  - {qid}")

print("\n💡 Tip: Try these in the chatbot:")
print("   'What's the warehouse recommendation for query ID test_abc12345?'")
print("   'Optimize warehouse for query test_xyz98765'")
print("   'Check query IDs test_abc12345 and test_xyz98765'")
