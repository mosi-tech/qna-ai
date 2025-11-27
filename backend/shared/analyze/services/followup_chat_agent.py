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
                 llm_service: Optional[LLMService] = None):
        super().__init__(llm_service=llm_service, service_name="followup-chat-agent")
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
                     user_id: str = None) -> FollowUpResponse:
        """
        Execute follow-up chat with tool support
        
        Args:
            user_message: User's follow-up question
            conversation: ConversationStore with message history
            session_id: Session ID for context
            user_id: User ID for context
            
        Returns:
            FollowUpResponse with answer and tool usage info
        """
        try:
            logger.info(f"🤖 Follow-up chat agent processing: {user_message[:80]}... (session: {session_id[:8] if session_id else 'unknown'})")
            
            start_time = time.time()
            
            # Store context for this execution (thread-local would be better but this is simpler)
            self._execution_context = {
                "session_id": session_id,
                "user_id": user_id
            }
            
            # Get conversation context with analysis IDs and metadata
            messages = await self.context_manager.get_conversation_messages_for_llm(
                conversation, ContextType.FOLLOW_UP_GENERATION, user_message,
                include_analysis_metadata=True
            )
            
            logger.debug(f"📋 Got {len(messages)} context messages")
            
            # Add rich metadata about recent analyses and executions (separate from conversation messages)
            # This helps with follow-up questions about analyses outside the recent message window
            recent_analyses = await self.context_manager._extract_recent_analyses(conversation, max_items=5)
            if recent_analyses:
                messages.insert(1, {  # Insert after first system message but before conversation
                    "role": "system",
                    "content": recent_analyses
                })
                logger.debug(f"📊 Added recent analyses metadata to context")
            
            # Extract execution IDs from conversation (for logging)
            execution_ids = await self._extract_execution_ids(conversation)
            logger.debug(f"📊 Found {len(execution_ids)} execution IDs available in conversation")
            
            # Load system prompt
            if not self.system_prompt:
                self.system_prompt = await self.load_system_prompt()
            
            # Ensure MCP tools are loaded in LLM service
            await self.llm_service.ensure_tools_loaded()
            
            # Call LLM with automatic MCP tool loading
            # The LLMService will automatically load tools from mcp-tools.json
            # based on the service name "followup-chat-agent"
            logger.debug(f"🔄 Calling LLM with {len(messages)} context messages")
            logger.info(f"📦 LLM service will auto-load MCP tools for 'followup-chat-agent'")
            
            # Agentic loop - keep calling LLM until it returns final answer (no tool calls)
            max_iterations = 5
            iteration = 0
            used_tools = []
            
            while iteration < max_iterations:
                iteration += 1
                logger.debug(f"🔄 Agent iteration {iteration}/{max_iterations}")
                
                # Call LLM
                response = await self.llm_service.make_request(
                    messages=messages,
                    max_tokens=1000,
                    temperature=0.6,
                    system_prompt=self.system_prompt
                )
                
                if not response.get("success"):
                    error_msg = response.get("error", "Unknown error")
                    logger.error(f"❌ Follow-up chat failed: {error_msg}")
                    return FollowUpResponse(content="I encountered an error processing your question. Please try again.")
                
                content = response.get("content", "").strip()
                tool_calls = response.get("tool_calls", [])
                
                # If no tool calls, LLM returned final answer
                if not tool_calls:
                    logger.info(f"✅ Agent completed in {iteration} iteration(s)")
                    duration = time.time() - start_time
                    logger.debug(f"⏱️ Follow-up response generated in {duration:.2f}s")
                    return FollowUpResponse(
                        content=content,
                        used_tools=used_tools
                    )
                
                # Handle tool calls
                logger.info(f"🔧 Iteration {iteration}: LLM made {len(tool_calls)} tool call(s)")
                
                # First, add the assistant message with tool_calls to the history
                # This shows what the assistant is trying to do
                assistant_message = {"role": "assistant", "content": content}
                if tool_calls:
                    assistant_message["tool_calls"] = tool_calls
                messages.append(assistant_message)
                logger.debug(f"📝 Added assistant message with {len(tool_calls)} tool calls to history")
                
                # Then execute each tool call and add results
                for tool_call in tool_calls:
                    tool_name = tool_call.get("function", {}).get("name")
                    tool_input = tool_call.get("function", {}).get("arguments", {})
                    tool_call_id = tool_call.get("id", f"call_{len(used_tools)}")
                    
                    logger.debug(f"  Executing tool: {tool_name} with args: {tool_input}")
                    used_tools.append(tool_name)
                    
                    # Execute tool and get result
                    try:
                        tool_result = await self.handle_tool_call(tool_name, tool_input)
                        logger.debug(f"  Tool result: {tool_result[:200]}..." if len(str(tool_result)) > 200 else f"  Tool result: {tool_result}")
                        
                        # Add tool result message (format: tool_result role with tool_use_id)
                        messages.append({
                            "role": "tool",
                            "tool_use_id": tool_call_id,
                            "content": tool_result
                        })
                        logger.debug(f"✅ Added tool result for {tool_name}")
                    except Exception as e:
                        logger.error(f"❌ Tool execution failed: {e}", exc_info=True)
                        error_result = f"Error executing {tool_name}: {str(e)}"
                        
                        # Add error result message
                        messages.append({
                            "role": "tool",
                            "tool_use_id": tool_call_id,
                            "content": error_result,
                            "is_error": True
                        })
                        logger.debug(f"❌ Added error for {tool_name}")
                
                logger.debug(f"  Processed {len(tool_calls)} tool calls")
            
            # Max iterations reached without final answer
            logger.warning(f"⚠️ Agent reached max iterations ({max_iterations}) without final answer")
            duration = time.time() - start_time
            return FollowUpResponse(
                content="I need more information to answer your question. Could you please provide additional details?",
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
        """Execute tool calls via MCP tools
        
        Tool calls are executed via MCP servers (e.g., analysis_details_server)
        Returns the tool result as a string to be added to the message history.
        """
        try:
            logger.info(f"🔧 Executing tool via MCP: {tool_name} with input: {tool_input}")
            
            # Inject current session_id if tool requires it and execution context is available
            if "session_id" in tool_input and hasattr(self, '_execution_context'):
                context = self._execution_context
                if context.get("session_id"):
                    tool_input["session_id"] = context["session_id"]
                    logger.debug(f"  Using session_id from context: {context['session_id']}")
            
            # Execute tool via MCP client
            from ...integrations.mcp.mcp_client import mcp_client
            
            if not mcp_client:
                logger.error(f"❌ MCP client not initialized")
                return f"Error: MCP client not initialized"
            
            # Call the tool via the MCP client
            # Tool name format: "server_name__tool_name" (e.g., "analysis-details__get_execution")
            result = await mcp_client.call_tool(tool_name, tool_input)
            
            # Extract text content from CallToolResult
            result_text = ""
            if hasattr(result, 'content') and result.content:
                # result.content is a list of content objects (TextContent, etc.)
                for content in result.content:
                    if hasattr(content, 'text'):
                        text = content.text
                        # If text is JSON string, pretty-print it
                        try:
                            import json
                            parsed = json.loads(text)
                            text = json.dumps(parsed, indent=2)
                        except (json.JSONDecodeError, ValueError):
                            # Not JSON, use as-is
                            pass
                        result_text += text
                    else:
                        result_text += str(content)
            else:
                result_text = str(result)
            
            logger.info(f"✅ Tool {tool_name} executed successfully")
            logger.debug(f"  Result: {result_text[:200]}..." if len(result_text) > 200 else f"  Result: {result_text}")
            
            return result_text
                
        except Exception as e:
            logger.error(f"❌ Tool execution failed: {e}", exc_info=True)
            return f"Error executing {tool_name}: {str(e)}"
