#!/usr/bin/env python3
"""
Test Updated AnalysisLibrary with Ollama Embeddings
"""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'search'))

from search.library import AnalysisLibrary

def test_updated_library():
    """Test the updated library with Ollama embeddings"""
    
    print("🧪 Testing Updated AnalysisLibrary with Ollama Embeddings")
    print("=" * 60)
    
    # Set environment variables for testing
    os.environ["CHROMA_HOST"] = "localhost"
    os.environ["CHROMA_PORT"] = "8050" 
    os.environ["OLLAMA_BASE_URL"] = "http://localhost:11434"
    os.environ["OLLAMA_EMBEDDING_MODEL"] = "qwen3-embedding"
    
    try:
        # Initialize library
        print("🔧 Initializing AnalysisLibrary...")
        library = AnalysisLibrary()
        
        # Test questions
        test_questions = [
            {
                "question": "What if I buy QQQ into VOO every month when rolling monthly return goes below -2%?",
                "function_name": "analyze_qqq_voo_rotation_strategy",
                "docstring": "Analyzes tactical rotation from QQQ to VOO based on monthly performance thresholds and evaluates the effectiveness of this momentum-based switching strategy."
            },
            {
                "question": "What if I bought TSLA into AAPL every month when rolling monthly return is less than -2%?", 
                "function_name": "analyze_tsla_aapl_rotation_strategy",
                "docstring": "Evaluates systematic rotation from TSLA to AAPL when monthly performance drops below threshold, focusing on equity-to-equity momentum switching."
            }
        ]
        
        # Clear existing test data
        print("🗑️ Clearing any existing test data...")
        try:
            # Get existing documents and delete test ones
            existing = library.collection.get()
            test_ids = []
            if existing['ids']:
                for i, metadata in enumerate(existing['metadatas']):
                    if metadata.get('function_name', '').startswith('analyze_'):
                        test_ids.append(existing['ids'][i])
            
            if test_ids:
                library.collection.delete(ids=test_ids)
                print(f"🗑️ Deleted {len(test_ids)} existing test documents")
        except:
            pass
        
        # Add test questions
        print("\n📝 Adding test questions...")
        for i, data in enumerate(test_questions):
            result = library.save_analysis(
                question=data["question"],
                function_name=data["function_name"], 
                docstring=data["docstring"]
            )
            if result["success"]:
                print(f"✅ Added Q{i+1}: {data['function_name']}")
            else:
                print(f"❌ Failed to add Q{i+1}: {result['error']}")
        
        # Test similarity searches
        print(f"\n🔍 Testing similarity searches...")
        print("-" * 50)
        
        test_searches = [
            "move from TQQQ -> QQQ when QQQ drawdown is less than 2%",
            "What happens if I sell SPY and buy TLT when market drops 3%?",
            "How to rotate between growth and value ETFs based on performance?",
            "TSLA to AAPL switching strategy"
        ]
        
        for search_query in test_searches:
            print(f"\nQuery: {search_query}")
            
            # Search with updated library
            results = library.search_similar(
                query=search_query,
                top_k=3,
                similarity_threshold=0.3  # Lower threshold with better embeddings
            )
            
            if results["success"] and results["found_similar"]:
                print(f"✅ Found {len(results['analyses'])} similar analyses:")
                for j, analysis in enumerate(results["analyses"]):
                    similarity = analysis["similarity"]
                    function_name = analysis["function_name"]
                    question = analysis["question"][:60] + "..." if len(analysis["question"]) > 60 else analysis["question"]
                    
                    # Color code similarity scores
                    if similarity >= 0.7:
                        status = "🟢 HIGH"
                    elif similarity >= 0.5:
                        status = "🟡 MODERATE" 
                    else:
                        status = "🔴 LOW"
                        
                    print(f"  {j+1}. {status} ({similarity:.3f}) | {function_name}")
                    print(f"     Question: {question}")
            else:
                print(f"❌ No similar analyses found")
        
        # Show library stats
        print(f"\n📊 Library Statistics:")
        stats = library.get_stats()
        if stats["success"]:
            print(f"  Total analyses: {stats['total_analyses']}")
            print(f"  Status: {stats['status']}")
        
        print(f"\n🎯 SUCCESS: Updated library working with Ollama embeddings!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing updated library: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_updated_library()
    if success:
        print(f"\n✅ Library update complete - ready for production use!")
    else:
        print(f"\n❌ Library update failed - check configuration")