#!/usr/bin/env python3
"""
Debug ChromaDB HttpClient Connection
"""

import os
import chromadb
from chromadb.config import Settings

def test_chroma_connection():
    """Test ChromaDB HttpClient connection"""
    
    # Get connection details from environment or defaults
    chroma_host = os.getenv("CHROMA_HOST", "localhost")
    chroma_port = int(os.getenv("CHROMA_PORT", "8000"))
    
    print(f"🔍 Testing ChromaDB connection to {chroma_host}:{chroma_port}")
    print("=" * 60)
    
    try:
        # Test 1: Basic connection
        print(f"1. Creating HttpClient...")
        client = chromadb.HttpClient(
            host=chroma_host,
            port=chroma_port,
            settings=Settings(anonymized_telemetry=False)
        )
        print(f"✅ HttpClient created successfully")
        
        # Test 2: Heartbeat/health check
        print(f"2. Testing heartbeat...")
        heartbeat = client.heartbeat()
        print(f"✅ Heartbeat successful: {heartbeat}")
        
        # Test 3: List collections
        print(f"3. Listing collections...")
        collections = client.list_collections()
        print(f"✅ Collections listed: {len(collections)} found")
        for collection in collections:
            print(f"   - {collection.name}: {collection.count()} items")
        
        # Test 4: Get or create collection
        print(f"4. Testing collection access...")
        collection = client.get_or_create_collection(
            name="test_connection",
            metadata={"description": "Test connection collection"}
        )
        print(f"✅ Collection access successful: {collection.name}")
        
        # Test 5: Basic operations
        print(f"5. Testing basic operations...")
        
        # Add a test document
        collection.add(
            documents=["This is a test document"],
            metadatas=[{"test": "connection"}],
            ids=["test_doc_1"]
        )
        print(f"✅ Document added successfully")
        
        # Query the document
        results = collection.query(
            query_texts=["test document"],
            n_results=1
        )
        print(f"✅ Query successful: {len(results['ids'][0])} results")
        
        # Clean up - delete test document
        collection.delete(ids=["test_doc_1"])
        print(f"✅ Test document deleted")
        
        print(f"\n🎉 All ChromaDB connection tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ ChromaDB connection failed: {e}")
        print(f"❌ Error type: {type(e).__name__}")
        
        # Additional troubleshooting info
        print(f"\n🔧 Troubleshooting:")
        print(f"   - Check if ChromaDB server is running:")
        print(f"     docker run -p 8000:8000 chromadb/chroma")
        print(f"   - Or start with: chroma run --host 0.0.0.0 --port 8000")
        print(f"   - Test direct HTTP: curl http://{chroma_host}:{chroma_port}/api/v2/heartbeat")
        
        return False

def test_environment_variables():
    """Test environment variable setup"""
    print(f"\n🌍 Environment Variables:")
    print(f"   CHROMA_HOST: {os.getenv('CHROMA_HOST', 'NOT SET (default: localhost)')}")
    print(f"   CHROMA_PORT: {os.getenv('CHROMA_PORT', 'NOT SET (default: 8000)')}")

if __name__ == "__main__":
    test_environment_variables()
    test_chroma_connection()