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


# EODHD API Mock Functions
def eodhd_eod_data(symbol: str, from_date: Optional[str] = None, to_date: Optional[str] = None, period: str = "d", order: str = "a") -> Dict[str, Any]:
    """End-of-day historical OHLC prices with adjustments"""
    try:
        if '.US' not in symbol:
            symbol = f"{symbol.upper()}.US"
        
        base_symbol = symbol.split('.')[0]
        
        # Date range
        if not to_date:
            end_date = datetime.now()
        else:
            end_date = datetime.strptime(to_date, "%Y-%m-%d")
        if not from_date:
            start_date = end_date - timedelta(days=30)
        else:
            start_date = datetime.strptime(from_date, "%Y-%m-%d")
        
        # Generate mock data
        np.random.seed(hash(base_symbol) % 2**32)
        base_price = {"AAPL": 185.64, "TSLA": 250.0, "SPY": 450.0}.get(base_symbol, 100.0)
        
        days = (end_date - start_date).days
        data = []
        
        current_price = base_price
        for i in range(days + 1):
            date = start_date + timedelta(days=i)
            if date.weekday() < 5:  # Weekdays only
                daily_return = np.random.normal(0.001, 0.02)
                open_price = current_price
                close_price = open_price * (1 + daily_return)
                high_price = max(open_price, close_price) * (1 + abs(np.random.normal(0, 0.01)))
                low_price = min(open_price, close_price) * (1 - abs(np.random.normal(0, 0.01)))
                volume = int(np.random.normal(50_000_000, 20_000_000))
                
                data.append({
                    "date": date.strftime("%Y-%m-%d"),
                    "open": round(open_price, 2),
                    "high": round(high_price, 2),
                    "low": round(low_price, 2),
                    "close": round(close_price, 2),
                    "adjusted_close": round(close_price, 2),
                    "volume": max(volume, 1_000_000)
                })
                current_price = close_price
        
        if order == "d":
            data.reverse()
        
        return data
        
    except Exception as e:
        return {"error": f"EOD data request failed: {str(e)}"}


def eodhd_real_time(symbol: str, fmt: str = "json") -> Dict[str, Any]:
    """Real-time stock prices and market data"""
    try:
        if '.US' not in symbol:
            symbol = f"{symbol.upper()}.US"
        
        base_symbol = symbol.split('.')[0]
        base_price = {"AAPL": 185.64, "TSLA": 250.0, "SPY": 450.0}.get(base_symbol, 100.0)
        
        np.random.seed(hash(base_symbol) % 2**32)
        change = np.random.normal(0, 0.02) * base_price
        current_price = base_price + change
        
        return {
            "code": symbol,
            "timestamp": int(datetime.now().timestamp()),
            "gmtoffset": 0,
            "open": round(base_price, 2),
            "high": round(current_price * 1.02, 2),
            "low": round(current_price * 0.98, 2),
            "close": round(current_price, 2),
            "volume": int(np.random.normal(50_000_000, 20_000_000)),
            "previousClose": round(base_price, 2),
            "change": round(change, 2),
            "change_p": round((change / base_price) * 100, 2)
        }
        
    except Exception as e:
        return {"error": f"Real-time data request failed: {str(e)}"}


def eodhd_fundamentals(symbol: str) -> Dict[str, Any]:
    """Company fundamental data, financials, ratios"""
    try:
        if '.US' not in symbol:
            symbol = f"{symbol.upper()}.US"
        
        base_symbol = symbol.split('.')[0]
        
        mock_data = {
            "AAPL": {
                "General": {
                    "Code": "AAPL",
                    "Type": "Common Stock",
                    "Name": "Apple Inc",
                    "Exchange": "NASDAQ",
                    "CurrencyCode": "USD",
                    "CurrencyName": "US Dollar",
                    "CurrencySymbol": "$",
                    "CountryName": "USA",
                    "CountryISO": "US",
                    "ISIN": "US0378331005",
                    "CUSIP": "037833100",
                    "Description": "Apple Inc. designs, manufactures, and markets smartphones...",
                    "Sector": "Technology",
                    "Industry": "Consumer Electronics",
                    "FullTimeEmployees": 164000,
                    "MarketCapitalization": 2875340000000,
                    "SharesOutstanding": 15441883000,
                    "DividendYield": 0.0044,
                    "EPS": 6.13,
                    "PERatio": 30.29,
                    "Beta": 1.286
                },
                "Financials": {
                    "Balance_Sheet": {
                        "quarterly": {
                            "2023-09-30": {
                                "totalAssets": "352755000000",
                                "totalLiab": "290020000000",
                                "totalStockholderEquity": "62735000000",
                                "cash": "29965000000",
                                "shortTermInvestments": "31590000000"
                            }
                        }
                    },
                    "Income_Statement": {
                        "quarterly": {
                            "2023-09-30": {
                                "totalRevenue": "89498000000",
                                "costOfRevenue": "54428000000",
                                "grossProfit": "35070000000",
                                "netIncome": "22956000000"
                            }
                        }
                    },
                    "Cash_Flow": {
                        "quarterly": {
                            "2023-09-30": {
                                "operatingCashFlow": "26321000000",
                                "capitalExpenditures": "-3736000000",
                                "freeCashFlow": "22585000000"
                            }
                        }
                    }
                },
                "Valuation": {
                    "TrailingPE": 30.29,
                    "ForwardPE": 28.15,
                    "PriceSalesTrailing12Months": 8.16,
                    "PriceBookMRQ": 46.21,
                    "EnterpriseValueRevenue": 7.89,
                    "EnterpriseValueEBITDA": 23.45
                },
                "SharesStats": {
                    "SharesOutstanding": 15441883000,
                    "SharesFloat": 15441883000,
                    "PercentInsiders": 0.07,
                    "PercentInstitutions": 61.31,
                    "SharesShort": 111520000,
                    "SharesShortPriorMonth": 113250000
                }
            }
        }
        
        return mock_data.get(base_symbol, {
            "General": {
                "Code": base_symbol,
                "Name": f"{base_symbol} Corp",
                "Exchange": "NYSE",
                "Sector": "Technology",
                "Industry": "Software"
            }
        })
        
    except Exception as e:
        return {"error": f"Fundamentals request failed: {str(e)}"}


def eodhd_dividends(symbol: str, from_date: Optional[str] = None, to_date: Optional[str] = None) -> List[Dict[str, Any]]:
    """Dividend payment history with ex-dates"""
    try:
        if '.US' not in symbol:
            symbol = f"{symbol.upper()}.US"
        
        base_symbol = symbol.split('.')[0]
        
        if base_symbol in ['AAPL', 'MSFT']:
            return [
                {
                    "date": "2024-02-09",
                    "declarationDate": "2024-02-01",
                    "recordDate": "2024-02-12",
                    "paymentDate": "2024-02-15",
                    "period": "Q1",
                    "value": 0.24,
                    "unadjustedValue": 0.24,
                    "currency": "USD"
                },
                {
                    "date": "2024-05-10",
                    "declarationDate": "2024-05-02",
                    "recordDate": "2024-05-13",
                    "paymentDate": "2024-05-16",
                    "period": "Q2",
                    "value": 0.25,
                    "unadjustedValue": 0.25,
                    "currency": "USD"
                }
            ]
        return []
        
    except Exception as e:
        return {"error": f"Dividends request failed: {str(e)}"}


def eodhd_splits(symbol: str, from_date: Optional[str] = None, to_date: Optional[str] = None) -> List[Dict[str, Any]]:
    """Stock split history with ratios"""
    try:
        if '.US' not in symbol:
            symbol = f"{symbol.upper()}.US"
        
        base_symbol = symbol.split('.')[0]
        
        if base_symbol in ['AAPL', 'TSLA']:
            return [
                {"date": "2020-08-31", "split": "4:1"},
                {"date": "2022-06-09", "split": "4:1"}
            ]
        return []
        
    except Exception as e:
        return {"error": f"Splits request failed: {str(e)}"}


def eodhd_technical(symbol: str, function: str, period: int = 14, from_date: Optional[str] = None, to_date: Optional[str] = None) -> List[Dict[str, Any]]:
    """Technical analysis indicators"""
    try:
        if not to_date:
            end_date = datetime.now()
        else:
            end_date = datetime.strptime(to_date, "%Y-%m-%d")
        if not from_date:
            start_date = end_date - timedelta(days=30)
        else:
            start_date = datetime.strptime(from_date, "%Y-%m-%d")
        
        data = []
        current_date = start_date
        base_value = 50 if function == 'rsi' else 185.42
        
        while current_date <= end_date:
            if current_date.weekday() < 5:
                variation = np.random.normal(0, 0.1)
                value = base_value + variation
                data.append({
                    "date": current_date.strftime("%Y-%m-%d"),
                    function: round(value, 2)
                })
            current_date += timedelta(days=1)
        
        return data
        
    except Exception as e:
        return {"error": f"Technical analysis request failed: {str(e)}"}


def eodhd_screener(filters: str = "", limit: int = 50, offset: int = 0, signals: str = "") -> List[Dict[str, Any]]:
    """Stock screener with custom filters"""
    try:
        return [
            {
                "code": "AAPL.US",
                "name": "Apple Inc",
                "market_cap": 2875340000000,
                "pe_ratio": 30.29,
                "dividend_yield": 0.0044,
                "price": 185.64,
                "change_p": -2.27,
                "volume": 82488200
            },
            {
                "code": "MSFT.US",
                "name": "Microsoft Corporation",
                "market_cap": 2789450000000,
                "pe_ratio": 35.67,
                "dividend_yield": 0.0072,
                "price": 374.58,
                "change_p": 1.42,
                "volume": 19567800
            }
        ]
        
    except Exception as e:
        return {"error": f"Screener request failed: {str(e)}"}


def eodhd_search(query: str) -> List[Dict[str, Any]]:
    """Search for stocks by name or symbol"""
    try:
        results = [
            {
                "Code": "AAPL.US",
                "Name": "Apple Inc",
                "Country": "USA",
                "Exchange": "NASDAQ",
                "Currency": "USD",
                "Type": "Common Stock"
            }
        ]
        
        if query.upper() in ['MICROSOFT', 'MSFT']:
            results.append({
                "Code": "MSFT.US",
                "Name": "Microsoft Corporation",
                "Country": "USA",
                "Exchange": "NASDAQ",
                "Currency": "USD",
                "Type": "Common Stock"
            })
        
        return results
        
    except Exception as e:
        return {"error": f"Search request failed: {str(e)}"}


def eodhd_exchanges_list() -> List[Dict[str, Any]]:
    """List all supported stock exchanges"""
    return [
        {
            "Name": "New York Stock Exchange",
            "Code": "NYSE",
            "OperatingMIC": "XNYS",
            "Country": "USA",
            "Currency": "USD",
            "CountryISO2": "US",
            "CountryISO3": "USA"
        },
        {
            "Name": "NASDAQ Global Market",
            "Code": "NASDAQ",
            "OperatingMIC": "XNAS",
            "Country": "USA",
            "Currency": "USD",
            "CountryISO2": "US",
            "CountryISO3": "USA"
        }
    ]


def eodhd_exchange_symbols(exchange: str) -> List[Dict[str, Any]]:
    """Get all tradeable symbols for specific exchange"""
    return [
        {
            "Code": "AAPL.US",
            "Name": "Apple Inc",
            "Country": "USA",
            "Exchange": "NASDAQ",
            "Currency": "USD",
            "Type": "Common Stock",
            "Isin": "US0378331005"
        },
        {
            "Code": "MSFT.US",
            "Name": "Microsoft Corporation",
            "Country": "USA",
            "Exchange": "NASDAQ",
            "Currency": "USD",
            "Type": "Common Stock",
            "Isin": "US5949181045"
        }
    ]


# Alpaca Trading API Mock Functions
def alpaca_trading_account() -> Dict[str, Any]:
    """Get account information including buying power, equity, cash balance"""
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


def alpaca_trading_positions() -> List[Dict[str, Any]]:
    """Get all open positions with P&L, market values, quantities"""
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


def alpaca_trading_position(symbol: str) -> Dict[str, Any]:
    """Get specific position details for one symbol"""
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


def alpaca_trading_orders(status: str = "open", limit: int = 100, after: Optional[str] = None, until: Optional[str] = None, direction: str = "desc", nested: bool = False) -> List[Dict[str, Any]]:
    """Get order history and status"""
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


def alpaca_trading_portfolio_history(period: str = "1D", timeframe: str = "15Min", end_date: Optional[str] = None, extended_hours: bool = False) -> Dict[str, Any]:
    """Portfolio performance history showing value changes over time"""
    return {
        "timestamp": [1580826600000, 1580827500000, 1580828400000],
        "equity": [27423.73, 27408.19, 27515.97],
        "profit_loss": [11.8, -3.74, 104.04],
        "profit_loss_pct": [0.000430469507, -0.0001364369455, 0.003790983306],
        "base_value": 27411.93,
        "timeframe": timeframe
    }


def alpaca_trading_clock() -> Dict[str, Any]:
    """Market clock status"""
    return {
        "timestamp": "2024-01-02T21:00:00.000Z",
        "is_open": False,
        "next_open": "2024-01-03T14:30:00.000Z",
        "next_close": "2024-01-03T21:00:00.000Z"
    }


# Alpaca Market Data API Mock Functions  
def alpaca_market_stocks_bars(symbols: str, timeframe: str = "1Day", start: Optional[str] = None, end: Optional[str] = None) -> Dict[str, Any]:
    """Historical OHLC price bars for stocks"""
    symbol_list = [s.strip().upper() for s in symbols.split(',')]
    
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


def alpaca_market_stocks_snapshots(symbols: str) -> Dict[str, Any]:
    """Current market snapshot with all data"""
    symbol_list = [s.strip().upper() for s in symbols.split(',')]
    
    snapshots = {}
    for symbol in symbol_list:
        base_price = {"AAPL": 185.64, "TSLA": 250.0, "SPY": 450.0}.get(symbol, 100.0)
        snapshots[symbol] = {
            "latestTrade": {"p": base_price, "s": 100, "t": "2024-01-02T21:00:00Z"},
            "latestQuote": {"bp": base_price - 0.01, "ap": base_price + 0.01, "t": "2024-01-02T21:00:00Z"},
            "dailyBar": {"o": base_price, "h": base_price * 1.02, "l": base_price * 0.98, "c": base_price, "v": 82488200}
        }
    
    return {"snapshots": snapshots}


def alpaca_market_stocks_quotes_latest(symbols: str) -> Dict[str, Any]:
    """Latest bid/ask quotes for stocks"""
    symbol_list = [s.strip().upper() for s in symbols.split(',')]
    
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


def alpaca_market_stocks_trades_latest(symbols: str) -> Dict[str, Any]:
    """Latest trade data for stocks"""
    symbol_list = [s.strip().upper() for s in symbols.split(',')]
    
    trades = {}
    for symbol in symbol_list:
        base_price = {"AAPL": 185.64, "TSLA": 250.0, "SPY": 450.0}.get(symbol, 100.0)
        trades[symbol] = {
            "t": "2024-01-02T21:00:00.029Z",
            "p": base_price,
            "s": 100
        }
    
    return {"trades": trades}


def alpaca_market_screener_most_actives(top: int = 10) -> Dict[str, Any]:
    """Screen for most active stocks by volume"""
    return {
        "most_actives": [
            {"symbol": "AAPL", "volume": 82488200, "trade_count": 123456},
            {"symbol": "TSLA", "volume": 67234100, "trade_count": 98765}
        ]
    }


def alpaca_market_screener_top_gainers(top: int = 10) -> Dict[str, Any]:
    """Screen for biggest stock gainers"""
    return {
        "top_gainers": [
            {"symbol": "NVDA", "percent_change": 5.23, "change": 12.45, "price": 250.67},
            {"symbol": "AMD", "percent_change": 3.87, "change": 4.32, "price": 115.89}
        ]
    }


def alpaca_market_screener_top_losers(top: int = 10) -> Dict[str, Any]:
    """Screen for biggest stock losers"""
    return {
        "top_losers": [
            {"symbol": "META", "percent_change": -3.21, "change": -8.76, "price": 264.33}
        ]
    }


def alpaca_market_news(symbols: str = "", start: Optional[str] = None, end: Optional[str] = None, sort: str = "desc", include_content: bool = True) -> Dict[str, Any]:
    """Financial news articles"""
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


# Registry of all mock financial functions
MOCK_FINANCIAL_FUNCTIONS = {
    # EODHD API
    'eodhd_eod_data': eodhd_eod_data,
    'eodhd_real_time': eodhd_real_time,
    'eodhd_fundamentals': eodhd_fundamentals,
    'eodhd_dividends': eodhd_dividends,
    'eodhd_splits': eodhd_splits,
    'eodhd_technical': eodhd_technical,
    'eodhd_screener': eodhd_screener,
    'eodhd_search': eodhd_search,
    'eodhd_exchanges_list': eodhd_exchanges_list,
    'eodhd_exchange_symbols': eodhd_exchange_symbols,
    
    # Alpaca Trading API
    'alpaca_trading_account': alpaca_trading_account,
    'alpaca_trading_positions': alpaca_trading_positions,
    'alpaca_trading_position': alpaca_trading_position,
    'alpaca_trading_orders': alpaca_trading_orders,
    'alpaca_trading_portfolio_history': alpaca_trading_portfolio_history,
    'alpaca_trading_clock': alpaca_trading_clock,
    
    # Alpaca Market Data API
    'alpaca_market_stocks_bars': alpaca_market_stocks_bars,
    'alpaca_market_stocks_snapshots': alpaca_market_stocks_snapshots,
    'alpaca_market_stocks_quotes_latest': alpaca_market_stocks_quotes_latest,
    'alpaca_market_stocks_trades_latest': alpaca_market_stocks_trades_latest,
    'alpaca_market_screener_most_actives': alpaca_market_screener_most_actives,
    'alpaca_market_screener_top_gainers': alpaca_market_screener_top_gainers,
    'alpaca_market_screener_top_losers': alpaca_market_screener_top_losers,
    'alpaca_market_news': alpaca_market_news,
}