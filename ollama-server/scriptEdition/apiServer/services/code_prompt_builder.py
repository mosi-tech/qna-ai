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
        """Load code prompt template"""
        template_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), 
            "..", 
            "config", 
            "code-prompt-template-optimized.txt"
        )
        
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                self.code_prompt_template = f.read()
            self.logger.info("✅ Loaded code prompt template")
        except FileNotFoundError:
            self.logger.error(f"❌ Code prompt template not found: {template_path}")
            self.code_prompt_template = "Generate Python script using the provided functions."
    
    
    async def build_enriched_prompt(self, user_query: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Build enriched prompt by analyzing query and selecting relevant MCP functions
        
        Args:
            user_query: User's financial question
            context: Optional context information
            
        Returns:
            Dict containing selected functions, schemas, and enriched prompt
        """
        try:
            self.logger.info(f"🔍 Building enriched prompt for query: {user_query[:100]}...")
            
            # Ensure MCP tools are loaded in LLM service
            await self.llm_service.ensure_tools_loaded()
            
            # Step 1: Analyze query and select functions
            function_selection = await self._analyze_and_select_functions(user_query, context)
            
            # Step 2: Fetch docstrings for selected functions (simplified)
            function_schemas = await self._get_function_schemas_from_llm(function_selection['selected_functions'])
            
            # Step 3: Build enriched prompt
            enriched_prompt = self._build_prompt(user_query, function_selection, function_schemas)
            
            result = {
                "status": "success",
                "analysis_type": function_selection.get('analysis_type', 'general'),
                "selected_functions": function_selection['selected_functions'],
                "function_schemas": function_schemas,
                "suggested_parameters": function_selection.get('suggested_parameters', {}),
                "enriched_prompt": enriched_prompt,
                "timestamp": datetime.now().isoformat()
            }
            
            self.logger.info(f"✅ Built enriched prompt with {len(function_selection['selected_functions'])} functions")
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
    
    def _build_prompt(self, user_query: str, function_selection: Dict, function_schemas: Dict[str, str]) -> str:
        """Build the enriched prompt for code generator using template file"""
        
        # Build function documentation section
        function_docs = "\n\n".join([
            f"=== {func_name} ===\n{schema}"
            for func_name, schema in function_schemas.items()
        ])
        
        # Use template and format with variables
        enriched_prompt = self.code_prompt_template.format(
            user_query=user_query,
            analysis_type=function_selection.get('analysis_type', 'general'),
            function_docs=function_docs,
            suggested_parameters=json.dumps(function_selection.get('suggested_parameters', {}), indent=2)
        )
        
        # Save prompt to debug folder for troubleshooting
        self._save_prompt_for_debugging(enriched_prompt, user_query)
        
        return enriched_prompt
    
    def _save_prompt_for_debugging(self, prompt: str, user_query: str):
        """Save generated prompt to code_gen folder for debugging"""
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
            filename = f"code_gen_prompt-{timestamp}.txt"
            filepath = os.path.join(code_gen_dir, filename)
            
            # Add header with metadata
            header = f"""# Code Generation Prompt Debug File
# Generated: {datetime.now().isoformat()}
# User Query: {user_query[:100]}{'...' if len(user_query) > 100 else ''}
# ==========================================

"""
            
            # Save prompt with header
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(header + prompt)
            
            self.logger.info(f"📝 Saved debug prompt to {filename}")
            
        except Exception as e:
            self.logger.warning(f"⚠️ Failed to save debug prompt: {e}")
            # Don't fail the main operation if debug saving fails

# Factory function for easy initialization
def create_code_prompt_builder() -> CodePromptBuilderService:
    """Create and return a CodePromptBuilderService instance"""
    return CodePromptBuilderService()