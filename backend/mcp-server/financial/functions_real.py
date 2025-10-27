"""
Generic Financial Data Functions - Vendor Independent Layer

This module provides vendor-independent financial data functions that work
with multiple data providers (Alpaca, EODHD) using standardized input/output formats.

All functions return data in consistent, standardized formats regardless of the
underlying vendor. Input parameters are also standardized - no vendor-specific
formatting required.

Key Features:
- Standardized symbol format: "AAPL" (no exchange suffixes)
- Consistent date format: "YYYY-MM-DD"
- Unified response structure with success/error handling
- Automatic vendor selection with fallback
- Data transformation between vendor formats
"""

import os
from typing import Dict, List, Any, Optional, Union
from .vendors import alpaca, eodhd
from .schemas import SymbolFormatter
from .transformers import (
    AlpacaTransformer, EODHDTransformer, 
    handle_vendor_error, ensure_standard_response
)


# Vendor availability check
ALPACA_AVAILABLE = bool(os.getenv('ALPACA_API_KEY') and os.getenv('ALPACA_SECRET_KEY'))
EODHD_AVAILABLE = bool(os.getenv('EODHD_API_KEY'))

# Default vendor preferences for different data types
DEFAULT_VENDORS = {
    'trading': 'alpaca',      # Trading operations only available via Alpaca
    'market_data': 'alpaca',  # Prefer Alpaca for market data
    'historical': 'eodhd',    # Prefer EODHD for historical data
    'fundamentals': 'eodhd',  # Fundamentals only available via EODHD
    'technical': 'eodhd',     # Technical indicators only available via EODHD
}


def _get_vendor(data_type: str, data_source: Optional[str] = None) -> str:
    """Determine which vendor to use for a given data type.
    
    Args:
        data_type: Type of data being requested (trading, market_data, etc.)
        data_source: Explicitly requested vendor ('alpaca' or 'eodhd')
        
    Returns:
        str: Vendor name to use
        
    Raises:
        ValueError: If no suitable vendor is available
    """
    if data_source:
        if data_source == 'alpaca' and not ALPACA_AVAILABLE:
            raise ValueError("Alpaca API credentials not configured")
        if data_source == 'eodhd' and not EODHD_AVAILABLE:
            raise ValueError("EODHD API credentials not configured")
        return data_source
    
    # Use default vendor for data type
    preferred = DEFAULT_VENDORS.get(data_type, 'alpaca')
    
    if preferred == 'alpaca' and ALPACA_AVAILABLE:
        return 'alpaca'
    elif preferred == 'eodhd' and EODHD_AVAILABLE:
        return 'eodhd'
    
    # Fall back to any available vendor
    if ALPACA_AVAILABLE:
        return 'alpaca'
    elif EODHD_AVAILABLE:
        return 'eodhd'
    
    raise ValueError("No financial data vendors configured")


# Generic Historical Data Functions
def get_historical_data(symbols: Union[str, List[str]], start_date: Optional[str] = None, end_date: Optional[str] = None, timeframe: str = "1Day", data_source: Optional[str] = None) -> Dict[str, Any]:
    """Retrieve historical OHLC price data with dividend and split adjustments.
    
    Fetches time-series price data including open, high, low, close, and volume
    for specified symbols across various timeframes. Data is automatically
    transformed to a standardized format regardless of the underlying vendor.
    
    Args:
        symbols: Stock symbol(s) in standard format. Can be a single symbol string
            (e.g., "AAPL") or a list of symbols (e.g., ["AAPL", "TSLA", "MSFT"]).
            No exchange suffixes required - use "AAPL" not "AAPL.US".
        start_date: Start date for historical data in 'YYYY-MM-DD' format.
            If None, defaults to vendor's default historical range (typically
            several years of data or as much as available).
        end_date: End date for historical data in 'YYYY-MM-DD' format.
            If None, defaults to most recent trading day.
        timeframe: Data frequency/granularity. Supported values:
            - "1Min", "5Min", "15Min", "30Min": Minute intervals
            - "1Hour": Hourly data
            - "1Day": Daily bars (default)
            - "1Week": Weekly bars
            - "1Month": Monthly bars
            Note: Higher frequency data may be limited to recent periods.
            
    Returns:
        Dict[str, Any]: Standardized response containing:
            - success (bool): True if request succeeded, False otherwise
            - data (Dict[str, List[StandardBar]]): Historical bars organized by symbol, where each symbol 
              maps to a list of OHLC bar objects, each containing:
                - timestamp: ISO 8601 formatted datetime string
                - symbol: Standard symbol format
                - open: Opening price for the period
                - high: Highest price during the period
                - low: Lowest price during the period
                - close: Closing price for the period
                - volume: Number of shares traded during the period
                - vwap: Volume weighted average price (if available)
                - trade_count: Number of individual trades (if available)
            - error (str or None): Error message if request failed, None on success
            
    Raises:
        ValueError: If data_source is specified but vendor is not configured,
            or if no vendors are available.
        
    Example:
        >>> # Get daily Apple data for the last month
        >>> response = get_historical_data("AAPL", "2024-01-01", "2024-01-31")
        >>> if response["success"]:
        ...     bars_by_symbol = response["data"]
        ...     aapl_bars = bars_by_symbol["AAPL"]
        ...     latest_bar = aapl_bars[-1]
        ...     print(f"Latest close: ${latest_bar.close}")
        ...     print(f"Volume: {latest_bar.volume:,}")
        
        >>> # Get hourly data for multiple stocks
        >>> response = get_historical_data(
        ...     ["AAPL", "TSLA"], 
        ...     "2024-01-15", 
        ...     "2024-01-15", 
        ...     "1Hour"
        ... )
        
    Note:
        - Requires appropriate API credentials (ALPACA_API_KEY/SECRET or EODHD_API_KEY)
        - Weekend and holiday dates are excluded from results
        - Adjusted close prices account for dividends and stock splits
        - EODHD preferred for historical data due to longer history availability
        - Alpaca provides more granular intraday data but with shorter history
    """
    try:
        vendor = _get_vendor('historical', data_source)
        symbol_list = [symbols] if isinstance(symbols, str) else symbols
        
        if vendor == 'eodhd':
            # Convert timeframe to EODHD period
            period_map = {"1Day": "d", "1Week": "w", "1Month": "m"}
            period = period_map.get(timeframe, "d")
            
            bars_by_symbol = {}
            for symbol in symbol_list:
                vendor_symbol = SymbolFormatter.from_standard(symbol, "eodhd")
                response = eodhd.get_eod_data(vendor_symbol, start_date, end_date, period, "a")
                
                if isinstance(response, dict) and "error" in response:
                    return ensure_standard_response(None, False, response["error"])
                
                bars = EODHDTransformer.transform_eod_data(response, symbol)
                # Merge symbol-organized bars into result dictionary
                bars_by_symbol.update(bars)
            
            return ensure_standard_response(bars_by_symbol)
            
        elif vendor == 'alpaca':
            vendor_symbols = [SymbolFormatter.from_standard(s, "alpaca") for s in symbol_list]
            response = alpaca.get_bars(vendor_symbols, timeframe, start_date, end_date)
            
            if isinstance(response, dict) and "error" in response:
                return ensure_standard_response(None, False, response["error"])
            
            bars = AlpacaTransformer.transform_bars(response, symbol_list)
            return ensure_standard_response(bars)
            
    except Exception as e:
        return ensure_standard_response(None, False, str(e))


def get_real_time_data(symbols: Union[str, List[str]], data_source: Optional[str] = None) -> Dict[str, Any]:
    """Fetch comprehensive real-time market snapshots with current pricing and trading data.
    
    Retrieves current market data including latest quotes, trades, and daily bars
    for each requested symbol. Provides complete market picture including current
    prices, spreads, volume, and trading activity.
    
    Args:
        symbols: Stock symbol(s) in standard format. Can be a single symbol string
            (e.g., "AAPL") or a list of symbols (e.g., ["AAPL", "TSLA", "SPY"]).
            No exchange suffixes required - use "AAPL" not "AAPL.US".
        data_source: Explicitly specify which vendor to use. Options:
            - None: Auto-select based on preferences (Alpaca preferred for real-time)
            - "alpaca": Force use of Alpaca Market Data API (recommended for real-time)
            - "eodhd": Force use of EODHD API (may have 15-20 min delays)
            If specified vendor is not configured, function will raise ValueError.
            
    Returns:
        Dict[str, Any]: Standardized response containing:
            - success (bool): True if request succeeded, False otherwise
            - data (Dict[str, StandardSnapshot]): Market snapshots organized by symbol, where each symbol 
              maps to a StandardSnapshot object containing:
                - symbol: Standard symbol format
                - timestamp: ISO 8601 formatted current timestamp
                - latest_trade: Most recent trade data (price, size, timestamp)
                - latest_quote: Current bid/ask quote (spread, sizes, timestamp)
                - daily_bar: Current day's OHLC data (open, high, low, close, volume)
                - previous_close: Previous trading day's closing price
            - error (str or None): Error message if request failed, None on success
            
    Raises:
        ValueError: If data_source is specified but vendor is not configured,
            or if no vendors are available.
        
    Example:
        >>> # Get real-time snapshots for tech stocks
        >>> response = get_real_time_data(["AAPL", "MSFT", "GOOGL"])
        >>> if response["success"]:
        ...     for snapshot in response["data"]:
        ...         if snapshot.latest_trade:
        ...             price = snapshot.latest_trade.price
        ...             print(f"{snapshot.symbol}: ${price:.2f}")
        ...         if snapshot.latest_quote:
        ...             spread = snapshot.latest_quote.ask_price - snapshot.latest_quote.bid_price
        ...             print(f"  Spread: ${spread:.2f}")
        
        >>> # Force use of specific vendor
        >>> response = get_real_time_data("SPY", data_source="alpaca")
        
    Note:
        - Requires appropriate API credentials (ALPACA_API_KEY/SECRET or EODHD_API_KEY)
        - Alpaca provides true real-time data during market hours
        - EODHD may have 15-20 minute delays for non-premium users
        - Outside market hours, returns previous close data
        - Market microstructure data useful for trading applications
    """
    try:
        vendor = _get_vendor('market_data', data_source)
        symbol_list = [symbols] if isinstance(symbols, str) else symbols
        
        if vendor == 'alpaca':
            vendor_symbols = [SymbolFormatter.from_standard(s, "alpaca") for s in symbol_list]
            response = alpaca.get_snapshots(vendor_symbols)
            
            if isinstance(response, dict) and "error" in response:
                return ensure_standard_response(None, False, response["error"])
            
            snapshots = AlpacaTransformer.transform_snapshots(response)
            return ensure_standard_response(snapshots)
            
        elif vendor == 'eodhd':
            snapshots = []
            for symbol in symbol_list:
                vendor_symbol = SymbolFormatter.from_standard(symbol, "eodhd")
                response = eodhd.get_real_time(vendor_symbol)
                
                if isinstance(response, dict) and "error" in response:
                    return ensure_standard_response(None, False, response["error"])
                
                snapshot = EODHDTransformer.transform_real_time(response, symbol)
                snapshots.append(snapshot)
            
            return ensure_standard_response(snapshots)
            
    except Exception as e:
        return ensure_standard_response(None, False, str(e))


def get_latest_quotes(symbols: Union[str, List[str]], data_source: Optional[str] = None) -> Dict[str, Any]:
    """Retrieve latest bid/ask quotes with market depth information.
    
    Fetches current market maker quotes including best bid/ask prices and sizes.
    Essential for understanding current market depth, spread analysis, and
    optimal order placement strategies. Provides real-time level 1 market data.
    
    Args:
        symbols: Stock symbol(s) in standard format. Can be a single symbol string
            (e.g., "AAPL") or a list of symbols (e.g., ["AAPL", "TSLA", "SPY"]).
            No exchange suffixes required - use "AAPL" not "AAPL.US".
        data_source: Explicitly specify which vendor to use. Options:
            - None: Auto-select based on preferences (Alpaca preferred for quotes)
            - "alpaca": Force use of Alpaca Market Data API (only option for quotes)
            - "eodhd": Not supported - quotes not available via EODHD
            If specified vendor is not configured, function will raise ValueError.
            
    Returns:
        Dict[str, Any]: Standardized response containing:
            - success (bool): True if request succeeded, False otherwise
            - data (Dict[str, StandardQuote]): Current quotes organized by symbol, where each symbol 
              maps to a StandardQuote object containing:
                - timestamp: ISO 8601 formatted quote timestamp
                - symbol: Standard symbol format
                - bid_price: Best bid price (highest price buyers willing to pay)
                - bid_size: Number of shares available at bid price
                - ask_price: Best ask price (lowest price sellers willing to accept)
                - ask_size: Number of shares available at ask price
            - error (str or None): Error message if request failed, None on success
            
    Raises:
        ValueError: If data_source is specified but vendor is not configured,
            if EODHD is requested (not supported), or if no vendors are available.
        
    Example:
        >>> # Get current bid/ask spreads for major stocks
        >>> response = get_latest_quotes(["AAPL", "MSFT", "GOOGL"])
        >>> if response["success"]:
        ...     for quote in response["data"]:
        ...         spread = quote.ask_price - quote.bid_price
        ...         mid_price = (quote.bid_price + quote.ask_price) / 2
        ...         print(f"{quote.symbol}:")
        ...         print(f"  Bid: ${quote.bid_price:.2f} x {quote.bid_size:,}")
        ...         print(f"  Ask: ${quote.ask_price:.2f} x {quote.ask_size:,}")
        ...         print(f"  Spread: ${spread:.2f} Mid: ${mid_price:.2f}")
        
        >>> # Check if market is liquid (tight spreads)
        >>> response = get_latest_quotes("SPY")
        >>> if response["success"] and response["data"]:
        ...     quote = response["data"][0]
        ...     spread_bps = (quote.ask_price - quote.bid_price) / quote.bid_price * 10000
        ...     print(f"SPY spread: {spread_bps:.1f} basis points")
        
    Note:
        - Requires Alpaca API credentials (ALPACA_API_KEY and ALPACA_SECRET_KEY)
        - Quotes updated continuously during market hours
        - Spread width indicates market liquidity (tighter = more liquid)
        - Use mid-price for fair value estimates
        - Quote sizes show market depth at best prices
        - Currently only available through Alpaca vendor
    """
    try:
        vendor = _get_vendor('market_data', data_source)
        symbol_list = [symbols] if isinstance(symbols, str) else symbols
        
        if vendor == 'alpaca':
            vendor_symbols = [SymbolFormatter.from_standard(s, "alpaca") for s in symbol_list]
            response = alpaca.get_quotes_latest(vendor_symbols)
            
            if isinstance(response, dict) and "error" in response:
                return ensure_standard_response(None, False, response["error"])
            
            quotes = AlpacaTransformer.transform_quotes(response)
            return ensure_standard_response(quotes)
        else:
            return ensure_standard_response(None, False, f"Latest quotes not available for vendor: {vendor}")
            
    except Exception as e:
        return ensure_standard_response(None, False, str(e))


def get_latest_trades(symbols: Union[str, List[str]], data_source: Optional[str] = None) -> Dict[str, Any]:
    """Retrieve latest trade execution data showing actual transaction prices.
    
    Fetches most recent trade transactions showing actual execution prices
    and volumes. Essential for understanding current market prices, recent
    trading activity patterns, and actual execution levels for price discovery.
    
    Args:
        symbols: Stock symbol(s) in standard format. Can be a single symbol string
            (e.g., "AAPL") or a list of symbols (e.g., ["AAPL", "TSLA", "SPY"]).
            No exchange suffixes required - use "AAPL" not "AAPL.US".
        data_source: Explicitly specify which vendor to use. Options:
            - None: Auto-select based on preferences (Alpaca preferred for trades)
            - "alpaca": Force use of Alpaca Market Data API (only option for trades)
            - "eodhd": Not supported - latest trades not available via EODHD
            If specified vendor is not configured, function will raise ValueError.
            
    Returns:
        Dict[str, Any]: Standardized response containing:
            - success (bool): True if request succeeded, False otherwise
            - data (Dict[str, StandardTrade]): Latest trades organized by symbol, where each symbol 
              maps to a StandardTrade object containing:
                - timestamp: ISO 8601 formatted trade execution timestamp
                - symbol: Standard symbol format
                - price: Actual execution price per share
                - size: Number of shares executed in the trade
                - exchange: Exchange where trade occurred (if available)
            - error (str or None): Error message if request failed, None on success
            
    Raises:
        ValueError: If data_source is specified but vendor is not configured,
            if EODHD is requested (not supported), or if no vendors are available.
        
    Example:
        >>> # Get latest trade prices for portfolio positions
        >>> response = get_latest_trades(["AAPL", "MSFT", "TSLA"])
        >>> if response["success"]:
        ...     for trade in response["data"]:
        ...         value = trade.price * trade.size
        ...         print(f"{trade.symbol} Latest Trade:")
        ...         print(f"  Price: ${trade.price:.2f}")
        ...         print(f"  Size: {trade.size:,} shares")
        ...         print(f"  Value: ${value:,.2f}")
        ...         print(f"  Time: {trade.timestamp}")
        
        >>> # Check for large institutional trades
        >>> response = get_latest_trades("SPY")
        >>> if response["success"] and response["data"]:
        ...     trade = response["data"][0]
        ...     if trade.size > 100000:  # 100k+ shares
        ...         print(f"Large trade detected: {trade.size:,} shares")
        
    Note:
        - Requires Alpaca API credentials (ALPACA_API_KEY and ALPACA_SECRET_KEY)
        - Trade prices represent actual execution levels (more accurate than quotes)
        - Large trades may indicate institutional activity or news-driven moves
        - Use for current price discovery and market timing analysis
        - Trade timestamps show exact execution time
        - Currently only available through Alpaca vendor
    """
    try:
        vendor = _get_vendor('market_data', data_source)
        symbol_list = [symbols] if isinstance(symbols, str) else symbols
        
        if vendor == 'alpaca':
            vendor_symbols = [SymbolFormatter.from_standard(s, "alpaca") for s in symbol_list]
            response = alpaca.get_trades_latest(vendor_symbols)
            
            if isinstance(response, dict) and "error" in response:
                return ensure_standard_response(None, False, response["error"])
            
            trades = AlpacaTransformer.transform_trades(response)
            return ensure_standard_response(trades)
        else:
            return ensure_standard_response(None, False, f"Latest trades not available for vendor: {vendor}")
            
    except Exception as e:
        return ensure_standard_response(None, False, str(e))


# Generic Screening Functions
def get_most_active_stocks(limit: int = 10, data_source: Optional[str] = None) -> Dict[str, Any]:
    """Screen for most actively traded stocks by volume to identify market interest.
    
    Identifies stocks with highest trading volume for the current or most recent
    trading session. High volume often indicates significant news, earnings,
    institutional activity, or momentum that's driving increased interest and
    potential trading opportunities.
    
    Args:
        limit: Maximum number of most active stocks to return. Range typically 1-50.
            Defaults to 10. Larger values may take longer to process but provide
            broader market coverage.
        data_source: Explicitly specify which vendor to use. Options:
            - None: Auto-select based on preferences (Alpaca preferred for screening)
            - "alpaca": Force use of Alpaca Market Data API (recommended)
            - "eodhd": Force use of EODHD screener API
            If specified vendor is not configured, function will raise ValueError.
            
    Returns:
        Dict[str, Any]: Standardized response containing:
            - success (bool): True if request succeeded, False otherwise
            - data (List[StandardScreenerResult]): List of active stocks, each containing:
                - symbol: Standard symbol format
                - name: Company name
                - price: Current stock price
                - change: Absolute price change from previous close
                - change_percent: Percentage change from previous close
                - volume: Current day trading volume
                - market_cap: Market capitalization (if available)
            - error (str or None): Error message if request failed, None on success
            
    Raises:
        ValueError: If data_source is specified but vendor is not configured,
            or if no vendors are available.
        
    Example:
        >>> # Find today's most active stocks for momentum trading
        >>> response = get_most_active_stocks(20)
        >>> if response["success"]:
        ...     stocks = response["data"]
        ...     print(f"Top {len(stocks)} Most Active Stocks:")
        ...     for stock in stocks:
        ...         volume_millions = stock.volume / 1_000_000
        ...         print(f"{stock.symbol}: {volume_millions:.1f}M shares")
        ...         print(f"  Price: ${stock.price:.2f} ({stock.change_percent:+.2f}%)")
        ...         print(f"  Company: {stock.name}")
        
        >>> # Check if unusual volume indicates news or events
        >>> response = get_most_active_stocks(5, data_source="alpaca")
        >>> if response["success"]:
        ...     for stock in response["data"]:
        ...         if abs(stock.change_percent) > 5:  # 5%+ move
        ...             print(f"{stock.symbol} showing unusual activity: {stock.change_percent:+.1f}%")
        
    Note:
        - Requires appropriate API credentials (ALPACA_API_KEY/SECRET or EODHD_API_KEY)
        - Volume data reflects current or most recent trading session
        - High volume may indicate breakout opportunities or news-driven moves
        - Useful for momentum strategies and trend identification
        - Data updated throughout trading day during market hours
        - Consider combining with price change analysis for better insights
    """
    try:
        vendor = _get_vendor('market_data', data_source)
        
        if vendor == 'alpaca':
            response = alpaca.get_most_actives(limit)
            
            if isinstance(response, dict) and "error" in response:
                return ensure_standard_response(None, False, response["error"])
            
            results = AlpacaTransformer.transform_screener(response, "most_actives")
            return ensure_standard_response(results)
            
        elif vendor == 'eodhd':
            response = eodhd.get_screener(filters="", limit=limit, signals="high_volume")
            
            if isinstance(response, dict) and "error" in response:
                return ensure_standard_response(None, False, response["error"])
            
            results = EODHDTransformer.transform_screener(response)
            return ensure_standard_response(results)
            
    except Exception as e:
        return ensure_standard_response(None, False, str(e))


def get_top_gainers(limit: int = 10, data_source: Optional[str] = None) -> Dict[str, Any]:
    """Screen for stocks with biggest percentage gains to identify momentum opportunities.
    
    Identifies stocks with highest percentage price increases for the current
    or most recent trading session. Useful for momentum strategies, breakout
    detection, and identifying stocks benefiting from positive news, earnings
    beats, or favorable market sentiment.
    
    Args:
        limit: Maximum number of top gaining stocks to return. Range typically 1-50.
            Defaults to 10. Larger values may include progressively smaller gains
            but provide broader market coverage for screening.
        data_source: Explicitly specify which vendor to use. Options:
            - None: Auto-select based on preferences (Alpaca preferred for screening)
            - "alpaca": Force use of Alpaca Market Data API (recommended)
            - "eodhd": Force use of EODHD screener API
            If specified vendor is not configured, function will raise ValueError.
            
    Returns:
        Dict[str, Any]: Standardized response containing:
            - success (bool): True if request succeeded, False otherwise
            - data (List[StandardScreenerResult]): List of gaining stocks, each containing:
                - symbol: Standard symbol format
                - name: Company name
                - price: Current stock price
                - change: Absolute price change in dollars from previous close
                - change_percent: Percentage gain from previous close
                - volume: Trading volume for the session
                - market_cap: Market capitalization (if available)
            - error (str or None): Error message if request failed, None on success
            
    Raises:
        ValueError: If data_source is specified but vendor is not configured,
            or if no vendors are available.
        
    Example:
        >>> # Find today's biggest winners for momentum trading
        >>> response = get_top_gainers(15)
        >>> if response["success"]:
        ...     stocks = response["data"]
        ...     print(f"Top {len(stocks)} Gaining Stocks:")
        ...     for stock in stocks:
        ...         print(f"{stock.symbol}: {stock.name}")
        ...         print(f"  Gain: +{stock.change_percent:.2f}% (+${stock.change:.2f})")
        ...         print(f"  Price: ${stock.price:.2f}")
        ...         print(f"  Volume: {stock.volume:,}")
        
        >>> # Identify potential breakout candidates
        >>> response = get_top_gainers(20, data_source="alpaca")
        >>> if response["success"]:
        ...     for stock in response["data"]:
        ...         if stock.change_percent > 10 and stock.volume > 1000000:
        ...             print(f"{stock.symbol}: Potential breakout candidate")
        ...             print(f"  Gain: {stock.change_percent:.1f}% on {stock.volume:,} volume")
        
    Note:
        - Requires appropriate API credentials (ALPACA_API_KEY/SECRET or EODHD_API_KEY)
        - Percentage changes calculated from previous trading day close
        - High gains may indicate momentum or news-driven moves
        - Useful for identifying breakout candidates and trend followers
        - Consider volume confirmation for validating strength of moves
        - May include penny stocks or low-float stocks with exaggerated moves
    """
    try:
        vendor = _get_vendor('market_data', data_source)
        
        if vendor == 'alpaca':
            response = alpaca.get_top_gainers(limit)
            
            if isinstance(response, dict) and "error" in response:
                return ensure_standard_response(None, False, response["error"])
            
            results = AlpacaTransformer.transform_screener(response, "top_gainers")
            return ensure_standard_response(results)
            
        elif vendor == 'eodhd':
            response = eodhd.get_screener(filters="", limit=limit, signals="top_gainers")
            
            if isinstance(response, dict) and "error" in response:
                return ensure_standard_response(None, False, response["error"])
            
            results = EODHDTransformer.transform_screener(response)
            return ensure_standard_response(results)
            
    except Exception as e:
        return ensure_standard_response(None, False, str(e))


def get_top_losers(limit: int = 10, data_source: Optional[str] = None) -> Dict[str, Any]:
    """Screen for stocks with biggest percentage losses to identify oversold opportunities.
    
    Identifies stocks with largest percentage price decreases for the current
    or most recent trading session. Useful for contrarian strategies, oversold
    opportunity identification, risk monitoring, and identifying stocks affected
    by negative news or market sentiment.
    
    Args:
        limit: Maximum number of top losing stocks to return. Range typically 1-50.
            Defaults to 10. Larger values may include progressively smaller losses
            but provide broader market coverage for screening.
        data_source: Explicitly specify which vendor to use. Options:
            - None: Auto-select based on preferences (Alpaca preferred for screening)
            - "alpaca": Force use of Alpaca Market Data API (recommended)
            - "eodhd": Force use of EODHD screener API
            If specified vendor is not configured, function will raise ValueError.
            
    Returns:
        Dict[str, Any]: Standardized response containing:
            - success (bool): True if request succeeded, False otherwise
            - data (List[StandardScreenerResult]): List of losing stocks, each containing:
                - symbol: Standard symbol format
                - name: Company name
                - price: Current stock price
                - change: Absolute price change in dollars from previous close (negative)
                - change_percent: Percentage loss from previous close (negative)
                - volume: Trading volume for the session
                - market_cap: Market capitalization (if available)
            - error (str or None): Error message if request failed, None on success
            
    Raises:
        ValueError: If data_source is specified but vendor is not configured,
            or if no vendors are available.
        
    Example:
        >>> # Find today's biggest losers for contrarian analysis
        >>> response = get_top_losers(15)
        >>> if response["success"]:
        ...     stocks = response["data"]
        ...     print(f"Top {len(stocks)} Losing Stocks:")
        ...     for stock in stocks:
        ...         print(f"{stock.symbol}: {stock.name}")
        ...         print(f"  Loss: {stock.change_percent:.2f}% (${stock.change:.2f})")
        ...         print(f"  Price: ${stock.price:.2f}")
        ...         print(f"  Volume: {stock.volume:,}")
        
        >>> # Identify potential oversold opportunities
        >>> response = get_top_losers(20, data_source="alpaca")
        >>> if response["success"]:
        ...     for stock in response["data"]:
        ...         if stock.change_percent < -10 and stock.volume > 500000:
        ...             print(f"{stock.symbol}: Potential oversold opportunity")
        ...             print(f"  Loss: {stock.change_percent:.1f}% on {stock.volume:,} volume")
        
    Note:
        - Requires appropriate API credentials (ALPACA_API_KEY/SECRET or EODHD_API_KEY)
        - Percentage changes calculated from previous trading day close
        - Large losses may indicate oversold opportunities or fundamental issues
        - Useful for contrarian strategies and value opportunity identification
        - Consider reasons for decline before assuming oversold conditions
        - High volume on decline may indicate more selling pressure ahead
        - Always research fundamentals before treating as buying opportunity
    """
    try:
        vendor = _get_vendor('market_data', data_source)
        
        if vendor == 'alpaca':
            response = alpaca.get_top_losers(limit)
            
            if isinstance(response, dict) and "error" in response:
                return ensure_standard_response(None, False, response["error"])
            
            results = AlpacaTransformer.transform_screener(response, "top_losers")
            return ensure_standard_response(results)
            
        elif vendor == 'eodhd':
            response = eodhd.get_screener(filters="", limit=limit, signals="top_losers")
            
            if isinstance(response, dict) and "error" in response:
                return ensure_standard_response(None, False, response["error"])
            
            results = EODHDTransformer.transform_screener(response)
            return ensure_standard_response(results)
            
    except Exception as e:
        return ensure_standard_response(None, False, str(e))


def get_market_news(symbols: List[str] = [], start_date: Optional[str] = None, end_date: Optional[str] = None, limit: int = 50, data_source: Optional[str] = None) -> Dict[str, Any]:
    """Retrieve financial news articles and market information for analysis and research.
    
    Fetches relevant financial news articles filtered by symbols, date ranges,
    and other criteria. Essential for fundamental analysis, sentiment tracking,
    staying informed about market-moving events, and understanding factors
    driving stock price movements.
    
    Args:
        symbols: List of stock symbols in standard format to filter news.
            Examples: ["AAPL", "TSLA", "MSFT"]. If empty list, returns general
            market news without symbol filtering. No exchange suffixes required.
        start_date: Start date for news articles in 'YYYY-MM-DD' format.
            If None, returns recent news without date filtering (typically
            last few days depending on vendor).
        end_date: End date for news articles in 'YYYY-MM-DD' format.
            If None, includes news up to current date.
        limit: Maximum number of articles to return. Defaults to 50.
            Range typically 1-1000 depending on API subscription and vendor.
        data_source: Explicitly specify which vendor to use. Options:
            - None: Auto-select based on preferences (Alpaca preferred for news)
            - "alpaca": Force use of Alpaca Market Data API (only option for news)
            - "eodhd": Not supported - news not available via EODHD
            If specified vendor is not configured, function will raise ValueError.
            
    Returns:
        Dict[str, Any]: Standardized response containing:
            - success (bool): True if request succeeded, False otherwise
            - data (List[StandardNewsArticle]): List of news articles, each containing:
                - id: Unique article identifier
                - headline: Article headline/title
                - summary: Brief article summary (if available)
                - content: Full article content (if available)
                - symbols: List of related stock symbols mentioned
                - published_at: Publication timestamp in ISO 8601 format
                - source: News source/publisher
                - url: Original article URL (if available)
            - error (str or None): Error message if request failed, None on success
            
    Raises:
        ValueError: If data_source is specified but vendor is not configured,
            if EODHD is requested (not supported), or if no vendors are available.
        
    Example:
        >>> # Get recent Apple news for fundamental analysis
        >>> response = get_market_news(["AAPL"], start_date="2024-01-01", limit=10)
        >>> if response["success"]:
        ...     articles = response["data"]
        ...     print(f"Found {len(articles)} Apple articles:")
        ...     for article in articles:
        ...         symbols = ', '.join(article.symbols)
        ...         print(f"Headline: {article.headline}")
        ...         print(f"Source: {article.source}")
        ...         print(f"Symbols: {symbols}")
        ...         print(f"Published: {article.published_at}")
        ...         print()
        
        >>> # Get general market news
        >>> response = get_market_news([], limit=5)
        >>> if response["success"]:
        ...     for article in response["data"]:
        ...         print(f"{article.headline} - {article.source}")
        
    Note:
        - Requires Alpaca API credentials (ALPACA_API_KEY and ALPACA_SECRET_KEY)
        - News articles updated continuously throughout trading day
        - Symbol filtering helps focus on relevant company-specific news
        - Full content useful for sentiment analysis and detailed research
        - Consider rate limits when requesting large date ranges
        - Currently only available through Alpaca vendor
        - Article content may be truncated depending on source and subscription
    """
    try:
        vendor = _get_vendor('market_data', data_source)
        
        if vendor == 'alpaca':
            vendor_symbols = [SymbolFormatter.from_standard(s, "alpaca") for s in symbols]
            response = alpaca.get_news(vendor_symbols, start_date, end_date, "desc", True)
            
            if isinstance(response, dict) and "error" in response:
                return ensure_standard_response(None, False, response["error"])
            
            articles = AlpacaTransformer.transform_news(response)
            return ensure_standard_response(articles[:limit])
        else:
            return ensure_standard_response(None, False, f"News not available for vendor: {vendor}")
            
    except Exception as e:
        return ensure_standard_response(None, False, str(e))


# Generic Fundamental Data Functions
def get_fundamentals(symbol: str, data_source: Optional[str] = None) -> Dict[str, Any]:
    """Retrieve comprehensive company fundamental data and financial metrics.
    
    Fetches detailed fundamental information including company profile,
    financial statements, valuation ratios, and key business metrics.
    Essential for fundamental analysis, stock valuation, and investment
    research to understand company health and value.
    
    Args:
        symbol: Stock symbol in standard format (e.g., "AAPL", "TSLA", "MSFT").
            No exchange suffixes required - use "AAPL" not "AAPL.US".
        data_source: Explicitly specify which vendor to use. Options:
            - None: Auto-select based on preferences (EODHD preferred for fundamentals)
            - "eodhd": Force use of EODHD API (only option for fundamentals)
            - "alpaca": Not supported - fundamentals not available via Alpaca
            If specified vendor is not configured, function will raise ValueError.
            
    Returns:
        Dict[str, Any]: Standardized response containing:
            - success (bool): True if request succeeded, False otherwise
            - data (StandardFundamentals): Fundamental data object containing:
                - symbol: Standard symbol format
                - company_name: Full company name
                - sector: Business sector (e.g., "Technology", "Healthcare")
                - industry: Specific industry classification
                - market_cap: Market capitalization in dollars
                - pe_ratio: Price-to-earnings ratio
                - pb_ratio: Price-to-book ratio
                - dividend_yield: Annual dividend yield as decimal
                - eps: Earnings per share (trailing twelve months)
                - revenue: Total revenue (trailing twelve months)
                - shares_outstanding: Number of shares outstanding
            - error (str or None): Error message if request failed, None on success
            
    Raises:
        ValueError: If data_source is specified but vendor is not configured,
            if Alpaca is requested (not supported), or if no vendors are available.
        
    Example:
        >>> # Analyze Apple's fundamental metrics
        >>> response = get_fundamentals("AAPL")
        >>> if response["success"]:
        ...     fund = response["data"]
        ...     print(f"Company: {fund.company_name}")
        ...     print(f"Sector: {fund.sector}")
        ...     print(f"Market Cap: ${fund.market_cap:,.0f}")
        ...     print(f"P/E Ratio: {fund.pe_ratio:.1f}")
        ...     print(f"Dividend Yield: {fund.dividend_yield:.2%}")
        ...     
        ...     # Value analysis
        ...     if fund.pe_ratio and fund.pe_ratio < 15:
        ...         print("Potentially undervalued based on P/E")
        ...     if fund.dividend_yield and fund.dividend_yield > 0.03:
        ...         print("Good dividend yield for income investing")
        
        >>> # Compare multiple stocks
        >>> symbols = ["AAPL", "MSFT", "GOOGL"]
        >>> for symbol in symbols:
        ...     response = get_fundamentals(symbol, data_source="eodhd")
        ...     if response["success"]:
        ...         fund = response["data"]
        ...         print(f"{symbol}: P/E={fund.pe_ratio:.1f}, Yield={fund.dividend_yield:.2%}")
        
    Note:
        - Requires EODHD API credentials (EODHD_API_KEY)
        - Data updated daily after market close
        - Some fields may be null for certain symbols or exchanges
        - Financial data typically covers last 4 quarters and 4 years
        - Currently only available through EODHD vendor
        - Use for stock screening, valuation analysis, and investment research
    """
    try:
        vendor = _get_vendor('fundamentals', data_source)
        
        if vendor == 'eodhd':
            vendor_symbol = SymbolFormatter.from_standard(symbol, "eodhd")
            response = eodhd.get_fundamentals(vendor_symbol)
            
            if isinstance(response, dict) and "error" in response:
                return ensure_standard_response(None, False, response["error"])
            
            fundamentals = EODHDTransformer.transform_fundamentals(response, symbol)
            return ensure_standard_response(fundamentals)
        else:
            return ensure_standard_response(None, False, f"Fundamentals not available for vendor: {vendor}")
            
    except Exception as e:
        return ensure_standard_response(None, False, str(e))


def get_dividends(symbol: str, start_date: Optional[str] = None, end_date: Optional[str] = None, data_source: Optional[str] = None) -> Dict[str, Any]:
    """Retrieve historical dividend payment data with important dates for income analysis.
    
    Fetches comprehensive dividend history including payment amounts,
    ex-dividend dates, record dates, and payment dates. Essential for income
    analysis, dividend yield calculations, and understanding dividend policy
    changes over time.
    
    Args:
        symbol: Stock symbol in standard format (e.g., "AAPL", "KO", "JNJ").
            No exchange suffixes required - use "AAPL" not "AAPL.US".
        start_date: Start date for dividend history in 'YYYY-MM-DD' format.
            If None, returns all available dividend history (typically several years).
        end_date: End date for dividend history in 'YYYY-MM-DD' format.
            If None, includes dividends up to present date.
        data_source: Explicitly specify which vendor to use. Options:
            - None: Auto-select based on preferences (EODHD preferred for dividends)
            - "eodhd": Force use of EODHD API (only option for dividends)
            - "alpaca": Not supported - dividend history not available via Alpaca
            If specified vendor is not configured, function will raise ValueError.
            
    Returns:
        Dict[str, Any]: Standardized response containing:
            - success (bool): True if request succeeded, False otherwise
            - data (List[StandardDividend]): List of dividend records, each containing:
                - symbol: Standard symbol format
                - ex_date: Ex-dividend date (when stock trades without dividend)
                - payment_date: Actual dividend payment date
                - record_date: Date of record for dividend eligibility
                - declaration_date: Date dividend was announced
                - amount: Dividend amount per share
                - currency: Currency of dividend payment
            - error (str or None): Error message if request failed, None on success
            
    Raises:
        ValueError: If data_source is specified but vendor is not configured,
            if Alpaca is requested (not supported), or if no vendors are available.
        
    Example:
        >>> # Analyze Apple's dividend history for income investing
        >>> response = get_dividends("AAPL", start_date="2023-01-01", end_date="2023-12-31")
        >>> if response["success"]:
        ...     dividends = response["data"]
        ...     total_dividends = sum(d.amount for d in dividends)
        ...     print(f"Total 2023 dividends: ${total_dividends:.2f} per share")
        ...     print(f"Number of payments: {len(dividends)}")
        ...     
        ...     for div in dividends:
        ...         print(f"{div.ex_date}: ${div.amount:.3f} (Ex-Date)")
        ...         print(f"  Payment Date: {div.payment_date}")
        
        >>> # Calculate dividend growth rate
        >>> response = get_dividends("JNJ", start_date="2020-01-01")
        >>> if response["success"]:
        ...     dividends = response["data"]
        ...     yearly_totals = {}
        ...     for div in dividends:
        ...         year = div.ex_date[:4]
        ...         yearly_totals[year] = yearly_totals.get(year, 0) + div.amount
        ...     
        ...     for year, total in sorted(yearly_totals.items()):
        ...         print(f"{year}: ${total:.2f} annual dividend")
        
    Note:
        - Requires EODHD API credentials (EODHD_API_KEY)
        - Ex-dividend date is when stock price typically drops by dividend amount
        - Record date determines eligibility (must own stock by this date)
        - Payment date is when dividend is actually deposited
        - Includes special dividends and regular quarterly payments
        - Currently only available through EODHD vendor
        - Essential for dividend growth investing and income analysis
    """
    try:
        vendor = _get_vendor('fundamentals', data_source)
        
        if vendor == 'eodhd':
            vendor_symbol = SymbolFormatter.from_standard(symbol, "eodhd")
            response = eodhd.get_dividends(vendor_symbol, start_date, end_date)
            
            if isinstance(response, dict) and "error" in response:
                return ensure_standard_response(None, False, response["error"])
            
            dividends = EODHDTransformer.transform_dividends(response, symbol)
            return ensure_standard_response(dividends)
        else:
            return ensure_standard_response(None, False, f"Dividends not available for vendor: {vendor}")
            
    except Exception as e:
        return ensure_standard_response(None, False, str(e))


def get_splits(symbol: str, start_date: Optional[str] = None, end_date: Optional[str] = None, data_source: Optional[str] = None) -> Dict[str, Any]:
    """Retrieve historical stock split data with split ratios for accurate price adjustments.
    
    Fetches complete stock split history including split ratios and dates,
    essential for adjusting historical price data and calculating accurate
    returns across split events. Critical for backtesting and performance
    analysis to account for corporate actions.
    
    Args:
        symbol: Stock symbol in standard format (e.g., "AAPL", "TSLA", "NVDA").
            No exchange suffixes required - use "AAPL" not "AAPL.US".
        start_date: Start date for split history in 'YYYY-MM-DD' format.
            If None, returns all available split history (typically several years).
        end_date: End date for split history in 'YYYY-MM-DD' format.
            If None, includes splits up to present date.
        data_source: Explicitly specify which vendor to use. Options:
            - None: Auto-select based on preferences (EODHD preferred for splits)
            - "eodhd": Force use of EODHD API (only option for splits)
            - "alpaca": Not supported - split history not available via Alpaca
            If specified vendor is not configured, function will raise ValueError.
            
    Returns:
        Dict[str, Any]: Standardized response containing:
            - success (bool): True if request succeeded, False otherwise
            - data (List[StandardSplit]): List of split records, each containing:
                - symbol: Standard symbol format
                - date: Effective date of the stock split
                - ratio: Split ratio in format 'new:old' (e.g., '2:1', '3:2')
                - split_factor: Numerical split multiplier (e.g., 2.0, 1.5)
            - error (str or None): Error message if request failed, None on success
            
    Raises:
        ValueError: If data_source is specified but vendor is not configured,
            if Alpaca is requested (not supported), or if no vendors are available.
        
    Example:
        >>> # Check Apple's recent stock splits for price adjustment
        >>> response = get_splits("AAPL", start_date="2020-01-01")
        >>> if response["success"]:
        ...     splits = response["data"]
        ...     print(f"Found {len(splits)} stock splits since 2020:")
        ...     for split in splits:
        ...         print(f"{split.date}: {split.ratio} split (factor: {split.split_factor}x)")
        ...         print(f"  Price adjustment: divide by {split.split_factor}")
        
        >>> # Calculate cumulative split adjustment since specific date
        >>> response = get_splits("NVDA", start_date="2021-01-01")
        >>> if response["success"]:
        ...     splits = response["data"]
        ...     cumulative_factor = 1.0
        ...     for split in splits:
        ...         cumulative_factor *= split.split_factor
        ...     print(f"Cumulative split factor since 2021: {cumulative_factor}x")
        ...     print(f"$100 pre-split = ${100 * cumulative_factor:.2f} post-split")
        
    Note:
        - Requires EODHD API credentials (EODHD_API_KEY)
        - Split ratios show new shares to old shares relationship
        - 2:1 split means each old share becomes 2 new shares
        - Stock price adjusts inversely to split ratio on split date
        - Essential for calculating adjusted historical returns
        - Currently only available through EODHD vendor
        - Use for backtesting and performance analysis accuracy
    """
    try:
        vendor = _get_vendor('fundamentals', data_source)
        
        if vendor == 'eodhd':
            vendor_symbol = SymbolFormatter.from_standard(symbol, "eodhd")
            response = eodhd.get_splits(vendor_symbol, start_date, end_date)
            
            if isinstance(response, dict) and "error" in response:
                return ensure_standard_response(None, False, response["error"])
            
            splits = EODHDTransformer.transform_splits(response, symbol)
            return ensure_standard_response(splits)
        else:
            return ensure_standard_response(None, False, f"Splits not available for vendor: {vendor}")
            
    except Exception as e:
        return ensure_standard_response(None, False, str(e))


# Generic Trading Functions
def get_account(data_source: Optional[str] = None) -> Dict[str, Any]:
    """Retrieve comprehensive trading account information and balances.
    
    Fetches current account status, buying power, equity positions,
    cash balances, and margin information. Essential for portfolio
    management, risk assessment, and understanding available capital
    for trading activities.
    
    Args:
        data_source: Explicitly specify which vendor to use. Options:
            - None: Auto-select based on preferences (Alpaca preferred for trading)
            - "alpaca": Force use of Alpaca Trading API (only option for trading)
            - "eodhd": Not supported - trading account not available via EODHD
            If specified vendor is not configured, function will raise ValueError.
            
    Returns:
        Dict[str, Any]: Standardized response containing:
            - success (bool): True if request succeeded, False otherwise
            - data (StandardAccount): Account information object containing:
                - account_id: Unique account identifier
                - status: Account status ("ACTIVE", "SUSPENDED", etc.)
                - currency: Base account currency (typically "USD")
                - cash: Available cash balance
                - buying_power: Total available buying power
                - portfolio_value: Total portfolio value (cash + positions)
                - equity: Current equity value
                - initial_margin: Required initial margin (if applicable)
                - maintenance_margin: Required maintenance margin (if applicable)
                - is_pattern_day_trader: Pattern Day Trader status flag
            - error (str or None): Error message if request failed, None on success
            
    Raises:
        ValueError: If data_source is specified but vendor is not configured,
            if EODHD is requested (not supported), or if no vendors are available.
        
    Example:
        >>> # Check account status and available capital
        >>> response = get_account()
        >>> if response["success"]:
        ...     account = response["data"]
        ...     print(f"Account Status: {account.status}")
        ...     print(f"Portfolio Value: ${account.portfolio_value:,.2f}")
        ...     print(f"Buying Power: ${account.buying_power:,.2f}")
        ...     print(f"Available Cash: ${account.cash:,.2f}")
        ...     
        ...     if account.is_pattern_day_trader:
        ...         print("Account flagged as Pattern Day Trader")
        ...     
        ...     # Check if account has sufficient funds for trade
        ...     trade_value = 10000
        ...     if account.buying_power >= trade_value:
        ...         print(f"Sufficient buying power for ${trade_value:,} trade")
        ...     else:
        ...         print(f"Insufficient funds. Need ${trade_value - account.buying_power:,.2f} more")
        
    Note:
        - Requires Alpaca API credentials (ALPACA_API_KEY and ALPACA_SECRET_KEY)
        - Account values updated in real-time during market hours
        - Pattern Day Trader rules apply to accounts with < $25,000 equity
        - Buying power varies based on account type and margin settings
        - Cash vs margin account affects available buying power calculation
        - Currently only available through Alpaca vendor
    """
    try:
        vendor = _get_vendor('trading', data_source)
        
        if vendor == 'alpaca':
            response = alpaca.get_account()
            
            if isinstance(response, dict) and "error" in response:
                return ensure_standard_response(None, False, response["error"])
            
            account = AlpacaTransformer.transform_account(response)
            return ensure_standard_response(account)
        else:
            return ensure_standard_response(None, False, f"Trading account not available for vendor: {vendor}")
            
    except Exception as e:
        return ensure_standard_response(None, False, str(e))


def get_positions(data_source: Optional[str] = None) -> Dict[str, Any]:
    """Retrieve all open stock positions with profit/loss and market values.
    
    Fetches complete position data including quantities, entry prices,
    current market values, and unrealized P&L for all holdings in
    the trading account. Essential for portfolio monitoring, risk
    management, and performance analysis.
    
    Args:
        data_source: Explicitly specify which vendor to use. Options:
            - None: Auto-select based on preferences (Alpaca preferred for trading)
            - "alpaca": Force use of Alpaca Trading API (only option for trading)
            - "eodhd": Not supported - positions not available via EODHD
            If specified vendor is not configured, function will raise ValueError.
            
    Returns:
        Dict[str, Any]: Standardized response containing:
            - success (bool): True if request succeeded, False otherwise
            - data (List[StandardPosition]): List of position objects, each containing:
                - symbol: Standard symbol format
                - quantity: Number of shares held (positive for long, negative for short)
                - side: Position side ("long" or "short")
                - avg_entry_price: Average cost basis per share
                - current_price: Current market price per share
                - market_value: Current market value of position
                - cost_basis: Total cost basis of position
                - unrealized_pnl: Unrealized profit/loss in dollars
                - unrealized_pnl_percent: Unrealized P&L as percentage
            - error (str or None): Error message if request failed, None on success
            
    Raises:
        ValueError: If data_source is specified but vendor is not configured,
            if EODHD is requested (not supported), or if no vendors are available.
        
    Example:
        >>> # Analyze portfolio performance
        >>> response = get_positions()
        >>> if response["success"]:
        ...     positions = response["data"]
        ...     total_value = sum(pos.market_value for pos in positions)
        ...     total_pnl = sum(pos.unrealized_pnl for pos in positions)
        ...     
        ...     print(f"Total positions: {len(positions)}")
        ...     print(f"Total market value: ${total_value:,.2f}")
        ...     print(f"Total unrealized P&L: ${total_pnl:,.2f}")
        ...     
        ...     print("\nIndividual positions:")
        ...     for pos in positions:
        ...         pnl_pct = pos.unrealized_pnl_percent * 100
        ...         print(f"{pos.symbol}: {pos.quantity:,.0f} shares")
        ...         print(f"  Value: ${pos.market_value:,.2f}")
        ...         print(f"  P&L: ${pos.unrealized_pnl:,.2f} ({pnl_pct:+.2f}%)")
        ...         print(f"  Entry: ${pos.avg_entry_price:.2f} Current: ${pos.current_price:.2f}")
        
        >>> # Find biggest winners and losers
        >>> response = get_positions(data_source="alpaca")
        >>> if response["success"]:
        ...     positions = response["data"]
        ...     winners = [p for p in positions if p.unrealized_pnl > 0]
        ...     losers = [p for p in positions if p.unrealized_pnl < 0]
        ...     
        ...     print(f"Winners: {len(winners)}, Losers: {len(losers)}")
        ...     
        ...     if winners:
        ...         best = max(winners, key=lambda p: p.unrealized_pnl_percent)
        ...         print(f"Best performer: {best.symbol} (+{best.unrealized_pnl_percent*100:.1f}%)")
        
    Note:
        - Requires Alpaca API credentials (ALPACA_API_KEY and ALPACA_SECRET_KEY)
        - Position values updated in real-time during market hours
        - Negative quantities indicate short positions
        - Cost basis includes commissions and fees
        - Market values based on current bid/ask or last trade price
        - Currently only available through Alpaca vendor
    """
    try:
        vendor = _get_vendor('trading', data_source)
        
        if vendor == 'alpaca':
            response = alpaca.get_positions()
            
            if isinstance(response, dict) and "error" in response:
                return ensure_standard_response(None, False, response["error"])
            
            positions = AlpacaTransformer.transform_positions(response)
            return ensure_standard_response(positions)
        else:
            return ensure_standard_response(None, False, f"Positions not available for vendor: {vendor}")
            
    except Exception as e:
        return ensure_standard_response(None, False, str(e))


def get_position(symbol: str, data_source: Optional[str] = None) -> Dict[str, Any]:
    """Retrieve detailed position information for a specific symbol.
    
    Fetches comprehensive position data for a single stock including
    entry price, current value, profit/loss metrics, and position size.
    Useful for position-specific analysis, risk management, and individual
    stock performance tracking.
    
    Args:
        symbol: Stock symbol in standard format (e.g., "AAPL", "TSLA", "MSFT").
            No exchange suffixes required - use "AAPL" not "AAPL.US".
            Case-insensitive, automatically converted to uppercase.
        data_source: Explicitly specify which vendor to use. Options:
            - None: Auto-select based on preferences (Alpaca preferred for trading)
            - "alpaca": Force use of Alpaca Trading API (only option for trading)
            - "eodhd": Not supported - position details not available via EODHD
            If specified vendor is not configured, function will raise ValueError.
            
    Returns:
        Dict[str, Any]: Standardized response containing:
            - success (bool): True if request succeeded, False otherwise
            - data (StandardPosition or None): Position details containing:
                - symbol: Standard symbol format
                - quantity: Number of shares held (positive for long, negative for short)
                - side: Position side ("long" or "short")
                - avg_entry_price: Average cost basis per share
                - current_price: Current market price per share
                - market_value: Current market value of position
                - cost_basis: Total cost basis of position
                - unrealized_pnl: Unrealized profit/loss in dollars
                - unrealized_pnl_percent: Unrealized P&L as percentage
            - error (str or None): Error message if request failed, None on success
            
    Raises:
        ValueError: If data_source is specified but vendor is not configured,
            if EODHD is requested (not supported), or if no vendors are available.
        
    Example:
        >>> # Check Apple position performance
        >>> response = get_position("AAPL")
        >>> if response["success"] and response["data"]:
        ...     position = response["data"]
        ...     qty = position.quantity
        ...     current_price = position.current_price
        ...     entry_price = position.avg_entry_price
        ...     pnl_pct = position.unrealized_pnl_percent * 100
        ...     
        ...     print(f"AAPL Position: {qty:,.0f} shares")
        ...     print(f"Entry Price: ${entry_price:.2f}")
        ...     print(f"Current Price: ${current_price:.2f}")
        ...     print(f"Market Value: ${position.market_value:,.2f}")
        ...     print(f"P&L: ${position.unrealized_pnl:,.2f} ({pnl_pct:+.2f}%)")
        ... elif response["success"]:
        ...     print("No position found for AAPL")
        
        >>> # Risk check for position size
        >>> response = get_position("TSLA", data_source="alpaca")
        >>> if response["success"] and response["data"]:
        ...     position = response["data"]
        ...     position_value = abs(position.market_value)
        ...     # Assume we have portfolio_value from get_account()
        ...     portfolio_value = 100000  # Example
        ...     concentration = position_value / portfolio_value
        ...     
        ...     if concentration > 0.10:  # 10% concentration limit
        ...         print(f"High concentration warning: {concentration:.1%} of portfolio")
        
    Note:
        - Requires Alpaca API credentials (ALPACA_API_KEY and ALPACA_SECRET_KEY)
        - Returns None in data field if no position exists for the symbol
        - Position values updated in real-time during market hours
        - Use get_positions() to retrieve all positions at once (more efficient)
        - Currently only available through Alpaca vendor
        - Useful for position-specific risk management and analysis
    """
    try:
        vendor = _get_vendor('trading', data_source)
        
        if vendor == 'alpaca':
            vendor_symbol = SymbolFormatter.from_standard(symbol, "alpaca")
            response = alpaca.get_position(vendor_symbol)
            
            if isinstance(response, dict) and "error" in response:
                return ensure_standard_response(None, False, response["error"])
            
            positions = AlpacaTransformer.transform_positions([response])
            return ensure_standard_response(positions[0] if positions else None)
        else:
            return ensure_standard_response(None, False, f"Position details not available for vendor: {vendor}")
            
    except Exception as e:
        return ensure_standard_response(None, False, str(e))


# Single-vendor functions (Alpaca Trading API only)
def get_orders(status: str = "open", limit: int = 100, after: Optional[str] = None, until: Optional[str] = None, direction: str = "desc", nested: bool = False, data_source: Optional[str] = None) -> Dict[str, Any]:
    """Retrieve order history and status with comprehensive order details.
    
    Fetches order information including execution status, fill prices,
    timestamps, and order parameters. Essential for trade reconciliation,
    performance analysis, and order management.
    
    Args:
        status: Order status filter. Options:
            - 'open': Active orders awaiting execution
            - 'closed': Completed orders (filled, canceled, expired)
            - 'all': All orders regardless of status
            Defaults to 'open'.
        limit: Maximum number of orders to return. Range: 1-500.
            Defaults to 100.
        after: Include orders after this timestamp (ISO 8601 format).
            If None, no after-time filtering applied.
        until: Include orders before this timestamp (ISO 8601 format).
            If None, no before-time filtering applied.
        direction: Sort order for returned results. Options:
            - 'desc': Newest orders first (default)
            - 'asc': Oldest orders first
        nested: Whether to include nested order details for complex orders.
            Defaults to False.
        data_source: Explicitly specify which vendor to use. Options:
            - None: Auto-select based on preferences (Alpaca only for trading)
            - "alpaca": Force use of Alpaca Trading API (only option)
            - "eodhd": Not supported - orders not available via EODHD
            
    Returns:
        Dict[str, Any]: Standardized response containing:
            - success (bool): True if request succeeded, False otherwise
            - data (List[StandardOrder]): List of orders, each containing:
                - order_id: Unique order identifier
                - client_order_id: Client-specified order ID
                - symbol: Stock symbol
                - side: Order side ('buy' or 'sell')
                - order_type: Order type (market, limit, stop, etc.)
                - quantity: Order quantity
                - filled_quantity: Quantity filled so far
                - status: Current order status
                - limit_price: Limit price (for limit orders)
                - stop_price: Stop price (for stop orders)
                - filled_avg_price: Average fill price
                - created_at: Order creation timestamp
                - filled_at: Order fill timestamp (if filled)
            - error (str or None): Error message if request failed, None on success
            
    Example:
        >>> # Get recent filled orders
        >>> response = get_orders(status='closed', limit=10)
        >>> if response["success"]:
        ...     orders = response["data"]
        ...     filled_orders = [o for o in orders if o.status == 'filled']
        ...     print(f"Found {len(filled_orders)} filled orders:")
        ...     for order in filled_orders:
        ...         qty = order.filled_quantity
        ...         price = order.filled_avg_price
        ...         value = float(qty) * float(price)
        ...         print(f"{order.symbol}: {order.side} {qty} @ ${price}")
        ...         print(f"  Total Value: ${value:,.2f}")
        
    Note:
        - Requires Alpaca API credentials (ALPACA_API_KEY and ALPACA_SECRET_KEY)
        - Order history retained for account lifetime
        - Use time filters for performance with large order histories
        - Partial fills show filled_quantity < quantity
        - Currently only available through Alpaca vendor
    """
    try:
        vendor = _get_vendor('trading', data_source)
        
        if vendor == 'alpaca':
            response = alpaca.get_orders(status, limit, after, until, direction, nested)
            
            if isinstance(response, dict) and "error" in response:
                return ensure_standard_response(None, False, response["error"])
            
            # Transform to standard format if needed
            return ensure_standard_response(response)
        else:
            return ensure_standard_response(None, False, f"Orders not available for vendor: {vendor}")
            
    except Exception as e:
        return ensure_standard_response(None, False, str(e))


def get_portfolio_history(period: str = "1D", timeframe: str = "15Min", end_date: Optional[str] = None, extended_hours: bool = False, data_source: Optional[str] = None) -> Dict[str, Any]:
    """Retrieve historical portfolio performance and value changes over time.
    
    Fetches time-series data of portfolio value, profit/loss, and percentage
    changes for performance analysis, charting, and risk assessment.
    
    Args:
        period: Historical period to retrieve. Options:
            - '1D': One day (intraday data)
            - '1W': One week
            - '1M': One month
            - '3M': Three months
            - '1Y': One year
            - 'YTD': Year to date
            - 'ALL': All available history
            Defaults to '1D'.
        timeframe: Data granularity for the specified period. Options:
            - '1Min', '5Min', '15Min': Minute intervals (for shorter periods)
            - '1Hour': Hourly data
            - '1Day': Daily data
            Defaults to '15Min'.
        end_date: End date for historical data in 'YYYY-MM-DD' format.
            If None, uses current date. Useful for backtesting scenarios.
        extended_hours: Whether to include extended trading hours data.
            If True, includes pre-market and after-hours activity.
            Defaults to False (regular hours only).
        data_source: Explicitly specify which vendor to use. Options:
            - None: Auto-select based on preferences (Alpaca only for trading)
            - "alpaca": Force use of Alpaca Trading API (only option)
            - "eodhd": Not supported - portfolio history not available via EODHD
            
    Returns:
        Dict[str, Any]: Portfolio history containing:
            - timestamp: Array of Unix timestamps for each data point
            - equity: Array of portfolio equity values
            - profit_loss: Array of profit/loss values
            - profit_loss_pct: Array of percentage changes
            - base_value: Starting portfolio value for the period
            - timeframe: Confirmed timeframe used
            - On error: {'error': 'error_description'}
            
    Example:
        >>> # Get one month of daily portfolio performance
        >>> response = get_portfolio_history('1M', '1Day')
        >>> if response["success"]:
        ...     history = response["data"]
        ...     timestamps = history['timestamp']
        ...     equity_values = history['equity']
        ...     pl_pct = history['profit_loss_pct']
        ...     
        ...     # Calculate performance metrics
        ...     start_value = history['base_value']
        ...     end_value = equity_values[-1]
        ...     total_return = (end_value / start_value - 1) * 100
        ...     
        ...     print(f"Portfolio Performance (1 Month):")
        ...     print(f"Starting Value: ${start_value:,.2f}")
        ...     print(f"Ending Value: ${end_value:,.2f}")
        ...     print(f"Total Return: {total_return:+.2f}%")
        
    Note:
        - Requires Alpaca API credentials (ALPACA_API_KEY and ALPACA_SECRET_KEY)
        - Higher frequency data (1Min, 5Min) limited to shorter periods
        - Extended hours data may show different liquidity patterns
        - Portfolio value includes cash and position market values
        - Currently only available through Alpaca vendor
    """
    try:
        vendor = _get_vendor('trading', data_source)
        
        if vendor == 'alpaca':
            response = alpaca.get_portfolio_history(period, timeframe, end_date, extended_hours)
            
            if isinstance(response, dict) and "error" in response:
                return ensure_standard_response(None, False, response["error"])
            
            return ensure_standard_response(response)
        else:
            return ensure_standard_response(None, False, f"Portfolio history not available for vendor: {vendor}")
            
    except Exception as e:
        return ensure_standard_response(None, False, str(e))


def get_market_clock(data_source: Optional[str] = None) -> Dict[str, Any]:
    """Retrieve current market status and trading session information.
    
    Fetches real-time market clock data including current market status,
    next open/close times, and session information. Essential for
    determining when markets are open for trading.
    
    Args:
        data_source: Explicitly specify which vendor to use. Options:
            - None: Auto-select based on preferences (Alpaca only for trading)
            - "alpaca": Force use of Alpaca Trading API (only option)
            - "eodhd": Not supported - market clock not available via EODHD
            
    Returns:
        Dict[str, Any]: Market clock information containing:
            - timestamp: Current timestamp in ISO 8601 format
            - is_open: Boolean indicating if market is currently open
            - next_open: Next market open time in ISO 8601 format
            - next_close: Next market close time in ISO 8601 format
            - On error: {'error': 'error_description'}
            
    Example:
        >>> response = get_market_clock()
        >>> if response["success"]:
        ...     clock = response["data"]
        ...     from datetime import datetime
        ...     
        ...     current_time = datetime.fromisoformat(clock['timestamp'].replace('Z', '+00:00'))
        ...     next_open = datetime.fromisoformat(clock['next_open'].replace('Z', '+00:00'))
        ...     next_close = datetime.fromisoformat(clock['next_close'].replace('Z', '+00:00'))
        ...     
        ...     print(f"Current Time: {current_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
        ...     print(f"Market Open: {'Yes' if clock['is_open'] else 'No'}")
        ...     
        ...     if clock['is_open']:
        ...         print(f"Market closes at: {next_close.strftime('%H:%M %Z')}")
        ...     else:
        ...         print(f"Market opens at: {next_open.strftime('%Y-%m-%d %H:%M %Z')}")
        
    Note:
        - Requires Alpaca API credentials (ALPACA_API_KEY and ALPACA_SECRET_KEY)
        - Market hours: 9:30 AM - 4:00 PM ET (regular session)
        - Extended hours: 4:00 AM - 9:30 AM, 4:00 PM - 8:00 PM ET
        - Market closed on weekends and federal holidays
        - Times returned in UTC, convert to local timezone as needed
        - Currently only available through Alpaca vendor
    """
    try:
        vendor = _get_vendor('trading', data_source)
        
        if vendor == 'alpaca':
            response = alpaca.get_clock()
            
            if isinstance(response, dict) and "error" in response:
                return ensure_standard_response(None, False, response["error"])
            
            return ensure_standard_response(response)
        else:
            return ensure_standard_response(None, False, f"Market clock not available for vendor: {vendor}")
            
    except Exception as e:
        return ensure_standard_response(None, False, str(e))


# Single-vendor functions (EODHD API only)
def get_technical_indicator(symbol: str, function: str, period: int = 14, start_date: Optional[str] = None, end_date: Optional[str] = None, data_source: Optional[str] = None) -> Dict[str, Any]:
    """Calculate technical analysis indicators for price trend analysis.
    
    Computes various technical indicators including moving averages,
    oscillators, and momentum indicators for technical analysis and
    algorithmic trading strategies.
    
    Args:
        symbol: Stock symbol in standard format (e.g., "AAPL", "SPY").
            No exchange suffixes required - use "AAPL" not "AAPL.US".
        function: Technical indicator to calculate. Common options:
            - 'sma': Simple Moving Average
            - 'ema': Exponential Moving Average
            - 'rsi': Relative Strength Index
            - 'macd': Moving Average Convergence Divergence
            - 'bb': Bollinger Bands
            - 'stoch': Stochastic Oscillator
        period: Calculation period for the indicator (number of periods).
            Defaults to 14, which is standard for RSI and many oscillators.
        start_date: Start date for calculation in 'YYYY-MM-DD' format.
            If None, uses sufficient history for accurate calculation.
        end_date: End date for calculation in 'YYYY-MM-DD' format.
            If None, calculates up to most recent trading day.
        data_source: Explicitly specify which vendor to use. Options:
            - None: Auto-select based on preferences (EODHD only for technical)
            - "eodhd": Force use of EODHD API (only option)
            - "alpaca": Not supported - technical indicators not available via Alpaca
            
    Returns:
        Dict[str, Any]: Time series of indicator values, each containing:
            - date: Trading date for the indicator value
            - [function]: Calculated indicator value (key matches function parameter)
            - Additional fields may be present for complex indicators (e.g., MACD)
            - On error: {'error': 'error_description'}
            
    Example:
        >>> # Calculate 14-period RSI for Apple
        >>> response = get_technical_indicator('AAPL', 'rsi', 14, '2024-01-01')
        >>> if response["success"]:
        ...     rsi_data = response["data"]
        ...     latest_rsi = rsi_data[-1]['rsi']
        ...     print(f"Current RSI: {latest_rsi:.2f}")
        ...     if latest_rsi > 70:
        ...         print("Potentially overbought")
        ...     elif latest_rsi < 30:
        ...         print("Potentially oversold")
        
    Note:
        - Requires EODHD API credentials (EODHD_API_KEY)
        - Indicators require sufficient price history for accurate calculation
        - Different indicators have different optimal periods (RSI: 14, SMA: 20/50/200)
        - Some indicators return multiple values (MACD: signal, histogram)
        - Currently only available through EODHD vendor
    """
    try:
        vendor = _get_vendor('technical', data_source)
        
        if vendor == 'eodhd':
            vendor_symbol = SymbolFormatter.from_standard(symbol, "eodhd")
            response = eodhd.get_technical(vendor_symbol, function, period, start_date, end_date)
            
            if isinstance(response, dict) and "error" in response:
                return ensure_standard_response(None, False, response["error"])
            
            return ensure_standard_response(response)
        else:
            return ensure_standard_response(None, False, f"Technical indicators not available for vendor: {vendor}")
            
    except Exception as e:
        return ensure_standard_response(None, False, str(e))


def search_symbols(query: str, data_source: Optional[str] = None) -> Dict[str, Any]:
    """Search for stocks and financial instruments by symbol or company name.
    
    Performs fuzzy search across multiple exchanges to find stocks,
    ETFs, and other instruments matching the search query. Useful
    for symbol lookup and discovery of tradeable instruments.
    
    Args:
        query: Search term - can be:
            - Stock symbol (e.g., 'AAPL', 'TSLA')
            - Company name (e.g., 'Apple', 'Microsoft')
            - Partial matches (e.g., 'tech', 'bank')
            - ISIN or other identifiers
        data_source: Explicitly specify which vendor to use. Options:
            - None: Auto-select based on preferences (EODHD only for search)
            - "eodhd": Force use of EODHD API (only option)
            - "alpaca": Not supported - symbol search not available via Alpaca
            
    Returns:
        Dict[str, Any]: List of matching instruments, each containing:
            - Code: Full symbol with exchange suffix (e.g., 'AAPL.US')
            - Name: Full company or instrument name
            - Country: Country where instrument is listed
            - Exchange: Exchange where instrument trades
            - Currency: Trading currency
            - Type: Instrument type (Common Stock, ETF, etc.)
            - ISIN: International Securities Identification Number (if available)
            - On error: {'error': 'error_description'}
            
    Example:
        >>> # Search for Apple-related stocks
        >>> response = search_symbols('Apple')
        >>> if response["success"]:
        ...     results = response["data"]
        ...     print(f"Found {len(results)} matches for 'Apple':")
        ...     for result in results:
        ...         print(f"{result['Code']}: {result['Name']}")
        ...         print(f"  Exchange: {result['Exchange']} ({result['Country']})")
        ...         print(f"  Type: {result['Type']}")
        
    Note:
        - Requires EODHD API credentials (EODHD_API_KEY)
        - Search is case-insensitive and supports partial matches
        - Results include instruments from multiple global exchanges
        - Use the returned 'Code' field for subsequent API calls
        - Currently only available through EODHD vendor
    """
    try:
        vendor = _get_vendor('fundamentals', data_source)
        
        if vendor == 'eodhd':
            response = eodhd.search_symbols(query)
            
            if isinstance(response, dict) and "error" in response:
                return ensure_standard_response(None, False, response["error"])
            
            return ensure_standard_response(response)
        else:
            return ensure_standard_response(None, False, f"Symbol search not available for vendor: {vendor}")
            
    except Exception as e:
        return ensure_standard_response(None, False, str(e))


def get_exchanges_list(data_source: Optional[str] = None) -> Dict[str, Any]:
    """Retrieve list of all stock exchanges supported by the API.
    
    Fetches comprehensive information about global stock exchanges,
    including trading details, currencies, and country information.
    Essential for understanding data coverage and symbol formatting.
    
    Args:
        data_source: Explicitly specify which vendor to use. Options:
            - None: Auto-select based on preferences (EODHD only for exchanges)
            - "eodhd": Force use of EODHD API (only option)
            - "alpaca": Not supported - exchanges list not available via Alpaca
            
    Returns:
        Dict[str, Any]: List of supported exchanges, each containing:
            - Name: Full exchange name (e.g., 'New York Stock Exchange')
            - Code: Exchange code used in symbols (e.g., 'NYSE', 'NASDAQ')
            - OperatingMIC: Market Identifier Code for the exchange
            - Country: Country where exchange is located
            - Currency: Primary trading currency
            - CountryISO2: 2-letter ISO country code
            - CountryISO3: 3-letter ISO country code
            - Timezone: Exchange timezone
            - On error: {'error': 'error_description'}
            
    Example:
        >>> response = get_exchanges_list()
        >>> if response["success"]:
        ...     exchanges = response["data"]
        ...     print(f"API supports {len(exchanges)} exchanges:")
        ...     us_exchanges = [ex for ex in exchanges if ex['Country'] == 'USA']
        ...     print(f"US Exchanges: {len(us_exchanges)}")
        ...     for ex in us_exchanges:
        ...         print(f"  {ex['Code']}: {ex['Name']} ({ex['Currency']})")
        
    Note:
        - Requires EODHD API credentials (EODHD_API_KEY)
        - Exchange codes are used as suffixes in symbol format (e.g., 'AAPL.US')
        - Data coverage varies by exchange and subscription tier
        - Some exchanges may have delayed data or require premium access
        - Currently only available through EODHD vendor
    """
    try:
        vendor = _get_vendor('fundamentals', data_source)
        
        if vendor == 'eodhd':
            response = eodhd.get_exchanges_list()
            
            if isinstance(response, dict) and "error" in response:
                return ensure_standard_response(None, False, response["error"])
            
            return ensure_standard_response(response)
        else:
            return ensure_standard_response(None, False, f"Exchanges list not available for vendor: {vendor}")
            
    except Exception as e:
        return ensure_standard_response(None, False, str(e))


def get_exchange_symbols(exchange: str, data_source: Optional[str] = None) -> Dict[str, Any]:
    """Retrieve all tradeable symbols available on a specific exchange.
    
    Fetches comprehensive list of stocks, ETFs, and other instruments
    trading on the specified exchange. Useful for universe creation,
    screening across entire exchanges, and symbol discovery.
    
    Args:
        exchange: Exchange code to query (e.g., 'NYSE', 'NASDAQ', 'LSE').
            Use the 'Code' field from get_exchanges_list() for valid codes.
        data_source: Explicitly specify which vendor to use. Options:
            - None: Auto-select based on preferences (EODHD only for exchange symbols)
            - "eodhd": Force use of EODHD API (only option)
            - "alpaca": Not supported - exchange symbols not available via Alpaca
            
    Returns:
        Dict[str, Any]: List of all symbols on the exchange, each containing:
            - Code: Full symbol with exchange suffix (e.g., 'AAPL.US')
            - Name: Company or instrument name
            - Country: Country of the exchange
            - Exchange: Exchange code
            - Currency: Trading currency
            - Type: Instrument type (Common Stock, ETF, Preferred Stock, etc.)
            - Isin: International Securities Identification Number (if available)
            - On error: {'error': 'error_description'}
            
    Example:
        >>> # Get all NASDAQ stocks
        >>> response = get_exchange_symbols('NASDAQ')
        >>> if response["success"]:
        ...     symbols = response["data"]
        ...     print(f"NASDAQ has {len(symbols)} tradeable symbols")
        ...     common_stocks = [s for s in symbols if s['Type'] == 'Common Stock']
        ...     etfs = [s for s in symbols if s['Type'] == 'ETF']
        ...     print(f"Common Stocks: {len(common_stocks)}")
        ...     print(f"ETFs: {len(etfs)}")
        ...     # Show some examples
        ...     for symbol in symbols[:5]:
        ...         print(f"  {symbol['Code']}: {symbol['Name']} ({symbol['Type']})")
        
    Note:
        - Requires EODHD API credentials (EODHD_API_KEY)
        - Symbol lists are updated regularly but may not be real-time
        - Use returned 'Code' field for subsequent data requests
        - Large exchanges like NYSE/NASDAQ may return thousands of symbols
        - Some symbols may be delisted or inactive
        - Currently only available through EODHD vendor
    """
    try:
        vendor = _get_vendor('fundamentals', data_source)
        
        if vendor == 'eodhd':
            response = eodhd.get_exchange_symbols(exchange)
            
            if isinstance(response, dict) and "error" in response:
                return ensure_standard_response(None, False, response["error"])
            
            return ensure_standard_response(response)
        else:
            return ensure_standard_response(None, False, f"Exchange symbols not available for vendor: {vendor}")
            
    except Exception as e:
        return ensure_standard_response(None, False, str(e))


def get_custom_screener(filters: str = "", limit: int = 50, offset: int = 0, signals: str = "", data_source: Optional[str] = None) -> Dict[str, Any]:
    """Screen stocks using custom financial and technical criteria with advanced filtering.
    
    Filters stocks across exchanges based on fundamental metrics, technical indicators,
    and market data to identify investment opportunities matching specific criteria.
    More advanced than basic screeners, allowing complex filter combinations.
    
    Args:
        filters: Custom filter criteria as a string. Format varies but typically
            includes conditions like 'market_cap > 1000000000' or
            'pe_ratio < 20 AND dividend_yield > 0.02'. If empty,
            returns general market data without filtering.
        limit: Maximum number of results to return. Range typically 1-1000
            depending on API subscription. Defaults to 50.
        offset: Number of results to skip for pagination. Defaults to 0.
            Use with limit for paginating through large result sets.
        signals: Technical signal filters as a string. Examples:
            'golden_cross', 'oversold_rsi', 'breakout'. If empty,
            no technical signal filtering is applied.
        data_source: Explicitly specify which vendor to use. Options:
            - None: Auto-select based on preferences (EODHD only for custom screening)
            - "eodhd": Force use of EODHD API (only option)
            - "alpaca": Not supported - custom screening not available via Alpaca
            
    Returns:
        Dict[str, Any]: Standardized response containing:
            - success (bool): True if request succeeded, False otherwise
            - data (List[Dict]): List of stocks matching criteria, each containing:
                - code: Stock symbol with exchange suffix
                - name: Company name
                - market_cap: Market capitalization
                - pe_ratio: Price-to-earnings ratio
                - dividend_yield: Annual dividend yield
                - price: Current stock price
                - change_p: Daily percentage change
                - volume: Trading volume
                - Additional fields based on screening criteria
            - error (str or None): Error message if request failed, None on success
            
    Raises:
        ValueError: If data_source is specified but vendor is not configured,
            if Alpaca is requested (not supported), or if invalid filter syntax provided.
        
    Example:
        >>> # Screen for large-cap dividend stocks
        >>> criteria = "market_cap > 10000000000 AND dividend_yield > 0.03"
        >>> response = get_custom_screener(filters=criteria, limit=20)
        >>> if response["success"]:
        ...     stocks = response["data"]
        ...     print(f"Found {len(stocks)} dividend stocks:")
        ...     for stock in stocks:
        ...         print(f"{stock['code']}: {stock['name']}")
        ...         print(f"  Yield: {stock['dividend_yield']:.2%}")
        ...         print(f"  Market Cap: ${stock['market_cap']:,.0f}")
        
        >>> # Technical screening with signals
        >>> response = get_custom_screener(
        ...     filters="pe_ratio < 15",
        ...     signals="oversold_rsi,golden_cross",
        ...     limit=10,
        ...     data_source="eodhd"
        ... )
        
        >>> # Paginated screening for large results
        >>> for page in range(3):  # Get first 3 pages
        ...     response = get_custom_screener(
        ...         filters="market_cap > 1000000000",
        ...         limit=50,
        ...         offset=page * 50
        ...     )
        ...     if response["success"]:
        ...         print(f"Page {page + 1}: {len(response['data'])} stocks")
        
    Note:
        - Requires EODHD API credentials (EODHD_API_KEY)
        - Filter syntax depends on EODHD's specific query language
        - Available fields for filtering vary by subscription tier
        - Results updated daily with fundamental data
        - Technical signals updated intraday during market hours
        - Currently only available through EODHD vendor
        - More powerful than basic screeners (get_most_active_stocks, etc.)
    """
    try:
        vendor = _get_vendor('fundamentals', data_source)
        
        if vendor == 'eodhd':
            response = eodhd.get_screener(filters, limit, offset, signals)
            
            if isinstance(response, dict) and "error" in response:
                return ensure_standard_response(None, False, response["error"])
            
            return ensure_standard_response(response)
        else:
            return ensure_standard_response(None, False, f"Custom screening not available for vendor: {vendor}")
            
    except Exception as e:
        return ensure_standard_response(None, False, str(e))


# Registry of all financial functions (both new standard and legacy)
REAL_FINANCIAL_FUNCTIONS = {
    # New standardized functions (recommended for new code)
    'get_historical_data': get_historical_data,
    'get_real_time_data': get_real_time_data,
    'get_latest_quotes': get_latest_quotes,
    'get_latest_trades': get_latest_trades,
    'get_most_active_stocks': get_most_active_stocks,
    'get_top_gainers': get_top_gainers,
    'get_top_losers': get_top_losers,
    'get_market_news': get_market_news,
    'get_fundamentals': get_fundamentals,
    'get_dividends': get_dividends,
    'get_splits': get_splits,
    'get_account': get_account,
    'get_positions': get_positions,
    'get_position': get_position,
    
    # Single-vendor functions (with standardized interface)
    'get_orders': get_orders,
    'get_portfolio_history': get_portfolio_history,
    'get_market_clock': get_market_clock,
    'get_technical_indicator': get_technical_indicator,
    'search_symbols': search_symbols,
    'get_exchanges_list': get_exchanges_list,
    'get_exchange_symbols': get_exchange_symbols,
    'get_custom_screener': get_custom_screener,
    
}