"""
Comprehensive Technical Analysis Module

This module provides a sophisticated, well-organized technical analysis system with:

1. CORE INDICATORS (36 functions):
   - Moving Averages (2): sma, ema
   - Momentum Oscillators (9): rsi, stochastic, stochastic_rsi, williams_r, cci, 
     money_flow_index, ultimate_oscillator, awesome_oscillator, rate_of_change
   - Trend Indicators (10): macd, adx, trix, parabolic_sar, aroon, mass_index, 
     dpo, kst, ichimoku, supertrend
   - Volatility Indicators (4): bollinger_bands, atr, keltner_channels, donchian_channels
   - Volume Indicators (11): obv, vwap, chaikin_money_flow, accumulation_distribution,
     chaikin_oscillator, volume_sma, volume_weighted_moving_average, ease_of_movement,
     force_index, negative_volume_index, positive_volume_index

2. CROSSOVER DETECTION (10 functions):
   - moving_average_crossover (Golden/Death Cross)
   - macd_crossover (MACD line vs Signal line)  
   - rsi_level_cross (Overbought/Oversold levels)
   - stochastic_crossover (%K vs %D)
   - price_channel_breakout (Donchian breakouts)
   - bollinger_band_crossover (Price vs BB bands)
   - adx_directional_crossover (+DI vs -DI)
   - price_moving_average_crossover (Price vs single MA)
   - zero_line_crossover (Oscillator zero line)
   - multi_timeframe_crossover (3-MA alignment)

3. ADVANCED PATTERNS (4 functions):
   - bullish_confluence (Multi-indicator bullish setup)
   - bearish_confluence (Multi-indicator bearish setup)
   - squeeze_pattern (Bollinger/Keltner squeeze)
   - trend_continuation_pattern (Pullback continuation)

4. ADVANCED INDICATORS (42 functions):
   - Momentum (7): momentum, price_momentum_oscillator, true_strength_index, 
     percentage_price_oscillator, elder_ray_index, klinger_oscillator, stochastic_momentum_index
   - Trend (8): hull_moving_average, kaufman_adaptive_moving_average, triple_exponential_moving_average,
     zero_lag_exponential_moving_average, mcginley_dynamic, arnaud_legoux_moving_average,
     linear_regression_moving_average, variable_moving_average
   - Volatility (9): standard_deviation, historical_volatility, garman_klass_volatility,
     parkinson_volatility, rogers_satchell_volatility, yang_zhang_volatility,
     relative_volatility_index, volatility_ratio, volatility_system
   - Statistical (10): linear_regression, correlation_coefficient, z_score, skewness,
     kurtosis, percentile_rank, beta_coefficient, alpha_coefficient, information_ratio, sharpe_ratio
   - Market Structure (8): traditional_pivot_points, fibonacci_pivot_points, woodie_pivot_points,
     camarilla_pivot_points, swing_high_low, support_resistance_levels, zigzag_indicator, fractal_analysis

Total: 115 professional-grade technical analysis functions

All functions follow consistent patterns:
- Clean input/output interfaces
- Comprehensive error handling
- Standardized parameter names
- Detailed return dictionaries
- Professional-grade implementations
"""

# Import all core indicators
from .core.indicators import (
    # Moving Averages (2)
    sma, ema,
    
    # Momentum Oscillators (9)
    rsi, stochastic, stochastic_rsi, williams_r, cci, money_flow_index,
    ultimate_oscillator, awesome_oscillator, rate_of_change,
    
    # Trend Indicators (10)
    macd, adx, trix, parabolic_sar, aroon, mass_index, 
    dpo, kst, ichimoku, supertrend,
    
    # Volatility Indicators (4)
    bollinger_bands, atr, keltner_channels, donchian_channels,
    
    # Volume Indicators (11)
    obv, vwap, chaikin_money_flow, accumulation_distribution, chaikin_oscillator,
    volume_sma, volume_weighted_moving_average, ease_of_movement, force_index,
    negative_volume_index, positive_volume_index,
    
    # Registry
    CORE_INDICATORS
)

# Import all crossover detection functions
from .crossovers.detection import (
    moving_average_crossover,
    macd_crossover,
    rsi_level_cross,
    stochastic_crossover,
    price_channel_breakout,
    bollinger_band_crossover,
    adx_directional_crossover,
    price_moving_average_crossover,
    zero_line_crossover,
    multi_timeframe_crossover,
    CROSSOVER_FUNCTIONS
)

# Import all pattern recognition functions
from .patterns.recognition import (
    bullish_confluence,
    bearish_confluence,
    squeeze_pattern,
    trend_continuation_pattern,
    PATTERN_FUNCTIONS
)

# Import all advanced technical analysis functions
from .advanced import (
    ADVANCED_TECHNICAL_FUNCTIONS,
    get_advanced_function_categories,
    get_all_advanced_functions,
    get_advanced_function_count,
    execute_advanced_function
)


# Master registry of ALL technical analysis functions (Core + Advanced)
ALL_TECHNICAL_FUNCTIONS = {
    **CORE_INDICATORS,
    **CROSSOVER_FUNCTIONS,
    **PATTERN_FUNCTIONS,
    **ADVANCED_TECHNICAL_FUNCTIONS
}


def get_function_categories():
    """
    Get organized categories of all technical analysis functions (Core + Advanced)
    
    Returns:
        Dictionary with categorized function lists
    """
    # Get advanced categories
    advanced_categories = get_advanced_function_categories()
    
    return {
        'core_indicators': {
            'moving_averages': ['sma', 'ema'],
            'momentum_oscillators': [
                'rsi', 'stochastic', 'stochastic_rsi', 'williams_r', 'cci', 
                'money_flow_index', 'ultimate_oscillator', 'awesome_oscillator', 'rate_of_change'
            ],
            'trend_indicators': [
                'macd', 'adx', 'trix', 'parabolic_sar', 'aroon', 'mass_index',
                'dpo', 'kst', 'ichimoku', 'supertrend'
            ],
            'volatility_indicators': ['bollinger_bands', 'atr', 'keltner_channels', 'donchian_channels'],
            'volume_indicators': [
                'obv', 'vwap', 'chaikin_money_flow', 'accumulation_distribution', 'chaikin_oscillator',
                'volume_sma', 'volume_weighted_moving_average', 'ease_of_movement', 'force_index',
                'negative_volume_index', 'positive_volume_index'
            ]
        },
        'crossovers': [
            'moving_average_crossover',
            'macd_crossover', 
            'rsi_level_cross',
            'stochastic_crossover',
            'price_channel_breakout',
            'bollinger_band_crossover',
            'adx_directional_crossover',
            'price_moving_average_crossover',
            'zero_line_crossover',
            'multi_timeframe_crossover'
        ],
        'patterns': [
            'bullish_confluence',
            'bearish_confluence',
            'squeeze_pattern',
            'trend_continuation_pattern'
        ],
        'advanced_indicators': {
            'momentum': advanced_categories['momentum'],
            'trend': advanced_categories['trend'],
            'volatility': advanced_categories['volatility'],
            'statistical': advanced_categories['statistical'],
            'market_structure': advanced_categories['market_structure']
        }
    }


def get_all_functions():
    """
    Get list of all technical analysis function names
    
    Returns:
        List of all function names
    """
    return list(ALL_TECHNICAL_FUNCTIONS.keys())


def get_function_count():
    """
    Get count of functions by category (Core + Advanced)
    
    Returns:
        Dictionary with function counts
    """
    categories = get_function_categories()
    core_count = sum(len(funcs) for funcs in categories['core_indicators'].values())
    advanced_count = sum(len(funcs) for funcs in categories['advanced_indicators'].values())
    
    return {
        'core_indicators': core_count,
        'crossovers': len(categories['crossovers']),
        'patterns': len(categories['patterns']),
        'advanced_indicators': advanced_count,
        'total': len(ALL_TECHNICAL_FUNCTIONS)
    }


def execute_function(function_name: str, *args, **kwargs):
    """
    Execute any technical analysis function by name
    
    Args:
        function_name: Name of the function to execute
        *args: Positional arguments for the function
        **kwargs: Keyword arguments for the function
        
    Returns:
        Result of the function call
        
    Raises:
        ValueError: If function name is not found
    """
    if function_name not in ALL_TECHNICAL_FUNCTIONS:
        available_functions = ', '.join(sorted(ALL_TECHNICAL_FUNCTIONS.keys()))
        raise ValueError(f"Function '{function_name}' not found. Available functions: {available_functions}")
    
    return ALL_TECHNICAL_FUNCTIONS[function_name](*args, **kwargs)


# Export everything for easy importing
__all__ = [
    # Core Indicators - Moving Averages
    'sma', 'ema',
    
    # Core Indicators - Momentum Oscillators
    'rsi', 'stochastic', 'stochastic_rsi', 'williams_r', 'cci', 'money_flow_index',
    'ultimate_oscillator', 'awesome_oscillator', 'rate_of_change',
    
    # Core Indicators - Trend
    'macd', 'adx', 'trix', 'parabolic_sar', 'aroon', 'mass_index',
    'dpo', 'kst', 'ichimoku', 'supertrend',
    
    # Core Indicators - Volatility
    'bollinger_bands', 'atr', 'keltner_channels', 'donchian_channels',
    
    # Core Indicators - Volume
    'obv', 'vwap', 'chaikin_money_flow', 'accumulation_distribution', 'chaikin_oscillator',
    'volume_sma', 'volume_weighted_moving_average', 'ease_of_movement', 'force_index',
    'negative_volume_index', 'positive_volume_index',
    
    # Crossovers
    'moving_average_crossover', 'macd_crossover', 'rsi_level_cross', 
    'stochastic_crossover', 'price_channel_breakout', 'bollinger_band_crossover',
    'adx_directional_crossover', 'price_moving_average_crossover', 'zero_line_crossover',
    'multi_timeframe_crossover',
    
    # Patterns
    'bullish_confluence', 'bearish_confluence', 'squeeze_pattern', 
    'trend_continuation_pattern',
    
    # Utilities
    'ALL_TECHNICAL_FUNCTIONS', 'get_function_categories', 'get_all_functions',
    'get_function_count', 'execute_function'
]