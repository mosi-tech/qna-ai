#!/usr/bin/env python3
"""
Analysis Queue System for Async Analysis Processing

Manages queuing and processing of analysis requests.
"""

import asyncio
import json
import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class AnalysisQueueInterface(ABC):
    """Abstract interface for analysis queue implementations"""
    
    @abstractmethod
    async def enqueue_analysis(self, analysis_data: Dict[str, Any]) -> str:
        """
        Add analysis to queue
        
        Args:
            analysis_data: Dict containing analysis details
            
        Returns:
            job_id: Unique identifier for the queued analysis
        """
        pass
    
    @abstractmethod 
    async def dequeue_analysis(self, worker_id: str) -> Optional[Dict[str, Any]]:
        """
        Get next analysis for worker (atomic claim operation)
        
        Args:
            worker_id: Unique identifier for the worker
            
        Returns:
            Analysis job data dict or None if queue empty
        """
        pass
    
    @abstractmethod
    async def ack_analysis(self, job_id: str, result: Dict[str, Any]) -> bool:
        """
        Mark analysis as completed successfully
        
        Args:
            job_id: Analysis job identifier
            result: Analysis result data
            
        Returns:
            True if successfully acknowledged
        """
        pass
    
    @abstractmethod
    async def nack_analysis(self, job_id: str, error: str, retry: bool = True) -> bool:
        """
        Mark analysis as failed
        
        Args:
            job_id: Analysis job identifier
            error: Error message
            retry: Whether to retry the analysis
            
        Returns:
            True if successfully marked as failed
        """
        pass
    
    @abstractmethod
    async def send_progress_event(self, session_id: str, event_data: Dict[str, Any]):
        """
        Send progress event via SSE
        
        Args:
            session_id: Session ID for routing
            event_data: Event data to send
        """
        pass


class MongoAnalysisQueue(AnalysisQueueInterface):
    """MongoDB-based analysis queue implementation"""
    
    def __init__(self, db):
        self.db = db
        self.collection = db.analysis_queue
        self._ensure_indexes()
    
    def _ensure_indexes(self):
        """Create required indexes for analysis queue"""
        try:
            # Index for efficient dequeue operations
            self.collection.create_index([
                ("status", 1),
                ("created_at", 1)
            ])
            
            # Index for tracking by worker
            self.collection.create_index([
                ("worker_id", 1),
                ("status", 1)
            ])
            
            # TTL index for automatic cleanup of old completed jobs
            self.collection.create_index(
                "expires_at",
                expireAfterSeconds=0
            )
            
            logger.info("✅ Analysis queue indexes created")
        except Exception as e:
            logger.warning(f"⚠️ Failed to create analysis queue indexes: {e}")
    
    async def enqueue_analysis(self, analysis_data: Dict[str, Any]) -> str:
        """Add analysis to queue"""
        job_id = str(uuid.uuid4())
        
        job_doc = {
            "job_id": job_id,
            "session_id": analysis_data.get("session_id"),
            "message_id": analysis_data.get("message_id"),
            "user_question": analysis_data.get("user_question"),
            "user_message_id": analysis_data.get("user_message_id"),
            "status": "pending",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "worker_id": None,
            "claimed_at": None,
            "completed_at": None,
            "retry_count": 0,
            "error": None,
            "result": None,
            # Expire completed jobs after 24 hours
            "expires_at": datetime.utcnow() + timedelta(hours=24)
        }
        
        try:
            await self.collection.insert_one(job_doc)
            logger.info(f"📥 Analysis queued: {job_id} for message {analysis_data.get('message_id')}")
            return job_id
        except Exception as e:
            logger.error(f"❌ Failed to enqueue analysis: {e}")
            raise
    
    async def dequeue_analysis(self, worker_id: str) -> Optional[Dict[str, Any]]:
        """Get next analysis for worker (atomic claim operation)"""
        try:
            # Atomically claim next pending job
            result = await self.collection.find_one_and_update(
                {
                    "status": "pending",
                    "$or": [
                        {"worker_id": None},
                        {"worker_id": worker_id}  # Allow same worker to reclaim
                    ]
                },
                {
                    "$set": {
                        "status": "claimed",
                        "worker_id": worker_id,
                        "claimed_at": datetime.utcnow(),
                        "updated_at": datetime.utcnow()
                    }
                },
                sort=[("created_at", 1)],  # FIFO order
                return_document=True
            )
            
            if result:
                logger.info(f"📤 Analysis claimed by {worker_id}: {result['job_id']}")
                return result
            else:
                return None
                
        except Exception as e:
            logger.error(f"❌ Failed to dequeue analysis: {e}")
            return None
    
    async def ack_analysis(self, job_id: str, result: Dict[str, Any]) -> bool:
        """Mark analysis as completed successfully"""
        try:
            update_result = await self.collection.update_one(
                {"job_id": job_id},
                {
                    "$set": {
                        "status": "completed",
                        "result": result,
                        "completed_at": datetime.utcnow(),
                        "updated_at": datetime.utcnow(),
                        "expires_at": datetime.utcnow() + timedelta(hours=1)  # Cleanup completed jobs faster
                    }
                }
            )
            
            if update_result.modified_count > 0:
                logger.info(f"✅ Analysis completed: {job_id}")
                return True
            else:
                logger.warning(f"⚠️ Failed to ack analysis (not found): {job_id}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Failed to ack analysis: {e}")
            return False
    
    async def nack_analysis(self, job_id: str, error: str, retry: bool = True) -> bool:
        """Mark analysis as failed"""
        try:
            # Get current job to check retry count
            job = await self.collection.find_one({"job_id": job_id})
            if not job:
                logger.warning(f"⚠️ Job not found for nack: {job_id}")
                return False
            
            retry_count = job.get("retry_count", 0)
            max_retries = 1
            
            if retry and retry_count < max_retries:
                # Retry the job
                update_result = await self.collection.update_one(
                    {"job_id": job_id},
                    {
                        "$set": {
                            "status": "pending",
                            "worker_id": None,
                            "claimed_at": None,
                            "updated_at": datetime.utcnow(),
                            "error": error
                        },
                        "$inc": {"retry_count": 1}
                    }
                )
                logger.info(f"🔄 Analysis retry queued: {job_id} (attempt {retry_count + 1})")
            else:
                # Mark as permanently failed
                update_result = await self.collection.update_one(
                    {"job_id": job_id},
                    {
                        "$set": {
                            "status": "failed",
                            "error": error,
                            "completed_at": datetime.utcnow(),
                            "updated_at": datetime.utcnow(),
                            "expires_at": datetime.utcnow() + timedelta(hours=24)
                        }
                    }
                )
                logger.error(f"❌ Analysis permanently failed: {job_id} - {error}")
            
            return update_result.modified_count > 0
            
        except Exception as e:
            logger.error(f"❌ Failed to nack analysis: {e}")
            return False
    
    async def send_progress_event(self, session_id: str, event_data: Dict[str, Any]):
        """Send progress event via progress event queue"""
        if self.progress_event_queue:
            try:
                await self.progress_event_queue.send_progress_event(session_id, event_data)
                logger.info(f"📝 Progress event stored via queue: {session_id} - {event_data.get('message', 'Progress update')}")
            except Exception as e:
                logger.warning(f"⚠️ Failed to store progress event via queue: {e}")
        else:
            logger.warning("⚠️ No progress event queue available for storing events")
    
    async def get_queue_stats(self) -> Dict[str, int]:
        """Get queue statistics"""
        try:
            stats = {}
            
            # Count by status
            pipeline = [
                {"$group": {"_id": "$status", "count": {"$sum": 1}}}
            ]
            
            async for result in self.collection.aggregate(pipeline):
                stats[result["_id"]] = result["count"]
            
            # Ensure all statuses are represented
            for status in ["pending", "claimed", "completed", "failed"]:
                if status not in stats:
                    stats[status] = 0
            
            return stats
            
        except Exception as e:
            logger.error(f"❌ Failed to get queue stats: {e}")
            return {}
    
    async def cleanup_expired_jobs(self):
        """Manual cleanup of expired jobs (MongoDB TTL should handle this)"""
        try:
            result = await self.collection.delete_many({
                "expires_at": {"$lt": datetime.utcnow()}
            })
            
            if result.deleted_count > 0:
                logger.info(f"🧹 Cleaned up {result.deleted_count} expired analysis jobs")
                
        except Exception as e:
            logger.warning(f"⚠️ Failed to cleanup expired jobs: {e}")


# Global analysis queue instance
analysis_queue: Optional[MongoAnalysisQueue] = None


def initialize_analysis_queue(db):
    """Initialize the global analysis queue instance"""
    global analysis_queue
    analysis_queue = MongoAnalysisQueue(db)
    logger.info("✅ Analysis queue initialized")


def get_analysis_queue() -> MongoAnalysisQueue:
    """Get the global analysis queue instance"""
    if analysis_queue is None:
        raise RuntimeError("Analysis queue not initialized. Call initialize_analysis_queue() first.")
    return analysis_queue