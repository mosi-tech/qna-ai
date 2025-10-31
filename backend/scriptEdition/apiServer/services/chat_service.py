"""
Chat History Service - Handles chat persistence and retrieval
"""

import logging
from typing import Optional, List, Dict, Any
from datetime import datetime

from db.repositories import RepositoryManager, ChatRepository
from db.schemas import (
    ChatMessageModel,
    ChatSessionModel,
    AnalysisModel,
    RoleType,
    QueryType,
)

logger = logging.getLogger("chat-service")


class ChatHistoryService:
    """Service for managing chat history and conversations"""
    
    def __init__(self, repo_manager: RepositoryManager):
        self.repo = repo_manager
        self.chat_repo = repo_manager.chat
        self.logger = logger
        
        # Initialize data transformer for message transformation
        from .utils.data_transformers import DataTransformer
        self.data_transformer = DataTransformer(self.chat_repo.db)
    
    
    async def start_session(self, user_id: str, title: Optional[str] = None) -> str:
        """Start a new chat session"""
        try:
            session_id = await self.chat_repo.start_session(user_id, title)
            self.logger.info(f"✓ Started session: {session_id}")
            return session_id
        except Exception as e:
            self.logger.error(f"✗ Failed to start session: {e}")
            raise
    
    async def add_user_message(
        self,
        session_id: str,
        user_id: str,
        question: str,
        query_type: QueryType = QueryType.COMPLETE,
        expanded_question: Optional[str] = None,
        expansion_confidence: float = 0.0,
    ) -> str:
        """Add user message to conversation"""
        try:
            msg_id = await self.chat_repo.add_user_message(
                session_id=session_id,
                user_id=user_id,
                question=question,
                query_type=query_type,
            )
            
            # Update with expansion if provided
            if expanded_question:
                await self.repo.db.db.chat_messages.update_one(
                    {"messageId": msg_id},
                    {
                        "$set": {
                            "metadata": {
                                "response_type": "user_message",
                                "original_question": question,
                                "expanded_question": expanded_question,
                                "expansion_confidence": expansion_confidence,
                                "query_type": query_type.value if query_type else None,
                            }
                        }
                    }
                )
            
            self.logger.info(f"✓ Added user message: {msg_id}")
            return msg_id
        except Exception as e:
            self.logger.error(f"✗ Failed to add user message: {e}")
            raise
    
    async def add_assistant_message_with_analysis(
        self,
        session_id: str,
        user_id: str,
        script: str,
        explanation: str,
        analysis: AnalysisModel,
        execution_id: Optional[str] = None,
    ) -> str:
        """Add assistant message with generated analysis (KEY WORKFLOW)"""
        try:
            msg_id = await self.chat_repo.add_assistant_message_with_analysis(
                session_id=session_id,
                user_id=user_id,
                script=script,
                explanation=explanation,
                analysis=analysis,
                mcp_calls=[],
                execution_id=execution_id,
            )
            
            self.logger.info(f"✓ Added assistant message with analysis: {msg_id}")
            return msg_id
        except Exception as e:
            self.logger.error(f"✗ Failed to add assistant message: {e}")
            raise
    
    async def add_assistant_message(
        self,
        session_id: str,
        user_id: str,
        content: str,
        analysis_id: str = None,
        execution_id: str = None,
        metadata: Dict[str, Any] = None
    ) -> str:
        """Add regular assistant message (with optional analysis and execution references)"""
        try:
            msg_id = await self.chat_repo.add_assistant_message(
                session_id=session_id,
                user_id=user_id,
                content=content,
                analysis_id=analysis_id,
                execution_id=execution_id,
                metadata=metadata
            )
            
            self.logger.info(f"✓ Added assistant message: {msg_id}")
            return msg_id
        except Exception as e:
            self.logger.error(f"✗ Failed to add assistant message: {e}")
            raise
    
    async def get_session_context(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session with full context for LLM"""
        try:
            context = await self.chat_repo.get_session_with_context(session_id)
            self.logger.info(f"✓ Retrieved session context: {session_id}")
            return context
        except Exception as e:
            self.logger.error(f"✗ Failed to get session context: {e}")
            raise
    
    async def get_conversation_history(self, session_id: str) -> List[Dict[str, Any]]:
        """Get conversation history for LLM context"""
        try:
            history = await self.chat_repo.get_conversation_history(session_id)
            self.logger.info(f"✓ Retrieved conversation history: {len(history)} messages")
            return history
        except Exception as e:
            self.logger.error(f"✗ Failed to get conversation history: {e}")
            raise
    
    async def get_session(self, session_id: str) -> Optional[ChatSessionModel]:
        """Get session by ID"""
        try:
            session = await self.repo.db.get_session(session_id)
            return session
        except Exception as e:
            self.logger.error(f"✗ Failed to get session: {e}")
            return None
    
    async def list_sessions(self, user_id: str, limit: int = 50) -> List[ChatSessionModel]:
        """Get user's chat sessions"""
        try:
            sessions = await self.repo.db.list_sessions(user_id, limit=limit)
            self.logger.info(f"✓ Retrieved {len(sessions)} sessions for user: {user_id}")
            return sessions
        except Exception as e:
            self.logger.error(f"✗ Failed to list sessions: {e}")
            raise
    
    async def archive_session(self, session_id: str) -> bool:
        """Archive a session"""
        try:
            result = await self.repo.db.archive_session(session_id)
            self.logger.info(f"✓ Archived session: {session_id}")
            return result
        except Exception as e:
            self.logger.error(f"✗ Failed to archive session: {e}")
            raise
    
    async def get_user_sessions(
        self,
        user_id: str,
        skip: int = 0,
        limit: int = 10,
        search_text: Optional[str] = None,
        archived: Optional[bool] = None,
    ) -> List[Dict[str, Any]]:
        """Get user sessions with metadata for list view"""
        try:
            sessions = await self.chat_repo.get_user_sessions(
                user_id=user_id,
                skip=skip,
                limit=limit,
                search_text=search_text,
                archived=archived,
            )
            self.logger.info(f"✓ Retrieved {len(sessions)} sessions for user: {user_id}")
            return sessions
        except Exception as e:
            self.logger.error(f"✗ Failed to get user sessions: {e}")
            raise
    
    async def get_session_with_messages(self, session_id: str, limit: int = 5, offset: int = 0) -> Optional[Dict[str, Any]]:
        """Get session with paginated messages for resume"""
        try:
            session = await self.chat_repo.get_session_with_messages(session_id, limit=limit, offset=offset)
            if session:
                # Transform messages to clean UI-safe data only
                if session.get('messages'):
                    clean_messages = []
                    for msg in session['messages']:
                        clean_msg = await self.data_transformer.transform_message_to_ui_data(msg)
                        clean_messages.append(clean_msg)
                    
                    # Replace messages with clean versions
                    session['messages'] = clean_messages
                
                self.logger.info(f"✓ Retrieved session with messages: {session_id} (offset={offset}, limit={limit})")
            return session
        except Exception as e:
            self.logger.error(f"✗ Failed to get session with messages: {e}")
            raise
    
    
    async def update_session(
        self,
        session_id: str,
        title: Optional[str] = None,
        is_archived: Optional[bool] = None,
    ) -> bool:
        """Update session metadata"""
        try:
            update_data = {}
            if title is not None:
                update_data['title'] = title
            if is_archived is not None:
                update_data['is_archived'] = is_archived
            
            result = await self.chat_repo.update_session(session_id, update_data)
            if result:
                self.logger.info(f"✓ Updated session: {session_id}")
            return result
        except Exception as e:
            self.logger.error(f"✗ Failed to update session: {e}")
            raise
    
    async def delete_session(self, session_id: str) -> bool:
        """Delete a session and all its messages"""
        try:
            result = await self.chat_repo.delete_session(session_id)
            if result:
                self.logger.info(f"✓ Deleted session: {session_id}")
            return result
        except Exception as e:
            self.logger.error(f"✗ Failed to delete session: {e}")
            raise
