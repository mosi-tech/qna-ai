# Financial Mock Data MCP Server

A comprehensive Model Context Protocol (MCP) server that provides realistic mock financial data for development and testing. This server implements all endpoints from Alpaca Trading API, Alpaca Market Data API, and EODHD API with realistic sample data.

## Features

### 🏦 **Alpaca Trading API Mock Data**
- **Account Management**: Account info, buying power, equity, trading status
- **Portfolio Management**: Positions, P&L, market values, portfolio history
- **Order Management**: Order history, status tracking, fills
- **Watchlists**: User watchlists with symbols and metadata
- **Options Trading**: Contracts, strikes, expirations
- **Corporate Actions**: Dividends, splits, mergers
- **Crypto Wallets**: Bitcoin and Ethereum wallet data

### 📈 **Alpaca Market Data Mock Data**
- **Stock Data**: OHLC bars, quotes, trades, snapshots
- **Options Data**: Option quotes, trades, snapshots, Greeks
- **Cryptocurrency**: Crypto pairs, perpetuals, order books
- **Forex**: Exchange rates, currency pairs
- **Market Screening**: Most actives, top gainers/losers
- **News**: Financial news with content and metadata
- **Corporate Actions**: Comprehensive corporate event data

### 📊 **EODHD Mock Data**
- **EOD Data**: End-of-day OHLC with adjustments
- **Real-time**: Live market data and pricing
- **Fundamentals**: Company financials, ratios, balance sheets
- **Dividends & Splits**: Historical dividend and split data
- **Technical Indicators**: RSI, MACD, SMA, EMA, and more
- **Screening**: Custom stock screeners with filters
- **ETF Data**: Holdings, composition, sector weights
- **Insider Trading**: Corporate insider transactions
- **Macro Data**: Economic indicators and government data

## Installation

```bash
cd mcp-financial-server
npm install
```

## Usage

### Running the Server

```bash
# Start the server
npm start

# Or run in development mode with auto-restart
npm run dev
```

### Available Tools

The server provides 48+ financial data tools across three APIs:

#### Alpaca Trading Tools
- `alpaca-trading_account` - Account information and balances
- `alpaca-trading_positions` - Open positions with P&L
- `alpaca-trading_orders` - Order history and status
- `alpaca-trading_portfolio-history` - Performance over time
- `alpaca-trading_watchlists` - User watchlists
- `alpaca-trading_account-activities` - Account activities
- And 6 more trading-related tools...

#### Alpaca Market Data Tools
- `alpaca-market_stocks-bars` - Historical stock OHLC data
- `alpaca-market_stocks-quotes-latest` - Real-time quotes
- `alpaca-market_options-snapshots` - Options market data
- `alpaca-market_crypto-bars` - Cryptocurrency data
- `alpaca-market_screener-most-actives` - Market screeners
- `alpaca-market_news` - Financial news
- And 9 more market data tools...

#### EODHD Tools  
- `eodhd_eod-data` - End-of-day price data
- `eodhd_fundamentals` - Company fundamental data
- `eodhd_technical-indicators` - Technical analysis
- `eodhd_screener` - Custom stock screening
- `eodhd_etf-holdings` - ETF composition data
- `eodhd_macro-indicators` - Economic indicators
- And 9 more comprehensive data tools...

### Example Usage

```javascript
// Get account information
{
  "name": "alpaca-trading_account",
  "arguments": {}
}

// Get stock price data
{
  "name": "alpaca-market_stocks-bars", 
  "arguments": {
    "symbols": "AAPL,TSLA,SPY",
    "timeframe": "1Day"
  }
}

// Get company fundamentals
{
  "name": "eodhd_fundamentals",
  "arguments": {
    "symbol": "AAPL.US"
  }
}
```

## Mock Data Features

### 🎯 **Realistic Data Generation**
- **Market Hours**: Respects actual trading hours and weekends
- **Price Movements**: Realistic price fluctuations and volatility  
- **Volume Patterns**: Appropriate volume ranges for different securities
- **Corporate Actions**: Realistic dividend yields, split ratios
- **Options Data**: Proper strike prices, expirations, Greeks

### 📋 **Comprehensive Coverage**
- **95 API Endpoints**: Complete coverage of all documented APIs
- **Multiple Asset Classes**: Stocks, options, crypto, forex, ETFs
- **Historical & Real-time**: Both historical series and current snapshots
- **Fundamental Data**: Full financial statements, ratios, metrics
- **Technical Analysis**: 10+ technical indicators with proper calculations

### 🔧 **Developer Friendly**
- **Parameterized**: Accepts all documented parameters
- **Consistent**: Deterministic but varied mock data
- **Error Handling**: Proper error responses for invalid requests
- **Performance**: Fast response times for development workflows

## Configuration

The server runs on stdio transport by default. To integrate with Claude Desktop or other MCP clients, add to your configuration:

```json
{
  "mcpServers": {
    "financial-mock": {
      "command": "node",
      "args": ["/path/to/mcp-financial-server/server.js"]
    }
  }
}
```

## Data Samples

### Account Information
```json
{
  "buying_power": "262113.632",
  "portfolio_value": "525487.34",
  "equity": "525487.34",
  "cash": "131056.82"
}
```

### Stock Positions
```json
[
  {
    "symbol": "AAPL",
    "qty": "100",
    "market_value": "18564.00",
    "unrealized_pl": "2564.00",
    "unrealized_plpc": "0.160000"
  }
]
```

### Market Data
```json
{
  "bars": {
    "AAPL": [
      {
        "t": "2024-01-02T05:00:00Z",
        "o": 187.15,
        "h": 188.44, 
        "l": 183.89,
        "c": 185.64,
        "v": 82488200
      }
    ]
  }
}
```

## Development

The server is built with:
- **@modelcontextprotocol/sdk**: Official MCP SDK
- **Modern JavaScript**: ES modules and latest features  
- **Realistic Algorithms**: Proper financial calculations
- **Comprehensive Testing**: Validated against real API responses

## License

MIT License - Feel free to use in your financial applications and trading systems.

---

**Perfect for**: 
- 🧪 **Testing**: Validate financial applications without API costs
- 🏗️ **Development**: Build trading systems with realistic data
- 📚 **Learning**: Explore financial APIs and data structures  
- 🎯 **Prototyping**: Create demos with convincing mock data