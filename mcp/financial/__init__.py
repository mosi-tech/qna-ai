"""
Financial Data MCP Server

Python implementation of financial data functions including:
- Alpaca Trading API
- Alpaca Market Data API  
- EODHD API

Available implementations:
- Mock: Realistic test data without API keys (functions_mock.py)
- Real: Actual API calls requiring credentials (functions_real.py)
"""

import os

# Import both mock and real implementations
try:
    from .functions_mock import MOCK_FINANCIAL_FUNCTIONS
except ImportError:
    MOCK_FINANCIAL_FUNCTIONS = {}

try:
    from .functions_real import REAL_FINANCIAL_FUNCTIONS  
except ImportError:
    REAL_FINANCIAL_FUNCTIONS = {}

# Determine which implementation to use
USE_MOCK = os.getenv('USE_MOCK_FINANCIAL_DATA', 'true').lower() == 'true'

# Select the appropriate function registry
if USE_MOCK:
    FINANCIAL_FUNCTIONS = MOCK_FINANCIAL_FUNCTIONS
    IMPLEMENTATION = "mock"
else:
    FINANCIAL_FUNCTIONS = REAL_FINANCIAL_FUNCTIONS
    IMPLEMENTATION = "real"

# Export all functions from the selected implementation
if USE_MOCK and MOCK_FINANCIAL_FUNCTIONS:
    from .functions_mock import *
elif REAL_FINANCIAL_FUNCTIONS:
    from .functions_real import *

__all__ = [
    'FINANCIAL_FUNCTIONS',
    'MOCK_FINANCIAL_FUNCTIONS', 
    'REAL_FINANCIAL_FUNCTIONS',
    'IMPLEMENTATION',
    'USE_MOCK'
]