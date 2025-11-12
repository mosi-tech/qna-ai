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
            id=data.get('id', str(uuid.uuid4())),  # Generate new ID if not present
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
            id=data.get('id', str(uuid.uuid4())),  # Generate new ID if not present
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
        self._context_window_size = 20  # Keep last 20 messages (10 exchanges)
        self.chat_history_service = chat_history_service
        
    
    @classmethod
    async def load_or_create(cls, session_id: str, chat_history_service, redis_client=None) -> 'ConversationStore':
        """Load existing conversation from Redis/DB or create new empty one"""
        store = cls(session_id, chat_history_service, redis_client)
        
        # Try to load from Redis first (faster)
        if redis_client:
            try:
                redis_messages = await redis_client.lrange(store._redis_key, 0, -1)
                if redis_messages:
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.debug(f"✓ Loaded {len(redis_messages)} messages from Redis for session {session_id[:8]}...")
                    return store
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"⚠️ Failed to load session from Redis: {e}")
        
        # Fallback to DB if Redis is empty or unavailable
        if chat_history_service:
            try:
                # Try to load existing conversation from DB
                db_messages = await chat_history_service.get_conversation_history(
                    session_id=session_id,
                    include_metadata=True  # Include metadata to preserve analysis suggestions
                )
                
                if db_messages:
                    await store._populate_from_db_messages(db_messages)
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.debug(f"✓ Loaded {len(db_messages)} messages from DB for session {session_id[:8]}...")
                
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"⚠️ Failed to load session from DB, starting fresh: {e}")
        
        return store
    
    async def _populate_from_db_messages(self, db_messages: List[Dict[str, Any]]) -> None:
        """Populate Redis from DB messages"""
        if not db_messages or not self.redis_client:
            return
        
        # Clear existing Redis data
        await self.redis_client.delete(self._redis_key)
        
        # Populate Redis from DB messages
        for db_msg in db_messages:
            role = db_msg.get("role", "user")
            if role == "user":
                message = UserMessage.from_dict(db_msg)
            else:
                message = AssistantMessage.from_dict(db_msg)
            await self._add_message_to_redis(message)
        
    
    
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
        message = AssistantMessage.create(content, **metadata)
        
        # 1. Add to Redis immediately
        await self._add_message_to_redis(message)
        
        # 2. Persist to database
        if self.chat_history_service:
            try:
                await self.chat_history_service.add_assistant_message(
                    session_id=self.session_id,
                    user_id=user_id,
                    content=content,
                    message_id=message.id,  # Pass the local ID to ensure consistency
                    metadata=metadata
                )
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"❌ Failed to persist assistant message: {e}")
                # Continue - message preserved in Redis
        
        # 3. Trim context window
        await self._trim_messages()
        
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
            return False
        
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
        """Get messages, optionally filtered by role"""
        messages = await self._get_messages_from_redis()
        if role:
            messages = [m for m in messages if m.role == role]
        if limit:
            messages = messages[-limit:]
        return messages
    
    async def get_last_user_message(self) -> Optional[UserMessage]:
        """Get most recent user message"""
        messages = await self._get_messages_from_redis()
        for message in reversed(messages):
            if isinstance(message, UserMessage):
                return message
        return None
    
    async def get_last_assistant_message(self) -> Optional[AssistantMessage]:
        """Get most recent assistant message"""
        messages = await self._get_messages_from_redis()
        for message in reversed(messages):
            if isinstance(message, AssistantMessage):
                return message
        return None
    
    async def get_pending_analysis_suggestion(self) -> Optional[Dict[str, Any]]:
        """Get pending analysis suggestion from most recent educational message"""
        messages = await self._get_messages_from_redis()
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
        """Add message to Redis list"""
        if not self.redis_client:
            return
            
        try:
            message_json = json.dumps(message.to_dict())
            await self.redis_client.lpush(self._redis_key, message_json)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"❌ Failed to add message to Redis: {e}")
    
    async def _get_messages_from_redis(self) -> List[Message]:
        """Get all messages from Redis"""
        if not self.redis_client:
            return []
            
        try:
            messages_json = await self.redis_client.lrange(self._redis_key, 0, -1)
            messages = []
            for msg_json in reversed(messages_json):  # Redis stores in reverse order (newest first)
                msg_dict = json.loads(msg_json)
                message = BaseMessage.from_dict(msg_dict)
                messages.append(message)
            return messages
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"❌ Failed to get messages from Redis: {e}")
            return []
    
    async def _update_message_in_redis(self, message_id: str, content: str = None, 
                                     analysis_id: str = None, execution_id: str = None, 
                                     **metadata) -> bool:
        """Update specific message in Redis"""
        if not self.redis_client:
            return False
            
        try:
            messages_json = await self.redis_client.lrange(self._redis_key, 0, -1)
            for i, msg_json in enumerate(messages_json):
                msg_dict = json.loads(msg_json)
                if msg_dict.get('id') == message_id:
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
                    return True
            return False
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"❌ Failed to update message in Redis: {e}")
            return False