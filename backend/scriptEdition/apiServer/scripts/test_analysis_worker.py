#!/usr/bin/env python3
"""
Test script for analysis worker with extracted logic
"""

import asyncio
import logging
import sys
import os

# Add the apiServer and shared to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/..')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/../../..')

from db.mongodb_client import MongoDBClient
from shared.queue.analysis_queue import initialize_analysis_queue, get_analysis_queue
from shared.queue.analysis_worker import AnalysisQueueWorker
from services.chat_service import ChatHistoryService
from db.repositories import RepositoryManager

logger = logging.getLogger(__name__)

async def test_analysis_worker():
    """Test the analysis worker with extracted logic"""
    print("🔄 Testing analysis worker with extracted logic...")
    
    # Initialize MongoDB client
    db_client = MongoDBClient()
    await db_client.connect()
    
    try:
        # Initialize repository manager and chat service
        repo_manager = RepositoryManager(db_client)
        await repo_manager.initialize()
        chat_service = ChatHistoryService(repo_manager)
        
        # Initialize analysis queue
        initialize_analysis_queue(db_client.db)
        queue = get_analysis_queue()
        
        # Create test session and message
        test_user_id = "test-user-worker"
        session_id = await chat_service.start_session(test_user_id, "Test Analysis Worker Session")
        
        message_id = await chat_service.add_assistant_message(
            session_id=session_id,
            user_id=test_user_id,
            content="Test analysis message for worker",
            metadata={"status": "pending", "message_type": "analysis"}
        )
        
        print(f"📋 Created test session: {session_id}")
        print(f"📋 Created test message: {message_id}")
        
        # Prepare analysis job data
        test_analysis_data = {
            "session_id": session_id,
            "message_id": message_id,
            "user_question": "What is the current price and volume of AAPL stock?",
            "user_message_id": "test-user-msg-789"
        }
        
        print(f"📋 Test analysis data: {test_analysis_data}")
        
        # Test 1: Create analysis worker with extracted logic
        print("\\n1. Creating analysis worker...")
        worker = AnalysisQueueWorker(queue, worker_id="test-worker-extracted", poll_interval=1)
        print(f"   ✅ Worker created: {worker.worker_id}")
        
        # Test 2: Enqueue analysis job
        print("\\n2. Enqueuing analysis job...")
        job_id = await queue.enqueue_analysis(test_analysis_data)
        print(f"   ✅ Analysis enqueued with job ID: {job_id}")
        
        # Test 3: Process one analysis job manually (not in polling loop)
        print("\\n3. Processing analysis job manually...")
        job = await queue.dequeue_analysis(worker.worker_id)
        if job:
            print(f"   📤 Claimed job: {job['job_id']}")
            
            # Process the job manually
            await worker._process_analysis(job)
            print("   ✅ Job processed successfully")
        else:
            print("   ❌ No job to process")
        
        # Test 4: Check message logs
        print("\\n4. Checking message logs...")
        updated_message = await db_client.db.chat_messages.find_one({"messageId": message_id})
        logs = updated_message.get("logs", []) if updated_message else []
        
        print(f"   📊 Found {len(logs)} log entries:")
        for i, log in enumerate(logs):
            timestamp = log.get("timestamp", "Unknown")
            level = log.get("level", "unknown")
            message = log.get("message", "No message")
            print(f"     {i+1}. [{level.upper()}] {message} ({timestamp})")
        
        # Test 5: Check queue completion
        print("\\n5. Checking queue statistics...")
        final_stats = await queue.get_queue_stats()
        print(f"   📊 Final stats: {final_stats}")
        
        print("\\n🎉 Analysis worker test completed!")
        
        # Cleanup
        await chat_service.delete_session(session_id)
        print(f"🧹 Cleaned up test session: {session_id}")
        
    except Exception as e:
        print(f"❌ Analysis worker test failed: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        await db_client.disconnect()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    asyncio.run(test_analysis_worker())