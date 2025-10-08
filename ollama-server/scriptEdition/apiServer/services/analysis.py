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
            
            # Make request with caching if enabled
            if enable_caching and self.cache_manager:
                result = await self.cache_manager.make_cached_request(
                    messages=messages,
                    model=model
                )
            else:
                result = await self.llm_service.make_request(
                    messages=messages,
                    model=model
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
                    # Check if script generation completed
                    script_generated = self._check_script_generation(tool_calls, tool_result.get("tool_results", []))
                    validation_completed = self._check_validation_completion(tool_calls, tool_result.get("tool_results", []))
                    
                    # Start conversation loop if needed
                    if script_generated or validation_completed:
                        logger.info("🔄 Starting conversation loop for completion")
                        
                        # Add tool results to conversation
                        messages.append({
                            "role": "assistant", 
                            "content": result.get("content", ""),
                            "tool_calls": tool_calls
                        })
                        messages.append({
                            "role": "user",
                            "content": f"Tool execution results: {json.dumps(tool_result.get('tool_results', []))}"
                        })
                        
                        # Continue conversation
                        final_result = await self._conversation_loop(model, messages, enable_caching)
                        
                        # Add completion metadata
                        final_result["task_completed"] = True
                        final_result["completion_reason"] = "script_generated" if script_generated else "validation_completed"
                        
                        # Add script information if generated
                        if script_generated:
                            final_result["generated_script"] = self._extract_script_info(tool_result.get("tool_results", []))
                        
                        return final_result
                    else:
                        # Return with tool results
                        result["tool_results"] = tool_result.get("tool_results", [])
                        result["tools_executed"] = len(tool_calls)
                        return result
                else:
                    logger.error(f"❌ Tool execution failed: {tool_result.get('error')}")
                    result["tool_error"] = tool_result.get("error")
                    return result
            else:
                # No tool calls, return direct response
                logger.info("💬 Direct response (no tool calls)")
                return result
                
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
            
            # Use MCP integration to execute tools
            tool_results = []
            
            for tool_call in tool_calls:
                try:
                    function_name = tool_call["function"]["name"]
                    arguments = tool_call["function"]["arguments"]
                    
                    logger.debug(f"Calling tool: {function_name}")
                    
                    # Execute via MCP
                    result = await self.mcp_integration.call_mcp_function(function_name, arguments)
                    
                    tool_results.append({
                        "tool_call_id": tool_call.get("id", f"call_{len(tool_results)}"),
                        "function_name": function_name,
                        "success": result.get("success", False),
                        "result": result.get("result"),
                        "error": result.get("error")
                    })
                    
                except Exception as e:
                    logger.error(f"❌ Tool call failed: {function_name} - {e}")
                    tool_results.append({
                        "tool_call_id": tool_call.get("id", f"call_{len(tool_results)}"),
                        "function_name": function_name,
                        "success": False,
                        "error": str(e)
                    })
            
            logger.info(f"✅ Executed {len(tool_results)} tool calls")
            
            return {
                "success": True,
                "tool_results": tool_results
            }
            
        except Exception as e:
            logger.error(f"❌ Tool execution error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _check_script_generation(self, tool_calls: List[Dict[str, Any]], tool_results: List[Dict[str, Any]]) -> bool:
        """Check if script generation was completed"""
        try:
            # Look for write operations that created Python files
            for result in tool_results:
                if result.get("success") and result.get("function_name"):
                    func_name = result["function_name"]
                    
                    # Check for file write operations
                    if "write" in func_name.lower() and result.get("result"):
                        content = str(result["result"])
                        # Look for Python file creation with substantial content
                        if any(ext in content.lower() for ext in [".py"]):
                            # Check if content suggests a complete script
                            if len(content) > 50 and 'def ' in content:
                                return True
            return False
        except:
            return False
    
    def _check_validation_completion(self, tool_calls: List[Dict[str, Any]], tool_results: List[Dict[str, Any]]) -> bool:
        """Check if validation process was completed"""
        try:
            # Look for validation tool calls
            validation_tools = [
                "validate_python_script",
                "validate_workflow_step", 
                "validate_template_variables",
                "validate_complete_workflow"
            ]
            
            for result in tool_results:
                if result.get("success") and result.get("function_name"):
                    func_name = result["function_name"]
                    
                    # Check if this was a validation tool
                    if any(val_tool in func_name for val_tool in validation_tools):
                        # Check if validation was successful
                        if self._is_validation_successful(result):
                            logger.info(f"✅ Validation completed successfully: {func_name}")
                            return True
                        else:
                            logger.info(f"⚠️ Validation completed with issues: {func_name}")
                            return True  # Still consider it completion
            
            return False
        except Exception as e:
            logger.error(f"❌ Error checking validation completion: {e}")
            return False
    
    async def _conversation_loop(self, model: str, messages: List[Dict[str, Any]], 
                               enable_caching: bool = False) -> Dict[str, Any]:
        """Handle multi-turn conversation after tool execution"""
        try:
            max_turns = 5  # Prevent infinite loops
            turn_count = 0
            
            while turn_count < max_turns:
                turn_count += 1
                logger.info(f"🔄 Conversation turn {turn_count}")
                
                # Continue conversation
                result = await self._continue_conversation(model, messages, enable_caching)
                
                if not result.get("success"):
                    logger.error(f"❌ Conversation turn {turn_count} failed")
                    return result
                
                # Check if there are new tool calls
                new_tool_calls = result.get("tool_calls", [])
                
                if new_tool_calls:
                    logger.info(f"🔧 Processing {len(new_tool_calls)} new tool calls")
                    
                    # Execute new tools
                    tool_result = await self._handle_tool_calls(new_tool_calls)
                    
                    # Add to conversation
                    messages.append({
                        "role": "assistant",
                        "content": result.get("content", ""),
                        "tool_calls": new_tool_calls
                    })
                    
                    if tool_result.get("success"):
                        messages.append({
                            "role": "user",
                            "content": f"Tool results: {json.dumps(tool_result.get('tool_results', []))}"
                        })
                        
                        # Check for completion again
                        script_generated = self._check_script_generation(new_tool_calls, tool_result.get("tool_results", []))
                        validation_completed = self._check_validation_completion(new_tool_calls, tool_result.get("tool_results", []))
                        
                        if script_generated or validation_completed:
                            logger.info(f"✅ Task completed in conversation turn {turn_count}")
                            result["tool_results"] = tool_result.get("tool_results", [])
                            result["conversation_turns"] = turn_count
                            return result
                    else:
                        logger.error(f"❌ Tool execution failed in turn {turn_count}")
                        result["tool_error"] = tool_result.get("error")
                        return result
                else:
                    # No more tool calls, conversation complete
                    logger.info(f"✅ Conversation completed after {turn_count} turns")
                    result["conversation_turns"] = turn_count
                    return result
            
            # Max turns reached
            logger.warning(f"⚠️ Conversation loop reached max turns ({max_turns})")
            return {
                "success": True,
                "content": "Analysis completed but may be incomplete due to conversation limits.",
                "conversation_turns": max_turns,
                "max_turns_reached": True
            }
            
        except Exception as e:
            logger.error(f"❌ Conversation loop error: {e}")
            return {
                "success": False,
                "error": f"Conversation error: {str(e)}"
            }
    
    async def _continue_conversation(self, model: str, messages: List[Dict[str, Any]], 
                                   enable_caching: bool = False) -> Dict[str, Any]:
        """Continue conversation with updated context"""
        try:
            # Make request with conversation context
            if enable_caching and self.cache_manager:
                result = await self.cache_manager.make_cached_request(
                    messages=messages,
                    model=model
                )
            else:
                result = await self.llm_service.make_request(
                    messages=messages,
                    model=model
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
    
    def _extract_script_info(self, tool_results: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Extract script information from tool results"""
        try:
            for result in tool_results:
                if result.get("success") and "write" in result.get("function_name", "").lower():
                    result_content = result.get("result", {})
                    if isinstance(result_content, dict):
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
                # Format the successful response
                response_data = {
                    "question": question,
                    "provider": result["provider"],
                    "model": model,
                    "content": result.get("content", ""),
                    "timestamp": datetime.now().isoformat()
                }
                
                # Add completion information if task was completed
                if result.get("task_completed"):
                    response_data["task_completed"] = result["task_completed"]
                    response_data["completion_reason"] = result.get("completion_reason")
                
                # Add generated script information if available
                if result.get("generated_script"):
                    response_data["generated_script"] = result["generated_script"]
                
                logger.info(f"✅ Question analyzed successfully using {result['provider']}")
                
                return {
                    "success": True,
                    "data": response_data
                }
            else:
                logger.error(f"❌ Question analysis failed: {result.get('error')}")
                return {
                    "success": False,
                    "error": result.get("error", "Unknown error"),
                    "provider": result.get("provider", self.llm_service.provider_type)
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