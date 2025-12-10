# Using Mock Snowflake Connector

## 🎯 Why Mock?

The mock Snowflake connector allows you to test the warehouse optimization feature without:
- Real Snowflake credentials
- Network connectivity
- Actual Snowflake account

## 🚀 Quick Start

### 1. Run the Demo
```bash
uv run demo_mock_connector.py
```

This will show you sample recommendations for 4 test queries.

### 2. Run the Chatbot
```bash
uv run main.py
```

The chatbot will automatically use the mock connector if real Snowflake credentials are not available.

### 3. Try These Questions

Ask the chatbot about query IDs:

```
🔍 Your question: What's the warehouse recommendation for query ID test_abc12345?
```

Or multiple IDs:
```
🔍 Your question: Optimize warehouse for queries test_abc12345 and test_xyz98765
```

## 📋 Available Mock Query IDs

The mock connector has 8 pre-loaded query IDs with different characteristics:

### Upsize Candidates (Slow on Small Warehouse)
- **test_abc12345** / **abc12345**
  - Current: XS warehouse
  - Runtime: 135 minutes (very slow!)
  - Recommendation: Upgrade to M
  - Impact: 60% faster, +3 credits/hour

### Downsize Candidates (Fast on Large Warehouse)
- **test_xyz98765** / **xyz98765**
  - Current: XL warehouse (overkill!)
  - Runtime: 2.5 seconds (very fast)
  - Recommendation: Downgrade to M
  - Impact: Still fast, -12 credits/hour savings

### Optimal (No Change Needed)
- **test_def56789** / **def56789**
  - Current: M warehouse
  - Runtime: 2 minutes
  - Recommendation: Keep M
  - Impact: No change

- **test_gld11223** / **gld11223**
  - Current: L warehouse
  - Runtime: 5 minutes
  - Recommendation: Keep L
  - Impact: No change

## 🔧 Adding Custom Mock Data

You can add your own test queries programmatically:

```python
from gemini.agents.mock_snowflake_connector import MockSnowflakeConnector

# Add a custom query
MockSnowflakeConnector.add_mock_query(
    query_id='my_test_query',
    warehouse='S',
    execution_time_ms=3000000,  # 50 minutes
    query_text='SELECT * FROM my_table WHERE complex_condition',
    bytes_scanned=2000000000,
    credits_used=0.005
)
```

## 🔄 Switching to Real Snowflake

When you're ready to use real Snowflake data:

1. **Create credentials file:**
   ```bash
   # Create gemini/config/snowflake_creds.json
   {
       "user": "your_username",
       "password": "your_password",
       "account": "your_account.snowflakecomputing.com",
       "warehouse": "COMPUTE_WH",
       "role": "SNOWFLAKE_MONITOR"
   }
   ```

2. **Update the connector import:**
   
   In `gemini/agents/snowflake_connector.py`, the real connector will be used automatically if credentials are valid.

3. **Run the chatbot:**
   ```bash
   uv run main.py
   ```
   
   It will try real Snowflake first, fall back to mock if it fails.

## 📊 Mock Data Structure

Each mock query has these fields:

```python
{
    'QUERY_ID': 'unique_identifier',
    'WAREHOUSE_NAME': 'XS|S|M|L|XL|2XL',
    'EXECUTION_TIME': 123456,  # milliseconds
    'BYTES_SCANNED': 1000000,
    'CREDITS_USED': 0.001,
    'QUERY_TEXT': 'SELECT ...'
}
```

## 💡 Tips

1. **Test Different Scenarios:**
   - Try both slow queries on small warehouses
   - Try fast queries on large warehouses
   - See what "optimal" looks like

2. **Understand the Logic:**
   - Runtime > 45 min on XS → Upsize to M
   - Runtime < 5 sec on L/XL/2XL → Downsize to M

3. **Experiment:**
   - Add your own mock queries
   - Modify thresholds in `gemini/main.py`
   - See how recommendations change

## 🎓 Learning Objectives

Using the mock connector helps you:
- ✅ Understand warehouse optimization without Snowflake access
- ✅ Test the chatbot integration locally
- ✅ Learn the recommendation logic
- ✅ Prototype before connecting to production

## 🐛 Troubleshooting

**Q: I want to force using the mock, even if I have credentials**

A: Rename or move your `gemini/config/snowflake_creds.json` file temporarily.

**Q: Can I modify the mock data?**

A: Yes! Edit `gemini/agents/mock_snowflake_connector.py` and modify the `MOCK_QUERY_DATA` dictionary.

**Q: The chatbot is using real Snowflake, but I want mock**

A: The system tries real first. If you get connection errors, it will automatically fall back to mock.

Enjoy testing! 🚀
