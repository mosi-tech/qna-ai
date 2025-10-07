#!/usr/bin/env python3
"""
Test Script: Generic Semantic Search in ChromaDB
Tests if semantic extraction improves similarity detection for financial questions.
"""

import os
import chromadb
from chromadb.config import Settings
from chromadb.utils.embedding_functions.ollama_embedding_function import (
    OllamaEmbeddingFunction,
)
import json

# Test questions - very similar but different language
QUESTION_1 = "What if I buy QQQ into VOO every month when rolling monthly return goes below -2%?"
QUESTION_2 = "What if I bought TSLA into AAPL every month when rolling monthly return is less than -2%?"

# Pre-generated semantic representations (what LLM would extract)
SEMANTIC_DATA = {
    "question_1": {
        "original_question": QUESTION_1,
        "semantic_meaning": "Analysis of tactical asset rotation strategy where investor switches from one asset to another when the first asset's monthly performance falls below a negative threshold. This is a momentum-based rebalancing approach that moves capital from underperforming to target assets based on rolling performance metrics.",
        "key_concepts": [
            "tactical asset rotation", 
            "monthly performance threshold", 
            "momentum-based rebalancing",
            "underperformance trigger",
            "rolling return analysis",
            "systematic switching strategy",
            "negative performance criterion"
        ],
        "function_name": "analyze_qqq_voo_rotation_strategy",
        "docstring": "Analyzes tactical rotation from QQQ to VOO based on monthly performance thresholds"
    },
    "question_2": {
        "original_question": QUESTION_2,
        "semantic_meaning": "Evaluation of momentum-driven asset allocation strategy involving systematic rotation from one equity to another when monthly returns drop below specified negative threshold. Strategy focuses on moving capital away from underperforming assets to target holdings based on rolling performance evaluation.",
        "key_concepts": [
            "momentum-driven allocation",
            "systematic asset rotation", 
            "monthly return threshold",
            "underperformance trigger",
            "rolling performance evaluation",
            "equity switching strategy", 
            "negative return criterion"
        ],
        "function_name": "analyze_tsla_aapl_rotation_strategy", 
        "docstring": "Evaluates systematic rotation from TSLA to AAPL when monthly performance drops below threshold"
    }
}

def setup_chroma_client():
    """Setup ChromaDB client"""
    host = os.getenv("CHROMA_HOST", "localhost")
    port = int(os.getenv("CHROMA_PORT", "8050"))
    
    print(f"🔗 Connecting to ChromaDB at {host}:{port}")
    
    try:
        client = chromadb.HttpClient(
            host=host,
            port=port,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Test connection
        heartbeat = client.heartbeat()
        print(f"✅ Connected successfully. Heartbeat: {heartbeat}")
        
        return client
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print(f"💡 Make sure ChromaDB is running on {host}:{port}")
        print(f"   Start with: chroma run --host 0.0.0.0 --port {port}")
        return None

def create_enriched_document(data):
    """Create enriched document with semantic information"""
    return f"""
ORIGINAL_QUESTION: {data['original_question']}

SEMANTIC_MEANING: {data['semantic_meaning']}

KEY_CONCEPTS: {' | '.join(data['key_concepts'])}

IMPLEMENTATION: {data['docstring']}

FUNCTION: {data['function_name']}
"""

def check_ollama_model():
    """Check if Ollama and qwen3-embedding model are available"""
    try:
        import requests
        
        # Check if Ollama is running
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            model_names = [model["name"] for model in models]
            
            if any("qwen" in name and "embedding" in name for name in model_names):
                print("✅ Ollama qwen3-embedding model is available")
                return True
            else:
                print("❌ qwen3-embedding model not found in Ollama")
                print(f"Available models: {', '.join(model_names[:5])}")
                print("💡 Run: ollama pull qwen3-embedding")
                return False
        else:
            print("❌ Ollama server not responding")
            return False
            
    except Exception as e:
        print(f"❌ Cannot connect to Ollama: {e}")
        print("💡 Make sure Ollama is running: ollama serve")
        return False

def test_semantic_search():
    """Test the semantic search approach"""
    
    print("🧪 Testing Generic Semantic Search in ChromaDB with Ollama Embeddings")
    print("=" * 70)
    
    # Setup ChromaDB
    client = setup_chroma_client()
    if not client:
        return False
    
    # Create or get collection
    collection_name = "test_semantic_financial_analysis"
    try:
        # Delete existing collection if it exists
        try:
            client.delete_collection(collection_name)
            print(f"🗑️  Deleted existing collection: {collection_name}")
        except:
            pass
        
        # Setup embedding function
        embedding_function = None
        if check_ollama_model():
            try:
                print(f"🔧 Setting up Ollama qwen3-embedding model...")
                embedding_function = OllamaEmbeddingFunction(
                    url="http://localhost:11434",
                    model_name="qwen3-embedding",
                )
                print(f"✅ Ollama embedding function ready")
            except Exception as e:
                print(f"❌ Failed to setup Ollama embeddings: {e}")
                print(f"⚠️  Falling back to default ChromaDB embeddings")
        
        if embedding_function:
            collection = client.create_collection(
                name=collection_name,
                embedding_function=embedding_function,
                metadata={"description": "Test collection with Ollama qwen3-embedding"}
            )
            print(f"✅ Created collection with Ollama embeddings")
        else:
            collection = client.create_collection(
                name=collection_name,
                metadata={"description": "Test collection with default embeddings"}
            )
            print(f"✅ Created collection with default embeddings")
        
    except Exception as e:
        print(f"❌ Failed to create collection: {e}")
        return False
    
    # Step 1: Add first question with semantic enrichment
    print(f"\n📝 Step 1: Adding Question 1 to ChromaDB")
    print(f"Question: {QUESTION_1}")
    
    try:
        q1_data = SEMANTIC_DATA["question_1"]
        enriched_doc = create_enriched_document(q1_data)
        
        collection.add(
            documents=[enriched_doc],
            metadatas=[{
                'original_question': q1_data['original_question'],
                'semantic_summary': q1_data['semantic_meaning'],
                'key_concepts': ' | '.join(q1_data['key_concepts']),  # Convert list to string
                'function_name': q1_data['function_name']
            }],
            ids=["test_analysis_1"]
        )
        
        print(f"✅ Added Question 1 with semantic enrichment")
        print(f"   Key concepts: {', '.join(q1_data['key_concepts'][:3])}...")
        
    except Exception as e:
        print(f"❌ Failed to add document: {e}")
        return False
    
    # Step 2: Search using Question 2
    print(f"\n🔍 Step 2: Searching for Question 2")
    print(f"Query: {QUESTION_2}")
    
    try:
        q2_data = SEMANTIC_DATA["question_2"] 
        
        # Test multiple search approaches
        search_approaches = [
            ("Original Question", QUESTION_2),
            ("Semantic Meaning", q2_data['semantic_meaning']),
            ("Key Concepts", ' '.join(q2_data['key_concepts'])),
            ("Mixed Query", f"{QUESTION_2} {q2_data['semantic_meaning']}")
        ]
        
        print(f"\n📊 Testing different search approaches:")
        print("-" * 50)
        
        best_similarity = 0
        best_approach = None
        
        for approach_name, query_text in search_approaches:
            try:
                results = collection.query(
                    query_texts=[query_text],
                    n_results=1,
                    include=["documents", "metadatas", "distances"]
                )
                
                if results['ids'][0]:  # Found results
                    distance = results['distances'][0][0]
                    similarity = 1 - distance  # Convert distance to similarity
                    
                    print(f"{approach_name:15} | Similarity: {similarity:.4f}")
                    
                    if similarity > best_similarity:
                        best_similarity = similarity
                        best_approach = approach_name
                        
                    # Show details for best result so far
                    if approach_name == "Semantic Meaning":
                        print(f"                | Found: {results['metadatas'][0][0]['function_name']}")
                        print(f"                | Match: QQQ→VOO vs TSLA→AAPL rotation strategies")
                        
                else:
                    print(f"{approach_name:15} | No results found")
                    
            except Exception as e:
                print(f"{approach_name:15} | Error: {e}")
        
        print("-" * 50)
        print(f"🏆 Best approach: {best_approach} (similarity: {best_similarity:.4f})")
        
        # Determine success
        if best_similarity > 0.7:
            print(f"🎉 SUCCESS: High semantic similarity detected!")
            success = True
        elif best_similarity > 0.5:
            print(f"✅ GOOD: Moderate semantic similarity detected")
            success = True
        elif best_similarity > 0.3:
            print(f"⚠️  MARGINAL: Low but detectable similarity")
            success = False
        else:
            print(f"❌ FAILED: No meaningful similarity detected")
            success = False
            
        # Cleanup
        client.delete_collection(collection_name)
        print(f"\n🧹 Cleaned up test collection")
        
        return success
        
    except Exception as e:
        print(f"❌ Search failed: {e}")
        return False

def show_semantic_comparison():
    """Show the semantic representations for comparison"""
    print(f"\n🔬 Semantic Analysis Comparison")
    print("=" * 60)
    
    q1_data = SEMANTIC_DATA["question_1"]
    q2_data = SEMANTIC_DATA["question_2"]
    
    print(f"Question 1: {q1_data['original_question']}")
    print(f"Question 2: {q2_data['original_question']}")
    print()
    
    print("🧠 Semantic Meanings:")
    print(f"Q1: {q1_data['semantic_meaning'][:100]}...")
    print(f"Q2: {q2_data['semantic_meaning'][:100]}...")
    print()
    
    print("🔑 Key Concepts Overlap:")
    concepts1 = set(q1_data['key_concepts'])
    concepts2 = set(q2_data['key_concepts'])
    
    overlap = concepts1.intersection(concepts2)
    unique1 = concepts1 - concepts2  
    unique2 = concepts2 - concepts1
    
    print(f"   Shared ({len(overlap)}): {', '.join(list(overlap)[:3])}...")
    print(f"   Q1 Only ({len(unique1)}): {', '.join(list(unique1)[:2])}...")
    print(f"   Q2 Only ({len(unique2)}): {', '.join(list(unique2)[:2])}...")
    
    concept_similarity = len(overlap) / len(concepts1.union(concepts2))
    print(f"   Concept Overlap: {concept_similarity:.2%}")

if __name__ == "__main__":
    # Show the semantic analysis
    show_semantic_comparison()
    
    # Test the search
    success = test_semantic_search()
    
    print(f"\n{'='*60}")
    if success:
        print(f"🎯 CONCLUSION: Generic semantic extraction WORKS!")
        print(f"   Semantic enrichment successfully detected similarity")
        print(f"   between questions with different language/assets")
    else:
        print(f"🤔 CONCLUSION: Needs tuning")
        print(f"   Semantic approach shows promise but needs optimization")
        print(f"   Consider: better embeddings, lower thresholds, or hybrid approach")