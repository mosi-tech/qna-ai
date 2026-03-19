/**
 * Template Registry - Pre-defined dashboard layouts for common financial questions
 * Each template maps to an intent and specifies blocks, data contracts, and MCP calls
 */

export interface TemplateBlock {
  blockId: string;
  category: string;
  title: string;
  blockType: 'kpi-card' | 'line-chart' | 'bar-chart' | 'bar-list' | 'donut-chart' | 'spark-chart' | 'table';
  dataKey: string; // Key in template data to pull from
  description?: string;
}

export interface TemplateDefinition {
  id: string;
  name: string;
  description: string;
  intent: string; // e.g., "portfolio_overview", "sector_analysis"
  keywords: string[]; // For classifier matching
  blocks: TemplateBlock[];
  mcpCalls: string[]; // Required MCP functions
  parameters: {
    name: string;
    type: 'string' | 'number' | 'date';
    optional?: boolean;
    description?: string;
  }[];
  estimatedTime: number; // seconds to fetch data
}

export const TEMPLATE_REGISTRY: Record<string, TemplateDefinition> = {
  // ─────────────────────────────────────────────────────────────
  // PORTFOLIO TEMPLATES
  // ─────────────────────────────────────────────────────────────

  portfolio_overview: {
    id: 'portfolio_overview',
    name: 'Portfolio Overview',
    description: 'Complete portfolio snapshot: holdings, P&L, allocation, and recent price movements',
    intent: 'portfolio_overview',
    keywords: ['portfolio', 'holdings', 'allocation', 'positions', 'my stocks'],
    blocks: [
      {
        blockId: 'table-01',
        category: 'tables',
        title: 'Current Holdings',
        blockType: 'table',
        dataKey: 'holdings',
        description: 'Detailed list of all holdings with quantities and values',
      },
      {
        blockId: 'kpi-card-01',
        category: 'kpi-cards',
        title: 'Portfolio Summary',
        blockType: 'kpi-card',
        dataKey: 'kpiMetrics',
        description: 'Total value, P&L, and returns',
      },
      {
        blockId: 'donut-chart-01',
        category: 'donut-charts',
        title: 'Sector Allocation',
        blockType: 'donut-chart',
        dataKey: 'sectorAllocation',
        description: 'How portfolio is distributed across sectors',
      },
      {
        blockId: 'spark-chart-01',
        category: 'spark-charts',
        title: 'Recent Price Movements',
        blockType: 'spark-chart',
        dataKey: 'priceMovements',
        description: 'Last 2 weeks of price action for top holdings',
      },
    ],
    mcpCalls: ['get_positions', 'get_portfolio_history', 'get_real_time_data', 'get_technical_indicator'],
    parameters: [
      { name: 'period', type: 'string', optional: true, description: '1D, 5D, 1M, 3M, 1Y, YTD' },
    ],
    estimatedTime: 4,
  },

  portfolio_performance: {
    id: 'portfolio_performance',
    name: 'Performance Analysis',
    description: 'Detailed performance metrics: returns, volatility, Sharpe ratio, drawdown, benchmarking',
    intent: 'performance_analysis',
    keywords: ['performance', 'returns', 'volatility', 'sharpe', 'drawdown', 'risk-adjusted'],
    blocks: [
      {
        blockId: 'line-chart-01',
        category: 'line-charts',
        title: 'Portfolio vs Benchmark',
        blockType: 'line-chart',
        dataKey: 'performanceComparison',
        description: 'Cumulative returns against S&P 500',
      },
      {
        blockId: 'kpi-card-02',
        category: 'kpi-cards',
        title: 'Risk Metrics',
        blockType: 'kpi-card',
        dataKey: 'riskMetrics',
        description: 'Volatility, Sharpe ratio, max drawdown',
      },
      {
        blockId: 'bar-chart-01',
        category: 'bar-charts',
        title: 'Monthly Returns',
        blockType: 'bar-chart',
        dataKey: 'monthlyReturns',
        description: 'Returns by month for last 12 months',
      },
      {
        blockId: 'bar-list-01',
        category: 'bar-lists',
        title: 'Best/Worst Performers',
        blockType: 'bar-list',
        dataKey: 'topBottomHoldings',
        description: 'Top and bottom 5 holdings by return',
      },
    ],
    mcpCalls: ['get_portfolio_history', 'get_historical_data', 'get_benchmark_data'],
    parameters: [
      { name: 'period', type: 'string', optional: true, description: '3M, 6M, 1Y, 3Y, 5Y, YTD' },
      { name: 'benchmark', type: 'string', optional: true, description: 'SPY, QQQ, IWM (default: SPY)' },
    ],
    estimatedTime: 5,
  },

  // ─────────────────────────────────────────────────────────────
  // SECTOR & ASSET CLASS TEMPLATES
  // ─────────────────────────────────────────────────────────────

  sector_analysis: {
    id: 'sector_analysis',
    name: 'Sector Analysis',
    description: 'Sector breakdown: allocation, performance, composition by sector',
    intent: 'sector_analysis',
    keywords: ['sector', 'sectors', 'industry', 'technology', 'healthcare', 'finance', 'allocation by sector'],
    blocks: [
      {
        blockId: 'donut-chart-01',
        category: 'donut-charts',
        title: 'Sector Allocation',
        blockType: 'donut-chart',
        dataKey: 'sectorWeights',
        description: 'Percentage allocation to each sector',
      },
      {
        blockId: 'bar-chart-01',
        category: 'bar-charts',
        title: 'Sector Performance',
        blockType: 'bar-chart',
        dataKey: 'sectorPerformance',
        description: 'Returns by sector',
      },
      {
        blockId: 'bar-list-01',
        category: 'bar-lists',
        title: 'Top Holdings by Sector',
        blockType: 'bar-list',
        dataKey: 'sectorComposition',
        description: 'Largest positions in each sector',
      },
      {
        blockId: 'table-01',
        category: 'tables',
        title: 'Sector Details',
        blockType: 'table',
        dataKey: 'sectorStats',
        description: 'Detailed metrics per sector',
      },
    ],
    mcpCalls: ['get_positions', 'get_technical_indicator', 'get_historical_data'],
    parameters: [
      { name: 'period', type: 'string', optional: true, description: '1M, 3M, YTD, 1Y' },
    ],
    estimatedTime: 4,
  },

  // ─────────────────────────────────────────────────────────────
  // STOCK RESEARCH TEMPLATES
  // ─────────────────────────────────────────────────────────────

  stock_research: {
    id: 'stock_research',
    name: 'Stock Research',
    description: 'Single stock deep dive: fundamentals, technicals, price history, dividends',
    intent: 'stock_research',
    keywords: ['stock', 'ticker', 'research', 'fundamental', 'technical', 'analysis'],
    blocks: [
      {
        blockId: 'kpi-card-01',
        category: 'kpi-cards',
        title: 'Stock Snapshot',
        blockType: 'kpi-card',
        dataKey: 'stockMetrics',
        description: 'Price, P/E, dividend yield, market cap',
      },
      {
        blockId: 'line-chart-01',
        category: 'line-charts',
        title: 'Price History',
        blockType: 'line-chart',
        dataKey: 'priceHistory',
        description: 'Historical price movement with moving averages',
      },
      {
        blockId: 'bar-list-01',
        category: 'bar-lists',
        title: 'Fundamental Metrics',
        blockType: 'bar-list',
        dataKey: 'fundamentals',
        description: 'P/E, P/B, ROE, dividend yield',
      },
      {
        blockId: 'table-01',
        category: 'tables',
        title: 'Quarterly Performance',
        blockType: 'table',
        dataKey: 'quarterlyData',
        description: 'Last 8 quarters of earnings and revenue',
      },
    ],
    mcpCalls: ['get_real_time_data', 'get_fundamentals', 'get_historical_data', 'get_dividends'],
    parameters: [
      { name: 'symbol', type: 'string', description: 'Stock ticker (e.g., AAPL)' },
      { name: 'period', type: 'string', optional: true, description: '3M, 6M, 1Y, 2Y, 5Y' },
    ],
    estimatedTime: 5,
  },

  // ─────────────────────────────────────────────────────────────
  // ETF TEMPLATES
  // ─────────────────────────────────────────────────────────────

  etf_comparison: {
    id: 'etf_comparison',
    name: 'ETF Comparison',
    description: 'Compare multiple ETFs: performance, holdings, expense ratios, diversification',
    intent: 'etf_comparison',
    keywords: ['etf', 'compare', 'fund', 'comparison', 'expense ratio', 'holdings'],
    blocks: [
      {
        blockId: 'bar-chart-01',
        category: 'bar-charts',
        title: 'Returns Comparison',
        blockType: 'bar-chart',
        dataKey: 'etfReturns',
        description: '1Y, 3Y, 5Y returns for selected ETFs',
      },
      {
        blockId: 'table-01',
        category: 'tables',
        title: 'ETF Metrics',
        blockType: 'table',
        dataKey: 'etfMetrics',
        description: 'Expense ratio, assets, dividend yield, portfolio turnover',
      },
      {
        blockId: 'donut-chart-01',
        category: 'donut-charts',
        title: 'Portfolio Composition',
        blockType: 'donut-chart',
        dataKey: 'etfHoldings',
        description: 'Top sector allocation',
      },
      {
        blockId: 'line-chart-01',
        category: 'line-charts',
        title: 'Price Performance',
        blockType: 'line-chart',
        dataKey: 'etfPerformance',
        description: 'Last year price movements',
      },
    ],
    mcpCalls: ['get_historical_data', 'get_fundamentals', 'get_real_time_data'],
    parameters: [
      { name: 'symbols', type: 'string', description: 'Comma-separated ETF tickers (e.g., SPY,QQQ,IWM)' },
      { name: 'period', type: 'string', optional: true, description: '1Y, 3Y, 5Y' },
    ],
    estimatedTime: 5,
  },

  // ─────────────────────────────────────────────────────────────
  // INCOME & DIVIDEND TEMPLATES
  // ─────────────────────────────────────────────────────────────

  income_dashboard: {
    id: 'income_dashboard',
    name: 'Income Dashboard',
    description: 'Dividend and income focus: yield, distributions, dividend growth, upcoming payments',
    intent: 'income_analysis',
    keywords: ['dividend', 'income', 'yield', 'distribution', 'dividend growth'],
    blocks: [
      {
        blockId: 'kpi-card-01',
        category: 'kpi-cards',
        title: 'Income Summary',
        blockType: 'kpi-card',
        dataKey: 'incomeMetrics',
        description: 'Annual income, yield, monthly income',
      },
      {
        blockId: 'bar-list-01',
        category: 'bar-lists',
        title: 'Top Dividend Payers',
        blockType: 'bar-list',
        dataKey: 'topDividends',
        description: 'Highest yielding holdings',
      },
      {
        blockId: 'line-chart-01',
        category: 'line-charts',
        title: 'Income Trend',
        blockType: 'line-chart',
        dataKey: 'incomeTrend',
        description: 'Monthly dividend income over 12 months',
      },
      {
        blockId: 'table-01',
        category: 'tables',
        title: 'Dividend Holdings',
        blockType: 'table',
        dataKey: 'dividendHoldings',
        description: 'All dividend-paying stocks and their yield',
      },
    ],
    mcpCalls: ['get_positions', 'get_dividends', 'get_real_time_data'],
    parameters: [
      { name: 'minYield', type: 'number', optional: true, description: 'Minimum dividend yield %' },
    ],
    estimatedTime: 4,
  },

  // ─────────────────────────────────────────────────────────────
  // RISK TEMPLATES
  // ─────────────────────────────────────────────────────────────

  risk_dashboard: {
    id: 'risk_dashboard',
    name: 'Risk Dashboard',
    description: 'Risk focus: VaR, concentration, correlation, drawdown, stress scenarios',
    intent: 'risk_analysis',
    keywords: ['risk', 'var', 'volatility', 'concentration', 'drawdown', 'correlation'],
    blocks: [
      {
        blockId: 'kpi-card-01',
        category: 'kpi-cards',
        title: 'Risk Metrics',
        blockType: 'kpi-card',
        dataKey: 'riskKpis',
        description: 'VaR, Volatility, Max Drawdown, Concentration',
      },
      {
        blockId: 'bar-chart-01',
        category: 'bar-charts',
        title: 'Volatility by Holding',
        blockType: 'bar-chart',
        dataKey: 'holdingVolatility',
        description: 'Individual stock volatility',
      },
      {
        blockId: 'bar-list-01',
        category: 'bar-lists',
        title: 'Concentration Risk',
        blockType: 'bar-list',
        dataKey: 'concentrationRisk',
        description: 'Top 10 positions as % of portfolio',
      },
      {
        blockId: 'line-chart-01',
        category: 'line-charts',
        title: 'Drawdown History',
        blockType: 'line-chart',
        dataKey: 'drawdownHistory',
        description: 'Historical peak-to-trough declines',
      },
    ],
    mcpCalls: ['get_portfolio_history', 'get_positions', 'get_technical_indicator'],
    parameters: [
      { name: 'period', type: 'string', optional: true, description: '1Y, 3Y, 5Y' },
    ],
    estimatedTime: 5,
  },

  // ─────────────────────────────────────────────────────────────
  // COMPARISON TEMPLATES
  // ─────────────────────────────────────────────────────────────

  portfolio_vs_benchmark: {
    id: 'portfolio_vs_benchmark',
    name: 'Portfolio vs Benchmark',
    description: 'Head-to-head comparison: returns, volatility, Sharpe ratio, capture ratios, attribution',
    intent: 'benchmark_comparison',
    keywords: ['benchmark', 'vs', 'compare', 'spy', 'qqq', 'performance comparison'],
    blocks: [
      {
        blockId: 'line-chart-01',
        category: 'line-charts',
        title: 'Cumulative Returns',
        blockType: 'line-chart',
        dataKey: 'cumulativeComparison',
        description: 'Portfolio vs Benchmark cumulative growth',
      },
      {
        blockId: 'bar-chart-01',
        category: 'bar-charts',
        title: 'Annual Returns',
        blockType: 'bar-chart',
        dataKey: 'annualReturns',
        description: 'Year-by-year return comparison',
      },
      {
        blockId: 'kpi-card-01',
        category: 'kpi-cards',
        title: 'Risk-Adjusted Metrics',
        blockType: 'kpi-card',
        dataKey: 'riskAdjustedComparison',
        description: 'Sharpe, Alpha, Beta, Information ratio',
      },
      {
        blockId: 'table-01',
        category: 'tables',
        title: 'Performance Attribution',
        blockType: 'table',
        dataKey: 'attributionBreakdown',
        description: 'Contribution to outperformance by holding',
      },
    ],
    mcpCalls: ['get_portfolio_history', 'get_historical_data', 'get_benchmark_data'],
    parameters: [
      { name: 'benchmark', type: 'string', optional: true, description: 'SPY, QQQ, IWM, XLK (default: SPY)' },
      { name: 'period', type: 'string', optional: true, description: '1Y, 3Y, 5Y' },
    ],
    estimatedTime: 5,
  },

  // ─────────────────────────────────────────────────────────────
  // WATCHLIST TEMPLATES
  // ─────────────────────────────────────────────────────────────

  watchlist_monitor: {
    id: 'watchlist_monitor',
    name: 'Watchlist Monitor',
    description: 'Track watched stocks: prices, changes, technical signals, news sentiment',
    intent: 'watchlist',
    keywords: ['watchlist', 'monitoring', 'track', 'watch', 'price alert'],
    blocks: [
      {
        blockId: 'spark-chart-01',
        category: 'spark-charts',
        title: 'Price Activity',
        blockType: 'spark-chart',
        dataKey: 'watchlistPrices',
        description: 'Recent price movements for watched stocks',
      },
      {
        blockId: 'table-01',
        category: 'tables',
        title: 'Watchlist Details',
        blockType: 'table',
        dataKey: 'watchlistData',
        description: 'Current prices, changes, volumes',
      },
      {
        blockId: 'bar-list-01',
        category: 'bar-lists',
        title: 'Top Gainers/Losers',
        blockType: 'bar-list',
        dataKey: 'watchlistMomentum',
        description: 'Best and worst performers in watchlist',
      },
    ],
    mcpCalls: ['get_real_time_data', 'get_latest_trades', 'get_technical_indicator'],
    parameters: [
      { name: 'symbols', type: 'string', description: 'Comma-separated tickers' },
    ],
    estimatedTime: 2,
  },
};

export function getTemplateByIntent(intent: string): TemplateDefinition | null {
  return Object.values(TEMPLATE_REGISTRY).find((t) => t.intent === intent) || null;
}

export function findTemplateByKeywords(query: string): TemplateDefinition | null {
  const lowerQuery = query.toLowerCase();
  return Object.values(TEMPLATE_REGISTRY).find((template) =>
    template.keywords.some((keyword) => lowerQuery.includes(keyword))
  ) || null;
}
