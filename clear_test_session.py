#!/usr/bin/env python3
"""
Clear test session messages from MongoDB
"""

import asyncio
import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def clear_session_messages(session_id: str):
    """Clear all messages for a specific session"""
    try:
        # Import after adding to path
        from backend.shared.db.repositories import RepositoryManager
        from backend.shared.config.database import get_database
        
        print(f"🧹 Clearing messages for session: {session_id}")
        
        # Get database and repository
        db = get_database()
        repo_manager = RepositoryManager(db)
        
        # Delete all messages for this session
        result = await repo_manager.chat.db.chat_messages.delete_many({
            "sessionId": session_id
        })
        
        print(f"✅ Deleted {result.deleted_count} messages")
        
        # Also delete session if exists
        session_result = await repo_manager.chat.db.chat_sessions.delete_many({
            "sessionId": session_id  
        })
        
        print(f"✅ Deleted {session_result.deleted_count} session records")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to clear session: {e}")
        return False

async def main():
    session_id = "6ca6d50c-d2bf-4ce5-acd2-96267c41766e"
    
    print("🧹 Clearing Test Session Messages")
    print(f"Session ID: {session_id}")
    
    success = await clear_session_messages(session_id)
    
    if success:
        print("✅ Session cleared successfully!")
    else:
        print("❌ Failed to clear session")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())