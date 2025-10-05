"""
MCP Integration and Tool Management
"""

import json
import logging
import os
from typing import Dict, Any, List
from mcp_client import mcp_client, initialize_mcp_client

logger = logging.getLogger("mcp-integration")


class MCPIntegration:
    """Handles MCP client connections and tool management"""
    
    def __init__(self):
        self.mcp_client = mcp_client  # Use singleton MCP client
        self.mcp_initialized = False
    
    async def ensure_mcp_initialized(self) -> bool:
        """Ensure MCP client is initialized"""
        if self.mcp_initialized:
            return True
            
        try:
            # Load MCP server configuration
            config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ollama-mcp-config.json")
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            # Initialize MCP client
            await initialize_mcp_client(config)
            self.mcp_initialized = True
            logger.info(f"MCP client initialized with {len(self.mcp_client.available_tools)} tools")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize MCP client: {e}")
            return False
    
    def get_mcp_tools_for_openai(self) -> List[Dict[str, Any]]:
        """Convert MCP tools to OpenAI-compatible format for LLM"""
        if not self.mcp_client or not self.mcp_client.available_tools:
            logger.warning("No MCP tools available")
            return []
        
        openai_tools = []
        
        for tool_name, tool_schema in self.mcp_client.available_tools.items():
            try:
                # Convert MCP tool schema to OpenAI function calling format
                openai_tool = {
                    "type": "function",
                    "function": {
                        "name": tool_name,
                        "description": tool_schema.get("description", f"MCP tool: {tool_name}"),
                        "parameters": tool_schema.get("inputSchema", {})
                    }
                }
                openai_tools.append(openai_tool)
                
            except Exception as e:
                logger.warning(f"Failed to convert tool {tool_name} to OpenAI format: {e}")
                continue
        
        logger.debug(f"Converted {len(openai_tools)} MCP tools to OpenAI format")
        return openai_tools
    
    def is_forbidden_function_call(self, function_name: str) -> bool:
        """Check if function call is forbidden (validation-only functions)"""
        forbidden_patterns = [
            "alpaca_market_screener_most_actives",
            "alpaca_market_stocks_bars", 
            "alpaca_market_stocks_snapshots",
            "alpaca_market_stocks_quotes_latest",
            "alpaca_market_stocks_trades_latest",
            "alpaca_market_screener_top_gainers",
            "alpaca_market_screener_top_losers",
            "alpaca_market_news",
            "alpaca_trading_account",
            "alpaca_trading_positions",
            "alpaca_trading_orders",
            "alpaca_trading_portfolio_history",
            "alpaca_trading_clock",
            "eodhd_eod_data",
            "eodhd_real_time", 
            "eodhd_fundamentals",
            "eodhd_dividends",
            "eodhd_splits",
            "eodhd_technical",
            "eodhd_screener",
            "eodhd_search",
            "eodhd_exchanges_list",
            "eodhd_exchange_symbols",
            "calculate_"
        ]
        
        return any(pattern in function_name for pattern in forbidden_patterns)
    
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
    
    def validate_mcp_functions(self, tool_calls: list) -> Dict[str, Any]:
        """Validate that tool calls only use allowed MCP functions"""
        validation_results = []
        
        for tool_call in tool_calls:
            function_name = tool_call.get("function", {}).get("name", "")
            
            if self.is_forbidden_function_call(function_name):
                validation_results.append({
                    "function": function_name,
                    "status": "forbidden",
                    "reason": "This function is not allowed in script generation. Use validation-server functions only."
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