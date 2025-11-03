#!/usr/bin/env python3
"""
Test script for distributed session locking
"""

import asyncio
import logging
import sys
import os

# Add the apiServer and shared to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/..')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/../../..')

from db.mongodb_client import MongoDBClient
from shared.locking import initialize_session_lock, get_session_lock

logger = logging.getLogger(__name__)

async def test_session_locking():
    """Test the distributed session locking system"""
    print("🔄 Testing distributed session locking...")
    
    # Initialize MongoDB client
    db_client = MongoDBClient()
    await db_client.connect()
    
    try:
        # Initialize session lock
        await initialize_session_lock(db_client.db)
        session_lock = get_session_lock()
        
        test_session_id = "test-session-123"
        test_message_id = "test-message-456"
        
        print(f"📋 Testing session: {test_session_id}")
        
        # Test 1: Acquire lock
        print("\n1. Testing lock acquisition...")
        success = await session_lock.acquire_lock(test_session_id, test_message_id)
        print(f"   ✅ Lock acquired: {success}")
        assert success, "Should be able to acquire lock for new session"
        
        # Test 2: Try to acquire same lock (should fail)
        print("\n2. Testing duplicate lock acquisition...")
        success = await session_lock.acquire_lock(test_session_id, "another-message")
        print(f"   ❌ Duplicate lock blocked: {not success}")
        assert not success, "Should not be able to acquire lock for already locked session"
        
        # Test 3: Check active message
        print("\n3. Testing active message retrieval...")
        active_message = await session_lock.get_active_message(test_session_id)
        print(f"   📋 Active message: {active_message}")
        assert active_message == test_message_id, f"Expected {test_message_id}, got {active_message}"
        
        # Test 4: Check lock status
        print("\n4. Testing lock status check...")
        is_locked = await session_lock.is_session_locked(test_session_id)
        print(f"   🔒 Session locked: {is_locked}")
        assert is_locked, "Session should be locked"
        
        # Test 5: List active locks
        print("\n5. Testing active locks listing...")
        active_locks = await session_lock.list_active_locks()
        print(f"   📊 Active locks: {len(active_locks)}")
        assert len(active_locks) >= 1, "Should have at least one active lock"
        
        # Test 6: Extend lock
        print("\n6. Testing lock extension...")
        await session_lock.extend_lock(test_session_id, 3600)  # 1 hour
        print("   ⏰ Lock extended successfully")
        
        # Test 7: Release lock
        print("\n7. Testing lock release...")
        await session_lock.release_lock(test_session_id)
        print("   🔓 Lock released")
        
        # Test 8: Verify lock is gone
        print("\n8. Testing lock release verification...")
        is_locked = await session_lock.is_session_locked(test_session_id)
        print(f"   🔓 Session unlocked: {not is_locked}")
        assert not is_locked, "Session should be unlocked after release"
        
        # Test 9: Try to acquire lock again (should work now)
        print("\n9. Testing lock re-acquisition...")
        success = await session_lock.acquire_lock(test_session_id, test_message_id)
        print(f"   ✅ Lock re-acquired: {success}")
        assert success, "Should be able to re-acquire lock after release"
        
        # Clean up
        await session_lock.release_lock(test_session_id)
        
        print("\n🎉 All session locking tests passed!")
        
    except Exception as e:
        print(f"❌ Session locking test failed: {e}")
        raise
    finally:
        await db_client.disconnect()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(test_session_locking())