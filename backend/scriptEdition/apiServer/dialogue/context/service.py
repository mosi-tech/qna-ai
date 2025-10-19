#!/usr/bin/env python3
"""
Context Service - LLM-powered context understanding for conversation management
"""

import logging
from typing import Optional, Dict, Any
from llm import create_context_llm, LLMService

logger = logging.getLogger(__name__)

class ContextService:
    """Context understanding service using optimized LLM for context tasks"""
    
    def __init__(self, llm_service: Optional[LLMService] = None):
        # Use provided LLM service or create context-optimized LLM
        self.llm_service = llm_service or create_context_llm()
        
        # Prompts for context operations
        self._prompts = ContextPrompts()
    
    async def classify_contextual(self, current_query: str, last_turn=None) -> Dict[str, Any]:
        """Classify if query is CONTEXTUAL or STANDALONE (not about completeness)
        
        CONTEXTUAL: References prior context (pronouns, phrases)
        STANDALONE: Can be understood in isolation
        """
        
        last_query = last_turn.user_query if last_turn else None
        
        system_prompt, user_message = self._prompts.build_contextual_classification_messages(
            current_query=current_query,
            last_query=last_query
        )
        
        try:
            result = await self._make_cached_llm_call(
                system_prompt=system_prompt,
                user_message=user_message,
                max_tokens=10,
                task="contextual_classification"
            )
            
            if not result["success"]:
                return {"success": False, "error": result["error"]}
            
            response = result["content"].upper().strip()
            
            # Simple yes/no mapping
            if response in ["CONTEXTUAL", "C"]:
                query_type = "contextual"
            elif response in ["STANDALONE", "COMPLETE", "S", "A"]:
                query_type = "standalone"
            else:
                logger.error(f"❌ Invalid contextual classification response: '{response}'")
                return {
                    "success": False,
                    "error": f"Invalid response: expected CONTEXTUAL/STANDALONE, got '{response}'"
                }
            
            return {
                "success": True,
                "query_type": query_type,
                "llm_response": result["content"],
                "reason": f"Query is {query_type}"
            }
            
        except Exception as e:
            logger.error(f"Contextual classification error: {e}")
            return {"success": False, "error": str(e)}
    
    async def classify_query(self, current_query: str, last_query: Optional[str] = None) -> Dict[str, Any]:
        """Classify query type using LLM service"""
        
        system_prompt, user_message = self._prompts.build_classification_messages(
            current_query=current_query,
            last_query=last_query
        )
        
        try:
            result = await self._make_cached_llm_call(
                system_prompt=system_prompt,
                user_message=user_message,
                max_tokens=1000,
                task="query_classification"
            )
            
            if not result["success"]:
                return {"success": False, "error": result["error"]}
            
            response = result["content"].upper().strip()
            
            # Parse response
            query_type_mapping = {
                "A": "complete",
                "B": "contextual", 
                "C": "comparative",
                "D": "parameter",
                "COMPLETE": "complete",
                "CONTEXTUAL": "contextual",
                "COMPARATIVE": "comparative", 
                "PARAMETER": "parameter"
            }
            
            # Require valid mapping - don't silently default
            if response not in query_type_mapping:
                logger.error(f"❌ LLM returned unmapped query type: '{response}'")
                logger.error(f"   Expected one of: {list(query_type_mapping.keys())}")
                logger.error(f"   Full LLM response: '{result['content']}'")
                return {
                    "success": False,
                    "error": f"Invalid LLM response: '{response}'. Expected one of: {list(query_type_mapping.keys())}"
                }
            
            query_type = query_type_mapping[response]
            
            return {
                "success": True,
                "query_type": query_type,
                "llm_response": result["content"],
                "confidence": 0.9
            }
            
        except Exception as e:
            logger.error(f"Query classification error: {e}")
            return {"success": False, "error": str(e)}
    
    async def expand_contextual_query(self, contextual_query: str, conversation_context: str) -> Dict[str, Any]:
        """Expand contextual query using actual conversation history"""
        
        system_prompt, user_message = self._prompts.build_expansion_messages_with_context(
            contextual_query=contextual_query,
            conversation_context=conversation_context
        )
        
        try:
            result = await self._make_cached_llm_call(
                system_prompt=system_prompt,
                user_message=user_message,
                max_tokens=200,
                task="context_expansion"
            )
            
            if not result["success"]:
                return {"success": False, "error": result["error"]}
            
            # Clean up response - should be a complete question
            expanded_query = result["content"].strip()
            
            # Remove any extra text before/after the question
            if "?" in expanded_query:
                expanded_query = expanded_query.split("?")[0] + "?"
            
            return {
                "success": True,
                "expanded_query": expanded_query,
                "llm_response": result["content"],
                "context_used": conversation_context
            }
            
        except Exception as e:
            logger.error(f"Context expansion error: {e}")
            return {"success": False, "error": str(e)}
    
    
    async def _make_cached_llm_call(self, system_prompt: str, user_message: str, max_tokens: int, task: str) -> Dict[str, Any]:
        """Make a cached LLM call using separate system prompt and user message for better caching"""
        
        try:
            # Use separate system prompt and user message for optimal caching
            messages = [{"role": "user", "content": user_message}]
            
            response = await self.llm_service.make_request(
                messages=messages,
                system_prompt=system_prompt,
                max_tokens=max_tokens,
                temperature=0.1,  # Low temperature for consistent results
                force_api=True    # Force API usage for context search (no CLI needed)
            )
            
            if response.get("success"):
                return {
                    "success": True,
                    "content": response.get("content", "").strip(),
                    "task": task
                }
            else:
                return {
                    "success": False,
                    "error": response.get("error", "LLM request failed")
                }
                
        except Exception as e:
            logger.error(f"Cached LLM call error ({task}): {e}")
            return {
                "success": False,
                "error": f"LLM service error: {str(e)}"
            }
    
    async def health_check(self) -> Dict[str, Any]:
        """Check if context service is available"""
        try:
            # Use the LLM service's health check
            llm_health = await self.llm_service.health_check()
            
            return {
                "success": True,
                "available": llm_health.get("healthy", False),
                "provider": self.llm_service.provider_type,
                "model": self.llm_service.default_model,
                "llm_error": llm_health.get("error") if not llm_health.get("healthy") else None
            }
            
        except Exception as e:
            return {
                "success": False,
                "available": False,
                "error": str(e)
            }


class ContextPrompts:
    """Optimized prompts for context understanding tasks with separate system/user messages for caching"""
    
    def build_contextual_classification_messages(self, current_query: str, last_query: Optional[str] = None) -> tuple[str, str]:
        """Build messages to classify if query is CONTEXTUAL or STANDALONE
        
        CONTEXTUAL: References prior context (pronouns, phrases)
        STANDALONE: Can be understood in isolation
        
        Does NOT validate completeness - only detects if query needs prior context
        """
        
        system_prompt = """You are a financial query classifier. Determine if a query is CONTEXTUAL or STANDALONE.

CONTEXTUAL - Query references prior context:
- Uses pronouns: "it", "that", "them", "those"
- Uses phrases: "what about", "how about", "instead", "switch to", "same strategy"
- Cannot be answered without knowing the previous question
- Examples: "What about QQQ?", "Same strategy with ETFs?", "How does that compare?"

STANDALONE - Query is complete on its own:
- Specifies all necessary information
- Can be understood in isolation
- No references to prior context
- Examples: "Correlation between AAPL and SPY", "Backtest strategy buying TSLA on 5% drops"

Return only: CONTEXTUAL or STANDALONE"""
        
        if last_query:
            user_message = f"""Previous question: "{last_query}"
Current question: "{current_query}"

Is the current question CONTEXTUAL or STANDALONE?"""
        else:
            user_message = f"""Question: "{current_query}"

This is the first question. Is it CONTEXTUAL or STANDALONE?"""
        
        return system_prompt, user_message
    
    def build_classification_messages(self, current_query: str, last_query: Optional[str] = None) -> tuple[str, str]:
        """Build classification system prompt and user message for optimal caching"""
        
        if last_query:
            system_prompt = """You are a financial query classifier. Your job is to classify user inputs based on their relationship to previous context.

ASSUMPTIONS:
- Assume market data and APIs are available for analysis
- Assume basic financial knowledge (assets, strategies, indicators)
- Focus on whether the query is self-contained or references previous context

Classification options:
A) COMPLETE - standalone question with all context (e.g., "What happens if I buy AAPL when it drops 2%?")
B) CONTEXTUAL - refers to previous context (e.g., "what about QQQ to SPY", "same strategy with different assets")
C) COMPARATIVE - comparing to previous (e.g., "how does that compare to...", "what's the difference")
D) PARAMETER - changing numbers/parameters (e.g., "what if 3% instead", "try 5% threshold")

Return only: A, B, C, or D"""
            
            user_message = f"""Previous question: "{last_query}"
Current input: "{current_query}"

Classify the current input:"""
        else:
            # First query in session - must be complete
            system_prompt = """You are a financial query classifier for first-time queries in a conversation.

ASSUMPTIONS:
- Assume market data and trading APIs are available
- Assume access to historical price data, technical indicators, and fundamental data
- Assume ability to perform backtesting and strategy analysis
- Focus on whether the standalone query contains sufficient information

A query is COMPLETE if it specifies:
- What assets/securities to analyze
- What strategy or analysis to perform
- Any necessary parameters or conditions

Examples of COMPLETE queries:
- "What if I buy QQQ into VOO every month when rolling monthly return goes below -2%?"
- "Show me correlation between AAPL and SPY over the last year"
- "Backtest a strategy buying TSLA on 5% drops"

Examples of INCOMPLETE queries:
- "What about the correlation?" (no assets specified)
- "Can you analyze this?" (no strategy specified)
- "What if 3% instead?" (no context about what strategy)

This is the first query in the conversation. Classify as:
A) COMPLETE - has enough context to answer
B) INCOMPLETE - needs more information

Return only: A or B"""
            
            user_message = f"""User input: "{current_query}"

Classify this query:"""
        
        return system_prompt, user_message


    def build_expansion_messages_with_context(self, contextual_query: str, conversation_context: str) -> tuple[str, str]:
        """Build expansion system prompt and user message using conversation history for optimal caching"""
        
        system_prompt = """You are a financial query expander. Your job is to expand incomplete contextual queries into complete, standalone questions using conversation history.

ASSUMPTIONS:
- Assume market data and trading APIs are available
- Assume all mentioned assets are tradeable
- Use conversation context to understand what the user is referring to

TASK: Transform the contextual query into a complete, standalone question that includes:
- Specific assets/securities to analyze
- Clear strategy or analysis to perform  
- Any necessary parameters or conditions
- Context from previous conversation

EXAMPLES:
- Context: "What if I buy AAPL when it drops 2%?"
- Contextual Query: "what about QQQ instead"
- Expanded: "What if I buy QQQ when it drops 2%?"

- Context: "Show correlation between SPY and VIX over last year"
- Contextual Query: "what about monthly timeframe"
- Expanded: "Show correlation between SPY and VIX over last year using monthly data"

Return only the complete expanded question, nothing else."""
        
        user_message = f"""CONVERSATION CONTEXT:
{conversation_context}

CONTEXTUAL QUERY: "{contextual_query}"

Expand this into a complete question:"""
        
        return system_prompt, user_message



# Factory function to create context service with shared LLM service
def create_context_service(llm_service: Optional[LLMService] = None) -> ContextService:
    """Create context service with shared or dedicated LLM service"""
    return ContextService(llm_service)

