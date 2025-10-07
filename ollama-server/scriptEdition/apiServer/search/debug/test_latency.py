#!/usr/bin/env python3
"""
Test ChromaDB + Ollama Embedding Latency
"""

import time
import os
import chromadb
from chromadb.config import Settings
from chromadb.utils.embedding_functions.ollama_embedding_function import (
    OllamaEmbeddingFunction,
)

def test_latency():
    """Test latency of different operations"""
    
    print("⏱️  ChromaDB + Ollama Embedding Latency Test")
    print("=" * 50)
    
    # Setup
    host = os.getenv("CHROMA_HOST", "localhost")
    port = int(os.getenv("CHROMA_PORT", "8050"))
    
    start = time.time()
    client = chromadb.HttpClient(host=host, port=port, settings=Settings(anonymized_telemetry=False))
    client_time = time.time() - start
    print(f"ChromaDB client setup: {client_time:.3f}s")
    
    # Setup Ollama embedding
    start = time.time()
    ollama_ef = OllamaEmbeddingFunction(
        url="http://localhost:11434",
        model_name="qwen3-embedding",
    )
    embedding_setup_time = time.time() - start
    print(f"Ollama embedding setup: {embedding_setup_time:.3f}s")
    
    # Create collection
    start = time.time()
    try:
        client.delete_collection("latency_test")
    except:
        pass
    
    collection = client.create_collection(
        name="latency_test",
        embedding_function=ollama_ef
    )
    collection_time = time.time() - start
    print(f"Collection creation: {collection_time:.3f}s")
    
    # Test document - realistic financial analysis
    test_doc = """
    ORIGINAL_QUESTION: What if I buy QQQ into VOO every month when rolling monthly return goes below -2%?
    
    SEMANTIC_MEANING: Analysis of tactical asset rotation strategy where investor switches from one asset to another when the first asset's monthly performance falls below a negative threshold. This is a momentum-based rebalancing approach that moves capital from underperforming to target assets based on rolling performance metrics.
    
    KEY_CONCEPTS: tactical asset rotation | monthly performance threshold | momentum-based rebalancing | underperformance trigger | rolling return analysis | systematic switching strategy | negative performance criterion
    
    IMPLEMENTATION: Analyzes tactical rotation from QQQ to VOO based on monthly performance thresholds
    
    FUNCTION: analyze_qqq_voo_rotation_strategy
    """
    
    # Add document (includes embedding generation)
    start = time.time()
    collection.add(
        documents=[test_doc],
        metadatas=[{"function_name": "test_function"}],
        ids=["test_1"]
    )
    add_time = time.time() - start
    print(f"Document add (with embedding): {add_time:.3f}s")
    
    # Test different query types and sizes
    queries = [
        ("Short query", "TSLA AAPL rotation"),
        ("Medium query", "What if I bought TSLA into AAPL every month when rolling monthly return is less than -2%?"),
        ("Long semantic query", "Evaluation of momentum-driven asset allocation strategy involving systematic rotation from one equity to another when monthly returns drop below specified negative threshold"),
        ("Mixed query", "What if I bought TSLA into AAPL every month when rolling monthly return is less than -2%? Evaluation of momentum-driven asset allocation strategy involving systematic rotation")
    ]
    
    print(f"\n🔍 Search Latency Tests:")
    print("-" * 40)
    
    total_search_time = 0
    num_searches = 0
    
    for query_name, query_text in queries:
        # Warm up (first query is often slower)
        collection.query(query_texts=[query_text], n_results=1)
        
        # Actual timing
        times = []
        for i in range(3):  # Run 3 times for average
            start = time.time()
            results = collection.query(
                query_texts=[query_text],
                n_results=5,
                include=["documents", "metadatas", "distances"]
            )
            query_time = time.time() - start
            times.append(query_time)
            
        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)
        
        print(f"{query_name:18} | Avg: {avg_time:.3f}s | Range: {min_time:.3f}-{max_time:.3f}s")
        
        total_search_time += avg_time
        num_searches += 1
    
    avg_search_time = total_search_time / num_searches
    
    print("-" * 40)
    print(f"Average search time: {avg_search_time:.3f}s")
    
    # Test batch operations
    print(f"\n📦 Batch Operations:")
    print("-" * 30)
    
    # Add 10 documents
    batch_docs = [f"Document {i}: Financial analysis example with various content length and complexity" for i in range(10)]
    batch_ids = [f"batch_{i}" for i in range(10)]
    batch_metadata = [{"type": "batch_test", "index": i} for i in range(10)]
    
    start = time.time()
    collection.add(
        documents=batch_docs,
        metadatas=batch_metadata,
        ids=batch_ids
    )
    batch_add_time = time.time() - start
    per_doc_time = batch_add_time / 10
    print(f"Batch add (10 docs): {batch_add_time:.3f}s ({per_doc_time:.3f}s per doc)")
    
    # Batch search
    start = time.time()
    results = collection.query(
        query_texts=["financial analysis"],
        n_results=10
    )
    batch_search_time = time.time() - start
    print(f"Search 10 results: {batch_search_time:.3f}s")
    
    # Collection stats
    start = time.time()
    count = collection.count()
    count_time = time.time() - start
    print(f"Collection count ({count} docs): {count_time:.3f}s")
    
    # Cleanup
    client.delete_collection("latency_test")
    
    print(f"\n📊 SUMMARY:")
    print("=" * 30)
    print(f"Setup overhead: {client_time + embedding_setup_time + collection_time:.3f}s")
    print(f"Per document add: {per_doc_time:.3f}s")
    print(f"Average search: {avg_search_time:.3f}s")
    print(f"Search throughput: ~{1/avg_search_time:.1f} queries/second")
    
    # Practical implications
    if avg_search_time < 0.1:
        print(f"🚀 EXCELLENT: Sub-100ms search is very fast for production")
    elif avg_search_time < 0.5:
        print(f"✅ GOOD: Sub-500ms search is acceptable for most use cases")
    elif avg_search_time < 1.0:
        print(f"⚠️  ACCEPTABLE: Sub-1s search may feel slightly slow")
    else:
        print(f"❌ SLOW: >1s search needs optimization")

if __name__ == "__main__":
    test_latency()