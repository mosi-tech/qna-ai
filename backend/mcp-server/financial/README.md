# MCP Financial Server

Python-based MCP server providing financial data from multiple APIs following exact API specifications.

## Features

- **EODHD API**: End-of-day data, real-time prices, fundamentals, dividends, technical indicators, screener
- **Alpaca Trading API**: Account info, positions, orders, portfolio history, market clock
- **Alpaca Market Data API**: Historical bars, snapshots, quotes, trades, screeners, news

## Two Implementations

### Mock Implementation (Default)
- Realistic test data without requiring API keys
- Perfect for development, testing, and demos
- Data generated based on real market patterns
- No external dependencies or rate limits

### Real Implementation
- Connects to actual financial APIs
- Requires valid API credentials
- Production-ready with proper error handling
- Respects API rate limits and authentication

## Usage

### Environment Variables

```bash
# Use mock data (default)
export USE_MOCK_FINANCIAL_DATA=true

# Use real APIs (requires credentials)
export USE_MOCK_FINANCIAL_DATA=false
export ALPACA_API_KEY=your_alpaca_key
export ALPACA_SECRET_KEY=your_alpaca_secret  
export EODHD_API_KEY=your_eodhd_key
```

### Running the Server

```bash
# Unified server (automatically detects mock/real)
python mcp/financial_server.py

# Explicitly run mock server
python mcp/financial_server_mock.py

# Explicitly run real server  
python mcp/financial_server_real.py
```

## API Coverage

### EODHD API Functions
- `eodhd_eod_data` - Historical OHLC prices
- `eodhd_real_time` - Real-time stock prices
- `eodhd_fundamentals` - Company fundamental data
- `eodhd_dividends` - Dividend history
- `eodhd_splits` - Stock split history
- `eodhd_technical` - Technical indicators
- `eodhd_screener` - Stock screener
- `eodhd_search` - Stock search
- `eodhd_exchanges_list` - Supported exchanges
- `eodhd_exchange_symbols` - Exchange symbols

### Alpaca Trading API Functions
- `alpaca_trading_account` - Account information
- `alpaca_trading_positions` - All positions
- `alpaca_trading_position` - Specific position
- `alpaca_trading_orders` - Order history
- `alpaca_trading_portfolio_history` - Portfolio performance
- `alpaca_trading_clock` - Market clock

### Alpaca Market Data API Functions
- `alpaca_market_stocks_bars` - Historical OHLC bars
- `alpaca_market_stocks_snapshots` - Market snapshots
- `alpaca_market_stocks_quotes_latest` - Latest quotes
- `alpaca_market_stocks_trades_latest` - Latest trades
- `alpaca_market_screener_most_actives` - Most active stocks
- `alpaca_market_screener_top_gainers` - Top gainers
- `alpaca_market_screener_top_losers` - Top losers
- `alpaca_market_news` - Financial news

## File Structure

```
mcp/financial/
├── __init__.py              # Unified entry point
├── functions_mock.py        # Mock implementations
├── functions_real.py        # Real API implementations
└── README.md               # This file

mcp/
├── financial_server.py      # Unified MCP server
├── financial_server_mock.py # Mock-only MCP server
└── financial_server_real.py # Real-only MCP server
```

## Examples

### Get Stock Snapshots (Mock)
```python
from mcp.financial import eodhd_real_time

result = eodhd_real_time("AAPL.US")
print(result)
```

### Get Historical Data (Real)
```bash
export USE_MOCK_FINANCIAL_DATA=false
export EODHD_API_KEY=your_key

python -c "
from mcp.financial import eodhd_eod_data
data = eodhd_eod_data('AAPL.US', '2024-01-01', '2024-01-31')
print(data)
"
```

## Development

The mock implementation generates realistic data patterns:
- Proper OHLC relationships (high >= max(open,close), low <= min(open,close))
- Realistic volatility and volume patterns
- Consistent symbol-specific base prices
- Proper date handling and market day filtering
- Authentic API response structures

## Production Deployment

For production use:
1. Set `USE_MOCK_FINANCIAL_DATA=false`
2. Configure all required API keys
3. Monitor API rate limits and usage
4. Implement proper error handling and retries
5. Use secure credential management