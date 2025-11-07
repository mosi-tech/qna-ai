#!/usr/bin/env python3
"""
Conversation Storage - Efficient conversation history management
"""

import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum

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

@dataclass
class ConversationTurn:
    """Single conversation exchange - updated for hybrid chat pattern"""
    id: str
    timestamp: datetime
    user_query: str                 # Original user input
    
    # Hybrid message fields (new)
    message_intent: Optional[MessageIntent]     # Intent classification for hybrid chat
    response_type: Optional[str]                # Response type (chat, educational_chat, etc.)
    assistant_response: Optional[str]           # Assistant's response content
    triggered_analysis: bool = False            # Whether this triggered an analysis
    
    # Legacy analysis fields (for backward compatibility)
    query_type: Optional[QueryType] = None
    expanded_query: Optional[str] = None        # LLM-expanded query if contextual
    analysis_summary: Optional[str] = None      # Brief summary of analysis found
    context_used: bool = False
    expansion_confidence: float = 0.0

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        result = asdict(self)
        result['timestamp'] = self.timestamp.isoformat()
        
        # Handle enum serialization
        if self.message_intent:
            result['message_intent'] = self.message_intent.value
        if self.query_type:
            result['query_type'] = self.query_type.value
        
        return result

    @classmethod
    def from_dict(cls, data: dict) -> 'ConversationTurn':
        """Create from dictionary"""
        data = data.copy()  # Avoid mutating original
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        
        # Handle enum deserialization
        if data.get('message_intent'):
            data['message_intent'] = MessageIntent(data['message_intent'])
        if data.get('query_type'):
            data['query_type'] = QueryType(data['query_type'])
            
        return cls(**data)

class ConversationStore:
    """Interface to conversation data stored in MongoDB/Redis"""
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.turns: List[ConversationTurn] = []
        self._context_window_size = 10  # Keep last 10 turns max
    
    def _populate_from_messages(self, db_messages: List[Dict[str, Any]]) -> None:
        """Populate turns from MongoDB messages
        
        Converts MongoDB messages to ConversationTurn objects
        Pairs user messages with their assistant responses
        """
        if not db_messages:
            return
        
        i = 0
        while i < len(db_messages):
            msg = db_messages[i]
            role = msg.get("role", "user")
            
            if role == "user":
                question = msg.get("content", "")
                analysis_summary = None
                
                # Look ahead for assistant response
                if i + 1 < len(db_messages):
                    next_msg = db_messages[i + 1]
                    if next_msg.get("role") == "assistant":
                        analysis_summary = next_msg.get("content", "")[:100]
                
                self.add_turn(
                    user_query=question,
                    query_type=QueryType.COMPLETE,
                    analysis_summary=analysis_summary,
                    context_used=False
                )
            
            i += 1
    
    def add_turn(self, 
                 user_query: str,
                 # New hybrid fields
                 message_intent: Optional[MessageIntent] = None,
                 response_type: Optional[str] = None,
                 assistant_response: Optional[str] = None,
                 triggered_analysis: bool = False,
                 # Legacy fields (for backward compatibility)
                 query_type: Optional[QueryType] = None,
                 expanded_query: Optional[str] = None,
                 analysis_summary: Optional[str] = None,
                 context_used: bool = False,
                 expansion_confidence: float = 0.0) -> ConversationTurn:
        """Add new conversation turn"""
        
        turn = ConversationTurn(
            id=str(uuid.uuid4())[:8],
            timestamp=datetime.now(),
            user_query=user_query,
            # New hybrid fields
            message_intent=message_intent,
            response_type=response_type,
            assistant_response=assistant_response,
            triggered_analysis=triggered_analysis,
            # Legacy fields
            query_type=query_type,
            expanded_query=expanded_query,
            analysis_summary=analysis_summary,
            context_used=context_used,
            expansion_confidence=expansion_confidence
        )
        
        self.turns.append(turn)
        
        # Trim to context window
        if len(self.turns) > self._context_window_size:
            self.turns = self.turns[-self._context_window_size:]
        
        return turn
    
    def add_hybrid_turn(self, 
                       user_query: str,
                       message_intent: MessageIntent,
                       response_type: str,
                       assistant_response: str,
                       triggered_analysis: bool = False) -> ConversationTurn:
        """Convenience method for adding hybrid chat turns"""
        return self.add_turn(
            user_query=user_query,
            message_intent=message_intent,
            response_type=response_type,
            assistant_response=assistant_response,
            triggered_analysis=triggered_analysis
        )
    
    def get_last_turn(self) -> Optional[ConversationTurn]:
        """Get most recent conversation turn"""
        return self.turns[-1] if self.turns else None
    
    def get_last_complete_turn(self) -> Optional[ConversationTurn]:
        """Find most recent turn with complete query (not contextual) - legacy method"""
        for turn in reversed(self.turns):
            if (turn.query_type == QueryType.COMPLETE and 
                turn.analysis_summary and 
                not turn.context_used):
                return turn
        return None
    
    def get_last_analysis_turn(self) -> Optional[ConversationTurn]:
        """Find most recent turn that triggered analysis (hybrid pattern)"""
        for turn in reversed(self.turns):
            if turn.triggered_analysis or turn.analysis_summary:
                return turn
        return None
    
    def get_last_educational_turn(self) -> Optional[ConversationTurn]:
        """Find most recent educational chat turn"""
        for turn in reversed(self.turns):
            if turn.message_intent == MessageIntent.EDUCATIONAL:
                return turn
        return None
    
    def get_recent_chat_history(self, max_turns: int = 5) -> List[Dict[str, str]]:
        """Get recent chat history formatted for LLM context"""
        history = []
        for turn in self.turns[-max_turns:]:
            # Add user message
            history.append({
                "role": "user",
                "content": turn.user_query
            })
            # Add assistant response if available
            if turn.assistant_response:
                history.append({
                    "role": "assistant", 
                    "content": turn.assistant_response
                })
        return history
    
    def get_context_summary(self) -> dict:
        """Get minimal context summary for LLM - updated for hybrid chat pattern"""
        last_turn = self.get_last_turn()
        last_analysis_turn = self.get_last_analysis_turn()
        last_educational_turn = self.get_last_educational_turn()
        
        return {
            "has_history": len(self.turns) > 0,
            "last_query": last_turn.user_query if last_turn else None,
            "last_message_intent": last_turn.message_intent.value if last_turn and last_turn.message_intent else None,
            "last_response_type": last_turn.response_type if last_turn else None,
            "last_assistant_response": last_turn.assistant_response[:200] if last_turn and last_turn.assistant_response else None,
            "last_analysis": last_analysis_turn.analysis_summary if last_analysis_turn else None,
            "last_educational_topic": last_educational_turn.assistant_response[:100] if last_educational_turn else None,
            "recent_analysis_triggered": any(turn.triggered_analysis for turn in self.turns[-3:]) if self.turns else False,
            "turn_count": len(self.turns),
            
            # Legacy fields for backward compatibility
            "last_query_type": last_turn.query_type.value if last_turn and last_turn.query_type else None
        }
    
    def to_dict(self) -> dict:
        """Serialize conversation for storage"""
        return {
            "session_id": self.session_id,
            "turns": [turn.to_dict() for turn in self.turns]
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ConversationStore':
        """Deserialize conversation from storage"""
        store = cls(data["session_id"])
        store.turns = [ConversationTurn.from_dict(turn_data) for turn_data in data["turns"]]
        return store