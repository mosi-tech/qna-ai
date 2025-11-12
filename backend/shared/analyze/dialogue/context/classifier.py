#!/usr/bin/env python3
"""
Query Classifier - Detect if query is contextual or standalone
Does NOT validate completeness - that's the validator's job
"""

import logging
from typing import Optional, Dict, Any
from ..conversation.store import ConversationStore
from .service import ContextService

logger = logging.getLogger(__name__)

class QueryClassifier:
    """Classify if query is contextual or standalone (yes/no)"""
    
    def __init__(self, context_service: ContextService):
        self.context_service = context_service
    
    async def classify(self, user_query: str, conversation: Optional[ConversationStore] = None) -> Dict[str, Any]:
        """
        Detect if query is CONTEXTUAL or STANDALONE using ConversationStore
        
        CONTEXTUAL: References prior context (pronouns, phrases like "what about")
        STANDALONE: Complete query that can be understood in isolation
        
        Does NOT validate completeness - that's done by validator after expansion
        
        Args:
            user_query: The user's query to classify
            conversation: ConversationStore with conversation history
        
        Returns:
            {
                "success": True/False,
                "is_contextual": True/False,  # True if contextual, False if standalone
                "reason": "explanation",
                "error": "error message if success=False"
            }
        """
        
        try:
            # Use modernized ContextService with ConversationStore
            llm_result = await self.context_service.classify_contextual(user_query, conversation)
            
            if not llm_result["success"]:
                logger.error(f"❌ Classification failed: {llm_result.get('error')}")
                return {
                    "success": False,
                    "error": f"Classification error: {llm_result.get('error', 'Unknown error')}"
                }
            
            # LLM returns "contextual" or "standalone"
            is_contextual = llm_result.get("query_type") == "contextual"
            
            return {
                "success": True,
                "is_contextual": is_contextual,
                "reason": llm_result.get("reason", ""),
                "llm_response": llm_result.get("llm_response", "")
            }
            
        except Exception as e:
            logger.error(f"❌ Classification exception: {e}", exc_info=True)
            return {
                "success": False,
                "error": f"Classification error: {str(e)}"
            }

# Factory function to create query classifier
def create_query_classifier(context_service: ContextService) -> QueryClassifier:
    """Create query classifier with context service dependency"""
    return QueryClassifier(context_service)