"""
Signal Analysis Module

Signal generation, manipulation, and analysis functions.
From financial-analysis-function-library.json signal_analysis category.
"""

from .generators import (
    generate_signals,
    calculate_signal_frequency,
    combine_signals,
    filter_signals,
    SIGNAL_GENERATORS_FUNCTIONS
)

from .analysis import (
    analyze_signal_quality,
    identify_false_signals,
    optimize_signal_parameters,
    SIGNAL_ANALYSIS_FUNCTIONS
)

__all__ = [
    'generate_signals',
    'calculate_signal_frequency',
    'combine_signals',
    'filter_signals',
    'analyze_signal_quality',
    'identify_false_signals',
    'optimize_signal_parameters',
    'SIGNAL_GENERATORS_FUNCTIONS',
    'SIGNAL_ANALYSIS_FUNCTIONS'
]