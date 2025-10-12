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
from llm.cache import ProviderCacheManager
from integrations.mcp.mcp_client import MCPClient

logger = logging.getLogger("code-prompt-builder")

class CodePromptBuilderService:
    """Service that analyzes queries and builds enriched prompts for code generation"""
    
    def __init__(self, llm_service: Optional[LLMService] = None):
        self.llm_service = llm_service or create_code_prompt_builder_llm()
        self.cache_manager = ProviderCacheManager(self.llm_service.provider, enable_caching=True)
        
        # Load system prompt for function selection
        self._load_system_prompt()
        
        # Load code prompt template
        self._load_code_prompt_template()
        
        # Initialize MCP client for docstring fetching
        self.mcp_client = MCPClient()
        self._mcp_initialized = False
        
        logger.info(f"🔧 Initialized Code Prompt Builder with {self.llm_service.provider_type}")
    
    def _load_system_prompt(self):
        """Load system prompt for code prompt builder"""
        prompt_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), 
            "..", 
            "config", 
            "system-prompt-code-prompt-builder.txt"
        )
        
        try:
            with open(prompt_path, 'r', encoding='utf-8') as f:
                self.system_prompt = f.read()
            logger.info("✅ Loaded code prompt builder system prompt")
        except FileNotFoundError:
            logger.error(f"❌ System prompt not found: {prompt_path}")
            self.system_prompt = "You are a financial analysis tool selector."
    
    def _load_code_prompt_template(self):
        """Load code prompt template"""
        template_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), 
            "..", 
            "config", 
            "code-prompt-template.txt"
        )
        
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                self.code_prompt_template = f.read()
            logger.info("✅ Loaded code prompt template")
        except FileNotFoundError:
            logger.error(f"❌ Code prompt template not found: {template_path}")
            self.code_prompt_template = "Generate Python script using the provided functions."
    
    async def _initialize_mcp_client(self):
        """Initialize MCP client with server configurations"""
        try:
            # Load MCP config
            config_path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)), 
                "..", 
                "config", 
                "ollama-mcp-config.json"
            )
            
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Store server configurations
            self.mcp_client.server_configs = config.get("mcpServers", {})
            logger.info(f"✅ Loaded MCP config with {len(self.mcp_client.server_configs)} servers")
            
            # Initialize tools discovery
            await self.mcp_client.discover_all_tools()
            logger.info(f"✅ Discovered {len(self.mcp_client.available_tools)} MCP tools")
            
        except Exception as e:
            logger.error(f"❌ Error loading MCP config: {e}")
            # Set fallback config
            self.mcp_client.server_configs = {
                "financial-server": {
                    "command": "python",
                    "args": ["/Users/shivc/Documents/Workspace/JS/qna-ai-admin/mcp-server/financial_server.py"],
                    "env": {"USE_MOCK_FINANCIAL_DATA": "true"}
                },
                "analytics-server": {
                    "command": "python",
                    "args": ["/Users/shivc/Documents/Workspace/JS/qna-ai-admin/mcp-server/analytics_server.py"]
                }
            }
    
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
            logger.info(f"🔍 Building enriched prompt for query: {user_query[:100]}...")
            
            # Initialize MCP client if not already done
            if not self._mcp_initialized:
                await self._initialize_mcp_client()
                self._mcp_initialized = True
            
            # Step 1: Analyze query and select functions
            function_selection = await self._analyze_and_select_functions(user_query, context)
            
            # Step 2: Fetch docstrings for selected functions
            function_schemas = await self._fetch_function_schemas(function_selection['selected_functions'])
            
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
            
            logger.info(f"✅ Built enriched prompt with {len(function_selection['selected_functions'])} functions")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error building enriched prompt: {e}")
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
        - workflow_steps: Brief description of analysis approach
        
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
                logger.error(f"❌ LLM request failed: {response.get('error')}")
                raise Exception(f"LLM request failed: {response.get('error')}")
            
            # Parse JSON response
            function_selection = json.loads(response["content"])
            logger.info(f"📋 Selected {len(function_selection.get('selected_functions', []))} functions")
            return function_selection
            
        except Exception as e:
            logger.error(f"❌ Error selecting functions: {e}")
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
    
    async def _fetch_function_schemas(self, function_names: List[str]) -> Dict[str, str]:
        """Fetch docstrings for selected functions via MCP"""
        schemas = {}
        
        logger.info(f"🔍 Fetching schemas for {len(function_names)} functions")
        logger.info(f"📋 Available MCP tools: {len(self.mcp_client.available_tools)}")
        
        for function_name in function_names:
            try:
                # Try financial server first, then analytics server
                servers_to_try = ["financial-server", "analytics-server"]
                
                docstring = None
                for server in servers_to_try:
                    tool_name = f"{server}__get_function_docstring"
                    logger.info(f"🔧 Trying {tool_name} for {function_name}")
                    
                    try:
                        # Check if tool exists
                        if not self.mcp_client.validate_function_exists(tool_name):
                            logger.warning(f"⚠️ Tool {tool_name} not found in available tools")
                            continue
                            
                        result = await self.mcp_client.call_tool(
                            tool_name,
                            {"function_name": function_name}
                        )
                        
                        # Extract and parse MCP result
                        result_text = None
                        if hasattr(result, 'content') and result.content:
                            result_text = result.content[0].text if hasattr(result.content[0], 'text') else str(result.content[0])
                        elif isinstance(result, str):
                            result_text = result
                        
                        if result_text:
                            try:
                                # Parse JSON response
                                parsed_result = json.loads(result_text)
                                if parsed_result.get('success'):
                                    docstring = parsed_result.get('docstring', '')
                                    if docstring:
                                        logger.info(f"✅ Got schema for {function_name} from {server}")
                                        break
                                else:
                                    logger.warning(f"⚠️ MCP call failed for {function_name}: {parsed_result.get('error', 'Unknown error')}")
                            except json.JSONDecodeError:
                                # If not JSON, treat as plain text docstring
                                docstring = result_text
                                logger.info(f"✅ Got schema for {function_name} from {server} (plain text)")
                                break
                            
                    except Exception as e:
                        logger.warning(f"⚠️ Error calling {tool_name}: {e}")
                        continue
                
                if docstring:
                    schemas[function_name] = docstring
                    logger.info(f"📖 Fetched schema for {function_name}")
                else:
                    logger.warning(f"⚠️ No schema found for {function_name}")
                    schemas[function_name] = f"Function: {function_name} (schema not available)"
                    
            except Exception as e:
                logger.error(f"❌ Error fetching schema for {function_name}: {e}")
                schemas[function_name] = f"Function: {function_name} (error fetching schema)"
        
        return schemas
    
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
            workflow_steps=function_selection.get('workflow_steps', 'Use selected functions to analyze the query'),
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
            
            logger.info(f"📝 Saved debug prompt to {filename}")
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to save debug prompt: {e}")
            # Don't fail the main operation if debug saving fails

# Factory function for easy initialization
def create_code_prompt_builder() -> CodePromptBuilderService:
    """Create and return a CodePromptBuilderService instance"""
    return CodePromptBuilderService()