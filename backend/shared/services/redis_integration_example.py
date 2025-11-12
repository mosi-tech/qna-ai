#!/usr/bin/env python3
"""
Redis Integration Example for ConversationStore
Shows how to connect all pieces together
"""

import asyncio
import logging
from .redis_client import get_redis_client
from .session_manager import SessionManager
from .chat_service import ChatHistoryService
from ..db.repositories import RepositoryManager, MongoDBClient

logger = logging.getLogger(__name__)

async def create_redis_enabled_session_manager() -> SessionManager:
    """Create SessionManager with Redis support
    
    Example usage:
        session_manager = await create_redis_enabled_session_manager()
        conversation = await session_manager.get_session("session_123")
        await conversation.add_user_message("Hello!")
    """
    
    # 1. Initialize Redis client
    redis_client = await get_redis_client()
    if redis_client:
        logger.info("✅ Redis enabled for ConversationStore")
    else:
        logger.warning("⚠️ Redis disabled - falling back to DB-only")
    
    # 2. Initialize MongoDB (if needed)
    try:
        # This would typically be initialized elsewhere in your app
        mongo_client = MongoDBClient()
        await mongo_client.connect()
        repo_manager = RepositoryManager(mongo_client)
        chat_service = ChatHistoryService(repo_manager.chat)
        logger.info("✅ MongoDB connected for persistence")
    except Exception as e:
        logger.warning(f"⚠️ MongoDB connection failed: {e}")
        chat_service = None
    
    # 3. Create SessionManager with both Redis and DB
    session_manager = SessionManager(
        chat_history_service=chat_service,
        redis_client=redis_client
    )
    
    return session_manager

async def demo_redis_conversation():
    """Demo showing Redis-backed conversation"""
    
    session_manager = await create_redis_enabled_session_manager()
    session_id = "demo_session_123"
    
    # Add some messages
    await session_manager.add_user_message(session_id, "What's the weather like?")
    await session_manager.add_assistant_message(session_id, "I can't check weather, but I can help with financial analysis!")
    
    # Get messages (from Redis)
    messages = await session_manager.get_messages(session_id)
    logger.info(f"Retrieved {len(messages)} messages from Redis")
    
    for msg in messages:
        logger.info(f"  {msg.role}: {msg.content[:50]}...")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(demo_redis_conversation())