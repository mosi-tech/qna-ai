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


class SessionRepository:
    """Repository for session operations on chat_sessions collection"""
    
    def __init__(self, db: MongoDBClient):
        self.db = db
    
    async def get_session_metadata(self, session_id: str) -> Optional[ChatSessionModel]:
        """Get session metadata (uses encapsulated MongoDB client method)"""
        return await self.db.get_session(session_id)
    
    async def create_session(self, session: ChatSessionModel) -> str:
        """Create new chat session"""
        return await self.db.create_session(session)
    
    async def update_session(self, session_id: str, updates: Dict[str, Any]) -> bool:
        """Update session metadata"""
        return await self.db.update_session(session_id, updates)
    
    async def delete_session(self, session_id: str) -> bool:
        """Delete a session"""
        return await self.db.delete_session(session_id)
    
    async def find_user_sessions(
        self,
        user_id: str,
        skip: int = 0,
        limit: int = 10,
        search_text: Optional[str] = None,
        archived: Optional[bool] = None,
    ) -> List[ChatSessionModel]:
        """Find user sessions with filters (uses encapsulated MongoDB client)"""
        return await self.db.find_user_sessions(user_id, skip, limit, search_text, archived)


class ChatRepository:
    """Repository for chat operations"""
    
    def __init__(self, db: MongoDBClient):
        self.db = db
        
        
    async def start_session(self, user_id: str, title: Optional[str] = None) -> str:
        """Create new chat session - delegates to SessionRepository"""
        session = ChatSessionModel(
            user_id=user_id,
            title=title or "New Conversation",
        )
        # Use SessionRepository for session operations
        session_repo = SessionRepository(self.db)
        return await session_repo.create_session(session)
    
    async def add_user_message(self, session_id: str, user_id: str, 
                               question: str, message_id: Optional[str] = None, query_type: QueryType = QueryType.COMPLETE) -> str:
        """Add user message to conversation"""
        # ✅ FIXED: Get message count using encapsulated method
        message_count = await self.db.count_session_messages(session_id)
        
        # Build message data, only include message_id if provided
        message_data = {
            "session_id": session_id,
            "user_id": user_id,
            "role": RoleType.USER,
            "content": question,
            "metadata": {
                "response_type": "user_message",
                "original_question": question,
                "query_type": query_type.value if query_type else None,
            },
            "message_index": message_count,
        }
        
        # Only include message_id if explicitly provided
        if message_id is not None:
            message_data["message_id"] = message_id
            
        message = ChatMessageModel(**message_data)
        return await self.db.create_message(message)
    
    async def get_raw_message_by_id(self, message_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific message by its ID without transformations (includes userId)"""
        try:
            # Use encapsulated MongoDB client method
            message = await self.db.find_message({"messageId": message_id})
            if message:
                # Convert ObjectId to string for JSON serialization if present
                if '_id' in message:
                    del message['_id']
                return message
            return None
        except Exception as e:
            logger.error(f"✗ Failed to get raw message {message_id}: {e}")
            return None

    async def get_message_by_id(self, message_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific message by its ID with execution and analysis data populated"""
        try:
            # Use same aggregation pipeline as get_session_with_messages to populate execution and analysis
            pipeline = [
                # Match specific message
                {"$match": {"messageId": message_id}},
                
                # Left join with executions collection
                {
                    "$lookup": {
                        "from": "executions",
                        "localField": "executionId", 
                        "foreignField": "executionId",
                        "as": "execution_data"
                    }
                },
                
                # Left join with analyses collection  
                {
                    "$lookup": {
                        "from": "analyses",
                        "localField": "analysisId",
                        "foreignField": "analysisId", 
                        "as": "analysis_data"
                    }
                },
                
                # Project final structure with joined data
                {
                    "$project": {
                        "messageId": 1,
                        "sessionId": 1,  # Keep sessionId for session verification
                        "role": 1,
                        "content": 1,
                        "createdAt": 1,
                        "analysisId": 1,
                        "executionId": 1,
                        "metadata": 1,
                        "logs": 1,  # Include logs field for progress history
                        # Include execution data as nested object
                        "execution": {
                            "$cond": {
                                "if": {"$gt": [{"$size": "$execution_data"}, 0]},
                                "then": {
                                    "executionId": "$executionId",
                                    "status": {"$arrayElemAt": ["$execution_data.status", 0]},
                                    "results": {
                                        "$cond": {
                                            "if": {"$eq": [{"$arrayElemAt": ["$execution_data.status", 0]}, "success"]},
                                            "then": {"$arrayElemAt": ["$execution_data.result", 0]},
                                            "else": None
                                        }
                                    }
                                },
                                "else": {
                                    "executionId": "$executionId",
                                    "status": None,
                                    "results": None
                                }
                            }
                        },
                        # Include analysis data if available  
                        "analysis": {
                            "$cond": {
                                "if": {"$gt": [{"$size": "$analysis_data"}, 0]},
                                "then": {
                                    "llm_response": {"$arrayElemAt": ["$analysis_data.llm_response", 0]},
                                    "question": {"$arrayElemAt": ["$analysis_data.question", 0]}
                                },
                                "else": None
                            }
                        }
                    }
                }
            ]
            
            # ✅ FIXED: Execute aggregation using encapsulated method
            messages = await self.db.aggregate_messages(pipeline)
            
            return messages[0] if messages else None
            
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"Failed to get message {message_id}: {e}")
            raise
    
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
        
        # ✅ FIXED: Get message count using encapsulated method
        message_count = await self.db.count_session_messages(session_id)
        
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
        
        # ✅ FIXED: Update session with analysis reference using encapsulated method
        await self.db.add_analysis_to_session(session_id, analysis_id)
        
        return message_id
    
    async def add_assistant_message(
        self,
        session_id: str,
        user_id: str,
        content: str,
        message_id: str = None,
        analysis_id: str = None,
        execution_id: str = None,
        metadata: Dict[str, Any] = None,
    ) -> str:
        """Add regular assistant message (with optional analysis, execution references, and metadata)"""
        # ✅ FIXED: Get message count using encapsulated method
        message_count = await self.db.count_session_messages(session_id)
        
        # Build message data, only include message_id if provided
        message_data = {
            "session_id": session_id,
            "user_id": user_id,
            "role": RoleType.ASSISTANT,
            "content": content,
            "analysis_id": analysis_id,
            "execution_id": execution_id,
            "message_index": message_count,
            "metadata": metadata or {},
        }
        
        # Only include message_id if explicitly provided
        if message_id is not None:
            message_data["message_id"] = message_id
            
        message = ChatMessageModel(**message_data)
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
            
        # If ObjectId conversion fails, treat as string
        query = {"messageId": message_id}
        
        # Build update operations
        update_operations = {"$set": update_data}
        
        # If metadata is provided, merge it with existing metadata instead of replacing
        if metadata is not None:
            # Use MongoDB $mergeObjects to merge metadata fields
            # First check if message exists and get current metadata
            # ✅ FIXED: Find message using encapsulated method
            existing_message = await self.db.find_message(query, {"metadata": 1})
            
            if existing_message:
                existing_metadata = existing_message.get("metadata", {})
                # Merge existing metadata with new metadata (new metadata takes precedence)
                merged_metadata = {**existing_metadata, **metadata}
                update_data["metadata"] = merged_metadata
            else:
                # Message doesn't exist or no existing metadata, just use new metadata
                update_data["metadata"] = metadata
            
        # ✅ FIXED: Update message using encapsulated method
        success = await self.db.update_message_with_query(query, update_operations)
        
        return success
    
    async def get_conversation_history(self, session_id: str, include_metadata: bool = False, sort_order: int = 1) -> List[Dict[str, Any]]:
        """Get conversation for LLM context
        
        Args:
            session_id: Session ID to get messages for
            include_metadata: If True, includes full message metadata (needed for ConversationStore reconstruction)
            sort_order: 1 for ascending (oldest first), -1 for descending (newest first)
        """
        messages = await self.db.get_session_messages(session_id, sort_order=sort_order)
        
        history = []
        for msg in messages:
            message_data = {
                "user_id": msg.user_id, 
                "message_id": msg.message_id, 
                "role": msg.role.value,
                "content": msg.content,
                "timestamp": msg.created_at.isoformat(),
            }
            
            # Include metadata if requested (needed for ConversationStore reconstruction)
            if include_metadata and msg.metadata:
                message_data["metadata"] = msg.metadata
            
            history.append(message_data)
        
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
        """Get user sessions with metadata for list view - FIXED: Uses proper encapsulation"""
        # ✅ FIXED: Use SessionRepository for session operations  
        session_repo = SessionRepository(self.db)
        sessions = await session_repo.find_user_sessions(user_id, skip, limit, search_text, archived)
        
        result = []
        for session in sessions:
            # ✅ FIXED: Get last message using encapsulated method
            last_msg = await self.db.get_last_message(session.session_id)
            
            # ✅ FIXED: Count messages using encapsulated method
            message_count = await self.db.count_session_messages(session.session_id)
            
            result.append({
                "session_id": session.session_id,
                "title": session.title,
                "created_at": session.created_at.isoformat() if session.created_at else datetime.now().isoformat(),
                "updated_at": session.updated_at.isoformat() if session.updated_at else datetime.now().isoformat(),
                "message_count": message_count,
                "last_message": last_msg.content[:100] if last_msg else None,
                "is_archived": getattr(session, 'is_archived', False),
            })
        
        return result
    
    async def get_session_with_messages(self, session_id: str, limit: int = 5, offset: int = 0) -> Optional[Dict[str, Any]]:
        """Get session with paginated messages for resume using efficient aggregation"""
        # Get session document
        # ✅ FIXED: Get session using encapsulated method
        session_model = await self.db.get_session(session_id)
        session = session_model.dict(by_alias=True) if session_model else None
        
        # If session doesn't exist but messages do, create it
        if not session:
            # ✅ FIXED: Check if messages exist using encapsulated method
            message_count = await self.db.count_session_messages(session_id)
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
            # ✅ FIXED: Insert session using encapsulated method
            await self.db.insert_session(session_doc)
            session = session_doc
        
        # ✅ FIXED: Get total message count using encapsulated method
        total_messages = await self.db.count_session_messages(session_id)
        
        # Use aggregation pipeline to join messages with execution and analysis data in single query
        pipeline = [
            # Match messages for this session
            {"$match": {"sessionId": session_id}},
            
            # Sort newest first for pagination  
            {"$sort": {"createdAt": -1}},
            
            # Apply pagination
            {"$skip": offset},
            {"$limit": limit},
            
            # Left join with executions collection
            {
                "$lookup": {
                    "from": "executions",
                    "localField": "executionId", 
                    "foreignField": "executionId",
                    "as": "execution_data"
                }
            },
            
            # Left join with analyses collection  
            {
                "$lookup": {
                    "from": "analyses",
                    "localField": "analysisId",
                    "foreignField": "analysisId", 
                    "as": "analysis_data"
                }
            },
            
            # Project final structure with joined data
            {
                "$project": {
                    "messageId": 1,
                    "role": 1,
                    "content": 1,
                    "createdAt": 1,
                    "analysisId": 1,
                    "executionId": 1,
                    "metadata": 1,
                    "logs": 1,  # Include logs field for progress history
                    # Include execution data as nested object
                    "execution": {
                        "$cond": {
                            "if": {"$gt": [{"$size": "$execution_data"}, 0]},
                            "then": {
                                "executionId": "$executionId",
                                "status": {"$arrayElemAt": ["$execution_data.status", 0]},
                                "results": {
                                    "$cond": {
                                        "if": {"$eq": [{"$arrayElemAt": ["$execution_data.status", 0]}, "success"]},
                                        "then": {"$arrayElemAt": ["$execution_data.result", 0]},
                                        "else": None
                                    }
                                }
                            },
                            "else": {
                                "executionId": "$executionId",
                                "status": None,
                                "results": None
                            }
                        }
                    },
                    # Include analysis data if available  
                    "analysis": {
                        "$cond": {
                            "if": {"$gt": [{"$size": "$analysis_data"}, 0]},
                            "then": {
                                "llm_response": {"$arrayElemAt": ["$analysis_data.llm_response", 0]},
                                "question": {"$arrayElemAt": ["$analysis_data.question", 0]}
                            },
                            "else": None
                        }
                    }
                }
            },
            
            # Sort by creation time ascending so newest appears last when rendered
            {"$sort": {"createdAt": 1}}
        ]
        
        # Execute aggregation
        # ✅ FIXED: Use encapsulated aggregation method
        messages = await self.db.aggregate_messages(pipeline)
        
        # Debug: Log the message ordering
        if messages:
            logger.info(f"DEBUG: Retrieved {len(messages)} messages, first: {messages[0].get('createdAt')}, last: {messages[-1].get('createdAt')}")
            logger.info(f"DEBUG: Message order - first message content: {messages[0].get('content', '')[:50]}...")
            logger.info(f"DEBUG: Message order - last message content: {messages[-1].get('content', '')[:50]}...")
        
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
                    "messageId": msg.get("messageId"),
                    "role": msg.get("role"),
                    "content": msg.get("content"),
                    "timestamp": msg.get("created_at", "").isoformat() if hasattr(msg.get("created_at"), 'isoformat') else str(msg.get("created_at")),
                    "analysisId": msg.get("analysisId"),
                    "executionId": msg.get("executionId"),
                    "metadata": msg.get("metadata", {}),
                    "logs": msg.get("logs", []),  # Include logs for progress history
                    # Include pre-populated execution and analysis data
                    "execution": msg.get("execution"),
                    "analysis": msg.get("analysis")
                }
                for msg in messages
            ]
        }
    
    
    
    async def update_session(self, session_id: str, update_data: Dict[str, Any]) -> bool:
        """Update session metadata"""
        return await self.db.update_session(session_id, update_data)
    
    async def clear_session_messages(self, session_id: str) -> int:
        """Clear all messages from a session but keep the session"""
        # ✅ FIXED: Delete messages using encapsulated method
        deleted_count = await self.db.delete_session_messages(session_id)
        
        # ✅ FIXED: Update session message count using encapsulated method
        await self.db.update_session_messages_count(session_id, 0)
        
        return deleted_count
    
    async def delete_session(self, session_id: str) -> bool:
        """Delete session and all its messages"""
        # Delete messages
        # ✅ FIXED: Delete messages using encapsulated method
        deleted_count = await self.db.delete_session_messages(session_id)
        # Delete session
        # ✅ FIXED: Delete session using encapsulated method
        success = await self.db.delete_session(session_id)
        return success


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
        
        # Extract and promote fields for easier access
        description = self._extract_description(llm_response)
        parameters = self._extract_parameters(llm_response)

        analysis = AnalysisModel(
            user_id=user_id,
            question=question,  
            llm_response=llm_response,
            script_url=script,
            description=description,
            parameters=parameters,
        )
        
        return await self.db.create_analysis(analysis)
    
    def _extract_description(self, llm_response: Dict[str, Any]) -> Optional[str]:
        """Extract analysis description from llmResponse"""
        # Try different possible paths for description
        description = llm_response.get('analysis_description')
        if not description:
            description = llm_response.get('description')
        if not description:
            description = llm_response.get('analysis', {}).get('description')
        if not description:
            # Try to get from summary or other fields
            description = llm_response.get('summary')
        
        return description if description else None
    
    def _extract_parameters(self, llm_response: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract parameters from llmResponse.execution.parameters"""
        # Try different possible paths for parameters
        parameters = None
        
        # Path 1: llmResponse.execution.parameters
        if 'execution' in llm_response and 'parameters' in llm_response['execution']:
            parameters = llm_response['execution']['parameters']
        
        # Path 2: llmResponse.parameters
        elif 'parameters' in llm_response:
            parameters = llm_response['parameters']
        
        # Path 3: llmResponse.script_generation.parameters
        elif 'script_generation' in llm_response and 'parameters' in llm_response['script_generation']:
            parameters = llm_response['script_generation']['parameters']
        
        return parameters if parameters else None
    
    async def get_similar_analyses(self, user_id: str, category: str, limit: int = 10) -> List[AnalysisModel]:
        """Get similar analyses in same category"""
        return await self.db.list_analyses(user_id, category=category, limit=limit)
    
    async def get_reusable_analyses(self, user_id: str) -> List[AnalysisModel]:
        """Get all analyses that can be reused as templates"""
        # ✅ FIXED: Find analyses using encapsulated method
        analyses = await self.db.find_analyses({
            "userId": user_id
        })
        
        return analyses  # Already returns AnalysisModel objects
    
    async def can_reuse_analysis(self, analysis_id: str, new_question: str) -> bool:
        """Check if analysis can be reused for new question"""
        analysis = await self.db.get_analysis(analysis_id)
        if not analysis:
            return False
        
        # Analysis is a reusable template, so we can always attempt reuse
        # Execution state is tracked separately in ExecutionModel
        await self.db.mark_analysis_used(analysis_id)
        return True
    
    async def get_analysis_by_id(self, analysis_id: str) -> Optional[Dict[str, Any]]:
        """Get analysis details by ID"""
        analysis = await self.db.get_analysis(analysis_id)
        if analysis:
            # Convert to dict format for API response
            return analysis.dict(by_alias=True) if hasattr(analysis, 'dict') else analysis
        return None
    
    async def get_session_analyses(self, session_id: str, limit: int = 5) -> List[AnalysisModel]:
        """Get latest analyses for a session, sorted by newest first"""
        analyses = await self.db.find_analyses({
            "sessionId": session_id
        })
        
        # Sort by created_at descending (newest first)
        if analyses:
            analyses.sort(
                key=lambda a: a.created_at if hasattr(a.created_at, 'timestamp') else a.created_at,
                reverse=True
            )
            analyses = analyses[:limit]
        
        return analyses


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
    
    async def get_user_execution_history(self, user_id: str, limit: int = 100) -> List[ExecutionModel]:
        """Get execution history for user"""
        return await self.db.list_user_executions(user_id, limit)
    
    async def get_executions_by_analysis_id(self, analysis_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get all executions for a specific analysis"""
        executions = await self.db.find_executions({
            "analysisId": analysis_id
        }, limit=limit, sort=[("createdAt", -1)])  # Sort by newest first
        
        # Convert to dict format for API response
        result = []
        for execution in executions:
            if hasattr(execution, 'dict'):
                result.append(execution.dict(by_alias=True))
            else:
                result.append(execution)
        return result
    
    async def get_primary_execution_by_analysis_id(self, analysis_id: str) -> Optional[Dict[str, Any]]:
        """Get the primary (original) execution for an analysis"""
        executions = await self.db.find_executions({
            "analysisId": analysis_id,
            "executionType": "primary"
        }, limit=1, sort=[("createdAt", 1)])  # Get the earliest primary execution
        
        if executions:
            execution = executions[0]
            if hasattr(execution, 'dict'):
                return execution.dict(by_alias=True)
            return execution
        return None
    
    async def get_user_reruns_by_analysis_id(self, analysis_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get user-initiated re-runs for a specific analysis (excluding primary)"""
        executions = await self.db.find_executions({
            "analysisId": analysis_id,
            "executionType": {"$ne": "primary"}  # Exclude primary executions
        }, limit=limit, sort=[("createdAt", -1)])  # Sort by newest first
        
        # Convert to dict format for API response
        result = []
        for execution in executions:
            if hasattr(execution, 'dict'):
                result.append(execution.dict(by_alias=True))
            else:
                result.append(execution)
        return result
    
    async def get_execution_by_message_id(self, message_id: str) -> Optional[Dict[str, Any]]:
        """Get the execution associated with a specific message"""
        executions = await self.db.find_executions({
            "createdMessageId": message_id
        }, limit=1)
        
        if executions:
            execution = executions[0]
            if hasattr(execution, 'dict'):
                return execution.dict(by_alias=True)
            return execution
        return None


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
        # ✅ FIXED: Delete cache using encapsulated method
        await self.db.delete_analysis_cache(analysis_id)


class RepositoryManager:
    """Unified repository access point"""
    
    def __init__(self, db: MongoDBClient):
        self.db_client = db
        self.session = SessionRepository(db)
        self.chat = ChatRepository(db)
        self.analysis = AnalysisRepository(db)
        self.execution = ExecutionRepository(db)
        self.cache = CacheRepository(db)
    
    async def initialize(self) -> None:
        """Initialize all repositories"""
        await self.db_client.connect()
        logger.info("✅ Repository manager initialized")
    
    async def shutdown(self) -> None:
        """Shutdown all repositories"""
        await self.db_client.disconnect()
        logger.info("✅ Repository manager shutdown")
