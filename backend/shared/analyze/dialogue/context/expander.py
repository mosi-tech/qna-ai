#!/usr/bin/env python3
"""
Context Expander - Expand contextual queries using conversation history
"""

import json
import logging
import time
from typing import Optional, Dict, Any, List
from ..conversation.store import ConversationStore
from ....llm import LLMService, LLMConfig
from ....services.base_service import BaseService
from .service import ContextService
from .simplified_context_manager import SimplifiedFinancialContextManager, ContextType

logger = logging.getLogger(__name__)

class ContextExpander:
    """Expand contextual queries using SimplifiedFinancialContextManager and optionally ContextService"""
    
    def __init__(self, context_service: ContextService):
        self.context_service = context_service 
    
    async def expand_query(self, 
                          contextual_query: str, 
                          conversation: ConversationStore) -> Dict[str, Any]:
        """Expand contextual query using ContextService if available, otherwise direct LLM"""
        
        if not conversation:
            return {
                "success": False,
                "error": "No conversation available for expansion",
                "expanded_query": contextual_query,
                "confidence": 0.0
            }
        
        # Check if conversation has messages
        messages = await conversation.get_messages()
        if not messages:
            return {
                "success": False,
                "error": "No conversation history available for expansion",
                "expanded_query": contextual_query,
                "confidence": 0.0
            }
        
        # Use ContextService if available (preferred approach for consistency)
        try:
            logger.debug(f"🔄 Using ContextService for expansion")
            return await self.context_service.expand_contextual_query(contextual_query, conversation)
        except Exception as e:
            logger.error(f"❌ Query expansion exception: {e}", exc_info=True)
            return {
                "success": False,
                "error": f"Query expansion error: {str(e)}"
            }
    
# Factory function to create context expander  
def create_context_expander(context_service: Optional[ContextService] = None) -> ContextExpander:
    """Create modernized context expander with optional ContextService integration"""
    return ContextExpander(context_service=context_service) 