"""
Anthropic Claude API provider implementation
"""

import json
import logging
import httpx
import subprocess
import tempfile
import os
import threading
import shlex
from typing import Dict, Any, List, Tuple, Optional

from .base import LLMProvider

logger = logging.getLogger("anthropic-provider")


class AnthropicProvider(LLMProvider):
    """Anthropic Claude API provider"""
    
    def __init__(self, api_key: str, default_model: str = "claude-3-5-haiku-20241022", base_url: str = None):
        if base_url is None:
            base_url = "https://api.anthropic.com/v1"
        super().__init__(api_key, base_url, default_model)
        self.use_cli = False
    
    def supports_caching(self) -> bool:
        return True
    
    def _should_use_claude_code_cli(self, messages: List[Dict[str, Any]], force_api: bool = False) -> bool:
        """Determine if request should use Claude Code CLI"""
        # Force API usage for specific use cases (like context search)
        if force_api:
            return False
        
        # Check if Claude CLI is available before attempting to use it
        cli_available = self._check_claude_cli_available()
        if not cli_available:
            logger.warning("⚠️ Claude CLI not available, falling back to API")
            return False
            
        # Use use_cli flag set by LLMService from config
        return self.use_cli
    
    def _check_claude_cli_available(self) -> bool:
        """Check if Claude CLI is available and accessible"""
        try:
            # Try to run claude --version to check availability
            result = subprocess.run(
                ["claude", "--version"], 
                capture_output=True, 
                text=True, 
                timeout=5
            )
            if result.returncode == 0:
                logger.debug(f"✅ Claude CLI available: {result.stdout.strip()}")
                return True
            else:
                logger.debug(f"❌ Claude CLI check failed: {result.stderr}")
                return False
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError) as e:
            logger.debug(f"❌ Claude CLI not available: {e}")
            return False
    
    def _stream_subprocess_output(self, process, timeout=300):
        """Stream subprocess output to console AND capture it"""
        
        def stream_and_capture(pipe, prefix, lines_list):
            """Stream output to logger and capture in list"""
            try:
                for line in iter(pipe.readline, ''):
                    if line:
                        lines_list.append(line)
                        # Log to our logger instead of direct print
                        logger.info(f"[{prefix}] {line.rstrip()}")
            except Exception as e:
                logger.error(f"Error in {prefix} stream: {e}")
            finally:
                pipe.close()
        
        stdout_lines = []
        stderr_lines = []
        
        # Start streaming threads
        stdout_thread = threading.Thread(
            target=stream_and_capture,
            args=(process.stdout, "CLAUDE", stdout_lines)
        )
        stderr_thread = threading.Thread(
            target=stream_and_capture,
            args=(process.stderr, "DEBUG", stderr_lines)
        )
        
        stdout_thread.start()
        stderr_thread.start()
        
        # Wait for process with timeout
        try:
            return_code = process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            process.kill()
            stdout_thread.join(timeout=1)
            stderr_thread.join(timeout=1)
            raise subprocess.TimeoutExpired(process.args, timeout)
        
        # Wait for threads to complete
        stdout_thread.join()
        stderr_thread.join()
        
        return {
            "returncode": return_code,
            "stdout": "".join(stdout_lines),
            "stderr": "".join(stderr_lines)
        }
    
    async def _call_claude_code_cli(self, model: str, messages: List[Dict[str, Any]], 
                                   max_tokens: int = 10000, enable_caching: bool = False) -> Dict[str, Any]:
        """Use Claude Code CLI instead of API for tool-enabled requests"""
        try:
            if not messages:
                raise Exception("No messages provided for Claude Code CLI")
            
            # Build CLI command with full message history (not just last user message)
            cli_command = [
                "claude",
                "--output-format", "json",
                "--permission-mode", "bypassPermissions"
            ]
            
            # Add system prompt if available (pre-loaded from provider)
            system_prompt = self._raw_system_prompt or "You are a helpful assistant."
            cli_command.extend(["--append-system-prompt", system_prompt])
            
            # Process messages for Claude Code CLI
            for msg in messages:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                
                # Handle different content formats
                if isinstance(content, list):
                    # Extract text from content blocks
                    text_parts = []
                    for block in content:
                        if isinstance(block, dict) and block.get("type") == "text":
                            text_parts.append(block.get("text", ""))
                        elif isinstance(block, str):
                            text_parts.append(block)
                    content = "\n".join(text_parts)
                
                if content and role == "user":
                    # Add user message as prompt
                    cli_command.extend(["-p", content])
                elif content and role == "assistant":
                    # Add assistant message context
                    cli_command.extend(["--append-system-prompt", f"Assistant: {content}"])
            
            # Verify we have at least one user message
            user_messages = [m for m in messages if m.get("role") == "user"]
            if not user_messages:
                raise Exception("No user message found for Claude Code CLI")
            
            # Add MCP config to CLI command if available (loaded by service via set_mcp_config)
            mcp_config_path = None
            if self._raw_mcp_config:
                if isinstance(self._raw_mcp_config, dict):
                    # Write filtered config to temp file for CLI
                    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                        json.dump(self._raw_mcp_config, f)
                        mcp_config_path = f.name
                    logger.debug(f"Created temp MCP config: {mcp_config_path}")
                elif isinstance(self._raw_mcp_config, str) and os.path.exists(self._raw_mcp_config):
                    # It's a file path
                    mcp_config_path = self._raw_mcp_config
                
                if mcp_config_path:
                    cli_command.extend(["--mcp-config", mcp_config_path])
                    service_info = f" for service '{self._mcp_service_name}'" if self._mcp_service_name else ""
                    logger.debug(f"Using MCP config{service_info}: {mcp_config_path}")
            
            if not mcp_config_path:
                logger.warning("⚠️ No MCP config available - Claude CLI may not have tool access")
            
            # Set working directory for script generation
            working_dir = "/Users/shivc/Documents/Workspace/JS/qna-ai-admin/mcp-server"
            os.makedirs(working_dir, exist_ok=True)
            
            logger.info("🚀 Calling Claude Code CLI with system prompt and MCP configuration")
            logger.debug(f"System prompt length: {len(system_prompt)} chars")
            
            # Set up environment with API key for Claude CLI
            env = os.environ.copy()
            if self.api_key and self.api_key != "dummy-key":
                env["ANTHROPIC_API_KEY"] = self.api_key
                logger.debug("🔑 Using Anthropic API key from provider")
            else:
                logger.warning("⚠️ No valid API key available - Claude CLI will use its own config")
            
            # Check if we should stream output in real-time (for debugging)
            stream_output = os.getenv("CLAUDE_CLI_STREAM", "false").lower() == "true"
            
            if stream_output:
                logger.info("🔄 Streaming Claude CLI output in real-time...")
                
                process = subprocess.Popen(
                    cli_command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    bufsize=1,
                    cwd=working_dir
                )
                
                result_data = self._stream_subprocess_output(process, timeout=300)
                
                result = type('Result', (), {
                    'returncode': result_data['returncode'],
                    'stdout': result_data['stdout'],
                    'stderr': result_data['stderr']
                })()
                
            else:
                result = subprocess.run(
                    cli_command,
                    capture_output=True,
                    text=True,
                    timeout=300,
                    cwd=working_dir
                )
            
            # Log subprocess output for debugging (even on success)
            logger.debug(f"📤 Claude CLI return code: {result.returncode}")
            if result.stdout:
                logger.debug(f"📤 Claude CLI stdout: {result.stdout[:500]}...")
            if result.stderr:
                logger.info(f"📤 Claude CLI stderr (verbose output): {result.stderr}")
            
            if result.returncode != 0:
                logger.error(f"❌ Claude Code CLI failed with return code {result.returncode}")
                logger.error(f"❌ Claude CLI stderr: {result.stderr}")
                logger.error(f"❌ Claude CLI stdout: {result.stdout}")
                raise Exception(f"Claude Code CLI failed with return code {result.returncode}: {result.stderr}")
            
            # Parse JSON response
            try:
                response_data = json.loads(result.stdout)
            except json.JSONDecodeError as e:
                logger.error(f"❌ Failed to parse CLI output as JSON")
                logger.error(f"❌ Raw output: {result.stdout}")
                logger.error(f"❌ JSON error: {e}")
                raise Exception(f"Invalid JSON response from Claude Code CLI: {e}")
            
            logger.info("✅ Claude Code CLI call successful")
            
            # Handle response_data as array - last element contains the result
            if isinstance(response_data, list) and len(response_data) > 0:
                # Get the last element which contains the result
                last_element = response_data[-1]
                
                # Extract the result field which is stringified JSON - parse it completely
                if isinstance(last_element, dict) and "result" in last_element:
                    result_content = last_element["result"]
                    # Try to parse the JSON if it's a string starting with ```json
                    if isinstance(result_content, str) and result_content.strip().startswith('```json'):
                        try:
                            # Extract JSON from markdown code block
                            json_start = result_content.find('{')
                            json_end = result_content.rfind('}') + 1
                            if json_start != -1 and json_end != -1:
                                json_str = result_content[json_start:json_end]
                                parsed_json = json.loads(json_str)
                                output_text = json.dumps(parsed_json, indent=2)
                            else:
                                output_text = result_content
                        except (json.JSONDecodeError, ValueError):
                            # If parsing fails, return as-is
                            output_text = result_content
                    else:
                        output_text = result_content
                else:
                    # Fallback to the entire last element
                    output_text = json.dumps(last_element, indent=2)
            else:
                # Fallback to original behavior if not an array
                output_text = response_data.get("output", json.dumps(response_data, indent=2))
            
            # Convert CLI response to provider format
            return {
                "success": True,
                "data": {
                    "content": [{"type": "text", "text": output_text}],
                    "claude_code_result": response_data,
                    "usage": response_data[-1].get("usage", {}) if isinstance(response_data, list) and len(response_data) > 0 else {}
                },
                "provider": "anthropic-cli"
            }
            
        except subprocess.TimeoutExpired:
            logger.error("Claude Code CLI timed out")
            return {
                "success": False,
                "error": "Claude Code CLI request timed out (300s)",
                "provider": "anthropic-cli"
            }
        except Exception as e:
            logger.error(f"Claude Code CLI error: {e}")
            return {
                "success": False,
                "error": f"Claude Code CLI error: {str(e)}",
                "provider": "anthropic-cli"
            }
    
    async def call_api(self, model: str, messages: List[Dict[str, Any]], 
                      max_tokens: int = 10000, enable_caching: bool = False,
                      override_system_prompt: Optional[str] = None,
                      override_tools: Optional[List[Dict[str, Any]]] = None,
                      force_api: bool = False) -> Dict[str, Any]:
        """Make Anthropic API call using stored system prompt and tools"""
        
        # Use overrides if provided, otherwise use stored data
        if override_system_prompt is not None:
            self.set_system_prompt(override_system_prompt)
        if override_tools is not None:
            self.set_tools(override_tools)
        
        # Route to Claude Code CLI if environment variable is set and not forced to use API
        if self._should_use_claude_code_cli(messages, force_api):
            logger.info("🔀 Routing to Claude Code CLI (USE_CLAUDE_CODE_CLI=true)")
            return await self._call_claude_code_cli(model, messages, max_tokens, enable_caching)
        
        # Fall back to regular API 
        if force_api:
            logger.info("🔀 Using regular Anthropic API (forced - e.g., context search)")
        else:
            logger.info("🔀 Using regular Anthropic API (USE_CLAUDE_CODE_CLI=false or unset)")
        return await self._call_anthropic_api(model, messages, max_tokens, enable_caching)
    
    async def _call_anthropic_api(self, model: str, messages: List[Dict[str, Any]], 
                                 max_tokens: int = 4000, enable_caching: bool = False) -> Dict[str, Any]:
        """Original Anthropic API implementation"""
        
        # Get processed system data (using stored system prompt)
        system_data = self.get_processed_system_data(enable_caching)
        processed_tools = self.get_processed_tools(enable_caching) if self._raw_tools else None

        # Filter out system messages from messages array (Anthropic handles separately)
        user_messages = [msg for msg in messages if msg["role"] != "system"]
        
        request_data = {
            "model": model,
            "system": system_data,
            "messages": user_messages,
            "max_tokens": max_tokens
        }

        # Prepare headers
        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01"
        }
        
        # Add processed tools if we have them stored
        if processed_tools:
            request_data["tools"] = processed_tools
            headers["anthropic-beta"] = "tools-2024-05-16"
        
        # Make API call
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{self.base_url}/messages",
                json=request_data,
                headers=headers
            )
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "data": response.json(),
                    "provider": "anthropic"
                }
            else:
                return {
                    "success": False,
                    "error": f"Anthropic API error: {response.status_code} - {response.text}",
                    "provider": "anthropic"
                }
    
    def parse_response(self, response_data: Dict[str, Any]) -> Tuple[str, List[Dict[str, Any]]]:
        """Parse Anthropic response format (both API and CLI)"""
        
        # Check if this is a Claude Code CLI response
        if "claude_code_result" in response_data:
            # This is a CLI response
            text_content = ""
            tool_calls = []
            
            # Extract text from CLI response
            if "content" in response_data:
                for block in response_data["content"]:
                    if isinstance(block, dict) and block.get("type") == "text":
                        text_content += block.get("text", "")
                    elif isinstance(block, str):
                        text_content += block
            
            # CLI handles tool execution internally, so no tool_calls to parse
            # The result is already the final output
            return text_content, tool_calls
        
        # Original API response parsing
        content_blocks = response_data.get("content", [])
        text_content = ""
        tool_calls = []
        
        for block in content_blocks:
            if block.get("type") == "text":
                text_content += block.get("text", "")
            elif block.get("type") == "tool_use":
                tool_calls.append({
                    "function": {
                        "name": block.get("name"),
                        "arguments": block.get("input", {})
                    },
                    "anthropic_block": block  # Preserve original for tool_result linking
                })
        
        return text_content, tool_calls

    def format_tool_calls(self, tool_calls: List[Dict[str, Any]]) -> Dict[str, Any]:
        formatted_tool_calls = []
        for tool_call in tool_calls:
            anthropic_block = tool_call.get("anthropic_block")
            if anthropic_block:
                formatted_tool_calls.append(anthropic_block)
        
        return formatted_tool_calls
    
    def format_assistant_message_with_tool_calls(self, tool_calls: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Format assistant message with tool calls for Anthropic"""
        return {
            "role": "assistant",
            "content": self.format_tool_calls(tool_calls)
        }
    
    def contains_tool_calls(self, message: Any) -> bool:
        """Check if message contains Anthropic tool calls"""
        if not message:
            return False
        
        # For Anthropic, tool calls are embedded in the content array
        # Extract content from message if this is a full message object
        content = message
        if isinstance(message, dict) and "content" in message:
            content = message["content"]
        
        # Handle different content formats
        if isinstance(content, list):
            # Content is a list of tool use objects
            for item in content:
                if isinstance(item, dict) and item.get("type") == "tool_use":
                    return True
        elif isinstance(content, str):
            # Content is a string representation - check for Anthropic tool indicators
            tool_indicators = ["tool_use", "function_name", "mcp__", "write_file", "validate_python_script"]
            return any(indicator in content for indicator in tool_indicators)
        elif isinstance(content, dict):
            # Content is a single tool use object
            if content.get("type") == "tool_use":
                return True
        
        return False
    
    def get_message_text_length(self, message: Dict[str, Any]) -> int:
        """Get text length from Anthropic message, handling content array format"""
        content = message.get("content", "")
        
        # Handle Anthropic format (content is array of blocks)
        if isinstance(content, list):
            text_length = 0
            for block in content:
                if isinstance(block, dict) and block.get("type") == "text":
                    text_length += len(block.get("text", ""))
            return text_length
        
        # Handle string format (fallback)
        if isinstance(content, str):
            return len(content)
        
        return 0
    
    def get_tool_result_role(self) -> str:
        """Anthropic uses 'user' role for tool result messages"""
        return "user"
    
    def message_contains_function(self, message: Any, function_name: str) -> bool:
        """Check if Anthropic message contains a specific function call"""
        if not message:
            return False
        
        # Extract content from message if this is a full message object
        content = message
        if isinstance(message, dict) and "content" in message:
            content = message["content"]
        
        # Handle different content formats
        if isinstance(content, list):
            # Content is a list of tool use objects
            for item in content:
                if isinstance(item, dict) and item.get("type") == "tool_use":
                    tool_name = item.get("name", "")
                    if function_name in tool_name:
                        return True
        elif isinstance(content, str):
            # Content is a string representation
            return function_name in content
        elif isinstance(content, dict):
            # Content is a single tool use object
            if content.get("type") == "tool_use":
                tool_name = content.get("name", "")
                return function_name in tool_name
        
        return False
    
    def contains_tool_results(self, message: Any) -> bool:
        """Check if Anthropic message contains tool results"""
        if not message:
            return False
        
        # Extract content from message if this is a full message object
        content = message
        if isinstance(message, dict) and "content" in message:
            content = message["content"]
        
        # Handle different content formats
        if isinstance(content, list):
            # Content is a list of objects, check for tool_result type
            for item in content:
                if isinstance(item, dict) and item.get("type") == "tool_result":
                    return True
        elif isinstance(content, str):
            # Content is a string representation - check for Anthropic tool result indicators
            tool_result_indicators = ["tool_result", "tool_use_id"]
            return any(indicator in content for indicator in tool_result_indicators)
        elif isinstance(content, dict):
            # Content is a single tool result object
            if content.get("type") == "tool_result":
                return True
        
        return False
                
    
    def format_tool_results(self, tool_calls: List[Dict[str, Any]], 
                           tool_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Format tool results for Anthropic API"""
        anthropic_tool_results = []
        
        for i, tool_result in enumerate(tool_results):
            tool_call = tool_calls[i]
            anthropic_block = tool_call.get("anthropic_block", {})
            tool_use_id = anthropic_block.get("id", tool_call.get("id", f"tool_{i}"))
            
            # Extract content from tool result
            if tool_result.get("success"):
                result_data = tool_result.get("result", "")
                
                # Handle MCP CallToolResult objects
                if hasattr(result_data, 'content') and result_data.content:
                    if hasattr(result_data.content[0], 'text'):
                        tool_content = result_data.content[0].text
                    else:
                        tool_content = str(result_data.content[0])
                else:
                    tool_content = result_data
                    
                if not isinstance(tool_content, str):
                    tool_content = json.dumps(tool_content, default=str)
            else:
                tool_content = f"Error: {tool_result.get('error', 'Unknown error')}"
            
            anthropic_tool_results.append({
                "tool_use_id": tool_use_id,
                "type": "tool_result",
                "content": [
                    {
                        "type": "text",
                        "text": tool_content
                    }
                ]
            })
        
        return {
            "role": "user",
            "content": anthropic_tool_results
        }
    
    def get_processed_system_data(self, enable_caching: bool = True) -> List[Dict[str, Any]]:
        """Get system prompt processed for Anthropic with caching control"""
        cache_key = f"system_{enable_caching}"
        
        if cache_key not in self._processed_system_cache:
            if not self._raw_system_prompt:
                return []
                
            system_data = [
                {
                    "type": "text",
                    "text": self._raw_system_prompt
                }
            ]
            
            # Add cache control only if caching is enabled
            if enable_caching and self.supports_caching():
                system_data[0]["cache_control"] = {
                    "type": "ephemeral",
                    "ttl": "1h"
                }
            
            self._processed_system_cache[cache_key] = system_data
            
        return self._processed_system_cache[cache_key]
    
    def get_processed_tools(self, enable_caching: bool = True) -> List[Dict[str, Any]]:
        """Get tools processed for Anthropic with caching control"""
        if not self._raw_tools:
            return []
            
        cache_key = f"tools_{enable_caching}_{len(self._raw_tools)}"
        
        if cache_key not in self._processed_tools_cache:
            anthropic_tools = []
            for i, tool in enumerate(self._raw_tools):
                anthropic_tool = {
                    "name": tool["function"]["name"],
                    "description": tool["function"]["description"],
                    "input_schema": tool["function"]["parameters"]
                }
                
                # Add cache control to the last tool only if caching is enabled
                if enable_caching and self.supports_caching() and i == len(self._raw_tools) - 1:
                    anthropic_tool["cache_control"] = {
                        "type": "ephemeral",
                        "ttl": "1h"
                    }
                
                anthropic_tools.append(anthropic_tool)
            
            self._processed_tools_cache[cache_key] = anthropic_tools
            
        return self._processed_tools_cache[cache_key]
    
    def create_simulated_tool_call(self, function_name: str, arguments: Dict[str, Any], call_id: str = None) -> Dict[str, Any]:
        """Create a simulated tool call in Anthropic's format"""
        if call_id is None:
            call_id = f"toolu_{function_name}_{hash(function_name) % 10000:04d}"
        
        return {
            "type": "tool_use",
            "id": call_id,
            "name": function_name,
            "input": arguments
        }
    
    def create_simulated_assistant_message_with_tool_calls(self, content: str, tool_calls: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create a simulated assistant message with tool calls in Anthropic's format"""
        # Anthropic format: content is a list with text and tool_use objects
        content_list = []
        
        if content:
            content_list.append({
                "type": "text",
                "text": content
            })
        
        # Add tool calls to content list
        content_list.extend(tool_calls)
        
        return {
            "role": "assistant",
            "content": content_list
        }
    
    def create_simulated_tool_result(self, tool_call_id: str, content: str) -> Dict[str, Any]:
        """Create a simulated tool result message in Anthropic's format"""
        return {
            "role": "user",
            "content": [
                {
                    "type": "tool_result",
                    "tool_use_id": tool_call_id,
                    "content": content
                }
            ]
        }