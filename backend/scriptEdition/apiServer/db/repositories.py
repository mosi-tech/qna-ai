"""
Repository Layer - High-level data access patterns
Combines multiple database operations for common workflows
"""

import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
import hashlib

from .mongodb_client import MongoDBClient
from .schemas import (
    ChatMessageModel,
    ChatSessionModel,
    AnalysisModel,
    ExecutionModel,
    SavedAnalysisModel,
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
            userId=user_id,
            title=title or "New Conversation",
        )
        return await self.db.create_session(session)
    
    async def add_user_message(self, session_id: str, user_id: str, 
                               question: str, query_type: QueryType = QueryType.COMPLETE) -> str:
        """Add user message to conversation"""
        from db.schemas import QuestionContext
        
        # Get message count to set message_index
        message_count = await self.db.db.chat_messages.count_documents({"sessionId": session_id})
        
        question_context = QuestionContext(
            original_question=question,
            query_type=query_type,
        )
        
        message = ChatMessageModel(
            sessionId=session_id,
            userId=user_id,
            role=RoleType.USER,
            content=question,
            questionContext=question_context,
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
            sessionId=session_id,
            userId=user_id,
            role=RoleType.ASSISTANT,
            content=explanation,
            analysisId=analysis_id,  # Reference to AnalysisModel in analyses collection
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
        script: Optional[str] = None,
        mcp_calls: Optional[List[str]] = None,
    ) -> str:
        """Add regular assistant message (without analysis)"""
        # Get message count to set message_index
        message_count = await self.db.db.chat_messages.count_documents({"sessionId": session_id})
        
        message = ChatMessageModel(
            sessionId=session_id,
            userId=user_id,
            role=RoleType.ASSISTANT,
            content=content,
            message_index=message_count,
        )
        return await self.db.create_message(message)
    
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
            if msg.analysisId:
                analysis = await self.db.get_analysis(msg.analysisId)
                if analysis:
                    analyses.append({
                        "id": analysis.analysisId,
                        "question": analysis.question,
                        "timestamp": msg.created_at.isoformat(),
                    })
        
        return {
            "session": session.dict(),
            "recent_messages": [m.dict() for m in messages[-5:]],
            "recent_analyses": analyses[-3:],
            "message_count": session.message_count,
        }


class AnalysisRepository:
    """Repository for analysis operations"""
    
    def __init__(self, db: MongoDBClient):
        self.db = db
    
    async def create_and_save_analysis(
        self,
        user_id: str,
        title: str,
        description: str,
        result: Dict[str, Any],
        parameters: Dict[str, Any],
        mcp_calls: List[str],
        category: str,
        script: Optional[str] = None,
        execution_time_ms: int = 0,
        data_sources: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
    ) -> str:
        """Create analysis and save it as reusable"""
        
        # Build llm_response from provided parameters
        llm_response = {
            "status": "success",
            "script_name": script or "analysis.py",
            "analysis_description": description,
            "execution": {
                "script_name": script or "analysis.py",
                "parameters": parameters
            }
        }
        
        analysis = AnalysisModel(
            userId=user_id,
            question=title,  # Use title as question for compatibility
            llm_response=llm_response,
            script_url=script or f"/tmp/{script or 'analysis.py'}",
            script_size_bytes=0,
            result=result,
            execution_time_ms=execution_time_ms,
            tags=tags or [],
            metadata={
                "category": category,
                "data_sources": data_sources or [],
                "mcp_calls": mcp_calls,
            }
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
        
        # Check if analysis has been executed (has results)
        if analysis.status != "success" or not analysis.result:
            return False
        
        # For now, simple check: can reuse if already executed
        await self.db.mark_analysis_used(analysis_id)
        return True


class ExecutionRepository:
    """Repository for execution tracking"""
    
    def __init__(self, db: MongoDBClient):
        self.db = db
    
    async def log_execution(
        self,
        user_id: str,
        session_id: str,
        message_id: str,
        question: str,
        script: str,
        parameters: Dict[str, Any],
        mcp_calls: List[str],
    ) -> str:
        """Log script execution"""
        
        from .schemas import ExecutionStatus
        
        execution = ExecutionModel(
            userId=user_id,
            sessionId=session_id,
            messageId=message_id,
            question=question,
            generated_script=script,
            parameters=parameters,
            status=ExecutionStatus.RUNNING,
            mcp_calls=mcp_calls,
        )
        
        return await self.db.create_execution(execution)
    
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
