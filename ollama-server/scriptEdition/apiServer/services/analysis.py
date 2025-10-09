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
from llm.cache import ProviderCacheManager
from integrations.mcp import MCPIntegration

logger = logging.getLogger("analysis-service")

class AnalysisService:
    """Financial question analysis service with MCP integration"""
    
    def __init__(self, llm_service: Optional[LLMService] = None):
        # Use provided LLM service or create default analysis LLM
        self.llm_service = llm_service or create_analysis_llm()
        
        # Initialize MCP integration for tool calling
        self.mcp_integration = MCPIntegration()
        
        # Cache for processed tools and initialization state
        self._processed_tools_cache = None
        self._tools_cache_timestamp = None
        self._provider_initialized = False
        
        # Load QnA-specific system prompt
        self._load_system_prompt_config()
        
        # Initialize cache manager
        self.cache_manager = ProviderCacheManager(self.llm_service.provider, enable_caching=True)
        
        logger.info(f"🤖 Initialized Analysis service with {self.llm_service.provider_type}")
    
    def _load_system_prompt_config(self):
        """Load system prompt configuration for QnA analysis"""
        prompt_filename = os.getenv("SYSTEM_PROMPT_FILE", "system-prompt.txt")
        self.system_prompt_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), 
            "..", 
            "config", 
            prompt_filename
        )
        self.system_prompt = None  # Cache for system prompt
        logger.info(f"📝 Using system prompt file: {prompt_filename}")
    
    # === SYSTEM PROMPT MANAGEMENT ===
    
    async def load_system_prompt(self) -> str:
        """Load the base system prompt from file"""
        try:
            logger.debug(f"Loading system prompt from: {self.system_prompt_path}")
            with open(self.system_prompt_path, 'r') as f:
                content = f.read().strip()
                logger.debug(f"System prompt loaded successfully ({len(content)} characters)")
                return content
        except Exception as e:
            logger.error(f"Failed to load system prompt from {self.system_prompt_path}: {e}")
            return "You are a helpful financial analysis assistant that generates tool calls for financial data analysis."
    
    async def get_system_prompt(self) -> str:
        """Get system prompt (cached)"""
        if self.system_prompt:
            return self.system_prompt
            
        self.system_prompt = await self.load_system_prompt()
        return self.system_prompt
    
    # === MCP INTEGRATION ===
    
    @property
    def mcp_client(self):
        """Access to MCP client through integration"""
        return self.mcp_integration.mcp_client
    
    @property
    def mcp_initialized(self):
        """Check if MCP is initialized"""
        return self.mcp_integration.mcp_initialized
    
    async def ensure_mcp_initialized(self) -> bool:
        """Ensure MCP client is initialized"""
        return await self.mcp_integration.ensure_mcp_initialized()
    
    async def ensure_provider_initialized(self) -> bool:
        """Ensure provider has system prompt and tools set (one-time setup)"""
        if self._provider_initialized:
            return True
            
        try:
            # Ensure MCP is initialized first
            await self.ensure_mcp_initialized()
            
            # Get system prompt and tools, set them on provider once
            system_prompt = await self.get_system_prompt()
            mcp_tools = self.get_mcp_tools()
            
            self.llm_service.provider.set_system_prompt(system_prompt)
            self.llm_service.provider.set_tools(mcp_tools)
            
            self._provider_initialized = True
            logger.info(f"🔧 Provider initialized with system prompt and {len(mcp_tools)} tools")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize provider: {e}")
            return False
    
    async def refresh_provider_tools(self) -> bool:
        """Refresh tools on provider if MCP tools have changed"""
        if not self._provider_initialized:
            return await self.ensure_provider_initialized()
            
        try:
            # Check if tools have changed
            current_timestamp = self._get_mcp_tools_timestamp()
            
            if self._tools_cache_timestamp != current_timestamp:
                logger.info("🔄 MCP tools changed, refreshing provider...")
                mcp_tools = self.get_mcp_tools()
                self.llm_service.provider.set_tools(mcp_tools)
                self._tools_cache_timestamp = current_timestamp
                logger.info(f"✅ Provider tools refreshed ({len(mcp_tools)} tools)")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to refresh provider tools: {e}")
            return False
    
    def get_mcp_tools(self) -> List[Dict[str, Any]]:
        """Get processed MCP tools for the provider"""
        try:
            # Use cached tools if available and timestamp matches
            current_timestamp = self._get_mcp_tools_timestamp()
            
            if (self._processed_tools_cache is not None and 
                self._tools_cache_timestamp == current_timestamp):
                return self._processed_tools_cache
            
            # Get fresh tools from MCP
            tools = self.mcp_integration.get_mcp_tools()
            self._processed_tools_cache = tools
            self._tools_cache_timestamp = current_timestamp
            
            return tools
            
        except Exception as e:
            logger.error(f"❌ Failed to get MCP tools: {e}")
            return []
    
    def _get_mcp_tools_timestamp(self) -> int:
        """Get timestamp for MCP tools cache invalidation"""
        try:
            return hash(str(self.mcp_integration.get_mcp_tools()))
        except:
            return 0
    
    # === ANALYSIS WORKFLOW ===
    
    async def warm_cache(self, model: str, enable_caching: bool = True) -> bool:
        """Warm up cache for faster subsequent requests"""
        try:
            logger.info(f"🔥 Warming cache for {model}")
            
            if enable_caching and self.cache_manager:
                success = await self.cache_manager.warm_cache(
                    model, 
                    await self.get_system_prompt(), 
                    self.get_mcp_tools()
                )
                if success:
                    logger.info(f"✅ Cache warmed successfully for {model}")
                    return True
                else:
                    logger.warning(f"⚠️ Cache warm failed for {model}")
                    return False
            else:
                logger.info("Cache warming skipped (caching disabled)")
                return True
                
        except Exception as e:
            logger.error(f"❌ Cache warm error for {model}: {e}")
            return False
    
    async def call_llm_with_tools(self, model: str, user_message: str, enable_caching: bool = False) -> Dict[str, Any]:
        """Call LLM with tool calling capability"""
        try:
            # Ensure provider is initialized with tools
            await self.ensure_provider_initialized()
            
            # Refresh tools if needed
            await self.refresh_provider_tools()
            
            # Create messages
            messages = [{"role": "user", "content": user_message}]
            
            result = await self.llm_service.make_request(
                messages=messages,
                model=model,
                enable_caching=enable_caching
            )
            
            if not result.get("success"):
                return result
            
            # Handle tool calls if present
            tool_calls = result.get("tool_calls", [])
            
            if tool_calls:
                logger.info(f"🔧 Processing {len(tool_calls)} tool calls")
                
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
                    logger.error(f"❌ Tool execution failed: {tool_result.get('error')}")
                    return {
                        "success": False,
                        "content": result.get("content", ""),
                        "provider": self.llm_service.provider_type,
                        "tool_error": tool_result.get("error"),
                        "error": f"Tool execution failed: {tool_result.get('error')}"
                    }
            else:
                # No tool calls - start conversation loop to handle reuse decisions
                return await self._conversation_loop(
                    model, messages, [], [], enable_caching
                )
                
        except Exception as e:
            logger.error(f"❌ LLM call error: {e}")
            return {
                "success": False,
                "error": str(e),
                "provider": self.llm_service.provider_type
            }
    
    async def _handle_tool_calls(self, tool_calls: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Execute tool calls using MCP integration"""
        try:
            logger.info(f"🔧 Executing {len(tool_calls)} tool calls")

            # Validate tool calls
            validation = self.mcp_integration.validate_mcp_functions(tool_calls)
            if not validation["all_valid"]:
                return {
                    "success": False,
                    "error": "Forbidden tool calls detected",
                    "validation": validation,
                    "provider": self.llm_service.provider_type
                }
            
            # Use MCP integration to execute all tools at once
            mcp_result = await self.mcp_integration.generate_tool_calls_only(tool_calls)
            
            if not mcp_result.get("success"):
                logger.error(f"❌ MCP tool execution failed: {mcp_result.get('error')}")
                return {
                    "success": False,
                    "error": mcp_result.get("error", "MCP tool execution failed")
                }
            
            # Convert MCP results to expected format
            tool_results = []
            mcp_tool_results = mcp_result.get("tool_results", [])
            all_tools_succeeded = True
            
            for i, (tool_call, mcp_tool_result) in enumerate(zip(tool_calls, mcp_tool_results)):
                tool_success = mcp_tool_result.get("success", False)
                if not tool_success:
                    all_tools_succeeded = False
                
                tool_results.append(mcp_tool_result)
            
            if all_tools_succeeded:
                logger.info(f"✅ All {len(tool_results)} tool calls succeeded")
            else:
                failed_tools = [tr for tr in tool_results if not tr["success"]]
                logger.error(f"❌ {len(failed_tools)} out of {len(tool_results)} tool calls failed")
            
            return {
                "success": all_tools_succeeded,
                "tool_calls": tool_calls,
                "tool_results": tool_results,
                "provider": self.llm_service.provider_type
            }
            
        except Exception as e:
            logger.error(f"❌ Tool execution error: {e}")
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
                                logger.debug(f"Raw text content type: {type(text_content)}")
                                logger.debug(f"Raw text content repr: {repr(text_content[:200])}")
                                
                                # Clean the text and try parsing
                                cleaned_text = text_content.strip()
                                parsed_result = json.loads(cleaned_text)
                                
                                if (parsed_result.get("success") and 
                                    parsed_result.get("absolute_path", "").endswith(".py") and
                                    parsed_result.get("size", 0) > 1000):
                                    logger.info(f"✅ Script generation detected: {parsed_result.get('absolute_path')}")
                                    return True
                            except json.JSONDecodeError as e:
                                logger.error(f"JSON decode error: {e}")
                                logger.error(f"Failed text: {repr(text_content)}")
                                # Fallback pattern matching
                                if (".py" in text_content and "success" in text_content and "size" in text_content):
                                    logger.info("✅ Script generation detected (fallback)")
                                    return True
                            except (AttributeError, IndexError) as e:
                                logger.error(f"Structure error: {e}")
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
                                logger.debug(f"Validation - Raw text content type: {type(text_content)}")
                                logger.debug(f"Validation - Raw text content repr: {repr(text_content[:200])}")
                                
                                # Clean the text and try parsing
                                cleaned_text = text_content.strip()
                                parsed_result = json.loads(cleaned_text)
                                
                                if parsed_result.get("valid") is not None:
                                    logger.info(f"✅ Validation completed: {func_name} - Valid: {parsed_result.get('valid')}")
                                    return True
                            except json.JSONDecodeError as e:
                                logger.error(f"Validation JSON decode error: {e}")
                                logger.error(f"Validation failed text: {repr(text_content)}")
                                # Fallback pattern matching
                                if any(keyword in text_content.lower() for keyword in ["valid", "validation", "executed successfully"]):
                                    logger.info(f"✅ Validation completed (fallback): {func_name}")
                                    return True
                            except (AttributeError, IndexError) as e:
                                logger.error(f"Validation structure error: {e}")
                                pass
                        
                        elif isinstance(result_content, dict):
                            # Direct dictionary access
                            if result_content.get("valid") is not None:
                                logger.info(f"✅ Validation completed: {func_name} - Valid: {result_content.get('valid')}")
                                return True
                        elif isinstance(result_content, str):
                            # JSON string - parse it
                            try:
                                parsed_result = json.loads(result_content)
                                if parsed_result.get("valid") is not None:
                                    logger.info(f"✅ Validation completed: {func_name} - Valid: {parsed_result.get('valid')}")
                                    return True
                            except json.JSONDecodeError:
                                # Fallback - if it contains validation keywords
                                if any(keyword in result_content.lower() for keyword in ["valid", "validation", "executed successfully"]):
                                    logger.info(f"✅ Validation completed (fallback): {func_name}")
                                    return True
            
            return False
        except Exception as e:
            logger.error(f"❌ Error checking validation completion: {e}")
            return False
    
    async def _conversation_loop(self, model: str, messages: List[Dict[str, Any]], 
                               all_tool_calls: List[Dict[str, Any]], all_tool_results: List[Dict[str, Any]], 
                               enable_caching: bool = False) -> Dict[str, Any]:
        """Main conversation loop that continues until LLM stops calling tools"""
        try:
            
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
                    model, messages, recent_tool_calls, recent_tool_results, enable_caching
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
                    
                    logger.info(f"🔄 Continuing conversation loop (total tool calls: {len(all_tool_calls)})")
                    continue
                else:
                    # No more tool calls - first check if this is a reuse decision
                    final_content = continuation_result.get("content", "")
                    reuse_decision = self._check_reuse_decision(final_content)
                    
                    if reuse_decision:
                        logger.info("✅ Reuse decision made - existing analysis can be reused")
                        return {
                            "success": True,
                            "provider": self.llm_service.provider_type,
                            "task_completed": True,
                            "response_type": "reuse_decision",
                            "data": reuse_decision,
                            "raw_content": final_content
                        }
                    
                    # Check if this is a script generation response
                    script_generation_response = self._check_script_generation_response(final_content)
                    if script_generation_response:
                        if script_generation_response.get("status") == "success":
                            logger.info("✅ Script generation completed successfully")
                            return {
                                "success": True,
                                "provider": self.llm_service.provider_type,
                                "task_completed": True,
                                "response_type": "script_generation",
                                "data": script_generation_response,
                                "raw_content": final_content
                            }
                        else:  # status == "failed"
                            logger.error("❌ Script generation failed")
                            return {
                                "success": False,
                                "provider": self.llm_service.provider_type,
                                "task_completed": False,
                                "response_type": "script_generation_failed",
                                "data": script_generation_response,
                                "raw_content": final_content,
                                "error": script_generation_response.get("final_error", "Script generation failed")
                            }
                    
                    # No reuse decision or script generation response found
                    logger.warning("❌ Task incomplete: No reuse decision or script generation response found")
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
            logger.error(f"❌ Conversation loop error: {e}")
            return {
                "success": False,
                "error": f"Conversation error: {str(e)}"
            }
    
    async def _continue_conversation(self, model: str, messages: List[Dict[str, Any]], 
                                   current_tool_calls: List[Dict[str, Any]], current_tool_results: List[Dict[str, Any]],
                                   enable_caching: bool = False) -> Dict[str, Any]:
        """Continue conversation after tool execution with proper formatting"""
        try:
            # Add assistant message with tool calls
            messages.append({
                "role": "assistant",
                "content": self.llm_service.provider.format_tool_calls(current_tool_calls)
            })

            foramtted_tool_results = self.llm_service.provider.format_tool_results(current_tool_calls, current_tool_results)
            
            # Add tool results using provider's formatting function
            if enable_caching and self.llm_service.provider_type == "anthropic":
                # Define functions that are allowed for caching
                cacheable_functions = {
                    "get_function_docstring": "1h",
                    # "write_file": "5m"
                }
                
                # Add caching metadata to tool results for cacheable functions
                for i, (tool_call, tool_result) in enumerate(zip(current_tool_calls, foramtted_tool_results.get("content", []))):
                    function_name = tool_call.get("function", "").get("name", "")
                    # Strip MCP server prefixes to get base function name
                    base_function_name = function_name.split("__")[-1] if "__" in function_name else function_name
                    
                    if base_function_name in cacheable_functions:
                        foramtted_tool_results["content"][i]["cache_control"] = {"type": "ephemeral", "ttl": cacheable_functions[base_function_name]}
                        logger.debug(f"Added caching for function: {function_name}")
                
            
            messages.append(foramtted_tool_results)
            
            # Make request with conversation context
            result = await self.llm_service.make_request(
                messages=messages,
                model=model,
                enable_caching=enable_caching
            )
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Continue conversation error: {e}")
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
    
    def _check_script_generation_response(self, content: str) -> Optional[Dict[str, Any]]:
        """Check if content contains a script generation JSON response"""
        try:
            # Look for JSON code blocks in the content
            import re
            
            # Extract JSON from markdown code blocks
            json_pattern = r'```json\s*(.*?)\s*```'
            json_matches = re.findall(json_pattern, content, re.DOTALL)
            
            for json_text in json_matches:
                try:
                    parsed_json = json.loads(json_text.strip())
                    
                    # Check if this is a script generation response
                    if "script_generation" in parsed_json:
                        script_data = parsed_json["script_generation"]
                        if script_data.get("status") == "success":
                            logger.info(f"📝 Script generation response found: {script_data.get('script_name')}")
                            return script_data
                        elif script_data.get("status") == "failed":
                            logger.info("❌ Script generation failed response found")
                            return script_data
                            
                except json.JSONDecodeError as e:
                    logger.debug(f"Failed to parse JSON block: {e}")
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
                
            return None
            
        except Exception as e:
            logger.debug(f"Error checking script generation response: {e}")
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
                            logger.info(f"🔄 Reuse decision found: {reuse_data.get('existing_function_name')}")
                            return reuse_data
                        elif reuse_data.get("should_reuse") is False:
                            logger.info("🆕 New analysis required - no reusable analysis found")
                            return None
                            
                except json.JSONDecodeError as e:
                    logger.debug(f"Failed to parse JSON block: {e}")
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
            logger.debug(f"Error checking reuse decision: {e}")
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
                            logger.debug(f"Extract script - Raw text: {repr(text_content[:200])}")
                            
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
                            logger.debug(f"Extract script JSON error: {e}")
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
            logger.error(f"Error extracting script info: {e}")
            return None
    
    # === MAIN ANALYSIS ENTRY POINT ===
    
    async def analyze_question(self, question: str, model: str = None, enable_caching: bool = True) -> Dict[str, Any]:
        """Main entry point for financial question analysis"""
        try:
            if not model:
                model = self.llm_service.default_model
            
            logger.info(f"🤔 Analyzing question with {self.llm_service.provider_type.upper()}: {question[:100]}...")
            
            # Call LLM with tools
            result = await self.call_llm_with_tools(model, question, enable_caching)
            
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
                
                logger.info(f"✅ Question analyzed successfully using {result['provider']} - Type: {result.get("response_type")}")
                
                return {
                    "success": True,
                    "data": response_data
                }
            else:
                logger.error(f"❌ Question analysis failed: {result.get('error')}")
                return {
                    "success": False,
                    "error": result.get("error", "Unknown error"),
                    "provider": result.get("provider", self.llm_service.provider_type),
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"❌ Analysis error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    # === LIFECYCLE MANAGEMENT ===
    
    async def close_sessions(self):
        """Cleanup method for server shutdown"""
        logger.info("Closing analysis service sessions...")
        self.mcp_integration.mcp_initialized = False
        logger.info("Cleaned up MCP client and caches")

# Factory function to create analysis service
def create_analysis_service(llm_service: Optional[LLMService] = None) -> AnalysisService:
    """Create analysis service instance"""
    return AnalysisService(llm_service)

# Note: Convenience functions removed - use AnalysisService instance directly