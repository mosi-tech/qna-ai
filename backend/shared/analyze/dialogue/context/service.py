#!/usr/bin/env python3
"""
Context Service - Modernized LLM-powered context understanding using ConversationStore and SimplifiedFinancialContextManager
"""

import logging
import time
from typing import Optional, Dict, Any
from ..conversation.store import ConversationStore
from ....llm import create_context_llm, LLMService
from .simplified_context_manager import SimplifiedFinancialContextManager, ContextType

logger = logging.getLogger(__name__)

class ContextService:
    """Modernized context understanding service using ConversationStore and SimplifiedFinancialContextManager"""
    
    def __init__(self, llm_service: Optional[LLMService] = None):
        self.context_manager = SimplifiedFinancialContextManager()
        self.llm_service = llm_service or create_context_llm()
    
    
    def _get_contextual_classification_prompt(self) -> str:
        """Get specific system prompt for contextual classification"""
        return """You are a financial query classifier. Determine if a query is CONTEXTUAL or STANDALONE.

IMPORTANT: This is ONLY about whether the query references prior conversation context.
It is NOT about whether we have the data to answer it.

CONTEXTUAL - Query references prior conversation:
- Uses pronouns referring to prior context: "it", "that", "them", "those", "this", "these"
- Uses comparison phrases: "what about", "how about", "instead", "switch to", "same strategy"
- References previous questions or discussions
- Examples: "What about QQQ?", "Same strategy with ETFs?", "How does that compare?", "What if we switch to SPY?"

STANDALONE - Query does NOT reference prior conversation:
- Can be understood completely without knowing previous questions
- Does not use context-referencing pronouns or phrases
- Even if we need to fetch data (like portfolio info), it's still standalone if it doesn't reference prior context
- Examples: "What is correlation of my portfolio with SPY", "Correlation between AAPL and SPY", "Backtest strategy buying TSLA on 5% drops"

Return only: CONTEXTUAL or STANDALONE"""

    def _get_expansion_prompt(self) -> str:
        """Get specific system prompt for query expansion"""
        return """You are a financial query expander. Your job is to expand incomplete contextual queries into complete, standalone questions that can be understood without any previous conversation context.

CRITICAL: The expanded query must be 100% SELF-CONTAINED and STANDALONE:
- DO NOT reference "previous analysis", "that analysis", "the above", "earlier results" 
- DO NOT use phrases like "like before", "same as", "compared to what we did"
- DO NOT mention charts, graphs, visualizations, or UI elements - focus on DATA ANALYSIS only
- INCLUDE ALL necessary details explicitly in the expanded query
- Make it so someone reading ONLY the expanded query can understand exactly what to do

TASK: Transform the contextual query into a complete, standalone question that includes:
- Specific assets/securities to analyze (spell out the tickers/names)
- Clear strategy or analysis to perform (be explicit about the analysis type)
- Any necessary parameters, timeframes, or conditions (include all details)
- Focus on data analysis, calculations, statistics, and numerical results
- NO references to previous questions or conversation history

EXAMPLES:
- Context: "What if I buy AAPL when it drops 2%?"
- Contextual Query: "what about QQQ instead"
- CORRECT Expanded: "What if I buy QQQ when it drops 2% from its current price?"
- WRONG: "What if I do the same strategy with QQQ instead?"

- Context: "Show correlation between SPY and VIX over last year"
- Contextual Query: "what about monthly timeframe"
- CORRECT Expanded: "Show correlation between SPY and VIX using monthly data over the last year"
- WRONG: "Show that correlation using monthly timeframe instead"

- Context: "Analyze TSLA performance during market downturns"
- Contextual Query: "how about NVDA"
- CORRECT Expanded: "Analyze NVDA performance during market downturns"
- WRONG: "Analyze NVDA performance like we did for TSLA"

RESPONSE FORMAT:
Return a JSON object with:
{
    "expanded_query": "The complete standalone question with NO references to previous context",
    "confidence": 0.0-1.0
}

Confidence should reflect how certain you are that:
- The expansion correctly interprets the user's intent
- The expanded query is completely self-contained
- Someone can understand and execute the query without knowing previous conversation"""
    
    def _initialize_service_specific(self):
        """Initialize context service specific components"""
        logger.info("✅ Context service initialized with SimplifiedFinancialContextManager")
    
    async def classify_contextual(self, current_query: str, conversation: ConversationStore = None) -> Dict[str, Any]:
        """Classify if query is CONTEXTUAL or STANDALONE using SimplifiedFinancialContextManager
        
        CONTEXTUAL: References prior context (pronouns, phrases)
        STANDALONE: Can be understood in isolation
        
        Args:
            current_query: The user's current query
            conversation: ConversationStore with conversation history
        """
        
        try:
            logger.debug(f"🔍 Classifying contextual: {current_query[:100]}...")
            
            # Get conversation messages for LLM (same pattern as intent classification)
            messages = await self.context_manager.get_conversation_messages_for_llm(
                conversation, ContextType.CONTEXTUAL_DETECTION, current_query
            )
            
            # Use LLM for classification with specific prompt
            start_time = time.time()
            
            # Use specific contextual classification prompt
            contextual_prompt = self._get_contextual_classification_prompt()
            
            response = await self.llm_service.make_request(
                messages=messages,
                max_tokens=200,
                temperature=0.1,
                system_prompt=contextual_prompt
            )
            duration = time.time() - start_time
            
            logger.debug(f"⏱️ Contextual classification: {duration:.3f}s")
            
            if not response.get("success"):
                error_msg = response.get("error", "Unknown error")
                logger.error(f"❌ Contextual classification failed: {error_msg}")
                return {"success": False, "error": f"Classification failed: {error_msg}"}
            
            # Parse response
            content = response.get("content", "").upper().strip()
            
            # Simple mapping
            if content in ["CONTEXTUAL", "C"]:
                query_type = "contextual"
            elif content in ["STANDALONE", "COMPLETE", "S", "A"]:
                query_type = "standalone"
            else:
                logger.warning(f"⚠️ Unexpected classification response: '{content}', defaulting to standalone")
                query_type = "standalone"
            
            return {
                "success": True,
                "query_type": query_type,
                "llm_response": response.get("content", ""),
                "reason": f"Query is {query_type}"
            }
            
        except Exception as e:
            logger.error(f"❌ Contextual classification error: {e}")
            return {"success": False, "error": str(e)}
    
    async def expand_contextual_query(self, contextual_query: str, conversation: ConversationStore) -> Dict[str, Any]:
        """Expand contextual query using ConversationStore and SimplifiedFinancialContextManager"""
        
        try:
            logger.debug(f"🔍 Expanding contextual query: {contextual_query[:100]}...")
            
            # Get conversation messages for LLM (same pattern as other services)
            messages = await self.context_manager.get_conversation_messages_for_llm(
                conversation, ContextType.QUERY_EXPANSION, contextual_query
            )
            
            # Use LLM for expansion with specific prompt
            start_time = time.time()
            
            # Use specific expansion prompt
            expansion_prompt = self._get_expansion_prompt()
            
            response = await self.llm_service.make_request(
                messages=messages,
                max_tokens=500,
                temperature=0.2,
                system_prompt=expansion_prompt
            )
            duration = time.time() - start_time
            
            logger.debug(f"⏱️ Context expansion: {duration:.3f}s")
            
            if not response.get("success"):
                error_msg = response.get("error", "Unknown error")
                logger.error(f"❌ Context expansion failed: {error_msg}")
                return {"success": False, "error": f"Expansion failed: {error_msg}"}
            
            # Parse expansion result (same pattern as intent classification)
            content = response.get("content", "")
            return self._parse_expansion_response(content, contextual_query)
            
        except Exception as e:
            logger.error(f"❌ Context expansion error: {e}")
            return {"success": False, "error": str(e)}
    
    def _parse_expansion_response(self, content: str, original_query: str) -> Dict[str, Any]:
        """Parse expansion response (same pattern as intent classification and context expander)"""
        
        try:
            # Try to parse JSON response
            from shared.utils.json_utils import safe_json_loads
            parsed = safe_json_loads(content, default={})
            
            if parsed and "expanded_query" in parsed:
                return {
                    "success": True,
                    "expanded_query": parsed.get("expanded_query", original_query),
                    "confidence": float(parsed.get("confidence", 0.8)),
                    "llm_response": content
                }
            else:
                # Fallback: treat whole content as expanded query
                logger.debug(f"Could not parse JSON, using content as expanded query")
                expanded_query = content.strip()
                
                # Clean up common artifacts
                if "?" in expanded_query:
                    expanded_query = expanded_query.split("?")[0] + "?"
                
                return {
                    "success": True,
                    "expanded_query": expanded_query,
                    "confidence": 0.7,
                    "llm_response": content
                }
                
        except Exception as e:
            logger.warning(f"Error parsing expansion response: {e}")
            return {
                "success": False,
                "error": f"Failed to parse expansion response: {str(e)}",
                "expanded_query": original_query,
                "confidence": 0.0
            }
    
    async def health_check(self) -> Dict[str, Any]:
        """Check if context service is available"""
        try:
            # Use the LLM service's health check
            if hasattr(self.llm_service, 'health_check'):
                llm_health = await self.llm_service.health_check()
                return {
                    "success": True,
                    "available": llm_health.get("healthy", False),
                    "provider": getattr(self.llm_service, 'provider_type', 'unknown'),
                    "model": getattr(self.llm_service, 'default_model', 'unknown'),
                    "llm_error": llm_health.get("error") if not llm_health.get("healthy") else None
                }
            else:
                return {
                    "success": True,
                    "available": True,
                    "provider": "unknown",
                    "model": "unknown"
                }
        except Exception as e:
            return {
                "success": False,
                "available": False,
                "error": str(e)
            }


# Factory function to create modernized context service
def create_context_service(llm_service: Optional[LLMService] = None) -> ContextService:
    """Create modernized context service using BaseService pattern and SimplifiedFinancialContextManager"""
    return ContextService(llm_service)

