#!/usr/bin/env python3
"""
Progress Event Queue System for Real-time Progress Communication

Manages progress events between workers and API server for SSE streaming.
Separate from analysis queue for clean separation of concerns.
"""

import asyncio
import json
import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Union
from abc import ABC, abstractmethod

from .progress_message import ProgressMessage

logger = logging.getLogger(__name__)


class ProgressEventQueueInterface(ABC):
    """Abstract interface for progress event queue implementations"""
    
    @abstractmethod
    async def send_progress_event(self, session_id: str, event_data: Union[ProgressMessage, Dict[str, Any]]):
        """
        Send progress event for SSE streaming
        
        Args:
            session_id: Session ID for routing events
            event_data: Event data to send (ProgressMessage or dict for backward compatibility)
        """
        pass
    
    @abstractmethod
    async def get_progress_events(self, session_id: str, since: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """
        Get progress events for a session
        
        Args:
            session_id: Session ID to get events for
            since: Optional timestamp to get events since
            
        Returns:
            List of progress event dictionaries
        """
        pass
    
    @abstractmethod
    async def cleanup_old_events(self, older_than_hours: int = 24):
        """
        Clean up old progress events
        
        Args:
            older_than_hours: Remove events older than this many hours
        """
        pass


class MongoProgressEventQueue(ProgressEventQueueInterface):
    """MongoDB-based progress event queue implementation"""
    
    def __init__(self, db):
        self.db = db
        self.collection = db.progress_events
        self._ensure_indexes()
    
    def _ensure_indexes(self):
        """Create required indexes for progress event queue"""
        try:
            # Index for efficient session-based queries
            self.collection.create_index([
                ("session_id", 1),
                ("timestamp", -1)
            ])
            
            # Index for monitoring unprocessed events
            self.collection.create_index([
                ("processed", 1),
                ("timestamp", 1)
            ])
            
            # TTL index for automatic cleanup of old events
            self.collection.create_index(
                "expires_at",
                expireAfterSeconds=0
            )
            
            logger.info("✅ Progress event queue indexes created")
        except Exception as e:
            logger.warning(f"⚠️ Failed to create progress event queue indexes: {e}")
    
    async def send_progress_event(self, session_id: str, event_data: Union[ProgressMessage, Dict[str, Any]]):
        """Store progress event for polling-based processing"""
        try:
            # Convert ProgressMessage to dict if needed
            if isinstance(event_data, ProgressMessage):
                event_dict = event_data.to_dict()
            else:
                event_dict = event_data
            
            # Store event in database for persistence and polling
            event_doc = {
                "event_id": str(uuid.uuid4()),
                "session_id": session_id,
                "timestamp": datetime.utcnow(),
                "processed": False,  # Flag for progress monitor polling
                # Flatten event_data into the document for easier monitoring
                **event_dict,
                # Auto-expire events after 24 hours
                "expires_at": datetime.utcnow() + timedelta(hours=24)
            }
            
            await self.collection.insert_one(event_doc)
            
            # Handle message logging if requested
            if event_dict.get("log_to_message") and event_dict.get("message_id"):
                await self._log_to_message(
                    message_id=event_dict["message_id"],
                    level=event_dict.get("level", "info"),
                    message=event_dict.get("message", "Progress update"),
                    details={k: v for k, v in event_dict.items() 
                            if k not in ["level", "message", "log_to_message", "message_id"]}
                )
            
            logger.info(f"📝 Progress event stored: {session_id} - {event_dict.get('message', 'Progress update')}")
                
        except Exception as e:
            logger.error(f"❌ Failed to store progress event: {e}")
    
    async def get_progress_events(self, session_id: str, since: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Get progress events for a session"""
        try:
            query = {"session_id": session_id}
            if since:
                query["timestamp"] = {"$gte": since}
            
            cursor = self.collection.find(query).sort("timestamp", 1)
            events = []
            
            async for event_doc in cursor:
                # Convert datetime to ISO string for JSON serialization
                event = {
                    "event_id": event_doc["event_id"],
                    "timestamp": event_doc["timestamp"].isoformat() if isinstance(event_doc["timestamp"], datetime) else event_doc["timestamp"],
                }
                
                # Add all other fields from the flattened event_dict, converting datetimes
                for key, value in event_doc.items():
                    if key not in ["_id", "event_id", "timestamp", "session_id", "processed", "expires_at"]:
                        if isinstance(value, datetime):
                            event[key] = value.isoformat()
                        else:
                            event[key] = value
                
                events.append(event)
            
            return events
            
        except Exception as e:
            logger.error(f"❌ Failed to get progress events: {e}")
            return []
    
    async def cleanup_old_events(self, older_than_hours: int = 24):
        """Clean up old progress events"""
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=older_than_hours)
            result = await self.collection.delete_many({
                "timestamp": {"$lt": cutoff_time}
            })
            
            if result.deleted_count > 0:
                logger.info(f"🧹 Cleaned up {result.deleted_count} old progress events")
                
        except Exception as e:
            logger.warning(f"⚠️ Failed to cleanup old progress events: {e}")
    
    async def _log_to_message(self, message_id: str, level: str, message: str, details: Dict[str, Any] = None):
        """Log progress to message logs array in chat_messages collection"""
        try:
            # Create log entry
            log_entry = {
                "message": message,
                "timestamp": datetime.utcnow(),
                "level": level,
                "details": details or {}
            }
            
            # Append to message logs array
            result = await self.db.chat_messages.update_one(
                {"messageId": message_id},
                {"$push": {"logs": log_entry}}
            )
            
            if result.modified_count > 0:
                logger.info(f"📝 [{message_id}] {level.upper()}: {message}")
            else:
                logger.warning(f"⚠️ Message not found for logging: {message_id}")
                
        except Exception as e:
            logger.error(f"❌ Failed to log to message {message_id}: {e}")
    
    async def get_queue_stats(self) -> Dict[str, int]:
        """Get progress event queue statistics"""
        try:
            total_events = await self.collection.count_documents({})
            
            # Count events by session
            pipeline = [
                {"$group": {"_id": "$session_id", "count": {"$sum": 1}}},
                {"$group": {"_id": None, "total_sessions": {"$sum": 1}, "avg_events_per_session": {"$avg": "$count"}}}
            ]
            
            stats = {"total_events": total_events, "total_sessions": 0, "avg_events_per_session": 0}
            
            async for result in self.collection.aggregate(pipeline):
                stats["total_sessions"] = result.get("total_sessions", 0)
                stats["avg_events_per_session"] = round(result.get("avg_events_per_session", 0), 2)
            
            return stats
            
        except Exception as e:
            logger.error(f"❌ Failed to get progress event queue stats: {e}")
            return {}


# Global progress event queue instance
progress_event_queue: Optional[MongoProgressEventQueue] = None


def initialize_progress_event_queue(db):
    """Initialize the global progress event queue instance"""
    global progress_event_queue
    progress_event_queue = MongoProgressEventQueue(db)
    logger.info("✅ Progress event queue initialized")


def get_progress_event_queue() -> MongoProgressEventQueue:
    """Get the global progress event queue instance"""
    if progress_event_queue is None:
        raise RuntimeError("Progress event queue not initialized. Call initialize_progress_event_queue() first.")
    return progress_event_queue