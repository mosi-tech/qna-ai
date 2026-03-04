// Elegant sample data for Robinhood/TradingView style components

export const elegantPortfolioData = {
  currentValue: 47650.82,
  dayChange: -387.23,
  dayChangePercent: -0.81,
  totalReturn: 24.7,
  ytdReturn: 8.4,
  sharpeRatio: 1.45,
  maxDrawdown: -12.3,
  
  chartData: [
    { date: new Date('2024-01-01'), value: 38250, benchmark: 37800 },
    { date: new Date('2024-01-15'), value: 39100, benchmark: 38200 },
    { date: new Date('2024-02-01'), value: 38950, benchmark: 38400 },
    { date: new Date('2024-02-15'), value: 40200, benchmark: 39100 },
    { date: new Date('2024-03-01'), value: 41100, benchmark: 39800 },
    { date: new Date('2024-03-15'), value: 40800, benchmark: 40200 },
    { date: new Date('2024-04-01'), value: 42300, benchmark: 40900 },
    { date: new Date('2024-04-15'), value: 43100, benchmark: 41500 },
    { date: new Date('2024-05-01'), value: 44200, benchmark: 42200 },
    { date: new Date('2024-05-15'), value: 43800, benchmark: 42800 },
    { date: new Date('2024-06-01'), value: 45100, benchmark: 43500 },
    { date: new Date('2024-06-15'), value: 46200, benchmark: 44200 },
    { date: new Date('2024-07-01'), value: 47100, benchmark: 45100 },
    { date: new Date('2024-07-15'), value: 47800, benchmark: 45800 },
    { date: new Date('2024-08-01'), value: 46900, benchmark: 45200 },
    { date: new Date('2024-08-15'), value: 48200, benchmark: 46100 },
    { date: new Date('2024-09-01'), value: 47500, benchmark: 45900 },
    { date: new Date('2024-09-15'), value: 48800, benchmark: 46800 },
    { date: new Date('2024-10-01'), value: 48100, benchmark: 46500 },
    { date: new Date('2024-10-15'), value: 49200, benchmark: 47200 },
    { date: new Date('2024-11-01'), value: 48400, benchmark: 46900 },
    { date: new Date('2024-11-15'), value: 47650, benchmark: 46400 }
  ]
};

// TradingView style price data with more granularity
export const tradingViewStyleData = {
  symbol: "AAPL",
  currentPrice: 189.43,
  dayChange: -2.87,
  dayChangePercent: -1.49,
  volume: 58420000,
  marketCap: "2.94T",
  
  priceData: [
    { date: new Date('2024-11-01T09:30:00'), price: 192.30, volume: 2100000 },
    { date: new Date('2024-11-01T10:00:00'), price: 191.85, volume: 1800000 },
    { date: new Date('2024-11-01T10:30:00'), price: 192.15, volume: 1600000 },
    { date: new Date('2024-11-01T11:00:00'), price: 191.90, volume: 1400000 },
    { date: new Date('2024-11-01T11:30:00'), price: 192.40, volume: 1900000 },
    { date: new Date('2024-11-01T12:00:00'), price: 192.10, volume: 1200000 },
    { date: new Date('2024-11-01T12:30:00'), price: 191.75, volume: 1100000 },
    { date: new Date('2024-11-01T13:00:00'), price: 191.45, volume: 1300000 },
    { date: new Date('2024-11-01T13:30:00'), price: 190.95, volume: 2200000 },
    { date: new Date('2024-11-01T14:00:00'), price: 190.20, volume: 2800000 },
    { date: new Date('2024-11-01T14:30:00'), price: 189.85, volume: 3100000 },
    { date: new Date('2024-11-01T15:00:00'), price: 189.60, volume: 2900000 },
    { date: new Date('2024-11-01T15:30:00'), price: 189.43, volume: 3500000 },
    { date: new Date('2024-11-01T16:00:00'), price: 189.43, volume: 4200000 }
  ]
};

// Clean allocation data for pie charts
export const elegantAllocationData = [
  { 
    name: "US Stocks", 
    value: 29870, 
    color: "#10B981",
    target: 65,
    risk: 'high' as const,
    expectedReturn: 10.2,
    sharpeRatio: 0.85
  },
  { 
    name: "International", 
    value: 8675, 
    color: "#3B82F6",
    target: 20,
    risk: 'high' as const,
    expectedReturn: 8.7,
    sharpeRatio: 0.72
  },
  { 
    name: "Bonds", 
    value: 6100, 
    color: "#6B7280",
    target: 12,
    risk: 'low' as const,
    expectedReturn: 4.2,
    sharpeRatio: 0.45
  },
  { 
    name: "REITs", 
    value: 1955, 
    color: "#F59E0B",
    target: 5,
    risk: 'medium' as const,
    expectedReturn: 7.8,
    sharpeRatio: 0.65
  },
  { 
    name: "Cash", 
    value: 1051, 
    color: "#EF4444",
    target: 3,
    risk: 'low' as const,
    expectedReturn: 2.1,
    sharpeRatio: 0.20
  }
];

// Holdings data - clean and minimal
export const elegantHoldingsData = [
  { 
    symbol: "AAPL", 
    name: "Apple Inc.", 
    shares: 125, 
    value: 23679.75,
    weight: 8.7,
    dayChange: -1.49,
    sector: "Technology",
    pe: 28.4,
    yield: 0.5
  },
  { 
    symbol: "MSFT", 
    name: "Microsoft Corp.", 
    shares: 48, 
    value: 18432.00,
    weight: 6.8,
    dayChange: 0.34,
    sector: "Technology",
    pe: 35.2,
    yield: 0.7
  },
  { 
    symbol: "GOOGL", 
    name: "Alphabet Inc.", 
    shares: 87, 
    value: 13298.01,
    weight: 4.9,
    dayChange: -0.82,
    sector: "Technology",
    pe: 24.1
  },
  { 
    symbol: "TSLA", 
    name: "Tesla Inc.", 
    shares: 52, 
    value: 11284.00,
    weight: 4.2,
    dayChange: -3.45,
    sector: "Consumer Discretionary",
    pe: 89.7
  },
  { 
    symbol: "AMZN", 
    name: "Amazon.com Inc.", 
    shares: 67, 
    value: 10234.55,
    weight: 3.8,
    dayChange: 1.23,
    sector: "Consumer Discretionary",
    pe: 52.3
  },
  { 
    symbol: "NVDA", 
    name: "NVIDIA Corporation", 
    shares: 24, 
    value: 9876.50,
    weight: 3.6,
    dayChange: 2.87,
    sector: "Technology",
    pe: 61.2
  },
  { 
    symbol: "BRK.B", 
    name: "Berkshire Hathaway", 
    shares: 31, 
    value: 8745.20,
    weight: 3.2,
    dayChange: 0.15,
    sector: "Financials",
    pe: 8.9,
    yield: 0.0
  },
  { 
    symbol: "JPM", 
    name: "JPMorgan Chase & Co.", 
    shares: 58, 
    value: 7654.30,
    weight: 2.8,
    dayChange: -0.67,
    sector: "Financials",
    pe: 12.4,
    yield: 2.3
  }
];

// Risk metrics data for elegant dashboard
export const elegantRiskMetrics = {
  sharpe: 1.45,
  sortino: 1.67,
  beta: 1.08,
  volatility: 18.5,
  maxDrawdown: -12.3,
  var95: -2.1,
  var99: -3.8,
  expectedShortfall: -4.2,
  calmar: 1.89,
  treynor: 0.089
};

// Volatility regime data
export const elegantVolatilityData = [
  { date: new Date('2024-01-01'), volatility: 15.2, regime: 'normal' as const },
  { date: new Date('2024-01-15'), volatility: 16.8, regime: 'normal' as const },
  { date: new Date('2024-02-01'), volatility: 22.4, regime: 'high' as const },
  { date: new Date('2024-02-15'), volatility: 28.9, regime: 'high' as const },
  { date: new Date('2024-03-01'), volatility: 31.2, regime: 'crisis' as const },
  { date: new Date('2024-03-15'), volatility: 25.7, regime: 'high' as const },
  { date: new Date('2024-04-01'), volatility: 19.3, regime: 'normal' as const },
  { date: new Date('2024-04-15'), volatility: 14.8, regime: 'normal' as const },
  { date: new Date('2024-05-01'), volatility: 12.1, regime: 'low' as const },
  { date: new Date('2024-05-15'), volatility: 11.5, regime: 'low' as const },
  { date: new Date('2024-06-01'), volatility: 13.9, regime: 'normal' as const },
  { date: new Date('2024-06-15'), volatility: 16.2, regime: 'normal' as const },
  { date: new Date('2024-07-01'), volatility: 18.7, regime: 'normal' as const },
  { date: new Date('2024-07-15'), volatility: 17.3, regime: 'normal' as const },
  { date: new Date('2024-08-01'), volatility: 21.5, regime: 'high' as const },
  { date: new Date('2024-08-15'), volatility: 19.8, regime: 'normal' as const },
  { date: new Date('2024-09-01'), volatility: 16.4, regime: 'normal' as const },
  { date: new Date('2024-09-15'), volatility: 15.7, regime: 'normal' as const },
  { date: new Date('2024-10-01'), volatility: 18.9, regime: 'normal' as const },
  { date: new Date('2024-10-15'), volatility: 20.2, regime: 'high' as const },
  { date: new Date('2024-11-01'), volatility: 18.5, regime: 'normal' as const }
];

// Drawdown data
export const elegantDrawdownData = [
  { date: new Date('2024-01-01'), drawdown: 0, underwater: false },
  { date: new Date('2024-01-15'), drawdown: -1.2, underwater: true },
  { date: new Date('2024-02-01'), drawdown: -2.8, underwater: true },
  { date: new Date('2024-02-15'), drawdown: -5.4, underwater: true },
  { date: new Date('2024-03-01'), drawdown: -12.3, underwater: true },
  { date: new Date('2024-03-15'), drawdown: -8.9, underwater: true },
  { date: new Date('2024-04-01'), drawdown: -4.2, underwater: true },
  { date: new Date('2024-04-15'), drawdown: -1.8, underwater: true },
  { date: new Date('2024-05-01'), drawdown: 0, underwater: false },
  { date: new Date('2024-05-15'), drawdown: -0.5, underwater: true },
  { date: new Date('2024-06-01'), drawdown: 0, underwater: false },
  { date: new Date('2024-06-15'), drawdown: 0, underwater: false },
  { date: new Date('2024-07-01'), drawdown: 0, underwater: false },
  { date: new Date('2024-07-15'), drawdown: 0, underwater: false },
  { date: new Date('2024-08-01'), drawdown: -2.1, underwater: true },
  { date: new Date('2024-08-15'), drawdown: 0, underwater: false },
  { date: new Date('2024-09-01'), drawdown: -1.3, underwater: true },
  { date: new Date('2024-09-15'), drawdown: 0, underwater: false },
  { date: new Date('2024-10-01'), drawdown: -0.8, underwater: true },
  { date: new Date('2024-10-15'), drawdown: 0, underwater: false },
  { date: new Date('2024-11-01'), drawdown: 0, underwater: false }
];

// Attribution analysis data
export const elegantAttributionData = [
  {
    name: "Technology",
    selection: 2.4,
    allocation: -0.3,
    interaction: 0.1,
    total: 2.2,
    description: "Overweight in AI leaders",
    category: "sector" as const
  },
  {
    name: "Healthcare",
    selection: 0.8,
    allocation: 0.5,
    interaction: 0.0,
    total: 1.3,
    description: "Biotech allocation timing",
    category: "sector" as const
  },
  {
    name: "Quality Factor",
    selection: 1.1,
    allocation: -0.2,
    interaction: 0.0,
    total: 0.9,
    description: "High ROE stock selection",
    category: "factor" as const
  },
  {
    name: "Financials",
    selection: -0.4,
    allocation: 0.2,
    interaction: -0.1,
    total: -0.3,
    description: "Regional bank exposure",
    category: "sector" as const
  },
  {
    name: "Energy",
    selection: -0.8,
    allocation: -0.6,
    interaction: -0.2,
    total: -1.6,
    description: "Underweight energy",
    category: "sector" as const
  }
];