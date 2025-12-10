import pandas as pd
from agents.snowflake_connector import SnowflakeConnector

# Phase 4.3: Hard-coded credit rates for rule-based cost calculation
CREDITS_PER_HOUR = {
    'XS': 1, 'S': 2, 'M': 4, 'L': 8, 'XL': 16, '2XL': 32
}
MS_TO_MINUTES = 60000
MS_TO_SECONDS = 1000

def warehouse_recommendation(query_details: list) -> list:
    """
    Action 2: Applies rule-based logic to recommend warehouse size and estimate impact.
    This fulfills Phase 4 (Recommendation Logic).
    """
    recommendations = []
    
    for query in query_details:
        current_wh = query['WAREHOUSE_NAME']
        runtime_ms = query['EXECUTION_TIME']
        
        suggested_wh = current_wh
        runtime_improvement_pct = 0
        cost_impact_cr_hr = 0
        expected_runtime_min = runtime_ms / MS_TO_MINUTES
        
        # --- 4.1 Upsizing Logic (Slow jobs on small warehouses) ---
        # Rule: If runtime > 45 minutes (2,700,000 ms) AND warehouse is XS
        if runtime_ms > 2700000 and current_wh in ['XS']:
            suggested_wh = 'M'
            
            # Estimation: Assume 2.5X speedup for XS -> M
            new_runtime_ms = runtime_ms / 2.5 
            runtime_improvement_pct = round((1 - (new_runtime_ms / runtime_ms)) * 100)
            
            # Cost Impact: New Cr/hr - Old Cr/hr (Result is positive, meaning higher hourly cost)
            cost_impact_cr_hr = CREDITS_PER_HOUR['M'] - CREDITS_PER_HOUR[current_wh]

        # --- 4.2 Downsizing Logic (Fast jobs on large warehouses) ---
        # Rule: If runtime < 5 seconds (5,000 ms) AND warehouse >= L
        elif runtime_ms < 5000 and current_wh in ['L', 'XL', '2XL']:
            suggested_wh = 'M'
            
            # Estimation: Assume runtime increases 3X (still very fast)
            new_runtime_ms = runtime_ms * 3 
            
            # Runtime Impact: Percentage change in runtime (will be positive increase)
            runtime_improvement_pct = round(((new_runtime_ms / runtime_ms) - 1) * 100)
            
            # Cost Savings: Old Cr/hr - New Cr/hr (Result is negative, meaning savings)
            cost_impact_cr_hr = -(CREDITS_PER_HOUR[current_wh] - CREDITS_PER_HOUR['M']) 

        recommendations.append({
            'Query ID': query['QUERY_ID'],
            'Current WH': current_wh,
            'Runtime (Min)': f"{runtime_ms / MS_TO_MINUTES:.2f}",
            'Suggested WH': suggested_wh,
            'Runtime Impr. (%)': f"{runtime_improvement_pct:.0f}%",
            'Cost Impact (Cr/Hr Diff)': cost_impact_cr_hr,
            'Query Text': query['QUERY_TEXT'][:50] + '...'
        })
        
    return recommendations


def ai_bot_workflow():
    """
    Phase 5: Simulates the AI Chatbot's workflow to answer the user query.
    """
    
    # 1. Fetch IDs from manual list (Simulation)
    # The actual AI Agent would dynamically fetch these based on the user's NL query
    print("1. AI Agent fetching Query IDs from manual list...")
    query_id_list = ['abc12345', 'xyz98765', 'def56789', 'gld11223'] 
    
    # Initialize connector (assuming config/snowflake_creds.json exists)
    connector = SnowflakeConnector()
    if not connector.conn:
        return "Cannot proceed: Snowflake connection failed."

    # 2. Ask Snowflake MCP for details (Action 1)
    print("2. Calling Snowflake MCP for query execution details...")
    query_details = connector.get_query_details(query_id_list)
    connector.close()

    if not query_details:
        return "No successful query details retrieved from Snowflake."

    # 3. Apply rules (Action 2)
    print("3. Applying rule-based AI reasoning for recommendations...")
    recommendations = warehouse_recommendation(query_details)
    
    # 4. Return table with summary (Phase 6 Final Output)
    print("\n4. Generating Final Report:")
    df = pd.DataFrame(recommendations)
    
    # Customize cost column for readability
    df['Cost Impact (Cr/Hr Diff)'] = df['Cost Impact (Cr/Hr Diff)'].apply(
        lambda x: f"+{x:.0f}" if x > 0 else (f"{x:.0f}" if x < 0 else "0")
    )
    
    final_output = "\n**Optimization Recommendation Report (SnowWiz Prototype)**\n"
    final_output += df.to_markdown(index=False)
    
    return final_output

if __name__ == "__main__":
    # Simulate a successful execution with placeholder data
    # (Note: This main function is for demonstration; replace with actual logic)
    
    # Mock data structure for demonstration (what the actual connector would return)
    # abc12345: Upsizing candidate (Long run on XS)
    # xyz98765: Downsizing candidate (Fast run on XL)
    # def56789: Normal (Medium run on M)
    # gld11223: Slow on L (Potential Upsize to XL, but prototype rule only looks at XS/S)
    
    mock_details = [
        {'QUERY_ID': 'abc12345', 'WAREHOUSE_NAME': 'XS', 'EXECUTION_TIME': 8100000, 'CREDITS_USED': 0.0056, 'QUERY_TEXT': 'SELECT complex_etl_job...'},
        {'QUERY_ID': 'xyz98765', 'WAREHOUSE_NAME': 'XL', 'EXECUTION_TIME': 2500, 'CREDITS_USED': 0.0001, 'QUERY_TEXT': 'SELECT simple_dashboard_query...'},
        {'QUERY_ID': 'def56789', 'WAREHOUSE_NAME': 'M', 'EXECUTION_TIME': 120000, 'CREDITS_USED': 0.0008, 'QUERY_TEXT': 'SELECT regular_report...'},
        {'QUERY_ID': 'gld11223', 'WAREHOUSE_NAME': 'L', 'EXECUTION_TIME': 300000, 'CREDITS_USED': 0.0066, 'QUERY_TEXT': 'SELECT heavy_join_on_L...'},
    ]
    
    print("--- Simulating AI Bot Workflow (using mock data for simplicity) ---")
    recommendations = warehouse_recommendation(mock_details)
    
    # Formatting for final display
    df = pd.DataFrame(recommendations)
    df['Cost Impact (Cr/Hr Diff)'] = df['Cost Impact (Cr/Hr Diff)'].apply(
        lambda x: f"+{x:.0f}" if x > 0 else (f"{x:.0f}" if x < 0 else "0")
    )
    
    final_output = "\n**Optimization Recommendation Report (SnowWiz Prototype)**\n"
    final_output += df.to_markdown(index=False)
    print(final_output)

# --- End of main.py ---