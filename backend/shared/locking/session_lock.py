#!/usr/bin/env python3
"""
Distributed Session Locking for Analysis Queue

Prevents multiple concurrent analyses in the same session.
Uses MongoDB for distributed locking across multiple pods/workers.
"""

import logging
from datetime import datetime, timedelta
from typing import Optional
from pymongo.errors import DuplicateKeyError

logger = logging.getLogger(__name__)


class SessionLockModel:
    """MongoDB document structure for session locks"""
    
    def __init__(self, session_id: str, message_id: str, ttl_seconds: int = 1800):
        self.session_id = session_id
        self.message_id = message_id
        self.locked_at = datetime.utcnow()
        self.expires_at = self.locked_at + timedelta(seconds=ttl_seconds)
    
    def to_dict(self) -> dict:
        return {
            "session_id": self.session_id,
            "message_id": self.message_id,
            "locked_at": self.locked_at,
            "expires_at": self.expires_at
        }


class DistributedSessionLock:
    """
    Distributed session locking system using MongoDB.
    
    Ensures only one analysis can run per session at a time,
    even across multiple pods/workers.
    """
    
    def __init__(self, db):
        self.db = db
        self.collection = db.session_locks
        # Note: _ensure_indexes() will be called separately as it's async
    
    async def _ensure_indexes(self):
        """Create required indexes for session locking"""
        try:
            # Unique index on session_id to prevent duplicate locks
            await self.collection.create_index("session_id", unique=True)
            
            # TTL index for auto-expiring locks
            await self.collection.create_index("expires_at", expireAfterSeconds=0)
            
            logger.info("✅ Session lock indexes created")
        except Exception as e:
            logger.warning(f"⚠️ Failed to create session lock indexes: {e}")
    
    async def acquire_lock(self, session_id: str, message_id: str, ttl_seconds: int = 1800) -> bool:
        """
        Acquire a distributed lock for a session.
        
        Args:
            session_id: Session to lock
            message_id: Analysis message ID
            ttl_seconds: Lock expiration time (default 30 minutes)
        
        Returns:
            True if lock acquired, False if session already locked
        """
        try:
            lock_doc = SessionLockModel(session_id, message_id, ttl_seconds)
            
            await self.collection.insert_one(lock_doc.to_dict())
            
            logger.info(f"🔒 Session lock acquired: {session_id} → {message_id}")
            return True
            
        except DuplicateKeyError:
            # Session already locked by another process
            logger.info(f"⚠️ Session already locked: {session_id}")
            return False
        except Exception as e:
            logger.error(f"❌ Failed to acquire session lock: {e}")
            return False
    
    async def release_lock(self, session_id: str):
        """
        Release the lock for a session.
        
        Args:
            session_id: Session to unlock
        """
        try:
            result = await self.collection.delete_one({"session_id": session_id})
            
            if result.deleted_count > 0:
                logger.info(f"🔓 Session lock released: {session_id}")
            else:
                logger.warning(f"⚠️ No lock found to release: {session_id}")
                
        except Exception as e:
            logger.error(f"❌ Failed to release session lock: {e}")
    
    async def get_active_message(self, session_id: str) -> Optional[str]:
        
        return None;
    
        """
        Get the message ID of the currently active analysis in a session.
        
        Args:
            session_id: Session to check
        
        Returns:
            Message ID if session is locked, None if not locked
        """
        try:
            # Clean up expired locks first
            await self._cleanup_expired_locks()
            
            lock_doc = await self.collection.find_one({"session_id": session_id})
            
            if lock_doc:
                message_id = lock_doc["message_id"]
                logger.info(f"📋 Active analysis found: {session_id} → {message_id}")
                return message_id
            else:
                return None
                
        except Exception as e:
            logger.error(f"❌ Failed to get active message: {e}")
            return None
    
    async def extend_lock(self, session_id: str, ttl_seconds: int = 1800):
        """
        Extend the TTL of an existing lock.
        
        Args:
            session_id: Session lock to extend
            ttl_seconds: New TTL in seconds
        """
        try:
            new_expires_at = datetime.utcnow() + timedelta(seconds=ttl_seconds)
            
            result = await self.collection.update_one(
                {"session_id": session_id},
                {"$set": {"expires_at": new_expires_at}}
            )
            
            if result.modified_count > 0:
                logger.info(f"⏰ Session lock extended: {session_id} (+{ttl_seconds}s)")
            else:
                logger.warning(f"⚠️ No lock found to extend: {session_id}")
                
        except Exception as e:
            logger.error(f"❌ Failed to extend session lock: {e}")
    
    async def is_session_locked(self, session_id: str) -> bool:
        """
        Check if a session is currently locked.
        
        Args:
            session_id: Session to check
        
        Returns:
            True if locked, False if available
        """
        try:
            await self._cleanup_expired_locks()
            
            lock_count = await self.collection.count_documents({"session_id": session_id})
            return lock_count > 0
            
        except Exception as e:
            logger.error(f"❌ Failed to check session lock: {e}")
            return False
    
    async def _cleanup_expired_locks(self):
        """
        Manually clean up expired locks.
        
        Note: MongoDB TTL index should handle this automatically,
        but this provides immediate cleanup for critical operations.
        """
        try:
            result = await self.collection.delete_many({
                "expires_at": {"$lt": datetime.utcnow()}
            })
            
            if result.deleted_count > 0:
                logger.info(f"🧹 Cleaned up {result.deleted_count} expired session locks")
                
        except Exception as e:
            logger.warning(f"⚠️ Failed to cleanup expired locks: {e}")
    
    async def list_active_locks(self) -> list:
        """
        List all currently active session locks.
        
        Returns:
            List of active lock documents
        """
        try:
            await self._cleanup_expired_locks()
            
            locks = await self.collection.find({}).to_list(length=None)
            
            logger.info(f"📊 Found {len(locks)} active session locks")
            return locks
            
        except Exception as e:
            logger.error(f"❌ Failed to list active locks: {e}")
            return []


# Global session lock instance (will be initialized with DB connection)
session_lock: Optional[DistributedSessionLock] = None


async def initialize_session_lock(db):
    """Initialize the global session lock instance"""
    global session_lock
    session_lock = DistributedSessionLock(db)
    await session_lock._ensure_indexes()
    logger.info("✅ Distributed session lock initialized")


def get_session_lock() -> DistributedSessionLock:
    """Get the global session lock instance"""
    if session_lock is None:
        raise RuntimeError("Session lock not initialized. Call initialize_session_lock() first.")
    return session_lock