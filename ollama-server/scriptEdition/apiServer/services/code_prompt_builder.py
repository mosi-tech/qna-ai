#!/usr/bin/env python3
"""
Code Prompt Builder Service

Analyzes financial questions, selects relevant MCP functions, fetches their docstrings,
and builds enriched prompts for the code generator service.
"""

import json
import logging
import os
from datetime import datetime
from typing import Dict, Any, Optional, List

from llm import create_code_prompt_builder_llm, LLMService
from .base_service import BaseService

class CodePromptBuilderService(BaseService):
    """Service that analyzes queries and builds enriched prompts for code generation"""
    
    def __init__(self, llm_service: Optional[LLMService] = None):
        super().__init__(llm_service=llm_service, service_name="code-prompt-builder")
    
    def _create_default_llm(self) -> LLMService:
        """Create default LLM service for code prompt builder"""
        return create_code_prompt_builder_llm()
    
    def _get_system_prompt_filename(self) -> str:
        """Use code prompt builder specific system prompt"""
        return "system-prompt-code-prompt-builder.txt"
    
    def _initialize_service_specific(self):
        """Initialize code prompt builder specific components"""
        # Load code prompt template
        self._load_code_prompt_template()
    
    
    def _load_code_prompt_template(self):
        """Load fixed system prompt template"""
        template_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), 
            "..", 
            "config", 
            "system-prompt-code-generation-fixed.txt"
        )
        
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                self.fixed_system_prompt = f.read()
            self.logger.info("✅ Loaded fixed system prompt for code generation")
        except FileNotFoundError:
            self.logger.error(f"❌ Fixed system prompt not found: {template_path}")
            self.fixed_system_prompt = "You are a financial script generator. Generate Python scripts using the provided MCP functions."
    
    
    async def create_code_prompt_messages(self, user_query: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Build enriched prompt with separate system prompt and user messages
        
        Args:
            user_query: User's financial question
            context: Optional context information
            
        Returns:
            Dict containing system prompt, user messages, and metadata
        """
        try:
            self.logger.info(f"🔍 Building enriched prompt for query: {user_query[:100]}...")
            
            # Ensure MCP tools are loaded in LLM service
            await self.llm_service.ensure_tools_loaded()
            
            # Step 1: Analyze query and select functions
            function_selection = await self._analyze_and_select_functions(user_query, context)
            
            # Step 2: Fetch docstrings for selected functions
            function_schemas = await self._get_function_schemas_from_llm(function_selection['selected_functions'])
            
            # Step 3: Build message structure with simulated tool calls using provider-agnostic methods
            system_prompt = self.fixed_system_prompt
            
            # Build messages simulating tool calls for function documentation
            user_messages = []
            
            # Initial user query
            query_message = f"Write a Python script to answer this question: {user_query}"
            user_messages.append({"role": "user", "content": query_message})
            
            # Get the provider for format-specific tool calls
            provider = self.llm_service.provider
            
            # Create simulated tool calls using provider-specific format
            tool_calls = []
            call_ids = {}
            for func_name in function_schemas.keys():
                arguments = {"function_name": func_name}
                call_id = f"call_{func_name}"
                
                tool_call = provider.create_simulated_tool_call("get_function_docstring", arguments, call_id)
                tool_calls.append(tool_call)
                call_ids[func_name] = call_id
            
            # Create assistant message with tool calls using provider-specific format
            assistant_message = provider.create_simulated_assistant_message_with_tool_calls(
                "I need to get documentation for the required functions first.",
                tool_calls
            )
            user_messages.append(assistant_message)
            
            # Create tool result messages using provider-specific format
            for func_name, schema in function_schemas.items():
                # Format the schema as expected structured JSON output for get_function_docstring
                structured_result = {
                    "success": True,
                    "function_name": func_name,
                    "original_name": func_name, 
                    "docstring": schema,
                    "signature": f"{func_name}(**kwargs)",
                    "module": "mcp_functions"
                }
                
                tool_result = provider.create_simulated_tool_result(
                    call_ids[func_name], 
                    json.dumps(structured_result, indent=2)
                )
                user_messages.append(tool_result)
            
            result = {
                "status": "success",
                "analysis_type": function_selection.get('analysis_type', 'general'),
                "selected_functions": function_selection['selected_functions'],
                "function_schemas": function_schemas,
                "suggested_parameters": function_selection.get('suggested_parameters', {}),
                "system_prompt": system_prompt,
                "user_messages": user_messages,
                "timestamp": datetime.now().isoformat()
            }
            
            # Save messages for debugging
            self._save_messages_for_debugging(result, user_query)
            
            self.logger.info(f"✅ Built enriched prompt with {len(function_selection['selected_functions'])} functions as simulated tool calls in {len(user_messages)} messages")
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Error building enriched prompt: {e}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def _analyze_and_select_functions(self, user_query: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Use LLM to analyze query and select relevant MCP functions"""
        
        # Build analysis prompt
        analysis_prompt = f"""
        FINANCIAL QUERY: {user_query}
        
        Analyze this financial question and select the most relevant MCP functions needed.
        
        Return only JSON with:
        - analysis_type: Single word category (portfolio, correlation, risk, etc.)
        - selected_functions: Array of 3-6 function names only (no descriptions)
        - suggested_parameters: Essential parameters only
        
        Be concise. No function descriptions.
        """
        
        try:
            response = await self.llm_service.make_request(
                messages=[{
                    "role": "user", 
                    "content": analysis_prompt
                }],
                system_prompt=self.system_prompt
            )
            
            # Check if LLM request was successful
            if not response.get("success"):
                self.logger.error(f"❌ LLM request failed: {response.get('error')}")
                raise Exception(f"LLM request failed: {response.get('error')}")
            
            # Parse JSON response
            function_selection = json.loads(response["content"])
            self.logger.info(f"📋 Selected {len(function_selection.get('selected_functions', []))} functions")
            return function_selection
            
        except Exception as e:
            self.logger.error(f"❌ Error selecting functions: {e}")
            # Fallback to basic function set
            return {
                "analysis_type": "general",
                "selected_functions": [
                    "alpaca_market_stocks_bars",
                    "calculate_returns_metrics",
                    "calculate_risk_metrics"
                ],
                "suggested_parameters": {
                    "symbols": ["SPY"],
                    "analysis_period_days": 180
                }
            }
    
    async def _get_function_schemas_from_llm(self, function_names: List[str]) -> Dict[str, str]:
        """Get detailed function schemas with docstrings via LLM service tool calls"""
        schemas = {}
        
        self.logger.info(f"🔍 Getting detailed schemas for {len(function_names)} functions")
        
        # Get available tools from LLM service to verify functions exist
        available_tools = self.llm_service.default_tools
        tool_map = {tool.get("function", {}).get("name", ""): tool for tool in available_tools if tool.get("type") == "function"}
        
        self.logger.info(f"📋 Available tools in LLM service: {len(tool_map)}")
        
        for function_name in function_names:
            try:
                # First check if function exists in available tools
                if function_name not in tool_map:
                    schemas[function_name] = f"Function: {function_name} (not found in available tools)"
                    self.logger.warning(f"⚠️ Function {function_name} not found in available tools")
                    continue
                
                # Try to get detailed docstring via MCP docstring tools
                docstring = await self._fetch_function_docstring(function_name)
                
                if docstring:
                    schemas[function_name] = docstring
                    self.logger.info(f"📖 Got detailed docstring for {function_name}")
                else:
                    # Fallback to basic tool schema if docstring fetch fails
                    tool_func = tool_map[function_name].get("function", {})
                    schema = f"Function: {function_name}\n"
                    schema += f"Description: {tool_func.get('description', 'No description available')}\n"
                    
                    parameters = tool_func.get('parameters', {})
                    if parameters:
                        schema += f"Parameters: {json.dumps(parameters, indent=2)}"
                    
                    schemas[function_name] = schema
                    self.logger.info(f"📖 Used basic schema for {function_name} (docstring unavailable)")
                    
            except Exception as e:
                self.logger.error(f"❌ Error getting schema for {function_name}: {e}")
                schemas[function_name] = f"Function: {function_name} (error fetching schema)"
        
        return schemas
    
    async def _fetch_function_docstring(self, function_name: str) -> Optional[str]:
        """Fetch detailed docstring for a function using server-specific docstring tool"""
        # Extract server name and base function name
        # e.g., "financial-analysis__alpaca_market_stocks_bars" -> server="financial-analysis", base="alpaca_market_stocks_bars"
        if "__" not in function_name:
            self.logger.debug(f"No server prefix in function name: {function_name}")
            return None
            
        server_name, base_function_name = function_name.split("__", 1)
        
        try:
            self.logger.debug(f"Attempting docstring fetch for: {base_function_name} from server: {server_name}")
            
            # Try direct MCP client call
            from integrations.mcp.mcp_client import mcp_client
            
            if not mcp_client:
                self.logger.debug("MCP client not available")
                return None
            
            # Construct the expected docstring tool name for this server
            docstring_tool = f"{server_name}__get_function_docstring"
            
            # Check if this specific docstring tool is available
            available_tool_names = {tool.get("function", {}).get("name", "") for tool in self.llm_service.default_tools if tool.get("type") == "function"}
            
            if docstring_tool not in available_tool_names:
                self.logger.debug(f"Docstring tool {docstring_tool} not available")
                return None
            
            self.logger.debug(f"🔧 Using {docstring_tool} for {base_function_name}")
            
            try:
                tool_result = await mcp_client.call_tool(
                    docstring_tool,
                    {"function_name": base_function_name}
                )
                
                # Parse the result - handle various formats
                if hasattr(tool_result, 'content') and tool_result.content:
                    text_content = tool_result.content[0].text
                    try:
                        parsed_result = json.loads(text_content.strip())
                        if parsed_result.get('success') and parsed_result.get('docstring'):
                            docstring = parsed_result['docstring']
                            self.logger.info(f"✅ Got docstring for {base_function_name} from {server_name}")
                            return docstring
                    except json.JSONDecodeError:
                        # Try as plain text if it's substantial
                        if text_content and len(text_content) > 50:
                            self.logger.info(f"✅ Got plain text docstring for {base_function_name} from {server_name}")
                            return text_content
                            
            except Exception as e:
                self.logger.debug(f"⚠️ Error calling {docstring_tool}: {e}")
            
            return None
            
        except Exception as e:
            self.logger.debug(f"Error in docstring fetch for {base_function_name}: {e}")
            return None
    
    def _save_messages_for_debugging(self, result: Dict[str, Any], user_query: str):
        """Save generated messages to code_gen folder for debugging"""
        try:
            # Create timestamp for filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Create code_gen directory path
            code_gen_dir = os.path.join(
                os.path.dirname(os.path.abspath(__file__)), 
                "..", 
                "code_gen"
            )
            
            # Ensure directory exists
            os.makedirs(code_gen_dir, exist_ok=True)
            
            # Create filename with timestamp
            filename = f"code_gen_messages-{timestamp}.txt"
            filepath = os.path.join(code_gen_dir, filename)
            
            # Build debug content with separated messages
            debug_content = f"""# Code Generation Messages Debug File
# Generated: {datetime.now().isoformat()}
# User Query: {user_query[:100]}{'...' if len(user_query) > 100 else ''}
# ==========================================

=== SYSTEM PROMPT ===
{result['system_prompt']}

"""
            
            # Add each message separately with proper type detection
            for i, message in enumerate(result['user_messages'], 1):
                role = message.get('role', 'unknown')
                
                if role == 'user':
                    msg_type = "(User Query)"
                elif role == 'assistant':
                    if message.get('tool_calls'):
                        msg_type = f"(Assistant with {len(message['tool_calls'])} tool calls)"
                    else:
                        msg_type = "(Assistant)"
                elif role == 'tool':
                    tool_call_id = message.get('tool_call_id', 'unknown')
                    msg_type = f"(Tool Result: {tool_call_id})"
                else:
                    msg_type = f"(Role: {role})"
                
                content = message.get('content', '')
                if message.get('tool_calls'):
                    content += f"\n\nTool Calls: {json.dumps(message['tool_calls'], indent=2)}"
                
                debug_content += f"""=== MESSAGE {i} {msg_type} ===
{content}

"""
            
            debug_content += f"""=== METADATA ===
Analysis Type: {result['analysis_type']}
Selected Functions: {len(result['selected_functions'])}
Function List: {result['selected_functions']}
Total Messages: {len(result['user_messages'])}
Tool Calls Simulated: {len([m for m in result['user_messages'] if m.get('role') == 'tool'])}
"""
            
            # Save messages with header
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(debug_content)
            
            self.logger.info(f"📝 Saved debug messages to {filename}")
            
        except Exception as e:
            self.logger.warning(f"⚠️ Failed to save debug messages: {e}")
            # Don't fail the main operation if debug saving fails

# Factory function for easy initialization
def create_code_prompt_builder() -> CodePromptBuilderService:
    """Create and return a CodePromptBuilderService instance"""
    return CodePromptBuilderService()