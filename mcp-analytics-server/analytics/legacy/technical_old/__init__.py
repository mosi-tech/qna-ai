"""
Technical Analysis Module - Clean, Consolidated Implementation

This module provides comprehensive technical analysis with ZERO redundancy:
- Single source of truth for each indicator
- Consistent API across all functions  
- Comprehensive error handling and data validation
- MCP-ready responses with rich metadata

Structure:
├── framework.py     - Shared utilities, decorators, error handling
├── momentum.py      - RSI, MACD, Stochastic, Williams %R, Awesome, Ultimate, ROC
├── trend.py         - ADX, CCI, Aroon, Parabolic SAR
├── volatility.py    - Bollinger Bands, ATR, Keltner, Donchian
├── volume.py        - OBV, MFI, A/D Line, Chaikin Money Flow  
└── patterns.py      - Support/Resistance, Gaps, Breakouts
"""

# Framework and utilities
from .framework import (
    mcp_resilient, standardize_ta_response, detect_crossovers, detect_divergences,
    calculate_signal_strength, generate_trading_recommendation, safe_ta_calculation,
    calculate_data_quality_score, DataQualityError, InsufficientDataError
)

# Momentum indicators (7 functions)
from .momentum import (
    calculate_rsi, calculate_macd, calculate_stochastic, calculate_williams_r,
    calculate_awesome_oscillator, calculate_ultimate_oscillator, calculate_rate_of_change
)

# Trend indicators (4 functions)  
from .trend import (
    calculate_adx, calculate_cci, calculate_aroon, calculate_parabolic_sar
)

# Volatility indicators (4 functions)
from .volatility import (
    calculate_bollinger_bands, calculate_atr, calculate_keltner_channels, 
    calculate_donchian_channels
)

# Volume indicators (4 functions)
from .volume import (
    calculate_obv, calculate_mfi, calculate_ad_line, calculate_chaikin_money_flow
)

# Pattern detection (3 functions)
from .patterns import (
    detect_support_resistance, detect_gaps, detect_breakouts
)

# Legacy modules (for backward compatibility)
from .trend_analysis import TrendAnalyzer
from .moving_averages import MovingAverages
from .gaps import GapAnalyzer
from .indicators_ta import TechnicalAnalysisTA

# Complete function registry
TECHNICAL_FUNCTIONS = {
    # Momentum Indicators
    'calculate_rsi': calculate_rsi,
    'calculate_macd': calculate_macd,
    'calculate_stochastic': calculate_stochastic,
    'calculate_williams_r': calculate_williams_r,
    'calculate_awesome_oscillator': calculate_awesome_oscillator,
    'calculate_ultimate_oscillator': calculate_ultimate_oscillator,
    'calculate_rate_of_change': calculate_rate_of_change,
    
    # Trend Indicators
    'calculate_adx': calculate_adx,
    'calculate_cci': calculate_cci,
    'calculate_aroon': calculate_aroon,
    'calculate_parabolic_sar': calculate_parabolic_sar,
    
    # Volatility Indicators
    'calculate_bollinger_bands': calculate_bollinger_bands,
    'calculate_atr': calculate_atr,
    'calculate_keltner_channels': calculate_keltner_channels,
    'calculate_donchian_channels': calculate_donchian_channels,
    
    # Volume Indicators
    'calculate_obv': calculate_obv,
    'calculate_mfi': calculate_mfi,
    'calculate_ad_line': calculate_ad_line,
    'calculate_chaikin_money_flow': calculate_chaikin_money_flow,
    
    # Pattern Detection
    'detect_support_resistance': detect_support_resistance,
    'detect_gaps': detect_gaps,
    'detect_breakouts': detect_breakouts,
}

def get_all_functions():
    """Get all available technical analysis functions organized by category."""
    return {
        "momentum": [
            "calculate_rsi", "calculate_macd", "calculate_stochastic", 
            "calculate_williams_r", "calculate_awesome_oscillator", 
            "calculate_ultimate_oscillator", "calculate_rate_of_change"
        ],
        "trend": [
            "calculate_adx", "calculate_cci", "calculate_aroon", "calculate_parabolic_sar"
        ],
        "volatility": [
            "calculate_bollinger_bands", "calculate_atr", 
            "calculate_keltner_channels", "calculate_donchian_channels"
        ],
        "volume": [
            "calculate_obv", "calculate_mfi", "calculate_ad_line", "calculate_chaikin_money_flow"
        ],
        "patterns": [
            "detect_support_resistance", "detect_gaps", "detect_breakouts"
        ],
        "legacy": [
            "TrendAnalyzer", "MovingAverages", "GapAnalyzer", "TechnicalAnalysisTA"
        ]
    }

def get_function_count():
    """Get count of functions by category."""
    functions = get_all_functions()
    return {
        category: len(func_list) 
        for category, func_list in functions.items()
    }

# All exports
__all__ = [
    # Framework
    'mcp_resilient', 'standardize_ta_response', 'detect_crossovers', 'detect_divergences',
    'calculate_signal_strength', 'generate_trading_recommendation', 'safe_ta_calculation',
    'calculate_data_quality_score', 'DataQualityError', 'InsufficientDataError',
    
    # Momentum (7)
    'calculate_rsi', 'calculate_macd', 'calculate_stochastic', 'calculate_williams_r',
    'calculate_awesome_oscillator', 'calculate_ultimate_oscillator', 'calculate_rate_of_change',
    
    # Trend (4)
    'calculate_adx', 'calculate_cci', 'calculate_aroon', 'calculate_parabolic_sar',
    
    # Volatility (4)
    'calculate_bollinger_bands', 'calculate_atr', 'calculate_keltner_channels', 
    'calculate_donchian_channels',
    
    # Volume (4)
    'calculate_obv', 'calculate_mfi', 'calculate_ad_line', 'calculate_chaikin_money_flow',
    
    # Patterns (3)
    'detect_support_resistance', 'detect_gaps', 'detect_breakouts',
    
    # Legacy (4)
    'TrendAnalyzer', 'MovingAverages', 'GapAnalyzer', 'TechnicalAnalysisTA',
    
    # Utilities
    'TECHNICAL_FUNCTIONS', 'get_all_functions', 'get_function_count'
]

# Quick stats
print(f"Technical Analysis Module Loaded:")
print(f"- {len([f for f in __all__ if f.startswith('calculate_') or f.startswith('detect_')])} core functions")
print(f"- {len([f for f in __all__ if not f.startswith('calculate_') and not f.startswith('detect_') and f[0].isupper()])} legacy classes") 
print(f"- Zero redundancy, single source of truth for each indicator")