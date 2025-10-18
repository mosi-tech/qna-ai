#!/usr/bin/env python3
"""
Context-Aware Search - Enhanced search with conversation context
"""

import logging
from typing import Optional, Dict, Any, List
from search.library import AnalysisLibrary
from ..conversation.store import ConversationStore, QueryType, ConversationTurn
from ..conversation.session_manager import SessionManager
from ..context.classifier import QueryClassifier
from ..context.expander import ContextExpander

logger = logging.getLogger(__name__)

class ContextAwareSearch:
    """Enhanced search that handles conversation context"""
    
    def __init__(self, 
                 analysis_library: AnalysisLibrary = None,
                 session_manager: SessionManager = None,
                 classifier: QueryClassifier = None,
                 expander: ContextExpander = None):
        self.analysis_library = analysis_library or AnalysisLibrary()
        self.session_manager = session_manager
        self.classifier = classifier
        self.expander = expander
        
        # Configuration
        self.confidence_threshold_auto = 0.8  # Auto-expand above this
        self.confidence_threshold_confirm = 0.5  # Confirm between this and auto
        self.default_similarity_threshold = 0.3
    
    async def search_with_context(self, 
                                 query: str, 
                                 session_id: Optional[str] = None,
                                 auto_expand: bool = True,
                                 similarity_threshold: float = None) -> Dict[str, Any]:
        """Main entry point for context-aware search"""
        
        similarity_threshold = similarity_threshold or self.default_similarity_threshold
        
        # Get or create session (SessionManager handles MongoDB context loading)
        session_id, conversation = await self.session_manager.get_or_create_session(session_id)
        
        # Step 1: Classify query type
        classification_result = await self._classify_query(query, conversation)
        
        if not classification_result["success"]:
            return self._error_response("Query classification failed", classification_result)
        
        query_type = classification_result["query_type_enum"]
        
        # Step 2: Handle based on query type
        if query_type == QueryType.COMPLETE:
            return self._handle_complete_query(query, conversation, similarity_threshold)
        
        elif query_type in [QueryType.CONTEXTUAL, QueryType.COMPARATIVE, QueryType.PARAMETER]:
            return await self._handle_contextual_query(
                query, conversation, query_type, auto_expand, similarity_threshold
            )
        
        else:
            return self._error_response(f"Unsupported query type: {query_type}")
    
    async def _classify_query(self, query: str, conversation: ConversationStore) -> Dict[str, Any]:
        """Classify the query type"""
        
        last_turn = conversation.get_last_turn()
        result = await self.classifier.classify(query, last_turn)
        
        logger.info(f"Classified '{query[:30]}...' as {result.get('query_type', 'unknown')}")
        
        return result
    
    def _handle_complete_query(self, 
                             query: str, 
                             conversation: ConversationStore,
                             similarity_threshold: float) -> Dict[str, Any]:
        """Handle complete standalone queries"""
        
        # Search directly
        search_result = self.analysis_library.search_similar(
            query=query,
            top_k=5,
            similarity_threshold=similarity_threshold
        )
        
        if not search_result["success"]:
            return self._error_response("Search failed", search_result)
        
        # Add brief analysis summary if found results
        analysis_summary = None
        if search_result["found_similar"] and search_result["analyses"]:
            best_match = search_result["analyses"][0]
            analysis_summary = best_match.get("name", "Financial analysis")
        
        # Add to conversation history
        turn = conversation.add_turn(
            user_query=query,
            query_type=QueryType.COMPLETE,
            analysis_summary=analysis_summary,
            context_used=False
        )
        
        return {
            "success": True,
            "session_id": conversation.session_id,
            "turn_id": turn.id,
            "query_type": "complete",
            "original_query": query,
            "search_results": search_result["analyses"],
            "found_similar": search_result["found_similar"],
            "context_used": False,
            "analysis_summary": analysis_summary
        }
    
    async def _handle_contextual_query(self,
                                      query: str,
                                      conversation: ConversationStore, 
                                      query_type: QueryType,
                                      auto_expand: bool,
                                      similarity_threshold: float) -> Dict[str, Any]:
        """Handle contextual queries that need expansion"""
        
        # Get conversation history for context expansion
        conversation_turns = conversation.turns
        
        if not conversation_turns:
            return self._error_response(
                "No conversation history available for contextual expansion",
                {"suggestion": "Please ask a complete question first"}
            )
        
        # Expand the contextual query using conversation history
        expansion_result = await self.expander.expand_query(query, conversation_turns)
        
        if not expansion_result["success"]:
            return self._error_response("Query expansion failed", expansion_result)
        
        expanded_query = expansion_result["expanded_query"]
        confidence = expansion_result["confidence"]
        
        # Decide if we need confirmation
        needs_confirmation = (
            not auto_expand and 
            confidence < self.confidence_threshold_auto and 
            confidence >= self.confidence_threshold_confirm
        )
        
        if needs_confirmation:
            return self._request_confirmation(
                query, expanded_query, confidence, conversation.session_id
            )
        
        # Low confidence - ask for clarification
        if confidence < self.confidence_threshold_confirm:
            return self._request_clarification(
                query, expanded_query, confidence, conversation.session_id
            )
        
        # High confidence or auto_expand - proceed with search
        search_result = self.analysis_library.search_similar(
            query=expanded_query,
            top_k=5,
            similarity_threshold=similarity_threshold
        )
        
        if not search_result["success"]:
            return self._error_response("Search failed", search_result)
        
        # Add to conversation history with analysis summary
        analysis_summary = None
        if search_result["found_similar"] and search_result["analyses"]:
            best_match = search_result["analyses"][0]
            analysis_summary = best_match.get("name", "Financial analysis")
        
        turn = conversation.add_turn(
            user_query=query,
            query_type=query_type,
            expanded_query=expanded_query,
            analysis_summary=analysis_summary,
            context_used=True,
            expansion_confidence=confidence
        )
        
        return {
            "success": True,
            "session_id": conversation.session_id,
            "turn_id": turn.id,
            "query_type": query_type.value,
            "original_query": query,
            "expanded_query": expanded_query,
            "expansion_confidence": confidence,
            "search_results": search_result["analyses"],
            "found_similar": search_result["found_similar"],
            "context_used": True,
            "analysis_summary": analysis_summary
        }
    
    
    def _request_confirmation(self, original_query: str, expanded_query: str, confidence: float, session_id: str) -> Dict[str, Any]:
        """Request user confirmation for expansion"""
        
        return {
            "success": True,
            "needs_confirmation": True,
            "session_id": session_id,
            "original_query": original_query,
            "expanded_query": expanded_query,
            "confidence": confidence,
            "message": f"I interpreted your query as: '{expanded_query}'. Is this correct?",
            "options": ["yes", "no", "clarify"]
        }
    
    def _request_clarification(self, original_query: str, expanded_query: str, confidence: float, session_id: str) -> Dict[str, Any]:
        """Request clarification for low-confidence expansion"""
        
        return {
            "success": True,
            "needs_clarification": True,
            "session_id": session_id,
            "original_query": original_query,
            "expanded_query": expanded_query,
            "confidence": confidence,
            "message": f"I'm not sure how to interpret '{original_query}'. Did you mean something like: '{expanded_query}'?",
            "suggestion": "Please provide more specific details about the assets and strategy you're interested in."
        }
    
    def _error_response(self, message: str, details: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate error response"""
        
        return {
            "success": False,
            "error": message,
            "details": details or {}
        }
    
    async def confirm_expansion(self, session_id: str, confirmed: bool) -> Dict[str, Any]:
        """Handle user confirmation response"""
        
        conversation = await self.session_manager._get_session(session_id)
        if not conversation:
            return self._error_response("Session not found or expired")
        
        # For now, return instruction to retry with auto_expand
        # In full implementation, we'd store pending expansions
        
        if confirmed:
            return {
                "success": True,
                "message": "Please retry your search with auto_expand=True or provide the expanded query directly"
            }
        else:
            return {
                "success": True,
                "message": "Please rephrase your question with more specific details"
            }
    
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