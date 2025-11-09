#!/usr/bin/env python3
"""
Query Classifier - Detect if query is contextual or standalone
Does NOT validate completeness - that's the validator's job
"""

import logging
from typing import Optional, Dict, Any
from ..conversation.store import UserMessage, AssistantMessage
from .service import ContextService

logger = logging.getLogger(__name__)

class QueryClassifier:
    """Classify if query is contextual or standalone (yes/no)"""
    
    def __init__(self, context_service: ContextService):
        self.context_service = context_service
    
    async def classify(self, user_query: str, last_user_message: Optional[UserMessage] = None, last_assistant_message: Optional[AssistantMessage] = None) -> Dict[str, Any]:
        """
        Detect if query is CONTEXTUAL or STANDALONE
        
        CONTEXTUAL: References prior context (pronouns, phrases like "what about")
        STANDALONE: Complete query that can be understood in isolation
        
        Does NOT validate completeness - that's done by validator after expansion
        
        Returns:
            {
                "success": True/False,
                "is_contextual": True/False,  # True if contextual, False if standalone
                "reason": "explanation",
                "error": "error message if success=False"
            }
        """
        
        try:
            # Use LLM to detect contextual vs standalone
            # Provide conversation history so LLM can detect patterns (pronouns, references)
            # But LLM doesn't fill gaps - just detects if query references prior context
            llm_result = await self.context_service.classify_contextual(user_query, last_turn)
            
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