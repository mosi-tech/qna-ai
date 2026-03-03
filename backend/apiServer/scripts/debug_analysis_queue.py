#!/usr/bin/env python3
"""
Debug script to check analysis queue collection in MongoDB
"""

import asyncio
import sys
import os

# Add backend directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from shared.db.mongodb_client import MongoDBClient

async def main():
    """Check analysis queue collection contents"""
    db_client = MongoDBClient()
    
    try:
        # Connect to MongoDB
        await db_client.connect()
        
        # Get the collection
        collection = db_client.db.analysis_queue
        
        # Count documents
        count = await collection.count_documents({})
        print(f"📊 Total documents in analysis_queue: {count}")
        
        # Get last 10 documents
        print("\n📋 Last 10 documents:")
        async for doc in collection.find({}).sort("created_at", -1).limit(10):
            print(f"  - Job ID: {doc.get('job_id')}")
            print(f"    Status: {doc.get('status')}")
            print(f"    Message ID: {doc.get('message_id')}")
            print(f"    Session ID: {doc.get('session_id')}")
            print(f"    Created: {doc.get('created_at')}")
            print()
        
        # Check specific job if provided
        if len(sys.argv) > 1:
            job_id = sys.argv[1]
            job = await collection.find_one({"job_id": job_id})
            if job:
                print(f"✅ Found job {job_id}:")
                print(f"   {job}")
            else:
                print(f"❌ Job {job_id} not found")
        
        await db_client.disconnect()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
