#!/usr/bin/env python3
"""
Context-Aware Search - Enhanced search with conversation context

Flow:
1. Classify: Is query CONTEXTUAL or STANDALONE?
2. If CONTEXTUAL: Expand using history → validate → search
3. If STANDALONE: Validate → search
"""

import logging
from typing import Optional, Dict, Any, List
from search.library import AnalysisLibrary
from ..conversation.store import ConversationStore, ConversationTurn
from ..conversation.session_manager import SessionManager
from ..context.classifier import QueryClassifier
from ..context.expander import ContextExpander
from ..context.validator import CompletenessValidator
from services.progress_service import (
    progress_manager,
    progress_info,
    progress_success,
    progress_warning,
)

logger = logging.getLogger(__name__)

class ContextAwareSearch:
    """Enhanced search that handles conversation context"""
    
    def __init__(self, 
                 analysis_library: AnalysisLibrary = None,
                 session_manager: SessionManager = None,
                 classifier: QueryClassifier = None,
                 expander: ContextExpander = None,
                 validator: CompletenessValidator = None):
        self.analysis_library = analysis_library or AnalysisLibrary()
        self.session_manager = session_manager
        self.classifier = classifier
        self.expander = expander
        self.validator = validator or CompletenessValidator()
        
        self.default_similarity_threshold = 0.3
    
    async def search_with_context(self, 
                                 query: str, 
                                 session_id: Optional[str] = None,
                                 auto_expand: bool = True,
                                 similarity_threshold: float = None):
        """Main entry point for context-aware search
        
        Flow:
        1. CLASSIFY: Detect if CONTEXTUAL or STANDALONE
        2. If CONTEXTUAL: EXPAND → VALIDATE → SEARCH
        3. If STANDALONE: VALIDATE → SEARCH
        
        Args:
            query: User's question/query
            session_id: Optional session ID
            auto_expand: Whether to auto-expand contextual queries
            similarity_threshold: Custom similarity threshold for search
        """
        
        similarity_threshold = similarity_threshold or self.default_similarity_threshold
        
        # Get conversation from session or create new one
        if self.session_manager and session_id:
            conversation = await self.session_manager.get_session(session_id)
            if not conversation:
                conversation = ConversationStore(session_id)
        else:
            # Create a temporary session_id for this conversation
            import uuid
            temp_session_id = str(uuid.uuid4())
            conversation = ConversationStore(temp_session_id)
        
        # Step 1: CLASSIFY - Is this query CONTEXTUAL or STANDALONE?
        classification = await self._classify_contextual(query, conversation)
        
        if not classification["success"]:
            return self._error_response("Unable to understand your query", classification)
        
        is_contextual = classification["is_contextual"]
        final_query = query
        
        # Step 2: EXPAND (if contextual) - Make query explicit using context
        expansion_confidence = 0.9  # Default high confidence for standalone
        
        if is_contextual:
            logger.info(f"Query is contextual, expanding with context...")
            expansion = await self._expand_query(query, conversation)
            
            if not expansion["success"]:
                return self._error_response("Unable to understand your question in context", expansion)
            
            final_query = expansion.get("expanded_query", query)
            expansion_confidence = expansion.get("confidence", 0.9)
            logger.info(f"Expanded query: {final_query[:100]}... (confidence: {expansion_confidence})")
            
            # If low confidence on expansion, ask for clarification
            if expansion_confidence < 0.7:
                logger.info(f"Low expansion confidence ({expansion_confidence}), requesting clarification")
                return self._request_clarification(
                    original_query=query,
                    expanded_query=final_query,
                    confidence=expansion_confidence,
                    session_id=session_id,
                    reason="I'm not confident about my interpretation"
                )
            
            # Step 2.5: Check if expansion is meaningless (e.g., "Why?" → "Why?")
            if await self._is_meaningless_expansion(query, final_query):
                logger.info(f"Expansion is meaningless ('{query}' → '{final_query}'), skipping clarification")
                return {
                    "success": True,
                    "is_meaningless": True,
                    "session_id": session_id,
                    "original_query": query,
                    "expanded_query": final_query,
                    "message": "I don't understand your request. I need more details to help you. Please tell me what you'd like to analyze.",
                    "type": "meaningless_query"
                }
        else:
            # For standalone queries, also check if they're meaningless
            logger.info(f"🔹 Query is STANDALONE, checking if meaningless...")
            is_meaningless = await self._is_meaningless_query(query)
            logger.info(f"🔹 Meaningless check result: {is_meaningless}")
            if is_meaningless:
                logger.info(f"✅ Standalone query is meaningless: '{query}'")
                return {
                    "success": True,
                    "is_meaningless": True,
                    "session_id": session_id,
                    "original_query": query,
                    "expanded_query": query,
                    "message": "I don't understand your request. I need more details to help you. Please tell me what you'd like to analyze.",
                    "type": "meaningless_query"
                }
            logger.info(f"🔹 Query is not meaningless, proceeding to validation")
        
        # Step 3: VALIDATE - Check if query is complete
        await progress_info(session_id, "Checking question for completeness...")
        validation = self.validator.validate(final_query)
        
        if not validation["complete"]:
            missing = ", ".join(validation["missing"])
            logger.info(f"Validation failed, missing: {missing}")
            return self._request_clarification(
                original_query=query,
                expanded_query=final_query,
                confidence=expansion_confidence,
                session_id=session_id,
                reason=f"Missing information: {missing}"
            )
        
        # Step 4: SEARCH - Query is ready
        logger.info(f"Query validated, proceeding with search: {final_query[:100]}...")
        
        # Search for similar analyses
        search_result = self.analysis_library.search_similar(
            query=final_query,
            top_k=5,
            similarity_threshold=similarity_threshold
        )
        
        if not search_result["success"]:
            return self._error_response("Search failed", search_result)
        
        return {
            "success": True,
            "session_id": session_id,
            "query_type": "contextual" if is_contextual else "standalone",
            "original_query": query,
            "final_query": final_query,
            "search_results": search_result.get("analyses", []),
            "found_similar": search_result.get("found_similar", False)
        }
    
    async def _classify_contextual(self, query: str, conversation: ConversationStore) -> Dict[str, Any]:
        """Classify if query is CONTEXTUAL or STANDALONE"""
        
        try:
            last_turn = conversation.get_last_turn()
            result = await self.classifier.classify(query, last_turn)
            
            if result["success"]:
                query_type = "contextual" if result["is_contextual"] else "standalone"
                logger.info(f"Query classified as {query_type}")
            else:
                logger.warning(f"Classification failed: {result.get('error')}")
            
            return result
        except Exception as e:
            logger.error(f"Classification exception: {e}", exc_info=True)
            return {
                "success": False,
                "error": "Unable to classify your query"
            }
    
    async def _expand_query(self, query: str, conversation: ConversationStore) -> Dict[str, Any]:
        """Expand contextual query using conversation history"""
        
        try:
            # Get conversation context as string
            context_str = self._format_conversation_context(conversation)
            
            result = await self.expander.expand_query(query, context_str)
            
            if result["success"]:
                logger.info(f"Query expanded to: {result['expanded_query'][:100]}...")
            else:
                logger.warning(f"Expansion failed: {result.get('error')}")
            
            return result
        except Exception as e:
            logger.error(f"Expansion exception: {e}", exc_info=True)
            return {
                "success": False,
                "error": "Unable to expand your query with context"
            }
    
    async def _is_meaningless_expansion(self, original: str, expanded: str) -> bool:
        """Check if expansion is meaningless using validator + LLM judgment"""
        original_clean = original.lower().strip()
        expanded_clean = expanded.lower().strip()
        
        # Quick check: if expansion is the same as original
        if original_clean == expanded_clean:
            logger.info(f"Expansion unchanged: '{original}' → '{expanded}'")
            return True
        
        # Check if expanded query has meaningful content (assets or analysis type)
        validation = self.validator.validate(expanded)
        
        # If missing both assets AND analysis type, likely meaningless
        if not validation["complete"] and len(validation["missing"]) == 2:
            logger.info(f"Expansion missing both assets and analysis: '{expanded}'")
            # Use LLM to confirm it's actually meaningless
            return await self._llm_check_meaningless(original, expanded)
        
        return False
    
    async def _is_meaningless_query(self, query: str) -> bool:
        """Check if a standalone query is meaningless using LLM judgment"""
        logger.info(f"🔍 Checking if standalone query is meaningless: '{query}'")
        
        # Quick check: very short generic questions that are obviously meaningless
        query_lower = query.lower().strip()
        quick_meaningless = ["why?", "what?", "how?", "when?", "where?", "who?", "huh?", "ok?", "sure?"]
        if query_lower in quick_meaningless:
            logger.info(f"⚡ Quick match: '{query}' is obviously meaningless")
            return True
        
        try:
            from dialogue.context.service import ContextService
            context_service = ContextService()
            
            system_prompt = """You are a financial query analyzer. Determine if a standalone query is meaningless, absurd, or not a valid financial analysis query.
Respond with only YES or NO.

CRITERIA for meaningless/invalid:
1. Too generic without financial context (e.g., "What?", "Why?", "Tell me", "How?")
2. Single word or vague phrases without specific metrics/assets (e.g., "stocks", "volatility", "correlation")
3. Not related to financial analysis (e.g., "What is the weather?", "How to cook?", "Tell me a story")
4. Nonsensical or empty queries

CRITERIA for valid/meaningful:
- Has specific financial assets (e.g., "AAPL", "SPY", "portfolio") or clear metrics
- Contains actionable financial terms (e.g., "analyze", "backtest", "compare", "calculate")
- References specific analysis types (volatility, correlation, returns, strategy, etc.)
- Requests actionable financial information

Examples:
- "Why?" → YES (meaningless, too generic)
- "What?" → YES (meaningless, vague generic question)
- "Stocks" → YES (meaningless, too vague without context)
- "volatility" → YES (meaningless, generic term without assets)
- "Check weather" → YES (not financial at all)
- "What is AAPL?" → NO (valid, has specific asset)
- "Correlation with SPY" → NO (valid, has asset + metric)
- "Volatility of Bitcoin" → NO (valid, has asset + metric)
- "Backtest buy strategy" → NO (valid, has strategy reference)
- "My portfolio performance" → NO (valid, has portfolio reference)"""
            
            user_message = f"""Query: "{query}"

Is this a meaningless or non-financial query that shouldn't be analyzed?"""
            
            logger.info(f"📞 Calling LLM for meaningless query check")
            result = await context_service._make_cached_llm_call(
                system_prompt=system_prompt,
                user_message=user_message,
                max_tokens=1000,
                task="meaningless_query_check"
            )
            
            if result["success"]:
                response = result["content"].upper().strip()
                is_meaningless = response.startswith("YES")
                logger.info(f"✅ LLM meaningless query check: '{query}' → {response} (meaningless={is_meaningless})")
                return is_meaningless
            else:
                logger.warning(f"❌ LLM call failed: {result}")
                return False
            
        except Exception as e:
            logger.warning(f"⚠️ LLM meaningless query check failed: {e}, trying quick fallback", exc_info=True)
            # Fallback: check if it's a very short generic question
            if len(query_lower) <= 6 and query_lower.endswith("?"):
                logger.info(f"⚡ Fallback: '{query}' looks like generic question")
                return True
            return False
    
    async def _llm_check_meaningless(self, original: str, expanded: str) -> bool:
        """Use LLM to determine if an expansion is meaningless/absurd"""
        try:
            from dialogue.context.service import ContextService
            context_service = ContextService()
            
            system_prompt = """You are a financial query analyzer. Determine if an expanded query is meaningless, absurd, or not a valid financial analysis query.
Respond with only YES or NO.

CRITERIA for meaningless/invalid:
1. Same as original (no expansion happened)
2. Generic question without financial context (e.g., "What?", "Why?", "Tell me")
3. Not related to financial analysis (e.g., "What is the weather?", "How to cook?")
4. Vague without specific assets, strategies, or metrics (e.g., "Tell me about stocks")

CRITERIA for valid/meaningful:
- Has specific financial assets (stocks, ETFs, crypto, etc.) or portfolio context
- References specific analysis (correlation, volatility, returns, strategy, backtest, etc.)
- Requests actionable financial information

Examples:
- Original: "Why?" Expanded: "Why?" → YES (meaningless, same + generic)
- Original: "What?" Expanded: "What?" → YES (meaningless, vague generic question)
- Original: "Check weather" Expanded: "Check weather today" → YES (not financial)
- Original: "Correlation" Expanded: "Correlation of AAPL with SPY" → NO (valid, has assets + metric)
- Original: "volatility" Expanded: "What is the volatility of Bitcoin?" → NO (valid, has asset + metric)
- Original: "Strategy" Expanded: "Backtest buy TSLA on 5% drop" → NO (valid, has asset + strategy)"""
            
            user_message = f"""Original: "{original}"
Expanded: "{expanded}"

Is this expansion meaningless or not a valid financial analysis query?"""
            
            result = await context_service._make_cached_llm_call(
                system_prompt=system_prompt,
                user_message=user_message,
                max_tokens=10,
                task="meaningless_check"
            )
            
            if result["success"]:
                response = result["content"].upper().strip()
                is_meaningless = response.startswith("YES")
                logger.info(f"LLM meaningless check: '{expanded}' → {response}")
                return is_meaningless
            
            return False
            
        except Exception as e:
            logger.warning(f"LLM meaningless check failed: {e}, using validator result")
            return True  # Default to True if LLM check fails
    
    def _format_conversation_context(self, conversation: ConversationStore) -> str:
        """Format conversation history as string context"""
        
        turns = conversation.turns[-5:]  # Last 5 turns for context
        context_lines = []
        
        for turn in turns:
            context_lines.append(f"Q: {turn.user_query}")
            if turn.expanded_query and turn.expanded_query != turn.user_query:
                context_lines.append(f"(expanded to: {turn.expanded_query})")
        
        return "\n".join(context_lines)
    
    def _request_clarification(self, 
                             original_query: str, 
                             expanded_query: str, 
                             confidence: float, 
                             session_id: str,
                             reason: str = None) -> Dict[str, Any]:
        """Request clarification for low-confidence expansion or incomplete query"""
        
        if reason is None:
            reason = "I'm not sure how to interpret your question"
        
        # Check if query was expanded (original != expanded) or just needs more info
        was_expanded = original_query.strip() != expanded_query.strip()
        
        if was_expanded:
            message = f"{reason}. Did you mean: '{expanded_query}'?"
        else:
            message = reason
        
        return {
            "success": True,
            "needs_clarification": True,
            "session_id": session_id,
            "original_query": original_query,
            "expanded_query": expanded_query,
            "confidence": confidence,
            "reason": reason,
            "message": message,
            "suggestion": "Please provide more specific details about the analysis you want."
        }
    
    def _request_confirmation(self, 
                            original_query: str, 
                            expanded_query: str, 
                            confidence: float, 
                            session_id: str) -> Dict[str, Any]:
        """Request user confirmation for expansion"""
        
        return {
            "success": True,
            "needs_confirmation": True,
            "session_id": session_id,
            "original_query": original_query,
            "expanded_query": expanded_query,
            "confidence": confidence,
            "message": f"I interpreted your query as: '{expanded_query}'. Is this correct?",
            "options": ["yes", "no", "rephrase"]
        }
    
    def _error_response(self, message: str, details: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate error response"""
        
        return {
            "success": False,
            "error": message,
            "details": details or {}
        }
    
    async def handle_clarification_response(self, 
                                            session_id: str, 
                                            user_response: str,
                                            original_query: str,
                                            expanded_query: str,
                                            similarity_threshold: float = None) -> Dict[str, Any]:
        """Handle user response to clarification request
        
        User can respond with:
        1. Confirmation ("yes", "ok", "that's right") → proceed to search
        2. Rejection ("no", "wrong") → ask for rephrase, restart
        3. New clarification → treat as new query with context
        """
        
        similarity_threshold = similarity_threshold or self.default_similarity_threshold
        
        # Get session
        conversation = await self.session_manager.get_session(session_id)
        if not conversation:
            return self._error_response("Session not found")
        
        response_lower = user_response.lower().strip()
        
        # Check if user confirmed
        if response_lower in ["yes", "ok", "correct", "that's right", "yep", "yeah", "sure", "confirm"]:
            logger.info(f"User confirmed expansion, proceeding to search with: {expanded_query[:100]}...")
            
            # Proceed directly to SEARCH (VALIDATE already passed before asking)
            search_result = self.analysis_library.search_similar(
                query=expanded_query,
                top_k=5,
                similarity_threshold=similarity_threshold
            )
            
            if not search_result["success"]:
                return self._error_response("Search failed", search_result)
            
            # Add to conversation history
            turn = conversation.add_turn(
                user_query=original_query,
                query_type="contextual",
                expanded_query=expanded_query,
                context_used=True
            )
            
            return {
                "success": True,
                "session_id": session_id,
                "query_type": "contextual",
                "original_query": original_query,
                "final_query": expanded_query,
                "search_results": search_result.get("analyses", []),
                "found_similar": search_result.get("found_similar", False),
                "stage": "ready"
            }
        
        # Check if user rejected
        elif response_lower in ["no", "wrong", "incorrect", "nope", "nah"]:
            logger.info(f"User rejected expansion, asking for rephrase")
            
            return {
                "success": True,
                "stage": "needs_input",
                "input_type": "rephrase",
                "session_id": session_id,
                "message": "Please rephrase your question with more specific details about the assets and analysis you want.",
                "hint": "Include what you want to analyze and what metrics/analysis you're interested in"
            }
        
        # Otherwise, treat user response as new clarification/input
        else:
            logger.info(f"User provided additional clarification, treating as new query with context")
            
            # User provided more details - treat as contextual query (has session history)
            # Re-run the full flow with the user's clarification
            return await self.search_with_context(
                query=user_response,
                session_id=session_id,
                similarity_threshold=similarity_threshold
            )
    
    async def get_session_context(self, session_id: str) -> Dict[str, Any]:
        """Get conversation context for debugging"""
        
        conversation = await self.session_manager._get_session(session_id)
        if not conversation:
            return {"error": "Session not found"}
        
        return conversation.get_context_summary()

# Factory function to create context-aware search with dependencies
def create_context_aware_search(analysis_library: AnalysisLibrary = None,
                               session_manager: SessionManager = None,
                               classifier: QueryClassifier = None,
                               expander: ContextExpander = None) -> ContextAwareSearch:
    """Create context-aware search with all dependencies"""
    return ContextAwareSearch(analysis_library, session_manager, classifier, expander)