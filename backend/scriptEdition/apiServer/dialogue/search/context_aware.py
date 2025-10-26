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

        Returns:
            Standardized response dict with:
            - success: bool
            - type: str ("error", "clarification_needed", "meaningless_query", "search_result")
            - session_id: str (always present)
            - query_type: str ("contextual" or "standalone", if applicable)
            - original_query: str (always present except errors)
            - expanded_query: str (always present for non-errors)
            - Additional fields based on type
        """

        similarity_threshold = similarity_threshold or self.default_similarity_threshold

        # Verify session_id is provided (REQUIRED)
        if not session_id:
            return self._error_response(
                message="Session ID is required for context-aware search",
                original_query=query
            )

        # Get conversation from session
        if self.session_manager:
            conversation = await self.session_manager.get_session(session_id)
            if not conversation:
                return self._error_response(
                    message="Session not found",
                    session_id=session_id,
                    original_query=query
                )
        else:
            # No session manager available, create minimal conversation store
            conversation = ConversationStore(session_id)

        # Step 1: CLASSIFY - Is this query CONTEXTUAL or STANDALONE?
        classification = await self._classify_contextual(query, conversation)

        if not classification["success"]:
            return self._error_response(
                message="Unable to understand your query",
                details=classification,
                session_id=session_id,
                original_query=query
            )

        is_contextual = classification["is_contextual"]
        expanded_query = query

        # Step 2: EXPAND (if contextual) - Make query explicit using context
        expansion_confidence = 0.9  # Default high confidence for standalone

        if is_contextual:
            logger.info(f"Query is contextual, expanding with context...")
            expansion = await self._expand_query(query, conversation)

            if not expansion["success"]:
                return self._error_response(
                    message="Unable to understand your question in context",
                    details=expansion,
                    session_id=session_id,
                    original_query=query
                )

            expanded_query = expansion.get("expanded_query", query)
            expansion_confidence = expansion.get("confidence", 0.9)
            logger.info(f"Expanded query: {expanded_query[:100]}... (confidence: {expansion_confidence})")

            # If low confidence on expansion, ask for clarification
            if expansion_confidence < 0.7:
                logger.info(f"Low expansion confidence ({expansion_confidence}), requesting clarification")
                return self._request_clarification(
                    original_query=query,
                    expanded_query=expanded_query,
                    confidence=expansion_confidence,
                    session_id=session_id,
                    query_type="contextual",
                    reason="I'm not confident about my interpretation"
                )

            # Step 2.5: Check if expansion is meaningless (e.g., "Why?" → "Why?")
            if await self._is_meaningless_query(expanded_query):
                logger.info(f"Expansion is meaningless ('{query}' → '{expanded_query}'), skipping clarification")
                return {
                    "success": True,
                    "type": "meaningless_query",
                    "session_id": session_id,
                    "query_type": "contextual",
                    "original_query": query,
                    "expanded_query": expanded_query,
                    "is_meaningless": True,
                    "message": "I don't understand your request. I need more details to help you. Please tell me what you'd like to analyze."
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
                    "type": "meaningless_query",
                    "session_id": session_id,
                    "query_type": "standalone",
                    "original_query": query,
                    "expanded_query": query,
                    "is_meaningless": True,
                    "message": "I don't understand your request. I need more details to help you. Please tell me what you'd like to analyze."
                }
            logger.info(f"🔹 Query is not meaningless, proceeding to validation")

        # Step 3: VALIDATE - Check if query is complete
        # await progress_info(session_id, "Checking question for completeness...")
        # validation = self.validator.validate(expanded_query)

        # if not validation["complete"]:
        #     missing = ", ".join(validation["missing"])
        #     logger.info(f"Validation failed, missing: {missing}")
        #     return self._request_clarification(
        #         original_query=query,
        #         expanded_query=expanded_query,
        #         confidence=expansion_confidence,
        #         session_id=session_id,
        #         query_type="contextual" if is_contextual else "standalone",
        #         reason=f"Missing information: {missing}"
        #     )

        # Step 4: SEARCH - Query is ready
        # logger.info(f"Query validated, proceeding with search: {expanded_query[:100]}...")

        # Search for similar analyses
        search_result = self.analysis_library.search_similar(
            query=expanded_query,
            top_k=5,
            similarity_threshold=similarity_threshold
        )

        if not search_result["success"]:
            return self._error_response(
                message="Search failed",
                details=search_result,
                session_id=session_id,
                original_query=query
            )

        return {
            "success": True,
            "type": "search_result",
            "session_id": session_id,
            "query_type": "contextual" if is_contextual else "standalone",
            "original_query": query,
            "expanded_query": expanded_query,
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
            # Get conversation turns (expander expects ConversationTurn objects, not string)
            turns = conversation.turns
            
            result = await self.expander.expand_query(query, turns)
            
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
                             query_type: str,
                             reason: str = None) -> Dict[str, Any]:
        """Request clarification for low-confidence expansion or incomplete query

        Returns standardized clarification response with type='clarification_needed'
        """

        if reason is None:
            reason = "I'm not sure how to interpret your question"

        # Check if query was expanded (original != final) or just needs more info
        was_expanded = original_query.strip() != expanded_query.strip()

        if was_expanded:
            message = f"{reason}. Did you mean: '{expanded_query}'?"
        else:
            message = reason

        return {
            "success": True,
            "type": "clarification_needed",
            "session_id": session_id,
            "query_type": query_type,
            "original_query": original_query,
            "expanded_query": expanded_query,
            "needs_clarification": True,
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
    
    def _error_response(self,
                       message: str,
                       details: Dict[str, Any] = None,
                       session_id: str = None,
                       original_query: str = None) -> Dict[str, Any]:
        """Generate standardized error response

        Returns error response with type='error' and standard fields
        """

        response = {
            "success": False,
            "type": "error",
            "error": message,
            "details": details or {}
        }

        # Add optional fields if provided
        if session_id is not None:
            response["session_id"] = session_id
        if original_query is not None:
            response["original_query"] = original_query

        return response
    
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
            return self._error_response(
                message="Session not found",
                session_id=session_id
            )


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
                return self._error_response(
                    message="Search failed",
                    details=search_result,
                    session_id=session_id,
                    original_query=original_query
                )

            # Add to conversation history
            turn = conversation.add_turn(
                user_query=original_query,
                query_type="contextual",
                expanded_query=expanded_query,
                context_used=True
            )

            return {
                "success": True,
                "type": "search_result",
                "session_id": session_id,
                "query_type": "contextual",
                "original_query": original_query,
                "expanded_query": expanded_query,
                "search_results": search_result.get("analyses", []),
                "found_similar": search_result.get("found_similar", False),
                "stage": "ready"
            }

        # Check if user rejected
        elif response_lower in ["no", "wrong", "incorrect", "nope", "nah"]:
            logger.info(f"User rejected expansion, asking for rephrase")

            return {
                "success": True,
                "type": "rephrase_needed",
                "session_id": session_id,
                "original_query": original_query,
                "expanded_query": expanded_query,
                "stage": "needs_input",
                "input_type": "rephrase",
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