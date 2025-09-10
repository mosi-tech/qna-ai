export const FINANCIAL_TOOLS = [
  // Alpaca Trading API Tools
  {
    name: 'alpaca-trading_account',
    description: 'Get account information including buying power, equity, cash balance, and trading status',
    inputSchema: {
      type: 'object',
      properties: {},
      additionalProperties: false,
    },
  },
  {
    name: 'alpaca-trading_positions',
    description: 'Get all open positions with P&L, market values, and quantities',
    inputSchema: {
      type: 'object',
      properties: {},
      additionalProperties: false,
    },
  },
  {
    name: 'alpaca-trading_orders',
    description: 'Get order history and status (filled, open, canceled)',
    inputSchema: {
      type: 'object',
      properties: {
        status: {
          type: 'string',
          description: 'Filter by order status',
          enum: ['open', 'closed', 'canceled', 'filled', 'partially_filled'],
        },
        limit: {
          type: 'number',
          description: 'Number of orders to return',
          default: 100,
        },
        symbols: {
          type: 'string',
          description: 'Comma-separated list of symbols',
        },
      },
      additionalProperties: false,
    },
  },
  {
    name: 'alpaca-trading_portfolio-history',
    description: 'Portfolio performance history showing value changes over time',
    inputSchema: {
      type: 'object',
      properties: {
        period: {
          type: 'string',
          description: 'Time period for history',
          enum: ['1D', '7D', '1M', '3M', '12M', 'YTD', 'ALL'],
          default: '1M',
        },
        timeframe: {
          type: 'string',
          description: 'Data frequency',
          enum: ['1Min', '5Min', '15Min', '1H', '1D'],
          default: '1D',
        },
      },
      additionalProperties: false,
    },
  },
  {
    name: 'alpaca-trading_watchlists',
    description: 'Get user watchlists with symbols',
    inputSchema: {
      type: 'object',
      properties: {},
      additionalProperties: false,
    },
  },
  {
    name: 'alpaca-trading_account-activities',
    description: 'Account activities (trades, fills, transactions)',
    inputSchema: {
      type: 'object',
      properties: {
        activity_type: {
          type: 'string',
          description: 'Type of activity',
          enum: ['FILL', 'TRANS', 'MISC', 'ACATC', 'ACATS'],
        },
        direction: {
          type: 'string',
          enum: ['asc', 'desc'],
          default: 'desc',
        },
        page_size: {
          type: 'number',
          default: 100,
        },
      },
      additionalProperties: false,
    },
  },
  {
    name: 'alpaca-trading_assets',
    description: 'Get tradeable assets/instruments',
    inputSchema: {
      type: 'object',
      properties: {
        status: {
          type: 'string',
          enum: ['active', 'inactive'],
          default: 'active',
        },
        asset_class: {
          type: 'string',
          enum: ['us_equity', 'crypto'],
        },
      },
      additionalProperties: false,
    },
  },
  {
    name: 'alpaca-trading_calendar',
    description: 'Market calendar with open/close times and holidays',
    inputSchema: {
      type: 'object',
      properties: {
        start: {
          type: 'string',
          description: 'Start date (YYYY-MM-DD)',
        },
        end: {
          type: 'string',
          description: 'End date (YYYY-MM-DD)',
        },
      },
      additionalProperties: false,
    },
  },
  {
    name: 'alpaca-trading_clock',
    description: 'Market clock status',
    inputSchema: {
      type: 'object',
      properties: {},
      additionalProperties: false,
    },
  },
  {
    name: 'alpaca-trading_options-contracts',
    description: 'Available options contracts',
    inputSchema: {
      type: 'object',
      properties: {
        underlying_symbol: {
          type: 'string',
          description: 'Underlying stock symbol',
        },
        status: {
          type: 'string',
          enum: ['active', 'inactive'],
          default: 'active',
        },
        type: {
          type: 'string',
          enum: ['call', 'put'],
        },
      },
      additionalProperties: false,
    },
  },
  {
    name: 'alpaca-trading_corporate-actions',
    description: 'Corporate action announcements',
    inputSchema: {
      type: 'object',
      properties: {
        ca_types: {
          type: 'string',
          description: 'Corporate action types (comma-separated)',
        },
        symbol: {
          type: 'string',
          description: 'Stock symbol',
        },
      },
      additionalProperties: false,
    },
  },
  {
    name: 'alpaca-trading_wallets',
    description: 'Crypto wallets information',
    inputSchema: {
      type: 'object',
      properties: {},
      additionalProperties: false,
    },
  },

  // Alpaca Market Data API Tools
  {
    name: 'alpaca-market_stocks-bars',
    description: 'Historical OHLC price bars for stocks',
    inputSchema: {
      type: 'object',
      properties: {
        symbols: {
          type: 'string',
          description: 'Comma-separated stock symbols',
          default: 'AAPL,TSLA,SPY',
        },
        timeframe: {
          type: 'string',
          description: 'Bar timeframe',
          enum: ['1Day', '1Hour', '1Min'],
          default: '1Day',
        },
        start: {
          type: 'string',
          description: 'Start date (YYYY-MM-DD)',
        },
        end: {
          type: 'string',
          description: 'End date (YYYY-MM-DD)',
        },
      },
      required: ['symbols'],
      additionalProperties: false,
    },
  },
  {
    name: 'alpaca-market_stocks-quotes-latest',
    description: 'Latest bid/ask quotes for stocks',
    inputSchema: {
      type: 'object',
      properties: {
        symbols: {
          type: 'string',
          description: 'Comma-separated stock symbols',
          default: 'AAPL,TSLA',
        },
      },
      required: ['symbols'],
      additionalProperties: false,
    },
  },
  {
    name: 'alpaca-market_stocks-trades-latest',
    description: 'Latest trade data for stocks',
    inputSchema: {
      type: 'object',
      properties: {
        symbols: {
          type: 'string',
          description: 'Comma-separated stock symbols',
          default: 'AAPL,TSLA',
        },
      },
      required: ['symbols'],
      additionalProperties: false,
    },
  },
  {
    name: 'alpaca-market_stocks-snapshots',
    description: 'Current market snapshot with all data',
    inputSchema: {
      type: 'object',
      properties: {
        symbols: {
          type: 'string',
          description: 'Comma-separated stock symbols',
          default: 'AAPL,SPY',
        },
      },
      required: ['symbols'],
      additionalProperties: false,
    },
  },
  {
    name: 'alpaca-market_options-quotes-latest',
    description: 'Latest option quotes (bid/ask)',
    inputSchema: {
      type: 'object',
      properties: {
        symbols: {
          type: 'string',
          description: 'Comma-separated option symbols',
          default: 'AAPL241220C00180000',
        },
      },
      required: ['symbols'],
      additionalProperties: false,
    },
  },
  {
    name: 'alpaca-market_options-trades-latest',
    description: 'Latest option trades',
    inputSchema: {
      type: 'object',
      properties: {
        symbols: {
          type: 'string',
          description: 'Comma-separated option symbols',
          default: 'AAPL241220C00180000',
        },
      },
      required: ['symbols'],
      additionalProperties: false,
    },
  },
  {
    name: 'alpaca-market_options-snapshots',
    description: 'Option market snapshots',
    inputSchema: {
      type: 'object',
      properties: {
        symbols: {
          type: 'string',
          description: 'Comma-separated option symbols',
          default: 'AAPL241220C00180000',
        },
      },
      required: ['symbols'],
      additionalProperties: false,
    },
  },
  {
    name: 'alpaca-market_crypto-bars',
    description: 'Cryptocurrency OHLC bars',
    inputSchema: {
      type: 'object',
      properties: {
        symbols: {
          type: 'string',
          description: 'Comma-separated crypto pairs',
          default: 'BTC/USD,ETH/USD',
        },
        timeframe: {
          type: 'string',
          enum: ['1Day', '1Hour', '1Min'],
          default: '1Day',
        },
        loc: {
          type: 'string',
          enum: ['us', 'global'],
          default: 'us',
        },
      },
      required: ['symbols'],
      additionalProperties: false,
    },
  },
  {
    name: 'alpaca-market_forex-rates',
    description: 'Latest forex exchange rates',
    inputSchema: {
      type: 'object',
      properties: {
        currency_pairs: {
          type: 'string',
          description: 'Comma-separated currency pairs',
          default: 'EUR/USD,GBP/USD,USD/JPY',
        },
      },
      required: ['currency_pairs'],
      additionalProperties: false,
    },
  },
  {
    name: 'alpaca-market_screener-most-actives',
    description: 'Screen for most active stocks by volume',
    inputSchema: {
      type: 'object',
      properties: {
        top: {
          type: 'number',
          description: 'Number of top stocks to return',
          default: 10,
          enum: [10, 25, 50],
        },
      },
      additionalProperties: false,
    },
  },
  {
    name: 'alpaca-market_screener-top-gainers',
    description: 'Screen for biggest stock gainers',
    inputSchema: {
      type: 'object',
      properties: {
        top: {
          type: 'number',
          description: 'Number of top gainers to return',
          default: 10,
          enum: [10, 25, 50],
        },
      },
      additionalProperties: false,
    },
  },
  {
    name: 'alpaca-market_screener-top-losers',
    description: 'Screen for biggest stock losers',
    inputSchema: {
      type: 'object',
      properties: {
        top: {
          type: 'number',
          description: 'Number of top losers to return',
          default: 10,
          enum: [10, 25, 50],
        },
      },
      additionalProperties: false,
    },
  },
  {
    name: 'alpaca-market_news',
    description: 'Financial news articles',
    inputSchema: {
      type: 'object',
      properties: {
        symbols: {
          type: 'string',
          description: 'Comma-separated stock symbols',
        },
        sort: {
          type: 'string',
          enum: ['desc', 'asc'],
          default: 'desc',
        },
        include_content: {
          type: 'boolean',
          default: true,
        },
      },
      additionalProperties: false,
    },
  },
  {
    name: 'alpaca-market_corporate-actions',
    description: 'Corporate actions like splits, dividends, mergers',
    inputSchema: {
      type: 'object',
      properties: {
        symbols: {
          type: 'string',
          description: 'Comma-separated stock symbols',
        },
        types: {
          type: 'string',
          description: 'Corporate action types',
        },
      },
      additionalProperties: false,
    },
  },

  // EODHD API Tools
  {
    name: 'eodhd_eod-data',
    description: 'End-of-day historical OHLC prices with adjustments',
    inputSchema: {
      type: 'object',
      properties: {
        symbol: {
          type: 'string',
          description: 'Stock symbol with exchange (e.g., AAPL.US)',
          default: 'AAPL.US',
        },
        period: {
          type: 'string',
          enum: ['d', 'w', 'm'],
          default: 'd',
        },
        from: {
          type: 'string',
          description: 'Start date (YYYY-MM-DD)',
        },
        to: {
          type: 'string',
          description: 'End date (YYYY-MM-DD)',
        },
      },
      required: ['symbol'],
      additionalProperties: false,
    },
  },
  {
    name: 'eodhd_real-time',
    description: 'Real-time stock prices and market data',
    inputSchema: {
      type: 'object',
      properties: {
        symbol: {
          type: 'string',
          description: 'Stock symbol with exchange (e.g., AAPL.US)',
          default: 'AAPL.US',
        },
      },
      required: ['symbol'],
      additionalProperties: false,
    },
  },
  {
    name: 'eodhd_fundamentals',
    description: 'Company fundamental data, financials, and ratios',
    inputSchema: {
      type: 'object',
      properties: {
        symbol: {
          type: 'string',
          description: 'Stock symbol with exchange (e.g., AAPL.US)',
          default: 'AAPL.US',
        },
      },
      required: ['symbol'],
      additionalProperties: false,
    },
  },
  {
    name: 'eodhd_dividends',
    description: 'Dividend payment history with ex-dates',
    inputSchema: {
      type: 'object',
      properties: {
        symbol: {
          type: 'string',
          description: 'Stock symbol with exchange (e.g., AAPL.US)',
          default: 'AAPL.US',
        },
        from: {
          type: 'string',
          description: 'Start date (YYYY-MM-DD)',
        },
        to: {
          type: 'string',
          description: 'End date (YYYY-MM-DD)',
        },
      },
      required: ['symbol'],
      additionalProperties: false,
    },
  },
  {
    name: 'eodhd_splits',
    description: 'Stock split history with ratios',
    inputSchema: {
      type: 'object',
      properties: {
        symbol: {
          type: 'string',
          description: 'Stock symbol with exchange (e.g., AAPL.US)',
          default: 'AAPL.US',
        },
        from: {
          type: 'string',
          description: 'Start date (YYYY-MM-DD)',
        },
        to: {
          type: 'string',
          description: 'End date (YYYY-MM-DD)',
        },
      },
      required: ['symbol'],
      additionalProperties: false,
    },
  },
  {
    name: 'eodhd_technical-indicators',
    description: 'Technical analysis indicators (RSI, MACD, SMA, etc.)',
    inputSchema: {
      type: 'object',
      properties: {
        symbol: {
          type: 'string',
          description: 'Stock symbol with exchange (e.g., AAPL.US)',
          default: 'AAPL.US',
        },
        function: {
          type: 'string',
          description: 'Technical indicator function',
          enum: ['sma', 'ema', 'rsi', 'macd', 'stoch', 'adx', 'cci', 'williams', 'momentum', 'roc'],
          default: 'sma',
        },
        period: {
          type: 'number',
          description: 'Indicator period',
          default: 14,
        },
      },
      required: ['symbol'],
      additionalProperties: false,
    },
  },
  {
    name: 'eodhd_screener',
    description: 'Stock screener with custom filters',
    inputSchema: {
      type: 'object',
      properties: {
        filters: {
          type: 'string',
          description: 'Screener filters',
          default: 'market_cap_more_than.1000000000',
        },
        limit: {
          type: 'number',
          default: 50,
        },
        signals: {
          type: 'string',
          description: 'Trading signals to filter by',
        },
      },
      additionalProperties: false,
    },
  },
  {
    name: 'eodhd_search',
    description: 'Search for stocks by name or symbol',
    inputSchema: {
      type: 'object',
      properties: {
        query: {
          type: 'string',
          description: 'Search query (company name or symbol)',
          default: 'apple',
        },
      },
      required: ['query'],
      additionalProperties: false,
    },
  },
  {
    name: 'eodhd_exchanges',
    description: 'List all supported stock exchanges',
    inputSchema: {
      type: 'object',
      properties: {},
      additionalProperties: false,
    },
  },
  {
    name: 'eodhd_etf-holdings',
    description: 'ETF holdings and composition data',
    inputSchema: {
      type: 'object',
      properties: {
        symbol: {
          type: 'string',
          description: 'ETF symbol with exchange (e.g., SPY.US)',
          default: 'SPY.US',
        },
      },
      required: ['symbol'],
      additionalProperties: false,
    },
  },
  {
    name: 'eodhd_insider-transactions',
    description: 'Corporate insider trading transactions',
    inputSchema: {
      type: 'object',
      properties: {
        symbol: {
          type: 'string',
          description: 'Stock symbol with exchange (e.g., AAPL.US)',
          default: 'AAPL.US',
        },
        from: {
          type: 'string',
          description: 'Start date (YYYY-MM-DD)',
        },
        to: {
          type: 'string',
          description: 'End date (YYYY-MM-DD)',
        },
      },
      required: ['symbol'],
      additionalProperties: false,
    },
  },
  {
    name: 'eodhd_short-interest',
    description: 'Short interest data and short ratio',
    inputSchema: {
      type: 'object',
      properties: {
        symbol: {
          type: 'string',
          description: 'Stock symbol with exchange (e.g., AAPL.US)',
          default: 'AAPL.US',
        },
        from: {
          type: 'string',
          description: 'Start date (YYYY-MM-DD)',
        },
        to: {
          type: 'string',
          description: 'End date (YYYY-MM-DD)',
        },
      },
      required: ['symbol'],
      additionalProperties: false,
    },
  },
  {
    name: 'eodhd_macro-indicators',
    description: 'Macroeconomic indicators and data',
    inputSchema: {
      type: 'object',
      properties: {
        indicator: {
          type: 'string',
          description: 'Macro indicator code',
          default: 'GDPUS.FRED',
        },
        from: {
          type: 'string',
          description: 'Start date (YYYY-MM-DD)',
        },
        to: {
          type: 'string',
          description: 'End date (YYYY-MM-DD)',
        },
      },
      required: ['indicator'],
      additionalProperties: false,
    },
  },
  {
    name: 'eodhd_earnings-calendar',
    description: 'Earnings calendar and corporate events',
    inputSchema: {
      type: 'object',
      properties: {
        symbol: {
          type: 'string',
          description: 'Stock symbol with exchange (e.g., AAPL.US)',
          default: 'AAPL.US',
        },
        from: {
          type: 'string',
          description: 'Start date (YYYY-MM-DD)',
        },
        to: {
          type: 'string',
          description: 'End date (YYYY-MM-DD)',
        },
      },
      required: ['symbol'],
      additionalProperties: false,
    },
  },
];