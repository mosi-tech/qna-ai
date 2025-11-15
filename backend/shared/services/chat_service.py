"""
Chat History Service - Handles chat persistence and retrieval
"""

import logging
from typing import Optional, List, Dict, Any
from datetime import datetime

from ..db.repositories import RepositoryManager, ChatRepository
from ..db.schemas import (
    ChatMessageModel,
    ChatSessionModel,
    AnalysisModel,
    RoleType,
    QueryType,
)
from ..utils.data_transformers import DataTransformer

logger = logging.getLogger("chat-service")


class ChatHistoryService:
    """Service for managing chat history and conversations"""
    
    def __init__(self, repo_manager: RepositoryManager):
        self.repo = repo_manager
        self.session_repo = repo_manager.session  # ✅ Direct access to SessionRepository
        self.chat_repo = repo_manager.chat
        self.logger = logger
        self.data_transformer = DataTransformer(self.chat_repo.db)
    
    async def validate_session_ownership(self, session_id: str, user_id: str) -> bool:
        """Validate that a user owns a specific session"""
        try:
            # Use the dedicated session repository for chat_sessions collection
            session_metadata = await self.session_repo.get_session_metadata(session_id)
            
            if not session_metadata:
                return False
            
            return session_metadata.user_id == user_id
            
        except Exception as e:
            logger.warning(f"Failed to validate session ownership for {session_id}: {e}")
            return False
    
    async def validate_message_ownership(self, message_id: str, user_id: str) -> bool:
        """Validate that a user owns a specific message"""
        try:
            # Get raw message to check ownership
            message = await self.chat_repo.get_raw_message_by_id(message_id)
            
            if not message:
                return False
            
            # Check userId field (handle both userId and user_id variants)
            message_user_id = message.get('userId') or message.get('user_id')
            return message_user_id == user_id
            
        except Exception as e:
            logger.warning(f"Failed to validate message ownership for {message_id}: {e}")
            return False
    
    
    async def start_session(self, user_id: str, title: Optional[str] = None) -> str:
        """Start a new chat session"""
        try:
            # ✅ Use SessionRepository for session operations
            from ..db.schemas import ChatSessionModel
            session = ChatSessionModel(user_id=user_id, title=title or "New Conversation")
            session_id = await self.session_repo.create_session(session)
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
        message_id: Optional[str] = None,
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
                message_id=message_id,
                query_type=query_type,
            )
            
            # ✅ FIXED: Update with expansion if provided using encapsulated method
            if expanded_question:
                await self.repo.db_client.update_message(
                    msg_id,
                    {
                        "metadata": {
                            "original_question": question,
                            "expanded_question": expanded_question,
                            "expansion_confidence": expansion_confidence,
                            "query_type": query_type.value if query_type else None,
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
        message_id: str = None,
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
                message_id=message_id,
                analysis_id=analysis_id,
                execution_id=execution_id,
                metadata=metadata
            )
            
            self.logger.info(f"✓ Added assistant message: {msg_id}")
            return msg_id
        except Exception as e:
            self.logger.error(f"✗ Failed to add assistant message: {e}")
            raise
    
    async def update_assistant_message(
        self,
        message_id: str,
        content: str,
        analysis_id: str = None,
        execution_id: str = None,
        metadata: Dict[str, Any] = None
    ) -> bool:
        """Update existing assistant message with new content and metadata"""
        try:
            success = await self.chat_repo.update_assistant_message(
                message_id=message_id,
                content=content,
                analysis_id=analysis_id,
                execution_id=execution_id,
                metadata=metadata
            )
            
            if success:
                self.logger.info(f"✓ Updated assistant message: {message_id}")
            else:
                self.logger.warning(f"⚠️ Failed to update assistant message: {message_id}")
            
            return success
        except Exception as e:
            self.logger.error(f"✗ Failed to update assistant message: {e}")
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
    
    async def get_conversation_history(self, session_id: str, include_metadata: bool = False) -> List[Dict[str, Any]]:
        """Get conversation history for LLM context"""
        try:
            history = await self.chat_repo.get_conversation_history(session_id, include_metadata=include_metadata)
            self.logger.info(f"✓ Retrieved conversation history: {len(history)} messages")
            return history
        except Exception as e:
            self.logger.error(f"✗ Failed to get conversation history: {e}")
            raise
    
    async def get_session(self, session_id: str) -> Optional[ChatSessionModel]:
        """Get session by ID"""
        try:
            session = await self.session_repo.get_session_metadata(session_id)
            return session
        except Exception as e:
            self.logger.error(f"✗ Failed to get session: {e}")
            return None
    
    async def list_sessions(self, user_id: str, limit: int = 50) -> List[ChatSessionModel]:
        """Get user's chat sessions"""
        try:
            sessions = await self.session_repo.find_user_sessions(user_id, limit=limit)
            self.logger.info(f"✓ Retrieved {len(sessions)} sessions for user: {user_id}")
            return sessions
        except Exception as e:
            self.logger.error(f"✗ Failed to list sessions: {e}")
            raise
    
    async def archive_session(self, session_id: str) -> bool:
        """Archive a session"""
        try:
            result = await self.session_repo.update_session(session_id, {"is_archived": True})
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
        """Get user sessions with metadata for list view - FIXED: Uses proper separation"""
        try:
            # ✅ FIXED: Use SessionRepository directly for session operations
            sessions = await self.session_repo.find_user_sessions(
                user_id=user_id,
                skip=skip,
                limit=limit,
                search_text=search_text,
                archived=archived,
            )
            
            # ✅ FIXED: Transform to dict format - use existing session fields, no extra DB calls!
            session_list = []
            for session in sessions:
                session_list.append({
                    "session_id": session.session_id,
                    "title": session.title,
                    "created_at": session.created_at.isoformat() if session.created_at else "",
                    "updated_at": session.updated_at.isoformat() if session.updated_at else "",
                    "message_count": session.message_count,  # ✅ Already available in session model!
                    "last_message": None,  # ✅ Remove expensive per-session query
                    "is_archived": getattr(session, 'is_archived', False),
                })
            
            self.logger.info(f"✓ Retrieved {len(session_list)} sessions for user: {user_id}")
            return session_list
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
            
            # ✅ FIXED: Use SessionRepository for session operations
            result = await self.session_repo.update_session(session_id, update_data)
            if result:
                self.logger.info(f"✓ Updated session: {session_id}")
            return result
        except Exception as e:
            self.logger.error(f"✗ Failed to update session: {e}")
            raise
    
    async def delete_session(self, session_id: str) -> bool:
        """Delete a session and all its messages"""
        try:
            # ✅ FIXED: Use SessionRepository for session operations
            result = await self.session_repo.delete_session(session_id)
            if result:
                self.logger.info(f"✓ Deleted session: {session_id}")
            return result
        except Exception as e:
            self.logger.error(f"✗ Failed to delete session: {e}")
            raise
    
    async def get_message_by_id(self, message_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific message by its ID with UI transformation"""
        try:
            message = await self.chat_repo.get_message_by_id(message_id)
            if message:
                # Transform message to clean UI-safe data (same pattern as get_session_with_messages)
                ui_message = await self.data_transformer.transform_message_to_ui_data(message)
                self.logger.info(f"✓ Retrieved and transformed message: {message_id}")
                return ui_message
            return None
        except Exception as e:
            self.logger.error(f"✗ Failed to get message: {e}")
            raise
    
    # === HYBRID CHAT + ANALYSIS SUPPORT (GitHub Issue #122) ===
    
    async def add_hybrid_message(
        self,
        session_id: str,
        user_id: str,
        content: str,
        message_type: str,  # "chat", "educational_chat", "analysis_confirmation", etc.
        intent: str = None,
        analysis_suggestion: Dict[str, Any] = None,
        analysis_id: str = None,
        execution_id: str = None,
        in_reply_to: str = None
    ) -> str:
        """
        Add hybrid chat+analysis message with enhanced metadata for tracking
        
        Args:
            session_id: Chat session ID
            user_id: User ID 
            content: Message content
            message_type: Type of hybrid message (chat, educational_chat, etc.)
            intent: Classified intent from IntentClassifierService
            analysis_suggestion: Analysis suggestion data if applicable
            analysis_id: Reference to analysis if applicable
            execution_id: Reference to execution if applicable
            in_reply_to: Message ID this is replying to
            
        Returns:
            Message ID
        """
        try:
            # Build hybrid metadata
            hybrid_metadata = {
                "response_type": message_type,
                "intent": intent,
                "hybrid_chat": True,  # Flag to identify hybrid messages
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Add analysis suggestion if provided
            if analysis_suggestion:
                hybrid_metadata["analysis_suggestion"] = {
                    "topic": analysis_suggestion.get("topic"),
                    "description": analysis_suggestion.get("description"), 
                    "suggested_question": analysis_suggestion.get("suggested_question"),
                    "analysis_type": analysis_suggestion.get("analysis_type")
                }
            
            # Add reply reference if provided
            if in_reply_to:
                hybrid_metadata["in_reply_to"] = in_reply_to
            
            # Add message using existing method
            msg_id = await self.add_assistant_message(
                session_id=session_id,
                user_id=user_id,
                content=content,
                analysis_id=analysis_id,
                execution_id=execution_id,
                metadata=hybrid_metadata
            )
            
            self.logger.info(f"✓ Added hybrid message: {msg_id} (type: {message_type})")
            return msg_id
            
        except Exception as e:
            self.logger.error(f"✗ Failed to add hybrid message: {e}")
            raise
