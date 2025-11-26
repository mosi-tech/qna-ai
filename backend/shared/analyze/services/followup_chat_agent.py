#!/usr/bin/env python3
"""
Follow-Up Chat Agent

Handles follow-up questions about previous analyses/executions.
Uses tool-calling to intelligently fetch execution details instead of bloating context.
"""

import logging
import time
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

from ...llm import LLMService
from ...services.base_service import BaseService
from .intent_classifier import IntentResult, MessageIntent
from ..dialogue.context.simplified_context_manager import SimplifiedFinancialContextManager, ContextType

logger = logging.getLogger(__name__)


@dataclass
class FollowUpResponse:
    """Response from follow-up chat agent"""
    content: str
    used_tools: List[str] = None


class FollowUpChatAgent(BaseService):
    """Agent for handling follow-up chat about previous analyses"""
    
    def __init__(self, 
                 llm_service: Optional[LLMService] = None,
                 audit_service=None):
        super().__init__(llm_service=llm_service, service_name="followup-chat-agent")
        self.audit_service = audit_service
        self.context_manager = SimplifiedFinancialContextManager()
    
    def _create_default_llm(self) -> LLMService:
        """Create default LLM service for follow-up chat"""
        from ...llm.utils import LLMConfig
        
        config = LLMConfig.from_env()
        config.temperature = 0.6
        config.max_tokens = 1000
        config.service_name = "followup-chat-agent"
        return LLMService(config)
    
    def _get_system_prompt_filename(self) -> str:
        """Use follow-up specific system prompt"""
        return "system-prompt-followup-chat-agent.txt"
    
    async def execute(self,
                     user_message: str,
                     conversation,
                     session_id: str = None,
                     audit_service=None) -> FollowUpResponse:
        """
        Execute follow-up chat with tool support
        
        Args:
            user_message: User's follow-up question
            conversation: ConversationStore with message history
            session_id: Session ID for context
            audit_service: AuditService for fetching execution details
            
        Returns:
            FollowUpResponse with answer and tool usage info
        """
        try:
            logger.info(f"🤖 Follow-up chat agent processing: {user_message[:80]}...")
            
            if audit_service:
                self.audit_service = audit_service
            
            start_time = time.time()
            
            # Get conversation context with analysis IDs and metadata
            messages = await self.context_manager.get_conversation_messages_for_llm(
                conversation, ContextType.FOLLOW_UP_GENERATION, user_message,
                include_analysis_metadata=True
            )
            
            logger.debug(f"📋 Got {len(messages)} context messages")
            
            # Extract execution IDs from conversation (for logging)
            execution_ids = await self._extract_execution_ids(conversation)
            logger.debug(f"📊 Found {len(execution_ids)} execution IDs available in conversation")
            
            # Load system prompt
            if not self.system_prompt:
                self.system_prompt = await self.load_system_prompt()
            
            # Call LLM with automatic MCP tool loading
            # The LLMService will automatically load tools from mcp-tools.json
            # based on the service name "followup-chat-agent"
            logger.debug(f"🔄 Calling LLM with {len(messages)} context messages")
            logger.info(f"📦 LLM service will auto-load MCP tools for 'followup-chat-agent'")
            
            response = await self.llm_service.make_request(
                messages=messages,
                max_tokens=1000,
                temperature=0.6,
                system_prompt=self.system_prompt
                # tools parameter omitted - LLMService handles MCP tool loading automatically
            )
            
            duration = time.time() - start_time
            logger.debug(f"⏱️ Follow-up response generated in {duration:.2f}s")
            logger.debug(f"📊 LLM response keys: {response.keys()}")
            
            if not response.get("success"):
                error_msg = response.get("error", "Unknown error")
                logger.error(f"❌ Follow-up chat failed: {error_msg}")
                return FollowUpResponse(content="I encountered an error processing your question. Please try again.")
            
            content = response.get("content", "").strip()
            used_tools = response.get("tool_calls", [])
            
            # Handle tool calls if any
            if used_tools:
                logger.info(f"🔧 LLM made {len(used_tools)} tool calls")
                for tool_call in used_tools:
                    logger.debug(f"  Tool: {tool_call.get('function', {}).get('name')}")
            else:
                logger.debug("✓ No tool calls needed")
            
            return FollowUpResponse(
                content=content,
                used_tools=used_tools
            )
            
        except Exception as e:
            logger.error(f"❌ Follow-up chat agent error: {e}", exc_info=True)
            raise
    
    async def _extract_execution_ids(self, conversation) -> List[str]:
        """Extract execution IDs from conversation history"""
        try:
            execution_ids = []
            messages = await conversation.get_messages()
            
            for msg in messages:
                metadata = msg.metadata or {}
                execution_id = metadata.get("executionId") or metadata.get("execution_id")
                if execution_id and execution_id not in execution_ids:
                    execution_ids.append(execution_id)
            
            return execution_ids
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to extract execution IDs: {e}")
            return []
    
    def _define_tools(self, execution_ids: List[str]) -> List[Dict[str, Any]]:
        """Get MCP tools from LLM service
        
        MCP tools are automatically loaded from mcp-tools.json config
        based on service name "followup-chat-agent"
        """
        # MCP tools are loaded automatically by LLMService based on service_name
        # Just log that tools will be available
        if execution_ids:
            logger.info(f"🔧 MCP tools will be available for {len(execution_ids)} execution IDs")
        
        # Return empty list - tools are loaded by LLMService.make_request()
        return []
    
    async def handle_tool_call(self, tool_name: str, tool_input: Dict[str, Any]) -> str:
        """Handle tool calls from LLM
        
        This would be called in a loop by the LLM service
        """
        try:
            if tool_name == "get_execution_details":
                return await self._handle_get_execution_details(tool_input)
            elif tool_name == "get_analysis_details":
                return await self._handle_get_analysis_details(tool_input)
            else:
                return f"Unknown tool: {tool_name}"
                
        except Exception as e:
            logger.error(f"❌ Tool call failed: {e}")
            return f"Error: {str(e)}"
    
    async def _handle_get_execution_details(self, tool_input: Dict[str, Any]) -> str:
        """Fetch and summarize execution details"""
        try:
            execution_id = tool_input.get("execution_id")
            field = tool_input.get("field", "all")
            
            if not execution_id or not self.audit_service:
                return "Cannot fetch execution details - service unavailable"
            
            # Fetch execution from audit service
            execution = await self.audit_service.get_execution(execution_id)
            if not execution:
                return f"Execution {execution_id} not found"
            
            # Build summary
            summary_parts = []
            
            if field in ["parameters", "all"]:
                params = execution.get("execution_params") or execution.get("parameters")
                if params:
                    summary_parts.append(f"Parameters: {self._safe_str(params)[:300]}")
            
            if field in ["results", "all"]:
                # Return result summary if available, not raw results
                result_summary = execution.get("result_summary") or self._generate_result_summary(
                    execution.get("result") or execution.get("output")
                )
                if result_summary:
                    summary_parts.append(f"Results: {result_summary[:300]}")
            
            return "\n".join(summary_parts) if summary_parts else "No details found"
            
        except Exception as e:
            logger.error(f"❌ Failed to get execution details: {e}")
            return f"Error fetching details: {str(e)}"
    
    async def _handle_get_analysis_details(self, tool_input: Dict[str, Any]) -> str:
        """Fetch analysis metadata"""
        try:
            execution_id = tool_input.get("execution_id")
            
            if not execution_id or not self.audit_service:
                return "Cannot fetch analysis details - service unavailable"
            
            # Get execution to find linked analysis
            execution = await self.audit_service.get_execution(execution_id)
            if not execution:
                return f"Execution {execution_id} not found"
            
            analysis_id = execution.get("analysis_id")
            if not analysis_id:
                return "No analysis linked to this execution"
            
            # Fetch analysis
            analysis = await self.audit_service.get_analysis(analysis_id)
            if not analysis:
                return f"Analysis {analysis_id} not found"
            
            # Build summary
            summary_parts = [
                f"Analysis Type: {analysis.get('analysis_type', 'Unknown')}",
                f"Description: {analysis.get('description', 'N/A')[:200]}",
                f"Original Question: {analysis.get('question', 'N/A')[:200]}"
            ]
            
            return "\n".join(summary_parts)
            
        except Exception as e:
            logger.error(f"❌ Failed to get analysis details: {e}")
            return f"Error fetching details: {str(e)}"
    
    def _generate_result_summary(self, results: Any) -> Optional[str]:
        """Generate a brief summary of execution results"""
        try:
            if not results:
                return None
            
            if isinstance(results, dict):
                summary_parts = []
                
                # Extract key metrics
                for key in ["summary", "status", "error"]:
                    if key in results:
                        summary_parts.append(f"{key}: {self._safe_str(results[key])[:100]}")
                
                # Extract numeric metrics
                for key in ["correlation", "performance", "risk", "value"]:
                    if key in results and isinstance(results[key], (int, float)):
                        summary_parts.append(f"{key}: {results[key]}")
                
                return " | ".join(summary_parts) if summary_parts else None
            
            return self._safe_str(results)[:200]
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to summarize results: {e}")
            return None
    
    def _safe_str(self, val: Any) -> str:
        """Safely convert value to string, handling NaN, inf, etc"""
        try:
            import math
            if isinstance(val, float):
                if math.isnan(val) or math.isinf(val):
                    return "N/A"
            return str(val)
        except:
            return str(val)
