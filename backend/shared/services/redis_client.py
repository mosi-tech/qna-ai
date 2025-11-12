#!/usr/bin/env python3
"""
Redis Client Configuration for ConversationStore
Provides Redis/KeyDB connection with fallback behavior
"""

import os
import logging
from typing import Optional
try:
    import redis.asyncio as redis
except ImportError:
    redis = None

logger = logging.getLogger(__name__)

class RedisClientManager:
    """Manage Redis connection for ConversationStore"""
    
    def __init__(self, redis_url: Optional[str] = None):
        self.redis_url = redis_url or os.getenv('REDIS_URL', 'redis://localhost:6379')
        self.client: Optional[redis.Redis] = None
        
    async def get_client(self) -> Optional[redis.Redis]:
        """Get Redis client with automatic connection"""
        if not redis:
            logger.warning("⚠️ Redis not installed - ConversationStore will run without Redis")
            return None
            
        if self.client is None:
            try:
                self.client = redis.from_url(
                    self.redis_url,
                    decode_responses=True,  # Auto-decode bytes to strings
                    socket_keepalive=True,
                    socket_keepalive_options={},
                    health_check_interval=30
                )
                
                # Test connection
                await self.client.ping()
                logger.info(f"✅ Redis connected: {self.redis_url}")
                
            except Exception as e:
                logger.warning(f"⚠️ Redis connection failed: {e}")
                logger.warning("ConversationStore will run without Redis (fallback to DB-only)")
                self.client = None
                
        return self.client
    
    async def close(self):
        """Close Redis connection"""
        if self.client:
            await self.client.close()
            self.client = None
            logger.info("✅ Redis connection closed")

# Global instance for easy access
redis_manager = RedisClientManager()

async def get_redis_client() -> Optional[redis.Redis]:
    """Get global Redis client instance"""
    return await redis_manager.get_client()

async def close_redis():
    """Close global Redis connection"""
    await redis_manager.close()