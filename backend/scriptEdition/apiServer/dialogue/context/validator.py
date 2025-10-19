#\!/usr/bin/env python3
"""
Query Completeness Validator - Validates if query has essential information
Separate from classification - only checks if query is answerable
"""

import logging
from typing import Dict, Any, List
from ..conversation.store import QueryType

logger = logging.getLogger(__name__)

class CompletenessValidator:
    """Validates if a query has essential information to be answered"""
    
    def __init__(self):
        # Essential keywords for different analysis types
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
    
    def validate(self, query: str, query_type: QueryType = None) -> Dict[str, Any]:
        """
        Validate if query has essential information
        
        Args:
            query: The query text
            query_type: Optional query type for contextual validation
            
        Returns:
            {
                "valid": True/False,
                "complete": True/False,
                "missing": [],  # List of missing essential info
                "reason": "explanation"
            }
        """
        try:
            query_lower = query.lower().strip()
            
            if not query:
                return {
                    "valid": False,
                    "complete": False,
                    "missing": ["query is empty"],
                    "reason": "Empty query"
                }
            
            # Check for essential components
            has_assets = self._has_assets(query_lower)
            has_analysis = self._has_analysis_type(query_lower)
            
            missing = []
            if not has_assets:
                missing.append("assets/securities (e.g., AAPL, SPY, portfolio)")
            if not has_analysis:
                missing.append("analysis type (e.g., correlation, returns, volatility)")
            
            is_complete = len(missing) == 0
            
            return {
                "valid": True,
                "complete": is_complete,
                "missing": missing,
                "reason": "Query is complete" if is_complete else f"Missing: {', '.join(missing)}"
            }
            
        except Exception as e:
            logger.error(f"Validation error: {e}")
            return {
                "valid": False,
                "complete": False,
                "missing": ["validation error"],
                "reason": f"Validation error: {str(e)}"
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
