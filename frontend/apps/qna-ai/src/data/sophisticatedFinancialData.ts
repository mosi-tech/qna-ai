// Portfolio data interface
interface PortfolioData {
  currentValue: number;
  totalReturn: number;
  dailyChange: number;
  inception: string;
  
  performance: {
    ytd: number;
    "1y": number;
    "3y": number;
    "5y": number;
    inception: number;
  };
  
  riskMetrics: {
    sharpe: number;
    sortino: number;
    beta: number;
    volatility: number;
    maxDrawdown: number;
    var95: number;
  };
  
  attribution: {
    alpha: number;
    factorContribution: Array<{
      name: string;
      contribution: number;
      exposure: number;
    }>;
  };
  
  allocation: Array<{
    name: string;
    value: number;
    change: number;
    weight: number;
  }>;
  
  chartData: Array<{
    date: string;
    portfolio: number;
    benchmark: number;
    drawdown?: number;
  }>;
  
  topHoldings: Array<{
    symbol: string;
    name: string;
    weight: number;
    dayChange: number;
    contribution: number;
    sector: string;
  }>;
  
  marketRegime: 'bull' | 'bear' | 'sideways' | 'volatile';
  riskLevel: 'conservative' | 'moderate' | 'aggressive';
  benchmark: string;
}

export const sophisticatedPortfolioData: PortfolioData = {
  currentValue: 847650,
  totalReturn: 24.7,
  dailyChange: -0.83,
  inception: "Jan 2021",
  benchmark: "SPY",
  marketRegime: "volatile",
  riskLevel: "moderate",

  performance: {
    ytd: 8.4,
    "1y": 12.7,
    "3y": 15.2,
    "5y": 11.8,
    inception: 24.7
  },

  riskMetrics: {
    sharpe: 1.42,
    sortino: 1.67,
    beta: 1.08,
    volatility: 18.5,
    maxDrawdown: -12.3,
    var95: -2.1
  },

  attribution: {
    alpha: 2.4,
    factorContribution: [
      { name: "Quality", contribution: 1.8, exposure: 0.65 },
      { name: "Growth", contribution: 1.2, exposure: 0.45 },
      { name: "Size", contribution: -0.3, exposure: -0.15 },
      { name: "Value", contribution: -0.8, exposure: -0.25 }
    ]
  },

  allocation: [
    { name: "US Large Cap", value: 387500, change: 1.2, weight: 45.7 },
    { name: "US Small Cap", value: 127450, change: -2.1, weight: 15.0 },
    { name: "International Dev", value: 169530, change: 0.8, weight: 20.0 },
    { name: "Emerging Markets", value: 76365, change: -1.5, weight: 9.0 },
    { name: "Bonds", value: 59247, change: 0.3, weight: 7.0 },
    { name: "REITs", value: 27558, change: -0.9, weight: 3.3 }
  ],

  chartData: [
    { date: "2021-01", portfolio: 0, benchmark: 0 },
    { date: "2021-02", portfolio: 2.3, benchmark: 1.8, drawdown: -0.5 },
    { date: "2021-03", portfolio: 5.8, benchmark: 4.2, drawdown: 0 },
    { date: "2021-04", portfolio: 8.2, benchmark: 6.1, drawdown: 0 },
    { date: "2021-05", portfolio: 6.9, benchmark: 5.3, drawdown: -1.3 },
    { date: "2021-06", portfolio: 9.1, benchmark: 7.4, drawdown: 0 },
    { date: "2021-07", portfolio: 11.5, benchmark: 9.2, drawdown: 0 },
    { date: "2021-08", portfolio: 13.2, benchmark: 10.8, drawdown: 0 },
    { date: "2021-09", portfolio: 10.8, benchmark: 8.9, drawdown: -2.4 },
    { date: "2021-10", portfolio: 14.6, benchmark: 11.7, drawdown: 0 },
    { date: "2021-11", portfolio: 16.9, benchmark: 13.4, drawdown: 0 },
    { date: "2021-12", portfolio: 18.5, benchmark: 15.1, drawdown: 0 },
    { date: "2022-01", portfolio: 15.2, benchmark: 12.8, drawdown: -3.3 },
    { date: "2022-02", portfolio: 12.8, benchmark: 11.2, drawdown: -5.7 },
    { date: "2022-03", portfolio: 10.1, benchmark: 9.1, drawdown: -8.4 },
    { date: "2022-04", portfolio: 13.7, benchmark: 11.8, drawdown: -4.8 },
    { date: "2022-05", portfolio: 8.9, benchmark: 8.7, drawdown: -9.6 },
    { date: "2022-06", portfolio: 5.4, benchmark: 6.9, drawdown: -12.3 },
    { date: "2022-07", portfolio: 7.8, benchmark: 8.4, drawdown: -10.7 },
    { date: "2022-08", portfolio: 9.2, benchmark: 9.8, drawdown: -9.3 },
    { date: "2022-09", portfolio: 6.1, benchmark: 7.2, drawdown: -12.4 },
    { date: "2022-10", portfolio: 8.7, benchmark: 9.1, drawdown: -9.8 },
    { date: "2022-11", portfolio: 11.3, benchmark: 10.8, drawdown: -7.2 },
    { date: "2022-12", portfolio: 9.8, benchmark: 9.6, drawdown: -8.7 },
    { date: "2023-01", portfolio: 12.4, benchmark: 11.2, drawdown: -6.1 },
    { date: "2023-02", portfolio: 15.1, benchmark: 13.1, drawdown: -3.4 },
    { date: "2023-03", portfolio: 13.8, benchmark: 12.4, drawdown: -4.7 },
    { date: "2023-04", portfolio: 16.5, benchmark: 14.2, drawdown: -2.0 },
    { date: "2023-05", portfolio: 18.2, benchmark: 15.8, drawdown: -0.3 },
    { date: "2023-06", portfolio: 21.1, benchmark: 17.9, drawdown: 0 },
    { date: "2023-07", portfolio: 23.7, benchmark: 19.2, drawdown: 0 },
    { date: "2023-08", portfolio: 22.4, benchmark: 18.6, drawdown: -1.3 },
    { date: "2023-09", portfolio: 20.8, benchmark: 17.4, drawdown: -2.9 },
    { date: "2023-10", portfolio: 18.6, benchmark: 16.1, drawdown: -5.1 },
    { date: "2023-11", portfolio: 21.9, benchmark: 18.7, drawdown: -1.8 },
    { date: "2023-12", portfolio: 24.3, benchmark: 20.4, drawdown: 0 },
    { date: "2024-01", portfolio: 26.1, benchmark: 21.8, drawdown: 0 },
    { date: "2024-02", portfolio: 28.4, benchmark: 23.2, drawdown: 0 },
    { date: "2024-03", portfolio: 26.7, benchmark: 22.1, drawdown: -1.7 },
    { date: "2024-04", portfolio: 29.2, benchmark: 24.5, drawdown: 0 },
    { date: "2024-05", portfolio: 31.8, benchmark: 26.1, drawdown: 0 },
    { date: "2024-06", portfolio: 30.1, benchmark: 25.3, drawdown: -1.7 },
    { date: "2024-07", portfolio: 33.2, benchmark: 27.8, drawdown: 0 },
    { date: "2024-08", portfolio: 31.9, benchmark: 26.9, drawdown: -1.3 },
    { date: "2024-09", portfolio: 29.4, benchmark: 25.1, drawdown: -3.8 },
    { date: "2024-10", portfolio: 32.1, benchmark: 27.3, drawdown: -1.1 },
    { date: "2024-11", portfolio: 24.7, benchmark: 20.8, drawdown: -8.5 }
  ],

  topHoldings: [
    {
      symbol: "AAPL",
      name: "Apple Inc.",
      weight: 8.7,
      dayChange: -1.2,
      contribution: -8.4,
      sector: "Technology"
    },
    {
      symbol: "MSFT", 
      name: "Microsoft Corporation",
      weight: 6.8,
      dayChange: 0.3,
      contribution: 2.1,
      sector: "Technology"
    },
    {
      symbol: "GOOGL",
      name: "Alphabet Inc.",
      weight: 4.9,
      dayChange: -2.1,
      contribution: -12.3,
      sector: "Technology"
    },
    {
      symbol: "AMZN",
      name: "Amazon.com Inc.",
      weight: 4.2,
      dayChange: -0.8,
      contribution: -3.6,
      sector: "Consumer Disc."
    },
    {
      symbol: "TSLA",
      name: "Tesla Inc.",
      weight: 3.8,
      dayChange: -3.4,
      contribution: -15.7,
      sector: "Consumer Disc."
    },
    {
      symbol: "NVDA",
      name: "NVIDIA Corporation", 
      weight: 3.5,
      dayChange: 1.8,
      contribution: 6.9,
      sector: "Technology"
    },
    {
      symbol: "META",
      name: "Meta Platforms Inc.",
      weight: 2.9,
      dayChange: -1.6,
      contribution: -5.2,
      sector: "Technology"
    },
    {
      symbol: "JNJ",
      name: "Johnson & Johnson",
      weight: 2.1,
      dayChange: 0.2,
      contribution: 0.8,
      sector: "Healthcare"
    }
  ]
};

// Alternative data for different portfolio types
export const conservativePortfolioData: PortfolioData = {
  ...sophisticatedPortfolioData,
  currentValue: 524200,
  totalReturn: 8.4,
  dailyChange: -0.12,
  marketRegime: "sideways",
  riskLevel: "conservative",
  
  riskMetrics: {
    sharpe: 1.18,
    sortino: 1.35,
    beta: 0.72,
    volatility: 8.9,
    maxDrawdown: -4.2,
    var95: -0.8
  },

  allocation: [
    { name: "US Bonds", value: 209680, change: 0.1, weight: 40.0 },
    { name: "US Large Cap", value: 157260, change: 0.8, weight: 30.0 },
    { name: "International Bonds", value: 78630, change: -0.2, weight: 15.0 },
    { name: "Treasury Bills", value: 52420, change: 0.05, weight: 10.0 },
    { name: "REITs", value: 26210, change: -0.4, weight: 5.0 }
  ]
};

export const aggressivePortfolioData: PortfolioData = {
  ...sophisticatedPortfolioData,
  currentValue: 1250000,
  totalReturn: 42.8,
  dailyChange: -2.4,
  marketRegime: "bull",
  riskLevel: "aggressive",
  
  riskMetrics: {
    sharpe: 1.65,
    sortino: 2.12,
    beta: 1.35,
    volatility: 28.7,
    maxDrawdown: -22.1,
    var95: -3.8
  },

  allocation: [
    { name: "US Growth", value: 625000, change: -1.8, weight: 50.0 },
    { name: "Emerging Markets", value: 250000, change: -3.2, weight: 20.0 },
    { name: "Small Cap", value: 187500, change: -2.1, weight: 15.0 },
    { name: "Crypto", value: 125000, change: -8.4, weight: 10.0 },
    { name: "Commodities", value: 62500, change: 1.2, weight: 5.0 }
  ]
};