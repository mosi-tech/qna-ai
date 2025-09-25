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

__version__ = "2.0.0"
__all__ = []