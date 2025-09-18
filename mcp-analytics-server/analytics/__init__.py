"""
Analytics New - Reorganized Financial Analysis Engine

Complete rewrite using libraries from requirements.txt - no manual calculations
From financial-analysis-function-library.json
"""

# Import all modules
from .utils import *
from .performance import *
from .indicators import *
from .portfolio import *
from .risk import *

# Export main interface
from .main import AnalyticsEngine, get_all_functions

__version__ = "2.0.0"
__all__ = [
    'AnalyticsEngine',
    'get_all_functions'
]