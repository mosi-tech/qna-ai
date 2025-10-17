#!/usr/bin/env python3
"""
Database Cleanup Script
Use this to clear all data from the database and reset to clean state
Run: python scripts/cleanup_database.py
"""

import asyncio
import sys
import logging

sys.path.insert(0, '/Users/shivc/Documents/Workspace/JS/qna-ai-admin/ollama-server/scriptEdition/apiServer')

from db import MongoDBClient

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("cleanup")


async def cleanup_database(confirmed: bool = False):
    """Clear all collections from the database"""
    
    logger.info("=" * 80)
    logger.info("DATABASE CLEANUP SCRIPT")
    logger.info("=" * 80)
    
    if not confirmed:
        logger.warning("\n⚠️  WARNING: This will DELETE ALL DATA from the database!")
        logger.warning("   This action is IRREVERSIBLE.\n")
        
        response = input("Type 'DELETE' to confirm: ").strip().upper()
        
        if response != "DELETE":
            logger.info("❌ Cleanup cancelled")
            return False
    
    try:
        logger.info("\n🔌 Connecting to MongoDB...")
        db_client = MongoDBClient()
        await db_client.connect()
        
        db = db_client.db
        
        # Collections to clear
        collections = [
            "users",
            "chat_sessions",
            "chat_messages",
            "analyses",
            "executions",
            "saved_analyses",
            "audit_logs",
            "cache",
            "test_connection"
        ]
        
        logger.info("\n🗑️  Clearing collections...\n")
        
        total_deleted = 0
        for collection_name in collections:
            try:
                result = await db[collection_name].delete_many({})
                total_deleted += result.deleted_count
                logger.info(f"  ✓ {collection_name}: deleted {result.deleted_count} documents")
            except Exception as e:
                logger.warning(f"  ⚠️  {collection_name}: {str(e)}")
        
        logger.info("\n" + "=" * 80)
        logger.info(f"✅ CLEANUP COMPLETE: Deleted {total_deleted} total documents")
        logger.info("=" * 80)
        logger.info("\nDatabase is now clean. You can:")
        logger.info("- Run: python scripts/seed_development_data.py (to seed sample data)")
        logger.info("- Run: python server.py (to start with empty database)")
        logger.info("- Hit the /analyze endpoint to create new data organically")
        logger.info("=" * 80)
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Cleanup failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        await db_client.disconnect()


async def main():
    # Check for --confirm flag
    confirmed = "--confirm" in sys.argv
    
    success = await cleanup_database(confirmed=confirmed)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
