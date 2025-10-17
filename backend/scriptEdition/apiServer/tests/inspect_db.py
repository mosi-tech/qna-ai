#!/usr/bin/env python3
"""
Inspect MongoDB test data
"""

import asyncio
import json
from db import MongoDBClient

async def inspect_data():
    """Inspect all test data in MongoDB"""
    db_client = MongoDBClient()
    await db_client.connect()
    
    try:
        print("=" * 80)
        print("MONGODB DATA INSPECTION")
        print("=" * 80)
        
        collections = ["chat_sessions", "chat_messages", "analyses", "executions", "cache"]
        
        for coll_name in collections:
            print(f"\n{'=' * 80}")
            print(f"COLLECTION: {coll_name}")
            print(f"{'=' * 80}")
            
            collection = db_client.db[coll_name]
            count = await collection.count_documents({})
            print(f"Total documents: {count}\n")
            
            docs = await collection.find({}).to_list(100)
            
            for i, doc in enumerate(docs, 1):
                print(f"\n--- Document {i} ---")
                # Convert to JSON-serializable format
                doc_copy = doc.copy()
                
                # Handle datetime objects
                for key, value in doc_copy.items():
                    if hasattr(value, 'isoformat'):
                        doc_copy[key] = value.isoformat()
                    elif isinstance(value, dict):
                        for k, v in value.items():
                            if hasattr(v, 'isoformat'):
                                value[k] = v.isoformat()
                
                print(json.dumps(doc_copy, indent=2, default=str))
        
        print(f"\n{'=' * 80}")
        print("END OF INSPECTION")
        print(f"{'=' * 80}\n")
        
    finally:
        await db_client.client.close()

if __name__ == "__main__":
    asyncio.run(inspect_data())
