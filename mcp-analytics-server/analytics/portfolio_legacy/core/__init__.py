"""
Portfolio Core Functions

Core portfolio management functions for retail investors.
"""

from .allocation import (
    portfolio_mix_tester,
    simple_asset_allocator,
    portfolio_drift_checker,
    three_fund_portfolio_builder,
    CORE_ALLOCATION_FUNCTIONS
)

from .rebalancing import (
    rebalancing_frequency_tester,
    rebalancing_cost_calculator,
    smart_rebalancing_alerts,
    dollar_cost_averaging_vs_rebalancing,
    REBALANCING_FUNCTIONS
)

from .performance import (
    portfolio_performance_analyzer,
    risk_return_metrics,
    benchmark_comparison,
    PERFORMANCE_FUNCTIONS
)

# Combine all core portfolio functions
CORE_PORTFOLIO_FUNCTIONS = {
    **CORE_ALLOCATION_FUNCTIONS,
    **REBALANCING_FUNCTIONS,
    **PERFORMANCE_FUNCTIONS
}

__all__ = [
    # Allocation functions
    'portfolio_mix_tester',
    'simple_asset_allocator', 
    'portfolio_drift_checker',
    'three_fund_portfolio_builder',
    
    # Rebalancing functions
    'rebalancing_frequency_tester',
    'rebalancing_cost_calculator',
    'smart_rebalancing_alerts',
    'dollar_cost_averaging_vs_rebalancing',
    
    # Performance functions
    'portfolio_performance_analyzer',
    'risk_return_metrics',
    'benchmark_comparison',
    
    # Registry
    'CORE_PORTFOLIO_FUNCTIONS'
]