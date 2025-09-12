"""
Advanced Technical Analysis Module

This module provides additional technical indicators not available in the core module:

MOMENTUM INDICATORS (7 functions):
- momentum: Basic price momentum
- price_momentum_oscillator: Normalized momentum
- true_strength_index: Double-smoothed momentum oscillator
- percentage_price_oscillator: MACD in percentage terms
- elder_ray_index: Bull/Bear Power relative to EMA
- klinger_oscillator: Volume-based momentum
- stochastic_momentum_index: Double-smoothed stochastic

TREND INDICATORS (8 functions):
- hull_moving_average: Reduced lag moving average
- kaufman_adaptive_moving_average: Volatility-adaptive MA
- triple_exponential_moving_average: Triple smoothed EMA
- zero_lag_exponential_moving_average: Momentum-adjusted EMA
- mcginley_dynamic: Market speed adaptive MA
- arnaud_legoux_moving_average: Gaussian-filtered MA
- linear_regression_moving_average: Regression-based MA
- variable_moving_average: Volatility-based variable MA

VOLATILITY INDICATORS (9 functions):
- standard_deviation: Rolling standard deviation
- historical_volatility: Annualized volatility
- garman_klass_volatility: OHLC-based volatility
- parkinson_volatility: High-Low volatility
- rogers_satchell_volatility: Drift-independent volatility
- yang_zhang_volatility: Combined overnight/intraday volatility
- relative_volatility_index: RSI applied to volatility
- volatility_ratio: Short/long term volatility ratio
- volatility_system: Comprehensive volatility analysis

STATISTICAL INDICATORS (10 functions):
- linear_regression: Slope, intercept, R-squared analysis
- correlation_coefficient: Rolling correlation
- z_score: Standard score calculation
- skewness: Distribution asymmetry
- kurtosis: Distribution tail heaviness
- percentile_rank: Current value percentile
- beta_coefficient: Market sensitivity
- alpha_coefficient: Risk-adjusted excess return
- information_ratio: Benchmark-relative risk-adjusted return
- sharpe_ratio: Risk-adjusted return measure

MARKET STRUCTURE INDICATORS (8 functions):
- traditional_pivot_points: Classic pivot levels
- fibonacci_pivot_points: Fibonacci-based pivots
- woodie_pivot_points: Close-weighted pivots
- camarilla_pivot_points: Intraday-focused pivots
- swing_high_low: Swing point detection
- support_resistance_levels: Key level identification
- zigzag_indicator: Trend reversal filter
- fractal_analysis: Williams Fractals

Total: 64 additional professional-grade technical analysis functions

All functions follow consistent patterns:
- Clean input/output interfaces
- Comprehensive error handling
- Standardized parameter names
- Detailed return values
- Professional implementations using pandas/numpy/scipy
"""

# Import all advanced indicator modules
from .momentum import (
    momentum, price_momentum_oscillator, true_strength_index,
    percentage_price_oscillator, elder_ray_index, klinger_oscillator,
    roc_smoothed, stochastic_momentum_index, ADVANCED_MOMENTUM_INDICATORS,
    get_momentum_function_names
)

from .trend import (
    hull_moving_average, kaufman_adaptive_moving_average,
    triple_exponential_moving_average, zero_lag_exponential_moving_average,
    mcginley_dynamic, arnaud_legoux_moving_average,
    linear_regression_moving_average, variable_moving_average,
    ADVANCED_TREND_INDICATORS, get_trend_function_names
)

from .volatility import (
    standard_deviation, historical_volatility, garman_klass_volatility,
    parkinson_volatility, rogers_satchell_volatility, yang_zhang_volatility,
    relative_volatility_index, volatility_ratio, variance, vix_style_indicator,
    volatility_system, ADVANCED_VOLATILITY_INDICATORS, get_volatility_function_names
)

from .statistical import (
    linear_regression, correlation_coefficient, z_score, skewness,
    kurtosis, percentile_rank, beta_coefficient, alpha_coefficient,
    information_ratio, sharpe_ratio, standard_error_regression,
    cointegration_test, hurst_exponent, t_test_indicator,
    ADVANCED_STATISTICAL_INDICATORS, get_statistical_function_names
)

from .market_structure import (
    traditional_pivot_points, fibonacci_pivot_points, woodie_pivot_points,
    camarilla_pivot_points, swing_high_low, support_resistance_levels,
    zigzag_indicator, fractal_analysis, market_profile_basic,
    volume_weighted_average_price_session, MARKET_STRUCTURE_INDICATORS,
    get_market_structure_function_names
)

# Import new indicator categories
from .volume_price import (
    volume_rate_of_change, price_volume_trend, volume_oscillator,
    klinger_volume_oscillator, arms_index, volume_weighted_rsi,
    volume_accumulation_oscillator, money_flow_oscillator,
    VOLUME_PRICE_INDICATORS, get_volume_price_function_names
)

from .cycle_analysis import (
    dominant_cycle, cycle_period_detector, phase_indicator,
    instantaneous_trendline, cycle_strength_indicator, market_mode_indicator,
    CYCLE_ANALYSIS_INDICATORS, get_cycle_analysis_function_names
)


# Master registry of ALL advanced technical analysis functions
ADVANCED_TECHNICAL_FUNCTIONS = {
    **ADVANCED_MOMENTUM_INDICATORS,
    **ADVANCED_TREND_INDICATORS,
    **ADVANCED_VOLATILITY_INDICATORS,
    **ADVANCED_STATISTICAL_INDICATORS,
    **MARKET_STRUCTURE_INDICATORS,
    **VOLUME_PRICE_INDICATORS,
    **CYCLE_ANALYSIS_INDICATORS
}


def get_advanced_function_categories():
    """
    Get organized categories of advanced technical analysis functions
    
    Returns:
        Dictionary with categorized function lists
    """
    return {
        'momentum': get_momentum_function_names(),
        'trend': get_trend_function_names(),
        'volatility': get_volatility_function_names(),
        'statistical': get_statistical_function_names(),
        'market_structure': get_market_structure_function_names(),
        'volume_price': get_volume_price_function_names(),
        'cycle_analysis': get_cycle_analysis_function_names()
    }


def get_all_advanced_functions():
    """
    Get list of all advanced technical analysis function names
    
    Returns:
        List of all advanced function names
    """
    return list(ADVANCED_TECHNICAL_FUNCTIONS.keys())


def get_advanced_function_count():
    """
    Get count of advanced functions by category
    
    Returns:
        Dictionary with function counts
    """
    categories = get_advanced_function_categories()
    
    return {
        'momentum': len(categories['momentum']),
        'trend': len(categories['trend']),
        'volatility': len(categories['volatility']),
        'statistical': len(categories['statistical']),
        'market_structure': len(categories['market_structure']),
        'volume_price': len(categories['volume_price']),
        'cycle_analysis': len(categories['cycle_analysis']),
        'total': len(ADVANCED_TECHNICAL_FUNCTIONS)
    }


def execute_advanced_function(function_name: str, *args, **kwargs):
    """
    Execute any advanced technical analysis function by name
    
    Args:
        function_name: Name of the function to execute
        *args: Positional arguments for the function
        **kwargs: Keyword arguments for the function
        
    Returns:
        Result of the function call
        
    Raises:
        ValueError: If function name is not found
    """
    if function_name not in ADVANCED_TECHNICAL_FUNCTIONS:
        available_functions = ', '.join(sorted(ADVANCED_TECHNICAL_FUNCTIONS.keys()))
        raise ValueError(f"Advanced function '{function_name}' not found. Available functions: {available_functions}")
    
    return ADVANCED_TECHNICAL_FUNCTIONS[function_name](*args, **kwargs)


# Export everything for easy importing
__all__ = [
    # Momentum Indicators
    'momentum', 'price_momentum_oscillator', 'true_strength_index',
    'percentage_price_oscillator', 'elder_ray_index', 'klinger_oscillator',
    'stochastic_momentum_index',
    
    # Trend Indicators
    'hull_moving_average', 'kaufman_adaptive_moving_average',
    'triple_exponential_moving_average', 'zero_lag_exponential_moving_average',
    'mcginley_dynamic', 'arnaud_legoux_moving_average',
    'linear_regression_moving_average', 'variable_moving_average',
    
    # Volatility Indicators
    'standard_deviation', 'historical_volatility', 'garman_klass_volatility',
    'parkinson_volatility', 'rogers_satchell_volatility', 'yang_zhang_volatility',
    'relative_volatility_index', 'volatility_ratio', 'volatility_system',
    
    # Statistical Indicators
    'linear_regression', 'correlation_coefficient', 'z_score', 'skewness',
    'kurtosis', 'percentile_rank', 'beta_coefficient', 'alpha_coefficient',
    'information_ratio', 'sharpe_ratio',
    
    # Market Structure Indicators
    'traditional_pivot_points', 'fibonacci_pivot_points', 'woodie_pivot_points',
    'camarilla_pivot_points', 'swing_high_low', 'support_resistance_levels',
    'zigzag_indicator', 'fractal_analysis',
    
    # Registries and Utilities
    'ADVANCED_TECHNICAL_FUNCTIONS', 'get_advanced_function_categories',
    'get_all_advanced_functions', 'get_advanced_function_count',
    'execute_advanced_function'
]