"""
Standardized Data Schemas for Financial Data

This module defines the canonical data formats that all vendors must conform to.
These schemas ensure consistent input/output regardless of the underlying vendor.
"""

from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from datetime import datetime


@dataclass
class StandardBar:
    """Standardized OHLC bar data format."""
    timestamp: str  # ISO 8601 format: "2024-01-01T09:30:00Z"
    symbol: str     # Standard symbol format: "AAPL"
    open: float
    high: float
    low: float
    close: float
    volume: int
    vwap: Optional[float] = None  # Volume weighted average price
    trade_count: Optional[int] = None


@dataclass
class StandardQuote:
    """Standardized quote data format."""
    timestamp: str  # ISO 8601 format
    symbol: str     # Standard symbol format: "AAPL"
    bid_price: float
    bid_size: int
    ask_price: float
    ask_size: int


@dataclass
class StandardTrade:
    """Standardized trade data format."""
    timestamp: str  # ISO 8601 format
    symbol: str     # Standard symbol format: "AAPL"
    price: float
    size: int
    exchange: Optional[str] = None


@dataclass
class StandardSnapshot:
    """Standardized market snapshot format."""
    symbol: str
    timestamp: str
    latest_trade: Optional[StandardTrade] = None
    latest_quote: Optional[StandardQuote] = None
    daily_bar: Optional[StandardBar] = None
    previous_close: Optional[float] = None


@dataclass
class StandardScreenerResult:
    """Standardized screener result format."""
    symbol: str
    name: str
    price: float
    change: float
    change_percent: float
    volume: int
    market_cap: Optional[float] = None


@dataclass
class StandardNewsArticle:
    """Standardized news article format."""
    id: str
    headline: str
    summary: Optional[str]
    content: Optional[str]
    symbols: List[str]
    published_at: str  # ISO 8601 format
    source: str
    url: Optional[str] = None


@dataclass
class StandardFundamentals:
    """Standardized fundamental data format."""
    symbol: str
    company_name: str
    sector: Optional[str] = None
    industry: Optional[str] = None
    market_cap: Optional[float] = None
    pe_ratio: Optional[float] = None
    pb_ratio: Optional[float] = None
    dividend_yield: Optional[float] = None
    eps: Optional[float] = None
    revenue: Optional[float] = None
    shares_outstanding: Optional[int] = None


@dataclass
class StandardDividend:
    """Standardized dividend data format."""
    symbol: str
    ex_date: str       # ISO 8601 date: "2024-01-01"
    payment_date: str  # ISO 8601 date
    record_date: Optional[str] = None
    declaration_date: Optional[str] = None
    amount: float
    currency: str = "USD"


@dataclass
class StandardSplit:
    """Standardized stock split data format."""
    symbol: str
    date: str          # ISO 8601 date: "2024-01-01"
    ratio: str         # Format: "2:1", "3:2", etc.
    split_factor: float  # Numerical factor: 2.0, 1.5, etc.


@dataclass
class StandardPosition:
    """Standardized position data format."""
    symbol: str
    quantity: float    # Positive for long, negative for short
    side: str         # "long" or "short"
    avg_entry_price: float
    current_price: float
    market_value: float
    cost_basis: float
    unrealized_pnl: float
    unrealized_pnl_percent: float


@dataclass
class StandardAccount:
    """Standardized account data format."""
    account_id: str
    status: str        # "ACTIVE", "SUSPENDED", etc.
    currency: str      # "USD", "CAD", etc.
    cash: float
    buying_power: float
    portfolio_value: float
    equity: float
    initial_margin: Optional[float] = None
    maintenance_margin: Optional[float] = None
    is_pattern_day_trader: bool = False


@dataclass
class StandardOrder:
    """Standardized order data format."""
    order_id: str
    client_order_id: Optional[str]
    symbol: str
    side: str          # "buy" or "sell"
    order_type: str    # "market", "limit", "stop", etc.
    quantity: float
    filled_quantity: float
    status: str        # "new", "filled", "canceled", etc.
    limit_price: Optional[float] = None
    stop_price: Optional[float] = None
    filled_avg_price: Optional[float] = None
    created_at: str    # ISO 8601 format
    filled_at: Optional[str] = None


# Standard symbol format utilities
class SymbolFormatter:
    """Utilities for standardizing symbol formats across vendors."""
    
    @staticmethod
    def to_standard(symbol: str, vendor: str) -> str:
        """Convert vendor-specific symbol to standard format.
        
        Standard format: Just the symbol (e.g., "AAPL")
        """
        if vendor == "eodhd":
            # EODHD uses "AAPL.US" format - remove exchange suffix
            return symbol.split('.')[0] if '.' in symbol else symbol
        elif vendor == "alpaca":
            # Alpaca uses "AAPL" format - already standard
            return symbol.upper()
        return symbol.upper()
    
    @staticmethod
    def from_standard(symbol: str, vendor: str) -> str:
        """Convert standard symbol to vendor-specific format."""
        if vendor == "eodhd":
            # EODHD requires exchange suffix for US stocks
            return f"{symbol.upper()}.US" if '.' not in symbol else symbol.upper()
        elif vendor == "alpaca":
            # Alpaca uses standard format
            return symbol.upper()
        return symbol.upper()
    
    @staticmethod
    def to_standard_list(symbols: List[str], vendor: str) -> List[str]:
        """Convert list of vendor symbols to standard format."""
        return [SymbolFormatter.to_standard(s, vendor) for s in symbols]
    
    @staticmethod
    def from_standard_list(symbols: List[str], vendor: str) -> List[str]:
        """Convert list of standard symbols to vendor format."""
        return [SymbolFormatter.from_standard(s, vendor) for s in symbols]


# Standard response formats
def standard_success_response(data: Any) -> Dict[str, Any]:
    """Standard success response format."""
    return {
        "success": True,
        "data": data,
        "error": None
    }


def standard_error_response(error_message: str) -> Dict[str, Any]:
    """Standard error response format."""
    return {
        "success": False,
        "data": None,
        "error": error_message
    }


# Validation utilities
def validate_date_format(date_str: str) -> bool:
    """Validate that date string is in YYYY-MM-DD format."""
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def validate_datetime_format(datetime_str: str) -> bool:
    """Validate that datetime string is in ISO 8601 format."""
    try:
        datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
        return True
    except ValueError:
        return False