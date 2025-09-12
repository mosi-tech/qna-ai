"""
Composable Portfolio Analytics

Atomic functions designed for Q&A workflows where user questions 
get broken down into discrete steps, each mapping to one function.

Key Design Principles:
- Each function does ONE specific task
- Functions compose together for complex analyses  
- Pure functions: same inputs → same outputs
- Clear interfaces that chain together
- No monolithic "do everything" functions

Example Q&A Workflow:
User: "What was the Sharpe ratio of a 60/40 portfolio in 2020?"

Steps:
1. calculate_portfolio_returns(data, {"stocks": 0.6, "bonds": 0.4})
2. filter_date_range(returns, "2020-01-01", "2020-12-31") 
3. calculate_sharpe_ratio(filtered_returns)
"""

# Import all atomic function categories
from .data_processing import (
    calculate_portfolio_returns,
    filter_date_range,
    resample_frequency,
    align_data_series,
    fill_missing_data,
    DATA_PROCESSING_FUNCTIONS
)

from .performance_metrics import (
    calculate_total_return,
    calculate_annualized_return,
    calculate_volatility,
    calculate_sharpe_ratio,
    calculate_sortino_ratio,
    calculate_calmar_ratio,
    PERFORMANCE_METRICS_FUNCTIONS
)

from .risk_analysis import (
    calculate_drawdown_series,
    calculate_max_drawdown,
    calculate_var,
    calculate_cvar,
    calculate_beta,
    identify_bear_markets,
    RISK_ANALYSIS_FUNCTIONS
)

from .comparison_functions import (
    calculate_tracking_error,
    calculate_information_ratio,
    calculate_alpha,
    compare_performance_metrics,
    calculate_relative_performance,
    COMPARISON_FUNCTIONS
)

from .time_utilities import (
    calculate_relative_date_range,
    get_market_trading_days,
    calculate_rolling_metrics,
    identify_time_periods,
    TIME_UTILITIES_FUNCTIONS
)

# Combined registry for MCP server
ALL_PORTFOLIO_FUNCTIONS = {
    **DATA_PROCESSING_FUNCTIONS,
    **PERFORMANCE_METRICS_FUNCTIONS,
    **RISK_ANALYSIS_FUNCTIONS,
    **COMPARISON_FUNCTIONS,
    **TIME_UTILITIES_FUNCTIONS
}

__all__ = [
    # Data Processing
    'calculate_portfolio_returns',
    'filter_date_range',
    'resample_frequency',
    'align_data_series',
    'fill_missing_data',
    
    # Performance Metrics
    'calculate_total_return',
    'calculate_annualized_return',
    'calculate_volatility', 
    'calculate_sharpe_ratio',
    'calculate_sortino_ratio',
    'calculate_calmar_ratio',
    
    # Risk Analysis
    'calculate_drawdown_series',
    'calculate_max_drawdown',
    'calculate_var',
    'calculate_cvar',
    'calculate_beta',
    'identify_bear_markets',
    
    # Registry
    'ALL_PORTFOLIO_FUNCTIONS'
]


def get_all_portfolio_functions():
    """Get dictionary of all atomic portfolio functions"""
    return ALL_PORTFOLIO_FUNCTIONS


def get_portfolio_workflow_examples():
    """Get example Q&A workflows using atomic functions"""
    return {
        "sharpe_ratio_2020": {
            "question": "What was the Sharpe ratio of a 60/40 portfolio in 2020?",
            "steps": [
                "calculate_portfolio_returns(data, {'stocks': 0.6, 'bonds': 0.4})",
                "filter_date_range(returns, '2020-01-01', '2020-12-31')",
                "calculate_sharpe_ratio(filtered_returns, risk_free_rate=0.02)"
            ]
        },
        "crisis_drawdown": {
            "question": "What was the maximum drawdown during the 2008 financial crisis?",
            "steps": [
                "calculate_portfolio_returns(data, portfolio_weights)",
                "filter_date_range(returns, '2008-01-01', '2009-12-31')",
                "calculate_max_drawdown(crisis_returns)"
            ]
        },
        "bear_market_analysis": {
            "question": "How many bear markets has my portfolio experienced?",
            "steps": [
                "calculate_portfolio_returns(data, portfolio_weights)",
                "identify_bear_markets(returns, threshold=-0.20)"
            ]
        },
        "volatility_comparison": {
            "question": "Compare monthly vs daily volatility",
            "steps": [
                "calculate_portfolio_returns(data, weights)",
                "resample_frequency(returns, 'monthly')",  
                "calculate_volatility(daily_returns)",
                "calculate_volatility(monthly_returns)"
            ]
        }
    }


def get_function_categories():
    """Get functions organized by category"""
    return {
        "data_processing": [
            "calculate_portfolio_returns",
            "filter_date_range", 
            "resample_frequency",
            "align_data_series",
            "fill_missing_data"
        ],
        "performance_metrics": [
            "calculate_total_return",
            "calculate_annualized_return",
            "calculate_volatility",
            "calculate_sharpe_ratio", 
            "calculate_sortino_ratio",
            "calculate_calmar_ratio"
        ],
        "risk_analysis": [
            "calculate_drawdown_series",
            "calculate_max_drawdown",
            "calculate_var",
            "calculate_cvar", 
            "calculate_beta",
            "identify_bear_markets"
        ]
    }


def get_composability_info():
    """Information about how functions compose together"""
    return {
        "design_principle": "Each function does ONE thing, composes with others",
        "total_functions": len(ALL_PORTFOLIO_FUNCTIONS),
        "categories": len(get_function_categories()),
        "workflow_pattern": "User question → Steps → Function chain → Result",
        "example_chain": [
            "Historical data + weights → calculate_portfolio_returns → returns",
            "Returns + date range → filter_date_range → filtered_returns", 
            "Filtered returns → calculate_sharpe_ratio → sharpe_ratio"
        ]
    }