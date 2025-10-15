"""
EODHD Vendor Implementation - Historical and Real-time Market Data API Functions

This module contains all EODHD-specific implementations for market data,
fundamentals, technical analysis, and screening. Functions here are called
by the generic vendor-independent layer in functions_real.py.
"""

import os
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union


# API Configuration
EODHD_API_KEY = os.getenv('EODHD_API_KEY')
EODHD_BASE_URL = os.getenv('EODHD_BASE_URL', 'https://eodhistoricaldata.com/api')


def get_eod_data(symbol: str, from_date: Optional[str] = None, to_date: Optional[str] = None, period: str = "d", order: str = "a") -> Dict[str, Any]:
    """Retrieve end-of-day historical OHLC prices with dividend and split adjustments."""
    try:
        if not EODHD_API_KEY:
            raise ValueError("EODHD_API_KEY not configured")
        
        params = {
            'api_token': EODHD_API_KEY,
            'period': period,
            'order': order
        }
        
        if from_date:
            params['from'] = from_date
        if to_date:
            params['to'] = to_date
            
        url = f"{EODHD_BASE_URL}/eod/{symbol}"
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        return response.json()
        
    except Exception as e:
        return {"error": f"EOD data request failed: {str(e)}"}


def get_real_time(symbol: str, fmt: str = "json") -> Dict[str, Any]:
    """Fetch real-time stock prices and current market data."""
    try:
        if not EODHD_API_KEY:
            raise ValueError("EODHD_API_KEY not configured")
        
        params = {
            'api_token': EODHD_API_KEY,
            'fmt': fmt
        }
        
        url = f"{EODHD_BASE_URL}/real-time/{symbol}"
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        return response.json()
        
    except Exception as e:
        return {"error": f"Real-time data request failed: {str(e)}"}


def get_fundamentals(symbol: str) -> Dict[str, Any]:
    """Retrieve comprehensive company fundamental data and financial metrics."""
    try:
        if not EODHD_API_KEY:
            raise ValueError("EODHD_API_KEY not configured")
        
        params = {'api_token': EODHD_API_KEY}
        
        url = f"{EODHD_BASE_URL}/fundamentals/{symbol}"
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        return response.json()
        
    except Exception as e:
        return {"error": f"Fundamentals request failed: {str(e)}"}


def get_dividends(symbol: str, from_date: Optional[str] = None, to_date: Optional[str] = None) -> List[Dict[str, Any]]:
    """Retrieve historical dividend payment data with important dates."""
    try:
        if not EODHD_API_KEY:
            raise ValueError("EODHD_API_KEY not configured")
        
        params = {'api_token': EODHD_API_KEY}
        
        if from_date:
            params['from'] = from_date
        if to_date:
            params['to'] = to_date
            
        url = f"{EODHD_BASE_URL}/div/{symbol}"
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        return response.json()
        
    except Exception as e:
        return {"error": f"Dividends request failed: {str(e)}"}


def get_splits(symbol: str, from_date: Optional[str] = None, to_date: Optional[str] = None) -> List[Dict[str, Any]]:
    """Retrieve historical stock split data with split ratios."""
    try:
        if not EODHD_API_KEY:
            raise ValueError("EODHD_API_KEY not configured")
        
        params = {'api_token': EODHD_API_KEY}
        
        if from_date:
            params['from'] = from_date
        if to_date:
            params['to'] = to_date
            
        url = f"{EODHD_BASE_URL}/splits/{symbol}"
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        return response.json()
        
    except Exception as e:
        return {"error": f"Splits request failed: {str(e)}"}


def get_technical(symbol: str, function: str, period: int = 14, from_date: Optional[str] = None, to_date: Optional[str] = None) -> List[Dict[str, Any]]:
    """Calculate technical analysis indicators for price trend analysis."""
    try:
        if not EODHD_API_KEY:
            raise ValueError("EODHD_API_KEY not configured")
        
        params = {
            'api_token': EODHD_API_KEY,
            'function': function,
            'period': period
        }
        
        if from_date:
            params['from'] = from_date
        if to_date:
            params['to'] = to_date
            
        url = f"{EODHD_BASE_URL}/technical/{symbol}"
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        return response.json()
        
    except Exception as e:
        return {"error": f"Technical analysis request failed: {str(e)}"}


def get_screener(filters: str = "", limit: int = 50, offset: int = 0, signals: str = "") -> List[Dict[str, Any]]:
    """Screen stocks using custom financial and technical criteria."""
    try:
        if not EODHD_API_KEY:
            raise ValueError("EODHD_API_KEY not configured")
        
        params = {
            'api_token': EODHD_API_KEY,
            'limit': limit,
            'offset': offset
        }
        
        if filters:
            params['filters'] = filters
        if signals:
            params['signals'] = signals
            
        url = f"{EODHD_BASE_URL}/screener"
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        return response.json()
        
    except Exception as e:
        return {"error": f"Screener request failed: {str(e)}"}


def search_symbols(query: str) -> List[Dict[str, Any]]:
    """Search for stocks and financial instruments by symbol or company name."""
    try:
        if not EODHD_API_KEY:
            raise ValueError("EODHD_API_KEY not configured")
        
        params = {'api_token': EODHD_API_KEY}
        
        url = f"{EODHD_BASE_URL}/search/{query}"
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        return response.json()
        
    except Exception as e:
        return {"error": f"Search request failed: {str(e)}"}


def get_exchanges_list() -> List[Dict[str, Any]]:
    """Retrieve list of all stock exchanges supported by EODHD API."""
    try:
        if not EODHD_API_KEY:
            raise ValueError("EODHD_API_KEY not configured")
        
        params = {'api_token': EODHD_API_KEY}
        
        url = f"{EODHD_BASE_URL}/exchanges-list"
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        return response.json()
        
    except Exception as e:
        return {"error": f"Exchanges list request failed: {str(e)}"}


def get_exchange_symbols(exchange: str) -> List[Dict[str, Any]]:
    """Retrieve all tradeable symbols available on a specific exchange."""
    try:
        if not EODHD_API_KEY:
            raise ValueError("EODHD_API_KEY not configured")
        
        params = {'api_token': EODHD_API_KEY}
        
        url = f"{EODHD_BASE_URL}/exchange-symbol-list/{exchange}"
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        return response.json()
        
    except Exception as e:
        return {"error": f"Exchange symbols request failed: {str(e)}"}