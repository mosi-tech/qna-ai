#!/usr/bin/env python3
"""
Conversation Storage - Efficient conversation history management
"""

import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, asdict
from enum import Enum
from abc import ABC, abstractmethod


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
            id=str(uuid.uuid4())[:8],
            content=content,
            timestamp=datetime.now(),
            user_id=user_id,
            metadata=metadata
        )
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserMessage':
        """Create UserMessage from dictionary"""
        return cls(
            id=data.get('id', str(uuid.uuid4())[:8]),  # Generate new ID if not present
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
            id=str(uuid.uuid4())[:8],
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
            id=data.get('id', str(uuid.uuid4())[:8]),  # Generate new ID if not present
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

class QueryType(Enum):
    # Legacy analysis types (for backward compatibility)
    COMPLETE = "complete"           # Full standalone question
    CONTEXTUAL = "contextual"       # "what about QQQ to SPY"
    COMPARATIVE = "comparative"     # "how does that compare"
    PARAMETER = "parameter"         # "what if 3% instead"

class MessageIntent(Enum):
    """Message intents for hybrid chat pattern"""
    PURE_CHAT = "pure_chat"                    # General conversation
    EDUCATIONAL = "educational"                # Educational about finance
    ANALYSIS_REQUEST = "analysis_request"      # Direct analysis request
    ANALYSIS_CONFIRMATION = "analysis_confirmation"  # Confirming analysis suggestion
    FOLLOW_UP = "follow_up"                   # Follow-up to previous analysis


class ConversationStore:
    """Single source of truth for conversation data - message-based design
    
    Handles independent user and assistant messages in sequential order.
    Supports real conversation patterns like multiple user messages, missing responses, etc.
    """
    
    def __init__(self, session_id: str, chat_history_service=None):
        self.session_id = session_id
        self.messages: List[Message] = []  # Sequential independent messages (Union[UserMessage, AssistantMessage])
        self._context_window_size = 20  # Keep last 20 messages (10 exchanges)
        self.chat_history_service = chat_history_service
        
    
    @classmethod
    async def load_or_create(cls, session_id: str, chat_history_service) -> 'ConversationStore':
        """Load existing conversation from DB or create new empty one"""
        store = cls(session_id, chat_history_service)
        
        if chat_history_service:
            try:
                # Try to load existing conversation from DB
                db_messages = await chat_history_service.get_conversation_history(
                    session_id=session_id,
                    include_metadata=True  # Include metadata to preserve analysis suggestions
                )
                
                if db_messages:
                    store._populate_from_db_messages(db_messages)
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.debug(f"✓ Loaded {len(db_messages)} messages for session {session_id[:8]}...")
                
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"⚠️ Failed to load session from DB, starting fresh: {e}")
        
        return store
    
    def _populate_from_db_messages(self, db_messages: List[Dict[str, Any]]) -> None:
        """Populate both new messages list and legacy turns from DB messages"""
        if not db_messages:
            return
        
        # Clear existing data
        self.messages = []
        
        # Populate new message-based structure
        for db_msg in db_messages:
            role = db_msg.get("role", "user")
            if role == "user":
                message = UserMessage.from_dict(db_msg)
            else:
                message = AssistantMessage.from_dict(db_msg)
            self.messages.append(message)
        
    
    
    # ========== NEW MESSAGE-BASED API ==========
    
    async def add_user_message(self, content: str, user_id: str = "anonymous", **metadata) -> UserMessage:
        """Add user message - immediately persisted, independent of assistant response"""
        message = UserMessage.create(content, user_id, **metadata)
        
        # 1. Add to memory immediately  
        self.messages.append(message)
        
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
                # Continue - message preserved in memory
        
        # 3. Trim context window
        self._trim_messages()
        
        return message
    
    async def add_assistant_message(self, content: str, user_id: str = "anonymous", **metadata) -> AssistantMessage:
        """Add assistant message - independent of user message"""
        message = AssistantMessage.create(content, **metadata)
        
        # 1. Add to memory immediately
        self.messages.append(message)
        
        # 2. Persist to database
        if self.chat_history_service:
            try:
                await self.chat_history_service.add_assistant_message(
                    session_id=self.session_id,
                    user_id=user_id,
                    content=content,
                    metadata=metadata
                )
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"❌ Failed to persist assistant message: {e}")
                # Continue - message preserved in memory
        
        # 3. Trim context window
        self._trim_messages()
        
        return message
    
    def _trim_messages(self):
        """Trim messages to context window size"""
        if len(self.messages) > self._context_window_size:
            self.messages = self.messages[-self._context_window_size:]
    
    def get_messages(self, role: Optional[str] = None, limit: Optional[int] = None) -> List[Message]:
        """Get messages, optionally filtered by role"""
        messages = self.messages
        if role:
            messages = [m for m in messages if m.role == role]
        if limit:
            messages = messages[-limit:]
        return messages
    
    def get_last_user_message(self) -> Optional[UserMessage]:
        """Get most recent user message"""
        for message in reversed(self.messages):
            if isinstance(message, UserMessage):
                return message
        return None
    
    def get_last_assistant_message(self) -> Optional[AssistantMessage]:
        """Get most recent assistant message"""
        for message in reversed(self.messages):
            if isinstance(message, AssistantMessage):
                return message
        return None
    
    async def get_pending_analysis_suggestion(self) -> Optional[Dict[str, Any]]:
        """Get pending analysis suggestion from most recent educational message"""
        for message in reversed(self.messages):
            if (isinstance(message, AssistantMessage) and 
                message.has_analysis_suggestion()):
                
                # Check if there's been a confirmation after this suggestion
                message_index = self.messages.index(message)
                for later_msg in self.messages[message_index + 1:]:
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
    
    
    def to_dict(self) -> dict:
        """Serialize conversation for storage"""
        return {
            "session_id": self.session_id,
            "messages": [msg.to_dict() for msg in self.messages]
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ConversationStore':
        """Deserialize conversation from storage"""
        store = cls(data["session_id"])
        
        # Load messages from the new format if available
        if "messages" in data:
            for msg_data in data["messages"]:
                message = BaseMessage.from_dict(msg_data)
                store.messages.append(message)
        
        return store