"""
Financial Data Vendors Package

This package contains vendor-specific implementations for financial data providers.
Each vendor module implements the same set of functions with consistent interfaces,
allowing the generic layer to switch between vendors transparently.

Available vendors:
- alpaca: Alpaca Trading and Market Data APIs
- eodhd: EODHD Historical and Real-time Data API
"""

from . import alpaca
from . import eodhd

__all__ = ['alpaca', 'eodhd']