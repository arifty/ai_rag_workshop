# RAG + Snowflake Warehouse Optimization Integration Guide

This guide explains how the RAG chatbot has been integrated with Snowflake warehouse optimization recommendations.

## 🎯 Overview

The enhanced RAG system can now:
1. Answer questions from your personal documents (original functionality)
2. Provide warehouse optimization recommendations when you ask about Snowflake Query IDs
3. Automatically detect when you're asking about query optimization

## 🏗️ Architecture

```
RAG_workshop/main.py (Enhanced Chatbot)
    ├── ChromaDB (Document Search)
    ├── OpenAI/Gemini (Answer Generation)
    └── Warehouse Recommendation System
            ├── gemini/main.py (Recommendation Logic)
            └── gemini/agents/snowflake_connector.py (Snowflake MCP)
```

## 📋 Prerequisites

1. **Install all dependencies:**
   ```bash
   cd /path/to/RAG_workshop
   uv sync
   ```

2. **Set up Snowflake credentials:**
   Create `gemini/config/snowflake_creds.json`:
   ```json
   {
       "user": "your_username",
       "password": "your_password",
       "account": "your_account.snowflakecomputing.com",
       "warehouse": "COMPUTE_WH",
       "role": "SNOWFLAKE_MONITOR"
   }
   ```

3. **Set API Key for RAG:**
   ```bash
   export API_KEY='your-gemini-api-key'
   ```

## 🚀 Usage

### Running the Enhanced Chatbot

```bash
uv run main.py
```

### Example Interactions

#### 1. **Document Questions** (Original RAG functionality)
```
🔍 Your question: What did we discuss in the meeting about project deadlines?

📚 Searching knowledge base...
📄 Found relevant information in:
  - example_notes.txt

💡 Generating answer...
According to the meeting notes, the project deadline was extended to...
```

#### 2. **Query ID Optimization** (NEW!)
```
🔍 Your question: What's the warehouse recommendation for query ID abc12345?

🏢 Checking Snowflake warehouse recommendations...

📊 Warehouse Optimization Recommendations

| Query ID  | Current WH | Runtime (Min) | Suggested WH | Runtime Impr. (%) | Cost Impact (Cr/Hr Diff) | Query Text                         |
|-----------|------------|---------------|--------------|-------------------|--------------------------|-----------------------------------|
| abc12345  | XS         | 135.00        | M            | 60%               | +3                       | SELECT complex_etl_job...         |

💡 Legend:
- Positive Cost Impact: Higher hourly cost (but faster execution)
- Negative Cost Impact: Cost savings (may have slower execution)
```

#### 3. **Multiple Query IDs**
```
🔍 Your question: Optimize warehouse for queries abc12345 and xyz98765

🏢 Checking Snowflake warehouse recommendations...
```

#### 4. **Keywords that Trigger Optimization**
The chatbot automatically detects optimization requests when you use keywords like:
- "query id" / "query_id" / "queryid"
- "recommend" / "recommendation"
- "optimize" / "optimization"
- "warehouse"

Combined with query IDs in your question.

## 🔧 How It Works

### 1. Query Detection
The `extract_query_ids()` function uses regex to find query IDs in user input:
```python
pattern = r'\b[a-zA-Z0-9]{8,}\b'  # Alphanumeric, 8+ characters
```

### 2. Snowflake Data Retrieval
When query IDs are detected, the system:
1. Connects to Snowflake using `SnowflakeConnector`
2. Fetches query metrics from `SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY`
3. Retrieves: execution time, warehouse size, credits used, query text

### 3. Recommendation Logic
The `warehouse_recommendation()` function applies rules:

**Upsizing Rule:**
- If runtime > 45 minutes AND warehouse is XS
- Suggests: Upgrade to M
- Estimates: 2.5X speedup, higher cost

**Downsizing Rule:**
- If runtime < 5 seconds AND warehouse >= L
- Suggests: Downgrade to M
- Estimates: 3X slower (still fast), cost savings

### 4. Response Formatting
Results are formatted as markdown tables with:
- Current vs. suggested warehouse
- Runtime improvement percentage
- Cost impact (credits/hour difference)
- Query text preview

## 🛠️ MCP Integration

The warehouse recommendation is also available via MCP for GitHub Copilot Chat.

### Add to `.vscode/mcp.json`:
```json
{
    "servers": {
        "rag_with_snowflake": {
            "type": "stdio",
            "command": "uv",
            "args": [
                "--directory",
                "/Users/arif.thayal/Workarea/MISSIONS/2024/luminus/demo-AI-workshop-1/workshops/RAG_workshop",
                "run",
                "rag_in_mcp.py"
            ]
        }
    }
}
```

### Use in Copilot Chat:
```
@workspace Get warehouse recommendations for query IDs abc12345, xyz98765
```

The MCP server provides:
- `search_knowledge_base()` - Search documents
- `add_document()` - Add new documents
- `get_collection_stats()` - Get statistics
- `get_warehouse_recommendations()` - NEW! Get optimization recommendations

## 📊 Recommendation Output Fields

| Field | Description |
|-------|-------------|
| Query ID | Snowflake query identifier |
| Current WH | Current warehouse size (XS, S, M, L, XL, 2XL) |
| Runtime (Min) | Actual execution time in minutes |
| Suggested WH | Recommended warehouse size |
| Runtime Impr. (%) | Expected runtime change (negative = slower, positive = faster) |
| Cost Impact (Cr/Hr Diff) | Credits/hour difference (+ = more expensive, - = savings) |
| Query Text | Preview of the SQL query |

## 🎓 Customization

### Adjust Recommendation Rules

Edit `gemini/main.py` to customize thresholds:

```python
# Upsizing threshold (currently 45 minutes)
if runtime_ms > 2700000 and current_wh in ['XS']:
    suggested_wh = 'M'
    
# Downsizing threshold (currently 5 seconds)
elif runtime_ms < 5000 and current_wh in ['L', 'XL', '2XL']:
    suggested_wh = 'M'
```

### Adjust Credit Rates

Update the `CREDITS_PER_HOUR` dictionary:
```python
CREDITS_PER_HOUR = {
    'XS': 1, 'S': 2, 'M': 4, 'L': 8, 'XL': 16, '2XL': 32
}
```

## 🐛 Troubleshooting

### "Unable to connect to Snowflake"
- Check `gemini/config/snowflake_creds.json` exists and has correct credentials
- Verify your Snowflake account URL format
- Ensure your role has access to `SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY`

### "No module named 'snowflake'"
```bash
uv sync  # This should install snowflake-connector-python
```

### "Missing optional dependency 'tabulate'"
```bash
uv sync  # This should install tabulate
```

### Query IDs not detected
- Ensure query IDs are at least 8 alphanumeric characters
- Use keywords like "query id", "optimize", "warehouse" in your question

## 🔐 Security Notes

1. **Never commit credentials:** Add `gemini/config/snowflake_creds.json` to `.gitignore`
2. **Use key-pair auth in production:** The current implementation uses password auth for demo purposes
3. **Limit role permissions:** Use a read-only role like `SNOWFLAKE_MONITOR`

## 📚 Additional Resources

- [Snowflake QUERY_HISTORY Documentation](https://docs.snowflake.com/en/sql-reference/account-usage/query_history)
- [Snowflake Warehouse Sizing Guide](https://docs.snowflake.com/en/user-guide/warehouses-considerations)
- [Model Context Protocol (MCP)](https://modelcontextprotocol.io/)

## 💡 Future Enhancements

- [ ] Add time-based analysis (compare performance over time)
- [ ] Include cost predictions based on query frequency
- [ ] Add support for multi-cluster warehouse recommendations
- [ ] Integrate with Snowflake cost monitoring dashboards
- [ ] Add machine learning-based predictions (beyond rule-based)
