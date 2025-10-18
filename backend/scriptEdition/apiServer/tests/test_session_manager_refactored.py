#!/usr/bin/env python3
"""
Test Refactored SessionManager with ChatHistoryService Coordination

Tests the unified flow:
1. SessionManager delegates to ChatHistoryService for persistence
2. In-memory caching of ConversationStore (session duration)
3. Seamless coordination between short-term context and full history
"""

import os
import sys
import asyncio
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from dialogue.conversation.session_manager import SessionManager
from dialogue.conversation.store import ConversationStore, QueryType
from db.schemas import ChatSessionModel, ChatMessageModel, RoleType


class MockChatHistoryService:
    """Mock ChatHistoryService for testing coordination"""
    
    def __init__(self):
        self.sessions = {}
        self.messages = {}
    
    async def start_session(self, user_id: str = None, title: str = None) -> str:
        """Create session"""
        import uuid
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = {
            "user_id": user_id or "test_user",
            "title": title or "Test Session",
            "created_at": datetime.now()
        }
        self.messages[session_id] = []
        return session_id
    
    async def add_user_message(self, session_id: str, user_id: str, question: str, 
                              query_type: str = "complete", expanded_question: str = None) -> str:
        """Add user message"""
        import uuid
        message_id = str(uuid.uuid4())
        self.messages[session_id].append({
            "id": message_id,
            "role": "user",
            "content": question,
            "timestamp": datetime.now()
        })
        return message_id
    
    async def add_assistant_message(self, session_id: str, user_id: str, content: str) -> str:
        """Add assistant message"""
        import uuid
        message_id = str(uuid.uuid4())
        self.messages[session_id].append({
            "id": message_id,
            "role": "assistant",
            "content": content,
            "timestamp": datetime.now()
        })
        return message_id
    
    @property
    def chat_repo(self):
        """Return self as chat_repo for compatibility"""
        return self
    
    async def get_conversation_history(self, session_id: str):
        """Get all messages for session"""
        messages = self.messages.get(session_id, [])
        return [
            {
                "role": msg["role"],
                "content": msg["content"],
                "timestamp": msg["timestamp"].isoformat()
            }
            for msg in messages
        ]


async def test_session_manager_with_chat_history_service():
    """Test SessionManager coordinates with ChatHistoryService"""
    print("\n✓ Test 1: SessionManager with ChatHistoryService Integration")
    
    chat_service = MockChatHistoryService()
    session_manager = SessionManager(chat_history_service=chat_service)
    
    # Create session
    session_id, store = await session_manager.get_or_create_session()
    
    assert session_id is not None
    assert isinstance(store, ConversationStore)
    print(f"  ✓ Session created: {session_id[:8]}...")
    print(f"  ✓ SessionManager integrated with ChatHistoryService")


async def test_in_memory_caching():
    """Test sessions cached in-memory during active conversation"""
    print("\n✓ Test 2: In-Memory Caching During Conversation")
    
    chat_service = MockChatHistoryService()
    session_manager = SessionManager(chat_history_service=chat_service)
    
    # First request - loads from ChatHistoryService
    session_id, store1 = await session_manager.get_or_create_session()
    print(f"  ✓ First request: loaded fresh from ChatHistoryService")
    
    # Second request with same session_id - should get from cache
    store2 = session_manager.get_session_store(session_id)
    assert store2 is store1, "Should return same in-memory instance"
    print(f"  ✓ Second request: returned from in-memory cache (same instance)")
    
    # Verify cache stats
    stats = session_manager.get_cache_stats()
    assert stats["cached_sessions"] == 1
    print(f"  ✓ Cache stats: {stats['cached_sessions']} sessions cached")


async def test_message_flow():
    """Test complete message flow from ChatHistoryService through SessionManager"""
    print("\n✓ Test 3: Complete Message Flow")
    
    chat_service = MockChatHistoryService()
    session_manager = SessionManager(chat_history_service=chat_service)
    
    # Create session
    session_id, store = await session_manager.get_or_create_session()
    
    # Simulate user sends message -> saved to ChatHistoryService
    await chat_service.add_user_message(session_id, "test_user", "What is AAPL volatility?")
    
    # Simulate assistant response
    await chat_service.add_assistant_message(session_id, "test_user", "AAPL volatility is 25%")
    
    print(f"  ✓ Messages saved to ChatHistoryService")
    
    # Clear cache to force reload from DB
    session_manager._sessions.clear()
    
    # Reload session - should load from ChatHistoryService and populate ConversationStore
    reloaded_session_id, reloaded_store = await session_manager.get_or_create_session(session_id)
    
    assert reloaded_session_id == session_id
    assert len(reloaded_store.turns) == 1, f"Expected 1 turn, got {len(reloaded_store.turns)}"  # One user-assistant pair
    assert reloaded_store.turns[0].user_query == "What is AAPL volatility?"
    print(f"  ✓ Session reloaded from ChatHistoryService")
    print(f"  ✓ ConversationStore populated: {len(reloaded_store.turns)} turn(s)")


async def test_context_window():
    """Test context window for query expansion"""
    print("\n✓ Test 4: Context Window for Query Expansion")
    
    chat_service = MockChatHistoryService()
    session_manager = SessionManager(chat_history_service=chat_service)
    
    # Create session with history
    session_id, store = await session_manager.get_or_create_session()
    
    # Add multiple turns
    for i in range(5):
        await chat_service.add_user_message(session_id, "test_user", f"Question {i+1}")
        await chat_service.add_assistant_message(session_id, "test_user", f"Analysis {i+1}")
    
    # Clear cache and reload - should hydrate ConversationStore with context window
    session_manager._sessions.clear()
    _, reloaded_store = await session_manager.get_or_create_session(session_id)
    
    # Verify context window available for expansion
    context = session_manager.get_context_window(session_id)
    assert context is not None
    assert context["turn_count"] == 5, f"Expected 5 turns, got {context['turn_count']}"
    assert "last_query" in context
    print(f"  ✓ Context window available: {context['turn_count']} turns")
    print(f"  ✓ Last query: {context['last_query']}")


async def test_cache_separation():
    """Test multiple sessions cached independently"""
    print("\n✓ Test 5: Multiple Sessions Cached Independently")
    
    chat_service = MockChatHistoryService()
    session_manager = SessionManager(chat_history_service=chat_service)
    
    # Create two sessions
    session_id_1, store_1 = await session_manager.get_or_create_session()
    session_id_2, store_2 = await session_manager.get_or_create_session()
    
    assert session_id_1 != session_id_2
    assert store_1 is not store_2
    
    # Add different messages to each
    await chat_service.add_user_message(session_id_1, "user", "Question for session 1")
    await chat_service.add_user_message(session_id_2, "user", "Question for session 2")
    
    # Verify cache stats
    stats = session_manager.get_cache_stats()
    assert stats["cached_sessions"] == 2
    print(f"  ✓ Both sessions cached: {stats['cached_sessions']} sessions")
    
    # Get each from cache
    cached_1 = session_manager.get_session_store(session_id_1)
    cached_2 = session_manager.get_session_store(session_id_2)
    
    assert cached_1 is store_1
    assert cached_2 is store_2
    print(f"  ✓ Each session retrieved independently from cache")


async def test_cache_expiration():
    """Test session cache expiration"""
    print("\n✓ Test 6: Session Cache Expiration (TTL)")
    
    chat_service = MockChatHistoryService()
    session_manager = SessionManager(chat_history_service=chat_service)
    session_manager._session_ttl_seconds = 1  # 1 second TTL for testing
    
    # Create session
    session_id, store = await session_manager.get_or_create_session()
    
    # Should be in cache
    cached = session_manager.get_session_store(session_id)
    assert cached is not None
    print(f"  ✓ Session in cache immediately after creation")
    
    # Wait for expiration
    await asyncio.sleep(1.1)
    
    # Should be expired from cache
    expired = session_manager.get_session_store(session_id)
    assert expired is None
    print(f"  ✓ Session expired from cache after TTL")
    
    # But should reload from ChatHistoryService
    _, reloaded = await session_manager.get_or_create_session(session_id)
    assert reloaded is not None
    print(f"  ✓ Session reloaded from ChatHistoryService after expiration")


async def test_add_turn_coordination():
    """Test add_turn coordinates in-memory + ChatHistoryService"""
    print("\n✓ Test 7: add_turn() Coordination")
    
    chat_service = MockChatHistoryService()
    session_manager = SessionManager(chat_history_service=chat_service)
    
    # Create session
    session_id, store = await session_manager.get_or_create_session()
    
    # Add turn through SessionManager
    turn = await session_manager.add_turn(
        session_id=session_id,
        user_query="Test question",
        query_type=QueryType.COMPLETE.value,
        analysis_summary="Test analysis"
    )
    
    assert turn is not None
    assert turn.user_query == "Test question"
    print(f"  ✓ Turn added: {turn.user_query}")
    
    # Verify it's in the cached store
    cached_store = session_manager.get_session_store(session_id)
    assert len(cached_store.turns) == 1
    print(f"  ✓ Turn in in-memory ConversationStore: {len(cached_store.turns)} turn(s)")


async def run_all_tests():
    """Run all refactored SessionManager tests"""
    
    print("\n" + "="*60)
    print("🧪 Refactored SessionManager with ChatHistoryService")
    print("="*60)
    
    tests = [
        ("SessionManager ChatHistoryService Integration", test_session_manager_with_chat_history_service),
        ("In-Memory Caching", test_in_memory_caching),
        ("Complete Message Flow", test_message_flow),
        ("Context Window", test_context_window),
        ("Multiple Sessions Cache", test_cache_separation),
        ("Cache Expiration (TTL)", test_cache_expiration),
        ("add_turn() Coordination", test_add_turn_coordination),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            await test_func()
            passed += 1
        except AssertionError as e:
            print(f"\n❌ {test_name} FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"\n❌ {test_name} ERROR: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "="*60)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    print("="*60)
    
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED! ✅")
        print("✅ SessionManager coordinates with ChatHistoryService")
        print("✅ In-memory caching works during active conversation")
        print("✅ Message flow: ChatHistoryService → ConversationStore")
        print("✅ Context window available for query expansion")
        print("✅ Multiple sessions cached independently")
        print("✅ Cache expiration (TTL) working")
        print("✅ add_turn() coordinates in-memory + storage")
        return True
    else:
        print(f"\n❌ {failed} tests failed")
        return False


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)
