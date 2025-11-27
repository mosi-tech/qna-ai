#!/usr/bin/env python3
"""
Conversation Storage - Efficient conversation history management
Now with Redis backend for cross-process message sharing
"""

import uuid
import json
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, asdict
from abc import ABC, abstractmethod

from shared.constants import QueryType, MessageIntent


@dataclass
class BaseMessage(ABC):
    """Base class for all messages in conversation"""
    id: str
    content: str
    timestamp: datetime
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
    
    @property
    @abstractmethod
    def role(self) -> str:
        """Role identifier for the message"""
        pass
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        result = asdict(self)
        result['role'] = self.role
        result['timestamp'] = self.timestamp.isoformat()
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """Create message from dictionary based on role"""
        role = data.get('role')
        if role == 'user':
            return UserMessage.from_dict(data)
        elif role == 'assistant':
            return AssistantMessage.from_dict(data)
        else:
            raise ValueError(f"Unknown message role: {role}")

@dataclass
class UserMessage(BaseMessage):
    """Message from a user"""
    user_id: str = "anonymous"
    
    @property
    def role(self) -> str:
        return "user"
    
    @classmethod
    def create(cls, content: str, user_id: str = "anonymous", **metadata) -> 'UserMessage':
        """Create a user message"""
        return cls(
            id=str(uuid.uuid4()),
            content=content,
            timestamp=datetime.now(),
            user_id=user_id,
            metadata=metadata
        )
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserMessage':
        """Create UserMessage from dictionary"""
        return cls(
            id=data.get('message_id', str(uuid.uuid4())),  # Generate new ID if not present
            content=data['content'],
            timestamp=datetime.fromisoformat(data['timestamp']),
            user_id=data.get('user_id', data.get('metadata', {}).get('user_id', 'anonymous')),
            metadata=data.get('metadata', {})
        )

@dataclass
class AssistantMessage(BaseMessage):
    """Message from the assistant"""
    message_type: Optional[str] = None
    intent: Optional[str] = None
    analysis_triggered: bool = False
    analysis_suggestion: Optional[Dict[str, Any]] = None
    
    @property
    def role(self) -> str:
        return "assistant"
    
    @classmethod
    def create(cls, content: str, **metadata) -> 'AssistantMessage':
        """Create an assistant message"""
        # Extract known fields from metadata
        message_type = metadata.pop('message_type', None)
        intent = metadata.pop('intent', None)
        analysis_triggered = metadata.pop('analysis_triggered', False)
        analysis_suggestion = metadata.pop('analysis_suggestion', None)
        
        return cls(
            id=str(uuid.uuid4()),
            content=content,
            timestamp=datetime.now(),
            message_type=message_type,
            intent=intent,
            analysis_triggered=analysis_triggered,
            analysis_suggestion=analysis_suggestion,
            metadata=metadata
        )
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AssistantMessage':
        """Create AssistantMessage from dictionary"""
        metadata = data.get('metadata', {})
        return cls(
            id=data.get('message_id', str(uuid.uuid4())),  # Generate new ID if not present
            content=data.get('content', ""),
            timestamp=datetime.fromisoformat(data['timestamp']),
            # Try top-level fields first, then fallback to metadata
            message_type=data.get('message_type') or metadata.get('message_type'),
            intent=data.get('intent') or metadata.get('intent'),
            analysis_triggered=data.get('analysis_triggered', metadata.get('analysis_triggered', False)),
            analysis_suggestion=data.get('analysis_suggestion') or metadata.get('analysis_suggestion'),
            metadata=metadata
        )
    
    def has_analysis_suggestion(self) -> bool:
        """Check if this message has an analysis suggestion"""
        return self.analysis_suggestion is not None
    
    def get_analysis_topic(self) -> Optional[str]:
        """Get the analysis suggestion topic if available"""
        if self.analysis_suggestion:
            return self.analysis_suggestion.get('topic')
        return None
    
    def to_context_string(self) -> str:
        """Format assistant message for context with rich metadata inline"""
        # Start with the main content
        result = self.content
        
        # Add metadata as natural annotations
        metadata_parts = []
        
        if self.message_type and self.message_type != "chat":
            metadata_parts.append(f"Response type: {self.message_type}")
            
        if self.intent:
            metadata_parts.append(f"Intent: {self.intent}")
            
        if self.analysis_triggered:
            metadata_parts.append("Analysis was triggered")
            
        if self.has_analysis_suggestion():
            suggestion = self.analysis_suggestion
            topic = suggestion.get('topic', '')
            description = suggestion.get('description', '')
            suggested_question = suggestion.get('suggested_question', '')
            
            if topic:
                metadata_parts.append(f"Analysis suggestion: {topic}")
            if description and len(description) <= 100:
                metadata_parts.append(f"Description: {description}")
            if suggested_question and len(suggested_question) <= 150:
                metadata_parts.append(f"Suggested question: {suggested_question}")
        
        # Add metadata as natural postfix if any exists
        if metadata_parts:
            result += f"\n[Metadata: {' | '.join(metadata_parts)}]"
            
        return result

# Type alias for any message type
Message = Union[UserMessage, AssistantMessage]


class ConversationStore:
    """Single source of truth for conversation data - message-based design
    
    Handles independent user and assistant messages in sequential order.
    Supports real conversation patterns like multiple user messages, missing responses, etc.
    """
    
    def __init__(self, session_id: str, chat_history_service=None, redis_client=None):
        self.session_id = session_id
        self.redis_client = redis_client
        self._redis_key = f"conversation:{session_id}"
        self._redis_analyses_key = f"analyses:{session_id}"  # Cache for recent analyses
        self._redis_executions_key = f"executions:{session_id}"  # Cache for recent executions
        self._context_window_size = 20  # Keep last 20 messages (10 exchanges)
        self._max_recent_analyses = 5  # Keep last 5 analyses for context
        self._max_recent_executions = 5  # Keep last 5 executions for context
        self.chat_history_service = chat_history_service
        
        # Redis health tracking to prevent stale data issues
        self.redis_loaded = False  # True when Redis has been successfully loaded/populated
        
    
    @classmethod
    async def load_or_create(cls, session_id: str, chat_history_service, redis_client=None) -> 'ConversationStore':
        """
        Load existing conversation with Redis health tracking
        
        Logic:
        1. If Redis was never successfully loaded (redis_loaded=False), load from DB first
        2. If Redis read/write fails, mark redis_loaded=False and fallback to DB
        3. Only trust Redis if it was previously loaded successfully
        """
        store = cls(session_id, chat_history_service, redis_client)
        
        import logging
        logger = logging.getLogger(__name__)
        
        # Check if we should trust Redis (was it successfully loaded before?)
        redis_available = False
        if redis_client:
            try:
                # Test Redis connectivity
                await redis_client.ping()
                redis_messages = await redis_client.lrange(store._redis_key, 0, -1)
                redis_available = True
                
                # Only use Redis if it has data AND we trust it's up-to-date
                # For now, we'll prioritize DB consistency and populate Redis from DB
                if redis_messages:
                    logger.debug(f"🔍 Found {len(redis_messages)} messages in Redis for session {session_id[:8]}")
                    # But we still load from DB to ensure consistency
                
            except Exception as e:
                logger.warning(f"⚠️ Redis connectivity failed: {e}")
                store.redis_loaded = False
        
        # Always load from DB first to ensure we have the latest data
        # Use descending order (newest first) so we naturally get the latest messages
        # This is more efficient: we get newest messages first and trim naturally
        if chat_history_service:
            try:
                db_messages = await chat_history_service.get_conversation_history(
                    session_id=session_id,
                    include_metadata=True,
                    sort_order=-1  # Descending: newest first
                )
                
                if db_messages:
                    # Populate Redis from DB (source of truth)
                    if redis_available:
                        await store._populate_from_db_messages(db_messages)
                        store.redis_loaded = True
                        logger.debug(f"✅ Loaded {len(db_messages)} messages from DB and synced to Redis")
                        
                        # Extract and cache analyses/executions from messages
                        await store._extract_and_cache_analyses_executions()
                    else:
                        logger.debug(f"✅ Loaded {len(db_messages)} messages from DB (Redis unavailable)")
                else:
                    # New conversation - mark Redis as loaded if available
                    if redis_available:
                        store.redis_loaded = True
                        logger.debug(f"✅ New conversation created with Redis available")
                
            except Exception as e:
                logger.warning(f"⚠️ Failed to load session from DB: {e}")
                store.redis_loaded = False
        
        return store
    
    async def _populate_from_db_messages(self, db_messages: List[Dict[str, Any]]) -> None:
        """Populate Redis from DB messages and trim to context window
        
        DB messages come in descending order (newest first).
        We populate in reverse order (oldest first in Redis list) for proper chronological order.
        """
        if not db_messages or not self.redis_client:
            return
        
        # Clear existing Redis data
        await self.redis_client.delete(self._redis_key)
        
        # Populate Redis from DB messages in reverse order (oldest first)
        # This way the Redis list has newest on the left (via lpush) for natural ordering
        for db_msg in reversed(db_messages):  # Reverse descending to get ascending
            role = db_msg.get("role", "user")
            if role == "user":
                message = UserMessage.from_dict(db_msg)
            else:
                message = AssistantMessage.from_dict(db_msg)
            await self._add_message_to_redis(message)
        
        # Trim to context window size after populating
        await self._trim_messages()
    
    async def _extract_and_cache_analyses_executions(self) -> None:
        """Cache latest analyses and executions for session independently
        
        Fetches the latest 5 analyses and 5 executions for the session
        directly from the database repositories, not from messages.
        """
        if not self.chat_history_service or not self.chat_history_service.repo:
            return
        
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            repo = self.chat_history_service.repo
            
            # Fetch latest executions for this session (already sorted by createdAt descending)
            executions = await repo.execution.get_execution_history(
                session_id=self.session_id
            )
            
            # Limit to max_recent_executions
            executions = executions[:self._max_recent_executions]
            
            # Cache executions
            for execution in executions:
                execution_data = {
                    "execution_id": execution.execution_id,
                    "analysis_id": execution.analysis_id,  # May be None for independent executions
                    "timestamp": execution.created_at.isoformat() if hasattr(execution.created_at, 'isoformat') else str(execution.created_at),
                    "status": execution.status.value if hasattr(execution.status, 'value') else str(execution.status),
                    "question": execution.question or "",
                    "script_name": getattr(execution, 'generated_script', "")[:50] if getattr(execution, 'generated_script', None) else ""
                }
                await self.add_recent_execution(execution_data)
            
            # TODO: Fetch and cache analyses once analysis model includes session_id
            # analyses = await repo.analysis.get_session_analyses(
            #     session_id=self.session_id,
            #     limit=self._max_recent_analyses
            # )
            # 
            # Cache analyses
            # for analysis in analyses:
            #     analysis_data = {
            #         "analysis_id": analysis.analysis_id,
            #         "timestamp": analysis.created_at.isoformat() if hasattr(analysis.created_at, 'isoformat') else str(analysis.created_at),
            #         "question": analysis.question or "",
            #         "analysis_type": "unknown"
            #     }
            #     await self.add_recent_analysis(analysis_data)
            
            logger.debug(f"✅ Cached {len(executions)} executions for session {self.session_id[:8]}")
            
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"❌ Failed to cache analyses/executions for session {self.session_id[:8]}: {e}")
        
    
    
    # ========== NEW MESSAGE-BASED API ==========
    
    async def add_user_message(self, content: str, user_id: str = "anonymous", **metadata) -> UserMessage:
        """Add user message - immediately persisted, independent of assistant response"""
        message = UserMessage.create(content, user_id, **metadata)
        
        # 1. Add to Redis immediately  
        await self._add_message_to_redis(message)
        
        # 2. Persist to database immediately (never lost)
        if self.chat_history_service:
            try:
                await self.chat_history_service.add_user_message(
                    session_id=self.session_id,
                    user_id=user_id,
                    message_id=message.id,  # Pass the local ID to ensure consistency
                    question=content
                )
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"❌ Failed to persist user message: {e}")
                # Continue - message preserved in Redis
        
        # 3. Trim context window
        await self._trim_messages()
        
        return message
    
    async def add_assistant_message(self, content: str, user_id: str = "anonymous", **metadata) -> AssistantMessage:
        """Add assistant message - independent of user message"""
        import logging
        logger = logging.getLogger(__name__)
        
        logger.debug(f"📝 add_assistant_message called - redis_client={bool(self.redis_client)}, redis_loaded={self.redis_loaded}")
        message = AssistantMessage.create(content, **metadata)
        logger.debug(f"📝 Created AssistantMessage: {message.id}")
        
        # 1. Add to Redis immediately
        logger.debug(f"📝 Adding to Redis...")
        await self._add_message_to_redis(message)
        logger.debug(f"✅ Added to Redis (redis_loaded={self.redis_loaded})")
        
        # 2. Persist to database
        if self.chat_history_service:
            try:
                logger.debug(f"📝 Persisting to database...")
                await self.chat_history_service.add_assistant_message(
                    session_id=self.session_id,
                    user_id=user_id,
                    content=content,
                    message_id=message.id,  # Pass the local ID to ensure consistency
                    metadata=metadata
                )
                logger.debug(f"✅ Persisted to database")
            except Exception as e:
                logger.error(f"❌ Failed to persist assistant message: {e}")
                # Continue - message preserved in Redis
        
        # 3. Trim context window
        await self._trim_messages()
        logger.info(f"✅ Added assistant message to conversation: {message.id}")
        
        return message
    
    async def update_assistant_message(self, message_id: str, content: str = None, analysis_id: str = None, 
                                     execution_id: str = None, **metadata) -> bool:
        """Update existing assistant message by ID"""
        # 1. Find and update message in Redis
        success = await self._update_message_in_redis(message_id, content, analysis_id, execution_id, **metadata)
        
        if not success:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"⚠️ Message {message_id} not found in conversation store")
            messages = await self.get_messages()
            logger.debug(f"Available assistant messages: {[(m.id, m.content[:50] + '...' if len(m.content) > 50 else m.content) for m in messages if isinstance(m, AssistantMessage)]}")
            logger.debug(f"All messages: {[(m.id, m.role, m.content[:30] + '...' if len(m.content) > 30 else m.content) for m in messages]}")
            logger.debug(f"Session ID: {getattr(self, 'session_id', 'unknown')}")
            logger.debug(f"Searching for message_id: '{message_id}' (type: {type(message_id)})")
            # Don't fail if redis update fails
            self.redis_loaded = False
            
        # 2. Persist to database
        if self.chat_history_service:
            try:
                db_success = await self.chat_history_service.update_assistant_message(
                    message_id=message_id,
                    content=content,
                    analysis_id=analysis_id,
                    execution_id=execution_id,
                    metadata=metadata
                )
                return db_success
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"❌ Failed to update assistant message {message_id}: {e}")
                return False
        
        # If no chat_history_service, consider it successful (Redis-only update)
        return True
    
    async def _trim_messages(self):
        """Trim messages to context window size"""
        if not self.redis_client:
            return
            
        try:
            message_count = await self.redis_client.llen(self._redis_key)
            if message_count > self._context_window_size:
                # Remove oldest messages (from the right side of the list)
                excess_count = message_count - self._context_window_size
                for _ in range(excess_count):
                    await self.redis_client.rpop(self._redis_key)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"⚠️ Failed to trim messages: {e}")
    
    async def get_messages(self, role: Optional[str] = None, limit: Optional[int] = None) -> List[Message]:
        """Get messages with Redis health tracking fallback"""
        messages = []
        
        # Try Redis first if it's been successfully loaded
        if self.redis_loaded and self.redis_client:
            messages = await self._get_messages_from_redis()
            
        # Fallback to DB if Redis is not loaded or failed
        if not messages and not self.redis_loaded and self.chat_history_service:
            try:
                import logging
                logger = logging.getLogger(__name__)
                logger.debug(f"📄 Falling back to DB for session {self.session_id[:8]} (Redis not loaded)")
                
                db_messages = await self.chat_history_service.get_conversation_history(
                    session_id=self.session_id,
                    include_metadata=True,
                    sort_order=-1  # Descending: newest first
                )
                
                # Get only the first 20 messages (since DB returns newest first)
                latest_messages = db_messages[:self._context_window_size]
                
                # Reverse to chronological order (oldest first) for LLM context
                latest_messages.reverse()
                
                # Convert DB messages to Message objects in chronological order
                for db_msg in latest_messages:
                    role_val = db_msg.get("role", "user")
                    if role_val == "user":
                        message = UserMessage.from_dict(db_msg)
                    else:
                        message = AssistantMessage.from_dict(db_msg)
                    messages.append(message)
                    
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"❌ Failed to fallback to DB: {e}")
        
        # Apply filters
        if role:
            messages = [m for m in messages if m.role == role]
        if limit:
            messages = messages[-limit:]
            
        return messages
    
    async def get_last_user_message(self) -> Optional[UserMessage]:
        """Get most recent user message"""
        messages = await self.get_messages()
        for message in reversed(messages):
            if isinstance(message, UserMessage):
                return message
        return None
    
    async def get_last_assistant_message(self) -> Optional[AssistantMessage]:
        """Get most recent assistant message"""
        messages = await self.get_messages()
        for message in reversed(messages):
            if isinstance(message, AssistantMessage):
                return message
        return None
    
    async def get_pending_analysis_suggestion(self) -> Optional[Dict[str, Any]]:
        """Get pending analysis suggestion from most recent educational message"""
        messages = await self.get_messages()
        for i, message in enumerate(reversed(messages)):
            if (isinstance(message, AssistantMessage) and 
                message.has_analysis_suggestion()):
                
                # Check if there's been a confirmation after this suggestion
                # Note: reversed list, so later messages have smaller indices
                for later_msg in messages[len(messages) - i:]:
                    if (isinstance(later_msg, AssistantMessage) and
                        later_msg.analysis_triggered):
                        return None  # Already confirmed
                
                return message.analysis_suggestion
        return None
    
    async def add_conversation_exchange(self, 
                                      user_content: str, 
                                      assistant_content: str, 
                                      user_id: str = "anonymous",
                                      **assistant_metadata) -> Tuple[UserMessage, AssistantMessage]:
        """Convenience method to add a user message + assistant response pair"""
        user_msg = await self.add_user_message(user_content, user_id)
        assistant_msg = await self.add_assistant_message(assistant_content, user_id, **assistant_metadata)
        return user_msg, assistant_msg
    
    
    async def to_dict(self) -> dict:
        """Serialize conversation for storage"""
        messages = await self._get_messages_from_redis()
        return {
            "session_id": self.session_id,
            "messages": [msg.to_dict() for msg in messages]
        }
    
    @classmethod
    async def from_dict(cls, data: dict, redis_client=None) -> 'ConversationStore':
        """Deserialize conversation from storage"""
        store = cls(data["session_id"], redis_client=redis_client)
        
        # Load messages from the new format if available
        if "messages" in data and redis_client:
            for msg_data in data["messages"]:
                message = BaseMessage.from_dict(msg_data)
                await store._add_message_to_redis(message)
        
        return store
    
    # ========== REDIS HELPER METHODS ==========
    
    async def _add_message_to_redis(self, message: Message) -> None:
        """Add message to Redis list with health tracking"""
        import logging
        logger = logging.getLogger(__name__)
        
        if not self.redis_client:
            logger.warning(f"⚠️ Redis client is None - cannot add message {message.id}")
            return
            
        try:
            message_json = json.dumps(message.to_dict())
            await self.redis_client.lpush(self._redis_key, message_json)
            # Redis operation successful - we can trust Redis again
            self.redis_loaded = True
            logger.debug(f"✅ Message added to Redis: {message.id}")
        except Exception as e:
            logger.error(f"❌ Failed to add message to Redis: {e}", exc_info=True)
            # Redis failed - mark as unreliable
            self.redis_loaded = False
    
    async def _get_messages_from_redis(self) -> List[Message]:
        """Get all messages from Redis with health tracking
        
        Redis stores messages in lpush order (newest on left).
        We reverse to get chronological order (oldest first).
        """
        if not self.redis_client:
            return []
            
        try:
            messages_json = await self.redis_client.lrange(self._redis_key, 0, -1)
            messages = []
            for msg_json in reversed(messages_json):  # Reverse lpush order to get chronological
                msg_dict = json.loads(msg_json)
                message = BaseMessage.from_dict(msg_dict)
                messages.append(message)
            # Redis read successful - we can trust Redis
            if messages:  # Only mark as loaded if we actually got data
                self.redis_loaded = True
            return messages
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"❌ Failed to get messages from Redis: {e}")
            # Redis failed - mark as unreliable
            self.redis_loaded = False
            return []
    
    async def _update_message_in_redis(self, message_id: str, content: str = None, 
                                     analysis_id: str = None, execution_id: str = None, 
                                     **metadata) -> bool:
        """Update specific message in Redis"""
        import logging
        logger = logging.getLogger(__name__)
        
        if not self.redis_client:
            logger.warning(f"⚠️ Redis client is None - cannot update message {message_id}")
            return False
            
        try:
            messages_json = await self.redis_client.lrange(self._redis_key, 0, -1)
            logger.debug(f"🔍 Looking for message {message_id} in {len(messages_json)} messages in Redis")
            
            for i, msg_json in enumerate(messages_json):
                msg_dict = json.loads(msg_json)
                if msg_dict.get('id') == message_id:
                    logger.info(f"✅ Found message {message_id} at index {i}")
                    # Update message content and metadata
                    if content is not None:
                        msg_dict['content'] = content
                    if analysis_id is not None:
                        if 'metadata' not in msg_dict:
                            msg_dict['metadata'] = {}
                        msg_dict['metadata']['analysis_id'] = analysis_id
                    if execution_id is not None:
                        if 'metadata' not in msg_dict:
                            msg_dict['metadata'] = {}
                        msg_dict['metadata']['execution_id'] = execution_id
                    
                    # Update additional metadata
                    if 'metadata' not in msg_dict:
                        msg_dict['metadata'] = {}
                    msg_dict['metadata'].update(metadata)
                    
                    # Update timestamp
                    msg_dict['timestamp'] = datetime.now().isoformat()
                    
                    # Replace message in Redis
                    updated_json = json.dumps(msg_dict)
                    await self.redis_client.lset(self._redis_key, i, updated_json)
                    logger.info(f"✅ Updated message {message_id} in Redis")
                    return True
            
            logger.warning(f"❌ Message {message_id} not found in Redis (searched {len(messages_json)} messages)")
            return False
        except Exception as e:
            logger.error(f"❌ Failed to update message in Redis: {e}", exc_info=True)
            return False
    
    # ========== RECENT ANALYSES/EXECUTIONS CACHING ==========
    
    async def add_recent_analysis(self, analysis_data: Dict[str, Any]) -> None:
        """Add analysis/execution to recent analyses cache in Redis
        
        Args:
            analysis_data: Dictionary with analysis_id, execution_id, timestamp, question, analysis_type
        """
        if not self.redis_client:
            return
        
        try:
            analysis_json = json.dumps(analysis_data, default=str)
            # lpush adds to the left (newest first)
            await self.redis_client.lpush(self._redis_analyses_key, analysis_json)
            # Trim to keep only max_recent_analyses
            await self.redis_client.ltrim(self._redis_analyses_key, 0, self._max_recent_analyses - 1)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"❌ Failed to add recent analysis: {e}")
    
    async def get_recent_analyses(self) -> List[Dict[str, Any]]:
        """Get recent analyses from Redis cache
        
        Returns:
            List of analysis dictionaries in chronological order (oldest first)
        """
        if not self.redis_client:
            return []
        
        try:
            analyses_json = await self.redis_client.lrange(self._redis_analyses_key, 0, -1)
            analyses = []
            for analysis_json in reversed(analyses_json):  # Reverse to get chronological order
                analysis_dict = json.loads(analysis_json)
                analyses.append(analysis_dict)
            return analyses
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"❌ Failed to get recent analyses: {e}")
            return []
    
    async def clear_recent_analyses_cache(self) -> None:
        """Clear the recent analyses cache (useful when reloading from DB)"""
        if not self.redis_client:
            return
        
        try:
            await self.redis_client.delete(self._redis_analyses_key)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"❌ Failed to clear recent analyses cache: {e}")
    
    async def add_recent_execution(self, execution_data: Dict[str, Any]) -> None:
        """Add execution to recent executions cache in Redis
        
        Args:
            execution_data: Dictionary with execution_id, analysis_id, timestamp, status, question, script_name
        """
        if not self.redis_client:
            return
        
        try:
            execution_json = json.dumps(execution_data, default=str)
            # lpush adds to the left (newest first)
            await self.redis_client.lpush(self._redis_executions_key, execution_json)
            # Trim to keep only max_recent_executions
            await self.redis_client.ltrim(self._redis_executions_key, 0, self._max_recent_executions - 1)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"❌ Failed to add recent execution: {e}")
    
    async def get_recent_executions(self) -> List[Dict[str, Any]]:
        """Get recent executions from Redis cache
        
        Returns:
            List of execution dictionaries in chronological order (oldest first)
        """
        if not self.redis_client:
            return []
        
        try:
            executions_json = await self.redis_client.lrange(self._redis_executions_key, 0, -1)
            executions = []
            for execution_json in reversed(executions_json):  # Reverse to get chronological order
                execution_dict = json.loads(execution_json)
                executions.append(execution_dict)
            return executions
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"❌ Failed to get recent executions: {e}")
            return []
    
    async def clear_recent_executions_cache(self) -> None:
        """Clear the recent executions cache (useful when reloading from DB)"""
        if not self.redis_client:
            return
        
        try:
            await self.redis_client.delete(self._redis_executions_key)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"❌ Failed to clear recent executions cache: {e}")