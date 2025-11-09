#!/usr/bin/env python3
"""
Context Expander - Expand contextual queries using conversation history
"""

import json
import logging
from typing import Optional, Dict, Any, List, Union
from ..conversation.store import UserMessage, AssistantMessage
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
                          conversation_messages: List[Union[UserMessage, AssistantMessage]]) -> Dict[str, Any]:
        """Expand contextual query using conversation history"""
        
        if not conversation_messages:
            return {
                "success": False,
                "error": "No conversation history available for expansion",
                "expanded_query": contextual_query,
                "confidence": 0.0
            }
        
        # Build conversation context from messages
        conversation_context = self._build_conversation_context(conversation_messages)
        
        # Use LLM to expand the query with conversation context
        expansion_result = await self._expand_with_llm(contextual_query, conversation_context)
        
        # LLM now returns confidence, no need to override
        return expansion_result
    
    def _build_conversation_context(self, conversation_messages: List[Union[UserMessage, AssistantMessage]]) -> str:
        """Build formatted conversation context from messages

        IMPORTANT: Skips messages where assistant returned an error message.
        Error messages don't provide useful context for expanding queries.
        """

        context_lines = []

        # Include up to last 6 messages for context (3 exchanges)
        recent_messages = conversation_messages[-6:] if len(conversation_messages) > 6 else conversation_messages
        
        for i, message in enumerate(recent_messages):
            if isinstance(message, UserMessage):
                context_lines.append(f"User: {message.content}")
            elif isinstance(message, AssistantMessage) and not self._is_error_response(message):
                context_lines.append(f"Assistant: {message.content[:200]}...")  # Truncate long responses
                
                # Add separator between message pairs
                if i < len(recent_messages) - 2:
                    context_lines.append("---")

        return "\n".join(context_lines)

    def _is_error_response(self, message: AssistantMessage) -> bool:
        """Check if a conversation message represents an error response

        Returns True if the assistant message was an error (no successful analysis).
        This helps skip failed queries when building context.
        """
        # Check if assistant message indicates an error
        if message.content:
            content_lower = message.content.lower()
            error_indicators = [
                "something went wrong",
                "could not answer",
                "error",
                "failed to",
                "unable to",
                "couldn't process",
                "I don't understand your request",
                "sorry",
                "apologize"
            ]
            return any(indicator in content_lower for indicator in error_indicators)

        # If no content at all, likely an error
        return not message.content
    
    async def _expand_with_llm(self, contextual_query: str, conversation_context: str) -> Dict[str, Any]:
        """Use LLM to expand contextual query with conversation context"""
        
        result = await self.context_service.expand_contextual_query(contextual_query, conversation_context)
        
        if result["success"]:
            logger.info(f"LLM expanded '{contextual_query}' to '{result['expanded_query'][:50]}...'")
        else:
            logger.warning(f"LLM expansion failed: {result.get('error')}")
        
        return result
    
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
    
    
# Factory function to create context expander
def create_context_expander(context_service: ContextService, classifier: QueryClassifier) -> ContextExpander:
    """Create context expander with dependencies"""
    return ContextExpander(context_service, classifier)