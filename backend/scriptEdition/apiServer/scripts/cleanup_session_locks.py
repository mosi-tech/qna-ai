#!/usr/bin/env python3
"""
Clean up session locks collection for testing
"""

import asyncio
import logging
import sys
import os

# Add the apiServer and shared to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/..')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/../../..')

from db.mongodb_client import MongoDBClient

logger = logging.getLogger(__name__)

async def cleanup_session_locks():
    """Clean up the session locks collection"""
    print("🧹 Cleaning up session locks...")
    
    # Initialize MongoDB client
    db_client = MongoDBClient()
    await db_client.connect()
    
    try:
        # Drop the entire collection to reset it
        await db_client.db.session_locks.drop()
        print("✅ Session locks collection dropped")
        
    except Exception as e:
        print(f"❌ Cleanup failed: {e}")
        raise
    finally:
        await db_client.disconnect()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(cleanup_session_locks())