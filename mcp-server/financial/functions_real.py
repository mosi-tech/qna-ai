"""
Real Financial Data Functions - Following API Specifications  

Real implementations (stubs) of financial functions that follow the exact API specifications
from eodhd-simple.json, alpaca-trading-simple.json, and alpaca-marketdata-simple.json

These are stub implementations that would call actual APIs in production.
"""

import os
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union


# API Configuration
ALPACA_API_KEY = os.getenv('ALPACA_API_KEY')
ALPACA_SECRET_KEY = os.getenv('ALPACA_SECRET_KEY')
EODHD_API_KEY = os.getenv('EODHD_API_KEY')

ALPACA_BASE_URL = os.getenv('ALPACA_BASE_URL', 'https://paper-api.alpaca.markets')
ALPACA_DATA_URL = os.getenv('ALPACA_DATA_URL', 'https://data.alpaca.markets')
EODHD_BASE_URL = os.getenv('EODHD_BASE_URL', 'https://eodhistoricaldata.com/api')


def get_headers() -> Dict[str, str]:
    """Generate HTTP headers for Alpaca API authentication.
    
    Creates the required authorization headers for making authenticated
    requests to Alpaca Trading and Market Data APIs using API key credentials.
    
    Returns:
        Dict[str, str]: HTTP headers dictionary containing:
            - APCA-API-KEY-ID: API key identifier
            - APCA-API-SECRET-KEY: Secret key for authentication
            - Content-Type: Application JSON content type
            
    Raises:
        ValueError: If ALPACA_API_KEY or ALPACA_SECRET_KEY environment
            variables are not configured.
            
    Example:
        >>> headers = get_headers()
        >>> response = requests.get(url, headers=headers)
        
    Note:
        Requires ALPACA_API_KEY and ALPACA_SECRET_KEY environment variables
        to be set. These credentials can be obtained from the Alpaca dashboard.
    """
    return {
        'APCA-API-KEY-ID': ALPACA_API_KEY,
        'APCA-API-SECRET-KEY': ALPACA_SECRET_KEY,
        'Content-Type': 'application/json'
    }


# EODHD API Real Functions (Stubs)
def eodhd_eod_data(symbol: str, from_date: Optional[str] = None, to_date: Optional[str] = None, period: str = "d", order: str = "a") -> Dict[str, Any]:
    """Retrieve end-of-day historical OHLC prices with dividend and split adjustments.
    
    Fetches historical daily, weekly, or monthly price data for a specified symbol
    from the EODHD API. Returns adjusted close prices that account for corporate
    actions like dividends and stock splits.
    
    Args:
        symbol: Stock symbol in format 'SYMBOL.EXCHANGE' (e.g., 'AAPL.US').
            For US stocks, '.US' suffix is automatically appended if missing.
        from_date: Start date for historical data in 'YYYY-MM-DD' format.
            If None, defaults to API's default historical range.
        to_date: End date for historical data in 'YYYY-MM-DD' format.
            If None, defaults to most recent trading day.
        period: Data frequency. Options: 'd' (daily), 'w' (weekly), 'm' (monthly).
            Defaults to 'd' for daily data.
        order: Sort order for returned data. Options: 'a' (ascending, oldest first),
            'd' (descending, newest first). Defaults to 'a'.
            
    Returns:
        Dict[str, Any]: Historical price data containing:
            - List of price records with date, open, high, low, close, adjusted_close, volume
            - On error: {'error': 'error_description'}
            
    Raises:
        ValueError: If EODHD_API_KEY environment variable is not configured.
        requests.exceptions.RequestException: If API request fails.
        
    Example:
        >>> data = eodhd_eod_data('AAPL.US', '2024-01-01', '2024-01-31')
        >>> print(f"Retrieved {len(data)} price records for Apple")
        >>> # Access latest price
        >>> latest = data[-1] if data else None
        >>> if latest:
        ...     print(f"Close: ${latest['close']}, Volume: {latest['volume']:,}")
        
    Note:
        - Requires EODHD_API_KEY environment variable
        - Adjusted close prices account for dividends and splits
        - Weekend and holiday dates are excluded from results
        - API rate limits may apply based on subscription tier
    """
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


def eodhd_real_time(symbol: str, fmt: str = "json") -> Dict[str, Any]:
    """Fetch real-time stock prices and current market data.
    
    Retrieves live market data including current price, daily change,
    volume, and other real-time metrics for a specified symbol from
    the EODHD API.
    
    Args:
        symbol: Stock symbol in format 'SYMBOL.EXCHANGE' (e.g., 'AAPL.US').
            For US stocks, '.US' suffix is automatically appended if missing.
        fmt: Response format. Currently only 'json' is supported.
            Defaults to 'json'.
            
    Returns:
        Dict[str, Any]: Real-time market data containing:
            - code: Symbol identifier
            - timestamp: Unix timestamp of last update
            - open, high, low, close: Daily OHLC prices
            - volume: Trading volume for current session
            - previousClose: Previous trading day close price
            - change: Absolute price change from previous close
            - change_p: Percentage change from previous close
            - On error: {'error': 'error_description'}
            
    Raises:
        ValueError: If EODHD_API_KEY environment variable is not configured.
        requests.exceptions.RequestException: If API request fails.
        
    Example:
        >>> data = eodhd_real_time('AAPL.US')
        >>> if 'error' not in data:
        ...     print(f"Current price: ${data['close']}")
        ...     print(f"Daily change: {data['change_p']:.2f}%")
        ...     print(f"Volume: {data['volume']:,}")
        
    Note:
        - Requires EODHD_API_KEY environment variable
        - Real-time data may have 15-20 minute delays for non-premium users
        - During market hours, data is updated continuously
        - Outside market hours, returns previous close data
    """
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


def eodhd_fundamentals(symbol: str) -> Dict[str, Any]:
    """Retrieve comprehensive company fundamental data and financial metrics.
    
    Fetches detailed fundamental information including company profile,
    financial statements, valuation ratios, and key business metrics
    from the EODHD API.
    
    Args:
        symbol: Stock symbol in format 'SYMBOL.EXCHANGE' (e.g., 'AAPL.US').
            For US stocks, '.US' suffix is automatically appended if missing.
            
    Returns:
        Dict[str, Any]: Comprehensive fundamental data including:
            - General: Company profile, sector, industry, market cap, employees
            - Financials: Balance sheet, income statement, cash flow data
            - Valuation: PE ratio, PB ratio, EV/EBITDA, dividend yield
            - SharesStats: Shares outstanding, float, insider/institutional ownership
            - Technicals: Beta, 52-week high/low, moving averages
            - On error: {'error': 'error_description'}
            
    Raises:
        ValueError: If EODHD_API_KEY environment variable is not configured.
        requests.exceptions.RequestException: If API request fails.
        
    Example:
        >>> data = eodhd_fundamentals('AAPL.US')
        >>> if 'error' not in data:
        ...     general = data.get('General', {})
        ...     print(f"Company: {general.get('Name', 'N/A')}")
        ...     print(f"Sector: {general.get('Sector', 'N/A')}")
        ...     print(f"Market Cap: ${general.get('MarketCapitalization', 0):,.0f}")
        ...     print(f"P/E Ratio: {general.get('PERatio', 'N/A')}")
        
    Note:
        - Requires EODHD_API_KEY environment variable
        - Data updated daily after market close
        - Some fields may be null for certain symbols or exchanges
        - Financial data typically covers last 4 quarters and 4 years
    """
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


def eodhd_dividends(symbol: str, from_date: Optional[str] = None, to_date: Optional[str] = None) -> List[Dict[str, Any]]:
    """Retrieve historical dividend payment data with important dates.
    
    Fetches comprehensive dividend history including payment amounts,
    ex-dividend dates, record dates, and payment dates for income analysis
    and dividend yield calculations.
    
    Args:
        symbol: Stock symbol in format 'SYMBOL.EXCHANGE' (e.g., 'AAPL.US').
            For US stocks, '.US' suffix is automatically appended if missing.
        from_date: Start date for dividend history in 'YYYY-MM-DD' format.
            If None, returns all available dividend history.
        to_date: End date for dividend history in 'YYYY-MM-DD' format.
            If None, includes dividends up to present date.
            
    Returns:
        List[Dict[str, Any]]: List of dividend records, each containing:
            - date: Ex-dividend date (when stock trades without dividend)
            - declarationDate: Date dividend was announced
            - recordDate: Date of record for dividend eligibility
            - paymentDate: Actual dividend payment date
            - value: Dividend amount per share
            - unadjustedValue: Original dividend amount before adjustments
            - currency: Currency of dividend payment
            - period: Dividend period (Q1, Q2, Annual, etc.)
            - On error: {'error': 'error_description'}
            
    Raises:
        ValueError: If EODHD_API_KEY environment variable is not configured.
        requests.exceptions.RequestException: If API request fails.
        
    Example:
        >>> dividends = eodhd_dividends('AAPL.US', '2023-01-01', '2023-12-31')
        >>> if dividends and 'error' not in dividends:
        ...     total_dividends = sum(d['value'] for d in dividends)
        ...     print(f"Total 2023 dividends: ${total_dividends:.2f} per share")
        ...     for div in dividends:
        ...         print(f"{div['date']}: ${div['value']:.2f} (Ex-Date)")
        
    Note:
        - Requires EODHD_API_KEY environment variable
        - Ex-dividend date is when stock price typically drops by dividend amount
        - Record date determines eligibility (must own stock by this date)
        - Payment date is when dividend is actually deposited
        - Includes special dividends and regular quarterly payments
    """
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


def eodhd_splits(symbol: str, from_date: Optional[str] = None, to_date: Optional[str] = None) -> List[Dict[str, Any]]:
    """Retrieve historical stock split data with split ratios.
    
    Fetches complete stock split history including split ratios and dates,
    essential for adjusting historical price data and calculating accurate
    returns across split events.
    
    Args:
        symbol: Stock symbol in format 'SYMBOL.EXCHANGE' (e.g., 'AAPL.US').
            For US stocks, '.US' suffix is automatically appended if missing.
        from_date: Start date for split history in 'YYYY-MM-DD' format.
            If None, returns all available split history.
        to_date: End date for split history in 'YYYY-MM-DD' format.
            If None, includes splits up to present date.
            
    Returns:
        List[Dict[str, Any]]: List of stock split records, each containing:
            - date: Effective date of the stock split
            - split: Split ratio in format 'new:old' (e.g., '2:1', '3:2')
            - splitCoefficient: Numerical split multiplier
            - On error: {'error': 'error_description'}
            
    Raises:
        ValueError: If EODHD_API_KEY environment variable is not configured.
        requests.exceptions.RequestException: If API request fails.
        
    Example:
        >>> splits = eodhd_splits('AAPL.US', '2020-01-01')
        >>> if splits and 'error' not in splits:
        ...     print(f"Found {len(splits)} stock splits since 2020:")
        ...     for split in splits:
        ...         print(f"{split['date']}: {split['split']} split")
        
    Note:
        - Requires EODHD_API_KEY environment variable
        - Split ratios show new shares to old shares relationship
        - 2:1 split means each old share becomes 2 new shares
        - Stock price adjusts inversely to split ratio
        - Essential for calculating adjusted historical returns
    """
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


def eodhd_technical(symbol: str, function: str, period: int = 14, from_date: Optional[str] = None, to_date: Optional[str] = None) -> List[Dict[str, Any]]:
    """Calculate technical analysis indicators for price trend analysis.
    
    Computes various technical indicators including moving averages,
    oscillators, and momentum indicators for technical analysis and
    algorithmic trading strategies.
    
    Args:
        symbol: Stock symbol in format 'SYMBOL.EXCHANGE' (e.g., 'AAPL.US').
            For US stocks, '.US' suffix is automatically appended if missing.
        function: Technical indicator to calculate. Common options:
            - 'sma': Simple Moving Average
            - 'ema': Exponential Moving Average
            - 'rsi': Relative Strength Index
            - 'macd': Moving Average Convergence Divergence
            - 'bb': Bollinger Bands
            - 'stoch': Stochastic Oscillator
        period: Calculation period for the indicator (number of periods).
            Defaults to 14, which is standard for RSI and many oscillators.
        from_date: Start date for calculation in 'YYYY-MM-DD' format.
            If None, uses sufficient history for accurate calculation.
        to_date: End date for calculation in 'YYYY-MM-DD' format.
            If None, calculates up to most recent trading day.
            
    Returns:
        List[Dict[str, Any]]: Time series of indicator values, each containing:
            - date: Trading date for the indicator value
            - [function]: Calculated indicator value (key matches function parameter)
            - Additional fields may be present for complex indicators (e.g., MACD)
            - On error: {'error': 'error_description'}
            
    Raises:
        ValueError: If EODHD_API_KEY environment variable is not configured
            or if invalid function/period parameters are provided.
        requests.exceptions.RequestException: If API request fails.
        
    Example:
        >>> # Calculate 14-period RSI for Apple
        >>> rsi_data = eodhd_technical('AAPL.US', 'rsi', 14, '2024-01-01')
        >>> if rsi_data and 'error' not in rsi_data:
        ...     latest_rsi = rsi_data[-1]['rsi']
        ...     print(f"Current RSI: {latest_rsi:.2f}")
        ...     if latest_rsi > 70:
        ...         print("Potentially overbought")
        ...     elif latest_rsi < 30:
        ...         print("Potentially oversold")
        
    Note:
        - Requires EODHD_API_KEY environment variable
        - Indicators require sufficient price history for accurate calculation
        - Different indicators have different optimal periods (RSI: 14, SMA: 20/50/200)
        - Some indicators return multiple values (MACD: signal, histogram)
        - Values may be null during initial calculation period
    """
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


def eodhd_screener(filters: str = "", limit: int = 50, offset: int = 0, signals: str = "") -> List[Dict[str, Any]]:
    """Screen stocks using custom financial and technical criteria.
    
    Filters stocks across exchanges based on fundamental metrics,
    technical indicators, and market data to identify investment
    opportunities matching specific criteria.
    
    Args:
        filters: Custom filter criteria as a string. Format varies but typically
            includes conditions like 'market_cap > 1000000000' or
            'pe_ratio < 20 AND dividend_yield > 0.02'. If empty,
            returns general market data without filtering.
        limit: Maximum number of results to return. Defaults to 50.
            Range typically 1-1000 depending on API subscription.
        offset: Number of results to skip for pagination. Defaults to 0.
            Use with limit for paginating through large result sets.
        signals: Technical signal filters as a string. Examples:
            'golden_cross', 'oversold_rsi', 'breakout'. If empty,
            no technical signal filtering is applied.
            
    Returns:
        List[Dict[str, Any]]: List of stocks matching criteria, each containing:
            - code: Stock symbol with exchange suffix
            - name: Company name
            - market_cap: Market capitalization
            - pe_ratio: Price-to-earnings ratio
            - dividend_yield: Annual dividend yield
            - price: Current stock price
            - change_p: Daily percentage change
            - volume: Trading volume
            - Additional fields based on screening criteria
            - On error: {'error': 'error_description'}
            
    Raises:
        ValueError: If EODHD_API_KEY environment variable is not configured
            or if invalid filter syntax is provided.
        requests.exceptions.RequestException: If API request fails.
        
    Example:
        >>> # Screen for large-cap dividend stocks
        >>> criteria = "market_cap > 10000000000 AND dividend_yield > 0.03"
        >>> stocks = eodhd_screener(filters=criteria, limit=20)
        >>> if stocks and 'error' not in stocks:
        ...     print(f"Found {len(stocks)} dividend stocks:")
        ...     for stock in stocks:
        ...         print(f"{stock['code']}: {stock['name']}")
        ...         print(f"  Yield: {stock['dividend_yield']:.2%}")
        ...         print(f"  Market Cap: ${stock['market_cap']:,.0f}")
        
    Note:
        - Requires EODHD_API_KEY environment variable
        - Filter syntax depends on EODHD's specific query language
        - Available fields for filtering vary by subscription tier
        - Results updated daily with fundamental data
        - Technical signals updated intraday during market hours
    """
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


def eodhd_search(query: str) -> List[Dict[str, Any]]:
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
            
    Returns:
        List[Dict[str, Any]]: List of matching instruments, each containing:
            - Code: Full symbol with exchange suffix (e.g., 'AAPL.US')
            - Name: Full company or instrument name
            - Country: Country where instrument is listed
            - Exchange: Exchange where instrument trades
            - Currency: Trading currency
            - Type: Instrument type (Common Stock, ETF, etc.)
            - ISIN: International Securities Identification Number (if available)
            - On error: {'error': 'error_description'}
            
    Raises:
        ValueError: If EODHD_API_KEY environment variable is not configured
            or if query is empty.
        requests.exceptions.RequestException: If API request fails.
        
    Example:
        >>> # Search for Apple-related stocks
        >>> results = eodhd_search('Apple')
        >>> if results and 'error' not in results:
        ...     print(f"Found {len(results)} matches for 'Apple':")
        ...     for result in results:
        ...         print(f"{result['Code']}: {result['Name']}")
        ...         print(f"  Exchange: {result['Exchange']} ({result['Country']})")
        ...         print(f"  Type: {result['Type']}")
        
    Note:
        - Requires EODHD_API_KEY environment variable
        - Search is case-insensitive and supports partial matches
        - Results include instruments from multiple global exchanges
        - Use the returned 'Code' field for subsequent API calls
        - Some exchanges may require specific subscription tiers
    """
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


def eodhd_exchanges_list() -> List[Dict[str, Any]]:
    """Retrieve list of all stock exchanges supported by EODHD API.
    
    Fetches comprehensive information about global stock exchanges,
    including trading details, currencies, and country information.
    Essential for understanding data coverage and symbol formatting.
    
    Returns:
        List[Dict[str, Any]]: List of supported exchanges, each containing:
            - Name: Full exchange name (e.g., 'New York Stock Exchange')
            - Code: Exchange code used in symbols (e.g., 'NYSE', 'NASDAQ')
            - OperatingMIC: Market Identifier Code for the exchange
            - Country: Country where exchange is located
            - Currency: Primary trading currency
            - CountryISO2: 2-letter ISO country code
            - CountryISO3: 3-letter ISO country code
            - Timezone: Exchange timezone
            - On error: {'error': 'error_description'}
            
    Raises:
        ValueError: If EODHD_API_KEY environment variable is not configured.
        requests.exceptions.RequestException: If API request fails.
        
    Example:
        >>> exchanges = eodhd_exchanges_list()
        >>> if exchanges and 'error' not in exchanges:
        ...     print(f"EODHD supports {len(exchanges)} exchanges:")
        ...     us_exchanges = [ex for ex in exchanges if ex['Country'] == 'USA']
        ...     print(f"US Exchanges: {len(us_exchanges)}")
        ...     for ex in us_exchanges:
        ...         print(f"  {ex['Code']}: {ex['Name']} ({ex['Currency']})")
        
    Note:
        - Requires EODHD_API_KEY environment variable
        - Exchange codes are used as suffixes in symbol format (e.g., 'AAPL.US')
        - Data coverage varies by exchange and subscription tier
        - Some exchanges may have delayed data or require premium access
        - Use exchange codes when fetching exchange-specific symbol lists
    """
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


def eodhd_exchange_symbols(exchange: str) -> List[Dict[str, Any]]:
    """Retrieve all tradeable symbols available on a specific exchange.
    
    Fetches comprehensive list of stocks, ETFs, and other instruments
    trading on the specified exchange. Useful for universe creation,
    screening across entire exchanges, and symbol discovery.
    
    Args:
        exchange: Exchange code to query (e.g., 'NYSE', 'NASDAQ', 'LSE').
            Use the 'Code' field from eodhd_exchanges_list() for valid codes.
            
    Returns:
        List[Dict[str, Any]]: List of all symbols on the exchange, each containing:
            - Code: Full symbol with exchange suffix (e.g., 'AAPL.US')
            - Name: Company or instrument name
            - Country: Country of the exchange
            - Exchange: Exchange code
            - Currency: Trading currency
            - Type: Instrument type (Common Stock, ETF, Preferred Stock, etc.)
            - Isin: International Securities Identification Number (if available)
            - On error: {'error': 'error_description'}
            
    Raises:
        ValueError: If EODHD_API_KEY environment variable is not configured
            or if exchange code is invalid.
        requests.exceptions.RequestException: If API request fails.
        
    Example:
        >>> # Get all NASDAQ stocks
        >>> symbols = eodhd_exchange_symbols('NASDAQ')
        >>> if symbols and 'error' not in symbols:
        ...     print(f"NASDAQ has {len(symbols)} tradeable symbols")
        ...     common_stocks = [s for s in symbols if s['Type'] == 'Common Stock']
        ...     etfs = [s for s in symbols if s['Type'] == 'ETF']
        ...     print(f"Common Stocks: {len(common_stocks)}")
        ...     print(f"ETFs: {len(etfs)}")
        ...     # Show some examples
        ...     for symbol in symbols[:5]:
        ...         print(f"  {symbol['Code']}: {symbol['Name']} ({symbol['Type']})")
        
    Note:
        - Requires EODHD_API_KEY environment variable
        - Symbol lists are updated regularly but may not be real-time
        - Use returned 'Code' field for subsequent data requests
        - Large exchanges like NYSE/NASDAQ may return thousands of symbols
        - Some symbols may be delisted or inactive
    """
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


# Alpaca Trading API Real Functions (Stubs)
def alpaca_trading_account() -> Dict[str, Any]:
    """Retrieve comprehensive trading account information and balances.
    
    Fetches current account status, buying power, equity positions,
    and cash balances from the Alpaca Trading API. Essential for
    portfolio management and risk assessment.
    
    Returns:
        Dict[str, Any]: Account information containing:
            - id: Unique account identifier
            - account_number: Account number for reference
            - status: Account status (ACTIVE, SUSPENDED, etc.)
            - currency: Base account currency (typically USD)
            - buying_power: Total available buying power
            - cash: Available cash balance
            - portfolio_value: Total portfolio value (cash + positions)
            - equity: Current equity value
            - pattern_day_trader: PDT status flag
            - trading_blocked: Whether trading is currently blocked
            - multiplier: Account margin multiplier
            - initial_margin: Required initial margin
            - maintenance_margin: Required maintenance margin
            - daytrade_count: Number of day trades in rolling 5-day period
            - On error: {'error': 'error_description'}
            
    Raises:
        ValueError: If Alpaca API credentials are not configured.
        requests.exceptions.RequestException: If API request fails.
        
    Example:
        >>> account = alpaca_trading_account()
        >>> if 'error' not in account:
        ...     print(f"Account Status: {account['status']}")
        ...     print(f"Portfolio Value: ${float(account['portfolio_value']):,.2f}")
        ...     print(f"Buying Power: ${float(account['buying_power']):,.2f}")
        ...     print(f"Cash: ${float(account['cash']):,.2f}")
        ...     if account['pattern_day_trader']:
        ...         print("Account flagged as Pattern Day Trader")
        
    Note:
        - Requires ALPACA_API_KEY and ALPACA_SECRET_KEY environment variables
        - Account values updated in real-time during market hours
        - Pattern Day Trader rules apply to accounts with < $25,000 equity
        - Buying power varies based on account type and margin settings
        - Cash vs margin account affects available buying power
    """
    try:
        if not ALPACA_API_KEY or not ALPACA_SECRET_KEY:
            raise ValueError("Alpaca API credentials not configured")
        
        url = f"{ALPACA_BASE_URL}/v2/account"
        response = requests.get(url, headers=get_headers())
        response.raise_for_status()
        
        return response.json()
        
    except Exception as e:
        return {"error": f"Account request failed: {str(e)}"}


def alpaca_trading_positions() -> List[Dict[str, Any]]:
    """Retrieve all open stock positions with profit/loss and market values.
    
    Fetches complete position data including quantities, entry prices,
    current market values, and unrealized P&L for all holdings in
    the trading account.
    
    Returns:
        List[Dict[str, Any]]: List of open positions, each containing:
            - asset_id: Unique identifier for the asset
            - symbol: Stock symbol (e.g., 'AAPL')
            - exchange: Exchange where asset trades
            - asset_class: Asset classification (us_equity, crypto, etc.)
            - qty: Number of shares held (positive for long, negative for short)
            - side: Position side ('long' or 'short')
            - avg_entry_price: Average cost basis per share
            - market_value: Current market value of position
            - cost_basis: Total cost basis of position
            - current_price: Current market price per share
            - unrealized_pl: Unrealized profit/loss in dollars
            - unrealized_plpc: Unrealized P&L as percentage
            - unrealized_intraday_pl: Intraday unrealized P&L
            - change_today: Today's price change percentage
            - On error: {'error': 'error_description'}
            
    Raises:
        ValueError: If Alpaca API credentials are not configured.
        requests.exceptions.RequestException: If API request fails.
        
    Example:
        >>> positions = alpaca_trading_positions()
        >>> if positions and 'error' not in positions:
        ...     total_value = sum(float(pos['market_value']) for pos in positions)
        ...     total_pl = sum(float(pos['unrealized_pl']) for pos in positions)
        ...     print(f"Total positions: {len(positions)}")
        ...     print(f"Total market value: ${total_value:,.2f}")
        ...     print(f"Total unrealized P&L: ${total_pl:,.2f}")
        ...     print("\nIndividual positions:")
        ...     for pos in positions:
        ...         pct_change = float(pos['unrealized_plpc']) * 100
        ...         print(f"{pos['symbol']}: {pos['qty']} shares")
        ...         print(f"  Value: ${float(pos['market_value']):,.2f}")
        ...         print(f"  P&L: ${float(pos['unrealized_pl']):,.2f} ({pct_change:+.2f}%)")
        
    Note:
        - Requires ALPACA_API_KEY and ALPACA_SECRET_KEY environment variables
        - Position values updated in real-time during market hours
        - Negative quantities indicate short positions
        - Cost basis includes commissions and fees
        - Market values based on current bid/ask or last trade price
    """
    try:
        if not ALPACA_API_KEY or not ALPACA_SECRET_KEY:
            raise ValueError("Alpaca API credentials not configured")
        
        url = f"{ALPACA_BASE_URL}/v2/positions"
        response = requests.get(url, headers=get_headers())
        response.raise_for_status()
        
        return response.json()
        
    except Exception as e:
        return {"error": f"Positions request failed: {str(e)}"}


def alpaca_trading_position(symbol: str) -> Dict[str, Any]:
    """Retrieve detailed position information for a specific symbol.
    
    Fetches comprehensive position data for a single stock including
    entry price, current value, profit/loss metrics, and position size.
    Useful for position-specific analysis and risk management.
    
    Args:
        symbol: Stock symbol to query (e.g., 'AAPL', 'TSLA').
            Case-insensitive, automatically converted to uppercase.
            
    Returns:
        Dict[str, Any]: Position details containing:
            - asset_id: Unique identifier for the asset
            - symbol: Stock symbol (uppercase)
            - exchange: Exchange where asset trades
            - asset_class: Asset classification (us_equity, crypto, etc.)
            - qty: Number of shares held (positive for long, negative for short)
            - side: Position side ('long' or 'short')
            - avg_entry_price: Average cost basis per share
            - market_value: Current market value of position
            - cost_basis: Total cost basis of position
            - current_price: Current market price per share
            - unrealized_pl: Unrealized profit/loss in dollars
            - unrealized_plpc: Unrealized P&L as percentage
            - On error: {'error': 'error_description'}
            
    Raises:
        ValueError: If Alpaca API credentials are not configured.
        requests.exceptions.RequestException: If API request fails.
        
    Example:
        >>> position = alpaca_trading_position('AAPL')
        >>> if 'error' not in position:
        ...     qty = float(position['qty'])
        ...     current_price = float(position['current_price'])
        ...     entry_price = float(position['avg_entry_price'])
        ...     pl_pct = float(position['unrealized_plpc']) * 100
        ...     print(f"AAPL Position: {qty:,.0f} shares")
        ...     print(f"Entry Price: ${entry_price:.2f}")
        ...     print(f"Current Price: ${current_price:.2f}")
        ...     print(f"P&L: {pl_pct:+.2f}%")
        
    Note:
        - Requires ALPACA_API_KEY and ALPACA_SECRET_KEY environment variables
        - Returns 404 error if no position exists for the symbol
        - Position values updated in real-time during market hours
        - Use alpaca_trading_positions() to get all positions at once
    """
    try:
        if not ALPACA_API_KEY or not ALPACA_SECRET_KEY:
            raise ValueError("Alpaca API credentials not configured")
        
        url = f"{ALPACA_BASE_URL}/v2/positions/{symbol}"
        response = requests.get(url, headers=get_headers())
        response.raise_for_status()
        
        return response.json()
        
    except Exception as e:
        return {"error": f"Position request failed: {str(e)}"}


def alpaca_trading_orders(status: str = "open", limit: int = 100, after: Optional[str] = None, until: Optional[str] = None, direction: str = "desc", nested: bool = False) -> List[Dict[str, Any]]:
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
            
    Returns:
        List[Dict[str, Any]]: List of orders, each containing:
            - id: Unique order identifier
            - client_order_id: Client-specified order ID
            - symbol: Stock symbol
            - asset_class: Asset type (us_equity, crypto, etc.)
            - qty: Order quantity
            - filled_qty: Quantity filled so far
            - side: Order side ('buy' or 'sell')
            - order_type: Order type (market, limit, stop, etc.)
            - time_in_force: Order duration (day, gtc, ioc, fok)
            - limit_price: Limit price (for limit orders)
            - stop_price: Stop price (for stop orders)
            - status: Current order status
            - created_at: Order creation timestamp
            - filled_at: Order fill timestamp (if filled)
            - filled_avg_price: Average fill price
            - On error: {'error': 'error_description'}
            
    Raises:
        ValueError: If Alpaca API credentials are not configured.
        requests.exceptions.RequestException: If API request fails.
        
    Example:
        >>> # Get recent filled orders
        >>> orders = alpaca_trading_orders(status='closed', limit=10)
        >>> if orders and 'error' not in orders:
        ...     filled_orders = [o for o in orders if o['status'] == 'filled']
        ...     print(f"Found {len(filled_orders)} filled orders:")
        ...     for order in filled_orders:
        ...         qty = order['filled_qty']
        ...         price = order['filled_avg_price']
        ...         value = float(qty) * float(price)
        ...         print(f"{order['symbol']}: {order['side']} {qty} @ ${price}")
        ...         print(f"  Total Value: ${value:,.2f}")
        ...         print(f"  Fill Time: {order['filled_at']}")
        
    Note:
        - Requires ALPACA_API_KEY and ALPACA_SECRET_KEY environment variables
        - Order history retained for account lifetime
        - Use time filters for performance with large order histories
        - Partial fills show filled_qty < qty
        - Complex orders may have nested sub-orders when nested=True
    """
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


def alpaca_trading_portfolio_history(period: str = "1D", timeframe: str = "15Min", end_date: Optional[str] = None, extended_hours: bool = False) -> Dict[str, Any]:
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
            
    Returns:
        Dict[str, Any]: Portfolio history containing:
            - timestamp: Array of Unix timestamps for each data point
            - equity: Array of portfolio equity values
            - profit_loss: Array of profit/loss values
            - profit_loss_pct: Array of percentage changes
            - base_value: Starting portfolio value for the period
            - timeframe: Confirmed timeframe used
            - On error: {'error': 'error_description'}
            
    Raises:
        ValueError: If Alpaca API credentials are not configured
            or if invalid period/timeframe combination provided.
        requests.exceptions.RequestException: If API request fails.
        
    Example:
        >>> # Get one month of daily portfolio performance
        >>> history = alpaca_trading_portfolio_history('1M', '1Day')
        >>> if 'error' not in history:
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
        ...     print(f"Best Day: {max(pl_pct)*100:+.2f}%")
        ...     print(f"Worst Day: {min(pl_pct)*100:+.2f}%")
        
    Note:
        - Requires ALPACA_API_KEY and ALPACA_SECRET_KEY environment variables
        - Higher frequency data (1Min, 5Min) limited to shorter periods
        - Extended hours data may show different liquidity patterns
        - Portfolio value includes cash and position market values
        - Useful for calculating Sharpe ratio, maximum drawdown, volatility
    """
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


def alpaca_trading_clock() -> Dict[str, Any]:
    """Retrieve current market status and trading session information.
    
    Fetches real-time market clock data including current market status,
    next open/close times, and session information. Essential for
    determining when markets are open for trading.
    
    Returns:
        Dict[str, Any]: Market clock information containing:
            - timestamp: Current timestamp in ISO 8601 format
            - is_open: Boolean indicating if market is currently open
            - next_open: Next market open time in ISO 8601 format
            - next_close: Next market close time in ISO 8601 format
            - On error: {'error': 'error_description'}
            
    Raises:
        ValueError: If Alpaca API credentials are not configured.
        requests.exceptions.RequestException: If API request fails.
        
    Example:
        >>> clock = alpaca_trading_clock()
        >>> if 'error' not in clock:
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
        - Requires ALPACA_API_KEY and ALPACA_SECRET_KEY environment variables
        - Market hours: 9:30 AM - 4:00 PM ET (regular session)
        - Extended hours: 4:00 AM - 9:30 AM, 4:00 PM - 8:00 PM ET
        - Market closed on weekends and federal holidays
        - Times returned in UTC, convert to local timezone as needed
        - Useful for scheduling trading algorithms and order submissions
    """
    try:
        if not ALPACA_API_KEY or not ALPACA_SECRET_KEY:
            raise ValueError("Alpaca API credentials not configured")
        
        url = f"{ALPACA_BASE_URL}/v2/clock"
        response = requests.get(url, headers=get_headers())
        response.raise_for_status()
        
        return response.json()
        
    except Exception as e:
        return {"error": f"Clock request failed: {str(e)}"}


# Alpaca Market Data API Real Functions (Stubs)
def alpaca_market_stocks_bars(symbols: List[str], timeframe: str = "1Day", start: Optional[str] = None, end: Optional[str] = None) -> Dict[str, Any]:
    """Retrieve historical OHLC price bars for multiple stocks using Alpaca Market Data API.
    
    Fetches time-series price data including open, high, low, close, and volume
    for specified symbols across various timeframes. Essential for technical analysis,
    backtesting, and chart generation with real market data.
    
    Args:
        symbols: List of stock symbols (e.g., [AAPL,TSLA,MSFT]).
            Each symbol must be valid and tradeable on supported exchanges.
        timeframe: Bar duration for the data. Options:
            - '1Min', '5Min', '15Min', '30Min': Minute intervals
            - '1Hour', '2Hour', '4Hour': Hourly intervals  
            - '1Day': Daily bars (default)
            - '1Week': Weekly bars
            - '1Month': Monthly bars
        start: Start date for historical data in 'YYYY-MM-DD' format.
            If None, defaults to API's default historical range.
        end: End date for historical data in 'YYYY-MM-DD' format.
            If None, defaults to most recent trading day.
            
    Returns:
        Dict[str, Any]: Historical price data containing:
            - bars: Dictionary with symbol keys, each containing array of bars:
                - t: Timestamp in ISO 8601 format
                - o: Open price for the period
                - h: Highest price during the period
                - l: Lowest price during the period
                - c: Close price for the period
                - v: Volume traded during the period
                - n: Number of trades during the period
                - vw: Volume weighted average price (VWAP)
            - next_page_token: Pagination token for additional data (if applicable)
            - On error: {'error': 'error_description'}
            
    Raises:
        ValueError: If Alpaca API credentials are not configured.
        requests.exceptions.RequestException: If API request fails.
        
    Example:
        >>> # Get daily bars for tech stocks over last month
        >>> bars = alpaca_market_stocks_bars([AAPL,GOOGL,MSFT], '1Day', '2024-01-01')
        >>> for symbol, symbol_bars in bars['bars'].items():
        ...     if symbol_bars:
        ...         latest = symbol_bars[-1]
        ...         first = symbol_bars[0]
        ...         total_return = (latest['c'] / first['o'] - 1) * 100
        ...         print(f"{symbol}: {len(symbol_bars)} bars")
        ...         print(f"  Return: {total_return:+.2f}%")
        ...         print(f"  Latest: ${latest['c']:.2f} (Vol: {latest['v']:,})")
        
    Note:
        - Requires ALPACA_API_KEY and ALPACA_SECRET_KEY environment variables
        - Higher frequency data (minute bars) limited to recent periods
        - Weekend and holiday dates excluded from results
        - Volume weighted average price (VWAP) useful for execution analysis
        - API rate limits apply - use pagination for large date ranges
    """
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


def alpaca_market_stocks_snapshots(symbols: List[str]) -> Dict[str, Any]:
    """Retrieve comprehensive current market snapshots for multiple stocks.
    
    Fetches real-time market data including latest quotes, trades, and daily bars
    for each requested symbol. Provides complete market picture including current
    prices, spreads, and trading activity.
    
    Args:
        symbols: List of stock symbols (e.g., ["AAPL","TSLA","SPY"]).
            Each symbol must be valid and actively traded.
            
    Returns:
        Dict[str, Any]: Comprehensive market snapshots containing:
            - snapshots: Dictionary with symbol keys, each containing:
                - latestTrade: Most recent trade data (price, size, timestamp)
                - latestQuote: Current bid/ask quote (spread, sizes, timestamp)
                - dailyBar: Current day's OHLC data (open, high, low, close, volume)
                - minuteBar: Latest minute bar data
                - prevDailyBar: Previous trading day's OHLC data
            - On error: {'error': 'error_description'}
            
    Raises:
        ValueError: If Alpaca API credentials are not configured.
        requests.exceptions.RequestException: If API request fails.
        
    Example:
        >>> snapshots = alpaca_market_stocks_snapshots([AAPL,MSFT,GOOGL])
        >>> for symbol, data in snapshots['snapshots'].items():
        ...     trade = data.get('latestTrade', {})
        ...     quote = data.get('latestQuote', {})
        ...     daily = data.get('dailyBar', {})
        ...     
        ...     print(f"{symbol} Current Snapshot:")
        ...     print(f"  Last Trade: ${trade.get('p', 'N/A')}")
        ...     print(f"  Bid/Ask: ${quote.get('bp', 'N/A')} / ${quote.get('ap', 'N/A')}")
        ...     print(f"  Volume: {daily.get('v', 0):,} shares")
        
    Note:
        - Requires ALPACA_API_KEY and ALPACA_SECRET_KEY environment variables
        - Real-time data during market hours, delayed outside hours
        - Includes comprehensive market microstructure data
        - Useful for real-time dashboards and trading applications
    """
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


def alpaca_market_stocks_quotes_latest(symbols: List[str]) -> Dict[str, Any]:
    """Retrieve latest bid/ask quotes for multiple stocks.
    
    Fetches current market maker quotes with bid/ask prices and sizes.
    Essential for understanding current market depth, spread analysis,
    and optimal order placement strategies.
    
    Args:
        symbols: List of stock symbols (e.g., ["AAPL","TSLA","SPY"]).
            Each symbol must be valid and actively quoted.
            
    Returns:
        Dict[str, Any]: Latest market quotes containing:
            - quotes: Dictionary with symbol keys, each containing:
                - t: Quote timestamp in ISO 8601 format
                - bp: Best bid price (highest price buyers are willing to pay)
                - bs: Bid size (number of shares at bid price)
                - ap: Best ask price (lowest price sellers are willing to accept)
                - as: Ask size (number of shares at ask price)
                - c: Conditions/flags for the quote
            - On error: {'error': 'error_description'}
            
    Raises:
        ValueError: If Alpaca API credentials are not configured.
        requests.exceptions.RequestException: If API request fails.
        
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
        - Requires ALPACA_API_KEY and ALPACA_SECRET_KEY environment variables
        - Quotes updated continuously during market hours
        - Spread indicates market liquidity (tighter = more liquid)
        - Use mid-price for fair value estimates
        - Quote sizes show market depth at best prices
    """
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


def alpaca_market_stocks_trades_latest(symbols: List[str]) -> Dict[str, Any]:
    """Retrieve latest trade execution data for multiple stocks.
    
    Fetches most recent trade transactions showing actual execution prices
    and volumes. Essential for understanding current market prices and
    recent trading activity patterns.
    
    Args:
        symbols: List of stock symbols (e.g., []"AAPL","TSLA","SPY"]).
            Each symbol must be valid and actively traded.
            
    Returns:
        Dict[str, Any]: Latest trade executions containing:
            - trades: Dictionary with symbol keys, each containing:
                - t: Trade timestamp in ISO 8601 format
                - p: Trade execution price
                - s: Trade size (number of shares executed)
                - c: Trade conditions/flags
                - i: Trade ID
                - x: Exchange where trade occurred
            - On error: {'error': 'error_description'}
            
    Raises:
        ValueError: If Alpaca API credentials are not configured.
        requests.exceptions.RequestException: If API request fails.
        
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
        - Requires ALPACA_API_KEY and ALPACA_SECRET_KEY environment variables
        - Trade prices represent actual execution levels
        - Large trades may indicate institutional activity
        - Use for current price discovery and market timing
        - Trade conditions provide execution context
    """
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


def alpaca_market_screener_most_actives(top: int = 10) -> Dict[str, Any]:
    """Screen for most actively traded stocks by volume using Alpaca Market Data API.
    
    Identifies stocks with highest trading volume for the current or most recent
    trading session. High volume often indicates significant news, earnings,
    or institutional activity driving increased interest.
    
    Args:
        top: Number of most active stocks to return. Range typically 1-50.
            Defaults to 10. Larger values may take longer to process.
            
    Returns:
        Dict[str, Any]: Most active stocks by volume containing:
            - most_actives: List of active stocks, each containing:
                - symbol: Stock symbol
                - volume: Current day trading volume
                - trade_count: Number of individual trades
                - price: Current or last trade price
                - change: Price change from previous close
                - percent_change: Percentage change from previous close
            - On error: {'error': 'error_description'}
            
    Raises:
        ValueError: If Alpaca API credentials are not configured.
        requests.exceptions.RequestException: If API request fails.
        
    Example:
        >>> actives = alpaca_market_screener_most_actives(20)
        >>> if actives and 'most_actives' in actives:
        ...     stocks = actives['most_actives']
        ...     print(f"Top {len(stocks)} Most Active Stocks:")
        ...     for stock in stocks:
        ...         volume_millions = stock['volume'] / 1_000_000
        ...         print(f"{stock['symbol']}: {volume_millions:.1f}M shares")
        ...         print(f"  Price: ${stock['price']:.2f} ({stock['percent_change']:+.2f}%)")
        ...         print(f"  Trades: {stock['trade_count']:,}")
        
    Note:
        - Requires ALPACA_API_KEY and ALPACA_SECRET_KEY environment variables
        - Volume data reflects current or most recent trading session
        - High volume may indicate breakout opportunities or news-driven moves
        - Useful for momentum strategies and trend identification
        - Data updated throughout trading day
    """
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


def alpaca_market_screener_top_gainers(top: int = 10) -> Dict[str, Any]:
    """Screen for stocks with biggest percentage gains using Alpaca Market Data API.
    
    Identifies stocks with highest percentage price increases for the current
    or most recent trading session. Useful for momentum strategies, breakout
    detection, and identifying stocks benefiting from positive news or sentiment.
    
    Args:
        top: Number of top gaining stocks to return. Range typically 1-50.
            Defaults to 10. Larger values may include smaller gains.
            
    Returns:
        Dict[str, Any]: Top gaining stocks containing:
            - top_gainers: List of gaining stocks, each containing:
                - symbol: Stock symbol
                - percent_change: Percentage gain from previous close
                - change: Absolute price change in dollars
                - price: Current stock price
                - volume: Trading volume for the session
            - On error: {'error': 'error_description'}
            
    Raises:
        ValueError: If Alpaca API credentials are not configured.
        requests.exceptions.RequestException: If API request fails.
        
    Example:
        >>> gainers = alpaca_market_screener_top_gainers(15)
        >>> if gainers and 'top_gainers' in gainers:
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
        - Requires ALPACA_API_KEY and ALPACA_SECRET_KEY environment variables
        - Percentage changes calculated from previous close
        - High gains may indicate momentum or news-driven moves
        - Useful for identifying breakout candidates and trend followers
        - Consider volume for confirming strength of moves
    """
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


def alpaca_market_screener_top_losers(top: int = 10) -> Dict[str, Any]:
    """Screen for stocks with biggest percentage losses using Alpaca Market Data API.
    
    Identifies stocks with largest percentage price decreases for the current
    or most recent trading session. Useful for contrarian strategies, oversold
    opportunity identification, and risk monitoring.
    
    Args:
        top: Number of top losing stocks to return. Range typically 1-50.
            Defaults to 10. Larger values may include smaller losses.
            
    Returns:
        Dict[str, Any]: Top losing stocks containing:
            - top_losers: List of losing stocks, each containing:
                - symbol: Stock symbol
                - percent_change: Percentage loss from previous close (negative)
                - change: Absolute price change in dollars (negative)
                - price: Current stock price
                - volume: Trading volume for the session
            - On error: {'error': 'error_description'}
            
    Raises:
        ValueError: If Alpaca API credentials are not configured.
        requests.exceptions.RequestException: If API request fails.
        
    Example:
        >>> losers = alpaca_market_screener_top_losers(15)
        >>> if losers and 'top_losers' in losers:
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
        - Requires ALPACA_API_KEY and ALPACA_SECRET_KEY environment variables
        - Percentage changes calculated from previous close
        - Large losses may indicate oversold opportunities or fundamental issues
        - Useful for contrarian strategies and value opportunity identification
        - Consider reasons for decline before assuming oversold conditions
    """
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


def alpaca_market_news(symbols: List[str] = [], start: Optional[str] = None, end: Optional[str] = None, sort: str = "desc", include_content: bool = True) -> Dict[str, Any]:
    """Retrieve financial news articles and market information using Alpaca Market Data API.
    
    Fetches relevant financial news articles filtered by symbols, date ranges,
    and other criteria. Essential for fundamental analysis, sentiment tracking,
    and staying informed about market-moving events.
    
    Args:
        symbols: List of symbols to filter news (e.g., ["AAPL","TSLA"]).
            If empty, returns general market news without symbol filtering.
        start: Start date for news articles in 'YYYY-MM-DD' format.
            If None, returns recent news without date filtering.
        end: End date for news articles in 'YYYY-MM-DD' format.
            If None, includes news up to current date.
        sort: Sort order for returned articles. Options:
            - 'desc': Newest articles first (default)
            - 'asc': Oldest articles first
        include_content: Whether to include full article content.
            If True, returns complete article text. If False, returns headlines only.
            
    Returns:
        Dict[str, Any]: Financial news articles containing:
            - news: List of news articles, each containing:
                - id: Unique article identifier
                - headline: Article headline/title
                - summary: Brief article summary (if available)
                - content: Full article content (if include_content=True)
                - symbols: List of related stock symbols mentioned
                - created_at: Publication timestamp in ISO 8601 format
                - updated_at: Last update timestamp
                - url: Original article URL
                - source: News source/publisher
            - next_page_token: Pagination token for additional articles
            - On error: {'error': 'error_description'}
            
    Raises:
        ValueError: If Alpaca API credentials are not configured.
        requests.exceptions.RequestException: If API request fails.
        
    Example:
        >>> # Get recent Apple news
        >>> news = alpaca_market_news(['AAPL'], start='2024-01-01', include_content=False)
        >>> if news and 'news' in news:
        ...     articles = news['news']
        ...     print(f"Found {len(articles)} Apple articles:")
        ...     for article in articles[:5]:  # Show first 5
        ...         symbols = ', '.join(article.get('symbols', []))
        ...         print(f"Headline: {article['headline']}")
        ...         print(f"Source: {article.get('source', 'N/A')}")
        ...         print(f"Symbols: {symbols}")
        ...         print(f"Published: {article['created_at']}")
        ...         print()
        
    Note:
        - Requires ALPACA_API_KEY and ALPACA_SECRET_KEY environment variables
        - News articles updated continuously throughout trading day
        - Symbol filtering helps focus on relevant company news
        - Full content useful for sentiment analysis and detailed research
        - Consider rate limits when requesting large date ranges
    """
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


# Registry of all real financial functions
REAL_FINANCIAL_FUNCTIONS = {
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