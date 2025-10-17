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
def get_eod_data(symbol: str, from_date: Optional[str] = None, to_date: Optional[str] = None, period: str = "d", order: str = "a") -> Dict[str, Any]:
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


def get_real_time(symbol: str, fmt: str = "json") -> Dict[str, Any]:
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


def get_fundamentals(symbol: str) -> Dict[str, Any]:
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


def get_dividends(symbol: str, from_date: Optional[str] = None, to_date: Optional[str] = None) -> List[Dict[str, Any]]:
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


def get_splits(symbol: str, from_date: Optional[str] = None, to_date: Optional[str] = None) -> List[Dict[str, Any]]:
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


def get_technical(symbol: str, function: str, period: int = 14, from_date: Optional[str] = None, to_date: Optional[str] = None) -> List[Dict[str, Any]]:
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


def get_screener(filters: str = "", limit: int = 50, offset: int = 0, signals: str = "") -> List[Dict[str, Any]]:
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


def search_symbols(query: str) -> List[Dict[str, Any]]:
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


def get_exchanges_list() -> List[Dict[str, Any]]:
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


def get_exchange_symbols(exchange: str) -> List[Dict[str, Any]]:
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

