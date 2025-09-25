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
    """Generate mock end-of-day historical OHLC prices with realistic data patterns.
    
    Creates simulated historical daily, weekly, or monthly price data that mimics
    real market behavior with proper OHLC relationships, volume patterns, and
    trending characteristics. Used for testing and development when real API access
    is not available.
    
    Args:
        symbol: Stock symbol in any format (e.g., 'AAPL', 'TSLA').
            Automatically appends '.US' suffix if missing for consistency.
            Different symbols generate different but deterministic price patterns.
        from_date: Start date for historical data in 'YYYY-MM-DD' format.
            If None, defaults to 30 days before to_date.
        to_date: End date for historical data in 'YYYY-MM-DD' format.
            If None, defaults to current date.
        period: Data frequency (currently only 'd' for daily is implemented).
            Future versions may support 'w' (weekly) and 'm' (monthly).
        order: Sort order for returned data.
            'a' for ascending (oldest first), 'd' for descending (newest first).
            
    Returns:
        Dict[str, Any]: List of mock price records, each containing:
            - date: Trading date in 'YYYY-MM-DD' format
            - open: Opening price for the day
            - high: Highest price during the day
            - low: Lowest price during the day
            - close: Closing price for the day
            - adjusted_close: Close price adjusted for splits/dividends (same as close)
            - volume: Trading volume (realistic random values)
            - On error: {'error': 'error_description'}
            
    Raises:
        Exception: If date parsing fails or other data generation errors occur.
        
    Example:
        >>> # Generate 30 days of Apple mock data
        >>> data = eodhd_eod_data('AAPL', '2024-01-01', '2024-01-31')
        >>> print(f"Generated {len(data)} trading days of mock data")
        >>> # Calculate simple metrics
        >>> prices = [d['close'] for d in data]
        >>> start_price, end_price = prices[0], prices[-1]
        >>> return_pct = (end_price / start_price - 1) * 100
        >>> print(f"Mock return: {return_pct:.2f}%")
        
    Note:
        - Uses numpy random with symbol-based seeding for reproducible results
        - Base prices: AAPL=$185.64, TSLA=$250.00, SPY=$450.00, others=$100.00
        - Generates realistic daily returns with ~2% volatility
        - Excludes weekends (only weekday trading)
        - Volume patterns based on normal distribution around 50M shares
        - High/low prices maintain proper OHLC relationships
    """
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
    """Generate mock real-time stock prices and current market data.
    
    Creates realistic simulated real-time market data including current price,
    daily changes, volume, and other live market metrics. Useful for testing
    applications that consume real-time market feeds.
    
    Args:
        symbol: Stock symbol in any format (e.g., 'AAPL', 'TSLA').
            Automatically appends '.US' suffix if missing for consistency.
            Different symbols generate different but deterministic patterns.
        fmt: Response format (currently only 'json' is supported).
            Maintained for API compatibility.
            
    Returns:
        Dict[str, Any]: Mock real-time market data containing:
            - code: Symbol with exchange suffix (e.g., 'AAPL.US')
            - timestamp: Current Unix timestamp
            - gmtoffset: GMT offset (always 0 for UTC)
            - open: Opening price for current session
            - high: Session high price
            - low: Session low price
            - close: Current/last price
            - volume: Current session volume
            - previousClose: Previous trading day close
            - change: Absolute price change from previous close
            - change_p: Percentage change from previous close
            - On error: {'error': 'error_description'}
            
    Raises:
        Exception: If data generation fails.
        
    Example:
        >>> # Get mock real-time data for Apple
        >>> data = eodhd_real_time('AAPL')
        >>> if 'error' not in data:
        ...     current_price = data['close']
        ...     change_pct = data['change_p']
        ...     volume_millions = data['volume'] / 1_000_000
        ...     
        ...     print(f"AAPL Mock Real-Time:")
        ...     print(f"Current: ${current_price:.2f}")
        ...     print(f"Change: {change_pct:+.2f}%")
        ...     print(f"Volume: {volume_millions:.1f}M")
        
    Note:
        - Uses symbol-based seeding for consistent mock data
        - Base prices: AAPL=$185.64, TSLA=$250.00, SPY=$450.00, others=$100.00
        - Simulates realistic intraday price movements with normal distribution
        - Volume based on realistic patterns (30-100M shares for major stocks)
        - High/low prices maintain 2% spread around current price
        - Timestamp reflects actual current time for realism
    """
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
    """Generate mock comprehensive company fundamental data and financial metrics.
    
    Creates realistic simulated fundamental information including company profile,
    financial statements, valuation ratios, and key business metrics. Returns
    detailed mock data for major stocks or generic data for others.
    
    Args:
        symbol: Stock symbol in any format (e.g., 'AAPL', 'TSLA').
            Automatically appends '.US' suffix if missing for consistency.
            
    Returns:
        Dict[str, Any]: Mock comprehensive fundamental data including:
            - General: Company profile, sector, industry, market cap, employees
            - Financials: Balance sheet, income statement, cash flow data
            - Valuation: PE ratio, PB ratio, EV/EBITDA, dividend yield
            - SharesStats: Shares outstanding, float, insider/institutional ownership
            - On error: {'error': 'error_description'}
            
    Raises:
        Exception: If mock data generation fails.
        
    Example:
        >>> data = eodhd_fundamentals('AAPL')
        >>> if 'error' not in data:
        ...     general = data.get('General', {})
        ...     print(f"Company: {general.get('Name', 'N/A')}")
        ...     print(f"Sector: {general.get('Sector', 'N/A')}")
        ...     print(f"Market Cap: ${general.get('MarketCapitalization', 0):,.0f}")
        ...     print(f"P/E Ratio: {general.get('PERatio', 'N/A')}")
        
    Note:
        - Provides detailed mock data for AAPL, generic data for other symbols
        - Mock financial data represents realistic but fictional values
        - Useful for testing fundamental analysis algorithms
        - Data structure matches EODHD API format exactly
    """
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
    """Generate mock historical dividend payment data with important dates.
    
    Creates realistic simulated dividend history for dividend-paying stocks.
    Returns mock quarterly dividend payments for major dividend stocks like
    AAPL and MSFT, empty list for non-dividend paying stocks.
    
    Args:
        symbol: Stock symbol in any format (e.g., 'AAPL', 'MSFT').
            Automatically appends '.US' suffix if missing for consistency.
        from_date: Start date filter (not implemented in mock - returns all data).
        to_date: End date filter (not implemented in mock - returns all data).
            
    Returns:
        List[Dict[str, Any]]: List of mock dividend records, each containing:
            - date: Ex-dividend date (when stock trades without dividend)
            - declarationDate: Date dividend was announced
            - recordDate: Date of record for dividend eligibility
            - paymentDate: Actual dividend payment date
            - value: Dividend amount per share
            - unadjustedValue: Original dividend amount
            - currency: Currency of dividend payment (USD)
            - period: Dividend period (Q1, Q2, etc.)
            - On error: {'error': 'error_description'}
            
    Raises:
        Exception: If mock data generation fails.
        
    Example:
        >>> dividends = eodhd_dividends('AAPL')
        >>> if dividends and 'error' not in dividends:
        ...     total_dividends = sum(d['value'] for d in dividends)
        ...     print(f"Mock total dividends: ${total_dividends:.2f} per share")
        ...     for div in dividends:
        ...         print(f"{div['date']}: ${div['value']:.2f} (Ex-Date)")
        
    Note:
        - Returns mock dividend data for AAPL and MSFT only
        - Other symbols return empty list (non-dividend paying)
        - Mock data includes realistic quarterly dividend progression
        - Useful for testing dividend analysis and income strategies
    """
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
    """Generate mock historical stock split data with split ratios.
    
    Creates realistic simulated stock split history for stocks that have
    historically executed splits. Returns mock 4:1 splits for major growth
    stocks like AAPL and TSLA.
    
    Args:
        symbol: Stock symbol in any format (e.g., 'AAPL', 'TSLA').
            Automatically appends '.US' suffix if missing for consistency.
        from_date: Start date filter (not implemented in mock - returns all data).
        to_date: End date filter (not implemented in mock - returns all data).
            
    Returns:
        List[Dict[str, Any]]: List of mock stock split records, each containing:
            - date: Effective date of the stock split
            - split: Split ratio in format 'new:old' (e.g., '4:1')
            - On error: {'error': 'error_description'}
            
    Raises:
        Exception: If mock data generation fails.
        
    Example:
        >>> splits = eodhd_splits('AAPL')
        >>> if splits and 'error' not in splits:
        ...     print(f"Found {len(splits)} mock stock splits:")
        ...     for split in splits:
        ...         print(f"{split['date']}: {split['split']} split")
        
    Note:
        - Returns mock split data for AAPL and TSLA only
        - Other symbols return empty list (no historical splits)
        - Mock splits show 4:1 ratios from 2020 and 2022
        - Useful for testing split-adjusted return calculations
    """
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
    """Generate mock technical analysis indicators for testing purposes.
    
    Creates simulated technical indicator values with realistic patterns.
    Generates time-series data for various indicators like RSI, SMA, MACD
    with appropriate value ranges and characteristics.
    
    Args:
        symbol: Stock symbol (not used in mock calculation but maintained for compatibility).
        function: Technical indicator to calculate. Examples:
            - 'rsi': Relative Strength Index (0-100 range)
            - 'sma': Simple Moving Average (price-based)
            - 'ema': Exponential Moving Average (price-based)
            - 'macd': Moving Average Convergence Divergence
        period: Calculation period (affects base value in mock).
        from_date: Start date for calculation in 'YYYY-MM-DD' format.
            If None, uses 30 days before to_date.
        to_date: End date for calculation in 'YYYY-MM-DD' format.
            If None, uses current date.
            
    Returns:
        List[Dict[str, Any]]: Time series of mock indicator values, each containing:
            - date: Trading date for the indicator value
            - [function]: Calculated indicator value (key matches function parameter)
            - On error: {'error': 'error_description'}
            
    Raises:
        Exception: If date parsing or mock calculation fails.
        
    Example:
        >>> # Generate mock 14-period RSI
        >>> rsi_data = eodhd_technical('AAPL', 'rsi', 14, '2024-01-01')
        >>> if rsi_data and 'error' not in rsi_data:
        ...     latest_rsi = rsi_data[-1]['rsi']
        ...     print(f"Mock RSI: {latest_rsi:.2f}")
        ...     if latest_rsi > 70:
        ...         print("Simulated overbought condition")
        ...     elif latest_rsi < 30:
        ...         print("Simulated oversold condition")
        
    Note:
        - Base values: RSI around 50, price indicators around $185
        - Values fluctuate with normal distribution for realism
        - Only includes weekday dates (excludes weekends)
        - Useful for testing technical analysis algorithms
    """
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
    """Generate mock stock screening results with sample companies.
    
    Returns a fixed set of mock screening results representing major
    technology stocks with realistic fundamental metrics. Useful for
    testing screening algorithms and UI components.
    
    Args:
        filters: Filter criteria (not implemented in mock - returns fixed results).
        limit: Maximum results (not implemented in mock - returns fixed set).
        offset: Results offset (not implemented in mock).
        signals: Technical signals (not implemented in mock).
            
    Returns:
        List[Dict[str, Any]]: Mock screening results, each containing:
            - code: Stock symbol with exchange suffix
            - name: Company name
            - market_cap: Market capitalization
            - pe_ratio: Price-to-earnings ratio
            - dividend_yield: Annual dividend yield
            - price: Current stock price
            - change_p: Daily percentage change
            - volume: Trading volume
            - On error: {'error': 'error_description'}
            
    Raises:
        Exception: If mock data generation fails.
        
    Example:
        >>> # Get mock screening results
        >>> results = eodhd_screener()
        >>> if results and 'error' not in results:
        ...     print(f"Found {len(results)} mock stocks:")
        ...     for stock in results:
        ...         print(f"{stock['code']}: {stock['name']}")
        ...         print(f"  P/E: {stock['pe_ratio']}, Yield: {stock['dividend_yield']:.2%}")
        
    Note:
        - Returns fixed mock data for AAPL and MSFT
        - Realistic market cap, P/E ratios, and dividend yields
        - Useful for testing screener UI and filtering logic
        - Filter parameters ignored in mock implementation
    """
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
    """Generate mock search results for stock and instrument lookup.
    
    Returns mock search results based on query content. Provides basic
    matching for common queries and always includes Apple as a default result.
    Useful for testing search functionality and symbol discovery.
    
    Args:
        query: Search term - can be stock symbol, company name, or partial match.
            Case-insensitive matching implemented for 'microsoft' and 'msft'.
            
    Returns:
        List[Dict[str, Any]]: Mock search results, each containing:
            - Code: Full symbol with exchange suffix (e.g., 'AAPL.US')
            - Name: Full company name
            - Country: Country where instrument is listed (USA)
            - Exchange: Exchange where instrument trades (NASDAQ)
            - Currency: Trading currency (USD)
            - Type: Instrument type (Common Stock)
            - On error: {'error': 'error_description'}
            
    Raises:
        Exception: If mock search fails.
        
    Example:
        >>> # Search for Microsoft
        >>> results = eodhd_search('Microsoft')
        >>> if results and 'error' not in results:
        ...     print(f"Found {len(results)} matches:")
        ...     for result in results:
        ...         print(f"{result['Code']}: {result['Name']}")
        ...         print(f"  Exchange: {result['Exchange']} ({result['Country']})")
        
    Note:
        - Always returns Apple (AAPL) as baseline result
        - Adds Microsoft (MSFT) for 'microsoft' or 'msft' queries
        - Useful for testing search UI and symbol lookup workflows
        - Case-insensitive matching for implemented queries
    """
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
    """Generate mock list of supported stock exchanges.
    
    Returns a fixed set of major US stock exchanges for testing.
    Useful for testing exchange selection UI and symbol formatting
    logic without requiring API access.
    
    Returns:
        List[Dict[str, Any]]: Mock list of exchanges, each containing:
            - Name: Full exchange name
            - Code: Exchange code used in symbols
            - OperatingMIC: Market Identifier Code
            - Country: Country where exchange is located (USA)
            - Currency: Primary trading currency (USD)
            - CountryISO2: 2-letter ISO country code (US)
            - CountryISO3: 3-letter ISO country code (USA)
            
    Example:
        >>> exchanges = eodhd_exchanges_list()
        >>> print(f"Mock exchanges available: {len(exchanges)}")
        >>> for ex in exchanges:
        ...     print(f"{ex['Code']}: {ex['Name']} ({ex['Currency']})")
        
    Note:
        - Returns fixed mock data for NYSE and NASDAQ only
        - Useful for testing exchange-related functionality
        - Always returns the same consistent results
    """
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
    """Generate mock list of tradeable symbols for a specific exchange.
    
    Returns a fixed set of major tech stocks as sample symbols for any
    exchange query. Useful for testing symbol listing functionality
    and exchange-specific operations.
    
    Args:
        exchange: Exchange code (not used in mock - returns fixed symbols).
            
    Returns:
        List[Dict[str, Any]]: Mock list of symbols, each containing:
            - Code: Full symbol with exchange suffix
            - Name: Company or instrument name
            - Country: Country (USA)
            - Exchange: Exchange code (NASDAQ)
            - Currency: Trading currency (USD)
            - Type: Instrument type (Common Stock)
            - Isin: International Securities Identification Number
            
    Example:
        >>> symbols = eodhd_exchange_symbols('NASDAQ')
        >>> print(f"Mock symbols: {len(symbols)}")
        >>> for symbol in symbols:
        ...     print(f"{symbol['Code']}: {symbol['Name']} ({symbol['Type']})")
        
    Note:
        - Returns fixed mock data for AAPL and MSFT regardless of exchange
        - Useful for testing symbol selection and listing UI
        - Exchange parameter ignored in mock implementation
    """
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


def alpaca_trading_positions() -> List[Dict[str, Any]]:
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


def alpaca_trading_position(symbol: str) -> Dict[str, Any]:
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


def alpaca_trading_orders(status: str = "open", limit: int = 100, after: Optional[str] = None, until: Optional[str] = None, direction: str = "desc", nested: bool = False) -> List[Dict[str, Any]]:
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


def alpaca_trading_portfolio_history(period: str = "1D", timeframe: str = "15Min", end_date: Optional[str] = None, extended_hours: bool = False) -> Dict[str, Any]:
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


def alpaca_trading_clock() -> Dict[str, Any]:
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
def alpaca_market_stocks_bars(symbols: str, timeframe: str = "1Day", start: Optional[str] = None, end: Optional[str] = None) -> Dict[str, Any]:
    """Generate mock historical OHLC price bars for multiple stocks.
    
    Creates realistic simulated time-series price data including open, high,
    low, close, and volume for specified symbols. Each symbol gets unique
    but deterministic price patterns based on symbol-based seeding.
    
    Args:
        symbols: Comma-separated list of stock symbols (e.g., 'AAPL,TSLA,MSFT').
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
        >>> bars = alpaca_market_stocks_bars('AAPL,GOOGL,MSFT', '1Day', '2024-01-01')
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
    """Generate mock comprehensive current market snapshots for multiple stocks.
    
    Creates simulated real-time market data including latest quotes, trades,
    and daily bars for each requested symbol. Uses consistent base prices
    per symbol for predictable testing.
    
    Args:
        symbols: Comma-separated list of stock symbols (e.g., 'AAPL,TSLA,SPY').
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
    """Generate mock latest bid/ask quotes for multiple stocks.
    
    Creates simulated current market maker quotes with realistic spreads
    and sizes. Uses base prices per symbol with tight spreads typical
    of liquid stocks.
    
    Args:
        symbols: Comma-separated list of stock symbols (e.g., 'AAPL,TSLA,SPY').
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
    """Generate mock latest trade execution data for multiple stocks.
    
    Creates simulated most recent trade transactions using base prices
    per symbol. Shows realistic trade sizes and fixed timestamps for
    consistent testing scenarios.
    
    Args:
        symbols: Comma-separated list of stock symbols (e.g., 'AAPL,TSLA,SPY').
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


def alpaca_market_screener_top_gainers(top: int = 10) -> Dict[str, Any]:
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


def alpaca_market_screener_top_losers(top: int = 10) -> Dict[str, Any]:
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


def alpaca_market_news(symbols: str = "", start: Optional[str] = None, end: Optional[str] = None, sort: str = "desc", include_content: bool = True) -> Dict[str, Any]:
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
        >>> news = alpaca_market_news('AAPL')
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


# Registry of all mock financial functions - For Testing and Development
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