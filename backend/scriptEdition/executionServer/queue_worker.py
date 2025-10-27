#!/usr/bin/env python3
"""
Standalone Queue Worker Script

Runs independently to process executions from the MongoDB queue.
Can be run as a separate service or background process.

Usage:
    python queue_worker.py [--worker-id WORKER_ID] [--poll-interval SECONDS] [--max-concurrent N]
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

logger = logging.getLogger("queue-worker")

class QueueWorkerService:
    """Standalone service for running queue workers"""
    
    def __init__(self, worker_id: Optional[str] = None, poll_interval: int = 5, max_concurrent: int = 3):
        self.worker_id = worker_id
        self.poll_interval = poll_interval
        self.max_concurrent = max_concurrent
        self.worker: Optional[ExecutionQueueWorker] = None
        self.running = False
    
    async def start(self):
        """Start the queue worker service"""
        try:
            # Initialize queue
            queue_config = {
                "mongo_url": os.getenv("MONGO_URL", "mongodb://localhost:27017"),
                "database_name": os.getenv("MONGO_DB_NAME", "qna_ai_admin"),
                "collection_name": "execution_queue"
            }
            
            logger.info("🔧 Initializing queue connection...")
            queue = await QueueFactory.create_queue_async("mongodb", queue_config)
            
            # Create worker
            self.worker = ExecutionQueueWorker(
                queue=queue,
                worker_id=self.worker_id,
                poll_interval=self.poll_interval,
                max_concurrent_executions=self.max_concurrent
            )
            
            logger.info(f"🚀 Starting queue worker: {self.worker.worker_id}")
            logger.info(f"⚙️  Poll interval: {self.poll_interval}s")
            logger.info(f"⚙️  Max concurrent executions: {self.max_concurrent}")
            
            self.running = True
            
            # Start worker
            await self.worker.start()
            
        except Exception as e:
            logger.error(f"❌ Failed to start queue worker: {e}")
            raise
    
    async def stop(self):
        """Stop the queue worker service gracefully"""
        if self.worker and self.running:
            logger.info("🛑 Stopping queue worker...")
            await self.worker.stop()
            self.running = False
            logger.info("✅ Queue worker stopped")

# Global service instance
worker_service = QueueWorkerService()

async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="MongoDB Queue Worker for Script Execution")
    parser.add_argument("--worker-id", help="Unique worker identifier")
    parser.add_argument("--poll-interval", type=int, default=5, help="Polling interval in seconds (default: 5)")
    parser.add_argument("--max-concurrent", type=int, default=3, help="Maximum concurrent executions (default: 3)")
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