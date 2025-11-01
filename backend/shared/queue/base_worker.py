#!/usr/bin/env python3
"""
Base Queue Worker

Abstract base class for all queue workers with common functionality.
"""

import asyncio
import logging
import uuid
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Set
from datetime import datetime

logger = logging.getLogger(__name__)


class BaseQueueWorker(ABC):
    """Abstract base class for queue workers"""
    
    def __init__(
        self, 
        queue,
        worker_id: Optional[str] = None,
        poll_interval: int = 5,
        max_concurrent_items: int = 3,
        worker_type: str = "worker"
    ):
        self.queue = queue
        self.worker_id = worker_id or f"{worker_type}_{uuid.uuid4().hex[:8]}"
        self.poll_interval = poll_interval
        self.max_concurrent_items = max_concurrent_items
        self.running = False
        self.active_items: Set[asyncio.Task] = set()
        self.worker_type = worker_type
        
        logger.info(f"🔧 Created {self.worker_type}: {self.worker_id}")
    
    async def start(self):
        """Start the worker polling loop"""
        logger.info(f"🚀 Starting {self.worker_type} {self.worker_id}")
        
        # Initialize worker-specific services
        await self._initialize_services()
        
        self.running = True
        
        try:
            while self.running:
                try:
                    # Check if we can handle more items
                    if len(self.active_items) < self.max_concurrent_items:
                        # Try to claim an item from the queue
                        item = await self._dequeue_item()
                        
                        if item:
                            # Process item in background
                            task = asyncio.create_task(self._process_item(item))
                            self.active_items.add(task)
                            
                            # Clean up completed tasks
                            self._cleanup_completed_tasks()
                        else:
                            # No items available, wait before next poll
                            await asyncio.sleep(self.poll_interval)
                    else:
                        # At capacity, wait for some items to complete
                        await asyncio.sleep(1)
                        
                        # Clean up completed tasks
                        self._cleanup_completed_tasks()
                
                except Exception as e:
                    logger.error(f"❌ Error in {self.worker_type} polling loop: {e}")
                    await asyncio.sleep(5)  # Wait longer on error
        
        except asyncio.CancelledError:
            logger.info(f"🛑 {self.worker_type.title()} {self.worker_id} cancelled")
        finally:
            await self._shutdown()
    
    async def stop(self):
        """Stop the worker gracefully"""
        logger.info(f"🛑 Stopping {self.worker_type} {self.worker_id}")
        self.running = False
        
        # Wait for active items to complete (with timeout)
        if self.active_items:
            logger.info(f"⏳ Waiting for {len(self.active_items)} active {self.worker_type} items to complete")
            try:
                await asyncio.wait_for(
                    asyncio.gather(*self.active_items, return_exceptions=True),
                    timeout=30
                )
            except asyncio.TimeoutError:
                logger.warning(f"⚠️ Timeout waiting for {self.worker_type} items to complete")
    
    def _cleanup_completed_tasks(self):
        """Clean up completed tasks from active set"""
        self.active_items = {
            task for task in self.active_items 
            if not task.done()
        }
    
    async def _shutdown(self):
        """Clean up worker resources"""
        # Cancel any remaining tasks
        for task in self.active_items:
            if not task.done():
                task.cancel()
        
        # Cleanup worker-specific resources
        await self._cleanup_services()
        
        logger.info(f"✅ {self.worker_type.title()} {self.worker_id} shutdown complete")
    
    @abstractmethod
    async def _initialize_services(self):
        """Initialize worker-specific services (database, formatters, etc.)"""
        pass
    
    @abstractmethod
    async def _dequeue_item(self):
        """Dequeue an item from the queue"""
        pass
    
    @abstractmethod
    async def _process_item(self, item: Dict[str, Any]):
        """Process a single item from the queue"""
        pass
    
    async def _cleanup_services(self):
        """Cleanup worker-specific services (override if needed)"""
        pass
    
