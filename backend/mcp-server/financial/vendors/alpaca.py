"""
Alpaca Vendor Implementation - Trading and Market Data API Functions

This module contains all Alpaca-specific implementations for both trading
and market data APIs. Functions here are called by the generic vendor-independent
layer in functions_real.py.
"""

import os
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union


# API Configuration
ALPACA_API_KEY = os.getenv('ALPACA_API_KEY')
ALPACA_SECRET_KEY = os.getenv('ALPACA_SECRET_KEY')
ALPACA_BASE_URL = os.getenv('ALPACA_BASE_URL', 'https://paper-api.alpaca.markets')
ALPACA_DATA_URL = os.getenv('ALPACA_DATA_URL', 'https://data.alpaca.markets')


def get_headers() -> Dict[str, str]:
    """Generate HTTP headers for Alpaca API authentication."""
    return {
        'APCA-API-KEY-ID': ALPACA_API_KEY,
        'APCA-API-SECRET-KEY': ALPACA_SECRET_KEY,
        'Content-Type': 'application/json'
    }


# Trading API Functions
def get_account() -> Dict[str, Any]:
    """Retrieve comprehensive trading account information and balances."""
    try:
        if not ALPACA_API_KEY or not ALPACA_SECRET_KEY:
            raise ValueError("Alpaca API credentials not configured")
        
        url = f"{ALPACA_BASE_URL}/v2/account"
        response = requests.get(url, headers=get_headers())
        response.raise_for_status()
        
        return response.json()
        
    except Exception as e:
        return {"error": f"Account request failed: {str(e)}"}


def get_positions() -> List[Dict[str, Any]]:
    """Retrieve all open stock positions with profit/loss and market values."""
    try:
        if not ALPACA_API_KEY or not ALPACA_SECRET_KEY:
            raise ValueError("Alpaca API credentials not configured")
        
        url = f"{ALPACA_BASE_URL}/v2/positions"
        response = requests.get(url, headers=get_headers())
        response.raise_for_status()
        
        return response.json()
        
    except Exception as e:
        return {"error": f"Positions request failed: {str(e)}"}


def get_position(symbol: str) -> Dict[str, Any]:
    """Retrieve detailed position information for a specific symbol."""
    try:
        if not ALPACA_API_KEY or not ALPACA_SECRET_KEY:
            raise ValueError("Alpaca API credentials not configured")
        
        url = f"{ALPACA_BASE_URL}/v2/positions/{symbol}"
        response = requests.get(url, headers=get_headers())
        response.raise_for_status()
        
        return response.json()
        
    except Exception as e:
        return {"error": f"Position request failed: {str(e)}"}


def get_orders(status: str = "open", limit: int = 100, after: Optional[str] = None, until: Optional[str] = None, direction: str = "desc", nested: bool = False) -> List[Dict[str, Any]]:
    """Retrieve order history and status with comprehensive order details."""
    try:
        if not ALPACA_API_KEY or not ALPACA_SECRET_KEY:
            raise ValueError("Alpaca API credentials not configured")
        
        params = {
            'status': status,
            'limit': limit,
            'direction': direction,
            'nested': nested
        }
        
        if after:
            params['after'] = after
        if until:
            params['until'] = until
            
        url = f"{ALPACA_BASE_URL}/v2/orders"
        response = requests.get(url, headers=get_headers(), params=params)
        response.raise_for_status()
        
        return response.json()
        
    except Exception as e:
        return {"error": f"Orders request failed: {str(e)}"}


def get_portfolio_history(period: str = "1D", timeframe: str = "15Min", end_date: Optional[str] = None, extended_hours: bool = False) -> Dict[str, Any]:
    """Retrieve historical portfolio performance and value changes over time."""
    try:
        if not ALPACA_API_KEY or not ALPACA_SECRET_KEY:
            raise ValueError("Alpaca API credentials not configured")
        
        params = {
            'period': period,
            'timeframe': timeframe,
            'extended_hours': extended_hours
        }
        
        if end_date:
            params['end_date'] = end_date
            
        url = f"{ALPACA_BASE_URL}/v2/portfolio/history"
        response = requests.get(url, headers=get_headers(), params=params)
        response.raise_for_status()
        
        return response.json()
        
    except Exception as e:
        return {"error": f"Portfolio history request failed: {str(e)}"}


def get_clock() -> Dict[str, Any]:
    """Retrieve current market status and trading session information."""
    try:
        if not ALPACA_API_KEY or not ALPACA_SECRET_KEY:
            raise ValueError("Alpaca API credentials not configured")
        
        url = f"{ALPACA_BASE_URL}/v2/clock"
        response = requests.get(url, headers=get_headers())
        response.raise_for_status()
        
        return response.json()
        
    except Exception as e:
        return {"error": f"Clock request failed: {str(e)}"}


# Market Data API Functions
def get_bars(symbols: List[str], timeframe: str = "1Day", start: Optional[str] = None, end: Optional[str] = None) -> Dict[str, Any]:
    """Retrieve historical OHLC price bars for multiple stocks."""
    try:
        if not ALPACA_API_KEY or not ALPACA_SECRET_KEY:
            raise ValueError("Alpaca API credentials not configured")
        
        params = {
            'symbols': ",".join(symbols),
            'timeframe': timeframe
        }
        
        if start:
            params['start'] = start
        if end:
            params['end'] = end
            
        url = f"{ALPACA_DATA_URL}/v2/stocks/bars"
        response = requests.get(url, headers=get_headers(), params=params)
        response.raise_for_status()
        
        return response.json()
        
    except Exception as e:
        return {"error": f"Bars request failed: {str(e)}"}


def get_snapshots(symbols: List[str]) -> Dict[str, Any]:
    """Retrieve comprehensive current market snapshots for multiple stocks."""
    try:
        if not ALPACA_API_KEY or not ALPACA_SECRET_KEY:
            raise ValueError("Alpaca API credentials not configured")
        
        params = {'symbols': ",".join(symbols)}
        
        url = f"{ALPACA_DATA_URL}/v2/stocks/snapshots"
        response = requests.get(url, headers=get_headers(), params=params)
        response.raise_for_status()
        
        return response.json()
        
    except Exception as e:
        return {"error": f"Snapshots request failed: {str(e)}"}


def get_quotes_latest(symbols: List[str]) -> Dict[str, Any]:
    """Retrieve latest bid/ask quotes for multiple stocks."""
    try:
        if not ALPACA_API_KEY or not ALPACA_SECRET_KEY:
            raise ValueError("Alpaca API credentials not configured")
        
        params = {'symbols': ",".join(symbols)}
        
        url = f"{ALPACA_DATA_URL}/v2/stocks/quotes/latest"
        response = requests.get(url, headers=get_headers(), params=params)
        response.raise_for_status()
        
        return response.json()
        
    except Exception as e:
        return {"error": f"Latest quotes request failed: {str(e)}"}


def get_trades_latest(symbols: List[str]) -> Dict[str, Any]:
    """Retrieve latest trade execution data for multiple stocks."""
    try:
        if not ALPACA_API_KEY or not ALPACA_SECRET_KEY:
            raise ValueError("Alpaca API credentials not configured")
        
        params = {'symbols': ",".join(symbols)}
        
        url = f"{ALPACA_DATA_URL}/v2/stocks/trades/latest"
        response = requests.get(url, headers=get_headers(), params=params)
        response.raise_for_status()
        
        return response.json()
        
    except Exception as e:
        return {"error": f"Latest trades request failed: {str(e)}"}


def get_most_actives(top: int = 10) -> Dict[str, Any]:
    """Screen for most actively traded stocks by volume."""
    try:
        if not ALPACA_API_KEY or not ALPACA_SECRET_KEY:
            raise ValueError("Alpaca API credentials not configured")
        
        params = {'top': top}
        
        url = f"{ALPACA_DATA_URL}/v1beta1/screener/stocks/most-actives"
        response = requests.get(url, headers=get_headers(), params=params)
        response.raise_for_status()
        
        return response.json()
        
    except Exception as e:
        return {"error": f"Most actives request failed: {str(e)}"}


def get_top_gainers(top: int = 10) -> Dict[str, Any]:
    """Screen for stocks with biggest percentage gains."""
    try:
        if not ALPACA_API_KEY or not ALPACA_SECRET_KEY:
            raise ValueError("Alpaca API credentials not configured")
        
        params = {'top': top}
        
        url = f"{ALPACA_DATA_URL}/v1beta1/screener/stocks/top-gainers"
        response = requests.get(url, headers=get_headers(), params=params)
        response.raise_for_status()
        
        return response.json()
        
    except Exception as e:
        return {"error": f"Top gainers request failed: {str(e)}"}


def get_top_losers(top: int = 10) -> Dict[str, Any]:
    """Screen for stocks with biggest percentage losses."""
    try:
        if not ALPACA_API_KEY or not ALPACA_SECRET_KEY:
            raise ValueError("Alpaca API credentials not configured")
        
        params = {'top': top}
        
        url = f"{ALPACA_DATA_URL}/v1beta1/screener/stocks/top-losers"
        response = requests.get(url, headers=get_headers(), params=params)
        response.raise_for_status()
        
        return response.json()
        
    except Exception as e:
        return {"error": f"Top losers request failed: {str(e)}"}


def get_news(symbols: List[str] = [], start: Optional[str] = None, end: Optional[str] = None, sort: str = "desc", include_content: bool = True) -> Dict[str, Any]:
    """Retrieve financial news articles and market information."""
    try:
        if not ALPACA_API_KEY or not ALPACA_SECRET_KEY:
            raise ValueError("Alpaca API credentials not configured")
        
        params = {
            'sort': sort,
            'include_content': include_content
        }
        
        if symbols:
            params['symbols'] = ",".join(symbols)
        if start:
            params['start'] = start
        if end:
            params['end'] = end
            
        url = f"{ALPACA_DATA_URL}/v1beta1/news"
        response = requests.get(url, headers=get_headers(), params=params)
        response.raise_for_status()
        
        return response.json()
        
    except Exception as e:
        return {"error": f"News request failed: {str(e)}"}