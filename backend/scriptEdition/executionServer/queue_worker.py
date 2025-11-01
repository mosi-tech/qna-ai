#!/usr/bin/env python3
"""
Unified Queue Worker Script

Runs either analysis or execution workers from MongoDB queues.
Can be run as a separate service or background process.

Usage:
    python queue_worker.py --type [analysis|execution] [--worker-id WORKER_ID] [--poll-interval SECONDS] [--max-concurrent N]
"""

import asyncio
import argparse
import logging
import os
import signal
import sys
from typing import Optional

# Add shared module path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.queue import QueueFactory, ExecutionQueueWorker
from shared.queue.analysis_worker import AnalysisQueueWorker
from shared.queue.analysis_queue import initialize_analysis_queue, get_analysis_queue
from shared.queue.progress_event_queue import initialize_progress_event_queue, get_progress_event_queue
from shared.queue.base_worker import BaseQueueWorker

logger = logging.getLogger("queue-worker")

class QueueWorkerService:
    """Standalone service for running queue workers"""
    
    def __init__(self, worker_type: str, worker_id: Optional[str] = None, poll_interval: int = 5, max_concurrent: int = 3):
        self.worker_type = worker_type
        self.worker_id = worker_id
        self.poll_interval = poll_interval
        self.max_concurrent = max_concurrent
        self.worker: Optional[BaseQueueWorker] = None  # Will be either ExecutionQueueWorker or AnalysisQueueWorker
        self.running = False
    
    async def start(self):
        """Start the queue worker service"""
        try:
            logger.info(f"🚀 Starting {self.worker_type} worker...")
            
            if self.worker_type == "execution":
                await self._start_execution_worker()
            elif self.worker_type == "analysis":
                await self._start_analysis_worker()
            else:
                raise ValueError(f"Unknown worker type: {self.worker_type}")
                
            self.running = True
            
            # Start worker
            await self.worker.start()
            
        except Exception as e:
            logger.error(f"❌ Failed to start {self.worker_type} worker: {e}")
            raise
    
    async def _start_execution_worker(self):
        """Start execution worker"""
        # Initialize execution queue
        queue_config = {
            "mongo_url": os.getenv("MONGO_URL", "mongodb://localhost:27017"),
            "database_name": os.getenv("MONGO_DB_NAME", "qna_ai_admin"),
            "collection_name": "execution_queue"
        }
        
        logger.info("🔧 Initializing execution queue connection...")
        queue = await QueueFactory.create_queue_async("mongodb", queue_config)
        
        # Create execution worker
        self.worker = ExecutionQueueWorker(
            queue=queue,
            worker_id=self.worker_id,
            poll_interval=self.poll_interval,
            max_concurrent_executions=self.max_concurrent
        )
        
        logger.info(f"🚀 Execution worker ready: {self.worker.worker_id}")
        logger.info(f"⚙️  Poll interval: {self.poll_interval}s")
        logger.info(f"⚙️  Max concurrent executions: {self.max_concurrent}")
    
    async def _start_analysis_worker(self):
        """Start analysis worker"""
        # Initialize MongoDB connection
        from db.mongodb_client import MongoDBClient
        from db.repositories import RepositoryManager
        
        db_client = MongoDBClient()
        await db_client.connect()
        repo_manager = RepositoryManager(db_client)
        await repo_manager.initialize()
        db = db_client.db
        
        # Initialize progress event queue
        initialize_progress_event_queue(db)
        
        # Initialize analysis queue
        initialize_analysis_queue(db)
        analysis_queue = get_analysis_queue()
        
        # Create analysis worker
        self.worker = AnalysisQueueWorker(
            queue=analysis_queue,
            worker_id=self.worker_id,
            poll_interval=self.poll_interval,
            max_concurrent_analyses=self.max_concurrent
        )
        
        logger.info(f"🚀 Analysis worker ready: {self.worker.worker_id}")
        logger.info(f"⚙️  Poll interval: {self.poll_interval}s")
        logger.info(f"⚙️  Max concurrent analyses: {self.max_concurrent}")
    
    async def stop(self):
        """Stop the queue worker service gracefully"""
        if self.worker and self.running:
            logger.info("🛑 Stopping queue worker...")
            await self.worker.stop()
            self.running = False
            logger.info("✅ Queue worker stopped")

# Global service instance (will be initialized in main)
worker_service = None

async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Unified Queue Worker for Analysis and Execution")
    parser.add_argument("--type", required=True, choices=["analysis", "execution"], help="Worker type: analysis or execution")
    parser.add_argument("--worker-id", help="Unique worker identifier")
    parser.add_argument("--poll-interval", type=int, default=5, help="Polling interval in seconds (default: 5)")
    parser.add_argument("--max-concurrent", type=int, default=3, help="Maximum concurrent jobs (default: 3)")
    parser.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"],
                       help="Logging level (default: INFO)")
    
    args = parser.parse_args()
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Initialize service
    global worker_service
    worker_service = QueueWorkerService(
        worker_type=args.type,
        worker_id=args.worker_id,
        poll_interval=args.poll_interval,
        max_concurrent=args.max_concurrent
    )
    
    # Set up signal handlers for graceful shutdown
    def signal_handler(signum, frame):
        logger.info(f"🛑 Received signal {signum}, initiating graceful shutdown...")
        asyncio.create_task(worker_service.stop())
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Start the worker service
        await worker_service.start()
        
    except KeyboardInterrupt:
        logger.info("🛑 Keyboard interrupt received")
    except Exception as e:
        logger.error(f"❌ Worker service error: {e}")
        return 1
    finally:
        if worker_service.running:
            await worker_service.stop()
    
    return 0

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        sys.exit(1)