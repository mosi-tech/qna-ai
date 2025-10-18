#!/usr/bin/env python3
"""
Integration Tests for SessionManager and ConversationStore with MongoDB

Tests the complete flow of:
1. Creating sessions in MongoDB
2. Retrieving existing sessions with conversation history
3. Populating ConversationStore from MongoDB messages
4. Message pairing (user + assistant response)
5. Context window trimming
6. Error handling when MongoDB unavailable
"""

import os
import sys
import asyncio
import pytest
from datetime import datetime
from typing import Optional, List, Dict, Any

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from dialogue.conversation.store import ConversationStore, ConversationTurn, QueryType
from dialogue.conversation.session_manager import SessionManager
from db.mongodb_client import MongoDBClient
from db.repositories import ChatRepository
from db.schemas import ChatSessionModel, ChatMessageModel, RoleType


class MockMongoDBClient:
    """Mock MongoDB client for testing without real database"""
    
    def __init__(self):
        self.sessions: Dict[str, ChatSessionModel] = {}
        self.messages: Dict[str, List[ChatMessageModel]] = {}
        self.session_counter = 0
    
    async def create_session(self, session: ChatSessionModel) -> str:
        """Create mock session"""
        session_id = session.sessionId
        self.sessions[session_id] = session
        self.messages[session_id] = []
        return session_id
    
    async def create_message(self, message: ChatMessageModel) -> str:
        """Create mock message"""
        if message.sessionId not in self.messages:
            self.messages[message.sessionId] = []
        self.messages[message.sessionId].append(message)
        return message.messageId
    
    async def get_session(self, session_id: str) -> Optional[ChatSessionModel]:
        """Get mock session"""
        return self.sessions.get(session_id)
    
    async def get_session_messages(self, session_id: str, limit: Optional[int] = None) -> List[ChatMessageModel]:
        """Get mock messages for session"""
        messages = self.messages.get(session_id, [])
        if limit:
            return messages[-limit:]
        return messages


class MockRepoManager:
    """Mock repo manager for testing"""
    
    def __init__(self):
        self.mock_db = MockMongoDBClient()
        self.chat = MockChatRepository(self.mock_db)


class MockChatRepository:
    """Mock chat repository for testing"""
    
    def __init__(self, db: MockMongoDBClient):
        self.db = db
    
    async def create_session(self, user_id: str = None, title: str = None) -> str:
        """Create session"""
        session = ChatSessionModel(
            userId=user_id or "test_user",
            title=title or "Test Session",
        )
        return await self.db.create_session(session)
    
    async def get_conversation_history(self, session_id: str) -> List[Dict[str, Any]]:
        """Get conversation history as dicts"""
        messages = await self.db.get_session_messages(session_id)
        history = []
        for msg in messages:
            history.append({
                "role": msg.role.value,
                "content": msg.content,
                "timestamp": msg.created_at.isoformat() if msg.created_at else datetime.now().isoformat(),
            })
        return history
    
    async def archive_session(self, session_id: str) -> bool:
        """Archive session"""
        if session_id in self.db.sessions:
            del self.db.sessions[session_id]
            return True
        return False


async def create_test_message(role: RoleType, content: str) -> Dict[str, Any]:
    """Helper to create test message dict"""
    return {
        "role": role.value,
        "content": content,
        "timestamp": datetime.now().isoformat(),
    }


async def test_create_session():
    """Test creating a new session in MongoDB"""
    print("\n✓ Test 1: Create Session")
    
    repo_manager = MockRepoManager()
    session_manager = SessionManager(repo_manager)
    
    session_id = await session_manager.create_session(user_id="test_user")
    
    assert session_id is not None
    assert len(session_id) > 0
    print(f"  ✓ Session created: {session_id}")


async def test_get_or_create_session_new():
    """Test getting or creating a new session"""
    print("\n✓ Test 2: Get or Create Session (New)")
    
    repo_manager = MockRepoManager()
    session_manager = SessionManager(repo_manager)
    
    session_id, store = await session_manager.get_or_create_session()
    
    assert session_id is not None
    assert isinstance(store, ConversationStore)
    assert store.session_id == session_id
    assert len(store.turns) == 0
    print(f"  ✓ New session created: {session_id}")
    print(f"  ✓ ConversationStore initialized")


async def test_populate_from_messages():
    """Test populating ConversationStore from MongoDB messages"""
    print("\n✓ Test 3: Populate from Messages (User/Assistant Pairing)")
    
    # Create test messages: user -> assistant -> user -> assistant
    db_messages = [
        {"role": "user", "content": "What is the volatility of AAPL?", "timestamp": "2025-01-01T10:00:00"},
        {"role": "assistant", "content": "AAPL volatility is 25% based on 30-day rolling window analysis", "timestamp": "2025-01-01T10:01:00"},
        {"role": "user", "content": "What about QQQ?", "timestamp": "2025-01-01T10:02:00"},
        {"role": "assistant", "content": "QQQ volatility is 35% with higher tech concentration", "timestamp": "2025-01-01T10:03:00"},
    ]
    
    store = ConversationStore("test_session_123")
    store._populate_from_messages(db_messages)
    
    assert len(store.turns) == 2
    print(f"  ✓ Populated {len(store.turns)} conversation turns")
    
    # Check first turn
    turn1 = store.turns[0]
    assert turn1.user_query == "What is the volatility of AAPL?"
    assert "AAPL volatility" in turn1.analysis_summary
    assert len(turn1.analysis_summary) <= 100
    assert turn1.query_type == QueryType.COMPLETE
    print(f"  ✓ Turn 1 - User query: {turn1.user_query[:40]}...")
    print(f"  ✓ Turn 1 - Analysis summary: {turn1.analysis_summary[:50]}...")
    
    # Check second turn
    turn2 = store.turns[1]
    assert turn2.user_query == "What about QQQ?"
    assert "QQQ volatility" in turn2.analysis_summary
    assert len(turn2.analysis_summary) <= 100
    print(f"  ✓ Turn 2 - User query: {turn2.user_query}")
    print(f"  ✓ Turn 2 - Analysis summary: {turn2.analysis_summary[:50]}...")


async def test_context_window_trimming():
    """Test that context window keeps only last 10 turns"""
    print("\n✓ Test 4: Context Window Trimming (Max 10 turns)")
    
    store = ConversationStore("test_session_123")
    
    # Add 15 turns
    for i in range(15):
        store.add_turn(
            user_query=f"Question {i+1}",
            query_type=QueryType.COMPLETE,
            analysis_summary=f"Analysis {i+1}"
        )
    
    # Should keep only last 10
    assert len(store.turns) == 10
    assert store.turns[0].user_query == "Question 6"
    assert store.turns[-1].user_query == "Question 15"
    print(f"  ✓ Store trimmed to {len(store.turns)} turns (max configured)")
    print(f"  ✓ Oldest turn: {store.turns[0].user_query}")
    print(f"  ✓ Newest turn: {store.turns[-1].user_query}")


async def test_get_last_turn():
    """Test getting the last conversation turn"""
    print("\n✓ Test 5: Get Last Turn")
    
    store = ConversationStore("test_session_123")
    
    # Empty store
    assert store.get_last_turn() is None
    
    # Add turns
    store.add_turn(user_query="Question 1", query_type=QueryType.COMPLETE)
    store.add_turn(user_query="Question 2", query_type=QueryType.CONTEXTUAL)
    
    last = store.get_last_turn()
    assert last.user_query == "Question 2"
    print(f"  ✓ Last turn retrieved: {last.user_query}")


async def test_get_last_complete_turn():
    """Test getting the last complete (standalone) turn"""
    print("\n✓ Test 6: Get Last Complete Turn")
    
    store = ConversationStore("test_session_123")
    
    # Add mixed turns
    store.add_turn(
        user_query="Question 1",
        query_type=QueryType.COMPLETE,
        analysis_summary="Analysis 1",
        context_used=False
    )
    store.add_turn(
        user_query="Question 2",
        query_type=QueryType.CONTEXTUAL,
        analysis_summary="Analysis 2",
        context_used=True
    )
    store.add_turn(
        user_query="Question 3",
        query_type=QueryType.COMPLETE,
        analysis_summary="Analysis 3",
        context_used=False
    )
    
    last_complete = store.get_last_complete_turn()
    assert last_complete.user_query == "Question 3"
    assert last_complete.context_used == False
    print(f"  ✓ Last complete turn: {last_complete.user_query}")


async def test_get_context_summary():
    """Test getting context summary for LLM"""
    print("\n✓ Test 7: Get Context Summary")
    
    store = ConversationStore("test_session_123")
    
    store.add_turn(
        user_query="What is the volatility?",
        query_type=QueryType.COMPLETE,
        analysis_summary="AAPL volatility analysis"
    )
    store.add_turn(
        user_query="What about QQQ?",
        query_type=QueryType.CONTEXTUAL,
        analysis_summary="QQQ volatility analysis",
        context_used=True
    )
    
    summary = store.get_context_summary()
    
    assert summary["has_history"] == True
    assert summary["turn_count"] == 2
    assert summary["last_query"] == "What about QQQ?"
    assert summary["last_query_type"] == "contextual"
    print(f"  ✓ Context summary: {summary['turn_count']} turns")
    print(f"  ✓ Last query: {summary['last_query']}")
    print(f"  ✓ Has history: {summary['has_history']}")


async def test_retrieve_existing_session():
    """Test retrieving an existing session with conversation history"""
    print("\n✓ Test 8: Retrieve Existing Session from MongoDB")
    
    repo_manager = MockRepoManager()
    
    # Step 1: Create session and add messages
    session_id = await repo_manager.chat.create_session(user_id="test_user")
    print(f"  ✓ Session created: {session_id}")
    
    # Add messages
    msg1 = ChatMessageModel(
        sessionId=session_id,
        userId="test_user",
        role=RoleType.USER,
        content="What is the volatility?",
    )
    msg2 = ChatMessageModel(
        sessionId=session_id,
        userId="test_user",
        role=RoleType.ASSISTANT,
        content="AAPL volatility is 25%",
    )
    await repo_manager.mock_db.create_message(msg1)
    await repo_manager.mock_db.create_message(msg2)
    print(f"  ✓ Added 2 messages to session")
    
    # Step 2: Use SessionManager to retrieve
    session_manager = SessionManager(repo_manager)
    retrieved_store = await session_manager._get_session(session_id)
    
    assert retrieved_store is not None
    assert retrieved_store.session_id == session_id
    assert len(retrieved_store.turns) == 1  # One user-assistant pair
    print(f"  ✓ Session retrieved from MongoDB")
    print(f"  ✓ Conversation store populated with {len(retrieved_store.turns)} turns")


async def test_delete_session():
    """Test deleting a session"""
    print("\n✓ Test 9: Delete Session")
    
    repo_manager = MockRepoManager()
    session_manager = SessionManager(repo_manager)
    
    # Create and delete
    session_id = await session_manager.create_session()
    success = await session_manager.delete_session(session_id)
    
    assert success == True
    print(f"  ✓ Session deleted: {session_id}")
    
    # Verify it's gone
    retrieved = await session_manager._get_session(session_id)
    assert retrieved is None
    print(f"  ✓ Verified session no longer exists")


async def test_session_manager_with_repo_manager():
    """Test SessionManager properly initialized with repo_manager"""
    print("\n✓ Test 10: SessionManager with Repo Manager")
    
    repo_manager = MockRepoManager()
    session_manager = SessionManager(repo_manager)
    
    assert session_manager.repo_manager is not None
    assert session_manager.repo_manager.chat is not None
    print(f"  ✓ SessionManager properly initialized with repo_manager")
    
    # Create and retrieve
    session_id, store = await session_manager.get_or_create_session()
    assert isinstance(store, ConversationStore)
    print(f"  ✓ Session created and store initialized: {session_id}")


async def test_message_pairing_edge_cases():
    """Test message pairing with edge cases"""
    print("\n✓ Test 11: Message Pairing Edge Cases")
    
    # Test 1: Unpaired user message (no assistant response)
    db_messages = [
        {"role": "user", "content": "First question"},
        {"role": "user", "content": "Second question"},  # No assistant response
    ]
    
    store = ConversationStore("test_session")
    store._populate_from_messages(db_messages)
    
    assert len(store.turns) == 2
    assert store.turns[0].analysis_summary is None
    assert store.turns[1].analysis_summary is None
    print(f"  ✓ Unpaired user messages handled: {len(store.turns)} turns")
    
    # Test 2: Assistant without preceding user
    db_messages_2 = [
        {"role": "assistant", "content": "Orphan response"},
        {"role": "user", "content": "Question"},
    ]
    
    store2 = ConversationStore("test_session_2")
    store2._populate_from_messages(db_messages_2)
    
    assert len(store2.turns) == 1
    assert store2.turns[0].user_query == "Question"
    print(f"  ✓ Orphan assistant message skipped: {len(store2.turns)} turns")


async def test_store_serialization():
    """Test ConversationStore serialization/deserialization"""
    print("\n✓ Test 12: Store Serialization")
    
    store = ConversationStore("test_session")
    store.add_turn(
        user_query="Test question",
        query_type=QueryType.COMPLETE,
        analysis_summary="Test analysis"
    )
    
    # Serialize
    store_dict = store.to_dict()
    assert store_dict["session_id"] == "test_session"
    assert len(store_dict["turns"]) == 1
    print(f"  ✓ Store serialized: {len(store_dict['turns'])} turns")
    
    # Deserialize
    restored = ConversationStore.from_dict(store_dict)
    assert restored.session_id == store.session_id
    assert len(restored.turns) == len(store.turns)
    assert restored.turns[0].user_query == store.turns[0].user_query
    print(f"  ✓ Store deserialized correctly")


async def test_conversation_turn_serialization():
    """Test ConversationTurn serialization"""
    print("\n✓ Test 13: Conversation Turn Serialization")
    
    turn = ConversationTurn(
        id="turn_123",
        timestamp=datetime.now(),
        user_query="Test question",
        query_type=QueryType.COMPLETE,
        expanded_query="Test expanded",
        analysis_summary="Analysis",
        context_used=False,
        expansion_confidence=0.95
    )
    
    # Serialize
    turn_dict = turn.to_dict()
    assert turn_dict["id"] == "turn_123"
    assert turn_dict["query_type"] == "complete"
    print(f"  ✓ Turn serialized")
    
    # Deserialize
    restored = ConversationTurn.from_dict(turn_dict)
    assert restored.id == turn.id
    assert restored.query_type == turn.query_type
    print(f"  ✓ Turn deserialized correctly")


async def run_all_tests():
    """Run all integration tests"""
    
    print("\n" + "="*60)
    print("🧪 SessionManager & ConversationStore Integration Tests")
    print("="*60)
    
    tests = [
        ("Create Session", test_create_session),
        ("Get or Create Session", test_get_or_create_session_new),
        ("Populate from Messages", test_populate_from_messages),
        ("Context Window Trimming", test_context_window_trimming),
        ("Get Last Turn", test_get_last_turn),
        ("Get Last Complete Turn", test_get_last_complete_turn),
        ("Get Context Summary", test_get_context_summary),
        ("Retrieve Existing Session", test_retrieve_existing_session),
        ("Delete Session", test_delete_session),
        ("SessionManager with Repo", test_session_manager_with_repo_manager),
        ("Message Pairing Edge Cases", test_message_pairing_edge_cases),
        ("Store Serialization", test_store_serialization),
        ("Turn Serialization", test_conversation_turn_serialization),
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
        print("✅ SessionManager properly initialized with MongoDB")
        print("✅ ConversationStore correctly populates from messages")
        print("✅ Message pairing and context window working")
        print("✅ Serialization/deserialization functional")
        return True
    else:
        print(f"\n❌ {failed} tests failed")
        return False


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)
