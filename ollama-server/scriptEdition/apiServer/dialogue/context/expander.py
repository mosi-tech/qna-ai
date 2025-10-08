#!/usr/bin/env python3
"""
Context Expander - Expand contextual queries using conversation history
"""

import json
import logging
from typing import Optional, Dict, Any, List
from ..conversation.store import ConversationTurn
from .service import ContextService
from .classifier import QueryClassifier

logger = logging.getLogger(__name__)

class ContextExpander:
    """Expand contextual queries using actual conversation history"""
    
    def __init__(self, context_service: ContextService, classifier: QueryClassifier):
        self.context_service = context_service
        self.classifier = classifier
    
    async def expand_query(self, 
                          contextual_query: str, 
                          conversation_turns: List[ConversationTurn]) -> Dict[str, Any]:
        """Expand contextual query using conversation history"""
        
        if not conversation_turns:
            return {
                "success": False,
                "error": "No conversation history available for expansion",
                "expanded_query": contextual_query,
                "confidence": 0.0
            }
        
        # Build conversation context from turns
        conversation_context = self._build_conversation_context(conversation_turns)
        
        # Use LLM to expand the query with conversation context
        expansion_result = await self._expand_with_llm(contextual_query, conversation_context)
        
        if not expansion_result["success"]:
            # Fallback to pattern-based expansion using conversation history
            expansion_result = self._expand_with_patterns(contextual_query, conversation_turns)
        
        # Score confidence of expansion
        if expansion_result["success"]:
            confidence_result = self._score_expansion_confidence(
                contextual_query, 
                expansion_result["expanded_query"], 
                conversation_context
            )
            expansion_result["confidence"] = confidence_result.get("confidence", 0.5)
            expansion_result["confidence_details"] = confidence_result
        
        return expansion_result
    
    def _build_conversation_context(self, conversation_turns: List[ConversationTurn]) -> str:
        """Build formatted conversation context from turns"""
        
        context_lines = []
        
        # Include up to last 3 turns for context (avoid too much noise)
        recent_turns = conversation_turns[-3:] if len(conversation_turns) > 3 else conversation_turns
        
        for i, turn in enumerate(recent_turns):
            if turn.user_query:
                context_lines.append(f"User: {turn.user_query}")
            
            # Add analysis summary if available
            if turn.analysis_summary:
                context_lines.append(f"Analysis: {turn.analysis_summary}")
            
            # Add separator between turns
            if i < len(recent_turns) - 1:
                context_lines.append("---")
        
        return "\n".join(context_lines)
    
    async def _expand_with_llm(self, contextual_query: str, conversation_context: str) -> Dict[str, Any]:
        """Use LLM to expand contextual query with conversation context"""
        
        result = await self.context_service.expand_contextual_query(contextual_query, conversation_context)
        
        if result["success"]:
            logger.info(f"LLM expanded '{contextual_query}' to '{result['expanded_query'][:50]}...'")
        else:
            logger.warning(f"LLM expansion failed: {result.get('error')}")
        
        return result
    
    def _expand_with_patterns(self, contextual_query: str, conversation_turns: List[ConversationTurn]) -> Dict[str, Any]:
        """Fallback pattern-based expansion using conversation history"""
        
        # Get the last user query for context
        last_turn = conversation_turns[-1] if conversation_turns else None
        if not last_turn or not last_turn.user_query:
            return {
                "success": False,
                "error": "No previous query available for pattern expansion",
                "expanded_query": contextual_query
            }
        
        last_query = last_turn.user_query
        
        # Simple pattern-based substitutions
        expanded_query = self._apply_substitution_patterns(contextual_query, last_query)
        
        if expanded_query != contextual_query:
            return {
                "success": True,
                "expanded_query": expanded_query,
                "method": "pattern_expansion",
                "original_context": last_query
            }
        
        return {
            "success": False,
            "error": "No suitable pattern expansion found",
            "expanded_query": contextual_query
        }
    
    def _apply_substitution_patterns(self, contextual_query: str, last_query: str) -> str:
        """Apply simple substitution patterns"""
        import re
        
        # Extract assets from contextual query
        asset_info = self.classifier.extract_assets_from_contextual_query(contextual_query)
        
        # Pattern 1: "what about X" -> substitute asset in previous query
        if "what about" in contextual_query.lower() and asset_info["assets_found"]:
            new_asset = asset_info["assets_found"][0]
            # Find first asset in last query and replace it
            asset_pattern = r'\b[A-Z]{2,5}\b'  # Simple asset ticker pattern
            match = re.search(asset_pattern, last_query)
            if match:
                return last_query.replace(match.group(), new_asset)
        
        # Pattern 2: "instead of X" -> substitute asset
        if "instead" in contextual_query.lower() and asset_info["assets_found"]:
            new_asset = asset_info["assets_found"][0]
            # Find assets mentioned in "instead of" context
            old_asset_match = re.search(r'instead of (\w+)', contextual_query, re.IGNORECASE)
            if old_asset_match:
                old_asset = old_asset_match.group(1).upper()
                return last_query.replace(old_asset, new_asset)
        
        # Pattern 3: "X to Y" -> substitute asset pair in query
        if " to " in contextual_query and len(asset_info["assets_found"]) >= 2:
            from_asset, to_asset = asset_info["assets_found"][:2]
            # Simple replacement - find first two assets in last query
            assets_in_last = re.findall(r'\b[A-Z]{2,5}\b', last_query)
            if len(assets_in_last) >= 2:
                expanded = last_query.replace(assets_in_last[0], from_asset)
                expanded = expanded.replace(assets_in_last[1], to_asset)
                return expanded
        
        # Pattern 4: Parameter changes like "3% instead" or "monthly instead"
        if "instead" in contextual_query.lower():
            # Extract number with % 
            pct_match = re.search(r'(\d+(?:\.\d+)?)%', contextual_query)
            if pct_match:
                new_pct = pct_match.group(1) + "%"
                # Replace any percentage in last query
                return re.sub(r'\d+(?:\.\d+)?%', new_pct, last_query)
            
            # Extract time period
            time_words = ["daily", "weekly", "monthly", "quarterly", "yearly"]
            for word in time_words:
                if word in contextual_query.lower():
                    # Replace any time period in last query
                    for old_word in time_words:
                        if old_word in last_query.lower():
                            return last_query.lower().replace(old_word, word)
        
        return contextual_query  # No pattern matched
    
    def _score_expansion_confidence(self, original_query: str, expanded_query: str, conversation_context: str) -> Dict[str, Any]:
        """Score confidence of expansion using heuristics"""
        
        # Simple heuristic scoring based on expansion quality
        confidence = self._heuristic_confidence_score(original_query, expanded_query, conversation_context)
        
        return {
            "success": True,
            "confidence": confidence,
            "method": "heuristic_scoring"
        }
    
    def _heuristic_confidence_score(self, original_query: str, expanded_query: str, conversation_context: str) -> float:
        """Calculate confidence using heuristics"""
        
        score = 0.5  # Base score
        
        # Expansion quality (0.4 weight)
        if expanded_query.endswith("?"):
            score += 0.1  # Proper question format
        
        if len(expanded_query.split()) > len(original_query.split()) * 1.5:
            score += 0.2  # Properly expanded with more detail
        
        if expanded_query != original_query:
            score += 0.1  # Actually expanded
        
        # Asset clarity (0.3 weight)
        assets_in_original = self.classifier.extract_assets_from_contextual_query(original_query)
        assets_in_expanded = self.classifier.extract_assets_from_contextual_query(expanded_query)
        
        if assets_in_expanded["asset_count"] >= assets_in_original["asset_count"]:
            score += 0.15  # Maintained or added asset clarity
        
        if assets_in_expanded["asset_count"] >= 2:
            score += 0.15  # Has sufficient asset context
        
        # Context utilization (0.3 weight)
        if conversation_context and len(conversation_context) > 20:
            score += 0.1  # Has meaningful context
        
        # Check if expanded query contains elements from context
        context_words = set(conversation_context.lower().split()) if conversation_context else set()
        expanded_words = set(expanded_query.lower().split())
        
        if context_words & expanded_words:  # Intersection
            score += 0.2  # Used context elements
        
        return min(1.0, max(0.0, score))
    
# Factory function to create context expander
def create_context_expander(context_service: ContextService, classifier: QueryClassifier) -> ContextExpander:
    """Create context expander with dependencies"""
    return ContextExpander(context_service, classifier)