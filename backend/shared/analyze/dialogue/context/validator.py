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
        Validate if query has essential information using both heuristic and LLM approaches
        
        Args:
            query: The query text
            query_type: Optional query type for contextual validation
            use_llm: Whether to use LLM validation (fallback to heuristic if False or unavailable)
            
        Returns:
            {
                "valid": True/False,
                "complete": True/False,
                "missing": [],  # List of missing essential info
                "reason": "explanation",
                "validation_method": "llm" | "heuristic"
            }
        """
        try:
            query_lower = query.lower().strip()
            
            if not query:
                return {
                    "valid": False,
                    "complete": False,
                    "missing": ["query is empty"],
                    "reason": "Empty query",
                    "validation_method": "basic"
                }
            
            # Try LLM validation first if available and requested
            if use_llm and self.llm_service:
                try:
                    llm_result = await self._validate_with_llm(query)
                    if llm_result:
                        llm_result["validation_method"] = "llm"
                        return llm_result
                except Exception as e:
                    logger.warning(f"LLM validation failed, falling back to heuristic: {e}")
            
            # Fallback to heuristic validation
            return await self._validate_heuristic(query_lower)
            
        except Exception as e:
            logger.error(f"Validation error: {e}")
            return {
                "valid": False,
                "complete": False,
                "missing": ["validation error"],
                "reason": f"Validation error: {str(e)}",
                "validation_method": "error"
            }
    
    async def _validate_with_llm(self, query: str) -> Optional[Dict[str, Any]]:
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
            response = await self.llm_service.chat_completion([
                {"role": "user", "content": validation_prompt}
            ], max_tokens=200)
            
            if response.success and response.content:
                import json
                # Try to parse JSON response
                try:
                    result = json.loads(response.content.strip())
                    
                    # Validate the response structure
                    if "complete" in result and "missing" in result and "reason" in result:
                        return {
                            "valid": True,
                            "complete": result["complete"],
                            "missing": result["missing"],
                            "reason": result["reason"]
                        }
                    else:
                        logger.warning(f"LLM response missing required fields: {result}")
                        
                except json.JSONDecodeError as e:
                    logger.warning(f"Failed to parse LLM response as JSON: {response.content}")
            else:
                logger.warning(f"LLM validation failed: {response.error}")
                
        except Exception as e:
            logger.error(f"LLM validation error: {e}")
        
        return None
    
    async def _validate_heuristic(self, query_lower: str) -> Dict[str, Any]:
        """Heuristic validation using keyword matching"""
        
        # Check for essential components
        has_assets = self._has_assets(query_lower)
        has_analysis = self._has_analysis_type(query_lower)
        
        missing = []
        if not has_assets:
            missing.append("security or portfolio")
        if not has_analysis:
            missing.append("what analysis you want")
        
        is_complete = len(missing) == 0
        
        return {
            "valid": True,
            "complete": is_complete,
            "missing": missing,
            "reason": "Query is complete" if is_complete else f"Please specify: {' and '.join(missing)}",
            "validation_method": "heuristic"
        }
    
    def _has_assets(self, query_lower: str) -> bool:
        """Check if query mentions any assets"""
        # Common assets/keywords
        asset_keywords = [
            # Stocks
            "aapl", "msft", "tsla", "googl", "meta", "nvda", "amzn", "spy", "qqq", "voo", "vti",
            # Generic mentions
            "stock", "stocks", "etf", "etfs", "bond", "bonds", "crypto", "bitcoin", "ethereum",
            "portfolio", "portfolios", "asset", "assets", "securities", "investment", "investments",
            # Symbols and patterns
            "sp500", "nasdaq", "dow", "$", "usd"
        ]
        
        return any(keyword in query_lower for keyword in asset_keywords)
    
    def _has_analysis_type(self, query_lower: str) -> bool:
        """Check if query mentions what analysis to perform"""
        all_keywords = []
        for keywords in self.analysis_keywords.values():
            all_keywords.extend(keywords)
        
        return any(keyword in query_lower for keyword in all_keywords)
