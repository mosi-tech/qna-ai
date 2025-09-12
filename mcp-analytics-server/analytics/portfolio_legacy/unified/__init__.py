"""
Unified Portfolio Analytics

Single comprehensive function that replaces all individual portfolio analysis tools.
Handles retail to quantitative complexity through parameter configuration.
"""

from .comprehensive_analyzer import (
    comprehensive_portfolio_analyzer,
    COMPREHENSIVE_PORTFOLIO_FUNCTIONS,
    get_comprehensive_functions
)

__all__ = [
    'comprehensive_portfolio_analyzer',
    'COMPREHENSIVE_PORTFOLIO_FUNCTIONS',
    'get_comprehensive_functions'
]