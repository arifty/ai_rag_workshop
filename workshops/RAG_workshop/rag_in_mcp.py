from fastmcp import FastMCP
import chromadb
from typing import List, Dict, Any
import os
import sys

# Import warehouse recommendation functionality
sys.path.insert(0, os.path.dirname(__file__))
try:
    from gemini.main import warehouse_recommendation
    # Try real connector first, fall back to mock
    try:
        from gemini.agents.snowflake_connector import SnowflakeConnector
    except Exception:
        from gemini.agents.mock_snowflake_connector import MockSnowflakeConnector as SnowflakeConnector
    SNOWFLAKE_AVAILABLE = True
except ImportError:
    SNOWFLAKE_AVAILABLE = False
    print("⚠️ Snowflake integration not available")

# Initialize FastMCP
mcp = FastMCP("ChromaDB RAG Server")

chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_or_create_collection("knowledge_base")

@mcp.tool()
def search_knowledge_base(query: str, n_results: int = 5) -> Dict[str, Any]:
    """
    Search the ChromaDB knowledge base for relevant documents.
    
    Args:
        query: The search query
        n_results: Number of results to return (default: 5)
    
    Returns:
        Dictionary containing documents, distances, and metadata
    """
    results = collection.query(
        query_texts=[query],
        n_results=n_results
    )
    
    formatted_results = []
    for i in range(len(results['documents'][0])):
        formatted_results.append({
            "document": results['documents'][0][i],
            "distance": results['distances'][0][i],
            "metadata": results['metadatas'][0][i] if results['metadatas'] else None,
            "id": results['ids'][0][i]
        })
    
    return {
        "query": query,
        "results": formatted_results,
        "count": len(formatted_results)
    }

@mcp.tool()
def add_document(text: str, metadata: Dict[str, str] = None, doc_id: str = None) -> str:
    """
    Add a document to the knowledge base.
    
    Args:
        text: The document text to add
        metadata: Optional metadata dictionary
        doc_id: Optional document ID (will be auto-generated if not provided)
    
    Returns:
        Success message with document ID
    """
    import uuid
    if doc_id is None:
        doc_id = str(uuid.uuid4())
    
    collection.add(
        documents=[text],
        metadatas=[metadata] if metadata else None,
        ids=[doc_id]
    )
    
    return f"Document added successfully with ID: {doc_id}"

@mcp.tool()
def get_collection_stats() -> Dict[str, Any]:
    """
    Get statistics about the knowledge base collection.
    
    Returns:
        Dictionary with collection statistics
    """
    count = collection.count()
    
    return {
        "name": collection.name,
        "document_count": count,
        "metadata": collection.metadata
    }

@mcp.resource("knowledge://documents/{doc_id}")
def get_document(doc_id: str) -> str:
    """Get a specific document by ID"""
    result = collection.get(ids=[doc_id])
    if result['documents']:
        return result['documents'][0]
    return f"Document {doc_id} not found"

@mcp.tool()
def get_warehouse_recommendations(query_ids: List[str]) -> Dict[str, Any]:
    """
    Get warehouse optimization recommendations for Snowflake query IDs.
    
    Args:
        query_ids: List of Snowflake query IDs to analyze
    
    Returns:
        Dictionary with recommendations for warehouse sizing and cost optimization
    """
    if not SNOWFLAKE_AVAILABLE:
        return {
            "error": "Snowflake integration not available",
            "message": "Missing dependencies or configuration"
        }
    
    try:
        # Initialize Snowflake connector
        connector = SnowflakeConnector(config_path="gemini/config/snowflake_creds.json")
        if not connector.conn:
            return {
                "error": "Snowflake connection failed",
                "message": "Unable to connect to Snowflake. Check credentials."
            }
        
        # Get query details
        query_details = connector.get_query_details(query_ids)
        connector.close()
        
        if not query_details:
            return {
                "error": "No data found",
                "message": f"No query details found for IDs: {', '.join(query_ids)}"
            }
        
        # Get recommendations
        recommendations = warehouse_recommendation(query_details)
        
        return {
            "success": True,
            "query_count": len(recommendations),
            "recommendations": recommendations
        }
        
    except Exception as e:
        return {
            "error": "Processing failed",
            "message": str(e)
        }

if __name__ == "__main__":
    mcp.run()