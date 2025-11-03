#!/usr/bin/env python3
"""
Test script for analysis queue system
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

logger = logging.getLogger(__name__)

async def test_analysis_queue():
    """Test the analysis queue system"""
    print("🔄 Testing analysis queue system...")
    
    # Initialize MongoDB client
    db_client = MongoDBClient()
    await db_client.connect()
    
    try:
        # Initialize analysis queue
        initialize_analysis_queue(db_client.db)
        queue = get_analysis_queue()
        
        test_analysis_data = {
            "session_id": "test-session-123",
            "message_id": "test-message-456", 
            "user_question": "What is the current price of AAPL?",
            "user_message_id": "test-user-msg-789"
        }
        
        print(f"📋 Testing analysis queue with data: {test_analysis_data}")
        
        # Test 1: Enqueue analysis
        print("\n1. Testing analysis enqueue...")
        job_id = await queue.enqueue_analysis(test_analysis_data)
        print(f"   ✅ Analysis enqueued with job ID: {job_id}")
        assert job_id, "Should return a job ID"
        
        # Test 2: Check queue stats
        print("\n2. Testing queue statistics...")
        stats = await queue.get_queue_stats()
        print(f"   📊 Queue stats: {stats}")
        assert stats.get("pending", 0) >= 1, "Should have at least one pending job"
        
        # Test 3: Dequeue analysis
        print("\n3. Testing analysis dequeue...")
        worker_id = "test-worker-123"
        claimed_job = await queue.dequeue_analysis(worker_id)
        print(f"   📤 Claimed job: {claimed_job['job_id'] if claimed_job else 'None'}")
        assert claimed_job, "Should be able to claim the queued job"
        assert claimed_job["job_id"] == job_id, "Should claim the correct job"
        
        # Test 4: Try to dequeue again (should be empty)
        print("\n4. Testing empty queue dequeue...")
        empty_job = await queue.dequeue_analysis(worker_id)
        print(f"   📭 Empty dequeue result: {empty_job}")
        assert empty_job is None, "Queue should be empty"
        
        # Test 5: Ack the job
        print("\n5. Testing job acknowledgment...")
        result_data = {
            "script_content": "# Test script\nprint('Hello Analysis')",
            "analysis_data": {"confidence": 0.95},
            "status": "completed"
        }
        ack_success = await queue.ack_analysis(job_id, result_data)
        print(f"   ✅ Job acknowledged: {ack_success}")
        assert ack_success, "Should successfully acknowledge job"
        
        # Test 6: Check final stats
        print("\n6. Testing final queue statistics...")
        final_stats = await queue.get_queue_stats()
        print(f"   📊 Final stats: {final_stats}")
        assert final_stats.get("completed", 0) >= 1, "Should have at least one completed job"
        
        # Test 7: Test job failure (enqueue another)
        print("\n7. Testing job failure handling...")
        failure_job_id = await queue.enqueue_analysis({
            **test_analysis_data,
            "message_id": "failure-test-msg"
        })
        failure_job = await queue.dequeue_analysis(worker_id)
        nack_success = await queue.nack_analysis(failure_job_id, "Test error", retry=False)
        print(f"   ❌ Job failed successfully: {nack_success}")
        assert nack_success, "Should successfully mark job as failed"
        
        print("\n🎉 All analysis queue tests passed!")
        
    except Exception as e:
        print(f"❌ Analysis queue test failed: {e}")
        raise
    finally:
        await db_client.disconnect()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(test_analysis_queue())