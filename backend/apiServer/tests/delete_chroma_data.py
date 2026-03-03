#!/usr/bin/env python3
"""
Delete all ChromaDB data
"""

import os
import sys

# Add backend directory to path for imports
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from shared.analyze.search.library import AnalysisLibrary

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

def delete_by_document_id(document_ids):
    """Delete specific documents by their IDs"""
    
    try:
        print(f"🗑️  Deleting documents by ID: {document_ids}")
        
        # Connect to ChromaDB
        library = AnalysisLibrary()
        collection = library.collection
        
        # Convert single ID to list
        if isinstance(document_ids, str):
            document_ids = [document_ids]
        
        # Check which documents exist
        existing_results = collection.get(ids=document_ids, include=["metadatas"])
        existing_ids = existing_results['ids']
        
        if not existing_ids:
            print("❌ No documents found with the specified IDs")
            return False
        
        print(f"📊 Found {len(existing_ids)} documents to delete:")
        for i, doc_id in enumerate(existing_ids):
            metadata = existing_results['metadatas'][i] if existing_results['metadatas'] else {}
            response_type = metadata.get('response_type', 'Unknown')
            question = metadata.get('original_question', 'No question')[:60]
            print(f"  • {doc_id}: {response_type} - {question}...")
        
        # Delete the documents
        collection.delete(ids=existing_ids)
        print(f"✅ Successfully deleted {len(existing_ids)} documents")
        
        # Verify deletion
        verify_results = collection.get(ids=document_ids)
        remaining_ids = verify_results['ids']
        
        if not remaining_ids:
            print("✅ Verification: All specified documents have been deleted")
        else:
            print(f"⚠️  Warning: {len(remaining_ids)} documents still remain: {remaining_ids}")
            
    except Exception as e:
        print(f"❌ Error deleting documents by ID: {e}")
        return False
    
    return True

def list_documents(limit=10):
    """List documents in the collection with their IDs"""
    
    try:
        print("📋 Listing documents in ChromaDB collection...")
        
        # Connect to ChromaDB
        library = AnalysisLibrary()
        collection = library.collection
        
        # Get documents with metadata
        results = collection.get(include=["metadatas"], limit=limit)
        doc_count = len(results['ids'])
        
        if doc_count == 0:
            print("✅ No documents found - collection is empty")
            return
        
        print(f"📊 Found {doc_count} documents (showing first {min(limit, doc_count)}):")
        print()
        
        for i, doc_id in enumerate(results['ids']):
            metadata = results['metadatas'][i] if results['metadatas'] else {}
            response_type = metadata.get('response_type', 'Unknown')
            question = metadata.get('original_question', 'No question')[:60]
            timestamp = metadata.get('timestamp', 'No timestamp')
            
            print(f"  {i+1}. ID: {doc_id}")
            print(f"     Type: {response_type}")
            print(f"     Question: {question}...")
            print(f"     Created: {timestamp}")
            print()
            
    except Exception as e:
        print(f"❌ Error listing documents: {e}")
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
    
    parser = argparse.ArgumentParser(description="Manage ChromaDB data")
    parser.add_argument("--all", action="store_true", help="Delete all documents")
    parser.add_argument("--collection", action="store_true", help="Delete entire collection")
    parser.add_argument("--id", "--ids", nargs='+', dest="document_ids", help="Delete specific document(s) by ID")
    parser.add_argument("--list", action="store_true", help="List documents with their IDs")
    parser.add_argument("--limit", type=int, default=10, help="Limit for listing documents (default: 10)")
    
    args = parser.parse_args()
    
    if args.collection:
        delete_entire_collection()
    elif args.all:
        delete_all_chroma_data()
    elif args.document_ids:
        delete_by_document_id(args.document_ids)
    elif args.list:
        list_documents(args.limit)
    else:
        print("Usage:")
        print("  python delete_chroma_data.py --all                    # Delete all documents")
        print("  python delete_chroma_data.py --collection             # Delete entire collection")
        print("  python delete_chroma_data.py --id <doc_id>            # Delete specific document by ID")
        print("  python delete_chroma_data.py --ids <id1> <id2> <id3>  # Delete multiple documents by ID")
        print("  python delete_chroma_data.py --list                   # List documents with IDs")
        print("  python delete_chroma_data.py --list --limit 20        # List first 20 documents")
        print("")
        print("Examples:")
        print("  python delete_chroma_data.py --list                   # See available document IDs")
        print("  python delete_chroma_data.py --id abc123              # Delete document with ID 'abc123'")
        print("  python delete_chroma_data.py --ids doc1 doc2 doc3     # Delete multiple documents")