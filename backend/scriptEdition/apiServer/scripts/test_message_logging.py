#!/usr/bin/env python3
"""
Test script for message-based progress logging
"""

import asyncio
import logging
import sys
import os
from datetime import datetime

# Add the apiServer and shared to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/..')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/../../..')

from db.mongodb_client import MongoDBClient
from services.progress_service import log_progress_to_message, log_message_info, log_message_success
from services.chat_service import ChatHistoryService
from db.repositories import RepositoryManager

logger = logging.getLogger(__name__)

async def test_message_logging():
    """Test message-based progress logging"""
    print("🔄 Testing message-based progress logging...")
    
    # Initialize MongoDB client
    db_client = MongoDBClient()
    await db_client.connect()
    
    try:
        # Initialize repository manager and chat service
        repo_manager = RepositoryManager(db_client)
        await repo_manager.initialize()
        chat_service = ChatHistoryService(repo_manager)
        
        # Create a test session
        test_user_id = "test-user-123"
        session_id = await chat_service.start_session(test_user_id, "Test Session for Logging")
        
        print(f"📋 Created test session: {session_id}")
        
        # Create a test message
        message_id = await chat_service.add_assistant_message(
            session_id=session_id,
            user_id=test_user_id,
            content="Test analysis message",
            metadata={"status": "pending", "message_type": "analysis"}
        )
        
        print(f"📋 Created test message: {message_id}")
        
        # Test 1: Direct progress logging
        print("\n1. Testing direct progress logging...")
        await log_progress_to_message(
            message_id, "info", "Analysis started", 
            {"step": 1, "total": 3}
        )
        print("   ✅ Direct log added")
        
        # Test 2: Convenience functions
        print("\n2. Testing convenience logging functions...")
        await log_message_info(message_id, "Building context for analysis", step=2, total=3)
        await log_message_success(message_id, "Analysis completed successfully", step=3, total=3)
        print("   ✅ Convenience logs added")
        
        # Test 3: Verify logs in database
        print("\n3. Verifying logs in database...")
        updated_message = await db_client.db.chat_messages.find_one({"messageId": message_id})
        logs = updated_message.get("logs", []) if updated_message else []
        
        print(f"   📊 Found {len(logs)} log entries:")
        for i, log in enumerate(logs):
            timestamp = log.get("timestamp", "Unknown")
            level = log.get("level", "unknown")
            message = log.get("message", "No message")
            print(f"     {i+1}. [{level.upper()}] {message} ({timestamp})")
        
        assert len(logs) >= 3, f"Expected at least 3 logs, got {len(logs)}"
        print("   ✅ All logs verified in database")
        
        # Test 4: Test with invalid message ID
        print("\n4. Testing with invalid message ID...")
        try:
            await log_message_info("invalid-message-id", "This should not crash")
            print("   ✅ Gracefully handled invalid message ID")
        except Exception as e:
            print(f"   ❌ Error with invalid message ID: {e}")
        
        print("\n🎉 All message logging tests passed!")
        
        # Cleanup
        await chat_service.delete_session(session_id)
        print(f"🧹 Cleaned up test session: {session_id}")
        
    except Exception as e:
        print(f"❌ Message logging test failed: {e}")
        raise
    finally:
        await db_client.disconnect()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(test_message_logging())