"""
Portfolio Analytics Module

NEW CONSOLIDATED SYSTEM: Single powerful function that handles all use cases
from simple retail questions to sophisticated quantitative analysis.

Key Features:
- One comprehensive function replacing 18+ separate tools
- Real market data integration (pre-fetched via MCP)
- Multi-tier complexity: Retail → Professional → Quantitative
- Handles portfolio allocation, rebalancing, backtesting, and reporting
- No internal MCP calls - data passed as input parameters
- Synchronous execution with proper error handling

Design Principles:
- Single function handles all complexity levels through parameters
- Pre-fetched data passed as input (proper MCP pattern)  
- Good defaults for retail use, full configurability for advanced users
- No function proliferation that confuses MCP tool selection
"""

# Import the consolidated comprehensive analyzer
from .unified import (
    comprehensive_portfolio_analyzer,
    COMPREHENSIVE_PORTFOLIO_FUNCTIONS
)

# Import legacy functions for backward compatibility (deprecated)
from .core import (
    portfolio_mix_tester,
    simple_asset_allocator,
    portfolio_drift_checker,
    CORE_PORTFOLIO_FUNCTIONS
)

from .simulation import (
    simple_portfolio_backtest,
    BACKTESTING_FUNCTIONS
)

from .optimization import (
    lazy_portfolio_comparison,
    LAZY_PORTFOLIO_FUNCTIONS
)

from .reporting import (
    portfolio_report_card,
    REPORTING_FUNCTIONS
)

# NEW: Primary function registry (single comprehensive function)
ALL_PORTFOLIO_FUNCTIONS = {
    **COMPREHENSIVE_PORTFOLIO_FUNCTIONS,
    # Legacy functions (for backward compatibility only)
    **CORE_PORTFOLIO_FUNCTIONS,
    **BACKTESTING_FUNCTIONS,
    **LAZY_PORTFOLIO_FUNCTIONS,
    **REPORTING_FUNCTIONS
}

__all__ = [
    # NEW: Primary comprehensive function (handles all use cases)
    'comprehensive_portfolio_analyzer',
    
    # Legacy functions (for backward compatibility - DEPRECATED)
    'portfolio_mix_tester',
    'simple_asset_allocator',
    'portfolio_drift_checker',
    'simple_portfolio_backtest',
    'lazy_portfolio_comparison',
    'portfolio_report_card',
    
    # Function registries
    'ALL_PORTFOLIO_FUNCTIONS',
    'COMPREHENSIVE_PORTFOLIO_FUNCTIONS'
]


def get_all_portfolio_functions():
    """Get dictionary of all portfolio functions"""
    return ALL_PORTFOLIO_FUNCTIONS


def get_recommended_function():
    """Get the recommended comprehensive function (replaces 18+ individual functions)"""
    return {
        'function_name': 'comprehensive_portfolio_analyzer',
        'description': 'Single powerful function handling all portfolio analysis needs',
        'capabilities': [
            'Portfolio allocation testing and optimization',
            'Rebalancing strategy analysis with transaction costs',
            'Historical backtesting with real market data',
            'Risk analysis and performance metrics',
            'Stress testing and scenario analysis',
            'Multi-tier complexity (retail/professional/quantitative)'
        ],
        'data_requirements': 'Pre-fetched historical data via MCP financial server',
        'replaces': '18+ individual portfolio functions'
    }


def get_portfolio_function_categories():
    """Get portfolio functions organized by category (NEW vs LEGACY)"""
    return {
        'recommended': ['comprehensive_portfolio_analyzer'],  # Handles everything
        'legacy_core': ['portfolio_mix_tester', 'simple_asset_allocator', 'portfolio_drift_checker'],
        'legacy_backtesting': ['simple_portfolio_backtest'],
        'legacy_optimization': ['lazy_portfolio_comparison'], 
        'legacy_reporting': ['portfolio_report_card']
    }


def get_portfolio_function_count():
    """Get count of portfolio functions by category"""
    return {
        'recommended_functions': 1,  # Single comprehensive function
        'legacy_functions': len(ALL_PORTFOLIO_FUNCTIONS) - 1,
        'total_functions': len(ALL_PORTFOLIO_FUNCTIONS),
        'consolidation_ratio': f"1 function replaces {len(ALL_PORTFOLIO_FUNCTIONS) - 1} legacy functions"
    }