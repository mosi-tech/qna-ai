#!/usr/bin/env python3
"""
Migration script: Add logs field to existing chat messages

This script adds an empty logs array to all existing chat messages
that don't already have the logs field.
"""

import asyncio
import logging
from datetime import datetime
import sys
import os

# Add the backend root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))

from shared.db.mongodb_client import MongoDBClient

logger = logging.getLogger(__name__)

async def migrate_add_logs_field():
    """Add logs field to existing messages"""
    print("🔄 Starting migration: Add logs field to chat messages...")
    
    # Initialize MongoDB client
    db_client = MongoDBClient()
    await db_client.connect()
    
    try:
        # Get the messages collection
        messages_collection = db_client.db.chat_messages
        
        # Find messages without logs field
        messages_without_logs = await messages_collection.count_documents({
            "logs": {"$exists": False}
        })
        
        print(f"📊 Found {messages_without_logs} messages without logs field")
        
        if messages_without_logs == 0:
            print("✅ All messages already have logs field - migration complete!")
            return
        
        # Update all messages without logs field
        result = await messages_collection.update_many(
            {"logs": {"$exists": False}},
            {"$set": {"logs": []}}
        )
        
        print(f"✅ Migration complete!")
        print(f"   - Messages updated: {result.modified_count}")
        print(f"   - Messages matched: {result.matched_count}")
        
        # Verify the migration
        remaining_without_logs = await messages_collection.count_documents({
            "logs": {"$exists": False}
        })
        
        if remaining_without_logs == 0:
            print("🎉 Verification successful - all messages now have logs field!")
        else:
            print(f"⚠️  Warning: {remaining_without_logs} messages still missing logs field")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        raise
    finally:
        await db_client.disconnect()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(migrate_add_logs_field())