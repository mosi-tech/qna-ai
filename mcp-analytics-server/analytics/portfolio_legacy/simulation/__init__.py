"""
Portfolio Simulation Functions

Backtesting and simulation tools for portfolio analysis.
"""

from .backtesting import (
    simple_portfolio_backtest,
    crisis_survival_test,
    rolling_returns_analysis,
    BACKTESTING_FUNCTIONS
)

__all__ = [
    'simple_portfolio_backtest',
    'crisis_survival_test', 
    'rolling_returns_analysis',
    'BACKTESTING_FUNCTIONS'
]