#!/usr/bin/env python3
"""
Quick test of the chatbot with mock queries
"""

import sys
import os
import re
from typing import List

# Simulate user interaction
print("Testing chatbot with mock Snowflake connector...\n")

# Add paths
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'gemini'))

# Import from RAG main (not gemini main)
import importlib.util
spec = importlib.util.spec_from_file_location(
    "rag_main", 
    os.path.join(os.path.dirname(__file__), "main.py")
)
rag_main = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rag_main)

extract_query_ids = rag_main.extract_query_ids
check_warehouse_recommendations = rag_main.check_warehouse_recommendations

# Test 1: Extract query IDs
test_queries = [
    "What's the warehouse recommendation for query ID test_abc12345?",
    "Optimize warehouse for queries test_abc12345 and test_xyz98765",
    "Check query test_def56789"
]

print("="*70)
print("Test 1: Query ID Extraction")
print("="*70)
for query in test_queries:
    ids = extract_query_ids(query)
    print(f"\nQuery: {query}")
    print(f"Extracted IDs: {ids}")

# Test 2: Get recommendations
print("\n" + "="*70)
print("Test 2: Get Warehouse Recommendations")
print("="*70)

test_id = "test_abc12345"
print(f"\nTesting with query ID: {test_id}")
result = check_warehouse_recommendations([test_id])
print(result)

# Test 3: Multiple IDs
print("\n" + "="*70)
print("Test 3: Multiple Query IDs")
print("="*70)

test_ids = ["test_abc12345", "test_xyz98765"]
print(f"\nTesting with query IDs: {test_ids}")
result = check_warehouse_recommendations(test_ids)
print(result)

print("\n" + "="*70)
print("✅ All tests completed successfully!")
print("="*70)
print("\n💡 Now run: uv run main.py")
print("   Then ask: What's the warehouse recommendation for query ID test_abc12345?")
