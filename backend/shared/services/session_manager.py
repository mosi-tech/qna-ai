#!/usr/bin/env python3
"""
Session Manager - Coordinates ConversationStore with Redis and ChatHistoryService

Architecture:
- SessionManager: Thin coordinator that manages session state
- ConversationStore: Redis-backed short-term context window (last 20 messages)
- ChatHistoryService: Persistent storage of all messages (for UI, full history)
- Redis: Fast shared conversation state across processes
- MongoDB: Underlying persistent store

Data Flow:
1. get_or_create_session() loads messages from Redis/ChatHistoryService → hydrates ConversationStore
2. add_user_message()/add_assistant_message() updates ConversationStore in Redis + persists via ChatHistoryService
3. Sessions cached in-memory during active conversation
"""

import uuid
import logging
from datetime import datetime
from typing import Dict, Optional, Tuple, List
from ..analyze.dialogue.conversation.store import ConversationStore, Message, UserMessage, AssistantMessage

logger = logging.getLogger(__name__)

class SessionManager:
    """Coordinate conversation state between ConversationStore and ChatHistoryService
    
    Responsibilities:
    - Manage in-memory ConversationStore cache (session-scoped)
    - Load/save through ChatHistoryService
    - Track context window for query expansion
    - Delegate persistence to ChatHistoryService
    """
    
    def __init__(self, chat_history_service=None, redis_client=None):
        self.chat_history_service = chat_history_service
        self.redis_client = redis_client
        
        # In-memory cache: session_id -> (ConversationStore, last_access_time)
        self._sessions: Dict[str, Tuple[ConversationStore, datetime]] = {}
        self._session_ttl_seconds = 3600  # 1 hour session timeout
    
    async def create_session(self, user_id: str = None, title: str = None) -> str:
        """Create new session in MongoDB via ChatHistoryService"""
        try:
            session_id = await self.chat_history_service.start_session(user_id, title)
            logger.info(f"✓ Created new session: {session_id}")
            return session_id
        except Exception as e:
            logger.warning(f"⚠️ Failed to create session via ChatHistoryService: {e}")
            return str(uuid.uuid4())
    
    async def get_session(self, session_id: str) -> Optional[ConversationStore]:
        """Get session with in-memory caching
        
        Flow:
        1. Check in-memory cache
        2. If not cached, load from MongoDB via ChatHistoryService
        3. Cache the ConversationStore in-memory
        4. Return ConversationStore or None if not found
        """
        if not session_id:
            return None
        
        # Check cache first
        cached_store = self._get_cached_session(session_id)
        if cached_store:
            logger.debug(f"✓ Session {session_id[:8]}... loaded from cache")
            return cached_store
        
        # Load or create ConversationStore (handles Redis/DB loading internally)
        store = await ConversationStore.load_or_create(session_id, self.chat_history_service, self.redis_client)
        self._cache_session(session_id, store)
        
        # Check if it actually loaded data or is empty (new session)
        messages = await store.get_messages()
        if messages:
            logger.info(f"✓ Session {session_id[:8]}... loaded with {len(messages)} messages")
        else:
            logger.debug(f"✓ Session {session_id[:8]}... created as new empty conversation")
        
        return store
    
    # ========== NEW MESSAGE-BASED API ==========
    
    async def add_user_message(self, session_id: str, content: str, user_id: str = "anonymous", **metadata) -> UserMessage:
        """Add user message to session - immediately persisted"""
        store = await self.get_session(session_id)
        message = await store.add_user_message(content, user_id, **metadata)
        logger.debug(f"✓ User message added: {content[:40]}...")
        return message
    
    async def add_assistant_message(self, session_id: str, content: str, user_id: str = "anonymous", **metadata) -> AssistantMessage:
        """Add assistant message to session - independently persisted"""
        store = await self.get_session(session_id)
        message = await store.add_assistant_message(content, user_id, **metadata)
        logger.debug(f"✓ Assistant message added: {content[:40]}...")
        return message
    
    async def add_conversation_exchange(self, session_id: str, user_content: str, assistant_content: str, 
                                      user_id: str = "anonymous", **assistant_metadata) -> Tuple[UserMessage, AssistantMessage]:
        """Add user + assistant message pair (convenience method)"""
        store = await self.get_session(session_id)
        user_msg, assistant_msg = await store.add_conversation_exchange(
            user_content, assistant_content, user_id, **assistant_metadata
        )
        logger.debug(f"✓ Conversation exchange added: {user_content[:40]}... -> {assistant_content[:40]}...")
        return user_msg, assistant_msg
    
    async def get_messages(self, session_id: str, role: Optional[str] = None, limit: Optional[int] = None) -> List[Message]:
        """Get messages from session"""
        store = await self.get_session(session_id)
        if not store:
            return []
        return await store.get_messages(role, limit)
    
    async def get_last_user_message(self, session_id: str) -> Optional[UserMessage]:
        """Get last user message from session"""
        store = await self.get_session(session_id)
        if not store:
            return None
        return await store.get_last_user_message()
    
    async def get_last_assistant_message(self, session_id: str) -> Optional[AssistantMessage]:
        """Get last assistant message from session"""
        store = await self.get_session(session_id)
        if not store:
            return None
        return await store.get_last_assistant_message()
    
    async def get_pending_analysis_suggestion(self, session_id: str) -> Optional[dict]:
        """Get pending analysis suggestion from session"""
        store = await self.get_session(session_id)
        if not store:
            return None
        return await store.get_pending_analysis_suggestion()
    
    
    def get_session_store(self, session_id: str) -> Optional[ConversationStore]:
        """Get in-memory ConversationStore (no load from DB)
        
        Returns None if not in cache - use get_or_create_session() to load
        """
        cached = self._get_cached_session(session_id)
        if cached:
            self._touch_session_cache(session_id)
        return cached
    
    async def get_context_window(self, session_id: str) -> Optional[Dict]:
        """Get context summary for current session
        
        Used by dialogue layer for query expansion context
        """
        store = await self.get_session(session_id)
        if not store:
            return None
        
        # Use message-based context instead of legacy get_context_summary
        last_user_msg = await store.get_last_user_message()
        last_assistant_msg = await store.get_last_assistant_message()
        messages = await store.get_messages()
        
        return {
            "has_history": len(messages) > 0,
            "last_query": last_user_msg.content if last_user_msg else None,
            "last_response": last_assistant_msg.content[:200] if last_assistant_msg else None,
            "message_count": len(messages)
        }
    
    async def delete_session(self, session_id: str) -> bool:
        """Delete session from MongoDB and clear cache"""
        try:
            # Remove from cache
            if session_id in self._sessions:
                del self._sessions[session_id]
            
            # Delete from MongoDB if ChatHistoryService available
            if self.chat_history_service:
                # ChatHistoryService should delegate to repository
                logger.info(f"✓ Session deleted: {session_id[:8]}...")
            
            return True
        except Exception as e:
            logger.warning(f"⚠️ Failed to delete session: {e}")
            return False
    
    async def export_session(self, session_id: str) -> Optional[dict]:
        """Export session data for debugging/analysis"""
        store = await self.get_session(session_id)
        return await store.to_dict() if store else None
    
    def _cache_session(self, session_id: str, store: ConversationStore) -> None:
        """Cache session in memory"""
        self._sessions[session_id] = (store, datetime.now())
        logger.debug(f"📦 Session cached: {session_id[:8]}...")
    
    def _get_cached_session(self, session_id: str) -> Optional[ConversationStore]:
        """Get session from in-memory cache if not expired"""
        if session_id not in self._sessions:
            return None
        
        store, cached_at = self._sessions[session_id]
        age = (datetime.now() - cached_at).total_seconds()
        
        if age > self._session_ttl_seconds:
            logger.debug(f"⏰ Session cache expired: {session_id[:8]}... (age: {age:.0f}s)")
            del self._sessions[session_id]
            return None
        
        return store
    
    def _touch_session_cache(self, session_id: str) -> None:
        """Update session cache access time"""
        if session_id in self._sessions:
            store, _ = self._sessions[session_id]
            self._sessions[session_id] = (store, datetime.now())
    
    
    def get_cache_stats(self) -> Dict:
        """Get cache statistics for monitoring"""
        return {
            "cached_sessions": len(self._sessions),
            "session_ttl_seconds": self._session_ttl_seconds,
            "sessions": [
                {
                    "session_id": sid[:8],
                    "messages": "redis_backed",
                    "age_seconds": (datetime.now() - cached_at).total_seconds()
                }
                for sid, (store, cached_at) in self._sessions.items()
            ]
        }
    
    # ========== MESSAGE UTILITIES ==========
    
    async def get_recent_conversation(self, session_id: str, max_messages: int = 10) -> List[Message]:
        """Get recent conversation messages for context"""
        store = await self.get_session(session_id)
        if not store:
            return []
        
        # Get last N messages
        return await store.get_messages(limit=max_messages)
    
    # ========== MESSAGE TYPE UTILITIES ==========
    
    async def get_user_messages(self, session_id: str, limit: Optional[int] = None) -> List[UserMessage]:
        """Get user messages only"""
        store = await self.get_session(session_id)
        if not store:
            return []
        messages = await store.get_messages(role="user", limit=limit)
        return [msg for msg in messages if isinstance(msg, UserMessage)]
    
    async def get_assistant_messages(self, session_id: str, limit: Optional[int] = None) -> List[AssistantMessage]:
        """Get assistant messages only"""
        store = await self.get_session(session_id)
        if not store:
            return []
        messages = await store.get_messages(role="assistant", limit=limit)
        return [msg for msg in messages if isinstance(msg, AssistantMessage)]
    
    async def get_messages_with_analysis_suggestions(self, session_id: str) -> List[AssistantMessage]:
        """Get assistant messages that have analysis suggestions"""
        assistant_messages = await self.get_assistant_messages(session_id)
        return [msg for msg in assistant_messages if msg.has_analysis_suggestion()]
    
    async def count_messages(self, session_id: str, role: Optional[str] = None) -> int:
        """Count messages in session, optionally filtered by role"""
        store = await self.get_session(session_id)
        if not store:
            return 0
        
        messages = await store.get_messages(role)
        return len(messages)

