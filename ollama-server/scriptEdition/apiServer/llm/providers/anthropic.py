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
            
        # Use environment variable to control CLI usage regardless of tool presence
        return os.getenv("USE_CLAUDE_CODE_CLI", "false").lower() == "true"
    
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
                                   max_tokens: int = 4000, enable_caching: bool = False) -> Dict[str, Any]:
        """Use Claude Code CLI instead of API for tool-enabled requests"""
        try:
            # Extract the user message (last message)
            user_message = ""
            for msg in reversed(messages):
                if msg["role"] == "user":
                    if isinstance(msg["content"], str):
                        user_message = msg["content"]
                    elif isinstance(msg["content"], list):
                        # Extract text from content blocks
                        text_parts = []
                        for block in msg["content"]:
                            if isinstance(block, dict) and block.get("type") == "text":
                                text_parts.append(block.get("text", ""))
                            elif isinstance(block, str):
                                text_parts.append(block)
                        user_message = "\n".join(text_parts)
                    break
            
            if not user_message:
                raise Exception("No user message found for Claude Code CLI")
            
            # Create MCP config for Claude Code CLI
            config_dir = os.path.dirname(os.path.abspath(__file__))
            mcp_config_path = os.path.join(config_dir, "..", "..", "config", "claude_mcp_servers.json")
            mcp_config_path = os.path.abspath(mcp_config_path)
            
            if not os.path.exists(mcp_config_path):
                raise Exception(f"MCP config file not found: {mcp_config_path}")
            
            # Set working directory for script generation
            working_dir = "/Users/shivc/Documents/Workspace/JS/qna-ai-admin/mcp-server"
            os.makedirs(working_dir, exist_ok=True)
            
            # Get system prompt if available
            system_prompt = self._raw_system_prompt or "You are a helpful assistant."
            
            # Build CLI command - simple approach with just claude
            cli_command = [
                "claude",
                "--append-system-prompt", system_prompt,
                "-p", user_message,
                "--output-format", "json",
                "--mcp-config", mcp_config_path,
                "--permission-mode", "bypassPermissions",
                "--verbose"
                # "--dangerously-skip-permissions"
            ]
            
            # logger.info(f"🚀 Calling Claude Code CLI with MCP config: {mcp_config_path}")
            # logger.info(f"📄 Using system prompt: {system_prompt[:100]}...")
            # logger.debug(f"CLI command: {cli_command}")
            
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
                # Stream output in real-time AND capture it
                logger.info("🔄 Streaming Claude CLI output in real-time...")
                
                process = subprocess.Popen(
                    cli_command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    bufsize=1,  # Line buffered
                    cwd=working_dir
                )
                
                # Use our streaming method
                result_data = self._stream_subprocess_output(process, timeout=300)
                
                # Create result object compatible with the rest of the code
                result = type('Result', (), {
                    'returncode': result_data['returncode'],
                    'stdout': result_data['stdout'],
                    'stderr': result_data['stderr']
                })()
                
            else:
                # Standard execution - capture output normally
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
                
                # Extract the result field which is stringified JSON - return as-is
                if isinstance(last_element, dict) and "result" in last_element:
                    output_text = last_element["result"]  # Return stringified JSON as-is
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
                      max_tokens: int = 4000, enable_caching: bool = False,
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