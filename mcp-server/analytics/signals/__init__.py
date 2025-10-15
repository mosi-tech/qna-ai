"""
Signal Analysis and Generation Module

Provides comprehensive trading signal generation, analysis, and optimization tools
for developing and evaluating systematic trading strategies and indicator-based systems.

Key Functionality:
    - Signal generation from technical indicators (moving average crossovers, etc.)
    - Signal quality assessment (win rate, average return per signal)
    - False signal identification and filtering
    - Signal combination and weighting strategies
    - Parameter optimization for signal-based systems
    - Signal frequency and consistency analysis
    - Multi-timeframe signal analysis and confirmation
    - Signal reliability metrics

Core Components:
    
    1. Signal Generators (generators.py)
       - generate_signals(): Create buy/sell signals from indicators
       - calculate_signal_frequency(): Measure signal generation rate
       - combine_signals(): Merge multiple signals with weighting
       - filter_signals(): Remove low-quality or unreliable signals
    
    2. Signal Analysis (analysis.py)
       - analyze_signal_quality(): Evaluate signal performance metrics
       - identify_false_signals(): Detect unreliable signal types
       - optimize_signal_parameters(): Find optimal parameter settings

Key Applications:
    - Technical analysis automation
    - Trading strategy development
    - Indicator combination and weighting
    - Signal reliability assessment
    - Strategy backtesting and optimization
    - Risk management for signal-based systems
    - Multi-timeframe analysis
    - Machine learning feature generation

Example Usage:
    >>> from analytics.signals import generate_signals, analyze_signal_quality
    >>> import pandas as pd
    >>> prices = pd.Series([100, 102, 98, 105, 110])
    >>> 
    >>> signals = generate_signals(prices, signal_type='sma_crossover',
    ...                            fast_period=10, slow_period=20)
    >>> quality = analyze_signal_quality(prices, signals)
    >>> print(f"Signal win rate: {quality['win_rate']:.1%}")

Signal Quality Dimensions:
    - Frequency: How often signals are generated (balance between activity and false signals)
    - Accuracy: Percentage of signals resulting in profitable trades
    - Consistency: Reliability across different market regimes
    - Timing: How early signals identify market turning points
    - Correlation: Redundancy with other signals (lower is better for diversification)

Industry Best Practices:
    - Always validate signals on out-of-sample data
    - Combine multiple signals to reduce false positives
    - Account for transaction costs and slippage in analysis
    - Monitor signal performance over time for degradation
    - Use walk-forward analysis for parameter optimization
    - Consider correlation with market regime and volatility

Note:
    - Signals represented as -1 (sell), 0 (neutral), +1 (buy)
    - All signal analysis assumes candlestick/price bar data
    - Performance depends heavily on market conditions and asset class
    - Signal generation is probabilistic, not deterministic
    - Past signal performance does not guarantee future results
"""

from .generators import *
from .analysis import *

