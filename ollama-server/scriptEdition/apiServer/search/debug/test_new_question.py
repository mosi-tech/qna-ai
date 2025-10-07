#!/usr/bin/env python3
"""
Test similarity with new question: "move from TQQQ -> QQQ when QQQ drawdown is less than 2%"
"""

import os
import chromadb
from chromadb.config import Settings
from chromadb.utils.embedding_functions.ollama_embedding_function import (
    OllamaEmbeddingFunction,
)

def test_new_question_similarity():
    """Test similarity with the new question"""
    
    print("🔍 Testing Similarity with New Question")
    print("=" * 60)
    
    # Original questions from our test
    original_q1 = "What if I buy QQQ into VOO every month when rolling monthly return goes below -2%?"
    original_q2 = "What if I bought TSLA into AAPL every month when rolling monthly return is less than -2%?"
    
    # New question to test
    new_question = "move from TQQQ -> QQQ when QQQ drawdown is less than 2%"
    
    print(f"📝 Original Q1: {original_q1}")
    print(f"📝 Original Q2: {original_q2}")
    print(f"🆕 New Question: {new_question}")
    print()
    
    # Setup ChromaDB with Ollama embeddings
    host = os.getenv("CHROMA_HOST", "localhost")
    port = int(os.getenv("CHROMA_PORT", "8050"))
    
    client = chromadb.HttpClient(host=host, port=port, settings=Settings(anonymized_telemetry=False))
    
    # Setup Ollama embedding
    ollama_ef = OllamaEmbeddingFunction(
        url="http://localhost:11434",
        model_name="qwen3-embedding",
    )
    
    # Create collection
    try:
        client.delete_collection("new_question_test")
    except:
        pass
    
    collection = client.create_collection(
        name="new_question_test",
        embedding_function=ollama_ef
    )
    
    # Add original questions with semantic enrichment
    documents = [
        f"""
        ORIGINAL_QUESTION: {original_q1}
        SEMANTIC_MEANING: Analysis of tactical asset rotation strategy where investor switches from one asset to another when the first asset's monthly performance falls below a negative threshold. This is a momentum-based rebalancing approach that moves capital from underperforming to target assets based on rolling performance metrics.
        KEY_CONCEPTS: tactical asset rotation | monthly performance threshold | momentum-based rebalancing | underperformance trigger | rolling return analysis | systematic switching strategy | negative performance criterion
        FUNCTION: analyze_qqq_voo_rotation_strategy
        """,
        f"""
        ORIGINAL_QUESTION: {original_q2}
        SEMANTIC_MEANING: Evaluation of momentum-driven asset allocation strategy involving systematic rotation from one equity to another when monthly returns drop below specified negative threshold. Strategy focuses on moving capital away from underperforming assets to target holdings based on rolling performance evaluation.
        KEY_CONCEPTS: momentum-driven allocation | systematic asset rotation | monthly return threshold | underperformance trigger | rolling performance evaluation | equity switching strategy | negative return criterion
        FUNCTION: analyze_tsla_aapl_rotation_strategy
        """
    ]
    
    collection.add(
        documents=documents,
        metadatas=[
            {"question": original_q1, "function": "analyze_qqq_voo_rotation_strategy"},
            {"question": original_q2, "function": "analyze_tsla_aapl_rotation_strategy"}
        ],
        ids=["q1", "q2"]
    )
    
    print("✅ Added original questions to ChromaDB")
    print()
    
    # Test similarity with new question
    print("🔍 Testing similarity with new question...")
    print("-" * 50)
    
    # Generate semantic representation for new question (manually created)
    new_question_semantics = {
        "semantic_meaning": "Strategy for transitioning from leveraged ETF to underlying ETF based on drawdown threshold of the underlying asset. Involves de-leveraging when underlying asset experiences modest decline to reduce volatility exposure.",
        "key_concepts": [
            "leveraged ETF transition",
            "de-leveraging strategy", 
            "drawdown threshold",
            "volatility reduction",
            "underlying asset performance",
            "risk management rotation"
        ]
    }
    
    # Test different search approaches
    search_queries = [
        ("Direct Question", new_question),
        ("Semantic Meaning", new_question_semantics["semantic_meaning"]),
        ("Key Concepts", " | ".join(new_question_semantics["key_concepts"])),
        ("Combined", f"{new_question} {new_question_semantics['semantic_meaning']}")
    ]
    
    print("Search Results:")
    for query_name, query_text in search_queries:
        results = collection.query(
            query_texts=[query_text],
            n_results=2,
            include=["documents", "metadatas", "distances"]
        )
        
        print(f"\n{query_name}:")
        for i, (doc_id, metadata, distance) in enumerate(zip(
            results['ids'][0], 
            results['metadatas'][0], 
            results['distances'][0]
        )):
            similarity = 1 - distance
            original_q = metadata['question'][:80] + "..." if len(metadata['question']) > 80 else metadata['question']
            print(f"  {i+1}. Similarity: {similarity:.4f} | {original_q}")
    
    # Analysis
    print(f"\n🧠 Semantic Analysis:")
    print("=" * 40)
    
    print("New Question Concepts:")
    for concept in new_question_semantics["key_concepts"]:
        print(f"  - {concept}")
    
    print(f"\nKey Differences from Original Questions:")
    print(f"  🔄 Asset Type: TQQQ (leveraged) vs QQQ/VOO/TSLA/AAPL (regular)")
    print(f"  📊 Metric: Drawdown vs Monthly Return")
    print(f"  🎯 Direction: De-leveraging vs Asset rotation")
    print(f"  ⚡ Trigger: 2% drawdown vs -2% monthly return")
    print(f"  🎲 Strategy: Risk reduction vs Momentum switching")
    
    print(f"\nSimilarities:")
    print(f"  ✅ Threshold-based switching")
    print(f"  ✅ Systematic rebalancing")
    print(f"  ✅ Performance-driven decisions")
    print(f"  ✅ Two-asset strategy")
    
    # Cleanup
    client.delete_collection("new_question_test")
    
    print(f"\n🎯 CONCLUSION:")
    print(f"The new question has MODERATE similarity to the originals")
    print(f"- Similar strategic framework (threshold-based switching)")
    print(f"- Different focus (de-leveraging vs momentum rotation)")
    print(f"- Different metrics (drawdown vs monthly returns)")

if __name__ == "__main__":
    test_new_question_similarity()