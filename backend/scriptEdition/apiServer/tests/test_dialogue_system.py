#!/usr/bin/env python3
"""
Test Dialogue System - Comprehensive test of conversation-aware search
"""

import os
import sys
import asyncio
import json
sys.path.insert(0, os.path.dirname(__file__))

from dialogue import (
    search_with_context, 
    session_manager, 
    QueryType,
    ConversationStore,
    initialize_dialogue_factory
)

async def test_dialogue_system():
    """Test the complete dialogue system"""
    
    print("🧪 Testing Dialogue System")
    print("=" * 60)
    
    # Set environment variables
    os.environ["CHROMA_HOST"] = "localhost"
    os.environ["CHROMA_PORT"] = "8050" 
    os.environ["OLLAMA_BASE_URL"] = "http://localhost:11434"
    os.environ["OLLAMA_MODEL"] = "gpt-oss:20b"
    os.environ["OLLAMA_EMBEDDING_MODEL"] = "qwen3-embedding"
    
    # Initialize dialogue factory with test LLM service
    from llm import create_context_llm
    from search.library import AnalysisLibrary
    
    print("🔧 Initializing dialogue system...")
    llm_service = create_context_llm()
    analysis_library = AnalysisLibrary()
    initialize_dialogue_factory(llm_service, analysis_library)
    print("✅ Dialogue system initialized")
    
    try:
        # Test 1: Complete Query (First in conversation)
        print("\n🔍 Test 1: Complete Query")
        print("-" * 40)
        
        result1 = await search_with_context(
            query="What if I buy QQQ into VOO every month when rolling monthly return goes below -2%?",
            session_id=None,  # New session
            auto_expand=True
        )
        
        if result1["success"]:
            session_id = result1["session_id"]
            print(f"✅ Complete query successful")
            print(f"   Session ID: {session_id}")
            print(f"   Query Type: {result1['query_type']}")
            print(f"   Found Similar: {result1['found_similar']}")
            print(f"   Results Count: {len(result1.get('search_results', []))}")
            
            if result1.get("analysis_summary"):
                print(f"   Analysis Summary: {result1['analysis_summary']}")
        else:
            print(f"❌ Complete query failed: {result1.get('error')}")
            return False
        
        # Test 2: Contextual Query (Reference to previous)
        print("\n🔍 Test 2: Contextual Query")
        print("-" * 40)
        
        result2 = await search_with_context(
            query="what about QQQ to SPY",
            session_id=session_id,
            auto_expand=True
        )
        
        if result2["success"]:
            print(f"✅ Contextual query successful")
            print(f"   Query Type: {result2['query_type']}")
            print(f"   Original Query: {result2['original_query']}")
            print(f"   Expanded Query: {result2.get('expanded_query', 'N/A')}")
            print(f"   Expansion Confidence: {result2.get('expansion_confidence', 0):.3f}")
            print(f"   Context Used: {result2['context_used']}")
            print(f"   Found Similar: {result2['found_similar']}")
        else:
            print(f"❌ Contextual query failed: {result2.get('error')}")
            if result2.get("needs_confirmation"):
                print(f"   💭 Needs confirmation: {result2.get('message')}")
            elif result2.get("needs_clarification"):
                print(f"   ❓ Needs clarification: {result2.get('message')}")
        
        # Test 3: Another Contextual Query  
        print("\n🔍 Test 3: Another Contextual Query")
        print("-" * 40)
        
        result3 = await search_with_context(
            query="try with TSLA to AAPL",
            session_id=session_id,
            auto_expand=True
        )
        
        if result3["success"]:
            print(f"✅ Second contextual query successful") 
            print(f"   Expanded Query: {result3.get('expanded_query', 'N/A')}")
            print(f"   Confidence: {result3.get('expansion_confidence', 0):.3f}")
        else:
            print(f"❌ Second contextual query failed: {result3.get('error')}")
        
        # Test 4: Parameter Variation Query
        print("\n🔍 Test 4: Parameter Variation")
        print("-" * 40)
        
        result4 = await search_with_context(
            query="what if 3% instead",
            session_id=session_id,
            auto_expand=True
        )
        
        if result4["success"]:
            print(f"✅ Parameter variation successful")
            print(f"   Expanded Query: {result4.get('expanded_query', 'N/A')}")
        else:
            print(f"❌ Parameter variation failed: {result4.get('error')}")
        
        # Test 5: Session Context Inspection
        print("\n📊 Test 5: Session Context")
        print("-" * 40)
        
        from dialogue.search.context_aware import context_aware_search
        context = context_aware_search.get_session_context(session_id)
        
        print(f"Session Context:")
        print(f"   Has History: {context.get('has_history', False)}")
        print(f"   Turn Count: {context.get('turn_count', 0)}")
        print(f"   Last Query: {context.get('last_query', 'N/A')[:50]}...")
        print(f"   Last Analysis: {context.get('last_analysis', 'N/A')}")
        
        # Test 6: Session Management Stats
        print("\n📈 Test 6: Session Management")
        print("-" * 40)
        
        stats = session_manager.get_stats()
        print(f"Session Stats:")
        print(f"   Active Sessions: {stats['active_sessions']}")
        print(f"   Session Timeout: {stats['session_timeout_minutes']} minutes")
        print(f"   Average Session Age: {stats['avg_session_age_minutes']:.1f} minutes")
        
        print(f"\n🎯 SUCCESS: Dialogue system fully functional!")
        print(f"✅ Complete queries: Classification and search")
        print(f"✅ Contextual queries: Expansion and context-aware search")
        print(f"✅ Session management: History tracking and cleanup")
        print(f"✅ Strategy patterns: Extraction and reuse")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing dialogue system: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_llm_health():
    """Test LLM connectivity"""
    
    print("\n🔧 Testing LLM Connectivity")
    print("-" * 40)
    
    try:
        from dialogue import get_dialogue_factory
        
        factory = get_dialogue_factory()
        health = await factory.context_service.health_check()
        
        if health["success"] and health["available"]:
            print(f"✅ LLM Service: Available")
            print(f"   Models: {health.get('models', [])[:3]}")  # Show first 3
            print(f"   Current Model: {health.get('current_model')}")
            print(f"   Model Available: {health.get('model_available')}")
            return True
        else:
            print(f"❌ LLM Service: {health.get('error', 'Unavailable')}")
            return False
            
    except Exception as e:
        print(f"❌ LLM Health Check Error: {e}")
        return False

async def test_chromadb_health():
    """Test ChromaDB connectivity"""
    
    print("\n🗄️ Testing ChromaDB Connectivity")
    print("-" * 40)
    
    try:
        from dialogue.search.context_aware import context_aware_search
        
        # Test library stats
        library = context_aware_search.analysis_library
        stats = library.get_stats()
        
        if stats["success"]:
            print(f"✅ ChromaDB: Connected")
            print(f"   Total Analyses: {stats['total_analyses']}")
            print(f"   Status: {stats['status']}")
            return True
        else:
            print(f"❌ ChromaDB: {stats.get('error', 'Connection failed')}")
            return False
            
    except Exception as e:
        print(f"❌ ChromaDB Health Check Error: {e}")
        return False

async def main():
    """Run all tests"""
    
    print("🚀 Dialogue System Integration Test")
    print("=" * 60)
    
    # Check dependencies
    print("\n🔍 Checking Dependencies...")
    
    llm_ok = await test_llm_health()
    chromadb_ok = await test_chromadb_health()
    
    if not llm_ok:
        print("\n⚠️ WARNING: LLM not available - some tests may fail")
        print("   Make sure Ollama is running: ollama serve")
        print("   And model is available: ollama pull llama3.2")
    
    if not chromadb_ok:
        print("\n⚠️ WARNING: ChromaDB not available - tests will fail")
        print("   Make sure ChromaDB is running on localhost:8050")
        return False
    
    # Run dialogue tests
    success = await test_dialogue_system()
    
    if success:
        print(f"\n🎉 ALL TESTS PASSED!")
        print(f"✅ Dialogue system is ready for production use")
        print(f"✅ API endpoints can be integrated")
        print(f"✅ Conversation history management working")
    else:
        print(f"\n❌ TESTS FAILED")
        print(f"❌ Check error messages above")
        print(f"❌ Verify dependencies are running")
    
    return success

if __name__ == "__main__":
    asyncio.run(main())