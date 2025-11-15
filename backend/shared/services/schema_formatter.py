"""
Shared Schema Formatter
Generates parameter schemas from analysis function signatures using LLM and BaseService pattern
"""

import logging
from typing import Dict, Any, Optional, List

from .base_service import BaseService
from ..llm import LLMService, create_analysis_llm
from ..storage import get_storage
from ..utils.json_utils import safe_json_loads

logger = logging.getLogger("shared-schema-formatter")


class SharedSchemaFormatter(BaseService):
    """Standalone schema formatter for generating parameter forms from function signatures"""
    
    def __init__(self, llm_service: Optional[LLMService] = None):
        """
        Initialize schema formatter using BaseService pattern
        
        Args:
            llm_service: Optional LLM service instance. If None, will create default.
        """
        super().__init__(llm_service=llm_service, service_name="schema-formatter")
    
    def _create_default_llm(self) -> LLMService:
        """Create default LLM service for schema generation"""
        return create_analysis_llm()
    
    def _get_system_prompt_filename(self) -> str:
        """Override to use schema-formatter specific prompt file"""
        return "system-prompt-schema-formatter.txt"
        
    async def generate_parameter_schema(
        self, 
        script_name: str,
        analysis_type: Optional[str] = None
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Generate parameter schema by reading script content and analyzing with LLM
        
        Args:
            script_name: Name of the analysis script (e.g., "stock_analysis.py")
            analysis_type: Optional type of analysis for better schema generation
            
        Returns:
            List of parameter schema objects or None if generation fails
        """
        try:
            logger.info(f"🤖 Generating parameter schema by reading script: {script_name}")
            
            # Read script content from storage
            storage = get_storage()
            script_content = await storage.read_script(script_name)
            
            if not script_content:
                logger.warning(f"Could not read script content for: {script_name}")
                return None
            
            # Get system prompt
            system_prompt = await self.get_system_prompt()
            
            # Prepare user message with script content
            user_message = self._prepare_script_content_request(script_name, script_content, analysis_type)
            
            # Generate schema using LLM
            response = await self.llm_service.make_request(
                messages=[{
                    "role": "user",
                    "content": user_message
                }],
                system_prompt=system_prompt,
                max_tokens=3000,
                temperature=0.2  # Low temperature for consistent structure
            )
            
            if response and response.get("success"):
                schema_content = response.get("content", "").strip()
                
                if schema_content:
                    # Parse the LLM response as JSON using safe_json_loads
                    parameter_schema = safe_json_loads(schema_content)
                    if parameter_schema is not None and isinstance(parameter_schema, list):
                        logger.info("✅ Successfully generated parameter schema from script content")
                        return parameter_schema
                    else:
                        logger.warning("LLM returned non-array schema format or invalid JSON")
                        return None
                else:
                    logger.warning("LLM returned empty parameter schema")
                    return None
            else:
                error_msg = response.get("error", "Unknown LLM error") if response else "No response from LLM"
                logger.warning(f"❌ LLM schema generation failed: {error_msg}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error generating schema from script: {e}")
            return None
    
    def _prepare_script_content_request(
        self,
        script_name: str,
        script_content: str,
        analysis_type: Optional[str] = None
    ) -> str:
        """Prepare the user message for script-content-based schema generation"""
        
        context_parts = []
        
        # Add script context
        context_parts.append(f"Script Name: {script_name}")
        if analysis_type:
            context_parts.append(f"Analysis Type: {analysis_type}")
        context_parts.append("")
        
        # Add script content (truncated if too long)
        context_parts.append("Script Content:")
        context_parts.append("```python")
        # Truncate if too long to avoid token limits
        if len(script_content) > 4000:
            context_parts.append(script_content[:4000] + "\n# ... (truncated)")
        else:
            context_parts.append(script_content)
        context_parts.append("```")
        context_parts.append("")
        
        # Add instructions
        context_parts.append("Based on the script content above, analyze the `analyze_question` function and generate a comprehensive parameter schema.")
        context_parts.append("")
        context_parts.append("Extract parameters from the function signature and create appropriate form fields including:")
        context_parts.append("1. Parameter names, types, and default values from the function")
        context_parts.append("2. User-friendly names and descriptions")
        context_parts.append("3. Appropriate form field types (text, number, select, multiselect, boolean)")
        context_parts.append("4. Validation rules based on parameter context")
        context_parts.append("5. Logical grouping (Basic/Advanced)")
        context_parts.append("6. Sensible default values and options for select fields")
        context_parts.append("")
        context_parts.append("Return only the JSON schema array with no explanation.")
        
        return "\n".join(context_parts)
    

# Factory function for easy initialization
def create_shared_schema_formatter(llm_service=None) -> SharedSchemaFormatter:
    """Create and return a SharedSchemaFormatter instance"""
    logger.info("Initializing the schema formatter service")
    return SharedSchemaFormatter(llm_service=llm_service)