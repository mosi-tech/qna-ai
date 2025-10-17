#!/usr/bin/env python3
"""
ChromaDB Browser - Simple script to inspect ChromaDB contents
"""

import os
import sys
import json
from datetime import datetime

# Add search directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'search'))

try:
    from search.library import AnalysisLibrary
    
    def browse_chroma():
        """Browse ChromaDB contents"""
        try:
            # Connect to ChromaDB
            print("🔍 Connecting to ChromaDB...")
            library = AnalysisLibrary()
            
            # Get basic stats
            stats = library.get_stats()
            print(f"📊 Database Stats: {stats}")
            
            # List all collections
            collections = library.client.list_collections()
            print(f"\n📁 Collections: {len(collections)}")
            for collection in collections:
                print(f"   - {collection.name}: {collection.count()} items")
            
            # Get all analyses from our collection
            print(f"\n📋 Financial Analyses:")
            try:
                results = library.collection.get(
                    include=["documents", "metadatas"]
                )
                
                if results['ids']:
                    for i, (doc_id, metadata, document) in enumerate(zip(
                        results['ids'], 
                        results['metadatas'], 
                        results['documents']
                    )):
                        print(f"\n{i+1}. ID: {doc_id}")
                        print(f"   Question: {metadata.get('question', 'N/A')}")
                        print(f"   Function: {metadata.get('function_name', 'N/A')}")
                        print(f"   Filename: {metadata.get('filename', 'N/A')}")
                        print(f"   Created: {metadata.get('created_date', 'N/A')}")
                        print(f"   Usage Count: {metadata.get('usage_count', 0)}")
                        print(f"   Document Preview: {document[:100]}...")
                else:
                    print("   No analyses found in database")
                    
            except Exception as e:
                print(f"   ❌ Error fetching analyses: {e}")
            
            # Test search functionality
            print(f"\n🔍 Testing Search (query: 'AAPL'):")
            try:
                search_result = library.search_similar("AAPL", top_k=3, similarity_threshold=0.1)
                if search_result.get("success") and search_result.get("analyses"):
                    for i, analysis in enumerate(search_result["analyses"], 1):
                        print(f"   {i}. {analysis['function_name']} (similarity: {analysis['similarity']:.3f})")
                        print(f"      Question: {analysis['question'][:80]}...")
                else:
                    print("   No similar analyses found")
            except Exception as e:
                print(f"   ❌ Search error: {e}")
                
        except Exception as e:
            print(f"❌ Connection error: {e}")
            print("💡 Make sure ChromaDB server is running:")
            print("   docker run -p 8000:8000 chromadb/chroma")
            return False
            
        return True
    
    if __name__ == "__main__":
        print("🚀 ChromaDB Browser")
        print("=" * 50)
        browse_chroma()

except ImportError as e:
    print(f"❌ Import error: {e}")
    print("💡 Make sure you're in the apiServer directory and have chromadb installed")
    print("   cd apiServer && pip install chromadb")