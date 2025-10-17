#!/usr/bin/env python3
"""
Financial Analysis Service - QnA analysis with MCP tool calling
"""

import json
import logging
import os
from datetime import datetime
from typing import Dict, Any, Optional, List

from llm import create_analysis_llm, LLMService
from .base_service import BaseService

class AnalysisService(BaseService):
    """Financial question analysis service with MCP integration"""
    
    def __init__(self, llm_service: Optional[LLMService] = None):
        super().__init__(llm_service=llm_service, service_name="analysis")
    
    def _create_default_llm(self) -> LLMService:
        """Create default LLM service for analysis"""
        return create_analysis_llm()
    
    
    def _get_default_system_prompt(self) -> str:
        """Default system prompt for analysis service"""
        return "You are a helpful financial analysis assistant that generates tool calls for financial data analysis."
    
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
                                parsed_result = json.loads(cleaned_text)
                                
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
                                parsed_result = json.loads(result_content)
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
    
    def _check_validation_completion(self, tool_results: List[Dict[str, Any]]) -> bool:
        """Check if validation process was completed"""
        try:
            # Look for validation tool calls (including MCP server prefixes)
            validation_tools = [
                "validate_python_script",
                "validate_workflow_step", 
                "validate_template_variables",
                "validate_complete_workflow",
                # Add MCP server prefix variations
                "validation-server__validate_python_script",
                "validation-server__validate_workflow_step",
                "validation-server__validate_template_variables", 
                "validation-server__validate_complete_workflow",
                "mcp__mcp-validation-server__validate_python_script",
                "mcp__mcp-validation-server__validate_workflow_step",
                "mcp__mcp-validation-server__validate_template_variables",
                "mcp__mcp-validation-server__validate_complete_workflow"
            ]
            
            for result in tool_results:
                if result.get("success") and result.get("function"):
                    func_name = result["function"]
                    
                    # Check if this was a validation tool
                    if any(val_tool in func_name for val_tool in validation_tools):
                        # Parse the result to check validation status
                        result_content = result.get("result")
                        
                        # Handle CallToolResult structure
                        if hasattr(result_content, 'content') and result_content.content:
                            # Extract text from CallToolResult
                            try:
                                text_content = result_content.content[0].text
                                self.logger.debug(f"Validation - Raw text content type: {type(text_content)}")
                                self.logger.debug(f"Validation - Raw text content repr: {repr(text_content[:200])}")
                                
                                # Clean the text and try parsing
                                cleaned_text = text_content.strip()
                                parsed_result = json.loads(cleaned_text)
                                
                                if parsed_result.get("valid") is not None:
                                    self.logger.info(f"✅ Validation completed: {func_name} - Valid: {parsed_result.get('valid')}")
                                    return True
                            except json.JSONDecodeError as e:
                                self.logger.error(f"Validation JSON decode error: {e}")
                                self.logger.error(f"Validation failed text: {repr(text_content)}")
                                # Fallback pattern matching
                                if any(keyword in text_content.lower() for keyword in ["valid", "validation", "executed successfully"]):
                                    self.logger.info(f"✅ Validation completed (fallback): {func_name}")
                                    return True
                            except (AttributeError, IndexError) as e:
                                self.logger.error(f"Validation structure error: {e}")
                                pass
                        
                        elif isinstance(result_content, dict):
                            # Direct dictionary access
                            if result_content.get("valid") is not None:
                                self.logger.info(f"✅ Validation completed: {func_name} - Valid: {result_content.get('valid')}")
                                return True
                        elif isinstance(result_content, str):
                            # JSON string - parse it
                            try:
                                parsed_result = json.loads(result_content)
                                if parsed_result.get("valid") is not None:
                                    self.logger.info(f"✅ Validation completed: {func_name} - Valid: {parsed_result.get('valid')}")
                                    return True
                            except json.JSONDecodeError:
                                # Fallback - if it contains validation keywords
                                if any(keyword in result_content.lower() for keyword in ["valid", "validation", "executed successfully"]):
                                    self.logger.info(f"✅ Validation completed (fallback): {func_name}")
                                    return True
            
            return False
        except Exception as e:
            self.logger.error(f"❌ Error checking validation completion: {e}")
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
        """Filter messages to keep only recent relevant tool interactions and conversation flow for context"""
        try:
            # Always keep all messages for conversation flow
            if not messages:
                return messages
            
            # For conversation mode, we want to keep the natural flow of user/assistant messages
            # Check if this looks like conversation mode (alternating user/assistant without tool calls)
            # This check is provider-aware and delegates to provider implementation
            has_conversation_flow = False
            for i, msg in enumerate(messages):
                if (msg.get("role") == "assistant" and 
                    not self._contains_tool_calls(msg) and 
                    self.llm_service.provider.get_message_text_length(msg) > 50):  # Substantial assistant message without tools
                    has_conversation_flow = True
                    break
            
            if has_conversation_flow:
                # In conversation mode, keep all messages to preserve the natural flow
                self.logger.debug(f"Detected conversation mode - keeping all {len(messages)} messages for context")
                return messages
            
            # Original logic for tool simulation mode
            # Keep all user messages at the beginning of the conversation
            filtered_messages = []
            for msg in messages:
                if msg.get("role") == "user":
                    filtered_messages.append(msg)
                else:
                    break  # Stop at first non-user message
            
            # Find assistant messages (both with and without tool calls) and corresponding tool results
            tool_interaction_pairs = []
            non_tool_assistant_messages = []
            i = len(filtered_messages)  # Start after all user messages
            while i < len(messages):
                msg = messages[i]
                if msg.get("role") == "assistant":
                    if self._contains_tool_calls(msg):
                        # Look for the corresponding tool result message using provider-specific role
                        tool_result_role = self.llm_service.provider.get_tool_result_role()
                        if (i + 1 < len(messages) and 
                            messages[i + 1].get("role") == tool_result_role and
                            self.llm_service.provider.contains_tool_results(messages[i + 1])):
                            tool_interaction_pairs.append((i, i + 1, msg))  # (assistant_idx, tool_idx, assistant_msg)
                            i += 2  # Skip both messages
                        else:
                            i += 1
                    else:
                        # Non-tool assistant message (like conversation flow messages)
                        non_tool_assistant_messages.append((i, msg))
                        i += 1
                else:
                    i += 1
            
            # Define functions that should be prioritized
            relevant_functions = {
                "write_file", "validate_python_script", "get_function_docstring",
                "read_file", "list_files", "delete_file", "write_and_validate"
            }
            
            # Find the most recent write_file and validate_python_script interactions
            last_write_pair = None
            last_write_idx = -1
            last_validate_pair = None
            last_validate_idx = -1
            docstring_pairs = []
            
            for assistant_idx, tool_idx, assistant_msg in tool_interaction_pairs:
                # Check if this message contains any relevant functions
                found_functions = []
                for func_name in relevant_functions:
                    if self.llm_service.provider.message_contains_function(assistant_msg, func_name):
                        found_functions.append(func_name)
                
                # Process based on the functions found
                if "write_file" in found_functions or "write_and_validate" in found_functions:
                    last_write_pair = (assistant_idx, tool_idx)
                    last_write_idx = assistant_idx
                elif "validate_python_script" in found_functions:
                    last_validate_pair = (assistant_idx, tool_idx)
                    last_validate_idx = assistant_idx
                elif "get_function_docstring" in found_functions:
                    # Keep all docstring calls as they provide important context
                    docstring_pairs.append((assistant_idx, tool_idx))
                else:
                    docstring_pairs.append((assistant_idx, tool_idx))
            
            # Collect pairs to keep
            pairs_to_keep = set()
            
            # Include all docstring interactions (they provide important context)
            for pair in docstring_pairs:
                pairs_to_keep.add(pair)
            
            # Include the most recent write_file
            if last_write_pair:
                pairs_to_keep.add(last_write_pair)
            
            # Only include validation if it comes AFTER the last write_file
            # (if write_file comes after validation, the validation is for an old script version)
            if last_validate_pair and (last_write_idx == -1 or last_validate_idx > last_write_idx):
                pairs_to_keep.add(last_validate_pair)
            
            # Collect all messages to add with their indices to maintain order
            messages_to_add = []
            
            # Add tool interaction pairs
            for assistant_idx, tool_idx in pairs_to_keep:
                messages_to_add.append((assistant_idx, messages[assistant_idx]))
                messages_to_add.append((tool_idx, messages[tool_idx]))
            
            # Add non-tool assistant messages (conversation flow)
            for assistant_idx, assistant_msg in non_tool_assistant_messages:
                messages_to_add.append((assistant_idx, assistant_msg))
            
            # Sort by original index to maintain conversation order
            messages_to_add.sort(key=lambda x: x[0])
            
            # Add the sorted messages
            for _, msg in messages_to_add:
                filtered_messages.append(msg)
            
            self.logger.debug(f"Filtered {len(messages)} messages down to {len(filtered_messages)} for context (including {len(non_tool_assistant_messages)} non-tool assistant messages)")
            return filtered_messages
            
        except Exception as e:
            self.logger.error(f"Error filtering messages for context: {e}")
            # Fallback: keep first message + last 6 messages (3 tool interactions)
            if len(messages) <= 7:
                return messages
            return [messages[0]] + messages[-6:]
    
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
                    "get_function_docstring": "1h",
                    # "write_file": "5m"
                }
                
                # Add caching metadata to tool results for cacheable functions
                for i, (tool_call, tool_result) in enumerate(zip(current_tool_calls, formatted_tool_results.get("content", []))):
                    function_name = tool_call.get("function", "").get("name", "")
                    # Strip MCP server prefixes to get base function name
                    base_function_name = function_name.split("__")[-1] if "__" in function_name else function_name
                    
                    if base_function_name in cacheable_functions:
                        formatted_tool_results["content"][i]["cache_control"] = {"type": "ephemeral", "ttl": cacheable_functions[base_function_name]}
                        self.logger.debug(f"Added caching for function: {function_name}")
                
            
            messages.append(formatted_tool_results)
            
            # Check if last tool call is write_and_validate and append verification message
            if current_tool_calls and original_question:
                last_tool_call = current_tool_calls[-1]
                if self._is_write_and_validate_tool_result(last_tool_call):
                    self.logger.info("📋 Last tool call is write_and_validate, appending verification message")
                    from llm import MessageFormatter
                    formatter = MessageFormatter(self.llm_service.provider_type)
                    verification_message = formatter.create_verification_message(original_question)
                    messages.append(verification_message)
                    self.logger.debug(f"Verification message appended: {verification_message.get('role')} role")
            
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
            
            # Handle different result formats
            if isinstance(result_data, dict):
                return result_data.get("valid", False) or result_data.get("success", False)
            elif isinstance(result_data, str):
                # Try to parse as JSON
                try:
                    parsed = json.loads(result_data)
                    return parsed.get("valid", False) or parsed.get("success", False)
                except:
                    # Check for success indicators in string
                    return "valid" in result_data.lower() or "success" in result_data.lower()
            else:
                # Convert to string and check
                json_str = str(result_data)
            
            parsed_result = json.loads(json_str)
            return parsed_result.get("valid", False)
        except:
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
                    parsed_json = json.loads(json_text.strip())
                    
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
                parsed_content = json.loads(content.strip())
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
                    parsed_json = json.loads(json_text.strip())
                    
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
                parsed_content = json.loads(content.strip())
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
                            filename = (parsed_result.get("filename") or 
                                      parsed_result.get("actual_filename") or
                                      parsed_result.get("absolute_path"))
                            
                            if filename and filename.endswith('.py'):
                                return {
                                    "filename": filename,
                                    "absolute_path": parsed_result.get("absolute_path"),
                                    "size": parsed_result.get("size", 0),
                                    "success": parsed_result.get("success", False)
                                }
                        except (json.JSONDecodeError, AttributeError, IndexError) as e:
                            self.logger.debug(f"Extract script JSON error: {e}")
                            continue
                    
                    elif isinstance(result_content, dict):
                        filename = result_content.get("filename") or result_content.get("file_path")
                        content = result_content.get("content") or result_content.get("file_content")
                        
                        if filename and content and filename.endswith('.py'):
                            return {
                                "filename": filename,
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