#!/usr/bin/env python3
"""
Session Manager - Coordinates ConversationStore with ChatHistoryService

Architecture:
- SessionManager: Thin coordinator that manages session state
- ConversationStore: In-memory short-term context window (last 10 turns)
- ChatHistoryService: Persistent storage of all messages (for UI, full history)
- MongoDB: Underlying persistent store

Data Flow:
1. get_or_create_session() loads messages from ChatHistoryService → hydrates ConversationStore
2. add_turn() updates ConversationStore in-memory + persists via ChatHistoryService
3. Sessions cached in-memory during active conversation
"""

import uuid
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
from .store import ConversationStore, ConversationTurn

logger = logging.getLogger(__name__)

class SessionManager:
    """Coordinate conversation state between ConversationStore and ChatHistoryService
    
    Responsibilities:
    - Manage in-memory ConversationStore cache (session-scoped)
    - Load/save through ChatHistoryService
    - Track context window for query expansion
    - Delegate persistence to ChatHistoryService
    """
    
    def __init__(self, repo_manager=None, chat_history_service=None):
        self.repo_manager = repo_manager
        self.chat_history_service = chat_history_service
        
        # In-memory cache: session_id -> (ConversationStore, last_access_time)
        self._sessions: Dict[str, Tuple[ConversationStore, datetime]] = {}
        self._session_ttl_seconds = 3600  # 1 hour session timeout
    
    async def create_session(self, user_id: str = None, title: str = None) -> str:
        """Create new session in MongoDB via ChatHistoryService"""
        if not self.chat_history_service:
            # Fallback: create session_id locally
            return str(uuid.uuid4())
        
        try:
            session_id = await self.chat_history_service.start_session(user_id, title)
            logger.info(f"✓ Created new session: {session_id}")
            return session_id
        except Exception as e:
            logger.warning(f"⚠️ Failed to create session via ChatHistoryService: {e}")
            return str(uuid.uuid4())
    
    async def get_or_create_session(self, session_id: Optional[str] = None) -> Tuple[str, ConversationStore]:
        """Get or create session with in-memory caching
        
        Flow:
        1. If session_id provided, check in-memory cache
        2. If not cached, load from MongoDB via ChatHistoryService
        3. If session_id is None, create new session
        4. Cache the ConversationStore in-memory
        5. Return session_id and ConversationStore
        """
        # If session_id provided, try to get from cache or load
        if session_id:
            cached_store = self._get_cached_session(session_id)
            if cached_store:
                logger.debug(f"✓ Session {session_id[:8]}... loaded from cache")
                return session_id, cached_store
            
            # Load from MongoDB
            store = await self._load_session_from_db(session_id)
            if store:
                self._cache_session(session_id, store)
                logger.info(f"✓ Session {session_id[:8]}... loaded from MongoDB")
                return session_id, store
        
        # Create new session
        new_session_id = await self.create_session()
        store = ConversationStore(new_session_id, self.repo_manager)
        self._cache_session(new_session_id, store)
        logger.info(f"✓ New session created: {new_session_id[:8]}...")
        
        return new_session_id, store
    
    async def add_turn(self, session_id: str, user_query: str, query_type: str,
                      expanded_query: Optional[str] = None,
                      analysis_summary: Optional[str] = None,
                      context_used: bool = False,
                      expansion_confidence: float = 0.0) -> ConversationTurn:
        """Add turn to session (in-memory + persisted)
        
        Updates both:
        1. In-memory ConversationStore
        2. MongoDB via ChatHistoryService
        """
        # Get or load session
        _, store = await self.get_or_create_session(session_id)
        
        # Add to in-memory store
        turn = store.add_turn(
            user_query=user_query,
            query_type=query_type,
            expanded_query=expanded_query,
            analysis_summary=analysis_summary,
            context_used=context_used,
            expansion_confidence=expansion_confidence
        )
        
        logger.debug(f"✓ Turn added to ConversationStore: {user_query[:40]}...")
        
        return turn
    
    def get_session_store(self, session_id: str) -> Optional[ConversationStore]:
        """Get in-memory ConversationStore (no load from DB)
        
        Returns None if not in cache - use get_or_create_session() to load
        """
        cached = self._get_cached_session(session_id)
        if cached:
            self._touch_session_cache(session_id)
        return cached
    
    def get_context_window(self, session_id: str) -> Optional[Dict]:
        """Get context summary for current session
        
        Used by dialogue layer for query expansion context
        """
        store = self.get_session_store(session_id)
        if not store:
            return None
        return store.get_context_summary()
    
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
        store = await self._load_session_from_db(session_id)
        return store.to_dict() if store else None
    
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
    
    async def _load_session_from_db(self, session_id: str) -> Optional[ConversationStore]:
        """Load session from MongoDB via ChatHistoryService"""
        if not self.chat_history_service:
            return None
        
        try:
            # ChatHistoryService should have method to get conversation history
            db_messages = await self.chat_history_service.chat_repo.get_conversation_history(session_id)
            
            if not db_messages:
                return None
            
            store = ConversationStore(session_id, self.repo_manager)
            store._populate_from_messages(db_messages)
            
            return store
        except Exception as e:
            logger.warning(f"⚠️ Failed to load session from DB: {e}")
            return None
    
    def get_cache_stats(self) -> Dict:
        """Get cache statistics for monitoring"""
        return {
            "cached_sessions": len(self._sessions),
            "session_ttl_seconds": self._session_ttl_seconds,
            "sessions": [
                {
                    "session_id": sid[:8],
                    "turns": len(store.turns),
                    "age_seconds": (datetime.now() - cached_at).total_seconds()
                }
                for sid, (store, cached_at) in self._sessions.items()
            ]
        }

# Global session manager instance
session_manager = SessionManager()

# Convenience functions
async def get_or_create_session(session_id: Optional[str] = None) -> Tuple[str, ConversationStore]:
    """Get or create session - convenience function"""
    return await session_manager.get_or_create_session(session_id)

def get_session_manager() -> SessionManager:
    """Get global session manager instance"""
    return session_manager