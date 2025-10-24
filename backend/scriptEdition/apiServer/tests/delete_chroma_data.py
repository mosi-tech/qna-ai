#!/usr/bin/env python3
"""
Delete all ChromaDB data
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from search.library import AnalysisLibrary

def delete_all_chroma_data():
    """Delete all documents from ChromaDB collection"""
    
    try:
        print("🗑️  Deleting all ChromaDB data...")
        
        # Connect to ChromaDB
        library = AnalysisLibrary()
        collection = library.collection
        
        # Get current count
        results = collection.get(include=["metadatas"])
        doc_count = len(results['ids'])
        
        if doc_count == 0:
            print("✅ No documents found - collection is already empty")
            return
        
        print(f"📊 Found {doc_count} documents to delete")
        
        # Delete all documents
        if results['ids']:
            collection.delete(ids=results['ids'])
            print(f"✅ Successfully deleted {doc_count} documents")
        
        # Verify deletion
        verify_results = collection.get()
        remaining_count = len(verify_results['ids'])
        
        if remaining_count == 0:
            print("✅ Verification: Collection is now empty")
        else:
            print(f"⚠️  Warning: {remaining_count} documents still remain")
            
    except Exception as e:
        print(f"❌ Error deleting ChromaDB data: {e}")
        return False
    
    return True

def delete_entire_collection():
    """Delete the entire collection (more thorough)"""
    
    try:
        print("🗑️  Deleting entire ChromaDB collection...")
        
        library = AnalysisLibrary()
        
        # Delete the entire collection
        library.client.delete_collection("financial_analyses")
        print("✅ Successfully deleted entire 'financial_analyses' collection")
        
        # The collection will be recreated automatically on next use
        print("💡 Collection will be recreated automatically when needed")
        
    except Exception as e:
        print(f"❌ Error deleting collection: {e}")
        return False
    
    return True

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Delete ChromaDB data")
    parser.add_argument("--all", action="store_true", help="Delete all documents")
    parser.add_argument("--collection", action="store_true", help="Delete entire collection")
    
    args = parser.parse_args()
    
    if args.collection:
        delete_entire_collection()
    elif args.all:
        delete_all_chroma_data()
    else:
        print("Usage:")
        print("  python delete_chroma_data.py --all         # Delete all documents")
        print("  python delete_chroma_data.py --collection  # Delete entire collection")