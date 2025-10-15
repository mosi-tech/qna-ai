"""
Utilities Module

Provides data validation, transformation, and standardization utilities for financial analysis.
This module implements core utility functions that support the entire analytics framework,
including time series processing, data validation, and output standardization.

Key Functionality:
    - Data validation for returns, prices, and time series data
    - Time series transformations (resampling, return calculations)
    - Output standardization for consistent API responses
    - Series alignment for multi-asset analysis
    - Data format conversions and type handling

All utilities leverage established libraries (pandas, numpy) for reliability and performance.

Example:
    >>> from analytics.utils import validate_return_data, prices_to_returns
    >>> import pandas as pd
    >>> prices = pd.Series([100, 102, 98, 105])
    >>> returns = prices_to_returns(prices, method='simple')
    >>> validated = validate_return_data(returns)
"""

from .data_utils import *