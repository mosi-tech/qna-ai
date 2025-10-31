#!/usr/bin/env python3
"""
Financial Analysis Service - QnA analysis with MCP tool calling
"""

import json
import logging
import os
import sys
from datetime import datetime
from typing import Dict, Any, Optional, List

# Import shared services
shared_path = os.path.join(os.path.dirname(__file__), '..', '..', '..')
sys.path.insert(0, shared_path)
from shared.llm import create_analysis_llm, LLMService
from shared.services.base_service import BaseService

# Import safe JSON utilities
utils_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "utils")
sys.path.append(utils_path)
from utils.json_utils import safe_json_loads

# Import verification service
from .verification import StandaloneVerificationService
from .verification.integration_helpers import VerificationIntegrationHelper

class AnalysisService(BaseService):
    """Financial question analysis service with MCP integration"""
    
    _verification_prompt_template = None
    
    def __init__(self, llm_service: Optional[LLMService] = None):
        super().__init__(llm_service=llm_service, service_name="analysis")
        self._load_verification_prompt()
        
        # Initialize verification service at startup
        self.verification_service = self._initialize_verification_service()
        self.verification_helper = VerificationIntegrationHelper()
        
        # Max attempts for write_and_validate (checked in message filter)
        self.max_write_and_validate_attempts = 4
    
    def _create_default_llm(self) -> LLMService:
        """Create default LLM service for analysis"""
        return create_analysis_llm()
    
    @classmethod
    def _load_verification_prompt(cls):
        """Load verification prompt from config file (lazy load)"""
        if cls._verification_prompt_template is None:
            prompt_path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                "..",
                "config",
                "verification-prompt.txt"
            )
            try:
                with open(prompt_path, 'r', encoding='utf-8') as f:
                    cls._verification_prompt_template = f.read()
                logging.getLogger(__name__).debug("✅ Loaded verification prompt from config")
            except FileNotFoundError:
                logging.getLogger(__name__).warning(f"⚠️ Verification prompt config not found: {prompt_path}")
                cls._verification_prompt_template = "Before we proceed, I need to verify something important:\n\n**Question**: {question}\n\nPlease check if the script correctly answers the question."
    
    def _initialize_verification_service(self):
        """Initialize verification service at startup"""
        if self._verification_prompt_template and StandaloneVerificationService:
            try:
                verification_service = StandaloneVerificationService(self._verification_prompt_template)
                
                # Log startup initialization summary
                available_services = len([s for s in verification_service.llm_services if s is not None])
                total_services = len(verification_service.llm_services)
                
                if available_services > 0:
                    configs_summary = [f"{c['provider']}/{c['model']}" for c in verification_service.verification_configs]
                    self.logger.info(f"✅ Verification service initialized at startup: {available_services}/{total_services} services available")
                    self.logger.debug(f"Verification configs: {configs_summary}")
                else:
                    self.logger.warning(f"⚠️ Verification service initialized but no LLM services available - check API keys")
                
                return verification_service
                
            except Exception as e:
                self.logger.error(f"❌ Failed to initialize verification service at startup: {e}")
                return None
        else:
            self.logger.warning("⚠️ No verification prompt available, verification service not initialized")
            return None
    
    def _get_verification_service(self):
        """Get verification service (already initialized at startup)"""
        return self.verification_service
    
    
    # === ANALYSIS WORKFLOW ===
    
    async def warm_cache(self, model: str, enable_caching: bool = True) -> bool:
        """Warm up cache for faster subsequent requests"""
        try:
            self.logger.info(f"🔥 Warming cache for {model}")
            
            if enable_caching:
                # Use LLM service's built-in cache warming
                success = await self.llm_service.warm_cache(model)
                if success:
                    self.logger.info(f"✅ Cache warmed successfully for {model}")
                    return True
                else:
                    self.logger.warning(f"⚠️ Cache warm failed for {model}")
                    return False
            else:
                self.logger.info("🚫 Cache warming skipped (caching disabled)")
                return True
                
        except Exception as e:
            self.logger.error(f"❌ Cache warm error for {model}: {e}")
            return False
    
    async def call_llm_with_tools(self, model: str, messages: List[Dict[str, str]], enable_caching: bool = False) -> Dict[str, Any]:
        """Call LLM with tool calling capability using provided messages"""
        try:
            # Ensure MCP tools are loaded
            await self.llm_service.ensure_tools_loaded()
            
            # Get system prompt from service configuration
            system_prompt = await self.get_system_prompt()
            
            result = await self.llm_service.make_request(
                messages=messages,
                model=model,
                system_prompt=system_prompt,
                enable_caching=enable_caching
            )
            
            if not result.get("success"):
                return result
            
            # Handle tool calls if present
            tool_calls = result.get("tool_calls", [])
            
            if tool_calls:
                self.logger.info(f"🔧 Processing {len(tool_calls)} tool calls")
                
                # Execute tools
                tool_result = await self._handle_tool_calls(tool_calls)
                
                if tool_result.get("success"):
                    # Start conversation loop with initial tool results
                    all_tool_calls = tool_calls
                    
                    all_tool_results = tool_result.get("tool_results", [])
                    
                    return await self._conversation_loop(
                        model, messages, all_tool_calls, all_tool_results, enable_caching
                    )
                else:
                    self.logger.error(f"❌ Tool execution failed: {tool_result.get('error')}")
                    return {
                        "success": False,
                        "content": result.get("content", ""),
                        "provider": self.llm_service.provider_type,
                        "tool_error": tool_result.get("error"),
                        "error": f"Tool execution failed: {tool_result.get('error')}"
                    }
            else:
                # No tool calls - parse response directly for structured content
                self.logger.info("📝 No tool calls detected, parsing response directly")
                final_content = result.get("content", "")
                
                parsed_response = self._parse_structured_response(final_content)
                
                if parsed_response.get("structured_response_found", True):
                    # Found a structured response (reuse decision or script generation)
                    return parsed_response
                else:
                    # No structured response found - may need tool calls, start conversation loop
                    self.logger.info("🔄 No structured response found, starting conversation loop")
                    return await self._conversation_loop(
                        model, messages, [], [], enable_caching
                    )
                
        except Exception as e:
            self.logger.error(f"❌ LLM call error: {e}")
            return {
                "success": False,
                "error": str(e),
                "provider": self.llm_service.provider_type
            }
    
    async def _handle_tool_calls(self, tool_calls: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Execute tool calls using MCP integration"""
        try:
            self.logger.info(f"🔧 Executing {len(tool_calls)} tool calls")

            # Use MCP integration for validation and execution
            from integrations.mcp.mcp_integration import MCPIntegration
            
            if not hasattr(self, 'mcp_integration'):
                self.mcp_integration = MCPIntegration()
                await self.mcp_integration.ensure_mcp_initialized()
            
            # Validate MCP functions (tool filtering handled by SimplifiedMCPLoader)
            validation = self.mcp_integration.validate_mcp_functions(tool_calls, [])
            
            if not validation.get("all_valid", False):
                invalid_functions = [
                    result["function"] for result in validation["validation_results"] 
                    if result["status"] != "allowed"
                ]
                self.logger.warning(f"🚫 Invalid functions detected: {invalid_functions}")
                return {
                    "success": False,
                    "error": f"Invalid functions not allowed: {', '.join(invalid_functions)}",
                    "provider": self.llm_service.provider_type
                }
            
            # Execute the tool calls using MCP integration
            mcp_result = await self.mcp_integration.generate_tool_calls_only(tool_calls)
            
            if mcp_result.get("success"):
                self.logger.info(f"✅ All {len(tool_calls)} tool calls executed successfully")
                return {
                    "success": True,
                    "tool_calls": tool_calls,
                    "tool_results": mcp_result.get("tool_results", []),
                    "provider": self.llm_service.provider_type
                }
            else:
                self.logger.error(f"❌ MCP tool execution failed: {mcp_result.get('error')}")
                return {
                    "success": False,
                    "error": mcp_result.get("error", "MCP tool execution failed"),
                    "provider": self.llm_service.provider_type
                }
            
        except Exception as e:
            self.logger.error(f"❌ Tool execution error: {e}")
            return {
                "success": False,
                "error": str(e),
                "provider": self.llm_service.provider_type
            }
    
    def _check_script_generation(self, tool_results: List[Dict[str, Any]]) -> bool:
        """Check if script generation was completed"""
        try:
            # Look for write operations that created Python files
            for result in tool_results:
                if result.get("success") and result.get("function"):
                    func_name = result["function"]
                    
                    # Check for file write operations
                    if "write_file" in func_name.lower() and result.get("result"):
                        # Parse the result content
                        result_content = result["result"]
                        
                        # Handle CallToolResult structure
                        if hasattr(result_content, 'content') and result_content.content:
                            # Extract text from CallToolResult
                            try:
                                text_content = result_content.content[0].text
                                self.logger.debug(f"Raw text content type: {type(text_content)}")
                                self.logger.debug(f"Raw text content repr: {repr(text_content[:200])}")
                                
                                # Clean the text and try parsing
                                cleaned_text = text_content.strip()
                                parsed_result = safe_json_loads(cleaned_text, default={})
                                
                                if (parsed_result.get("success") and 
                                    parsed_result.get("absolute_path", "").endswith(".py") and
                                    parsed_result.get("size", 0) > 1000):
                                    self.logger.info(f"✅ Script generation detected: {parsed_result.get('absolute_path')}")
                                    return True
                            except json.JSONDecodeError as e:
                                self.logger.error(f"JSON decode error: {e}")
                                self.logger.error(f"Failed text: {repr(text_content)}")
                                # Fallback pattern matching
                                if (".py" in text_content and "success" in text_content and "size" in text_content):
                                    self.logger.info("✅ Script generation detected (fallback)")
                                    return True
                            except (AttributeError, IndexError) as e:
                                self.logger.error(f"Structure error: {e}")
                                pass
                        
                        elif isinstance(result_content, dict):
                            # Direct dictionary access
                            if (result_content.get("success") and 
                                result_content.get("absolute_path", "").endswith(".py") and
                                result_content.get("size", 0) > 1000):  # Substantial file size
                                return True
                        elif isinstance(result_content, str):
                            # JSON string - parse it
                            try:
                                parsed_result = safe_json_loads(result_content, default={})
                                if (parsed_result.get("success") and 
                                    parsed_result.get("absolute_path", "").endswith(".py") and
                                    parsed_result.get("size", 0) > 1000):
                                    return True
                            except json.JSONDecodeError:
                                # Fallback to string checking
                                if (".py" in result_content and 
                                    "success" in result_content and
                                    len(result_content) > 200):
                                    return True
            return False
        except:
            return False
    
    async def _conversation_loop(self, model: str, messages: List[Dict[str, Any]], 
                               all_tool_calls: List[Dict[str, Any]], all_tool_results: List[Dict[str, Any]], 
                               enable_caching: bool = False) -> Dict[str, Any]:
        """Main conversation loop that continues until LLM stops calling tools"""
        try:
            # Extract original question from first user message
            original_question = ""
            for msg in messages:
                if msg.get("role") == "user":
                    content = msg.get("content", "")
                    if isinstance(content, str):
                        original_question = content
                    elif isinstance(content, list):
                        # Handle Anthropic content array format
                        for block in content:
                            if isinstance(block, dict) and block.get("type") == "text":
                                original_question = block.get("text", "")
                                break
                    if original_question:
                        break
            
            # Track how many tool calls we've processed to know what's "recent"
            processed_tool_calls = 0
            while True:
                # Get the most recent unprocessed tool calls/results
                if processed_tool_calls == 0:
                    # First iteration - use initial tool calls/results
                    recent_tool_calls = all_tool_calls
                    recent_tool_results = all_tool_results
                else:
                    # Subsequent iterations - use only the newly added ones
                    recent_tool_calls = all_tool_calls[processed_tool_calls:]
                    recent_tool_results = all_tool_results[processed_tool_calls:]
                
                processed_tool_calls = len(all_tool_calls)
                
                continuation_result = await self._continue_conversation(
                    model, messages, recent_tool_calls, recent_tool_results, enable_caching, original_question
                )
                
                # Check if continuation failed
                if not continuation_result["success"]:
                    return {
                        "success": False,
                        "provider": self.llm_service.provider_type,
                        "task_completed": False,
                        "response_type": "error",
                        "data": {
                            "error_type": "conversation_failed",
                            "message": continuation_result.get("error", "Conversation continuation failed"),
                            "tool_calls": all_tool_calls,
                            "tool_results": all_tool_results
                        },
                        "raw_content": continuation_result.get("content", ""),
                        "error": continuation_result.get("error", "Conversation continuation failed")
                    }
                
                # Check if LLM wants to make more tool calls
                new_tool_calls = continuation_result.get("tool_calls", [])
                if new_tool_calls:
                    # Execute new tools
                    tool_execution_result = await self._handle_tool_calls(new_tool_calls)
                    
                    if not tool_execution_result["success"]:
                        return {
                            "success": False,
                            "provider": self.llm_service.provider_type,
                            "task_completed": False,
                            "response_type": "error",
                            "data": {
                                "error_type": "tool_execution_failed",
                                "message": tool_execution_result.get("error", "Tool execution failed"),
                                "tool_calls": all_tool_calls,
                                "tool_results": all_tool_results
                            },
                            "raw_content": "",
                            "error": tool_execution_result.get("error", "Tool execution failed")
                        }
                    
                    # Accumulate results
                    all_tool_calls.extend(new_tool_calls)
                    all_tool_results.extend(tool_execution_result["tool_results"])
                    
                    self.logger.info(f"🔄 Continuing conversation loop (total tool calls: {len(all_tool_calls)})")
                    continue
                else:
                    # No more tool calls - parse response for structured content
                    final_content = continuation_result.get("content", "")
                    parsed_response = self._parse_structured_response(final_content)
                    
                    if parsed_response.get("structured_response_found", True):
                        # Found a structured response (reuse decision or script generation)
                        return parsed_response
                    else:
                        # No structured response found
                        self.logger.warning("❌ Task incomplete: No reuse decision or script generation response found")
                        return {
                            "success": False,
                            "provider": self.llm_service.provider_type,
                            "task_completed": False,
                            "response_type": "error",
                            "data": {
                                "error_type": "no_structured_response",
                                "message": "LLM response did not contain reuse decision or script generation JSON"
                            },
                            "raw_content": final_content,
                            "error": "LLM response did not contain reuse decision or script generation JSON"
                        }
                        
        except Exception as e:
            self.logger.error(f"❌ Conversation loop error: {e}")
            return {
                "success": False,
                "error": f"Conversation error: {str(e)}"
            }
    
    
    def _filter_messages_for_context(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Filter messages by scanning in REVERSE order (simpler and cleaner).
        Keep:
        - Most recent write_and_validate pair (stop after finding first)
        - All get_function_docstring pairs
        - Most recent verification message (only if AFTER write_and_validate)
        - Initial conversation messages before first tool call
        Then reconstruct in ORIGINAL order
        """
        if not messages:
            return messages

        self.logger.debug(f"Starting REVERSE filter with {len(messages)} messages")

        indices_to_keep = set()
        write_and_validate_index = None
        verification_index = None
        verification_failure_index = None
        unsuccessful_write_and_validate_count = 0

        # Scan in REVERSE order to find most recent items first
        i = len(messages) - 1
        while i >= 0:
            msg = messages[i]
            role = msg.get("role")

            # Track verification failure message (only if it's the last message)
            if verification_failure_index is None and role == "user" and i == len(messages) - 1:
                content = msg.get("content", [])
                if isinstance(content, list):
                    for block in content:
                        if isinstance(block, dict) and block.get("type") == "text":
                            text = block.get("text", "")
                            if "Multi-model verification FAILED" in text:
                                verification_failure_index = i
                                self.logger.debug(f"Found verification failure message at index {i} (last message)")
                                break
                elif isinstance(content, str):
                    if "Multi-model verification FAILED" in content:
                        verification_failure_index = i
                        self.logger.debug(f"Found verification failure message at index {i} (last message)")

            # Track verification message (don't add to indices yet - validate placement later)
            if verification_index is None and role == "user":
                content = msg.get("content", [])
                if isinstance(content, list):
                    for block in content:
                        if isinstance(block, dict) and block.get("type") == "text":
                            text = block.get("text", "").lower()
                            if "verification" in text or "before we proceed" in text:
                                verification_index = i
                                self.logger.debug(f"Found verification message at index {i}")
                                break

            # Check for assistant messages with tool calls
            if role == "assistant":
                if self._contains_tool_calls(msg):
                    # Check if this is write_and_validate or docstring
                    has_write_validate = self.llm_service.provider.message_contains_function(msg, "write_and_validate")
                    has_docstring = self.llm_service.provider.message_contains_function(msg, "get_function_docstring")

                    if has_write_validate:
                        # Check if this attempt was unsuccessful
                        tool_result_role = self.llm_service.provider.get_tool_result_role()
                        if i + 1 < len(messages) and messages[i + 1].get("role") == tool_result_role:
                            tool_result = messages[i + 1]
                            if not self._is_validation_successful(tool_result):
                                unsuccessful_write_and_validate_count += 1
                                self.logger.debug(f"Found unsuccessful write_and_validate at index {i} (count: {unsuccessful_write_and_validate_count})")
                        
                        # Keep only the most recent write_and_validate pair
                        if write_and_validate_index is None:
                            write_and_validate_index = i
                            indices_to_keep.add(i)
                            # Add tool result (next message)
                            if i + 1 < len(messages) and messages[i + 1].get("role") == tool_result_role:
                                indices_to_keep.add(i + 1)
                            self.logger.debug(f"Most recent write_and_validate at index {i}")

                    elif has_docstring:
                        # Keep all docstring pairs
                        indices_to_keep.add(i)
                        tool_result_role = self.llm_service.provider.get_tool_result_role()
                        if i + 1 < len(messages) and messages[i + 1].get("role") == tool_result_role:
                            indices_to_keep.add(i + 1)
                        self.logger.debug(f"Docstring call at index {i}")

            i -= 1

        # Check if unsuccessful write_and_validate limit exceeded
        if unsuccessful_write_and_validate_count >= self.max_write_and_validate_attempts:
            error_msg = f"Maximum unsuccessful write_and_validate attempts ({self.max_write_and_validate_attempts}) exceeded in conversation. This usually indicates the script generation is not converging. Please try rephrasing your question or breaking it into smaller parts."
            self.logger.error(f"❌ {error_msg} (found {unsuccessful_write_and_validate_count} unsuccessful attempts)")
            raise ValueError(error_msg)

        # Always keep verification failure message (most recent one)
        if verification_failure_index is not None:
            indices_to_keep.add(verification_failure_index)
            self.logger.debug(f"Keeping verification failure message at {verification_failure_index}")

        # Validate verification message placement
        # Verification should only be kept if it comes AFTER write_and_validate
        if verification_index is not None:
            if write_and_validate_index is not None:
                if verification_index > write_and_validate_index:
                    indices_to_keep.add(verification_index)
                    self.logger.debug(f"Keeping verification at {verification_index} (after write_and_validate at {write_and_validate_index})")
                else:
                    self.logger.debug(f"Removing verification at {verification_index} (before write_and_validate at {write_and_validate_index})")
            else:
                # No write_and_validate found, keep verification anyway
                indices_to_keep.add(verification_index)
                self.logger.debug(f"Keeping verification at {verification_index} (no write_and_validate found)")

        # Add all INITIAL messages (user and assistant) until we hit the first tool call
        # This preserves the conversational context at the beginning
        for i, msg in enumerate(messages):
            role = msg.get("role")
            if role == "user":
                indices_to_keep.add(i)
            elif role == "assistant":
                if self._contains_tool_calls(msg):
                    # Stop here - we've hit the tool interaction phase
                    break
                else:
                    # Non-tool assistant message at start - keep it
                    indices_to_keep.add(i)

        # Build filtered list in ORIGINAL order
        filtered_messages = [messages[i] for i in range(len(messages)) if i in indices_to_keep]

        self.logger.debug(f"Filtered {len(messages)} → {len(filtered_messages)} messages")
        self.logger.debug(f"Kept indices: {sorted(indices_to_keep)}")

        return filtered_messages
    
    def _contains_tool_calls(self, message_content) -> bool:
        """Check if message content contains tool calls using provider-specific logic"""
        return self.llm_service.provider.contains_tool_calls(message_content)
    
    def _is_write_and_validate_tool_result(self, tool_call: Dict[str, Any]) -> bool:
        """Check if a tool call is a write_and_validate function"""
        if not tool_call:
            return False
        
        function_info = tool_call.get("function", {})
        if isinstance(function_info, dict):
            function_name = function_info.get("name", "")
        else:
            function_name = str(function_info)
        
        # Check if the function name ends with write_and_validate
        return function_name.endswith("write_and_validate")


    async def _continue_conversation(self, model: str, messages: List[Dict[str, Any]], 
                                   current_tool_calls: List[Dict[str, Any]], current_tool_results: List[Dict[str, Any]],
                                   enable_caching: bool = False, original_question: str = "") -> Dict[str, Any]:
        """Continue conversation after tool execution with proper formatting"""
        try:
            # Add assistant message with current tool calls using provider-specific formatting
            assistant_message = self.llm_service.provider.format_assistant_message_with_tool_calls(current_tool_calls)
            messages.append(assistant_message)

            formatted_tool_results = self.llm_service.provider.format_tool_results(current_tool_calls, current_tool_results)
            
            # Add tool results using provider's formatting function
            if enable_caching and self.llm_service.provider_type == "anthropic":
                # Define functions that are allowed for caching
                cacheable_functions = {
                    # "get_function_docstring": "1h",
                    "write_and_validate": "5m"
                }
                
                # Add caching metadata to tool results for cacheable functions
                for i, tool_call in enumerate(current_tool_calls):
                    function_name = tool_call.get("function", "").get("name", "")
                    # Strip MCP server prefixes to get base function name
                    base_function_name = function_name.split("__")[-1] if "__" in function_name else function_name
                    
                    if base_function_name in cacheable_functions:
                        formatted_tool_results["content"][i]["cache_control"] = {"type": "ephemeral", "ttl": cacheable_functions[base_function_name]}
                        self.logger.debug(f"Added caching for function: {function_name}")
                
            
            messages.append(formatted_tool_results)
            
            # Check if last tool call is write_and_validate AND its result success is true
            if current_tool_calls and current_tool_results and original_question:
                last_tool_call = current_tool_calls[-1]
                if self._is_write_and_validate_tool_result(last_tool_call):
                    # Check if the last tool result indicates success
                    last_tool_result = current_tool_results[-1] if current_tool_results else None
                    if last_tool_result and self._is_validation_successful(last_tool_result):
                        self.logger.info("📋 write_and_validate succeeded, starting multi-model verification")
                        
                        verification_result = None
                        verification_attempted = False
                        
                        # Check if verification is available
                        if not self.verification_helper:
                            self.logger.warning("⚠️ Multi-model verification not available, skipping")
                        else:
                            # Extract script content from tool result
                            script_content = self.verification_helper.extract_script_content_from_tool_result(last_tool_result)
                            
                            if script_content:
                                # Run multi-model verification
                                verification_service = self._get_verification_service()
                                if verification_service:
                                    try:
                                        verification_attempted = True
                                        verification_result = await verification_service.verify_script(
                                            question=original_question,
                                            script_content=script_content
                                        )
                                        
                                        # Create handoff message based on verification result
                                        handoff_message = self.verification_helper.create_verification_handoff_message(
                                            verification_result, original_question
                                        )
                                        messages.append(handoff_message)
                                        
                                        # Log verification summary
                                        summary = self.verification_helper.format_model_results_summary(verification_result)
                                        self.logger.info(f"🔍 Multi-model verification result: {'APPROVED' if verification_result.verified else 'REJECTED'}")
                                        self.logger.debug(f"Verification details:\n{summary}")
                                        
                                    except Exception as e:
                                        self.logger.error(f"❌ Multi-model verification failed: {e}")
                                        raise
                                        
                                else:
                                    self.logger.warning("⚠️ Verification service not available, skipping verification")
                            else:
                                self.logger.warning("⚠️ Could not extract script content, skipping verification")
                        
                        # CRITICAL: Only raise exception if verification was not attempted or did not complete
                        if verification_attempted and verification_result:
                            # Verification was attempted and completed - continue conversation regardless of result
                            if verification_result.verified:
                                self.logger.info("✅ Multi-model verification PASSED - continuing conversation")
                            else:
                                rejection_reasons = []
                                for model_result in verification_result.model_results:
                                    if model_result.verdict == "REJECT":
                                        rejection_reasons.extend(model_result.critical_issues)
                                
                                self.logger.warning(f"⚠️ Multi-model verification FAILED but continuing conversation. Issues: {'; '.join(set(rejection_reasons))}")
                        elif verification_attempted and not verification_result:
                            # Verification was attempted but failed to produce a result
                            error_msg = "Multi-model verification FAILED - no verification result produced"
                            self.logger.error(f"❌ {error_msg}")
                            raise ValueError(error_msg)
                        elif not verification_attempted:
                            # Verification was not attempted - this could be a configuration issue
                            error_msg = "Multi-model verification FAILED - verification system not available or not properly configured"
                            self.logger.error(f"❌ {error_msg}")
                            raise ValueError(error_msg)
                            
                    else:
                        self.logger.info("⚠️ write_and_validate failed or result unavailable. Continue with script generation")
            
            # Filter messages to keep only recent relevant tool interactions
            filtered_messages = self._filter_messages_for_context(messages)
            
            # Make request with filtered conversation context
            result = await self.llm_service.make_request(
                messages=filtered_messages,
                model=model,
                enable_caching=enable_caching
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Continue conversation error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _is_validation_successful(self, tool_result: Dict[str, Any]) -> bool:
        """Check if a validation tool result indicates success"""
        try:
            result_data = tool_result.get("result")
            if not result_data:
                return False
            
            # Handle CallToolResult structure (has .content attribute)
            if hasattr(result_data, 'content') and result_data.content:
                try:
                    text_content = result_data.content[0].text
                    parsed = safe_json_loads(text_content.strip(), default={})
                    # Check if validation_result.valid is true OR write_result.success is true
                    if parsed.get("validation_result", {}).get("valid"):
                        return True
                    if parsed.get("write_result", {}).get("success") and parsed.get("validation_result", {}).get("valid"):
                        return True
                    return False
                except (json.JSONDecodeError, AttributeError, IndexError):
                    return False
            
            # Handle different result formats
            if isinstance(result_data, dict):
                # Check for nested validation_result.valid
                if result_data.get("validation_result", {}).get("valid"):
                    return True
                # Check for top-level valid or success
                return result_data.get("valid", False) or result_data.get("success", False)
            elif isinstance(result_data, str):
                # Try to parse as JSON
                try:
                    parsed = safe_json_loads(result_data, default={})
                    # Check for nested validation_result.valid
                    if parsed.get("validation_result", {}).get("valid"):
                        return True
                    # Check for top-level valid or success
                    return parsed.get("valid", False) or parsed.get("success", False)
                except json.JSONDecodeError:
                    # Check for success indicators in string
                    return "valid" in result_data.lower() or "success" in result_data.lower()
            
            return False
        except Exception as e:
            self.logger.debug(f"Error checking validation success: {e}")
            return False
    
    def _parse_structured_response(self, content: str) -> Dict[str, Any]:
        """Parse LLM response for structured content (reuse decisions or script generation)"""
        try:
            # Check if this is a reuse decision
            reuse_decision = self._check_reuse_decision(content)
            if reuse_decision:
                self.logger.info("✅ Reuse decision made - existing analysis can be reused")
                return {
                    "success": True,
                    "provider": self.llm_service.provider_type,
                    "task_completed": True,
                    "response_type": "reuse_decision",
                    "data": reuse_decision,
                    "raw_content": content
                }
            
            # Check if this is a script generation response
            script_generation_response = self._check_script_generation_response(content)
            if script_generation_response:
                if script_generation_response.get("status") == "success":
                    self.logger.info("✅ Script generation completed successfully")
                    return {
                        "success": True,
                        "provider": self.llm_service.provider_type,
                        "task_completed": True,
                        "response_type": "script_generation",
                        "data": script_generation_response,
                        "raw_content": content
                    }
                else:  # status == "failed"
                    self.logger.error("❌ Script generation failed")
                    return {
                        "success": False,
                        "provider": self.llm_service.provider_type,
                        "task_completed": False,
                        "response_type": "script_generation_failed",
                        "data": script_generation_response,
                        "raw_content": content,
                        "error": script_generation_response.get("final_error", "Script generation failed")
                    }
            
            # No structured response found
            return {
                "success": False,
                "structured_response_found": False,
                "message": "No structured response found"
            }
            
        except Exception as e:
            self.logger.error(f"❌ Error parsing structured response: {e}")
            return {
                "success": False,
                "error": f"Error parsing response: {str(e)}"
            }

    def _check_script_generation_response(self, content: str) -> Optional[Dict[str, Any]]:
        """Check if content contains a script generation JSON response or Python script"""
        try:
            import re
            
            # First, look for JSON code blocks in the content
            json_pattern = r'```json\s*(.*?)\s*```'
            json_matches = re.findall(json_pattern, content, re.DOTALL)
            
            for json_text in json_matches:
                try:
                    parsed_json = safe_json_loads(json_text.strip(), default={})
                    
                    # Check if this is a script generation response
                    if "script_generation" in parsed_json:
                        script_data = parsed_json["script_generation"]
                        if script_data.get("status") == "success":
                            self.logger.info(f"📝 Script generation response found: {script_data.get('script_name')}")
                            return script_data
                        elif script_data.get("status") == "failed":
                            self.logger.info("❌ Script generation failed response found")
                            return script_data
                            
                except json.JSONDecodeError as e:
                    self.logger.debug(f"Failed to parse JSON block: {e}")
                    continue
            
            # If no JSON blocks found, try parsing the entire content as JSON
            try:
                parsed_content = safe_json_loads(content.strip(), default={})
                if "script_generation" in parsed_content:
                    script_data = parsed_content["script_generation"]
                    if script_data.get("status") in ["success", "failed"]:
                        return script_data
            except json.JSONDecodeError:
                pass
            
            # If no JSON structured response found, look for Python scripts in markdown
            python_pattern = r'```python\s*(.*?)\s*```'
            python_matches = re.findall(python_pattern, content, re.DOTALL)
            
            if python_matches:
                # Found Python script - create script generation response
                script_content = python_matches[0].strip()
                if len(script_content) > 100:  # Ensure it's a substantial script
                    self.logger.info("📝 Python script found in markdown content")
                    return {
                        "status": "success",
                        "script_content": script_content,
                        "script_name": "generated_analysis.py",
                        "analysis_description": "Python script for financial analysis",
                        "source": "markdown_extraction"
                    }
                
            return None
            
        except Exception as e:
            self.logger.debug(f"Error checking script generation response: {e}")
            return None

    def _check_reuse_decision(self, content: str) -> Optional[Dict[str, Any]]:
        """Check if content contains a reuse decision JSON response"""
        try:
            # Look for JSON code blocks in the content
            import re
            
            # Extract JSON from markdown code blocks
            json_pattern = r'```json\s*(.*?)\s*```'
            json_matches = re.findall(json_pattern, content, re.DOTALL)
            
            for json_text in json_matches:
                try:
                    parsed_json = safe_json_loads(json_text.strip(), default={})
                    
                    # Check if this is a reuse decision
                    if "reuse_decision" in parsed_json:
                        reuse_data = parsed_json["reuse_decision"]
                        if reuse_data.get("should_reuse") is True:
                            self.logger.info(f"🔄 Reuse decision found: {reuse_data.get('existing_function_name')}")
                            return reuse_data
                        elif reuse_data.get("should_reuse") is False:
                            self.logger.info("🆕 New analysis required - no reusable analysis found")
                            return None
                            
                except json.JSONDecodeError as e:
                    self.logger.debug(f"Failed to parse JSON block: {e}")
                    continue
            
            # If no JSON blocks found, try parsing the entire content as JSON
            try:
                parsed_content = safe_json_loads(content.strip(), default={})
                if "reuse_decision" in parsed_content:
                    reuse_data = parsed_content["reuse_decision"]
                    if reuse_data.get("should_reuse") is True:
                        return reuse_data
            except json.JSONDecodeError:
                pass
                
            return None
            
        except Exception as e:
            self.logger.debug(f"Error checking reuse decision: {e}")
            return None

    def _extract_script_info(self, tool_results: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Extract script information from tool results"""
        try:
            for result in tool_results:
                if result.get("success") and "write" in result.get("function", "").lower():
                    result_content = result.get("result", {})
                    
                    # Handle CallToolResult structure
                    if hasattr(result_content, 'content') and result_content.content:
                        try:
                            text_content = result_content.content[0].text
                            self.logger.debug(f"Extract script - Raw text: {repr(text_content[:200])}")
                            
                            cleaned_text = text_content.strip()
                            parsed_result = json.loads(cleaned_text)
                            
                            # Look for filename and path info
                            saved_filename = parsed_result.get("saved_filename")
                            
                            if saved_filename and saved_filename.endswith('.py'):
                                return {
                                    "filename": saved_filename,
                                    "size": parsed_result.get("size", 0),
                                    "success": parsed_result.get("success", False)
                                }
                        except (json.JSONDecodeError, AttributeError, IndexError) as e:
                            self.logger.debug(f"Extract script JSON error: {e}")
                            continue
                    
                    elif isinstance(result_content, dict):
                        saved_filename = result_content.get("filename") or result_content.get("file_path")
                        content = result_content.get("content") or result_content.get("file_content")
                        
                        if saved_filename and content and saved_filename.endswith('.py'):
                            return {
                                "filename": saved_filename,
                                "content": content,
                                "size": len(str(content))
                            }
            return None
        except Exception as e:
            self.logger.error(f"Error extracting script info: {e}")
            return None
    
    # === MAIN ANALYSIS ENTRY POINT ===
    
    async def analyze_question(self, question: str, messages: List[Dict[str, str]] = None, model: str = None, enable_caching: bool = True) -> Dict[str, Any]:
        """Main entry point for financial question analysis"""
        try:
            if not model:
                model = self.llm_service.default_model
            
            self.logger.info(f"🤔 Analyzing question with {self.llm_service.provider_type.upper()}: {question[:100]}...")
            
            # System prompt should be automatically handled by LLMService
            
            # Use provided messages or create fallback message
            if messages:
                analysis_messages = messages
                self.logger.info(f"📨 Using {len(messages)} provided messages")
            else:
                analysis_messages = [{
                    "role": "user",
                    "content": question
                }]
                self.logger.info("📨 Using fallback single message")
            
            # Call LLM with tools
            result = await self.call_llm_with_tools(model, analysis_messages, enable_caching)
            
            if result.get("success"):
                # Format the successful response based on new standardized format
                response_data = {
                    "question": question,
                    "provider": result["provider"],
                    "model": model,
                    "response_type": result.get("response_type"),
                    "raw_content": result.get("raw_content", ""),
                    "timestamp": datetime.now().isoformat()
                }
                
                # Add completion information
                if result.get("task_completed"):
                    response_data["task_completed"] = result["task_completed"]
                
                # Always use consistent key structure regardless of response type
                response_data["analysis_result"] = result.get("data", {})
                
                self.logger.info(f"✅ Question analyzed successfully using {result['provider']} - Type: {result.get("response_type")}")
                
                return {
                    "success": True,
                    "data": response_data
                }
            else:
                self.logger.error(f"❌ Question analysis failed: {result.get('error')}")
                return {
                    "success": False,
                    "error": result.get("error", "Unknown error"),
                    "provider": result.get("provider", self.llm_service.provider_type),
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            self.logger.error(f"❌ Analysis error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    # === LIFECYCLE MANAGEMENT ===
    
    async def close_sessions(self):
        """Cleanup method for server shutdown"""
        self.logger.info("Closing analysis service sessions...")
        # Note: MCP client cleanup is handled by the mcp_client module
        self.logger.info("Cleaned up analysis service")

# Factory function to create analysis service
def create_analysis_service(llm_service: Optional[LLMService] = None) -> AnalysisService:
    """Create analysis service instance"""
    return AnalysisService(llm_service)

# Note: Convenience functions removed - use AnalysisService instance directly