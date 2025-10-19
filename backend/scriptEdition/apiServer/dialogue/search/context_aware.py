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
                                 similarity_threshold: float = None) -> Dict[str, Any]:
        """Main entry point for context-aware search
        
        Flow:
        1. CLASSIFY: Detect if CONTEXTUAL or STANDALONE
        2. If CONTEXTUAL: EXPAND → VALIDATE → SEARCH
        3. If STANDALONE: VALIDATE → SEARCH
        """
        
        similarity_threshold = similarity_threshold or self.default_similarity_threshold
        
        # Get or create session (SessionManager handles MongoDB context loading)
        session_id, conversation = await self.session_manager.get_or_create_session(session_id)
        
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
        
        # Step 3: VALIDATE - Check if query is complete
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
        
        # Add to conversation history
        turn = conversation.add_turn(
            user_query=query,
            query_type="contextual" if is_contextual else "standalone",
            expanded_query=final_query if is_contextual else None,
            context_used=is_contextual
        )
        
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
        
        return {
            "success": True,
            "needs_clarification": True,
            "session_id": session_id,
            "original_query": original_query,
            "expanded_query": expanded_query,
            "confidence": confidence,
            "reason": reason,
            "message": f"{reason}. Did you mean: '{expanded_query}'?",
            "suggestion": "Please provide more specific details about the assets and analysis you want."
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
        session_id_result, conversation = await self.session_manager.get_or_create_session(session_id)
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
                "session_id": session_id_result,
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
                "session_id": session_id_result,
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
                session_id=session_id_result,
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