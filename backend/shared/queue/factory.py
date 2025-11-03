#!/usr/bin/env python3
"""
Factory for creating queue implementations
"""

import logging
from typing import Dict, Any
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from .base_queue import ExecutionQueueInterface
from .execution_queue import MongoDBExecutionQueue

logger = logging.getLogger(__name__)

class QueueFactory:
    """Factory for creating queue implementations"""
    
    @staticmethod
    def create_queue(queue_type: str, config: Dict[str, Any]) -> ExecutionQueueInterface:
        """
        Create a queue implementation based on type and config
        
        Args:
            queue_type: Type of queue ("mongodb", "kafka", "redis", "sqs")
            config: Configuration dictionary for the queue
            
        Returns:
            Queue implementation instance
        """
        if queue_type == "mongodb":
            return QueueFactory._create_mongodb_queue(config)
        elif queue_type == "kafka":
            return QueueFactory._create_kafka_queue(config)
        elif queue_type == "redis":
            return QueueFactory._create_redis_queue(config)
        elif queue_type == "sqs":
            return QueueFactory._create_sqs_queue(config)
        else:
            raise ValueError(f"Unsupported queue type: {queue_type}")
    
    @staticmethod
    def _create_mongodb_queue(config: Dict[str, Any]) -> MongoDBExecutionQueue:
        """Create MongoDB queue implementation"""
        try:
            # Extract MongoDB connection details
            mongo_url = config.get("mongo_url", "mongodb://localhost:27017")
            database_name = config.get("database_name", "qna_ai_admin")
            collection_name = config.get("collection_name", "execution_queue")
            
            # Create motor client and database
            client = AsyncIOMotorClient(mongo_url)
            db = client[database_name]
            
            queue = MongoDBExecutionQueue(db, collection_name)
            logger.info(f"✅ Created MongoDB queue: {mongo_url}/{database_name}/{collection_name}")
            
            return queue
            
        except Exception as e:
            logger.error(f"❌ Failed to create MongoDB queue: {e}")
            raise
    
    @staticmethod
    def _create_kafka_queue(config: Dict[str, Any]) -> ExecutionQueueInterface:
        """Create Kafka queue implementation (placeholder)"""
        # TODO: Implement KafkaExecutionQueue
        raise NotImplementedError("Kafka queue not implemented yet")
    
    @staticmethod
    def _create_redis_queue(config: Dict[str, Any]) -> ExecutionQueueInterface:
        """Create Redis queue implementation (placeholder)"""
        # TODO: Implement RedisExecutionQueue
        raise NotImplementedError("Redis queue not implemented yet")
    
    @staticmethod
    def _create_sqs_queue(config: Dict[str, Any]) -> ExecutionQueueInterface:
        """Create SQS queue implementation (placeholder)"""
        # TODO: Implement SQSExecutionQueue
        raise NotImplementedError("SQS queue not implemented yet")
    
    @staticmethod
    async def create_queue_async(queue_type: str, config: Dict[str, Any]) -> ExecutionQueueInterface:
        """
        Create queue and perform any async initialization
        
        Args:
            queue_type: Type of queue
            config: Configuration dictionary
            
        Returns:
            Initialized queue implementation
        """
        queue = QueueFactory.create_queue(queue_type, config)
        
        # Perform async initialization if needed
        if hasattr(queue, 'ensure_indexes'):
            await queue.ensure_indexes()
        
        return queue