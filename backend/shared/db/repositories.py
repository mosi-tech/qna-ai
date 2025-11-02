"""
Repository Layer - High-level data access patterns
Combines multiple database operations for common workflows
"""

import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
import hashlib
from bson import ObjectId

from .mongodb_client import MongoDBClient
from .schemas import (
    ChatMessageModel,
    ChatSessionModel,
    AnalysisModel,
    ExecutionModel,
    RoleType,
    QueryType,
)

logger = logging.getLogger("repositories")


class ChatRepository:
    """Repository for chat operations"""
    
    def __init__(self, db: MongoDBClient):
        self.db = db
        
        
    async def start_session(self, user_id: str, title: Optional[str] = None) -> str:
        """Create new chat session"""
        session = ChatSessionModel(
            user_id=user_id,
            title=title or "New Conversation",
        )
        return await self.db.create_session(session)
    
    async def add_user_message(self, session_id: str, user_id: str, 
                               question: str, query_type: QueryType = QueryType.COMPLETE) -> str:
        """Add user message to conversation"""
        # Get message count to set message_index
        message_count = await self.db.db.chat_messages.count_documents({"sessionId": session_id})
        
        message = ChatMessageModel(
            session_id=session_id,
            user_id=user_id,
            role=RoleType.USER,
            content=question,
            metadata={
                "response_type": "user_message",
                "original_question": question,
                "query_type": query_type.value if query_type else None,
            },
            message_index=message_count,
        )
        return await self.db.create_message(message)
    
    async def add_assistant_message_with_analysis(
        self,
        session_id: str,
        user_id: str,
        script: str,
        explanation: str,
        analysis: AnalysisModel,
        mcp_calls: List[str],
        execution_id: Optional[str] = None,
    ) -> str:
        """Add assistant message with generated analysis (KEY WORKFLOW)"""
        
        # First save the analysis
        analysis_id = await self.db.create_analysis(analysis)
        
        # Get message count to set message_index
        message_count = await self.db.db.chat_messages.count_documents({"sessionId": session_id})
        
        # Then create message with reference to analysis (no embedding)
        # Note: Execution details accessible via analysisId → Analysis.executionId
        message = ChatMessageModel(
            session_id=session_id,
            user_id=user_id,
            role=RoleType.ASSISTANT,
            content=explanation,
            analysis_id=analysis_id,
            message_index=message_count,
        )
        
        message_id = await self.db.create_message(message)
        
        # Update session with analysis reference
        await self.db.db.chat_sessions.update_one(
            {"sessionId": session_id},
            {"$push": {"analysis_ids": analysis_id}}
        )
        
        return message_id
    
    async def add_assistant_message(
        self,
        session_id: str,
        user_id: str,
        content: str,
        analysis_id: str = None,
        execution_id: str = None,
        metadata: Dict[str, Any] = None,
    ) -> str:
        """Add regular assistant message (with optional analysis, execution references, and metadata)"""
        # Get message count to set message_index
        message_count = await self.db.db.chat_messages.count_documents({"sessionId": session_id})
        
        message = ChatMessageModel(
            session_id=session_id,
            user_id=user_id,
            role=RoleType.ASSISTANT,
            content=content,
            analysis_id=analysis_id,
            execution_id=execution_id,
            message_index=message_count,
            metadata=metadata or {},
        )
        return await self.db.create_message(message)
    
    async def update_assistant_message(
        self,
        message_id: str,
        content: str,
        analysis_id: str = None,
        execution_id: str = None,
        metadata: Dict[str, Any] = None,
    ) -> bool:
        """Update existing assistant message with new content and metadata"""
        update_data = {
            "content": content,
            "updatedAt": datetime.utcnow()
        }
        
        if analysis_id is not None:
            update_data["analysisId"] = analysis_id
        if execution_id is not None:
            update_data["executionId"] = execution_id
        if metadata is not None:
            update_data["metadata"] = metadata
            
        # If ObjectId conversion fails, treat as string
        query = {"messageId": message_id}
            
        result = await self.db.db.chat_messages.update_one(
            query,
            {"$set": update_data}
        )
        
        return result.modified_count > 0
    
    async def get_conversation_history(self, session_id: str) -> List[Dict[str, Any]]:
        """Get conversation for LLM context"""
        messages = await self.db.get_session_messages(session_id)
        
        history = []
        for msg in messages:
            history.append({
                "role": msg.role.value,
                "content": msg.content,
                "timestamp": msg.created_at.isoformat(),
            })
        
        return history
    
    async def get_session_with_context(self, session_id: str) -> Dict[str, Any]:
        """Get session with full context"""
        session = await self.db.get_session(session_id)
        if not session:
            return None
        
        messages = await self.db.get_session_messages(session_id, limit=5)
        analyses = []
        
        for msg in messages:
            if msg.analysis_id:
                analysis = await self.db.get_analysis(msg.analysis_id)
                if analysis:
                    analyses.append({
                        "id": analysis.analysis_id,
                        "question": analysis.question,
                        "timestamp": msg.created_at.isoformat(),
                    })
        
        return {
            "session": session.dict(by_alias=True),
            "recent_messages": [m.dict(by_alias=True) for m in messages[-5:]],
            "recent_analyses": analyses[-3:],
            "message_count": session.message_count,
        }
    
    async def get_user_sessions(
        self,
        user_id: str,
        skip: int = 0,
        limit: int = 10,
        search_text: Optional[str] = None,
        archived: Optional[bool] = None,
    ) -> List[Dict[str, Any]]:
        """Get user sessions with metadata for list view"""
        query = {"userId": user_id}
        
        if archived is not None:
            query["is_archived"] = archived
        
        if search_text:
            query["title"] = {"$regex": search_text, "$options": "i"}
        
        sessions = await self.db.db.chat_sessions.find(query)\
            .sort("updated_at", -1)\
            .skip(skip)\
            .limit(limit)\
            .to_list(limit)
        
        result = []
        for session in sessions:
            # Get last message
            last_msg = await self.db.db.chat_messages.find_one(
                {"sessionId": session.get("sessionId")},
                sort=[("created_at", -1)]
            )
            
            result.append({
                "session_id": session.get("sessionId"),
                "title": session.get("title"),
                "created_at": session.get("created_at", datetime.now()).isoformat(),
                "updated_at": session.get("updated_at", datetime.now()).isoformat(),
                "message_count": await self.db.db.chat_messages.count_documents(
                    {"sessionId": session.get("sessionId")}
                ),
                "last_message": last_msg.get("content", "")[:100] if last_msg else None,
                "is_archived": session.get("is_archived", False),
            })
        
        return result
    
    async def get_session_with_messages(self, session_id: str, limit: int = 5, offset: int = 0) -> Optional[Dict[str, Any]]:
        """Get session with paginated messages for resume"""
        # Get session document
        session = await self.db.db.chat_sessions.find_one({"sessionId": session_id})
        
        # If session doesn't exist but messages do, create it
        if not session:
            # Check if messages exist for this session
            message_count = await self.db.db.chat_messages.count_documents({"sessionId": session_id})
            if message_count == 0:
                return None
            
            # Create implicit session document
            session_doc = {
                "sessionId": session_id,
                "userId": "anonymous",
                "title": f"Conversation {session_id[:8]}",
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
                "is_archived": False,
                "message_count": message_count,
            }
            await self.db.db.chat_sessions.insert_one(session_doc)
            session = session_doc
        
        # Get total message count
        total_messages = await self.db.db.chat_messages.count_documents({"sessionId": session_id})
        
        # Get messages (newest first, then reverse for correct order)
        messages = await self.db.db.chat_messages.find({"sessionId": session_id})\
            .sort("created_at", -1)\
            .skip(offset)\
            .limit(limit)\
            .to_list(limit)
        
        # Reverse to get chronological order
        messages.reverse()
        
        return {
            "session_id": session.get("sessionId"),
            "user_id": session.get("userId"),
            "title": session.get("title"),
            "created_at": session.get("created_at", datetime.now()).isoformat() if hasattr(session.get("created_at"), 'isoformat') else str(session.get("created_at")),
            "updated_at": session.get("updated_at", datetime.now()).isoformat() if hasattr(session.get("updated_at"), 'isoformat') else str(session.get("updated_at")),
            "is_archived": session.get("is_archived", False),
            "total_messages": total_messages,
            "offset": offset,
            "limit": limit,
            "has_older": (offset + limit) < total_messages,
            "messages": [
                {
                    "id": msg.get("messageId"),
                    "role": msg.get("role"),
                    "content": msg.get("content"),
                    "timestamp": msg.get("created_at", "").isoformat() if hasattr(msg.get("created_at"), 'isoformat') else str(msg.get("created_at")),
                    "analysisId": msg.get("analysisId"),
                    "executionId": msg.get("executionId"),
                    "metadata": msg.get("metadata", {}),  # Return raw metadata instead of transformed uiData
                }
                for msg in messages
            ]
        }
    
    
    
    async def update_session(self, session_id: str, update_data: Dict[str, Any]) -> bool:
        """Update session metadata"""
        return await self.db.update_session(session_id, update_data)
    
    async def delete_session(self, session_id: str) -> bool:
        """Delete session and all its messages"""
        # Delete messages
        await self.db.db.chat_messages.delete_many({"sessionId": session_id})
        # Delete session
        result = await self.db.db.chat_sessions.delete_one({"sessionId": session_id})
        return result.deleted_count > 0


class AnalysisRepository:
    """Repository for analysis operations"""
    
    def __init__(self, db: MongoDBClient):  
        self.db = db
    
    async def create_and_save_analysis(
        self,
        user_id: str,
        question: str,
        llm_response: Dict,
        script: str,
    ) -> str:
        """Create analysis template (reusable script)\n
        Analysis is a template that can be executed multiple times.
        Execution results are tracked separately in ExecutionModel.
        """

        analysis = AnalysisModel(
            user_id=user_id,
            question=question,  
            llm_response=llm_response,
            script_url=script,
        )
        
        return await self.db.create_analysis(analysis)
    
    async def get_similar_analyses(self, user_id: str, category: str, limit: int = 10) -> List[AnalysisModel]:
        """Get similar analyses in same category"""
        return await self.db.list_analyses(user_id, category=category, limit=limit)
    
    async def get_reusable_analyses(self, user_id: str) -> List[AnalysisModel]:
        """Get all analyses that can be reused as templates"""
        docs = await self.db.db.analyses.find({
            "userId": user_id
        }).sort("last_used_at", -1).to_list(100)
        
        return [AnalysisModel(**doc) for doc in docs]
    
    async def can_reuse_analysis(self, analysis_id: str, new_question: str) -> bool:
        """Check if analysis can be reused for new question"""
        analysis = await self.db.get_analysis(analysis_id)
        if not analysis:
            return False
        
        # Analysis is a reusable template, so we can always attempt reuse
        # Execution state is tracked separately in ExecutionModel
        await self.db.mark_analysis_used(analysis_id)
        return True


class ExecutionRepository:
    """Repository for execution tracking"""
    
    def __init__(self, db: MongoDBClient):
        self.db = db
    
    async def log_execution(
        self,
        user_id: str,
        analysis_id: str,
        question: str,
        generated_script: str,
        parameters: Dict[str, Any],
        mcp_calls: List[str] = None,
        session_id: Optional[str] = None,
        created_message_id: Optional[str] = None,
    ) -> str:
        """Log script execution (Execution is independent record linked to Analysis)
        
        Args:
            user_id: User performing execution
            analysis_id: Which analysis is being executed
            question: Original question
            generated_script: Full script content
            parameters: Execution parameters from LLM config
            mcp_calls: List of MCP tool calls from execution config
            session_id: Optional chat session context
            created_message_id: Will be set later after message creation
        """
        
        from .schemas import ExecutionStatus
        
        execution = ExecutionModel(
            user_id=user_id,
            analysis_id=analysis_id,
            session_id=session_id,
            created_message_id=created_message_id,
            question=question,
            generated_script=generated_script,
            parameters=parameters,
            status=ExecutionStatus.PENDING,
            mcp_calls=mcp_calls or [],
        )
        
        return await self.db.create_execution(execution)
    
    async def link_execution_to_message(
        self,
        execution_id: str,
        message_id: str,
    ) -> bool:
        """Link execution to the chat message that was created from it"""
        return await self.db.update_execution(
            execution_id,
            {"created_message_id": message_id}
        )
    
    async def complete_execution(
        self,
        execution_id: str,
        result: Dict[str, Any],
        execution_time_ms: int,
        success: bool = True,
        error: Optional[str] = None,
    ) -> bool:
        """Mark execution as complete"""
        
        from .schemas import ExecutionStatus
        
        status = ExecutionStatus.SUCCESS if success else ExecutionStatus.FAILED
        
        return await self.db.update_execution(
            execution_id,
            {
                "status": status,
                "completed_at": datetime.utcnow(),
                "execution_time_ms": execution_time_ms,
                "result": result,
                "error": error,
            }
        )
    
    async def get_execution_history(self, session_id: str) -> List[ExecutionModel]:
        """Get execution history for session"""
        return await self.db.list_executions(session_id)


class CacheRepository:
    """Repository for caching operations"""
    
    def __init__(self, db: MongoDBClient):
        self.db = db
    
    def _generate_cache_key(self, question: str, parameters: Dict[str, Any]) -> str:
        """Generate cache key from question and parameters"""
        cache_data = f"{question}:{str(sorted(parameters.items()))}"
        return hashlib.sha256(cache_data.encode()).hexdigest()
    
    async def get_cached_analysis(
        self,
        question: str,
        parameters: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        """Get cached analysis result"""
        cache_key = self._generate_cache_key(question, parameters)
        return await self.db.get_cached_result(cache_key)
    
    async def cache_analysis(
        self,
        question: str,
        parameters: Dict[str, Any],
        result: Dict[str, Any],
        analysis_id: Optional[str] = None,
        ttl_hours: int = 24,
    ) -> str:
        """Cache analysis result"""
        cache_key = self._generate_cache_key(question, parameters)
        return await self.db.cache_result(cache_key, result, analysis_id, ttl_hours)
    
    async def invalidate_analysis_cache(self, analysis_id: str) -> None:
        """Invalidate cache for specific analysis"""
        await self.db.db.cache.delete_many({"analysisId": analysis_id})


class RepositoryManager:
    """Unified repository access point"""
    
    def __init__(self, db: MongoDBClient):
        self.db = db
        self.chat = ChatRepository(db)
        self.analysis = AnalysisRepository(db)
        self.execution = ExecutionRepository(db)
        self.cache = CacheRepository(db)
    
    async def initialize(self) -> None:
        """Initialize all repositories"""
        await self.db.connect()
        logger.info("✅ Repository manager initialized")
    
    async def shutdown(self) -> None:
        """Shutdown all repositories"""
        await self.db.disconnect()
        logger.info("✅ Repository manager shutdown")
