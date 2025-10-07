"""
Unified LLM Service supporting multiple providers (Anthropic, OpenAI, Ollama)
"""

import json
import logging
import os
from datetime import datetime
from typing import Dict, Any, Optional, List

from providers import create_provider, LLMProvider
from services.cache import ProviderCacheManager
from integrations.mcp import MCPIntegration

logger = logging.getLogger("unified-llm-service")


class UnifiedLLMService:
    """Universal LLM service supporting multiple providers with MCP integration"""
    
    def __init__(self):
        # Use configurable system prompt file (defaults to system-prompt.txt)
        prompt_filename = os.getenv("SYSTEM_PROMPT_FILE", "system-prompt.txt")
        self.system_prompt_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "config", prompt_filename)
        logger.info(f"📝 Using system prompt file: {prompt_filename}")
        self.system_prompt = None  # Cache for system prompt
        
        # Cache for processed tools
        self._processed_tools_cache = None
        self._tools_cache_timestamp = None
        self._provider_initialized = False
        
        # Initialize components
        self.mcp_integration = MCPIntegration()
        
        # Determine which LLM provider to use
        self.provider_type = os.getenv("LLM_PROVIDER", "anthropic").lower()
        
        # Initialize provider
        self.provider = self._create_provider()
        
        # Initialize cache manager (caching control will be parameter-based, not env-based)
        self.cache_manager = ProviderCacheManager(self.provider, enable_caching=True)
        
        logger.info(f"🤖 Initialized {self.provider_type.upper()} LLM service")
    
    def _create_provider(self) -> LLMProvider:
        """Create the appropriate LLM provider"""
        if self.provider_type == "anthropic":
            api_key = os.getenv("ANTHROPIC_API_KEY")
            default_model = os.getenv("ANTHROPIC_MODEL", "claude-3-5-haiku-20241022")
            base_url = os.getenv("ANTHROPIC_BASE_URL")
            if not api_key:
                logger.warning("ANTHROPIC_API_KEY environment variable not set")
            return create_provider("anthropic", api_key, default_model=default_model, base_url=base_url)
            
        elif self.provider_type == "openai":
            api_key = os.getenv("OPENAI_API_KEY")
            default_model = os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")
            base_url = os.getenv("OPENAI_BASE_URL")
            if not api_key:
                logger.warning("OPENAI_API_KEY environment variable not set")
            return create_provider("openai", api_key, default_model=default_model, base_url=base_url)
            
        elif self.provider_type == "ollama":
            # For Ollama, we'll still use the original implementation since it's local
            # This would require adapting the existing Ollama code to the provider interface
            raise NotImplementedError("Ollama provider not yet implemented in unified service")
            
        else:
            raise ValueError(f"Unsupported LLM_PROVIDER: {self.provider_type}")
    
    @property
    def default_model(self) -> str:
        """Get default model for the provider"""
        return self.provider.default_model
    
    @property
    def mcp_client(self):
        """Access to MCP client through integration"""
        return self.mcp_integration.mcp_client
    
    @property
    def mcp_initialized(self):
        """Check if MCP is initialized"""
        return self.mcp_integration.mcp_initialized
    
    
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
            
            self.provider.set_system_prompt(system_prompt)
            self.provider.set_tools(mcp_tools)
            
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
                self.provider.set_tools(mcp_tools)
                logger.info(f"🔧 Provider updated with {len(mcp_tools)} tools")
                
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to refresh provider tools: {e}")
            return False
    
    def get_mcp_tools(self) -> List[Dict[str, Any]]:
        """Get MCP tools in OpenAI format (cached)"""
        # Check if tools cache is still valid
        current_timestamp = self._get_mcp_tools_timestamp()
        
        if (self._processed_tools_cache is None or 
            self._tools_cache_timestamp != current_timestamp):
            
            logger.debug("🔄 Refreshing tools cache...")
            self._processed_tools_cache = self.mcp_integration.get_mcp_tools_for_openai()
            self._tools_cache_timestamp = current_timestamp
            logger.debug(f"📦 Cached {len(self._processed_tools_cache)} processed tools")
            
        return self._processed_tools_cache
    
    def _get_mcp_tools_timestamp(self) -> int:
        """Get a timestamp representing when MCP tools were last updated"""
        if not self.mcp_integration.mcp_client or not self.mcp_integration.mcp_client.available_tools:
            return 0
        return len(self.mcp_integration.mcp_client.available_tools)
    
    
    async def warm_cache(self, model: str, enable_caching: bool = True) -> bool:
        """Warm provider cache if supported"""
        if not enable_caching:
            logger.info("🔧 Caching disabled, skipping cache warming...")
            return True
            
        # Ensure provider is initialized first
        await self.ensure_provider_initialized()
        
        system_prompt = await self.get_system_prompt()
        mcp_tools = self.get_mcp_tools()
        
        return await self.cache_manager.warm_cache(model, system_prompt, mcp_tools)
    
    async def call_llm_with_tools(self, model: str, user_message: str, enable_caching: bool = False) -> Dict[str, Any]:
        """Call LLM with multi-level tool calling support"""
        try:
            # Use provider default model if none specified
            if not model:
                model = self.default_model
                
            # Ensure provider is initialized with system prompt and tools (one-time setup)
            await self.ensure_provider_initialized()
                
            # Validate API key
            if not self.provider.api_key:
                raise Exception(f"{self.provider_type.upper()}_API_KEY not set in environment")
            
            logger.info(f"🔧 Provider: {self.provider_type}")
            logger.info(f"🔧 Provider initialized: {self._provider_initialized}")
            
            # Prepare initial messages
            messages = [{"role": "user", "content": user_message}]
            
            # Make initial API call (provider uses stored system prompt and tools)
            response = await self.provider.call_api(
                model=model,
                messages=messages,
                enable_caching=enable_caching
            )
            
            if not response["success"]:
                return response
            
            # Parse response
            content, tool_calls = self.provider.parse_response(response["data"])
            
            if tool_calls:
                # Execute tools
                tool_execution_result = await self._handle_tool_calls(tool_calls)
                
                if not tool_execution_result["success"]:
                    return tool_execution_result
                
                # Start conversation loop with initial tool results
                all_tool_calls = tool_calls
                all_tool_results = tool_execution_result["tool_results"]
                
                return await self._conversation_loop(
                    model, messages, all_tool_calls, all_tool_results, enable_caching
                )
            else:
                # No tool calls - this means no script was generated
                logger.warning("❌ Task incomplete: LLM responded without calling any tools (no script generated)")
                return {
                    "success": False,
                    "content": content,
                    "provider": self.provider_type,
                    "task_completed": False,
                    "completion_reason": "no_tools_called",
                    "error": "LLM did not generate a script - no tool calls made",
                    "usage": response["data"].get("usage", {})
                }
                
        except Exception as e:
            logger.error(f"LLM call failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "provider": self.provider_type
            }
    
    async def _handle_tool_calls(self, tool_calls: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Handle tool execution and return results (does not continue conversation)"""
        try:
            # Validate tool calls
            validation = self.mcp_integration.validate_mcp_functions(tool_calls)
            if not validation["all_valid"]:
                return {
                    "success": False,
                    "error": "Forbidden tool calls detected",
                    "validation": validation,
                    "provider": self.provider_type
                }
            
            # Execute tool calls and return results
            tool_results = await self.mcp_integration.generate_tool_calls_only(tool_calls)
            
            return {
                "success": True,
                "tool_calls": tool_calls,
                "tool_results": tool_results["tool_results"],
                "provider": self.provider_type
            }
            
        except Exception as e:
            logger.error(f"Tool call handling failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "provider": self.provider_type
            }
    
    def _check_script_generation(self, tool_calls: List[Dict[str, Any]], tool_results: List[Dict[str, Any]]) -> bool:
        """Check if a script was generated (write_file tool was called successfully)"""
        for call, result in zip(tool_calls, tool_results):
            if "write_file" in call["function"]["name"] and result.get("success", False):
                # Check if the written content looks like a Python script
                try:
                    args = call["function"].get("arguments", {})
                    filename = args.get("filename", "")
                    content = args.get("content", "")
                    
                    # Basic checks for Python script content
                    if filename.endswith('.py') and len(content) > 50 and 'def ' in content:
                        return True
                except Exception:
                    continue
        
        return False
    
    def _check_validation_completion(self, tool_calls: List[Dict[str, Any]], tool_results: List[Dict[str, Any]]) -> bool:
        """Check if validation was completed successfully"""
        for call, result in zip(tool_calls, tool_results):
            if "validate_python_script" in call["function"]["name"] and result.get("success", False):
                try:
                    result_data = result.get("result", "")
                    
                    # Handle different data structures
                    if hasattr(result_data, 'content') and result_data.content:
                        if hasattr(result_data.content[0], 'text'):
                            json_str = result_data.content[0].text
                        else:
                            json_str = str(result_data.content[0])
                    elif isinstance(result_data, str):
                        json_str = result_data
                    else:
                        json_str = str(result_data)
                    
                    parsed_result = json.loads(json_str)
                    if parsed_result.get("valid", False):
                        return True
                except Exception as e:
                    logger.warning(f"❌ Failed to parse validation result: {e}")
                    continue
        
        return False
    
    async def _conversation_loop(self, model: str, messages: List[Dict[str, Any]], 
                               all_tool_calls: List[Dict[str, Any]], all_tool_results: List[Dict[str, Any]], 
                               enable_caching: bool = True) -> Dict[str, Any]:
        """Main conversation loop that continues until LLM stops calling tools"""
        # Track how many tool calls we've processed to know what's "recent"
        processed_tool_calls = 0
        
        # Track script content throughout the conversation
        generated_script_content = None
        generated_script_filename = None
        
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
                return continuation_result
            
            # Check if LLM wants to make more tool calls
            if continuation_result.get("new_tool_calls"):
                # Execute new tools
                new_tool_calls = continuation_result["new_tool_calls"]
                tool_execution_result = await self._handle_tool_calls(new_tool_calls)
                
                if not tool_execution_result["success"]:
                    return tool_execution_result
                
                # Accumulate results
                all_tool_calls.extend(new_tool_calls)
                all_tool_results.extend(tool_execution_result["tool_results"])
                
                # Check for script generation in new tool calls and results
                for i, tool_call in enumerate(new_tool_calls):
                    if "write_file" in tool_call.get("function", {}).get("name", ""):
                        # Get corresponding tool result
                        tool_result = tool_execution_result["tool_results"][i] if i < len(tool_execution_result["tool_results"]) else None
                        
                        # Only track if tool execution was successful
                        if tool_result and tool_result.get("success", False):
                            args = tool_call.get("function", {}).get("arguments", {})
                            filename = args.get("filename", "")
                            content = args.get("content", "")
                            
                            # Only track Python scripts
                            if filename.endswith('.py') and content and len(content) > 50:
                                generated_script_content = content
                                generated_script_filename = filename
                                logger.info(f"📝 Tracked script generation: {filename} (confirmed by tool result)")
                
                logger.info(f"🔄 Continuing conversation loop (total tool calls: {len(all_tool_calls)})")
                continue
            else:
                # No more tool calls - check completion using ALL accumulated results
                script_generated = self._check_script_generation(all_tool_calls, all_tool_results)
                validation_completed = self._check_validation_completion(all_tool_calls, all_tool_results)
                
                final_content = continuation_result.get("content", "")
                usage = continuation_result.get("usage", {})
                
                if script_generated and validation_completed:
                    logger.info("🏁 Task completed: Script generated and validated successfully")
                    return {
                        "success": True,
                        "content": final_content,
                        "tool_calls": all_tool_calls,
                        "tool_results": all_tool_results,
                        "provider": self.provider_type,
                        "task_completed": True,
                        "completion_reason": "script_generated_and_validated",
                        "generated_script": {
                            "content": generated_script_content,
                            "filename": generated_script_filename
                        } if generated_script_content else None,
                        "usage": usage
                    }
                elif script_generated:
                    logger.info("⚠️ Task partially completed: Script generated but not validated")
                    return {
                        "success": False,
                        "content": final_content,
                        "tool_calls": all_tool_calls,
                        "tool_results": all_tool_results,
                        "provider": self.provider_type,
                        "task_completed": False,
                        "completion_reason": "script_generated_not_validated",
                        "generated_script": {
                            "content": generated_script_content,
                            "filename": generated_script_filename
                        } if generated_script_content else None,
                        "usage": usage
                    }
                else:
                    logger.warning("❌ Task incomplete: No validated script was generated")
                    return {
                        "success": False,
                        "content": final_content,
                        "tool_calls": all_tool_calls,
                        "tool_results": all_tool_results,
                        "provider": self.provider_type,
                        "task_completed": False,
                        "completion_reason": "no_script_generated",
                        "generated_script": {
                            "content": generated_script_content,
                            "filename": generated_script_filename
                        } if generated_script_content else None,
                        "error": "LLM stopped without generating a validated script",
                        "usage": usage
                    }

    async def _continue_conversation(self, model: str, messages: List[Dict[str, Any]], 
                                   current_tool_calls: List[Dict[str, Any]], current_tool_results: List[Dict[str, Any]], 
                                   enable_caching: bool = True) -> Dict[str, Any]:
        """Continue conversation after tool execution (single round only)"""
        try:
            # Format tool results for the provider
            if self.provider_type == "anthropic":
                # Add assistant message with tool calls
                assistant_content = []
                
                # Add any text content if it exists
                if hasattr(current_tool_calls[0], 'content') and current_tool_calls[0].content:
                    assistant_content.append({"type": "text", "text": current_tool_calls[0].content})
                
                # Add tool use blocks
                for tool_call in current_tool_calls:
                    anthropic_block = tool_call.get("anthropic_block")
                    if anthropic_block:
                        assistant_content.append(anthropic_block)
                
                messages.append({"role": "assistant", "content": assistant_content})
                
                # Add tool results
                tool_result_message = self.provider.format_tool_results(current_tool_calls, current_tool_results)
                messages.append(tool_result_message)
                
            elif self.provider_type == "openai":
                # Add assistant and tool messages
                tool_result_messages = self.provider.format_tool_results(current_tool_calls, current_tool_results)
                messages.extend(tool_result_messages)
            
            # Check if we should reduce tokens for validation results
            has_validation_results = any(
                "validate_python_script" in tr.get("function", "") and 
                self._is_validation_successful(tr) 
                for tr in current_tool_results
            )
            max_tokens = 5 if has_validation_results else 4000
            
            if has_validation_results:
                logger.info("🔧 Validation results detected - using max_tokens=5 for efficiency")
            
            # Make continuation API call
            response = await self.provider.call_api(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                enable_caching=enable_caching
            )
            
            if not response["success"]:
                return response
            
            # Parse continuation response and return info about new tool calls
            content, new_tool_calls = self.provider.parse_response(response["data"])
            
            return {
                "success": True,
                "content": content,
                "new_tool_calls": new_tool_calls,
                "usage": response["data"].get("usage", {})
            }
                
        except Exception as e:
            logger.error(f"Conversation continuation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "provider": self.provider_type
            }
    
    def _is_validation_successful(self, tool_result: Dict[str, Any]) -> bool:
        """Check if a tool result represents successful validation"""
        if not tool_result.get("success", False):
            return False
        
        try:
            result_data = tool_result.get("result", "")
            
            # Handle different data structures
            if hasattr(result_data, 'content') and result_data.content:
                if hasattr(result_data.content[0], 'text'):
                    json_str = result_data.content[0].text
                else:
                    json_str = str(result_data.content[0])
            elif isinstance(result_data, str):
                json_str = result_data
            else:
                json_str = str(result_data)
            
            parsed_result = json.loads(json_str)
            return parsed_result.get("valid", False)
        except:
            return False
    
    async def analyze_question(self, question: str, model: str = None, enable_caching: bool = True) -> Dict[str, Any]:
        """Main entry point for question analysis"""
        try:
            if not model:
                model = self.default_model
            
            logger.info(f"🤔 Analyzing question with {self.provider_type.upper()}: {question[:100]}...")
            
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
                
                # Add tool information if tools were called
                # if result.get("tool_calls"):
                #     response_data["tool_calls"] = result["tool_calls"]
                #     response_data["tool_results"] = result["tool_results"]
                
                # Add usage information if available
                # if result.get("usage"):
                #     response_data["usage"] = result["usage"]
                
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
                    "provider": result.get("provider", self.provider_type)
                }
                
        except Exception as e:
            logger.error(f"❌ Analysis error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def close_sessions(self):
        """Cleanup method for server shutdown"""
        logger.info("Closing unified LLM service sessions...")
        self.mcp_integration.mcp_initialized = False
        logger.info("Cleaned up MCP client and caches")