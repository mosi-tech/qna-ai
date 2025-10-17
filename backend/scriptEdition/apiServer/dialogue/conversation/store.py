#!/usr/bin/env python3
"""
Conversation Storage - Efficient conversation history management
"""

import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum

class QueryType(Enum):
    COMPLETE = "complete"           # Full standalone question
    CONTEXTUAL = "contextual"       # "what about QQQ to SPY"
    COMPARATIVE = "comparative"     # "how does that compare"
    PARAMETER = "parameter"         # "what if 3% instead"

@dataclass
class ConversationTurn:
    """Single conversation exchange - simplified for conversation context"""
    id: str
    timestamp: datetime
    user_query: str                 # Original user input
    query_type: QueryType
    expanded_query: Optional[str]   # LLM-expanded query if contextual
    analysis_summary: Optional[str] # Brief summary of analysis found (e.g., "AAPL volatility analysis")
    context_used: bool
    expansion_confidence: float = 0.0

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        result = asdict(self)
        result['timestamp'] = self.timestamp.isoformat()
        result['query_type'] = self.query_type.value
        return result

    @classmethod
    def from_dict(cls, data: dict) -> 'ConversationTurn':
        """Create from dictionary"""
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        data['query_type'] = QueryType(data['query_type'])
        return cls(**data)

class ConversationStore:
    """Store conversation history for a session"""
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.created_at = datetime.now()
        self.last_activity = datetime.now()
        self.turns: List[ConversationTurn] = []
        self._context_window_size = 10  # Keep last 10 turns max
    
    def add_turn(self, 
                 user_query: str,
                 query_type: QueryType,
                 expanded_query: Optional[str] = None,
                 analysis_summary: Optional[str] = None,
                 context_used: bool = False,
                 expansion_confidence: float = 0.0) -> ConversationTurn:
        """Add new conversation turn"""
        
        turn = ConversationTurn(
            id=str(uuid.uuid4())[:8],
            timestamp=datetime.now(),
            user_query=user_query,
            query_type=query_type,
            expanded_query=expanded_query,
            analysis_summary=analysis_summary,
            context_used=context_used,
            expansion_confidence=expansion_confidence
        )
        
        self.turns.append(turn)
        self.last_activity = datetime.now()
        
        # Trim to context window
        if len(self.turns) > self._context_window_size:
            self.turns = self.turns[-self._context_window_size:]
        
        return turn
    
    def get_last_turn(self) -> Optional[ConversationTurn]:
        """Get most recent conversation turn"""
        return self.turns[-1] if self.turns else None
    
    def get_last_complete_turn(self) -> Optional[ConversationTurn]:
        """Find most recent turn with complete query (not contextual)"""
        for turn in reversed(self.turns):
            if (turn.query_type == QueryType.COMPLETE and 
                turn.analysis_summary and 
                not turn.context_used):
                return turn
        return None
    
    def is_expired(self, timeout_minutes: int = 30) -> bool:
        """Check if conversation is expired"""
        return datetime.now() - self.last_activity > timedelta(minutes=timeout_minutes)
    
    def get_context_summary(self) -> dict:
        """Get minimal context summary for LLM"""
        last_turn = self.get_last_turn()
        last_complete_turn = self.get_last_complete_turn()
        
        return {
            "has_history": len(self.turns) > 0,
            "last_query": last_turn.user_query if last_turn else None,
            "last_query_type": last_turn.query_type.value if last_turn else None,
            "last_analysis": last_complete_turn.analysis_summary if last_complete_turn else None,
            "turn_count": len(self.turns)
        }
    
    def to_dict(self) -> dict:
        """Serialize conversation for storage"""
        return {
            "session_id": self.session_id,
            "created_at": self.created_at.isoformat(),
            "last_activity": self.last_activity.isoformat(),
            "turns": [turn.to_dict() for turn in self.turns]
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ConversationStore':
        """Deserialize conversation from storage"""
        store = cls(data["session_id"])
        store.created_at = datetime.fromisoformat(data["created_at"])
        store.last_activity = datetime.fromisoformat(data["last_activity"])
        store.turns = [ConversationTurn.from_dict(turn_data) for turn_data in data["turns"]]
        return store