#!/usr/bin/env python3
"""
Reuse Evaluator Service

Analyzes financial questions against existing analyses to determine if existing scripts
can be reused with different parameters instead of creating new ones.
"""

import json
import logging
import os
from datetime import datetime
from typing import Dict, Any, Optional, List

from llm import create_reuse_evaluator_llm, LLMService
from .base_service import BaseService

class ReuseEvaluatorService(BaseService):
    """Service that evaluates whether existing analyses can be reused for new queries"""
    
    def __init__(self, llm_service: Optional[LLMService] = None):
        super().__init__(llm_service=llm_service, service_name="reuse-evaluator")
    
    def _create_default_llm(self) -> LLMService:
        """Create default LLM service for reuse evaluator"""
        return create_reuse_evaluator_llm()
    
    def _get_system_prompt_filename(self) -> str:
        """Use reuse evaluator specific system prompt"""
        return "system-prompt-reuse-evaluator.txt"
    
    def _get_default_system_prompt(self) -> str:
        """Default system prompt for reuse evaluator"""
        return "You are a financial analysis reuse evaluator."
    
    async def evaluate_reuse(self, user_query: str, existing_analyses: List[Dict], context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Evaluate if existing analyses can be reused for the user query
        
        Args:
            user_query: User's financial question
            existing_analyses: List of existing analysis metadata
            context: Optional context information
            
        Returns:
            Dict containing reuse decision and reasoning
        """
        try:
            logger.info(f"🔍 Evaluating reuse for query: {user_query[:100]}...")
            
            # Build evaluation prompt with existing analyses
            evaluation_prompt = self._build_evaluation_prompt(user_query, existing_analyses, context)
            
            # Get reuse decision from LLM
            response = await self.llm_service.make_request(
                messages=[{
                    "role": "user", 
                    "content": evaluation_prompt
                }],
                system_prompt=self.system_prompt
            )
            
            # Check if LLM request was successful
            if not response.get("success"):
                logger.error(f"❌ LLM request failed: {response.get('error')}")
                return {
                    "status": "error",
                    "reuse_decision": {
                        "should_reuse": False,
                        "reason": f"LLM request failed: {response.get('error')}"
                    },
                    "error": response.get('error'),
                    "timestamp": datetime.now().isoformat()
                }
            
            # Parse JSON response
            try:
                reuse_decision = json.loads(response["content"])
                logger.info(f"📋 Reuse decision: {reuse_decision['reuse_decision']['should_reuse']}")
                
                result = {
                    "status": "success",
                    "reuse_decision": reuse_decision["reuse_decision"],
                    "timestamp": datetime.now().isoformat()
                }
                
                return result
                
            except json.JSONDecodeError as e:
                logger.error(f"❌ Failed to parse reuse decision JSON: {e}")
                logger.error(f"Raw response: {response['content']}")
                
                # Fallback to no reuse if parsing fails
                return {
                    "status": "success",
                    "reuse_decision": {
                        "should_reuse": False,
                        "reason": "Failed to parse reuse evaluation response"
                    },
                    "timestamp": datetime.now().isoformat()
                }
            
        except Exception as e:
            logger.error(f"❌ Error evaluating reuse: {e}")
            
            # Fallback to no reuse on error
            return {
                "status": "error",
                "reuse_decision": {
                    "should_reuse": False,
                    "reason": f"Error during reuse evaluation: {str(e)}"
                },
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _build_evaluation_prompt(self, user_query: str, existing_analyses: List[Dict], context: Optional[Dict] = None) -> str:
        """Build evaluation prompt with user query and existing analyses"""
        
        # Format existing analyses section
        if existing_analyses:
            analyses_section = "📋 RELEVANT EXISTING ANALYSES:\n\n"
            for i, analysis in enumerate(existing_analyses, 1):
                analyses_section += f"{i}. **{analysis.get('name', 'Unknown Analysis')}**\n"
                analyses_section += f"   - Script: {analysis.get('script_name', 'N/A')}\n"
                analyses_section += f"   - Question: {analysis.get('question', 'N/A')}\n"
                analyses_section += f"   - Description: {analysis.get('description', 'N/A')}\n"
                if analysis.get('apis'):
                    analyses_section += f"   - APIs: {', '.join(analysis['apis'])}\n"
                analyses_section += "\n"
        else:
            analyses_section = "📋 RELEVANT EXISTING ANALYSES: None provided\n\n"
        
        # Build context section
        context_section = ""
        if context:
            context_section = f"CONTEXT: {json.dumps(context, indent=2)}\n\n"
        
        # Build evaluation prompt
        evaluation_prompt = f"""USER QUERY: {user_query}

{context_section}{analyses_section}TASK: Evaluate if any of the existing analyses can be reused for this user query.

Consider:
1. Is the core financial methodology the same?
2. Are only parameters different (symbols, timeframes, thresholds)?
3. Is the expected output format similar?
4. Does the analysis approach match what's needed?

Return your decision in the exact JSON format specified in the system prompt."""
        
        return evaluation_prompt

# Factory function for easy initialization
def create_reuse_evaluator() -> ReuseEvaluatorService:
    """Create and return a ReuseEvaluatorService instance"""
    return ReuseEvaluatorService()