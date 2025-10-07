#!/usr/bin/env python3
"""
Test Migration to Ollama Embeddings
"""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'search'))

from search.library import AnalysisLibrary

def test_migration():
    """Test migrating to Ollama embeddings"""
    
    print("🔄 Testing Migration to Ollama Embeddings")
    print("=" * 50)
    
    # Set environment variables
    os.environ["CHROMA_HOST"] = "localhost"
    os.environ["CHROMA_PORT"] = "8050"
    os.environ["OLLAMA_BASE_URL"] = "http://localhost:11434"
    os.environ["OLLAMA_EMBEDDING_MODEL"] = "qwen3-embedding"
    
    try:
        # Initialize library
        library = AnalysisLibrary()
        
        # Check if Ollama embeddings are available
        if library.embedding_function:
            print("✅ Ollama embeddings available, migrating...")
            
            # Migrate to Ollama embeddings
            migration_result = library.migrate_to_ollama_embeddings()
            
            if migration_result["success"]:
                print(f"🎉 Migration successful!")
                print(f"   Migrated: {migration_result.get('migrated_count', 0)} documents")
                print(f"   Message: {migration_result.get('message', '')}")
                
                # Test similarity search after migration
                print(f"\n🔍 Testing similarity search with Ollama embeddings...")
                
                test_query = "move from TQQQ -> QQQ when QQQ drawdown is less than 2%"
                results = library.search_similar(test_query, top_k=3, similarity_threshold=0.3)
                
                if results["success"] and results["found_similar"]:
                    print(f"✅ Found {len(results['analyses'])} similar analyses:")
                    for analysis in results["analyses"]:
                        print(f"   - {analysis['similarity']:.3f}: {analysis['function_name']}")
                        print(f"     {analysis['question'][:60]}...")
                else:
                    print(f"⚠️ No similar analyses found (threshold: 0.3)")
                    
                return True
            else:
                print(f"❌ Migration failed: {migration_result['error']}")
                return False
        else:
            print("⚠️ Ollama embeddings not available, keeping existing setup")
            return True
            
    except Exception as e:
        print(f"❌ Error during migration: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_migration()