"""
MCP Integration and Tool Management
"""

import json
import logging
import os
from typing import Dict, Any, List
from integrations.mcp.mcp_client import mcp_client, initialize_mcp_client

logger = logging.getLogger("mcp-integration")


class MCPIntegration:
    """Handles MCP client connections and tool management"""
    
    def __init__(self):
        self.mcp_client = mcp_client  # Use singleton MCP client
        self.mcp_initialized = False
    
    async def ensure_mcp_initialized(self) -> bool:
        """Ensure MCP client is initialized - relies on SimplifiedMCPLoader"""
        if self.mcp_initialized:
            return True
            
        # Check if the global MCP client is already initialized by SimplifiedMCPLoader
        if self.mcp_client and hasattr(self.mcp_client, 'available_tools') and self.mcp_client.available_tools:
            self.mcp_initialized = True
            logger.info(f"✅ MCP client already initialized with {len(self.mcp_client.available_tools)} tools")
            return True
        else:
            logger.warning("⚠️ MCP client not initialized - should be initialized by SimplifiedMCPLoader in LLMService")
            return False
    
    def get_mcp_tools(self) -> List[Dict[str, Any]]:
        """Convert MCP tools to OpenAI-compatible format for LLM"""
        if not self.mcp_client or not self.mcp_client.available_tools:
            logger.warning("No MCP tools available")
            return []
        
        all_tools = []
        
        for tool_name, tool_schema in self.mcp_client.available_tools.items():
            try:
                # Convert MCP tool schema to OpenAI function calling format
                tool = {
                    "type": "function",
                    "function": {
                        "name": tool_name,
                        "description": tool_schema.get("description", f"MCP tool: {tool_name}"),
                        "parameters": tool_schema.get("inputSchema", {})
                    }
                }
                all_tools.append(tool)
                
            except Exception as e:
                logger.warning(f"Failed to convert tool {tool_name} to OpenAI format: {e}")
                continue
        
        logger.debug(f"Converted {len(all_tools)} MCP tools to OpenAI format")
        return all_tools
    
    def is_forbidden_function_call(self, function_name: str, excluded_tools: List[str] = None) -> bool:
        """Check if function call is forbidden based on provided exclusion list"""
        if excluded_tools is None:
            excluded_tools = []
        
        # Check both full name and base name (without MCP server prefix)
        base_function_name = function_name.split("__")[-1] if "__" in function_name else function_name
        
        return (function_name in excluded_tools or 
                base_function_name in excluded_tools or
                any(pattern in function_name for pattern in excluded_tools) or
                any(pattern in base_function_name for pattern in excluded_tools))
    
    def massage_file_tool_paths(self, function_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Convert relative filenames to absolute paths for file tools"""
        if function_name in ["mcp__mcp-validation-server__write_file", 
                           "mcp__mcp-validation-server__read_file",
                           "mcp__mcp-validation-server__validate_python_script"]:
            
            if "filename" in arguments or "script_filename" in arguments:
                filename_key = "filename" if "filename" in arguments else "script_filename"
                filename = arguments[filename_key]
                
                # If it's not an absolute path, convert to absolute path
                if not os.path.isabs(filename):
                    # Use validation server scripts directory
                    validation_server_dir = os.path.join(
                        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        "mcp-server"
                    )
                    
                    if function_name == "mcp__mcp-validation-server__validate_python_script":
                        # For validation, file should be in scripts directory
                        arguments[filename_key] = filename
                    else:
                        # For write/read, use scripts directory as well
                        scripts_dir = os.path.join(validation_server_dir, "scripts")
                        os.makedirs(scripts_dir, exist_ok=True)
                        arguments[filename_key] = os.path.join(scripts_dir, filename)
                    
                    logger.debug(f"Massaged {filename_key}: {filename} -> {arguments[filename_key]}")
        
        return arguments
    
    def validate_mcp_functions(self, tool_calls: list, excluded_tools: List[str] = None) -> Dict[str, Any]:
        """Validate that tool calls only use allowed MCP functions"""
        validation_results = []
        
        for tool_call in tool_calls:
            function_name = tool_call.get("function", {}).get("name", "")
            
            if self.is_forbidden_function_call(function_name, excluded_tools):
                validation_results.append({
                    "function": function_name,
                    "status": "forbidden",
                    "reason": "This function is not allowed for this service type."
                })
            else:
                validation_results.append({
                    "function": function_name,
                    "status": "allowed"
                })
        
        return {
            "validation_results": validation_results,
            "all_valid": all(result["status"] == "allowed" for result in validation_results)
        }
    
    async def generate_tool_calls_only(self, tool_calls: list) -> Dict[str, Any]:
        """Process tool calls and return results"""
        if not self.mcp_client:
            return {
                "success": False,
                "error": "MCP client not initialized",
                "tool_results": []
            }
        
        tool_results = []
        
        for tool_call in tool_calls:
            function_name = tool_call.get("function", {}).get("name", "")
            arguments = tool_call.get("function", {}).get("arguments", {})
            
            try:
                # Apply path massaging for file tools
                massaged_args = self.massage_file_tool_paths(function_name, arguments)
                
                # Call the MCP function
                result = await self.mcp_client.call_tool(function_name, massaged_args)
                
                tool_results.append({
                    "function": function_name,
                    "arguments": massaged_args,
                    "result": result,
                    "success": True
                })
                
            except Exception as e:
                logger.error(f"MCP tool call failed for {function_name}: {e}")
                tool_results.append({
                    "function": function_name,
                    "arguments": arguments,
                    "error": str(e),
                    "success": False
                })
        
        return {
            "success": True,
            "tool_results": tool_results
        }