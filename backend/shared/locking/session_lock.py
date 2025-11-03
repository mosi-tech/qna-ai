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
            # First, clean up any expired locks
            await self._cleanup_expired_locks()
            
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
    
    async def acquire_lock_or_takeover(self, session_id: str, message_id: str, ttl_seconds: int = 1800, max_wait_seconds: int = 30) -> bool:
        """
        Try to acquire lock, and if fails, check if we can take over based on execution status.
        
        Args:
            session_id: Session to lock
            message_id: Analysis message ID
            ttl_seconds: Lock expiration time (default 30 minutes)
            max_wait_seconds: Max time to wait before taking over (default 30 seconds)
        
        Returns:
            True if lock acquired or taken over, False if session is actively locked
        """
        # Try normal acquisition first
        if await self.acquire_lock(session_id, message_id, ttl_seconds):
            return True
        
        # Check if existing lock can be taken over based on execution status
        try:
            existing_lock = await self.collection.find_one({"session_id": session_id})
            if existing_lock:
                locked_message_id = existing_lock["message_id"]
                lock_age = datetime.utcnow() - existing_lock["locked_at"]
                
                # First check execution status - this is more reliable than just time
                can_takeover = await self._can_takeover_based_on_execution(locked_message_id, lock_age, max_wait_seconds)
                
                if can_takeover:
                    logger.info(f"🔄 Taking over lock with completed/failed execution: {session_id} (message: {locked_message_id})")
                    
                    # Delete old lock and create new one
                    await self.collection.delete_one({"session_id": session_id})
                    
                    lock_doc = SessionLockModel(session_id, message_id, ttl_seconds)
                    await self.collection.insert_one(lock_doc.to_dict())
                    
                    logger.info(f"🔒 Session lock taken over: {session_id} → {message_id}")
                    return True
                else:
                    logger.info(f"⏳ Cannot take over lock - execution still active or lock too fresh: {session_id}")
                    return False
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Failed to check lock takeover for {session_id}: {e}")
            return False
    
    async def _can_takeover_based_on_execution(self, locked_message_id: str, lock_age: timedelta, max_wait_seconds: int) -> bool:
        """
        Check if we can take over a lock based on the execution status of the locked message.
        
        Args:
            locked_message_id: Message ID that currently holds the lock
            lock_age: How long the lock has been held
            max_wait_seconds: Maximum time to wait before allowing takeover
        
        Returns:
            True if lock can be taken over, False if execution is still active
        """
        try:
            # Get the locked message to find its execution ID
            messages_collection = self.db.chat_messages
            locked_message = await messages_collection.find_one({"messageId": locked_message_id})
            
            if not locked_message:
                logger.info(f"📝 Locked message not found, allowing takeover: {locked_message_id}")
                return True
            
            execution_id = locked_message.get("executionId")
            if not execution_id:
                # No execution associated - check age as fallback
                if lock_age.total_seconds() > max_wait_seconds:
                    logger.info(f"⏰ No execution found, using age-based takeover: {lock_age.total_seconds():.1f}s")
                    return True
                return False
            
            # Check execution status
            executions_collection = self.db.executions
            execution = await executions_collection.find_one({"executionId": execution_id})
            
            if not execution:
                logger.info(f"🔍 Execution not found, allowing takeover: {execution_id}")
                return True
            
            execution_status = execution.get("status")
            logger.info(f"📊 Execution status for {execution_id}: {execution_status}")
            
            # If execution is completed or failed, we can take over
            if execution_status in ["success", "completed", "failed", "timeout"]:
                logger.info(f"✅ Execution finished ({execution_status}), allowing takeover")
                return True
            
            # If execution is still pending/running, check age as secondary criteria
            if execution_status in ["pending", "running"]:
                if lock_age.total_seconds() > max_wait_seconds:
                    logger.info(f"⏰ Execution still {execution_status} but lock aged out ({lock_age.total_seconds():.1f}s), allowing takeover")
                    return True
                else:
                    logger.info(f"🔄 Execution still {execution_status} and lock fresh ({lock_age.total_seconds():.1f}s), denying takeover")
                    return False
            
            # Unknown status - use age-based fallback
            if lock_age.total_seconds() > max_wait_seconds:
                logger.info(f"❓ Unknown execution status '{execution_status}', using age-based takeover")
                return True
            
            return False
            
        except Exception as e:
            logger.warning(f"⚠️ Error checking execution status for takeover, using age-based fallback: {e}")
            # Fallback to age-based check if execution lookup fails
            return lock_age.total_seconds() > max_wait_seconds
    
    async def get_active_message(self, session_id: str) -> Optional[str]:
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
    logger.info("✅ Distributed session lock initialized with execution-aware takeover")


def get_session_lock() -> DistributedSessionLock:
    """Get the global session lock instance"""
    if session_lock is None:
        raise RuntimeError("Session lock not initialized. Call initialize_session_lock() first.")
    return session_lock