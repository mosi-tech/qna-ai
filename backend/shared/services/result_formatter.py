"""
Shared Result Formatter
Generates formatted markdown from analysis results using LLM using shared BaseService
"""

import json
import logging
from typing import Dict, Any, Optional

from .base_service import BaseService
from ..llm import LLMService, create_result_formatter_llm

logger = logging.getLogger("shared-result-formatter")


class SharedResultFormatter(BaseService):
    """Standalone result formatter for use in both apiServer and queue worker"""
    
    def __init__(self, llm_service: Optional[LLMService] = None):
        """
        Initialize formatter using BaseService pattern
        
        Args:
            llm_service: Optional LLM service instance. If None, will create default.
        """
        super().__init__(llm_service=llm_service, service_name="result-formatter")
    
    def _create_default_llm(self) -> LLMService:
        """Create default LLM service for result formatting"""
        return create_result_formatter_llm()
    
    def _get_system_prompt_filename(self) -> str:
        """Override to use result-formatter specific prompt file"""
        return "system-prompt-result-formatter.txt"
        
    async def format_execution_result(
        self, 
        execution_result: Dict[str, Any], 
        user_question: Optional[str] = None
    ) -> Optional[str]:
        """
        Format complete execution result including nested results
        
        Args:
            execution_result: Complete execution result from database
            user_question: Optional original user question for context
            
        Returns:
            Formatted markdown or None if formatting fails
        """
        try:
            # Extract the actual results from execution_result
            results = execution_result.get("results", {})
            
            if not results:
                logger.warning("No results found in execution_result")
                return None
            
            # Try to extract analysis type from execution metadata
            response_type = execution_result.get("response_type") or "Financial Analysis"
            
            return await self.format_results_to_markdown(results, response_type, user_question)
            
        except Exception as e:
            logger.error(f"❌ Error formatting execution result: {e}")
            return None
    
    async def format_results_to_markdown(
        self, 
        results: Dict[str, Any], 
        response_type: Optional[str] = None,
        user_question: Optional[str] = None
    ) -> Optional[str]:
        """
        Generate formatted markdown from analysis results using LLM
        
        Args:
            results: Dictionary containing analysis results
            response_type: Optional type of analysis for context
            user_question: Optional original user question for context
            
        Returns:
            Formatted markdown string or None if generation fails
        """
        try:
            if not results:
                self.logger.warning("No results provided for formatting")
                return None
            
            # Get system prompt using BaseService method
            system_prompt = await self.get_system_prompt()
            
            # Prepare user message with results and question context
            user_message = self._prepare_formatting_request(results, response_type, user_question)
            
            self.logger.info(f"🤖 Formatting results using {self.llm_service.provider_type}")
            
            # Generate markdown using LLM
            response = await self.llm_service.make_request(
                messages=[{
                    "role": "user",
                    "content": user_message
                }],
                system_prompt=system_prompt,
                max_tokens=2000,
                temperature=0.3  # Lower temperature for consistent formatting
            )
            
            if response and response.get("success"):
                markdown_content = response.get("content", "").strip()
                
                if markdown_content:
                    self.logger.info("✅ Successfully generated markdown summary")
                    return markdown_content
                else:
                    self.logger.warning("LLM returned empty markdown content")
                    return self._generate_simple_markdown(results, response_type, user_question)
            else:
                error_msg = response.get("error", "Unknown LLM error") if response else "No response from LLM"
                self.logger.error(f"❌ LLM formatting failed: {error_msg}")
                return self._generate_simple_markdown(results, response_type, user_question)
                
        except Exception as e:
            self.logger.error(f"❌ Error generating markdown summary: {e}")
            return self._generate_simple_markdown(results, response_type, user_question)
    
    def _prepare_formatting_request(
        self, 
        results: Dict[str, Any], 
        response_type: Optional[str] = None,
        user_question: Optional[str] = None
    ) -> str:
        """
        Prepare the user message for LLM formatting request
        
        Args:
            results: Analysis results to format
            response_type: Optional analysis type for context
            user_question: Optional original user question for context
            
        Returns:
            Formatted user message string
        """
        # Convert results to readable JSON string
        results_json = json.dumps(results, indent=2, default=str)
        
        # Build context message
        context_parts = []
        
        # Add user question context if available
        if user_question:
            context_parts.append(f"Original Question: {user_question}")
            context_parts.append("")
        
        context_parts.append("Raw Results Data:")
        context_parts.append("```json")
        context_parts.append(results_json)
        context_parts.append("```")
        
        if user_question:
            context_parts.append(f"\nPlease format these analysis results into clear, readable markdown that directly answers the user's question: '{user_question}'. Highlight the key insights and present the data in an organized, investor-friendly format.")
        else:
            context_parts.append("\nPlease format these analysis results into clear, readable markdown that highlights the key insights and presents the data in an organized, investor-friendly format.")
        
        return "\n".join(context_parts)
    
    
    def _generate_simple_markdown(
        self, 
        results: Dict[str, Any], 
        response_type: Optional[str] = None,
        user_question: Optional[str] = None
    ) -> str:
        """Generate simple markdown fallback when LLM is not available"""
        markdown_lines = ["# Analysis Results", ""]
        
        # Add question context if available
        if user_question:
            markdown_lines.append(f"**Question**: {user_question}")
            markdown_lines.append("")
        
        # Add key metrics
        if results:
            markdown_lines.append("## Key Metrics")
            markdown_lines.append("")
            
            for key, value in results.items():
                # Format key to be more readable
                formatted_key = key.replace('_', ' ').title()
                markdown_lines.append(f"- **{formatted_key}**: {value}")
            
            markdown_lines.append("")
        
        # Add summary section
        markdown_lines.append("## Summary")
        markdown_lines.append("")
        if user_question:
            markdown_lines.append(f"Analysis completed successfully in response to: '{user_question}'. The above metrics provide the requested information.")
        else:
            markdown_lines.append("Analysis completed successfully with the above metrics.")
        
        return "\n".join(markdown_lines)


# Factory function for easy initialization
def create_shared_result_formatter(llm_service=None) -> SharedResultFormatter:
    """Create and return a SharedResultFormatter instance"""
    logger.info("Initializing the result formatter service")
    return SharedResultFormatter(llm_service=llm_service)