import { ModuleConfig } from '@/types/modules';

export const modules: ModuleConfig = {
  rebalance: {
    title: "Portfolio Rebalancing Analysis",
    description: "Analyze the impact of different rebalancing frequencies on portfolio performance",
    category: "Portfolio Management",
    difficulty: "Intermediate",
    estimatedTime: "2-3 minutes",
    params: [
      { 
        type: "dropdown", 
        label: "Rebalancing Frequency", 
        options: ["Monthly", "Quarterly", "Semi-Annually", "Yearly"],
        defaultValue: "Quarterly"
      },
      { 
        type: "input", 
        label: "Transaction Cost (%)",
        defaultValue: "0.15",
        placeholder: "e.g., 0.1 for 0.1%"
      },
      { 
        type: "dropdown", 
        label: "Benchmark", 
        options: ["SPY (S&P 500)", "QQQ (NASDAQ-100)", "IWM (Russell 2000)", "VTI (Total Stock Market)"],
        defaultValue: "SPY (S&P 500)"
      },
      {
        type: "dropdown",
        label: "Portfolio Type",
        options: ["60/40 Stocks/Bonds", "All Weather", "Three-Fund Portfolio", "Custom"],
        defaultValue: "60/40 Stocks/Bonds"
      }
    ]
  },
  backtest: {
    title: "Visual Strategy Backtest",
    description: "Build and backtest trading strategies using a visual block-based interface",
    category: "Strategy Testing",
    difficulty: "Advanced",
    estimatedTime: "5-10 minutes",
    params: [
      {
        type: "input",
        label: "Primary Symbols",
        defaultValue: "AAPL,MSFT",
        placeholder: "e.g., AAPL,MSFT,SPY"
      },
      {
        type: "dropdown",
        label: "Initial Investment",
        options: ["$10,000", "$25,000", "$50,000", "$100,000", "$250,000"],
        defaultValue: "$100,000"
      },
      {
        type: "date",
        label: "Backtest Start",
        defaultValue: "2023-01-01"
      },
      {
        type: "date",
        label: "Backtest End",
        defaultValue: "2024-01-01"
      },
      {
        type: "dropdown",
        label: "Risk Management",
        options: ["Conservative (3% stop loss)", "Moderate (5% stop loss)", "Aggressive (10% stop loss)", "Custom"],
        defaultValue: "Moderate (5% stop loss)"
      }
    ]
  },
  regression: {
    title: "Factor Regression Analysis",
    description: "Understand your portfolio's factor exposures and risk characteristics",
    category: "Risk Analysis",
    difficulty: "Advanced",
    estimatedTime: "2-4 minutes",
    params: [
      { 
        type: "dropdown", 
        label: "Portfolio/Security", 
        options: ["My Tech Portfolio", "My ETF Portfolio", "AAPL", "TSLA", "ARKK", "Custom Upload"],
        defaultValue: "My Tech Portfolio"
      },
      { 
        type: "checkbox", 
        label: "Risk Factors", 
        options: ["Market (Beta)", "Size (SMB)", "Value (HML)", "Momentum (UMD)", "Quality", "Volatility"],
        defaultValue: ["Market (Beta)", "Size (SMB)", "Value (HML)"]
      },
      { 
        type: "date", 
        label: "Analysis Period Start",
        defaultValue: "2022-01-01"
      },
      { 
        type: "date", 
        label: "Analysis Period End",
        defaultValue: "2024-01-01"
      },
      {
        type: "dropdown",
        label: "Return Frequency",
        options: ["Daily", "Weekly", "Monthly"],
        defaultValue: "Weekly"
      }
    ]
  },
  risk: {
    title: "Portfolio Risk Assessment",
    description: "Comprehensive risk analysis including VaR, stress testing, and correlation analysis",
    category: "Risk Analysis",
    difficulty: "Intermediate",
    estimatedTime: "2-3 minutes",
    params: [
      {
        type: "dropdown",
        label: "Portfolio",
        options: ["Current Holdings", "Proposed Portfolio", "Benchmark Comparison"],
        defaultValue: "Current Holdings"
      },
      {
        type: "dropdown",
        label: "Risk Metrics",
        options: ["Value at Risk (VaR)", "Expected Shortfall", "Maximum Drawdown", "Beta Analysis"],
        defaultValue: "Value at Risk (VaR)"
      },
      {
        type: "dropdown",
        label: "Confidence Level",
        options: ["90%", "95%", "99%"],
        defaultValue: "95%"
      },
      {
        type: "input",
        label: "Time Horizon (days)",
        defaultValue: "30"
      }
    ]
  },
  screening: {
    title: "Stock Screening & Discovery",
    description: "Find stocks based on fundamental, technical, and custom criteria",
    category: "Stock Discovery",
    difficulty: "Beginner",
    estimatedTime: "1-2 minutes",
    params: [
      {
        type: "dropdown",
        label: "Screen Type",
        options: ["Fundamental", "Technical", "Dividend", "Growth", "Value"],
        defaultValue: "Fundamental"
      },
      {
        type: "dropdown",
        label: "Market Cap",
        options: ["All", "Large Cap (>$10B)", "Mid Cap ($2B-$10B)", "Small Cap (<$2B)"],
        defaultValue: "Large Cap (>$10B)"
      },
      {
        type: "checkbox",
        label: "Sectors",
        options: ["Technology", "Healthcare", "Financial", "Consumer Discretionary", "Energy", "Industrials"],
        defaultValue: ["Technology", "Healthcare"]
      },
      {
        type: "dropdown",
        label: "Sort By",
        options: ["Market Cap", "P/E Ratio", "Dividend Yield", "Revenue Growth", "Price Performance"],
        defaultValue: "Market Cap"
      }
    ]
  },
  correlation: {
    title: "Asset Correlation Analysis",
    description: "Analyze correlations between assets to optimize diversification",
    category: "Portfolio Management", 
    difficulty: "Intermediate",
    estimatedTime: "2-3 minutes",
    params: [
      {
        type: "input",
        label: "Assets (comma-separated)",
        defaultValue: "AAPL,GOOGL,MSFT,TSLA,SPY",
        placeholder: "e.g., AAPL,MSFT,GOOGL"
      },
      {
        type: "dropdown",
        label: "Time Period",
        options: ["1 Month", "3 Months", "6 Months", "1 Year", "2 Years", "5 Years"],
        defaultValue: "1 Year"
      },
      {
        type: "dropdown",
        label: "Correlation Type",
        options: ["Pearson", "Spearman", "Rolling Correlation"],
        defaultValue: "Pearson"
      },
      {
        type: "dropdown",
        label: "Data Frequency",
        options: ["Daily", "Weekly", "Monthly"],
        defaultValue: "Daily"
      }
    ]
  },
  strategy_builder: {
    title: "Visual Strategy Builder",
    description: "Build and backtest trading strategies using a visual block-based interface",
    category: "Strategy Testing",
    difficulty: "Advanced",
    estimatedTime: "5-10 minutes",
    params: [
      {
        type: "input",
        label: "Primary Symbols",
        defaultValue: "AAPL,MSFT",
        placeholder: "e.g., AAPL,MSFT,SPY"
      },
      {
        type: "dropdown",
        label: "Initial Investment",
        options: ["$10,000", "$25,000", "$50,000", "$100,000", "$250,000"],
        defaultValue: "$100,000"
      },
      {
        type: "date",
        label: "Backtest Start",
        defaultValue: "2023-01-01"
      },
      {
        type: "date",
        label: "Backtest End",
        defaultValue: "2024-01-01"
      },
      {
        type: "dropdown",
        label: "Risk Management",
        options: ["Conservative (3% stop loss)", "Moderate (5% stop loss)", "Aggressive (10% stop loss)", "Custom"],
        defaultValue: "Moderate (5% stop loss)"
      }
    ]
  }
};