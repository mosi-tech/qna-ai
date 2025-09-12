"""
Portfolio Optimization Functions

Lazy portfolios and optimization tools.
"""

from .lazy_portfolios import (
    three_fund_portfolio_builder,
    four_fund_portfolio_builder,
    target_date_portfolio_analyzer,
    lazy_portfolio_comparison,
    LAZY_PORTFOLIO_FUNCTIONS
)

__all__ = [
    'three_fund_portfolio_builder',
    'four_fund_portfolio_builder',
    'target_date_portfolio_analyzer',
    'lazy_portfolio_comparison',
    'LAZY_PORTFOLIO_FUNCTIONS'
]