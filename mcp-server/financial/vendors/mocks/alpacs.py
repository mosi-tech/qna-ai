"""
Mock Financial Data Functions - Following API Specifications

Mock implementations of financial functions that follow the exact API specifications
from eodhd-simple.json, alpaca-trading-simple.json, and alpaca-marketdata-simple.json
"""

import json
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
import warnings
warnings.filterwarnings('ignore')


# Alpaca Trading API Mock Functions
def get_account() -> Dict[str, Any]:
    """Generate mock trading account information and balances.
    
    Creates realistic simulated account data including buying power,
    equity positions, cash balances, and account status. Useful for
    testing portfolio management and account display functionality.
    
    Returns:
        Dict[str, Any]: Mock account information containing:
            - id: Unique account identifier
            - account_number: Account number for reference
            - status: Account status (ACTIVE)
            - currency: Base account currency (USD)
            - buying_power: Total available buying power
            - cash: Available cash balance
            - portfolio_value: Total portfolio value (cash + positions)
            - equity: Current equity value
            - pattern_day_trader: PDT status flag (False)
            - trading_blocked: Trading status (False)
            - multiplier: Account margin multiplier (2)
            - initial_margin: Required initial margin
            - maintenance_margin: Required maintenance margin
            - daytrade_count: Number of day trades in rolling 5-day period (0)
            
    Example:
        >>> account = alpaca_trading_account()
        >>> print(f"Account Status: {account['status']}")
        >>> print(f"Portfolio Value: ${float(account['portfolio_value']):,.2f}")
        >>> print(f"Buying Power: ${float(account['buying_power']):,.2f}")
        >>> print(f"Cash: ${float(account['cash']):,.2f}")
        >>> if account['pattern_day_trader']:
        ...     print("Account flagged as Pattern Day Trader")
        
    Note:
        - Mock account shows healthy cash account with ~$131K portfolio value
        - 2x margin multiplier simulating margin account capabilities
        - No day trading restrictions (daytrade_count = 0)
        - Useful for testing account management UI and risk calculations
    """
    return {
        "id": "904837e3-3b76-47ec-b432-046db621571b",
        "account_number": "010203ABCD",
        "status": "ACTIVE",
        "crypto_status": "ACTIVE",
        "currency": "USD",
        "buying_power": "262113.632",
        "regt_buying_power": "262113.632",
        "daytrading_buying_power": "262113.632",
        "non_marginable_buying_power": "131056.82",
        "cash": "131056.82",
        "accrued_fees": "0",
        "portfolio_value": "131056.82",
        "pattern_day_trader": False,
        "trading_blocked": False,
        "transfers_blocked": False,
        "account_blocked": False,
        "created_at": "2019-06-12T22:47:07.99Z",
        "trade_suspended_by_user": False,
        "multiplier": "2",
        "shorting_enabled": True,
        "equity": "131056.82",
        "last_equity": "131056.82",
        "long_market_value": "126392.12",
        "short_market_value": "0",
        "initial_margin": "63196.06",
        "maintenance_margin": "37917.636",
        "last_maintenance_margin": "37917.636",
        "sma": "131056.82",
        "daytrade_count": 0
    }


def get_positions() -> List[Dict[str, Any]]:
    """Generate mock list of open stock positions with P&L and market values.
    
    Creates a sample position showing realistic profit/loss metrics,
    entry prices, and current market values. Useful for testing
    position management and portfolio display functionality.
    
    Returns:
        List[Dict[str, Any]]: Mock list of positions, each containing:
            - asset_id: Unique identifier for the asset
            - symbol: Stock symbol (AAPL)
            - exchange: Exchange where asset trades (NASDAQ)
            - asset_class: Asset classification (us_equity)
            - qty: Number of shares held (5 shares)
            - side: Position side (long)
            - avg_entry_price: Average cost basis per share ($100)
            - market_value: Current market value ($600)
            - cost_basis: Total cost basis ($500)
            - unrealized_pl: Unrealized profit/loss ($100)
            - unrealized_plpc: Unrealized P&L percentage (20%)
            - current_price: Current market price per share ($120)
            - change_today: Today's price change percentage
            
    Example:
        >>> positions = alpaca_trading_positions()
        >>> if positions:
        ...     total_value = sum(float(pos['market_value']) for pos in positions)
        ...     total_pl = sum(float(pos['unrealized_pl']) for pos in positions)
        ...     print(f"Total positions: {len(positions)}")
        ...     print(f"Total market value: ${total_value:,.2f}")
        ...     print(f"Total unrealized P&L: ${total_pl:,.2f}")
        
    Note:
        - Returns single mock AAPL position with 20% unrealized gain
        - Position shows realistic entry vs current price spread
        - Useful for testing position analysis and P&L calculations
    """
    return [
        {
            "asset_id": "904837e3-3b76-47ec-b432-046db621571b",
            "symbol": "AAPL",
            "exchange": "NASDAQ",
            "asset_class": "us_equity",
            "avg_entry_price": "100.0",
            "qty": "5",
            "side": "long",
            "market_value": "600.0",
            "cost_basis": "500.0",
            "unrealized_pl": "100.0",
            "unrealized_plpc": "0.20",
            "unrealized_intraday_pl": "10.0",
            "unrealized_intraday_plpc": "0.0084",
            "current_price": "120.0",
            "lastday_price": "119.0",
            "change_today": "0.0084"
        }
    ]


def get_position(symbol: str) -> Dict[str, Any]:
    """Generate mock position information for a specific symbol.
    
    Creates simulated position data for the requested symbol with
    realistic profit/loss metrics and position details. Symbol is
    automatically converted to uppercase for consistency.
    
    Args:
        symbol: Stock symbol to query (e.g., 'AAPL', 'TSLA').
            Case-insensitive, automatically converted to uppercase.
            
    Returns:
        Dict[str, Any]: Mock position details containing:
            - asset_id: Unique identifier for the asset
            - symbol: Stock symbol (uppercase)
            - exchange: Exchange (NASDAQ)
            - asset_class: Asset classification (us_equity)
            - qty: Number of shares held (5)
            - side: Position side (long)
            - avg_entry_price: Average cost basis per share ($100)
            - market_value: Current market value ($600)
            - cost_basis: Total cost basis ($500)
            - current_price: Current market price per share ($120)
            - unrealized_pl: Unrealized profit/loss ($100)
            - unrealized_plpc: Unrealized P&L percentage (20%)
            
    Example:
        >>> position = alpaca_trading_position('AAPL')
        >>> qty = float(position['qty'])
        >>> current_price = float(position['current_price'])
        >>> entry_price = float(position['avg_entry_price'])
        >>> pl_pct = float(position['unrealized_plpc']) * 100
        >>> print(f"{position['symbol']} Position: {qty:,.0f} shares")
        >>> print(f"Entry Price: ${entry_price:.2f}")
        >>> print(f"Current Price: ${current_price:.2f}")
        >>> print(f"P&L: {pl_pct:+.2f}%")
        
    Note:
        - Returns same mock position data regardless of symbol requested
        - Shows 20% unrealized gain scenario for testing
        - Useful for testing single position analysis and display
    """
    return {
        "asset_id": "904837e3-3b76-47ec-b432-046db621571b",
        "symbol": symbol.upper(),
        "exchange": "NASDAQ",
        "asset_class": "us_equity",
        "avg_entry_price": "100.0",
        "qty": "5",
        "side": "long",
        "market_value": "600.0",
        "cost_basis": "500.0",
        "unrealized_pl": "100.0",
        "unrealized_plpc": "0.20",
        "current_price": "120.0"
    }


def get_orders(status: str = "open", limit: int = 100, after: Optional[str] = None, until: Optional[str] = None, direction: str = "desc", nested: bool = False) -> List[Dict[str, Any]]:
    """Generate mock order history and status information.
    
    Creates sample order data showing a filled market order with realistic
    execution details. Useful for testing order management, trade reconciliation,
    and order history display functionality.
    
    Args:
        status: Order status filter (ignored in mock).
        limit: Maximum number of orders (ignored in mock).
        after: Include orders after timestamp (ignored in mock).
        until: Include orders before timestamp (ignored in mock).
        direction: Sort order (ignored in mock).
        nested: Include nested order details (ignored in mock).
            
    Returns:
        List[Dict[str, Any]]: Mock list of orders, each containing:
            - id: Unique order identifier
            - client_order_id: Client-specified order ID
            - symbol: Stock symbol (AAPL)
            - asset_class: Asset type (us_equity)
            - qty: Order quantity (5)
            - filled_qty: Quantity filled (3)
            - side: Order side (buy)
            - order_type: Order type (market)
            - time_in_force: Order duration (day)
            - limit_price: Limit price ($107.00)
            - stop_price: Stop price ($106.00)
            - status: Current order status (filled)
            - created_at: Order creation timestamp
            - filled_at: Order fill timestamp
            - filled_avg_price: Average fill price ($100.00)
            
    Example:
        >>> orders = alpaca_trading_orders(status='filled')
        >>> if orders:
        ...     for order in orders:
        ...         qty = order['filled_qty']
        ...         price = order['filled_avg_price']
        ...         value = float(qty) * float(price)
        ...         print(f"{order['symbol']}: {order['side']} {qty} @ ${price}")
        ...         print(f"  Total Value: ${value:,.2f}")
        
    Note:
        - Returns single mock AAPL buy order, partially filled
        - Shows realistic order progression from creation to fill
        - Filter parameters ignored in mock implementation
        - Useful for testing order management UI and workflows
    """
    return [
        {
            "id": "904837e3-3b76-47ec-b432-046db621571b",
            "client_order_id": "904837e3-3b76-47ec-b432-046db621571b",
            "created_at": "2021-03-16T18:38:01.942282Z",
            "updated_at": "2021-03-16T18:38:01.942282Z",
            "submitted_at": "2021-03-16T18:38:01.937734Z",
            "filled_at": "2021-03-16T18:38:01.937734Z",
            "asset_id": "904837e3-3b76-47ec-b432-046db621571b",
            "symbol": "AAPL",
            "asset_class": "us_equity",
            "qty": "5",
            "filled_qty": "3",
            "filled_avg_price": "100.0",
            "order_type": "market",
            "side": "buy",
            "time_in_force": "day",
            "limit_price": "107.00",
            "stop_price": "106.00",
            "status": "filled",
            "extended_hours": False
        }
    ]


def get_portfolio_history(period: str = "1D", timeframe: str = "15Min", end_date: Optional[str] = None, extended_hours: bool = False) -> Dict[str, Any]:
    """Generate mock portfolio performance history showing value changes over time.
    
    Creates sample time-series data of portfolio value, profit/loss, and percentage
    changes. Shows realistic intraday portfolio fluctuations useful for testing
    performance charting and analysis functionality.
    
    Args:
        period: Historical period (ignored in mock).
        timeframe: Data granularity (returned in response).
        end_date: End date (ignored in mock).
        extended_hours: Include extended hours (ignored in mock).
            
    Returns:
        Dict[str, Any]: Mock portfolio history containing:
            - timestamp: Array of Unix timestamps for sample data points
            - equity: Array of portfolio equity values showing progression
            - profit_loss: Array of profit/loss values (positive and negative)
            - profit_loss_pct: Array of percentage changes
            - base_value: Starting portfolio value for the period
            - timeframe: Confirmed timeframe (echoed from input)
            
    Example:
        >>> history = alpaca_trading_portfolio_history('1D', '15Min')
        >>> timestamps = history['timestamp']
        >>> equity_values = history['equity']
        >>> pl_pct = history['profit_loss_pct']
        >>> 
        >>> start_value = history['base_value']
        >>> end_value = equity_values[-1]
        >>> total_return = (end_value / start_value - 1) * 100
        >>> 
        >>> print(f"Mock Portfolio Performance:")
        >>> print(f"Starting Value: ${start_value:,.2f}")
        >>> print(f"Ending Value: ${end_value:,.2f}")
        >>> print(f"Total Return: {total_return:+.2f}%")
        
    Note:
        - Shows realistic intraday portfolio fluctuations
        - Includes both gains and losses for testing
        - Useful for performance charting and analysis UI
        - Parameters ignored in mock implementation
    """
    return {
        "timestamp": [1580826600000, 1580827500000, 1580828400000],
        "equity": [27423.73, 27408.19, 27515.97],
        "profit_loss": [11.8, -3.74, 104.04],
        "profit_loss_pct": [0.000430469507, -0.0001364369455, 0.003790983306],
        "base_value": 27411.93,
        "timeframe": timeframe
    }


def get_clock() -> Dict[str, Any]:
    """Generate mock market clock status and trading session information.
    
    Creates sample market timing data showing market closed status with
    next open/close times. Useful for testing market hours logic and
    trading schedule functionality.
    
    Returns:
        Dict[str, Any]: Mock market clock information containing:
            - timestamp: Fixed timestamp (2024-01-02T21:00:00.000Z)
            - is_open: Market status (False - market closed)
            - next_open: Next market open time
            - next_close: Next market close time
            
    Example:
        >>> clock = alpaca_trading_clock()
        >>> from datetime import datetime
        >>> 
        >>> current_time = clock['timestamp']
        >>> next_open = clock['next_open']
        >>> next_close = clock['next_close']
        >>> 
        >>> print(f"Current Time: {current_time}")
        >>> print(f"Market Open: {'Yes' if clock['is_open'] else 'No'}")
        >>> print(f"Next Open: {next_open}")
        >>> print(f"Next Close: {next_close}")
        
    Note:
        - Always shows market closed status for consistent testing
        - Fixed timestamps for predictable behavior
        - Useful for testing market hours validation logic
        - Times in UTC format matching real API responses
    """
    return {
        "timestamp": "2024-01-02T21:00:00.000Z",
        "is_open": False,
        "next_open": "2024-01-03T14:30:00.000Z",
        "next_close": "2024-01-03T21:00:00.000Z"
    }


# Alpaca Market Data API Mock Functions  
def get_bars(symbols: List[str], timeframe: str = "1Day", start: Optional[str] = None, end: Optional[str] = None) -> Dict[str, Any]:
    """Generate mock historical OHLC price bars for multiple stocks.
    
    Creates realistic simulated time-series price data including open, high,
    low, close, and volume for specified symbols. Each symbol gets unique
    but deterministic price patterns based on symbol-based seeding.
    
    Args:
        symbols: List of stock symbols (e.g., 'AAPL,TSLA,MSFT').
            Each symbol generates unique price patterns.
        timeframe: Bar duration (returned in structure but not used in calculation).
        start: Start date in 'YYYY-MM-DD' format. If None, defaults to 1 year ago.
        end: End date in 'YYYY-MM-DD' format. If None, defaults to current date.
            
    Returns:
        Dict[str, Any]: Mock historical price data containing:
            - bars: Dictionary with symbol keys, each containing array of bars:
                - t: Timestamp in ISO 8601 format
                - o: Open price
                - h: High price
                - l: Low price
                - c: Close price
                - v: Volume (realistic random values)
            
    Example:
        >>> bars = alpaca_market_stocks_bars(['AAPL','GOOGL','MSFT'], '1Day', '2024-01-01')
        >>> for symbol, symbol_bars in bars['bars'].items():
        ...     if symbol_bars:
        ...         latest = symbol_bars[-1]
        ...         first = symbol_bars[0]
        ...         total_return = (latest['c'] / first['o'] - 1) * 100
        ...         print(f"{symbol}: {len(symbol_bars)} bars")
        ...         print(f"  Return: {total_return:+.2f}%")
        ...         print(f"  Latest: ${latest['c']:.2f} (Vol: {latest['v']:,})")
        
    Note:
        - Uses symbol-based seeding for consistent mock data per symbol
        - Base prices: AAPL=$185.64, TSLA=$250.00, SPY=$450.00, others=$100.00
        - Realistic daily returns (~1.8% volatility) and volume patterns
        - Excludes weekends, includes only trading days
        - Volume based on lognormal distribution for realism
    """
    symbol_list = symbols
    
    # Parse dates
    if start:
        start_date = datetime.strptime(start, "%Y-%m-%d")
    else:
        start_date = datetime.now() - timedelta(days=365)
    
    if end:
        end_date = datetime.strptime(end, "%Y-%m-%d")
    else:
        end_date = datetime.now()
    
    bars = {}
    for symbol in symbol_list:
        # Set seed for consistent data per symbol
        np.random.seed(hash(symbol) % 2**32)
        
        base_price = {"AAPL": 185.64, "TSLA": 250.0, "SPY": 450.0, "QQQ": 400.0, "MSFT": 350.0}.get(symbol, 100.0)
        
        symbol_bars = []
        current_price = base_price
        current_date = start_date
        
        while current_date <= end_date:
            # Only weekdays (skip weekends)
            if current_date.weekday() < 5:
                # Generate realistic daily movement
                daily_return = np.random.normal(0.0008, 0.018)  # Slightly positive bias with realistic volatility
                
                open_price = current_price
                close_price = open_price * (1 + daily_return)
                
                # High and low with realistic spreads
                daily_range = abs(np.random.normal(0, 0.015))
                high_price = max(open_price, close_price) * (1 + daily_range)
                low_price = min(open_price, close_price) * (1 - daily_range)
                
                # Volume with realistic patterns
                avg_volume = {"AAPL": 55_000_000, "TSLA": 85_000_000, "SPY": 75_000_000}.get(symbol, 25_000_000)
                volume = int(avg_volume * np.random.lognormal(0, 0.4))
                
                symbol_bars.append({
                    "t": current_date.strftime("%Y-%m-%dT05:00:00Z"),
                    "o": round(open_price, 2),
                    "h": round(high_price, 2),
                    "l": round(low_price, 2),
                    "c": round(close_price, 2),
                    "v": volume
                })
                
                current_price = close_price
            
            current_date += timedelta(days=1)
        
        bars[symbol] = symbol_bars
    
    return {"bars": bars}


def get_snapshots(symbols: List[str]) -> Dict[str, Any]:
    """Generate mock comprehensive current market snapshots for multiple stocks.
    
    Creates simulated real-time market data including latest quotes, trades,
    and daily bars for each requested symbol. Uses consistent base prices
    per symbol for predictable testing.
    
    Args:
        symbols: List of stock symbols (e.g., ['AAPL','TSLA','SPY']).
            Each symbol gets its own mock snapshot data.
            
    Returns:
        Dict[str, Any]: Mock market snapshots containing:
            - snapshots: Dictionary with symbol keys, each containing:
                - latestTrade: Most recent trade data (price, size, timestamp)
                - latestQuote: Current bid/ask quote (spread, sizes, timestamp)
                - dailyBar: Current day's OHLC data (open, high, low, close, volume)
            
    Example:
        >>> snapshots = alpaca_market_stocks_snapshots('AAPL,MSFT,GOOGL')
        >>> for symbol, data in snapshots['snapshots'].items():
        ...     trade = data.get('latestTrade', {})
        ...     quote = data.get('latestQuote', {})
        ...     daily = data.get('dailyBar', {})
        ...     
        ...     print(f"{symbol} Mock Snapshot:")
        ...     print(f"  Last Trade: ${trade.get('p', 'N/A')}")
        ...     print(f"  Bid/Ask: ${quote.get('bp', 'N/A')} / ${quote.get('ap', 'N/A')}")
        ...     print(f"  Volume: {daily.get('v', 0):,} shares")
        
    Note:
        - Base prices: AAPL=$185.64, TSLA=$250.00, SPY=$450.00
        - Realistic bid/ask spreads (1 cent for liquid stocks)
        - Fixed timestamps for consistent testing
        - Useful for testing real-time dashboard displays
    """
    symbol_list = symbols
    
    snapshots = {}
    for symbol in symbol_list:
        base_price = {"AAPL": 185.64, "TSLA": 250.0, "SPY": 450.0}.get(symbol, 100.0)
        snapshots[symbol] = {
            "latestTrade": {"p": base_price, "s": 100, "t": "2024-01-02T21:00:00Z"},
            "latestQuote": {"bp": base_price - 0.01, "ap": base_price + 0.01, "t": "2024-01-02T21:00:00Z"},
            "dailyBar": {"o": base_price, "h": base_price * 1.02, "l": base_price * 0.98, "c": base_price, "v": 82488200}
        }
    
    return {"snapshots": snapshots}


def get_quotes_latest(symbols: List[str]) -> Dict[str, Any]:
    """Generate mock latest bid/ask quotes for multiple stocks.
    
    Creates simulated current market maker quotes with realistic spreads
    and sizes. Uses base prices per symbol with tight spreads typical
    of liquid stocks.
    
    Args:
        symbols: List of stock symbols (e.g., ['AAPL','TSLA','SPY']).
            Each symbol gets its own quote data.
            
    Returns:
        Dict[str, Any]: Mock latest quotes containing:
            - quotes: Dictionary with symbol keys, each containing:
                - t: Quote timestamp in ISO 8601 format
                - bp: Best bid price (base_price - $0.01)
                - bs: Bid size (2 round lots)
                - ap: Best ask price (base_price + $0.01)
                - as: Ask size (1 round lot)
            
    Example:
        >>> quotes = alpaca_market_stocks_quotes_latest('AAPL,MSFT,GOOGL')
        >>> for symbol, quote in quotes['quotes'].items():
        ...     bid = quote['bp']
        ...     ask = quote['ap']
        ...     spread = ask - bid
        ...     mid_price = (bid + ask) / 2
        ...     
        ...     print(f"{symbol}:")
        ...     print(f"  Bid: ${bid:.2f} x {quote['bs']:,}")
        ...     print(f"  Ask: ${ask:.2f} x {quote['as']:,}")
        ...     print(f"  Spread: ${spread:.2f}")
        ...     print(f"  Mid: ${mid_price:.2f}")
        
    Note:
        - Uses tight 1-cent spreads typical of liquid stocks
        - Base prices: AAPL=$185.64, TSLA=$250.00, SPY=$450.00
        - Fixed bid/ask sizes for consistent testing
        - Useful for testing limit order pricing logic
    """
    symbol_list = symbols
    
    quotes = {}
    for symbol in symbol_list:
        base_price = {"AAPL": 185.64, "TSLA": 250.0, "SPY": 450.0}.get(symbol, 100.0)
        quotes[symbol] = {
            "t": "2024-01-02T21:00:00.029Z",
            "bp": base_price - 0.01,
            "bs": 2,
            "ap": base_price + 0.01,
            "as": 1
        }
    
    return {"quotes": quotes}


def get_trades_latest(symbols: List[str]) -> Dict[str, Any]:
    """Generate mock latest trade execution data for multiple stocks.
    
    Creates simulated most recent trade transactions using base prices
    per symbol. Shows realistic trade sizes and fixed timestamps for
    consistent testing scenarios.
    
    Args:
        symbols: List of stock symbols (e.g., ['AAPL','TSLA','SPY']).
            Each symbol gets its own latest trade data.
            
    Returns:
        Dict[str, Any]: Mock latest trades containing:
            - trades: Dictionary with symbol keys, each containing:
                - t: Trade timestamp in ISO 8601 format
                - p: Trade price (based on symbol's base price)
                - s: Trade size (100 shares - 1 round lot)
            
    Example:
        >>> trades = alpaca_market_stocks_trades_latest('AAPL,MSFT,TSLA')
        >>> for symbol, trade in trades['trades'].items():
        ...     price = trade['p']
        ...     size = trade['s']
        ...     value = price * size
        ...     timestamp = trade['t']
        ...     
        ...     print(f"{symbol} Latest Trade:")
        ...     print(f"  Price: ${price:.2f}")
        ...     print(f"  Size: {size:,} shares")
        ...     print(f"  Value: ${value:,.2f}")
        ...     print(f"  Time: {timestamp}")
        
    Note:
        - Base prices: AAPL=$185.64, TSLA=$250.00, SPY=$450.00
        - Fixed 100-share trade sizes for consistency
        - Same timestamp for all symbols in single request
        - Useful for testing last price display and trade monitoring
    """
    symbol_list = symbols
    
    trades = {}
    for symbol in symbol_list:
        base_price = {"AAPL": 185.64, "TSLA": 250.0, "SPY": 450.0}.get(symbol, 100.0)
        trades[symbol] = {
            "t": "2024-01-02T21:00:00.029Z",
            "p": base_price,
            "s": 100
        }
    
    return {"trades": trades}


def get_most_actives(top: int = 10) -> Dict[str, Any]:
    """Generate mock list of most actively traded stocks by volume.
    
    Returns fixed mock data showing major stocks with high trading activity.
    Useful for testing volume-based screening logic and active stock
    identification workflows.
    
    Args:
        top: Number of stocks to return (ignored in mock - returns fixed list).
            
    Returns:
        Dict[str, Any]: Mock most active stocks containing:
            - most_actives: List of active stocks, each containing:
                - symbol: Stock symbol (AAPL, TSLA)
                - volume: Current day trading volume
                - trade_count: Number of individual trades
            
    Example:
        >>> actives = alpaca_market_screener_most_actives(20)
        >>> if actives:
        ...     stocks = actives['most_actives']
        ...     print(f"Top {len(stocks)} Most Active Stocks:")
        ...     for stock in stocks:
        ...         volume_millions = stock['volume'] / 1_000_000
        ...         print(f"{stock['symbol']}: {volume_millions:.1f}M shares")
        ...         print(f"  Trades: {stock['trade_count']:,}")
        
    Note:
        - Returns fixed data for AAPL (82.5M volume) and TSLA (67.2M volume)
        - Realistic volume and trade count numbers
        - Top parameter ignored in mock implementation
        - Useful for testing volume-based screening and momentum detection
    """
    return {
        "most_actives": [
            {"symbol": "AAPL", "volume": 82488200, "trade_count": 123456},
            {"symbol": "TSLA", "volume": 67234100, "trade_count": 98765}
        ]
    }


def get_top_gainers(top: int = 10) -> Dict[str, Any]:
    """Generate mock list of stocks with the biggest percentage gains.
    
    Returns fixed mock data showing technology stocks with strong positive
    performance. Useful for testing momentum screening and gainer
    identification functionality.
    
    Args:
        top: Number of stocks to return (ignored in mock - returns fixed list).
            
    Returns:
        Dict[str, Any]: Mock top gaining stocks containing:
            - top_gainers: List of gaining stocks, each containing:
                - symbol: Stock symbol (NVDA, AMD)
                - percent_change: Percentage gain from previous close
                - change: Absolute price change in dollars
                - price: Current stock price
            
    Example:
        >>> gainers = alpaca_market_screener_top_gainers(15)
        >>> if gainers:
        ...     stocks = gainers['top_gainers']
        ...     print(f"Top {len(stocks)} Gaining Stocks:")
        ...     for stock in stocks:
        ...         gain_pct = stock['percent_change']
        ...         price_change = stock['change']
        ...         current_price = stock['price']
        ...         
        ...         print(f"{stock['symbol']}:")
        ...         print(f"  Gain: +{gain_pct:.2f}% (+${price_change:.2f})")
        ...         print(f"  Price: ${current_price:.2f}")
        
    Note:
        - Returns fixed data for NVDA (+5.23%) and AMD (+3.87%)
        - Realistic percentage gains and price levels
        - Top parameter ignored in mock implementation
        - Useful for testing momentum strategies and trend identification
    """
    return {
        "top_gainers": [
            {"symbol": "NVDA", "percent_change": 5.23, "change": 12.45, "price": 250.67},
            {"symbol": "AMD", "percent_change": 3.87, "change": 4.32, "price": 115.89}
        ]
    }


def get_top_losers(top: int = 10) -> Dict[str, Any]:
    """Generate mock list of stocks with the biggest percentage losses.
    
    Returns fixed mock data showing a major stock with negative performance.
    Useful for testing contrarian screening and oversold opportunity
    identification functionality.
    
    Args:
        top: Number of stocks to return (ignored in mock - returns fixed list).
            
    Returns:
        Dict[str, Any]: Mock top losing stocks containing:
            - top_losers: List of losing stocks, each containing:
                - symbol: Stock symbol (META)
                - percent_change: Percentage loss from previous close (negative)
                - change: Absolute price change in dollars (negative)
                - price: Current stock price
            
    Example:
        >>> losers = alpaca_market_screener_top_losers(15)
        >>> if losers:
        ...     stocks = losers['top_losers']
        ...     print(f"Top {len(stocks)} Losing Stocks:")
        ...     for stock in stocks:
        ...         loss_pct = stock['percent_change']
        ...         price_change = stock['change']
        ...         current_price = stock['price']
        ...         
        ...         print(f"{stock['symbol']}:")
        ...         print(f"  Loss: {loss_pct:.2f}% (${price_change:.2f})")
        ...         print(f"  Price: ${current_price:.2f}")
        
    Note:
        - Returns fixed data for META (-3.21%)
        - Realistic percentage loss and price level
        - Top parameter ignored in mock implementation
        - Useful for testing contrarian strategies and oversold analysis
    """
    return {
        "top_losers": [
            {"symbol": "META", "percent_change": -3.21, "change": -8.76, "price": 264.33}
        ]
    }


def get_news(symbols: List[str] = "", start: Optional[str] = None, end: Optional[str] = None, sort: str = "desc", include_content: bool = True) -> Dict[str, Any]:
    """Generate mock financial news articles and market information.
    
    Returns fixed sample news article about Apple earnings. Useful for
    testing news display functionality, headline parsing, and news-driven
    analysis workflows without requiring live news feeds.
    
    Args:
        symbols: Symbol filter (ignored in mock - returns Apple news).
        start: Start date filter (ignored in mock).
        end: End date filter (ignored in mock).
        sort: Sort order (ignored in mock).
        include_content: Include full content (ignored in mock).
            
    Returns:
        Dict[str, Any]: Mock financial news containing:
            - news: List of news articles, each containing:
                - id: Unique article identifier
                - headline: Article headline
                - summary: Brief article summary
                - symbols: List of related stock symbols
                - created_at: Publication timestamp
            
    Example:
        >>> news = alpaca_market_news(['AAPL'])
        >>> if news:
        ...     articles = news['news']
        ...     print(f"Found {len(articles)} mock articles:")
        ...     for article in articles:
        ...         symbols = ', '.join(article.get('symbols', []))
        ...         print(f"Headline: {article['headline']}")
        ...         print(f"Summary: {article['summary']}")
        ...         print(f"Symbols: {symbols}")
        
    Note:
        - Returns single mock article about Apple Q4 earnings
        - Fixed content for consistent testing scenarios
        - All filter parameters ignored in mock implementation
        - Useful for testing news integration and display components
    """
    return {
        "news": [
            {
                "id": 24843171,
                "headline": "Apple Reports Strong Q4 Earnings",
                "summary": "Apple exceeded expectations...",
                "symbols": ["AAPL"],
                "created_at": "2024-01-02T10:30:00Z"
            }
        ]
    }

