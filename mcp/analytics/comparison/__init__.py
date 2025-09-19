"""
Comparison Analysis Module

Atomic comparison functions for assets, strategies, and portfolios.
From financial-analysis-function-library.json comparison_analysis category.
"""

from .metrics import (
    compare_performance_metrics,
    compare_risk_metrics,
    compare_drawdowns,
    compare_volatility_profiles,
    compare_correlation_stability,
    compare_sector_exposure,
    compare_expense_ratios,
    compare_liquidity,
    compare_fundamental,
    COMPARISON_METRICS_FUNCTIONS
)

__all__ = [
    'compare_performance_metrics',
    'compare_risk_metrics', 
    'compare_drawdowns',
    'compare_volatility_profiles',
    'compare_correlation_stability',
    'compare_sector_exposure',
    'compare_expense_ratios',
    'compare_liquidity',
    'compare_fundamental',
    'COMPARISON_METRICS_FUNCTIONS'
]