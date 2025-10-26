"""Market Analysis Package.

This package provides comprehensive market analysis tools for detecting trends, regimes, stress
conditions, and structural patterns in financial markets. The module implements both simple atomic
functions and complex analytical functions using industry-standard libraries like empyrical,
scipy, and scikit-learn for proven accuracy and advanced statistical analysis.

Modules:
    metrics: All market analysis functions with standardized outputs

Available Market Analysis Functions:
    Trend & Strength Analysis:
        - calculate_trend_strength: Multi-method trend strength measurement (ADX, regression, momentum)
        - calculate_market_stress: Comprehensive stress indicator using correlation, volatility, and tail risk
        - calculate_market_breadth: Market participation analysis using advance/decline ratios
    
    Regime & Pattern Detection:
        - detect_market_regime: Bull/bear/sideways regime identification using multiple methodologies
        - analyze_volatility_clustering: ARCH effects and volatility regime analysis
        - analyze_seasonality: Calendar effect and seasonal pattern detection
    
    Structural Analysis:
        - detect_structural_breaks: CUSUM-based breakpoint detection for regime changes
        - detect_crisis_periods: Crisis identification using drawdown and volatility thresholds
        
    Specialized Analysis:
        - calculate_crypto_metrics: Cryptocurrency-specific metrics including fear/greed index
        - analyze_weekday_performance: Day-of-week effect and trading anomaly analysis
        - analyze_monthly_performance: Monthly seasonal pattern and calendar effect analysis

Features:
    - Industry-standard statistical methods using empyrical, scipy, and scikit-learn
    - Multiple methodologies for robust analysis (technical, statistical, machine learning)
    - Comprehensive regime detection with transition analysis
    - Advanced time series analysis for structural break detection
    - Crisis period identification with market stress indicators
    - Support for both traditional and cryptocurrency market analysis
    - Standardized return format with success indicators and detailed error handling
    - Google docstring documentation with examples and interpretation guidance

Example:
    >>> from mcp.analytics.market import calculate_trend_strength, detect_market_regime
    >>> import pandas as pd
    >>> import numpy as np
    >>> 
    >>> # Create sample price data
    >>> dates = pd.date_range('2020-01-01', periods=252, freq='D')
    >>> prices = pd.Series(100 * np.cumprod(1 + np.random.normal(0.0008, 0.015, 252)), index=dates)
    >>> 
    >>> # Analyze trend strength
    >>> trend_analysis = calculate_trend_strength(prices, method="regression")
    >>> print(f"Trend Strength: {trend_analysis['strength_rating']}")
    >>> print(f"R-squared: {trend_analysis['r_squared']:.3f}")
    >>> print(f"Trend Direction: {trend_analysis['trend_direction']}")
    >>> 
    >>> # Detect market regime
    >>> regime_analysis = detect_market_regime(prices, method="volatility_trend")
    >>> print(f"Current Regime: {regime_analysis['current_regime']}")
    >>> print(f"Most Common Regime: {regime_analysis['regime_stability']['most_common_regime']}")

Note:
    - Functions support both price and return data with automatic data type detection
    - Multiple methodologies provided for each analysis type to suit different use cases
    - Advanced functions use machine learning techniques for pattern recognition
    - All statistical tests include significance levels and confidence intervals
    - Cryptocurrency functions account for 24/7 trading and higher volatility characteristics
    - Results include both quantitative metrics and qualitative interpretations
"""

from .metrics import *

