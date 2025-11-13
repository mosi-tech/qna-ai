#\!/usr/bin/env python3
"""
Query Completeness Validator - Validates if query has essential information
Separate from classification - only checks if query is answerable
"""

import logging
from typing import Dict, Any, List, Optional
from ..conversation.store import QueryType
from shared.services.base_service import BaseService
from shared.llm import LLMService

logger = logging.getLogger(__name__)

class CompletenessValidator:
    """Validates if a query has essential information to be answered"""
    
    def __init__(self, llm_service: Optional[LLMService] = None):
        self.llm_service = llm_service
        
        # Essential keywords for different analysis types (for heuristic fallback)
        self.analysis_keywords = {
            "correlation": ["correlation", "correlated", "correlation coefficient"],
            "volatility": ["volatility", "vol", "standard deviation", "variance"],
            "returns": ["return", "returns", "performance", "gain", "loss"],
            "strategy": ["strategy", "backtest", "backtest", "trade", "buy", "sell"],
            "rebalance": ["rebalance", "rebalancing", "allocation"],
            "price": ["price", "prices", "pricing"],
            "momentum": ["momentum", "trend", "trending"],
            "dividend": ["dividend", "dividends", "yield"],
        }
    
    async def validate(self, query: str, query_type: QueryType = None, use_llm: bool = True) -> Dict[str, Any]:
        """
        CRITICAL: Validate if query has essential information using both heuristic and LLM approaches
        
        This function must be reliable in execution but STRICT in validation.
        If validation determines the query is incomplete, it fails hard with no fallbacks.
        
        Args:
            query: The query text
            query_type: Optional query type for contextual validation
            use_llm: Whether to use LLM validation (fallback to heuristic if False or unavailable)
            
        Returns:
            {
                "success": True/False,
                "complete": True/False,
                "missing": [],  # List of missing essential info
                "reason": "explanation",
                "validation_method": "llm" | "heuristic" | "basic"
            }
        """
        
        # Basic validation - empty query FAILS HARD
        if not query:
            return {
                "success": False,
                "complete": False,
                "missing": ["query is empty"],
                "reason": "Empty query provided",
                "validation_method": "basic"
            }
        
        return await self._validate_with_llm(query)

    async def _validate_with_llm(self, query: str) -> Optional[Dict[str, Any]]:
        """Single LLM validation attempt"""
        """Use LLM to validate query completeness"""
        
        validation_prompt = f"""You are a financial analysis validator. Your job is to determine if a user's question contains enough information to perform a meaningful financial analysis.

Analyze this question: "{query}"

A complete financial analysis question should specify:
1. What securities/assets to analyze (specific stocks, ETFs, portfolios, etc.)
2. What type of analysis to perform (correlation, volatility, returns, comparison, etc.)

Examples of INCOMPLETE questions:
- "Can you run ETF analysis" (missing: which ETF?)
- "Analyze correlation" (missing: between what assets?)
- "Show me volatility" (missing: of what security?)

Examples of COMPLETE questions:
- "Analyze AAPL vs MSFT correlation over the past 30 days"
- "What's the volatility of SPY ETF?"
- "Compare returns between Tesla and Apple stock"

Respond ONLY with a JSON object:
{{
    "complete": true/false,
    "missing": ["list", "of", "missing", "elements"],
    "reason": "Brief explanation of what's missing or why it's complete"
}}"""

        try:
            response = await self.llm_service.simple_completion(
                prompt=validation_prompt,
                max_tokens=1000
            )
            
            # Handle both dict and object response formats
            if isinstance(response, dict):
                success = response.get("success", False)
                content = response.get("content", "")
                error_msg = response.get("error", "Unknown error")
            else:
                success = getattr(response, "success", False)
                content = getattr(response, "content", "")
                error_msg = getattr(response, "error", "Unknown error")
            
            if success and content:
                import json
                # Try to parse JSON response
                try:
                    result = json.loads(content.strip())
                    
                    # Validate the response structure
                    if "complete" in result and "missing" in result and "reason" in result:
                        return {
                            "success": True,
                            "complete": result["complete"],
                            "missing": result["missing"],
                            "reason": result["reason"]
                        }
                    else:
                        logger.warning(f"LLM response missing required fields: {result}")
                        
                except json.JSONDecodeError as e:
                    logger.warning(f"Failed to parse LLM response as JSON: {content}")
            else:
                logger.warning(f"LLM validation failed: {error_msg}")
                
        except Exception as e:
            logger.error(f"LLM validation error: {e}")
        
        return {
            "success": False,
            "complete": False,
            "missing": ["validation failed"],
            "reason": "LLM validation unavailable",
            "validation_method": "error"
        }
    