#!/usr/bin/env python3
"""
Query Classifier - Determine query type with minimal context
"""

import logging
from typing import Optional, Dict, Any
from ..conversation.store import QueryType, ConversationTurn
from .service import ContextService

logger = logging.getLogger(__name__)

class QueryClassifier:
    """Classify user queries efficiently using minimal context"""
    
    def __init__(self, context_service: ContextService):
        self.context_service = context_service
        self._fallback_patterns = {
            "contextual": [
                "what about", "how about", "try with", "same with", 
                "different assets", "switch to", "instead of"
            ],
            "comparative": [
                "compare", "vs", "versus", "difference", "better than",
                "how does that", "which is better"
            ],
            "parameter": [
                "what if", "try", "instead", "%", "percent", "threshold",
                "change", "different", "higher", "lower"
            ]
        }
    
    async def classify(self, user_query: str, last_turn: Optional[ConversationTurn] = None) -> Dict[str, Any]:
        """Classify query type using LLM with minimal context"""
        
        # First attempt: LLM classification
        llm_result = await self._classify_with_llm(user_query, last_turn)
        
        # Fallback: Pattern matching
        pattern_result = self._classify_with_patterns(user_query)
        
        # Combine results - prefer LLM if confident, otherwise use patterns
        if llm_result["success"] and llm_result["confidence"] > 0.7:
            result = llm_result.copy()
            result["fallback_used"] = False
            result["pattern_classification"] = pattern_result["query_type"]
        elif llm_result["success"]:
            result = llm_result.copy()
            result["fallback_used"] = False
            result["pattern_classification"] = pattern_result["query_type"]
        else:
            result = pattern_result.copy()
            result["fallback_used"] = True
            result["llm_error"] = llm_result.get("error", "Unknown LLM error")
        
        # Always convert string to QueryType enum
        try:
            result["query_type_enum"] = QueryType(result["query_type"])
        except ValueError:
            result["query_type_enum"] = QueryType.COMPLETE
            result["query_type"] = "complete"
        
        return result
    
    async def _classify_with_llm(self, user_query: str, last_turn: Optional[ConversationTurn]) -> Dict[str, Any]:
        """Use LLM for classification with minimal context"""
        
        last_query = last_turn.user_query if last_turn else None
        
        result = await self.context_service.classify_query(
            current_query=user_query,
            last_query=last_query
        )
        
        if result["success"]:
            logger.info(f"LLM classified '{user_query[:30]}...' as {result['query_type']}")
        else:
            logger.warning(f"LLM classification failed: {result.get('error')}")
        
        return result
    
    def _classify_with_patterns(self, user_query: str) -> Dict[str, Any]:
        """Fallback pattern-based classification"""
        
        query_lower = user_query.lower()
        
        # Check for contextual patterns
        for pattern in self._fallback_patterns["contextual"]:
            if pattern in query_lower:
                return {
                    "success": True,
                    "query_type": "contextual",
                    "confidence": 0.8,
                    "method": "pattern_matching",
                    "matched_pattern": pattern
                }
        
        # Check for comparative patterns  
        for pattern in self._fallback_patterns["comparative"]:
            if pattern in query_lower:
                return {
                    "success": True,
                    "query_type": "comparative", 
                    "confidence": 0.7,
                    "method": "pattern_matching",
                    "matched_pattern": pattern
                }
        
        # Check for parameter patterns
        for pattern in self._fallback_patterns["parameter"]:
            if pattern in query_lower:
                return {
                    "success": True,
                    "query_type": "parameter",
                    "confidence": 0.6,
                    "method": "pattern_matching", 
                    "matched_pattern": pattern
                }
        
        # Default to complete
        return {
            "success": True,
            "query_type": "complete",
            "confidence": 0.9,
            "method": "pattern_matching",
            "matched_pattern": "default"
        }
    
    def extract_assets_from_contextual_query(self, query: str) -> Dict[str, Any]:
        """Extract asset mentions from contextual queries"""
        
        # Common asset patterns
        asset_patterns = [
            # ETFs
            r'\b(SPY|QQQ|VOO|VTI|AAPL|MSFT|TSLA|AMZN|GOOGL|META|NVDA)\b',
            # Leveraged ETFs
            r'\b(TQQQ|SQQQ|UPRO|SPXU|TLT|TMF|UGL|GLD)\b',
            # Crypto
            r'\b(BTC|ETH|bitcoin|ethereum)\b'
        ]
        
        import re
        assets_found = []
        
        for pattern in asset_patterns:
            matches = re.findall(pattern, query.upper())
            assets_found.extend(matches)
        
        # Remove duplicates while preserving order
        unique_assets = list(dict.fromkeys(assets_found))
        
        # Try to identify FROM and TO assets
        from_asset = unique_assets[0] if len(unique_assets) > 0 else None
        to_asset = unique_assets[1] if len(unique_assets) > 1 else None
        
        return {
            "assets_found": unique_assets,
            "from_asset": from_asset,
            "to_asset": to_asset,
            "asset_count": len(unique_assets),
            "has_asset_pair": len(unique_assets) >= 2
        }

# Factory function to create query classifier
def create_query_classifier(context_service: ContextService) -> QueryClassifier:
    """Create query classifier with context service dependency"""
    return QueryClassifier(context_service)