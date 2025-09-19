"""
Market Analysis Module

Market analysis functions from financial-analysis-function-library.json market_analysis category.
Both simple atomic functions and complex analytical functions.
"""

from .metrics import (
    calculate_trend_strength,
    calculate_market_stress,
    calculate_market_breadth,
    detect_market_regime,
    analyze_volatility_clustering,
    analyze_seasonality,
    detect_structural_breaks,
    detect_crisis_periods,
    MARKET_ANALYSIS_FUNCTIONS
)

__all__ = [
    'calculate_trend_strength',
    'calculate_market_stress', 
    'calculate_market_breadth',
    'detect_market_regime',
    'analyze_volatility_clustering',
    'analyze_seasonality',
    'detect_structural_breaks',
    'detect_crisis_periods',
    'MARKET_ANALYSIS_FUNCTIONS'
]