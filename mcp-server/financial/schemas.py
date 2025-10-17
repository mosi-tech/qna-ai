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
    """Standardized OHLC bar data format.
    
    Supports both attribute and dictionary-style access:
        bar.timestamp or bar["timestamp"]
        bar.close or bar["close"]
    """
    timestamp: str  # ISO 8601 format: "2024-01-01T09:30:00Z"
    symbol: str     # Standard symbol format: "AAPL"
    open: float
    high: float
    low: float
    close: float
    volume: int
    vwap: Optional[float] = None  # Volume weighted average price
    trade_count: Optional[int] = None
    
    def __getitem__(self, key: str) -> Any:
        """Support dictionary-style access: bar['timestamp']"""
        return getattr(self, key)
    
    def __setitem__(self, key: str, value: Any) -> None:
        """Support dictionary-style setting: bar['close'] = 150.0"""
        setattr(self, key, value)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Support dict.get() method: bar.get('vwap', 0.0)"""
        return getattr(self, key, default)
    
    def __contains__(self, key: str) -> bool:
        """Support 'in' operator: 'timestamp' in bar"""
        return hasattr(self, key)
    
    def keys(self):
        """Return field names like dict.keys()"""
        return self.__dataclass_fields__.keys()
    
    def values(self):
        """Return field values like dict.values()"""
        return [getattr(self, k) for k in self.__dataclass_fields__.keys()]
    
    def items(self):
        """Return (key, value) pairs like dict.items()"""
        return [(k, getattr(self, k)) for k in self.__dataclass_fields__.keys()]


@dataclass
class StandardQuote:
    """Standardized quote data format.
    
    Supports both attribute and dictionary-style access:
        quote.bid_price or quote["bid_price"]
        quote.ask_price or quote["ask_price"]
    """
    timestamp: str  # ISO 8601 format
    symbol: str     # Standard symbol format: "AAPL"
    bid_price: float
    bid_size: int
    ask_price: float
    ask_size: int
    
    def __getitem__(self, key: str) -> Any:
        """Support dictionary-style access: quote['bid_price']"""
        return getattr(self, key)
    
    def __setitem__(self, key: str, value: Any) -> None:
        """Support dictionary-style setting: quote['bid_price'] = 150.0"""
        setattr(self, key, value)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Support dict.get() method: quote.get('bid_price', 0.0)"""
        return getattr(self, key, default)
    
    def __contains__(self, key: str) -> bool:
        """Support 'in' operator: 'bid_price' in quote"""
        return hasattr(self, key)
    
    def keys(self):
        """Return field names like dict.keys()"""
        return self.__dataclass_fields__.keys()
    
    def values(self):
        """Return field values like dict.values()"""
        return [getattr(self, k) for k in self.__dataclass_fields__.keys()]
    
    def items(self):
        """Return (key, value) pairs like dict.items()"""
        return [(k, getattr(self, k)) for k in self.__dataclass_fields__.keys()]


@dataclass
class StandardTrade:
    """Standardized trade data format.
    
    Supports both attribute and dictionary-style access:
        trade.price or trade["price"]
        trade.size or trade["size"]
    """
    timestamp: str  # ISO 8601 format
    symbol: str     # Standard symbol format: "AAPL"
    price: float
    size: int
    exchange: Optional[str] = None
    
    def __getitem__(self, key: str) -> Any:
        """Support dictionary-style access: trade['price']"""
        return getattr(self, key)
    
    def __setitem__(self, key: str, value: Any) -> None:
        """Support dictionary-style setting: trade['price'] = 150.0"""
        setattr(self, key, value)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Support dict.get() method: trade.get('exchange', 'UNKNOWN')"""
        return getattr(self, key, default)
    
    def __contains__(self, key: str) -> bool:
        """Support 'in' operator: 'price' in trade"""
        return hasattr(self, key)
    
    def keys(self):
        """Return field names like dict.keys()"""
        return self.__dataclass_fields__.keys()
    
    def values(self):
        """Return field values like dict.values()"""
        return [getattr(self, k) for k in self.__dataclass_fields__.keys()]
    
    def items(self):
        """Return (key, value) pairs like dict.items()"""
        return [(k, getattr(self, k)) for k in self.__dataclass_fields__.keys()]


@dataclass
class StandardSnapshot:
    """Standardized market snapshot format.
    
    Supports both attribute and dictionary-style access:
        snapshot.symbol or snapshot["symbol"]
        snapshot.latest_trade or snapshot["latest_trade"]
    """
    symbol: str
    timestamp: str
    latest_trade: Optional[StandardTrade] = None
    latest_quote: Optional[StandardQuote] = None
    daily_bar: Optional[StandardBar] = None
    previous_close: Optional[float] = None
    
    def __getitem__(self, key: str) -> Any:
        """Support dictionary-style access: snapshot['symbol']"""
        return getattr(self, key)
    
    def __setitem__(self, key: str, value: Any) -> None:
        """Support dictionary-style setting: snapshot['previous_close'] = 150.0"""
        setattr(self, key, value)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Support dict.get() method: snapshot.get('previous_close', 0.0)"""
        return getattr(self, key, default)
    
    def __contains__(self, key: str) -> bool:
        """Support 'in' operator: 'latest_trade' in snapshot"""
        return hasattr(self, key)
    
    def keys(self):
        """Return field names like dict.keys()"""
        return self.__dataclass_fields__.keys()
    
    def values(self):
        """Return field values like dict.values()"""
        return [getattr(self, k) for k in self.__dataclass_fields__.keys()]
    
    def items(self):
        """Return (key, value) pairs like dict.items()"""
        return [(k, getattr(self, k)) for k in self.__dataclass_fields__.keys()]


@dataclass
class StandardScreenerResult:
    """Standardized screener result format.
    
    Supports both attribute and dictionary-style access:
        result.symbol or result["symbol"]
        result.price or result["price"]
    """
    symbol: str
    name: str
    price: float
    change: float
    change_percent: float
    volume: int
    market_cap: Optional[float] = None
    
    def __getitem__(self, key: str) -> Any:
        """Support dictionary-style access: result['price']"""
        return getattr(self, key)
    
    def __setitem__(self, key: str, value: Any) -> None:
        """Support dictionary-style setting: result['price'] = 150.0"""
        setattr(self, key, value)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Support dict.get() method: result.get('market_cap', 0.0)"""
        return getattr(self, key, default)
    
    def __contains__(self, key: str) -> bool:
        """Support 'in' operator: 'market_cap' in result"""
        return hasattr(self, key)
    
    def keys(self):
        """Return field names like dict.keys()"""
        return self.__dataclass_fields__.keys()
    
    def values(self):
        """Return field values like dict.values()"""
        return [getattr(self, k) for k in self.__dataclass_fields__.keys()]
    
    def items(self):
        """Return (key, value) pairs like dict.items()"""
        return [(k, getattr(self, k)) for k in self.__dataclass_fields__.keys()]


@dataclass
class StandardNewsArticle:
    """Standardized news article format.
    
    Supports both attribute and dictionary-style access:
        article.headline or article["headline"]
        article.symbols or article["symbols"]
    """
    id: str
    headline: str
    summary: Optional[str]
    content: Optional[str]
    symbols: List[str]
    published_at: str  # ISO 8601 format
    source: str
    url: Optional[str] = None
    
    def __getitem__(self, key: str) -> Any:
        """Support dictionary-style access: article['headline']"""
        return getattr(self, key)
    
    def __setitem__(self, key: str, value: Any) -> None:
        """Support dictionary-style setting: article['headline'] = 'New Headline'"""
        setattr(self, key, value)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Support dict.get() method: article.get('url', 'N/A')"""
        return getattr(self, key, default)
    
    def __contains__(self, key: str) -> bool:
        """Support 'in' operator: 'url' in article"""
        return hasattr(self, key)
    
    def keys(self):
        """Return field names like dict.keys()"""
        return self.__dataclass_fields__.keys()
    
    def values(self):
        """Return field values like dict.values()"""
        return [getattr(self, k) for k in self.__dataclass_fields__.keys()]
    
    def items(self):
        """Return (key, value) pairs like dict.items()"""
        return [(k, getattr(self, k)) for k in self.__dataclass_fields__.keys()]


@dataclass
class StandardFundamentals:
    """Standardized fundamental data format.
    
    Supports both attribute and dictionary-style access:
        fundamental.pe_ratio or fundamental["pe_ratio"]
        fundamental.market_cap or fundamental["market_cap"]
    """
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
    
    def __getitem__(self, key: str) -> Any:
        """Support dictionary-style access: fundamental['pe_ratio']"""
        return getattr(self, key)
    
    def __setitem__(self, key: str, value: Any) -> None:
        """Support dictionary-style setting: fundamental['pe_ratio'] = 20.5"""
        setattr(self, key, value)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Support dict.get() method: fundamental.get('market_cap', 0.0)"""
        return getattr(self, key, default)
    
    def __contains__(self, key: str) -> bool:
        """Support 'in' operator: 'pe_ratio' in fundamental"""
        return hasattr(self, key)
    
    def keys(self):
        """Return field names like dict.keys()"""
        return self.__dataclass_fields__.keys()
    
    def values(self):
        """Return field values like dict.values()"""
        return [getattr(self, k) for k in self.__dataclass_fields__.keys()]
    
    def items(self):
        """Return (key, value) pairs like dict.items()"""
        return [(k, getattr(self, k)) for k in self.__dataclass_fields__.keys()]


@dataclass
class StandardDividend:
    """Standardized dividend data format.
    
    Supports both attribute and dictionary-style access:
        dividend.amount or dividend["amount"]
        dividend.ex_date or dividend["ex_date"]
    """
    symbol: str
    ex_date: str       # ISO 8601 date: "2024-01-01"
    payment_date: str  # ISO 8601 date
    amount: float
    record_date: Optional[str] = None
    declaration_date: Optional[str] = None
    currency: str = "USD"
    
    def __getitem__(self, key: str) -> Any:
        """Support dictionary-style access: dividend['amount']"""
        return getattr(self, key)
    
    def __setitem__(self, key: str, value: Any) -> None:
        """Support dictionary-style setting: dividend['amount'] = 0.25"""
        setattr(self, key, value)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Support dict.get() method: dividend.get('record_date', 'N/A')"""
        return getattr(self, key, default)
    
    def __contains__(self, key: str) -> bool:
        """Support 'in' operator: 'record_date' in dividend"""
        return hasattr(self, key)
    
    def keys(self):
        """Return field names like dict.keys()"""
        return self.__dataclass_fields__.keys()
    
    def values(self):
        """Return field values like dict.values()"""
        return [getattr(self, k) for k in self.__dataclass_fields__.keys()]
    
    def items(self):
        """Return (key, value) pairs like dict.items()"""
        return [(k, getattr(self, k)) for k in self.__dataclass_fields__.keys()]


@dataclass
class StandardSplit:
    """Standardized stock split data format.
    
    Supports both attribute and dictionary-style access:
        split.ratio or split["ratio"]
        split.split_factor or split["split_factor"]
    """
    symbol: str
    date: str          # ISO 8601 date: "2024-01-01"
    ratio: str         # Format: "2:1", "3:2", etc.
    split_factor: float  # Numerical factor: 2.0, 1.5, etc.
    
    def __getitem__(self, key: str) -> Any:
        """Support dictionary-style access: split['ratio']"""
        return getattr(self, key)
    
    def __setitem__(self, key: str, value: Any) -> None:
        """Support dictionary-style setting: split['split_factor'] = 2.0"""
        setattr(self, key, value)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Support dict.get() method: split.get('ratio', '1:1')"""
        return getattr(self, key, default)
    
    def __contains__(self, key: str) -> bool:
        """Support 'in' operator: 'split_factor' in split"""
        return hasattr(self, key)
    
    def keys(self):
        """Return field names like dict.keys()"""
        return self.__dataclass_fields__.keys()
    
    def values(self):
        """Return field values like dict.values()"""
        return [getattr(self, k) for k in self.__dataclass_fields__.keys()]
    
    def items(self):
        """Return (key, value) pairs like dict.items()"""
        return [(k, getattr(self, k)) for k in self.__dataclass_fields__.keys()]  # Numerical factor: 2.0, 1.5, etc.


@dataclass
class StandardPosition:
    """Standardized position data format.
    
    Supports both attribute and dictionary-style access:
        position.quantity or position["quantity"]
        position.market_value or position["market_value"]
    """
    symbol: str
    quantity: float    # Positive for long, negative for short
    side: str         # "long" or "short"
    avg_entry_price: float
    current_price: float
    market_value: float
    cost_basis: float
    unrealized_pnl: float
    unrealized_pnl_percent: float
    
    def __getitem__(self, key: str) -> Any:
        """Support dictionary-style access: position['quantity']"""
        return getattr(self, key)
    
    def __setitem__(self, key: str, value: Any) -> None:
        """Support dictionary-style setting: position['market_value'] = 15000.0"""
        setattr(self, key, value)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Support dict.get() method: position.get('unrealized_pnl', 0.0)"""
        return getattr(self, key, default)
    
    def __contains__(self, key: str) -> bool:
        """Support 'in' operator: 'unrealized_pnl' in position"""
        return hasattr(self, key)
    
    def keys(self):
        """Return field names like dict.keys()"""
        return self.__dataclass_fields__.keys()
    
    def values(self):
        """Return field values like dict.values()"""
        return [getattr(self, k) for k in self.__dataclass_fields__.keys()]
    
    def items(self):
        """Return (key, value) pairs like dict.items()"""
        return [(k, getattr(self, k)) for k in self.__dataclass_fields__.keys()]


@dataclass
class StandardAccount:
    """Standardized account data format.
    
    Supports both attribute and dictionary-style access:
        account.cash or account["cash"]
        account.portfolio_value or account["portfolio_value"]
    """
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
    
    def __getitem__(self, key: str) -> Any:
        """Support dictionary-style access: account['cash']"""
        return getattr(self, key)
    
    def __setitem__(self, key: str, value: Any) -> None:
        """Support dictionary-style setting: account['cash'] = 50000.0"""
        setattr(self, key, value)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Support dict.get() method: account.get('initial_margin', 0.0)"""
        return getattr(self, key, default)
    
    def __contains__(self, key: str) -> bool:
        """Support 'in' operator: 'initial_margin' in account"""
        return hasattr(self, key)
    
    def keys(self):
        """Return field names like dict.keys()"""
        return self.__dataclass_fields__.keys()
    
    def values(self):
        """Return field values like dict.values()"""
        return [getattr(self, k) for k in self.__dataclass_fields__.keys()]
    
    def items(self):
        """Return (key, value) pairs like dict.items()"""
        return [(k, getattr(self, k)) for k in self.__dataclass_fields__.keys()]


@dataclass
class StandardOrder:
    """Standardized order data format.
    
    Supports both attribute and dictionary-style access:
        order.order_id or order["order_id"]
        order.status or order["status"]
    """
    order_id: str
    symbol: str
    side: str          # "buy" or "sell"
    order_type: str    # "market", "limit", "stop", etc.
    quantity: float
    filled_quantity: float
    status: str        # "new", "filled", "canceled", etc.
    created_at: str    # ISO 8601 format
    client_order_id: Optional[str] = None
    limit_price: Optional[float] = None
    stop_price: Optional[float] = None
    filled_avg_price: Optional[float] = None
    filled_at: Optional[str] = None
    
    def __getitem__(self, key: str) -> Any:
        """Support dictionary-style access: order['status']"""
        return getattr(self, key)
    
    def __setitem__(self, key: str, value: Any) -> None:
        """Support dictionary-style setting: order['status'] = 'filled'"""
        setattr(self, key, value)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Support dict.get() method: order.get('limit_price', 0.0)"""
        return getattr(self, key, default)
    
    def __contains__(self, key: str) -> bool:
        """Support 'in' operator: 'limit_price' in order"""
        return hasattr(self, key)
    
    def keys(self):
        """Return field names like dict.keys()"""
        return self.__dataclass_fields__.keys()
    
    def values(self):
        """Return field values like dict.values()"""
        return [getattr(self, k) for k in self.__dataclass_fields__.keys()]
    
    def items(self):
        """Return (key, value) pairs like dict.items()"""
        return [(k, getattr(self, k)) for k in self.__dataclass_fields__.keys()]


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