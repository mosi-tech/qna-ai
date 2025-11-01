#!/usr/bin/env python3
"""
Execution Queue Service

Provides a high-level interface for interacting with the execution queue system.
Integrates with the routes.py and provides queue management capabilities.
"""

import os
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from motor.motor_asyncio import AsyncIOMotorClient

import sys
from shared.queue import QueueFactory, ExecutionQueueInterface, ExecutionQueueWorker

logger = logging.getLogger(__name__)

class ExecutionQueueService:
    """High-level service for execution queue operations"""
    
    def __init__(self):
        self.queue: Optional[ExecutionQueueInterface] = None
        self.worker: Optional[ExecutionQueueWorker] = None
        self._initialized = False
    
    async def initialize(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the queue service with configuration"""
        if self._initialized:
            return
        
        try:
            # Default configuration
            default_config = {
                "queue_type": os.getenv("QUEUE_TYPE", "mongodb"),
                "mongo_url": os.getenv("MONGO_URL", "mongodb://localhost:27017"),
                "database_name": os.getenv("MONGO_DB_NAME", "qna_ai_admin"),
                "collection_name": "execution_queue"
            }
            
            # Merge with provided config
            if config:
                default_config.update(config)
            
            # Create queue instance
            self.queue = await QueueFactory.create_queue_async(
                queue_type=default_config["queue_type"],
                config=default_config
            )
            
            logger.info(f"✅ Execution queue service initialized ({default_config['queue_type']})")
            self._initialized = True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize execution queue service: {e}")
            raise
    
    async def enqueue_execution(
        self,
        execution_id: str,
        analysis_id: str,
        session_id: str,
        user_id: str,
        execution_params: Optional[Dict[str, Any]] = None,
        priority: int = 2,
        timeout_seconds: int = 300
    ) -> bool:
        """
        Enqueue an execution for processing
        
        Args:
            execution_id: Unique execution identifier
            analysis_id: Related analysis ID
            session_id: User session ID
            user_id: User identifier
            execution_params: Optional execution parameters
            priority: Execution priority (1=high, 2=normal, 3=low)
            timeout_seconds: Execution timeout
            
        Returns:
            True if successfully enqueued
        """
        if not self._initialized:
            await self.initialize()
        
        try:
            execution_data = {
                "execution_id": execution_id,
                "analysis_id": analysis_id,
                "session_id": session_id,
                "user_id": user_id,
                "execution_params": execution_params or {},
                "priority": priority,
                "timeout_seconds": timeout_seconds,
                "metadata": {
                    "source": "api_server",
                    "enqueued_at": datetime.now(timezone.utc)
                }
            }
            
            queued_id = await self.queue.enqueue(execution_data)
            logger.info(f"✅ Enqueued execution: {execution_id}")
            return queued_id == execution_id
            
        except Exception as e:
            logger.error(f"❌ Failed to enqueue execution {execution_id}: {e}")
            return False
    
    async def get_execution_status(self, execution_id: str) -> Dict[str, Any]:
        """Get status and details of an execution"""
        if not self._initialized:
            await self.initialize()
        
        try:
            return await self.queue.get_status(execution_id)
        except Exception as e:
            logger.error(f"❌ Failed to get execution status {execution_id}: {e}")
            return {"status": "error", "error": str(e)}
    
    async def stream_execution_logs(self, execution_id: str):
        """Stream real-time logs for an execution"""
        if not self._initialized:
            await self.initialize()
        
        try:
            async for log_entry in self.queue.stream_logs(execution_id):
                yield log_entry
        except Exception as e:
            logger.error(f"❌ Failed to stream logs for {execution_id}: {e}")
            yield {"error": str(e)}
    
    async def start_worker(self, worker_config: Optional[Dict[str, Any]] = None):
        """Start a queue worker for processing executions"""
        if not self._initialized:
            await self.initialize()
        
        if self.worker and self.worker.running:
            logger.warning("⚠️ Worker already running")
            return
        
        try:
            config = worker_config or {}
            
            self.worker = ExecutionQueueWorker(
                queue=self.queue,
                worker_id=config.get("worker_id"),
                poll_interval=config.get("poll_interval", 5),
                max_concurrent_executions=config.get("max_concurrent_executions", 3)
            )
            
            # Start worker in background
            import asyncio
            asyncio.create_task(self.worker.start())
            
            logger.info("🚀 Execution queue worker started")
            
        except Exception as e:
            logger.error(f"❌ Failed to start worker: {e}")
            raise
    
    async def stop_worker(self):
        """Stop the queue worker gracefully"""
        if self.worker:
            await self.worker.stop()
            self.worker = None
            logger.info("🛑 Execution queue worker stopped")
    
    async def get_executions_by_user(self, user_id: str, limit: int = 50, status_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get executions for a specific user"""
        if not self._initialized:
            await self.initialize()
        
        try:
            # Build query filter
            query_filter = {"user_id": user_id}
            if status_filter:
                query_filter["status"] = status_filter
            
            # Use MongoDB collection directly for filtering
            if hasattr(self.queue, 'collection'):
                cursor = self.queue.collection.find(query_filter).sort("created_at", -1).limit(limit)
                executions = await cursor.to_list(length=limit)
                
                # Convert ObjectId to string for JSON serialization
                for execution in executions:
                    if "_id" in execution:
                        execution["_id"] = str(execution["_id"])
                
                logger.info(f"✅ Found {len(executions)} executions for user {user_id}")
                return executions
            else:
                logger.warning("⚠️ Queue does not support direct collection access")
                return []
                
        except Exception as e:
            logger.error(f"❌ Failed to get executions for user {user_id}: {e}")
            return []
    
    async def get_executions_by_session(self, session_id: str, limit: int = 50, status_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get executions for a specific session"""
        if not self._initialized:
            await self.initialize()
        
        try:
            # Build query filter
            query_filter = {"session_id": session_id}
            if status_filter:
                query_filter["status"] = status_filter
            
            # Use MongoDB collection directly for filtering
            if hasattr(self.queue, 'collection'):
                cursor = self.queue.collection.find(query_filter).sort("created_at", -1).limit(limit)
                executions = await cursor.to_list(length=limit)
                
                # Convert ObjectId to string for JSON serialization
                for execution in executions:
                    if "_id" in execution:
                        execution["_id"] = str(execution["_id"])
                
                logger.info(f"✅ Found {len(executions)} executions for session {session_id}")
                return executions
            else:
                logger.warning("⚠️ Queue does not support direct collection access")
                return []
                
        except Exception as e:
            logger.error(f"❌ Failed to get executions for session {session_id}: {e}")
            return []
    
    async def cleanup_old_executions(self, older_than_days: int = 7) -> int:
        """Clean up old completed executions"""
        if not self._initialized:
            await self.initialize()
        
        try:
            if hasattr(self.queue, 'cleanup_old_executions'):
                return await self.queue.cleanup_old_executions(older_than_days)
            return 0
        except Exception as e:
            logger.error(f"❌ Failed to cleanup old executions: {e}")
            return 0

# Global service instance
execution_queue_service = ExecutionQueueService()