#!/usr/bin/env python3

import asyncio
from db import MongoDBClient

async def cleanup_db():
    """Clean all test data from MongoDB"""
    db_client = MongoDBClient()
    await db_client.connect()
    
    try:
        collections = ["chat_sessions", "chat_messages", "analyses", "executions", "cache", "audit_logs", "users"]
        
        print("Cleaning MongoDB test data...")
        for coll_name in collections:
            result = await db_client.db[coll_name].delete_many({})
            print(f"  - {coll_name}: deleted {result.deleted_count} documents")
        
        print("✅ Cleanup complete")
        
    finally:
        await db_client.disconnect()

if __name__ == "__main__":
    asyncio.run(cleanup_db())
