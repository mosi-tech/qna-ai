#!/usr/bin/env python3
"""
Dialogue System - Conversation-aware financial query processing

This package provides context-aware search capabilities that can handle:
- Complete standalone queries
- Contextual queries like "what about QQQ to SPY"
- Comparative queries like "how does that compare"
- Parameter variations like "what if 3% instead"

Main components:
- ConversationStore: Session and conversation history management
- QueryClassifier: Determine query type with minimal LLM context
- ContextExpander: Expand incomplete queries using conversation history
- ContextAwareSearch: Enhanced search with context understanding

Usage:
    from dialogue.search.context_aware import search_with_context
    
    result = search_with_context(
        query="what about QQQ to SPY",
        session_id="user-session-123",
        auto_expand=True
    )
"""

from .conversation.store import ConversationStore, ConversationTurn, QueryType
from .conversation.session_manager import session_manager, get_session_manager
from .factory import (
    initialize_dialogue_factory, 
    get_dialogue_factory, 
    search_with_context
)

__version__ = "1.0.0"
__author__ = "Financial API Server"

# Main exports
__all__ = [
    # Core classes
    "ConversationStore",
    "ConversationTurn", 
    "QueryType",
    
    # Session management
    "session_manager",
    "get_session_manager",
    
    # Factory and initialization
    "initialize_dialogue_factory",
    "get_dialogue_factory",
    
    # Main search function
    "search_with_context"
]