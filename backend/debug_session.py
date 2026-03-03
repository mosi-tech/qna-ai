#!/usr/bin/env python3
"""
Quick script to debug session 2004555a-1817-4ed8-9032-c344d9183c92
"""

import asyncio
import os
from pymongo import MongoClient

async def debug_session():
    # Connect to MongoDB
    mongo_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    client = MongoClient(mongo_uri)
    db = client["qna-ai-db"]
    
    session_id = "2004555a-1817-4ed8-9032-c344d9183c92"
    
    print(f"Debugging session: {session_id}")
    print("=" * 50)
    
    # Check chat_sessions collection
    print("\n1. Checking chat_sessions collection:")
    sessions = list(db.chat_sessions.find({"sessionId": session_id}))
    if not sessions:
        sessions = list(db.chat_sessions.find({"session_id": session_id}))
    print(f"Found {len(sessions)} sessions")
    for session in sessions:
        print(f"Session: {session}")
    
    # Check chat_messages collection
    print("\n2. Checking chat_messages collection:")
    messages_by_sessionId = list(db.chat_messages.find({"sessionId": session_id}))
    print(f"Found {len(messages_by_sessionId)} messages with sessionId field")
    
    messages_by_session_id = list(db.chat_messages.find({"session_id": session_id}))
    print(f"Found {len(messages_by_session_id)} messages with session_id field")
    
    # Show first few messages
    all_messages = messages_by_sessionId + messages_by_session_id
    for i, msg in enumerate(all_messages[:5]):
        print(f"Message {i+1}: {msg.get('role', 'unknown')} - {msg.get('content', 'no content')[:100]}")
    
    # Check field names in first message
    if all_messages:
        print(f"\n3. Field names in first message:")
        print(f"Keys: {list(all_messages[0].keys())}")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(debug_session())