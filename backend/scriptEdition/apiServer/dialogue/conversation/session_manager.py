#!/usr/bin/env python3
"""
Session Manager - Handle conversation session lifecycle
"""

import uuid
import json
import logging
from datetime import datetime
from typing import Dict, Optional
from .store import ConversationStore

logger = logging.getLogger(__name__)

class SessionManager:
    """Manage conversation sessions with automatic cleanup"""
    
    def __init__(self, session_timeout_minutes: int = 30):
        self._sessions: Dict[str, ConversationStore] = {}
        self._session_timeout_minutes = session_timeout_minutes
        self._max_sessions = 1000  # Prevent memory leaks
    
    def create_session(self) -> str:
        """Create new conversation session"""
        session_id = str(uuid.uuid4())
        
        # Clean up if we have too many sessions
        if len(self._sessions) >= self._max_sessions:
            self._cleanup_expired_sessions()
        
        self._sessions[session_id] = ConversationStore(session_id)
        logger.info(f"Created new session: {session_id}")
        
        return session_id
    
    def get_session(self, session_id: str) -> Optional[ConversationStore]:
        """Get existing session or None if not found/expired"""
        if session_id not in self._sessions:
            return None
        
        session = self._sessions[session_id]
        
        # Check if expired
        if session.is_expired(self._session_timeout_minutes):
            logger.info(f"Session expired: {session_id}")
            del self._sessions[session_id]
            return None
        
        return session
    
    def get_or_create_session(self, session_id: Optional[str] = None) -> tuple[str, ConversationStore]:
        """Get existing session or create new one"""
        if session_id:
            session = self.get_session(session_id)
            if session:
                return session_id, session
        
        # Create new session
        new_session_id = self.create_session()
        return new_session_id, self._sessions[new_session_id]
    
    def delete_session(self, session_id: str) -> bool:
        """Delete session manually"""
        if session_id in self._sessions:
            del self._sessions[session_id]
            logger.info(f"Deleted session: {session_id}")
            return True
        return False
    
    def _cleanup_expired_sessions(self):
        """Remove expired sessions"""
        expired_sessions = []
        
        for session_id, session in self._sessions.items():
            if session.is_expired(self._session_timeout_minutes):
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            del self._sessions[session_id]
        
        if expired_sessions:
            logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")
    
    def get_stats(self) -> dict:
        """Get session manager statistics"""
        active_sessions = len(self._sessions)
        
        # Calculate session ages
        now = datetime.now()
        session_ages = []
        for session in self._sessions.values():
            age_minutes = (now - session.created_at).total_seconds() / 60
            session_ages.append(age_minutes)
        
        return {
            "active_sessions": active_sessions,
            "session_timeout_minutes": self._session_timeout_minutes,
            "avg_session_age_minutes": sum(session_ages) / len(session_ages) if session_ages else 0,
            "max_sessions": self._max_sessions
        }
    
    def export_session(self, session_id: str) -> Optional[dict]:
        """Export session data for debugging/analysis"""
        session = self.get_session(session_id)
        return session.to_dict() if session else None
    
    def import_session(self, session_data: dict) -> bool:
        """Import session data (for testing/migration)"""
        try:
            session = ConversationStore.from_dict(session_data)
            self._sessions[session.session_id] = session
            logger.info(f"Imported session: {session.session_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to import session: {e}")
            return False

# Global session manager instance
session_manager = SessionManager()

# Convenience functions
def get_session(session_id: str) -> Optional[ConversationStore]:
    """Get session - convenience function"""
    return session_manager.get_session(session_id)

def create_session() -> str:
    """Create session - convenience function"""
    return session_manager.create_session()

def get_or_create_session(session_id: Optional[str] = None) -> tuple[str, ConversationStore]:
    """Get or create session - convenience function"""
    return session_manager.get_or_create_session(session_id)