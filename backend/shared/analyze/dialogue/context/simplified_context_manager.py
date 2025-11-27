#!/usr/bin/env python3
"""
Simplified Financial Context Manager - Let LLM do the reasoning

Revolutionary approach: Instead of complex manual context building, 
provide rich formatted conversation strings and let LLM handle pattern recognition.

Key improvements:
- Smart context window sizing based on conversation structure
- Rich metadata preserved in natural format  
- Incremental summarization with caching
- 90% less complexity while providing better context
"""

import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

from ..conversation.store import ConversationStore, UserMessage, AssistantMessage, Message

logger = logging.getLogger(__name__)

class ContextType(Enum):
    """Types of context needed by different services"""
    INTENT_CLASSIFICATION = "intent_classification"
    CONTEXTUAL_DETECTION = "contextual_detection" 
    FOLLOW_UP_GENERATION = "follow_up_generation"
    QUERY_EXPANSION = "contextual_query_expansion"

@dataclass
class ContextWindowRequirements:
    """Requirements for different context types"""
    min_user_messages: int
    min_assistant_messages: int
    max_total_messages: int = 15

class SimplifiedFinancialContextManager:
    """
    Simplified context manager that provides rich conversation strings
    instead of pre-processed context. Let LLM do the intelligent reasoning.
    """
    
    def __init__(self, llm_service=None):
        # Context window requirements by type
        self.requirements = {
            ContextType.INTENT_CLASSIFICATION: ContextWindowRequirements(1, 1, 8),
            ContextType.CONTEXTUAL_DETECTION: ContextWindowRequirements(2, 1, 6),
            ContextType.FOLLOW_UP_GENERATION: ContextWindowRequirements(2, 2, 15),
            ContextType.QUERY_EXPANSION: ContextWindowRequirements(2, 2, 15)
        }
        
        # Incremental summarization cache
        self.conversation_summaries: Dict[str, str] = {}
        self.last_summarized_index: Dict[str, int] = {}
        self.summary_threshold = 8  # Summarize when we have 8+ historical messages
        
        self.llm_service = llm_service
        
        logger.info("✅ SimplifiedFinancialContextManager initialized")
    
    async def get_conversation_messages_for_llm(self, 
                                              conversation: ConversationStore, 
                                              context_type: ContextType,
                                              current_query: str,
                                              include_analysis_metadata: bool = False) -> List[Dict[str, str]]:
        """
        Revolutionary approach: Format conversation as native LLM messages array
        
        Uses smart windowing, historical summaries, and proper message formatting
        for LLM provider's native conversation format. This is the TRUE approach -
        let LLM providers handle conversation formatting naturally.
        
        Args:
            conversation: ConversationStore with message history
            context_type: Type of context needed
            current_query: Current user query
            include_analysis_metadata: If True, add system message listing available analysis/execution IDs
            
        Returns:
            List of messages in LLM format: [{"role": "user/assistant", "content": "..."}]
        """
        try:
            if not conversation:
                # No conversation - just the current query
                return [{"role": "user", "content": current_query}]
            
            all_messages = await conversation.get_messages()
            if not all_messages:
                # No messages - just the current query
                return [{"role": "user", "content": current_query}]
                
            logger.debug(f"🔍 Formatting {len(all_messages)} messages for LLM ({context_type.value})")
            
            # Phase 1: Smart context window sizing
            recent_window = self._get_smart_context_window(all_messages, context_type)
            
            # Phase 1.5: Extract available analysis/execution IDs if requested
            messages = []
            if include_analysis_metadata:
                analysis_metadata = await self._extract_available_ids(recent_window)
                if analysis_metadata:
                    messages.append({
                        "role": "system",
                        "content": analysis_metadata
                    })
            
            # Phase 2: Get historical summary if needed (for very long conversations)
            if len(all_messages) > len(recent_window):
                historical_summary = await self._get_cached_summary_if_needed(
                    conversation.session_id, all_messages, len(recent_window)
                )
                if historical_summary:
                    # Add summary as first assistant message
                    messages.append({
                        "role": "assistant", 
                        "content": f"Previous conversation summary: {historical_summary}"
                    })
            
            # Phase 3: Add recent conversation in native LLM format with full metadata
            for message in recent_window:
                if isinstance(message, AssistantMessage):
                    # Use rich formatted content with all metadata
                    content = message.to_context_string()
                    
                    # Add analysis context if available (for follow-up questions)
                    metadata = message.metadata or {}
                    if metadata.get("analysisId") or metadata.get("analysis_id"):
                        context_parts = []
                        context_parts.append("=== Analysis Context ===")
                        
                        analysis_id = metadata.get("analysisId") or metadata.get("analysis_id")
                        execution_id = metadata.get("executionId") or metadata.get("execution_id")
                        if analysis_id:
                            context_parts.append(f"Analysis: {analysis_id}")
                        if execution_id:
                            context_parts.append(f"Execution: {execution_id}")
                        
                        if "script_name" in metadata:
                            context_parts.append(f"Script: {metadata['script_name']}")
                        
                        if "execution" in metadata:
                            params = str(metadata["execution"])[:200]
                            context_parts.append(f"Parameters: {params}")
                        
                        context_parts.append("Reference this context for follow-up questions.")
                        
                        context_str = "\n".join(context_parts)
                        content = f"{content}\n\n{context_str}"
                else:
                    # User messages are just content
                    content = message.content
                    
                messages.append({
                    "role": message.role,
                    "content": content
                })
            
            # Add current query as final user message (only if not already included)
            if not recent_window or recent_window[-1].content != current_query:
                messages.append({
                    "role": "user", 
                    "content": current_query
                })
            
            logger.debug(f"✅ Formatted {len(messages)} messages for LLM (including {len(recent_window)} recent + current query)")
            return messages
            
        except Exception as e:
            logger.error(f"❌ LLM message formatting failed: {e}", exc_info=True)
            # Safe fallback
            return [{"role": "user", "content": current_query}]
    
    async def _extract_available_ids(self, messages: List[Message]) -> Optional[str]:
        """
        Extract available analysis and execution IDs from recent messages.
        Returns formatted system message listing all available IDs for LLM tool calling.
        """
        try:
            available_ids = {}
            
            for msg in messages:
                metadata = msg.metadata or {}
                analysis_id = metadata.get("analysisId") or metadata.get("analysis_id")
                execution_id = metadata.get("executionId") or metadata.get("execution_id")
                
                if analysis_id or execution_id:
                    key = f"{analysis_id}_{execution_id}" if (analysis_id and execution_id) else (analysis_id or execution_id)
                    if key not in available_ids:
                        available_ids[key] = {
                            "analysis_id": analysis_id,
                            "execution_id": execution_id
                        }
            
            if not available_ids:
                return None
            
            parts = ["Available analysis contexts in this conversation:"]
            for info in available_ids.values():
                if info["analysis_id"] and info["execution_id"]:
                    parts.append(f"• Analysis: {info['analysis_id']}, Execution: {info['execution_id']}")
                elif info["analysis_id"]:
                    parts.append(f"• Analysis: {info['analysis_id']}")
                elif info["execution_id"]:
                    parts.append(f"• Execution: {info['execution_id']}")
            
            parts.append("\nYou can use the available MCP tools to fetch details about these analyses and executions.")
            
            return "\n".join(parts)
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to extract available IDs: {e}")
            return None
    
    async def _extract_recent_analyses(self, conversation: ConversationStore, max_items: int = 5) -> Optional[str]:
        """
        Extract rich metadata about recent analyses and executions from Redis cache.
        Returns formatted context about recent work separately from conversation messages.
        Merges both analyses and executions (they're independent) for complete picture.
        
        Args:
            conversation: ConversationStore with Redis cache
            max_items: Maximum number of combined items to include (analyses + executions)
            
        Returns:
            Formatted string with recent analyses/executions metadata, or None if none found
        """
        try:
            # Get both recent analyses and executions from Redis cache
            recent_analyses = await conversation.get_recent_analyses()
            recent_executions = await conversation.get_recent_executions()
            
            if not recent_analyses and not recent_executions:
                return None
            
            # Merge and sort by timestamp (newest first) for chronological grouping
            all_items = []
            
            for analysis in recent_analyses:
                timestamp = analysis.get("timestamp", "")
                all_items.append({
                    "type": "analysis",
                    "timestamp": timestamp,
                    "data": analysis
                })
            
            for execution in recent_executions:
                timestamp = execution.get("timestamp", "")
                all_items.append({
                    "type": "execution",
                    "timestamp": timestamp,
                    "data": execution
                })
            
            # Sort by timestamp descending (newest first)
            all_items.sort(key=lambda x: x["timestamp"], reverse=True)
            
            # Limit to max_items
            all_items = all_items[:max_items]
            
            if not all_items:
                return None
            
            parts = [f"📊 Recent analyses and executions (last {len(all_items)}):"]
            for i, item in enumerate(all_items, 1):
                item_type = item["type"]
                data = item["data"]
                timestamp_val = data.get("timestamp", "")
                
                if isinstance(timestamp_val, str):
                    timestamp_str = timestamp_val.split(".")[0]  # Remove microseconds
                else:
                    timestamp_str = str(timestamp_val)
                
                parts.append(f"\n{i}. [{timestamp_str}] {item_type.upper()}")
                
                # Common fields for both
                question = data.get("question", "")
                if question:
                    parts.append(f"   Question: {question[:100]}")
                
                if item_type == "analysis":
                    analysis_type = data.get("analysis_type", "")
                    if analysis_type:
                        parts.append(f"   Type: {analysis_type}")
                    
                    analysis_id = data.get("analysis_id", "")
                    if analysis_id:
                        parts.append(f"   Analysis ID: {analysis_id}")
                
                elif item_type == "execution":
                    status = data.get("status", "")
                    if status:
                        parts.append(f"   Status: {status}")
                    
                    script_name = data.get("script_name", "")
                    if script_name:
                        parts.append(f"   Script: {script_name}")
                    
                    execution_id = data.get("execution_id", "")
                    if execution_id:
                        parts.append(f"   Execution ID: {execution_id}")
                    
                    # Link to analysis if exists
                    analysis_id = data.get("analysis_id", "")
                    if analysis_id:
                        parts.append(f"   Analysis ID: {analysis_id}")
            
            parts.append("\nUse these IDs to fetch detailed results using available MCP tools.")
            
            return "\n".join(parts)
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to extract recent analyses/executions: {e}")
            return None
    
    # ========== PHASE 1: Smart Context Window Sizing ==========
    
    def _get_smart_context_window(self, messages: List[Message], 
                                context_type: ContextType) -> List[Message]:
        """
        Determine optimal context window based on conversation structure.
        Ensures minimum representation of both user and assistant messages.
        """
        if not messages:
            return []
        
        requirements = self.requirements[context_type]
        
        # Start with reasonable recent window
        max_window = min(requirements.max_total_messages, len(messages))
        recent_window = messages[-max_window:]
        
        # Build balanced window that meets minimum requirements
        return self._build_balanced_window(
            messages, 
            requirements.min_user_messages,
            requirements.min_assistant_messages,
            requirements.max_total_messages
        )
    
    def _build_balanced_window(self, messages: List[Message], 
                             min_users: int, min_assistants: int,
                             max_total: int = 15) -> List[Message]:
        """
        Build context window ensuring minimum representation of both roles.
        Expands window if necessary to meet requirements.
        """
        if not messages:
            return []
        
        # Start with recent messages up to max limit
        current_window = messages[-max_total:] if len(messages) > max_total else messages
        
        # Count message types in current window
        user_count = sum(1 for msg in current_window if isinstance(msg, UserMessage))
        assistant_count = sum(1 for msg in current_window if isinstance(msg, AssistantMessage))
        
        logger.debug(f"Window analysis: {user_count} users, {assistant_count} assistants (need {min_users}/{min_assistants})")
        
        # If current window doesn't meet minimums, expand carefully
        if user_count < min_users or assistant_count < min_assistants:
            # Try expanding window size gradually
            for window_size in range(max_total + 1, len(messages) + 1):
                expanded_window = messages[-window_size:]
                
                exp_user_count = sum(1 for msg in expanded_window if isinstance(msg, UserMessage))
                exp_assistant_count = sum(1 for msg in expanded_window if isinstance(msg, AssistantMessage))
                
                if exp_user_count >= min_users and exp_assistant_count >= min_assistants:
                    logger.debug(f"Expanded window to {window_size} messages to meet requirements")
                    return expanded_window
                
                # Don't expand beyond reasonable limits
                if window_size > 25:
                    break
            
            # If still can't meet requirements, return all messages
            logger.warning(f"Cannot meet minimum requirements, returning all {len(messages)} messages")
            return messages
        
        return current_window
    
    # ========== PHASE 2: Incremental Summarization ==========
    
    async def _get_cached_summary_if_needed(self, session_id: str, 
                                          all_messages: List[Message], 
                                          recent_window_size: int) -> Optional[str]:
        """
        Get cached summary for historical messages, update incrementally if needed.
        Only makes LLM calls when new historical messages need summarizing.
        """
        historical_count = len(all_messages) - recent_window_size
        
        # No historical messages to summarize
        if historical_count <= 0:
            return None
        
        # Don't summarize very short histories
        if historical_count < self.summary_threshold:
            return None
        
        last_summarized = self.last_summarized_index.get(session_id, 0)
        
        # If we have new historical messages that haven't been summarized
        if historical_count > last_summarized:
            logger.debug(f"Updating summary: {last_summarized} -> {historical_count} messages")
            
            # Get new messages to summarize
            new_messages = all_messages[last_summarized:historical_count]
            old_summary = self.conversation_summaries.get(session_id, "")
            
            # Incremental update (only one LLM call for new content)
            updated_summary = await self._update_summary_incrementally(
                old_summary, new_messages, session_id
            )
            
            # Cache results
            self.conversation_summaries[session_id] = updated_summary
            self.last_summarized_index[session_id] = historical_count
            
            return updated_summary
        
        # Return existing summary
        return self.conversation_summaries.get(session_id)
    
    async def _update_summary_incrementally(self, old_summary: str, 
                                          new_messages: List[Message],
                                          session_id: str) -> str:
        """
        Update conversation summary incrementally with new messages.
        More efficient than re-summarizing entire conversation.
        """
        if not new_messages:
            return old_summary
        
        try:
            # Format new messages for summarization
            new_content = self._format_messages_for_summary(new_messages)
            
            if self.llm_service:
                # Use LLM to create/update summary
                if old_summary:
                    prompt = f"""Previous conversation summary: {old_summary}

New messages to incorporate:
{new_content}

Please update the summary to include the new information. Focus on:
- Key topics discussed
- Financial instruments mentioned (tickers, ETFs, etc.)
- Analysis types performed or suggested
- User's investment interests/goals

Updated summary:"""
                else:
                    prompt = f"""Summarize this financial conversation. Focus on:
- Key topics discussed  
- Financial instruments mentioned
- Analysis types performed or suggested
- User's investment interests/goals

Conversation:
{new_content}

Summary:"""
                
                # Make LLM call for summary
                response = await self.llm_service.make_request(
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=200,
                    temperature=0.3
                )
                
                if response.get("success"):
                    return response.get("content", old_summary)
            
            # Fallback to rule-based summary if LLM unavailable
            return self._create_rule_based_summary(old_summary, new_messages)
            
        except Exception as e:
            logger.error(f"Summary update failed for session {session_id}: {e}")
            return old_summary
    
    def _format_messages_for_summary(self, messages: List[Message]) -> str:
        """Format messages for LLM summarization"""
        formatted = []
        for msg in messages:
            if isinstance(msg, UserMessage):
                formatted.append(f"User: {msg.content}")
            else:
                # Use the rich formatting from AssistantMessage
                formatted.append(msg.to_context_string())
        return "\n".join(formatted)
    
    def _create_rule_based_summary(self, old_summary: str, new_messages: List[Message]) -> str:
        """Fallback rule-based summary when LLM unavailable"""
        # Extract key information from new messages
        topics = set()
        tickers = set()
        analyses = []
        
        for msg in new_messages:
            if isinstance(msg, AssistantMessage):
                # Extract topics
                if msg.message_type:
                    topics.add(msg.message_type)
                if msg.has_analysis_suggestion():
                    suggestion = msg.analysis_suggestion
                    topics.add(suggestion.get('analysis_type', 'general'))
                    analyses.append(suggestion.get('topic', 'unknown'))
            
            # Extract tickers (basic regex)
            import re
            ticker_matches = re.findall(r'\b[A-Z]{2,5}\b', msg.content)
            tickers.update(ticker_matches)
        
        # Build simple summary
        summary_parts = []
        if old_summary:
            summary_parts.append(old_summary)
        
        new_info = []
        if topics:
            new_info.append(f"Topics: {', '.join(list(topics)[:3])}")
        if analyses:
            new_info.append(f"Analyses: {', '.join(analyses[:2])}")
        if tickers:
            new_info.append(f"Assets: {', '.join(list(tickers)[:3])}")
        
        if new_info:
            summary_parts.append(f"Recent activity - {', '.join(new_info)}")
        
        return ". ".join(summary_parts)
    
    # ========== Utility Methods ==========
    
    def clear_session_cache(self, session_id: str):
        """Clear cached summary for a session (useful for testing/cleanup)"""
        self.conversation_summaries.pop(session_id, None)
        self.last_summarized_index.pop(session_id, None)
        logger.debug(f"Cleared cache for session {session_id}")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics for monitoring"""
        return {
            "cached_sessions": len(self.conversation_summaries),
            "total_summaries": sum(len(s) for s in self.conversation_summaries.values()),
            "summary_threshold": self.summary_threshold
        }


# ========== Factory and Helper Functions ==========

def create_simplified_context_manager(llm_service=None) -> SimplifiedFinancialContextManager:
    """Factory function to create SimplifiedFinancialContextManager"""
    return SimplifiedFinancialContextManager(llm_service=llm_service)

# Global instance for easy access
_simplified_context_manager = None

def get_simplified_context_manager() -> SimplifiedFinancialContextManager:
    """Get singleton simplified context manager instance"""
    global _simplified_context_manager
    if _simplified_context_manager is None:
        _simplified_context_manager = create_simplified_context_manager()
    return _simplified_context_manager


# Public API
__all__ = [
    'ContextType',
    'SimplifiedFinancialContextManager',
    'create_simplified_context_manager',
    'get_simplified_context_manager',
    'get_followup_context_string'
]