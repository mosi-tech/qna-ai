#!/usr/bin/env python3
"""
MongoDB implementation of execution queue
"""

import asyncio
import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Any, AsyncGenerator, Optional
from pymongo import ReturnDocument
from motor.motor_asyncio import AsyncIOMotorCollection, AsyncIOMotorDatabase

from .base_queue import ExecutionQueueInterface

logger = logging.getLogger(__name__)

class MongoDBExecutionQueue(ExecutionQueueInterface):
    """MongoDB-based execution queue implementation"""
    
    def __init__(self, db: AsyncIOMotorDatabase, collection_name: str = "execution_queue"):
        self.db = db
        self.collection: AsyncIOMotorCollection = db[collection_name]
        self.collection_name = collection_name
        self.progress_events_collection: AsyncIOMotorCollection = db["progress_events"]
        
    async def ensure_indexes(self):
        """Create necessary indexes for performance"""
        try:
            # Index for efficient polling by status and priority
            await self.collection.create_index([
                ("status", 1),
                ("priority", 1), 
                ("created_at", 1)
            ], name="queue_polling_idx")
            
            # Index for fast execution_id lookups
            await self.collection.create_index("execution_id", unique=True, name="execution_id_idx")
            
            # Index for worker_id queries
            await self.collection.create_index("worker_id", name="worker_id_idx")
            
            # Index for progress events by session_id and timestamp
            await self.progress_events_collection.create_index([
                ("session_id", 1),
                ("timestamp", 1)
            ], name="progress_events_idx")
            
            logger.info("✅ MongoDB queue indexes created successfully")
            
        except Exception as e:
            logger.warning(f"Failed to create indexes: {e}")
    
    async def enqueue(self, execution_data: Dict[str, Any]) -> str:
        """Add execution to queue"""
        try:
            execution_id = execution_data.get("execution_id")
            if not execution_id:
                raise ValueError("execution_id is required in execution_data")
            
            # Extract script info from execution_params if provided, fallback to top-level
            execution_params = execution_data.get("execution_params", {})
            
            document = {
                "execution_id": execution_id,
                "analysis_id": execution_data.get("analysis_id"),
                "session_id": execution_data.get("session_id"),
                "user_id": execution_data.get("user_id"),
                "status": "pending",
                "priority": execution_data.get("priority", 2),  # 1=high, 2=normal, 3=low
                "created_at": datetime.utcnow(),
                "started_at": None,
                "completed_at": None,
                "timeout_seconds": execution_data.get("timeout_seconds", 300),
                "retry_count": 0,
                "max_retries": execution_data.get("max_retries", 3),
                "worker_id": None,
                "execution_logs": [],
                "result": None,
                "execution_params": execution_params,
                "metadata": execution_data.get("metadata", {})
            }
            
            await self.collection.insert_one(document)
            logger.info(f"✅ Enqueued execution: {execution_id}")
            return execution_id
            
        except Exception as e:
            logger.error(f"❌ Failed to enqueue execution: {e}")
            raise
    
    async def dequeue(self, worker_id: str) -> Optional[Dict[str, Any]]:
        """Get next execution for worker (atomic operation)"""
        try:
            # Atomic find-and-modify to claim execution
            result = await self.collection.find_one_and_update(
                {
                    "status": "pending"
                },
                {
                    "$set": {
                        "status": "processing",
                        "worker_id": worker_id,
                        "started_at": datetime.now(timezone.utc)
                    },
                    "$inc": {"retry_count": 1}
                },
                sort=[("priority", 1), ("created_at", 1)],
                return_document=ReturnDocument.AFTER
            )
            
            if result:
                logger.info(f"✅ Claimed execution {result['execution_id']} by worker {worker_id}")
                return result
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Failed to dequeue execution: {e}")
            return None
    
    async def ack(self, execution_id: str, result: Dict[str, Any]) -> bool:
        """Mark execution as completed successfully"""
        try:
            update_result = await self.collection.update_one(
                {"execution_id": execution_id},
                {
                    "$set": {
                        "status": "completed",
                        "completed_at": datetime.utcnow(),
                        "result": result
                    }
                }
            )
            
            success = update_result.modified_count > 0
            if success:
                logger.info(f"✅ Acked execution: {execution_id}")
            else:
                logger.warning(f"⚠️ Failed to ack execution (not found): {execution_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Failed to ack execution {execution_id}: {e}")
            return False
    
    async def nack(self, execution_id: str, error: str, retry: bool = True) -> bool:
        """Mark execution as failed"""
        try:
            # Determine if we should retry or mark as permanently failed
            execution = await self.collection.find_one({"execution_id": execution_id})
            if not execution:
                logger.warning(f"⚠️ Execution not found for nack: {execution_id}")
                return False
            
            retry_count = execution.get("retry_count", 0)
            max_retries = execution.get("max_retries", 3)
            
            if retry and retry_count < max_retries:
                # Reset to pending for retry
                new_status = "pending"
                logger.info(f"🔄 Execution {execution_id} will be retried (attempt {retry_count + 1}/{max_retries})")
            else:
                # Mark as permanently failed
                new_status = "failed"
                logger.warning(f"❌ Execution {execution_id} permanently failed after {retry_count} attempts")
            
            update_result = await self.collection.update_one(
                {"execution_id": execution_id},
                {
                    "$set": {
                        "status": new_status,
                        "worker_id": None,
                        "completed_at": datetime.utcnow() if new_status == "failed" else None
                    },
                    "$push": {
                        "execution_logs": {
                            "timestamp": datetime.utcnow(),
                            "level": "ERROR",
                            "message": f"Execution failed: {error}"
                        }
                    }
                }
            )
            
            return update_result.modified_count > 0
            
        except Exception as e:
            logger.error(f"❌ Failed to nack execution {execution_id}: {e}")
            return False
    
    async def get_status(self, execution_id: str) -> Dict[str, Any]:
        """Get execution status and logs"""
        try:
            execution = await self.collection.find_one({"execution_id": execution_id})
            if not execution:
                return {"status": "not_found", "error": "Execution not found"}
            
            # Convert MongoDB ObjectId to string and clean up
            execution.pop("_id", None)
            
            return {
                "status": execution.get("status"),
                "execution_id": execution.get("execution_id"),
                "analysis_id": execution.get("analysis_id"),
                "created_at": execution.get("created_at"),
                "started_at": execution.get("started_at"),
                "completed_at": execution.get("completed_at"),
                "worker_id": execution.get("worker_id"),
                "retry_count": execution.get("retry_count", 0),
                "execution_logs": execution.get("execution_logs", []),
                "result": execution.get("result"),
                "script_name": execution.get("script_name"),
                "parameters": execution.get("parameters")
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get status for {execution_id}: {e}")
            return {"status": "error", "error": str(e)}
    
    async def stream_logs(self, execution_id: str) -> AsyncGenerator[Dict, None]:
        """Stream real-time execution logs"""
        try:
            last_log_count = 0
            
            while True:
                execution = await self.collection.find_one({"execution_id": execution_id})
                if not execution:
                    break
                
                logs = execution.get("execution_logs", [])
                
                # Yield new logs since last check
                if len(logs) > last_log_count:
                    for log_entry in logs[last_log_count:]:
                        yield {
                            "execution_id": execution_id,
                            "timestamp": log_entry.get("timestamp"),
                            "level": log_entry.get("level"),
                            "message": log_entry.get("message")
                        }
                    last_log_count = len(logs)
                
                # Check if execution is complete
                status = execution.get("status")
                if status in ["completed", "failed"]:
                    break
                
                # Wait before next poll
                await asyncio.sleep(1)
                
        except Exception as e:
            logger.error(f"❌ Failed to stream logs for {execution_id}: {e}")
            yield {"error": str(e)}
    
    async def update_logs(self, execution_id: str, log_entry: Dict[str, Any]) -> bool:
        """Add a log entry to execution"""
        try:
            log_with_timestamp = {
                "timestamp": log_entry.get("timestamp", datetime.utcnow()),
                "level": log_entry.get("level", "INFO"),
                "message": log_entry.get("message", "")
            }
            
            update_result = await self.collection.update_one(
                {"execution_id": execution_id},
                {"$push": {"execution_logs": log_with_timestamp}}
            )
            
            return update_result.modified_count > 0
            
        except Exception as e:
            logger.error(f"❌ Failed to update logs for {execution_id}: {e}")
            return False
    
    async def cleanup_old_executions(self, older_than_days: int = 7) -> int:
        """Clean up old completed/failed executions"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=older_than_days)
            
            result = await self.collection.delete_many({
                "status": {"$in": ["completed", "failed"]},
                "completed_at": {"$lt": cutoff_date}
            })
            
            deleted_count = result.deleted_count
            if deleted_count > 0:
                logger.info(f"🧹 Cleaned up {deleted_count} old executions")
            
            return deleted_count
            
        except Exception as e:
            logger.error(f"❌ Failed to cleanup old executions: {e}")
            return 0
    