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
        """Validate query completeness and expand standalone queries with sensible defaults"""
        
        system_prompt = """You are a financial analysis validator and enhancer. Your job is to:
1. Determine if a user's question contains enough information for a meaningful financial analysis
2. If complete but terse/sparse, COMPREHENSIVELY enhance it with detailed financial context and multiple analysis dimensions

A complete financial analysis question should specify:
1. What securities/assets to analyze (specific stocks, ETFs, portfolios, etc.)
2. What type of analysis to perform (correlation, volatility, returns, comparison, etc.)

Examples of INCOMPLETE questions (missing core info):
- "Can you run ETF analysis" → missing: which ETF?
- "Analyze correlation" → missing: between what assets?
- "Show me volatility" → missing: of what security?

Examples of COMPLETE but TERSE questions (have core info but lack details):
- "Volatility of SPY" → complete, but NEEDS COMPREHENSIVE expansion
- "AAPL vs MSFT correlation" → complete, but NEEDS COMPREHENSIVE expansion
- "Portfolio return analysis" → complete, but NEEDS COMPREHENSIVE expansion

COMPREHENSIVE ENHANCEMENT RULES (expand terse queries substantially):

FOR TIME PERIOD:
- Always include TRIPLE period analysis for complete perspective:
  - SHORT-TERM: Past 1 year (252 trading days) for current trends and recent volatility
  - MEDIUM-TERM: Past 10 years for structural trends and multiple market cycles
  - OVERALL/HISTORICAL: Inception-to-date or maximum available history for complete story
- Add comparison periods: 3-month, YTD, quarterly comparisons where relevant
- When requesting metrics, specify all 3 periods for consistency (e.g., "volatility over 1-year, 10-year, and inception-to-date")

FOR METRICS (add key ones, not exhaustive list):
- RISK: volatility (annualized), max drawdown, Sharpe ratio
- RETURN: total return, annualized return, cumulative return
- CORRELATION: Pearson correlation with S&P 500 benchmark
- Optional: Add 1-2 additional metrics based on query context (e.g., beta if comparing assets, win rate if strategy-focused)

FOR ANALYSIS SCOPE:
- Add benchmark comparison (S&P 500 or relevant index)
- Include period-over-period comparison (current vs historical performance)
- Request trend analysis (momentum, volatility changes) where relevant

FOR CONTEXT:
- Specify analysis focus (risk analysis, return analysis, comparative, etc.)
- Request actionable insights (performance relative to baseline, trend direction)

ENHANCEMENT APPROACH:
- Start with the terse query
- Add time periods: 1-year (current) + 10-year (structural) + inception-to-date (historical full context)
- Add 2-3 key metric dimensions: risk + return + benchmark comparison (add 1 more if relevant to query)
- For each metric, request the 3 periods for consistency
- Include comparative analysis: current vs historical (trend, direction, context)
- Make expanded query 1.5-2x longer with clearer structure
- Keep it focused but comprehensive: enough for deep insight without overwhelming detail"""

        user_message = f"""Validate and enhance this question:

"{query}"

Respond ONLY with a JSON object:
{{
    "complete": true/false,
    "missing": ["list", "of", "missing", "core", "elements"],
    "is_terse": true/false,
    "enhanced_query": "expanded version of query with sensible defaults if terse, otherwise same as input",
    "enhancements_applied": ["list", "of", "enhancements"],
    "reason": "Brief explanation"
}}"""

        try:
            response = await self.llm_service.simple_completion(
                prompt=user_message,
                system_prompt=system_prompt,
                max_tokens=1500
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
                        # Extract enhanced query if provided and query was terse
                        enhanced_query = result.get("enhanced_query", None)
                        is_terse = result.get("is_terse", False)
                        enhancements = result.get("enhancements_applied", [])
                        
                        # Log enhancements for transparency
                        if enhanced_query and enhanced_query != query:
                            logger.info(f"✨ Query enhanced: '{query[:80]}...' → '{enhanced_query[:80]}...'")
                            if enhancements:
                                logger.info(f"   Enhancements: {', '.join(enhancements)}")
                        
                        return {
                            "success": True,
                            "complete": result["complete"],
                            "missing": result["missing"],
                            "reason": result["reason"],
                            "is_terse": is_terse,
                            "enhanced_query": enhanced_query if enhanced_query != query else None,
                            "enhancements_applied": enhancements
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
    