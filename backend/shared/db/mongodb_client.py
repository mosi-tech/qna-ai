"""
MongoDB Client - Connection management and operations
"""

import os
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo import ASCENDING, DESCENDING, TEXT
from bson import ObjectId

AsyncClient = AsyncIOMotorClient
AsyncDatabase = AsyncIOMotorDatabase

def oid_to_str(oid: ObjectId) -> str:
    """Convert ObjectId to string"""
    return str(oid)

def str_to_oid(s: str) -> ObjectId:
    """Convert string to ObjectId"""
    try:
        return ObjectId(s)
    except:
        return None

from .schemas import (
    UserModel,
    ChatSessionModel,
    ChatMessageModel,
    AnalysisModel,
    ExecutionModel,
    AuditLogModel,
    SavedAnalysisModel,
    CacheModel,
)

logger = logging.getLogger("mongodb-client")


# Field name mapping from snake_case (Python) to camelCase (MongoDB)
FIELD_ALIAS_MAP = {
    # User fields
    "user_id": "userId",
    "last_login": "lastLogin",
    "user_agent": "userAgent",
    # Session fields
    "session_id": "sessionId",
    "message_count": "messageCount",
    "is_archived": "isArchived",
    "created_at": "createdAt",
    "updated_at": "updatedAt",
    "last_message_at": "lastMessageAt",
    "analysis_ids": "analysisIds",
    # Message fields
    "message_id": "messageId",
    "message_index": "messageIndex",
    "analysis_id": "analysisId",
    "execution_id": "executionId",
    # Analysis fields
    "script_url": "scriptUrl",
    "llm_response": "llmResponse",
    "last_used_at": "lastUsedAt",
    "usage_count": "usageCount",
    # Execution fields
    "created_message_id": "createdMessageId",
    "generated_script": "generatedScript",
    "started_at": "startedAt",
    "completed_at": "completedAt",
    "execution_time_ms": "executionTimeMs",
    "mcp_calls": "mcpCalls",
    "mcp_errors": "mcpErrors",
    "memory_used_mb": "memoryUsedMb",
    "cpu_percent": "cpuPercent",
    "cache_hit": "cacheHit",
    "cache_key": "cacheKey",
    # Cache fields
    "cache_id": "cacheId",
    "hit_count": "hitCount",
    "expires_at": "expiresAt",
    # SavedAnalysis fields
    "saved_analysis_id": "savedAnalysisId",
    "is_favorited": "isFavorited",
    # AuditLog fields
    "audit_log_id": "auditLogId",
    "operation": "operation",
    "resource_type": "resourceType",
    "resource_id": "resourceId",
    "user_id": "userId",
    "ip_address": "ipAddress",
    "error_message": "errorMessage",
}


def convert_to_camel_case(data: Dict[str, Any]) -> Dict[str, Any]:
    """Convert snake_case keys to camelCase using alias mapping"""
    converted = {}
    for key, value in data.items():
        mapped_key = FIELD_ALIAS_MAP.get(key, key)
        converted[mapped_key] = value
    return converted


class MongoDBClient:
    """Async MongoDB client for all database operations"""
    
    def __init__(self):
        self.client: Optional[AsyncClient] = None
        self.db: Optional[AsyncDatabase] = None
        self.mongodb_uri = os.getenv(
            "MONGODB_URI",
            "mongodb://localhost:27017"
        )
        self.db_name = os.getenv("MONGODB_DB_NAME", "qna_ai_admin")
    
    async def connect(self) -> None:
        """Connect to MongoDB and initialize indexes"""
        try:
            self.client = AsyncClient(self.mongodb_uri)
            self.db = self.client[self.db_name]
            
            # Test connection
            await self.client.admin.command('ping')
            logger.info(f"✅ Connected to MongoDB: {self.db_name}")
            
            # Initialize indexes
            await self._create_indexes()
            logger.info("✅ Database indexes created")
            
        except Exception as e:
            logger.error(f"❌ Failed to connect to MongoDB: {e}")
            raise
    
    async def disconnect(self) -> None:
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            logger.info("✅ Disconnected from MongoDB")
    
    async def _create_indexes(self) -> None:
        """Create all collection indexes"""
        collections_config = {
            "users": [
                ([("userId", ASCENDING)], {"unique": True}),
                ([("email", ASCENDING)], {"unique": True}),
                ([("created_at", DESCENDING)], {}),
            ],
            "chat_sessions": [
                ([("sessionId", ASCENDING)], {"unique": True}),
                ([("userId", ASCENDING), ("created_at", DESCENDING)], {}),
                ([("userId", ASCENDING), ("is_archived", ASCENDING)], {}),
                ([("last_message_at", DESCENDING)], {}),
                ([("title", TEXT)], {}),
            ],
            "chat_messages": [
                ([("messageId", ASCENDING)], {"unique": True}),
                ([("sessionId", ASCENDING), ("created_at", ASCENDING)], {}),
                ([("userId", ASCENDING), ("created_at", DESCENDING)], {}),
                ([("role", ASCENDING)], {}),
                ([("analysisId", ASCENDING)], {}),
            ],
            "analyses": [
                ([("analysisId", ASCENDING)], {"unique": True}),
                ([("userId", ASCENDING), ("created_at", DESCENDING)], {}),
                ([("category", ASCENDING)], {}),
                ([("is_template", ASCENDING)], {}),
                ([("tags", ASCENDING)], {}),
                ([("title", TEXT), ("description", TEXT)], {}),
            ],
            "executions": [
                ([("executionId", ASCENDING)], {"unique": True}),
                ([("userId", ASCENDING), ("created_at", DESCENDING)], {}),
                ([("sessionId", ASCENDING)], {}),
                ([("status", ASCENDING)], {}),
                ([("started_at", DESCENDING)], {}),
            ],
            "saved_analyses": [
                ([("savedAnalysisId", ASCENDING)], {"unique": True}),
                ([("userId", ASCENDING), ("created_at", DESCENDING)], {}),
                ([("userId", ASCENDING), ("is_template", ASCENDING)], {}),
                ([("tags", ASCENDING)], {}),
            ],
            "audit_logs": [
                ([("auditLogId", ASCENDING)], {"unique": True}),
                ([("userId", ASCENDING), ("created_at", DESCENDING)], {}),
                ([("action", ASCENDING)], {}),
                ([("resource_type", ASCENDING), ("resource_id", ASCENDING)], {}),
                ([("created_at", DESCENDING)], {}),
            ],
            "cache": [
                ([("cacheId", ASCENDING)], {"unique": True}),
                ([("cache_key", ASCENDING)], {}),
                ([("expires_at", ASCENDING)], {"expireAfterSeconds": 0}),
            ],
        }
        
        for collection_name, indexes in collections_config.items():
            collection = self.db[collection_name]
            for index_fields, index_options in indexes:
                try:
                    await collection.create_index(index_fields, **index_options)
                except Exception as e:
                    logger.warning(f"Index creation warning for {collection_name}: {e}")
    
    # ========================================================================
    # USER OPERATIONS
    # ========================================================================
    
    async def create_user(self, user: UserModel) -> str:
        """Create new user"""
        result = await self.db.users.insert_one(user.dict(by_alias=True))
        await self._log_audit("user_created", "user", str(result.inserted_id), after=user.dict(by_alias=True))
        return str(result.inserted_id)
    
    async def get_user(self, user_id: str) -> Optional[UserModel]:
        """Get user by ID"""
        doc = await self.db.users.find_one({"userId": user_id})
        return UserModel(**doc) if doc else None
    
    async def update_user(self, user_id: str, updates: Dict[str, Any]) -> bool:
        """Update user"""
        camel_case_updates = convert_to_camel_case(updates)
        camel_case_updates["updatedAt"] = datetime.utcnow()
        result = await self.db.users.update_one(
            {"userId": user_id},
            {"$set": camel_case_updates}
        )
        await self._log_audit("user_updated", "user", user_id, after=camel_case_updates)
        return result.modified_count > 0
    
    # ========================================================================
    # CHAT SESSION OPERATIONS
    # ========================================================================
    
    async def create_session(self, session: ChatSessionModel) -> str:
        """Create new chat session"""
        doc = session.dict(by_alias=True)
        result = await self.db.chat_sessions.insert_one(doc)
        await self._log_audit("session_created", "session", session.session_id, after=doc)
        return session.session_id
    
    async def get_session(self, session_id: str) -> Optional[ChatSessionModel]:
        """Get chat session by ID"""
        doc = await self.db.chat_sessions.find_one({"sessionId": session_id})
        return ChatSessionModel(**doc) if doc else None
    
    async def list_sessions(self, user_id: str, limit: int = 50) -> List[ChatSessionModel]:
        """List user's chat sessions"""
        docs = await self.db.chat_sessions.find(
            {"userId": user_id}
        ).sort("createdAt", -1).limit(limit).to_list(limit)
        return [ChatSessionModel(**doc) for doc in docs]
    
    async def find_user_sessions(
        self, 
        user_id: str, 
        skip: int = 0, 
        limit: int = 10, 
        search_text: Optional[str] = None, 
        archived: Optional[bool] = None,
        include_last_message: bool = False
    ) -> List[ChatSessionModel]:
        """Find user sessions with filters and pagination, optionally include last message via aggregation"""
        if not include_last_message:
            # Simple query - just get sessions
            query = {"userId": user_id}
            
            if archived is not None:
                query["isArchived"] = archived
            
            if search_text:
                query["title"] = {"$regex": search_text, "$options": "i"}
            
            docs = await self.db.chat_sessions.find(query)\
                .sort("updatedAt", -1)\
                .skip(skip)\
                .limit(limit)\
                .to_list(limit)
            
            return [ChatSessionModel(**doc) for doc in docs]
        
        else:
            # Optimized aggregation to get sessions with last message in single query
            match_stage = {"userId": user_id}
            if archived is not None:
                match_stage["isArchived"] = archived
            if search_text:
                match_stage["title"] = {"$regex": search_text, "$options": "i"}
            
            pipeline = [
                {"$match": match_stage},
                {"$sort": {"updatedAt": -1}},
                {"$skip": skip},
                {"$limit": limit},
                # Lookup last message for each session
                {
                    "$lookup": {
                        "from": "chat_messages",
                        "let": {"sessionId": "$sessionId"},
                        "pipeline": [
                            {"$match": {"$expr": {"$eq": ["$sessionId", "$$sessionId"]}}},
                            {"$sort": {"createdAt": -1}},
                            {"$limit": 1},
                            {"$project": {"content": 1}}
                        ],
                        "as": "lastMessage"
                    }
                },
                # Add last message content to session
                {
                    "$addFields": {
                        "lastMessageContent": {
                            "$cond": {
                                "if": {"$gt": [{"$size": "$lastMessage"}, 0]},
                                "then": {"$substr": [{"$arrayElemAt": ["$lastMessage.content", 0]}, 0, 100]},
                                "else": null
                            }
                        }
                    }
                },
                {"$unset": "lastMessage"}  # Remove the temporary field
            ]
            
            docs = await self.db.chat_sessions.aggregate(pipeline).to_list(limit)
            return [ChatSessionModel(**doc) for doc in docs]
    
    async def update_session(self, session_id: str, updates: Dict[str, Any]) -> bool:
        """Update chat session"""
        camel_case_updates = convert_to_camel_case(updates)
        camel_case_updates["updatedAt"] = datetime.utcnow()
        result = await self.db.chat_sessions.update_one(
            {"sessionId": session_id},
            {"$set": camel_case_updates}
        )
        return result.modified_count > 0
    
    async def archive_session(self, session_id: str) -> bool:
        """Archive chat session"""
        return await self.update_session(session_id, {"is_archived": True})
    
    async def delete_session(self, session_id: str) -> bool:
        """Delete chat session"""
        result = await self.db.chat_sessions.delete_one({"sessionId": session_id})
        return result.deleted_count > 0
    
    async def insert_session(self, session_doc: Dict[str, Any]) -> str:
        """Insert a new session document"""
        result = await self.db.chat_sessions.insert_one(session_doc)
        return session_doc.get("sessionId")
    
    async def add_analysis_to_session(self, session_id: str, analysis_id: str) -> bool:
        """Add analysis ID to session's analysis_ids array"""
        result = await self.db.chat_sessions.update_one(
            {"sessionId": session_id},
            {"$push": {"analysis_ids": analysis_id}}
        )
        return result.modified_count > 0
    
    # ========================================================================
    # CHAT MESSAGE OPERATIONS
    # ========================================================================
    
    async def create_message(self, message: ChatMessageModel) -> str:
        """Create new chat message"""
        doc = message.dict(by_alias=True)
        result = await self.db.chat_messages.insert_one(doc)
        message_id = message.message_id
        
        # Update session message count and last message time
        await self.db.chat_sessions.update_one(
            {"sessionId": message.session_id},
            {
                "$inc": {"messageCount": 1},
                "$set": {"lastMessageAt": datetime.utcnow()},
            }
        )
        
        await self._log_audit("message_created", "message", message_id, after=doc)
        return message_id
    
    async def get_message(self, message_id: str) -> Optional[ChatMessageModel]:
        """Get message by ID"""
        doc = await self.db.chat_messages.find_one({"messageId": message_id})
        return ChatMessageModel(**doc) if doc else None
    
    async def get_session_messages(self, session_id: str, limit: int = 100) -> List[ChatMessageModel]:
        """Get all messages in session"""
        docs = await self.db.chat_messages.find(
            {"sessionId": session_id}
        ).sort("created_at", 1).limit(limit).to_list(limit)
        return [ChatMessageModel(**doc) for doc in docs]
    
    async def get_last_message(self, session_id: str) -> Optional[ChatMessageModel]:
        """Get last message in session"""
        doc = await self.db.chat_messages.find_one(
            {"sessionId": session_id},
            sort=[("created_at", -1)]
        )
        return ChatMessageModel(**doc) if doc else None
    
    async def count_session_messages(self, session_id: str) -> int:
        """Count messages in a session"""
        return await self.db.chat_messages.count_documents({"sessionId": session_id})
    
    async def update_message(self, message_id: str, updates: Dict[str, Any]) -> bool:
        """Update a chat message"""
        result = await self.db.chat_messages.update_one(
            {"messageId": message_id},
            {"$set": updates}
        )
        return result.modified_count > 0
    
    async def update_message_with_query(self, query: Dict[str, Any], update_operations: Dict[str, Any]) -> bool:
        """Update message with custom query and update operations"""
        result = await self.db.chat_messages.update_one(query, update_operations)
        return result.modified_count > 0
    
    async def find_message(self, query: Dict[str, Any], projection: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """Find a single message with optional projection"""
        return await self.db.chat_messages.find_one(query, projection)
    
    async def aggregate_messages(self, pipeline: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Execute aggregation pipeline on messages"""
        cursor = self.db.chat_messages.aggregate(pipeline)
        return await cursor.to_list(None)
    
    async def delete_session_messages(self, session_id: str) -> int:
        """Delete all messages in a session"""
        result = await self.db.chat_messages.delete_many({"sessionId": session_id})
        return result.deleted_count
    
    async def update_session_messages_count(self, session_id: str, count: int) -> bool:
        """Update message count for a session"""
        result = await self.db.chat_sessions.update_one(
            {"sessionId": session_id},
            {"$set": {"messageCount": count}}
        )
        return result.modified_count > 0
    
    # ========================================================================
    # ANALYSIS OPERATIONS
    # ========================================================================
    
    async def create_analysis(self, analysis: AnalysisModel) -> str:
        """Create new analysis"""
        doc = analysis.dict(by_alias=True)
        result = await self.db.analyses.insert_one(doc)
        await self._log_audit("analysis_created", "analysis", analysis.analysis_id, after=doc)
        return analysis.analysis_id
    
    async def get_analysis(self, analysis_id: str) -> Optional[AnalysisModel]:
        """Get analysis by ID"""
        doc = await self.db.analyses.find_one({"analysisId": analysis_id})
        return AnalysisModel(**doc) if doc else None
    
    async def list_analyses(self, user_id: str, category: Optional[str] = None, limit: int = 100) -> List[AnalysisModel]:
        """List user's analyses"""
        query = {"userId": user_id}
        if category:
            query["category"] = category
        
        docs = await self.db.analyses.find(query).sort("createdAt", -1).limit(limit).to_list(limit)
        return [AnalysisModel(**doc) for doc in docs]
    
    async def search_analyses(self, user_id: str, search_text: str, limit: int = 50) -> List[AnalysisModel]:
        """Search analyses by title/description"""
        docs = await self.db.analyses.find(
            {
                "userId": user_id,
                "$text": {"$search": search_text}
            }
        ).limit(limit).to_list(limit)
        return [AnalysisModel(**doc) for doc in docs]
    
    async def update_analysis(self, analysis_id: str, updates: Dict[str, Any]) -> bool:
        """Update analysis"""
        updates["updatedAt"] = datetime.utcnow()
        result = await self.db.analyses.update_one(
            {"analysisId": analysis_id},
            {"$set": updates}
        )
        return result.modified_count > 0
    
    async def mark_analysis_used(self, analysis_id: str) -> bool:
        """Update last_used_at timestamp"""
        return await self.update_analysis(analysis_id, {"lastUsedAt": datetime.utcnow()})
    
    async def find_analyses(self, query: Dict[str, Any]) -> List[AnalysisModel]:
        """Find analyses with query"""
        docs = await self.db.analyses.find(query).to_list(None)
        return [AnalysisModel(**doc) for doc in docs]
    
    # ========================================================================
    # EXECUTION OPERATIONS
    # ========================================================================
    
    async def create_execution(self, execution: ExecutionModel) -> str:
        """Create execution record"""
        doc = execution.dict(by_alias=True)
        result = await self.db.executions.insert_one(doc)
        await self._log_audit("execution_created", "execution", execution.execution_id, after=doc)
        return execution.execution_id
    
    async def get_execution(self, execution_id: str) -> Optional[ExecutionModel]:
        """Get execution by ID"""
        doc = await self.db.executions.find_one({"executionId": execution_id})
        return ExecutionModel(**doc) if doc else None
    
    async def list_executions(self, session_id: str, limit: int = 100) -> List[ExecutionModel]:
        """List executions in session"""
        docs = await self.db.executions.find(
            {"sessionId": session_id}
        ).sort("startedAt", -1).limit(limit).to_list(limit)
        return [ExecutionModel(**doc) for doc in docs]
    
    async def list_user_executions(self, user_id: str, limit: int = 100) -> List[ExecutionModel]:
        """List executions for user"""
        docs = await self.db.executions.find(
            {"userId": user_id}
        ).sort("startedAt", -1).limit(limit).to_list(limit)
        return [ExecutionModel(**doc) for doc in docs]
    
    async def update_execution(self, execution_id: str, updates: Dict[str, Any]) -> bool:
        """Update execution"""
        camel_case_updates = convert_to_camel_case(updates)
        result = await self.db.executions.update_one(
            {"executionId": execution_id},
            {"$set": camel_case_updates}
        )
        return result.modified_count > 0
    
    # ========================================================================
    # SAVED ANALYSIS OPERATIONS (Reusable Templates)
    # ========================================================================
    
    async def save_analysis(self, saved: SavedAnalysisModel) -> str:
        """Save analysis as reusable template"""
        result = await self.db.saved_analyses.insert_one(saved.dict(by_alias=True))
        saved_id = str(result.inserted_id)
        await self._log_audit("analysis_saved", "saved_analysis", saved_id, after=saved.dict(by_alias=True))
        return saved_id
    
    async def get_saved_analysis(self, saved_id: str) -> Optional[SavedAnalysisModel]:
        """Get saved analysis"""
        doc = await self.db.saved_analyses.find_one({"savedAnalysisId": saved_id})
        return SavedAnalysisModel(**doc) if doc else None
    
    async def list_saved_analyses(self, user_id: str, limit: int = 100) -> List[SavedAnalysisModel]:
        """List user's saved analyses"""
        docs = await self.db.saved_analyses.find(
            {"userId": user_id}
        ).sort("createdAt", -1).limit(limit).to_list(limit)
        return [SavedAnalysisModel(**doc) for doc in docs]
    
    async def increment_saved_analysis_usage(self, saved_id: str) -> bool:
        """Increment usage counter"""
        result = await self.db.saved_analyses.update_one(
            {"savedAnalysisId": saved_id},
            {
                "$inc": {"usageCount": 1},
                "$set": {"lastUsedAt": datetime.utcnow()},
            }
        )
        return result.modified_count > 0
    
    # ========================================================================
    # CACHE OPERATIONS
    # ========================================================================
    
    async def get_cached_result(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get cached result if exists and not expired"""
        doc = await self.db.cache.find_one(
            {
                "cacheKey": cache_key,
                "expiresAt": {"$gt": datetime.utcnow()}
            }
        )
        
        if doc:
            # Increment hit count and update last used
            await self.db.cache.update_one(
                {"cacheId": doc["cacheId"]},
                {
                    "$inc": {"hitCount": 1},
                    "$set": {"lastUsedAt": datetime.utcnow()}
                }
            )
            return doc["result"]
        
        return None
    
    async def cache_result(self, cache_key: str, result: Dict[str, Any], 
                          analysis_id: Optional[str] = None, ttl_hours: int = 24) -> str:
        """Cache query result"""
        cache = CacheModel(
            cache_key=cache_key,
            result=result,
            analysis_id=analysis_id,
            expires_at=datetime.utcnow() + timedelta(hours=ttl_hours),
        )
        
        result = await self.db.cache.insert_one(cache.dict(by_alias=True))
        return cache.cache_id  # Return the cache_id in snake_case for Python code
    
    async def delete_analysis_cache(self, analysis_id: str) -> int:
        """Delete cache entries for an analysis"""
        result = await self.db.cache.delete_many({"analysisId": analysis_id})
        return result.deleted_count
    
    # ========================================================================
    # AUDIT LOGGING
    # ========================================================================
    
    async def _log_audit(self, action: str, resource_type: str, resource_id: str,
                        before: Optional[Dict] = None, after: Optional[Dict] = None,
                        user_id: Optional[str] = None, success: bool = True,
                        error_message: Optional[str] = None) -> None:
        """Log audit event"""
        audit = AuditLogModel(
            user_id=user_id or "system",
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            before=before,
            after=after,
            success=success,
            error_message=error_message,
        )
        
        await self.db.audit_logs.insert_one(audit.dict(by_alias=True))
    
    async def get_audit_logs(self, user_id: str, limit: int = 100) -> List[AuditLogModel]:
        """Get user's audit logs"""
        docs = await self.db.audit_logs.find(
            {"userId": user_id}
        ).sort("created_at", -1).limit(limit).to_list(limit)
        return [AuditLogModel(**doc) for doc in docs]
    
    # ========================================================================
    # HEALTH CHECK
    # ========================================================================
    
    async def health_check(self) -> bool:
        """Check MongoDB connection"""
        try:
            await self.client.admin.command('ping')
            return True
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False
