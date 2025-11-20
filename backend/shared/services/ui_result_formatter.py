"""
UI Result Formatter

Generates UI configurations from analysis results using LLM with UI MCP server tools.
The LLM intelligently selects and configures React components based on data structure,
analysis type, and user question context.
"""

import json
import logging
from typing import Dict, Any, Optional, List

from .base_service import BaseService
from ..llm import LLMService, create_ui_formatter_llm
# MCP tools are auto-loaded by the LLM service

logger = logging.getLogger("shared-ui-result-formatter")


class UIResultFormatter(BaseService):
    """
    UI Result Formatter that uses MCP tools and LLM to generate dynamic UI configurations
    for React component rendering based on analysis results.
    """
    
    def __init__(self, llm_service: Optional[LLMService] = None):
        """
        Initialize UI formatter using BaseService pattern
        
        Args:
            llm_service: Optional LLM service instance. If None, will create default.
        """
        super().__init__(llm_service=llm_service, service_name="ui-result-formatter")
    
    def _create_default_llm(self) -> LLMService:
        """Create default LLM service for UI result formatting"""
        return create_ui_formatter_llm()
    
    def _get_system_prompt_filename(self) -> str:
        """Override to use UI-specific prompt file"""
        return "system-prompt-ui-formatter.txt"
    
    async def format_execution_result_to_ui(
        self, 
        execution_result: Dict[str, Any], 
        user_question: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Format complete execution result into UI configuration
        
        Args:
            execution_result: Complete execution result from database
            user_question: Optional original user question for context
            
        Returns:
            UI configuration dict with analysis_data and ui_config or None if formatting fails
        """
        try:
            # Extract the actual results from execution_result
            results = execution_result.get("results", {})
            
            if not results:
                logger.warning("No results found in execution_result")
                return None
            
            return await self.generate_ui_configuration(results, user_question)
            
        except Exception as e:
            logger.error(f"❌ Error formatting execution result to UI: {e}")
            return None
    
    async def generate_ui_configuration(
        self, 
        analysis_results: Dict[str, Any], 
        user_question: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Generate complete UI configuration using LLM with MCP tools
        
        Args:
            analysis_results: Dictionary containing analysis results
            user_question: Optional original user question for context
            
        Returns:
            Complete UI configuration dict or None if generation fails
        """
        try:
            if not analysis_results:
                self.logger.warning("No analysis results provided for UI generation")
                return None
            
            await self.llm_service.ensure_tools_loaded()
            
            # Get system prompt (MCP tools auto-loaded)
            system_prompt = await self.get_system_prompt()
            
            # Prepare user message with analysis results and context
            user_message = await self._prepare_ui_generation_request(
                analysis_results, user_question
            )
            
            self.logger.info(f"🤖 Generating UI config using {self.llm_service.provider_type}")
            
            # Generate UI configuration using LLM with MCP tools
            ui_config = await self._generate_ui_with_llm(system_prompt, user_message)
            
            if not ui_config:
                raise Exception("UI generation failed - no configuration returned")
            
            # Return complete response structure
            return {
                "analysis_data": analysis_results,
                "ui_config": ui_config,
                "metadata": {
                    "question": user_question,
                    "generated_at": self._get_current_timestamp(),
                    "formatter_version": "1.0.0"
                }
            }
                
        except Exception as e:
            self.logger.error(f"❌ Error generating UI configuration: {e}")
            raise
    
    
    async def _prepare_ui_generation_request(
        self, 
        analysis_results: Dict[str, Any], 
        user_question: Optional[str] = None
    ) -> str:
        """
        Prepare the user message for LLM UI generation request
        
        Args:
            analysis_results: Analysis results to create UI for
            user_question: Optional original user question for context
            
        Returns:
            Formatted user message string
        """
        # Convert results to readable JSON string
        results_json = json.dumps(analysis_results, indent=2, default=str)
        
        # Build context message
        context_parts = []
        
        # Add user question context if available
        if user_question:
            context_parts.append(f"USER QUESTION: {user_question}")
            context_parts.append("")
        
        
        context_parts.append("ANALYSIS RESULTS DATA STRUCTURE:")
        context_parts.append("```json")
        context_parts.append(results_json)
        context_parts.append("```")
        context_parts.append("")
        
        context_parts.append("")
        context_parts.append("TASK: Generate UI configuration JSON that optimally displays this data to answer the user's question.")
        
        return "\n".join(context_parts)
    
    async def _generate_ui_with_llm(
        self, 
        system_prompt: str, 
        user_message: str
    ) -> Optional[Dict[str, Any]]:
        """
        Generate UI configuration using LLM with MCP tools available
        """
        try:
            # Build multi-message conversation for clarity
            conversation_messages = self._build_multi_message_conversation(user_message)
            
            # Make LLM request with multi-message conversation
            response = await self.llm_service.make_request(
                messages=conversation_messages,
                system_prompt=system_prompt,
                max_tokens=2000,
                temperature=0.1
            )
            
            if response and response.get("success"):
                content = response.get("content", "").strip()
                
                # Extract JSON from response
                ui_config = self._extract_json_from_content(content)
                
                if ui_config and self._validate_ui_config(ui_config):
                    self.logger.info("✅ Successfully generated UI config with multi-message approach")
                    return ui_config
                else:
                    self.logger.warning("Generated UI config failed validation")
                    return None
            else:
                self.logger.error("LLM request failed")
                return None
                
        except Exception as e:
            self.logger.error(f"❌ Error in UI generation: {e}")
            return None
    
    def _validate_ui_config(self, ui_config: Dict[str, Any]) -> bool:
        """Validate the generated UI configuration structure"""
        try:
            # Check required top-level fields
            if "selected_components" not in ui_config:
                self.logger.warning("UI config missing 'selected_components'")
                return False
            
            selected_components = ui_config["selected_components"]
            if not isinstance(selected_components, list) or len(selected_components) == 0:
                self.logger.warning("UI config 'selected_components' must be non-empty list")
                return False
            
            # Validate each component
            for i, comp in enumerate(selected_components):
                if not isinstance(comp, dict):
                    self.logger.warning(f"Component {i} must be a dict")
                    return False
                
                required_fields = ["component_name", "role", "props", "layout"]
                for field in required_fields:
                    if field not in comp:
                        self.logger.warning(f"Component {i} missing required field: {field}")
                        return False
                
                # Validate role
                if comp["role"] not in ["primary", "supporting", "summary"]:
                    self.logger.warning(f"Component {i} has invalid role: {comp['role']}")
                    return False
                
                # Validate layout
                layout = comp["layout"]
                if not isinstance(layout, dict) or "size" not in layout:
                    self.logger.warning(f"Component {i} has invalid layout structure")
                    return False
                
                if layout["size"] not in ["third", "half", "full"]:
                    self.logger.warning(f"Component {i} has invalid layout size: {layout['size']}")
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating UI config: {e}")
            return False
    

    def _get_current_timestamp(self) -> str:
        """Get current timestamp in ISO format"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def _build_multi_message_conversation(self, user_message: str) -> List[Dict[str, str]]:
        """Build multi-message conversation with component schemas and analysis data separated"""
        
        # Component registry copied from react_components_server.py
        COMPONENT_REGISTRY = {
            "BarChart": {
                "id": "BarChart",
                "category": "charts",
                "description": "Clean bar chart for comparing values across categories",
                "use_cases": ["Rankings", "category comparisons", "performance metrics", "distribution analysis"],
                "data_format": "Array of objects with label and value properties",
                "props_schema": {
                    "type": "object",
                    "properties": {
                        "data": {"type": "array", "items": {"type": "object", "properties": {"label": {"type": "string"}, "value": {"type": "number"}}, "required": ["label", "value"]}},
                        "title": {"type": "string", "optional": True},
                        "format": {"type": "string", "enum": ["number", "percentage", "currency"], "default": "number"},
                        "color": {"type": "string", "enum": ["blue", "green", "purple", "orange"], "default": "blue"}
                    },
                    "required": ["data"]
                },
                "layout_hints": ["third", "half", "full"],
                "best_for_data_types": ["numerical", "categorical", "rankings", "comparisons"]
            },
            "PieChart": {
                "id": "PieChart",
                "category": "charts", 
                "description": "Clean pie/donut chart for showing proportional data and distributions",
                "use_cases": ["Portfolio allocations", "category distributions", "market share", "composition analysis"],
                "props_schema": {
                    "type": "object",
                    "properties": {
                        "data": {"type": "array", "items": {"type": "object", "properties": {"label": {"type": "string"}, "value": {"type": "number"}}, "required": ["label", "value"]}},
                        "title": {"type": "string", "optional": True},
                        "showLegend": {"type": "boolean", "default": True},
                        "showPercentages": {"type": "boolean", "default": True}
                    },
                    "required": ["data"]
                },
                "layout_hints": ["half", "full"],
                "best_for_data_types": ["proportional", "categorical", "distributions", "allocations"]
            },
            "LineChart": {
                "id": "LineChart",
                "category": "charts",
                "description": "Clean line chart for time series data and trend visualization",
                "use_cases": ["Performance over time", "historical analysis", "trend tracking", "growth curves"],
                "props_schema": {
                    "type": "object",
                    "properties": {
                        "data": {"type": "array", "items": {"type": "object", "properties": {"label": {"type": "string"}, "value": {"type": "number"}}, "required": ["label", "value"]}},
                        "title": {"type": "string", "optional": True},
                        "format": {"type": "string", "enum": ["number", "percentage", "currency"], "default": "number"}
                    },
                    "required": ["data"]
                },
                "layout_hints": ["half", "full"],
                "best_for_data_types": ["time_series", "trends", "historical", "sequential"]
            },
            "RankingTable": {
                "id": "RankingTable",
                "category": "tables",
                "description": "Advanced ranking table with sorting, formatting, and performance indicators",
                "use_cases": ["Performance rankings", "leaderboards", "comparisons", "sorted data display"],
                "props_schema": {
                    "type": "object",
                    "properties": {
                        "data": {"type": "array", "items": {"type": "object"}},
                        "title": {"type": "string", "optional": True},
                        "columns": {"type": "array", "items": {"type": "object", "properties": {"id": {"type": "string"}, "name": {"type": "string"}, "format": {"type": "string", "enum": ["text", "number", "percentage", "currency"], "default": "text"}}, "required": ["id", "name"]}}
                    },
                    "required": ["data", "columns"]
                },
                "layout_hints": ["half", "full"],
                "best_for_data_types": ["rankings", "tabular", "comparisons", "multi_column"]
            },
            "StatGroup": {
                "id": "StatGroup",
                "category": "cards",
                "description": "Group of key statistics with optional change indicators",
                "use_cases": ["KPI display", "summary metrics", "dashboard stats", "key numbers"],
                "props_schema": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string", "optional": True},
                        "stats": {"type": "array", "items": {"type": "object", "properties": {"label": {"type": "string"}, "value": {"type": "string"}, "format": {"type": "string", "enum": ["number", "percentage", "currency"], "default": "number"}}, "required": ["label", "value"]}}
                    },
                    "required": ["stats"]
                },
                "layout_hints": ["third", "half", "full"],
                "best_for_data_types": ["statistics", "kpis", "metrics", "numerical"]
            },
            "ExecutiveSummary": {
                "id": "ExecutiveSummary",
                "category": "lists",
                "description": "High-level executive summary with key findings and color-coded insights",
                "use_cases": ["Key findings", "executive overview", "main insights", "summary points"],
                "props_schema": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string", "optional": True},
                        "items": {"type": "array", "items": {"type": "object", "properties": {"label": {"type": "string"}, "text": {"type": "string"}, "color": {"type": "string", "enum": ["default", "blue", "green", "orange", "red"], "default": "default"}}, "required": ["label", "text"]}}
                    },
                    "required": ["items"]
                },
                "layout_hints": ["half", "full"],
                "best_for_data_types": ["summary", "insights", "findings", "textual"]
            },
            "SummaryConclusion": {
                "id": "SummaryConclusion",
                "category": "text",
                "description": "Comprehensive conclusion with findings, analysis, and next steps",
                "use_cases": ["Final analysis", "conclusions", "recommendations", "comprehensive summaries"],
                "props_schema": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string", "optional": True},
                        "keyFindings": {"type": "array", "items": {"type": "string"}},
                        "conclusion": {"type": "string"},
                        "nextSteps": {"type": "array", "items": {"type": "string"}, "optional": True}
                    },
                    "required": ["keyFindings", "conclusion"]
                },
                "layout_hints": ["half", "full"],
                "best_for_data_types": ["conclusion", "summary", "recommendations", "textual"]
            }
        }
        
        # Build component schemas message
        components_message_parts = []
        components_message_parts.append("I have these React components available for building UI dashboards:")
        components_message_parts.append("")
        
        for comp_id, comp_data in COMPONENT_REGISTRY.items():
            components_message_parts.append(f"**{comp_id}** ({comp_data['category']})")
            components_message_parts.append(f"- {comp_data['description']}")
            components_message_parts.append(f"- Use cases: {', '.join(comp_data['use_cases'])}")
            components_message_parts.append(f"- Best for: {', '.join(comp_data['best_for_data_types'])}")
            components_message_parts.append(f"- Layout options: {', '.join(comp_data['layout_hints'])}")
            components_message_parts.append(f"- Props schema: {json.dumps(comp_data['props_schema'], indent=2)}")
            components_message_parts.append("")
        
        # Build conversation messages
        messages = [
            {
                "role": "assistant",
                "content": "\n".join(components_message_parts)
            },
            {
                "role": "user", 
                "content": user_message  # This should contain the analysis data
            },
            {
                "role": "user",
                "content": "Based on the components I showed you and the analysis data above, please select 2-4 components to build a comprehensive dashboard. Generate the complete UI configuration in the required JSON format.\n\n🚨 CRITICAL REQUIREMENTS:\n- START with a summary component (StatGroup, ExecutiveSummary) as the FIRST element\n- LAYOUT: Design for no-scroll viewing - maximum 2-3 rows total\n- SIZES: Use third/short for summary, half/medium for charts, avoid multiple full-width components\n- ONLY use titles that accurately reflect the actual data provided\n- NEVER create or assume data that doesn't exist in the analysis\n- NEVER use comparative language (vs, comparison) when only single data points exist\n- VERIFY every data reference path exists in the analysis results\n- Use exact terminology from the analysis data for all labels\n\nPLAN YOUR LAYOUT: Row 1 (summary + chart), Row 2 (main data), avoid scrolling!"
            }
        ]
        
        return messages
    
    def _extract_json_from_content(self, content: str) -> Optional[Dict[str, Any]]:
        """Extract JSON from LLM response content"""
        try:
            # Remove markdown code blocks if present
            if "```json" in content:
                start = content.find("```json") + 7
                end = content.find("```", start)
                if end != -1:
                    content = content[start:end].strip()
            elif "```" in content:
                start = content.find("```") + 3
                end = content.find("```", start)
                if end != -1:
                    content = content[start:end].strip()
            
            return json.loads(content)
        except json.JSONDecodeError:
            return None
    


# Factory function for easy initialization
def create_ui_result_formatter(llm_service=None) -> UIResultFormatter:
    """Create and return a UIResultFormatter instance"""
    logger.info("Initializing the UI result formatter service")
    return UIResultFormatter(llm_service=llm_service)