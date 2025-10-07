#!/usr/bin/env python3
"""
ChromaDB Document Deletion Examples
"""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'search'))

from search.library import AnalysisLibrary

def delete_examples():
    """Examples of different deletion methods in ChromaDB"""
    
    # Connect to ChromaDB
    library = AnalysisLibrary()
    collection = library.collection
    
    print("🗑️  ChromaDB Deletion Methods")
    print("=" * 50)
    
    # Method 1: Delete by IDs
    print("\n1. Delete by Document IDs:")
    try:
        # Get all current documents first
        results = collection.get(include=["metadatas"])
        if results['ids']:
            print(f"   Current documents: {len(results['ids'])}")
            for i, (doc_id, metadata) in enumerate(zip(results['ids'], results['metadatas'])):
                print(f"   {i+1}. {doc_id}: {metadata.get('function_name', 'N/A')}")
            
            # Delete specific documents by ID
            # ids_to_delete = [results['ids'][0]]  # Delete first document
            # collection.delete(ids=ids_to_delete)
            # print(f"   ✅ Would delete: {ids_to_delete}")
            print("   💡 Uncomment lines above to actually delete")
        else:
            print("   No documents to delete")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Method 2: Delete by metadata filter
    print("\n2. Delete by Metadata Filter:")
    try:
        # Delete all analyses for a specific function
        # collection.delete(where={"function_name": "analyze_aapl_dip_buying_strategy"})
        print("   💡 Example: collection.delete(where={'function_name': 'specific_function'})")
        print("   💡 This would delete all documents with that function name")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Method 3: Delete by query results
    print("\n3. Delete by Query Results:")
    try:
        # Find documents to delete based on content similarity
        query_results = collection.query(
            query_texts=["AAPL dip buying"],
            n_results=5,
            include=["metadatas"]
        )
        
        if query_results['ids'][0]:
            print(f"   Found {len(query_results['ids'][0])} similar documents:")
            for doc_id, metadata in zip(query_results['ids'][0], query_results['metadatas'][0]):
                print(f"   - {doc_id}: {metadata.get('question', 'N/A')[:50]}...")
            
            # Uncomment to delete these results
            # collection.delete(ids=query_results['ids'][0])
            print("   💡 Uncomment line above to delete these documents")
        else:
            print("   No documents found matching query")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Method 4: Delete entire collection
    print("\n4. Delete Entire Collection:")
    print("   💡 library.client.delete_collection('financial_analyses')")
    print("   ⚠️  This deletes ALL documents in the collection!")
    
    # Method 5: Peek and selective delete
    print("\n5. Peek and Selective Delete:")
    try:
        # Peek at a few documents
        peek_results = collection.peek(limit=3)
        if peek_results['ids']:
            print(f"   Peeking at {len(peek_results['ids'])} documents:")
            for doc_id, metadata in zip(peek_results['ids'], peek_results['metadatas']):
                print(f"   - {doc_id}: {metadata.get('function_name', 'N/A')}")
        else:
            print("   No documents to peek at")
    except Exception as e:
        print(f"   ❌ Error: {e}")

def interactive_delete():
    """Interactive deletion interface"""
    
    library = AnalysisLibrary()
    collection = library.collection
    
    print("\n🔍 Interactive Document Deletion")
    print("=" * 40)
    
    try:
        # List all documents
        results = collection.get(include=["metadatas"])
        
        if not results['ids']:
            print("No documents found in the collection.")
            return
        
        print(f"Found {len(results['ids'])} documents:")
        for i, (doc_id, metadata) in enumerate(zip(results['ids'], results['metadatas'])):
            question = metadata.get('question', 'N/A')
            function_name = metadata.get('function_name', 'N/A')
            print(f"{i+1}. {doc_id}")
            print(f"   Function: {function_name}")
            print(f"   Question: {question[:80]}{'...' if len(question) > 80 else ''}")
            print()
        
        # Uncomment for actual interactive deletion
        """
        while True:
            choice = input("Enter document number to delete (or 'q' to quit): ").strip()
            if choice.lower() == 'q':
                break
            
            try:
                index = int(choice) - 1
                if 0 <= index < len(results['ids']):
                    doc_id = results['ids'][index]
                    collection.delete(ids=[doc_id])
                    print(f"✅ Deleted document: {doc_id}")
                    
                    # Refresh list
                    results = collection.get(include=["metadatas"])
                    if not results['ids']:
                        print("No more documents remaining.")
                        break
                else:
                    print("Invalid document number.")
            except ValueError:
                print("Please enter a valid number.")
        """
        print("💡 Uncomment the interactive section above for actual deletion")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    delete_examples()
    interactive_delete()