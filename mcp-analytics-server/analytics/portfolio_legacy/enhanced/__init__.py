"""
Enhanced Portfolio Analytics

Next-generation portfolio analysis system that integrates real financial data,
supports multi-tier complexity, and provides sophisticated yet accessible tools.

Key Features:
- Real MCP financial data integration (Alpaca, EODHD)
- Multi-tier interface: Retail → Professional → Quantitative
- Highly configurable analysis parameters
- Integration with technical indicators
- Custom scenario and stress testing
- Factor-based portfolio construction
- Dynamic rebalancing strategies

Architecture:
- data_driven_analyzer: Sophisticated portfolio analysis with real data
- configurable_rebalancing: Advanced rebalancing strategies and testing
- scenario_testing: Custom market scenario analysis
- factor_models: Factor-based portfolio construction (coming soon)
"""

from .data_driven_analyzer import (
    enhanced_portfolio_analyzer,
    AssetSpec,
    AnalysisConfig,
    ENHANCED_PORTFOLIO_FUNCTIONS
)

from .configurable_rebalancing import (
    configurable_rebalancing_analyzer,
    RebalancingStrategy,
    RebalancingConfig,
    ENHANCED_REBALANCING_FUNCTIONS
)

# Combined enhanced function registry
ENHANCED_FUNCTIONS = {
    **ENHANCED_PORTFOLIO_FUNCTIONS,
    **ENHANCED_REBALANCING_FUNCTIONS
}

__all__ = [
    # Core enhanced functions
    'enhanced_portfolio_analyzer',
    'configurable_rebalancing_analyzer',
    
    # Configuration classes
    'AssetSpec',
    'AnalysisConfig', 
    'RebalancingStrategy',
    'RebalancingConfig',
    
    # Registry
    'ENHANCED_FUNCTIONS'
]


def get_enhanced_functions():
    """Get all enhanced portfolio functions"""
    return ENHANCED_FUNCTIONS


def get_enhanced_function_info():
    """Get information about enhanced functions"""
    return {
        "enhanced_portfolio_analyzer": {
            "description": "Multi-tier portfolio analysis with real market data",
            "modes": ["retail", "professional", "quantitative"],
            "data_sources": ["alpaca", "eodhd"],
            "features": ["real_data", "technical_integration", "stress_testing", "custom_scenarios"]
        },
        "configurable_rebalancing_analyzer": {
            "description": "Advanced rebalancing strategy analysis and comparison",
            "strategies": ["calendar", "threshold", "momentum", "technical_signals", "volatility_target"],
            "features": ["transaction_costs", "strategy_comparison", "real_backtesting"]
        }
    }


# Example usage configurations for different user types

RETAIL_EXAMPLES = {
    "simple_portfolio_test": {
        "portfolio_assets": {"VTI": 60, "BND": 40},
        "initial_investment": 10000,
        "monthly_contribution": 500
    },
    "three_fund_analysis": {
        "portfolio_preset": "3_fund",
        "initial_investment": 50000,
        "config": "AnalysisConfig(mode='retail', lookback_years=10)"
    }
}

PROFESSIONAL_EXAMPLES = {
    "factor_tilt_portfolio": {
        "portfolio_assets": [
            "AssetSpec('VTV', 'Value Stocks', 'value', 30.0)",
            "AssetSpec('VUG', 'Growth Stocks', 'growth', 30.0)", 
            "AssetSpec('VEA', 'International', 'international', 25.0)",
            "AssetSpec('BND', 'Bonds', 'bonds', 15.0)"
        ],
        "config": "AnalysisConfig(mode='professional', use_technical_indicators=True, stress_test_periods=['2008-01-01:2009-12-31'])"
    },
    "momentum_rebalancing": {
        "rebalancing_config": "RebalancingConfig(strategy=RebalancingStrategy.MOMENTUM, momentum_lookback=60)",
        "analysis_mode": "professional"
    }
}

QUANTITATIVE_EXAMPLES = {
    "risk_parity_portfolio": {
        "config": "AnalysisConfig(mode='quantitative')",
        "rebalancing_config": "RebalancingConfig(strategy=RebalancingStrategy.RISK_PARITY)",
        "custom_factors": ["momentum", "value", "quality", "low_volatility"]
    }
}