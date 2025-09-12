// Registry mapping for experimental JSON outputs
export const registryMap = {
  "triangle-pattern-breakouts": {
    id: "triangle-pattern-breakouts",
    name: "Triangle Pattern Breakout Scanner",
    file: "experimental/TrianglePatternBreakouts.json"
  },
  "treasury-tlt-interest-rate-hedge": {
    id: "treasury-tlt-interest-rate-hedge",
    name: "Long-Term Treasury TLT Interest Rate Hedge Analysis",
    file: "experimental/TreasuryTLTInterestRateHedge.json"
  },
  "keltner-channels-analysis": {
    id: "keltner-channels-analysis",
    name: "Keltner Channels Breakout Analysis",
    file: "experimental/KeltnerChannelsAnalysis.json"
  },
  "macd-crossover-signals": {
    id: "macd-crossover-signals",
    name: "MACD Crossover Signal Analysis",
    file: "experimental/MACDCrossoverSignals.json"
  },
  "price-volume-breakouts": {
    id: "price-volume-breakouts",
    name: "Price Volume Breakout Analysis",
    file: "experimental/PriceVolumeBreakouts.json"
  },
  "three-black-crows-pattern": {
    id: "three-black-crows-pattern",
    name: "Three Black Crows Bearish Pattern",
    file: "experimental/ThreeBlackCrowsPattern.json"
  },
  "adx-trend-strength": {
    id: "adx-trend-strength",
    name: "ADX Trend Strength Analysis",
    file: "experimental/ADXTrendStrength.json"
  },
  "accumulation-distribution-line": {
    id: "accumulation-distribution-line",
    name: "Accumulation Distribution Line Analysis", 
    file: "experimental/AccumulationDistributionLine.json"
  },
  "aapl-weekday-trading-analysis": {
    id: "aapl-weekday-trading-analysis",
    name: "AAPL Weekday Trading Analysis",
    file: "experimental/AAPLWeekdayTradingAnalysis.json"
  },
  "sector-etf-friday-performance": {
    id: "sector-etf-friday-performance",
    name: "Sector ETF Friday Performance Analysis",
    file: "experimental/SectorETFFridayPerformance.json"
  },
  "first-hour-momentum-leaders": {
    id: "first-hour-momentum-leaders",
    name: "First Hour Momentum Leaders (3+ Sessions)",
    file: "experimental/FirstHourMomentumLeaders.json"
  },
  "holdings-news-sensitivity-analysis": {
    id: "holdings-news-sensitivity-analysis",
    name: "Holdings News Sensitivity Analysis",
    file: "experimental/HoldingsNewsSensitivityAnalysis.json"
  },
  "holdings-least-correlated": {
    id: "holdings-least-correlated",
    name: "Holdings Least Correlated Analysis",
    file: "experimental/HoldingsLeastCorrelated.json"
  },
  "highest-up-day-percentage": {
    id: "highest-up-day-percentage",
    name: "Highest Up Day Percentage (30-Day)",
    file: "experimental/HighestUpDayPercentage.json"
  },
  "watchlist-momentum-ranking": {
    id: "watchlist-momentum-ranking",
    name: "Watchlist Momentum Ranking (6-Month)",
    file: "experimental/WatchlistMomentumRanking.json"
  },
  "closing-volume-spikes": {
    id: "closing-volume-spikes",
    name: "Largest Closing Volume Spikes Today",
    file: "experimental/ClosingVolumeSpikes.json"
  },
  "downside-gap-fills": {
    id: "downside-gap-fills",
    name: "Largest Downside Gap Fills Today",
    file: "experimental/DownsideGapFills.json"
  },
  "position-rebound-after-3-down-days": {
    id: "position-rebound-after-3-down-days",
    name: "Position Rebound After 3 Down Days",
    file: "experimental/PositionReboundAfter3DownDays.json"
  },
  "etf-outperformance-analysis": {
    id: "etf-outperformance-analysis",
    name: "ETF Outperformance vs SPY & QQQ",
    file: "experimental/ETFOutperformanceAnalysis.json"
  },
  "watchlist-risk-adjusted-returns": {
    id: "watchlist-risk-adjusted-returns",
    name: "Watchlist Risk-Adjusted Returns",
    file: "experimental/WatchlistRiskAdjustedReturns.json",
    Component: require('./WatchlistRiskAdjustedReturns').default
  },
  "position-corr-top2": {
    id: "position-corr-top2",
    name: "Top Positions Correlation",
    file: "experimental/PositionCorrelation.json",
    Component: require('./PositionCorrelation').default
  },
  "trading-performance-dashboard": {
    id: "trading-performance-dashboard", 
    name: "Trading Performance Dashboard",
    file: "experimental/TradingPerformanceDashboard.json",
    Component: require('./TradingPerformanceDashboard').default
  },
  "total-unrealized-pnl": {
    id: "total-unrealized-pnl",
    name: "Total Unrealized P&L",
    file: "experimental/TotalUnrealizedPnL.json",
    Component: require('./TotalUnrealizedPnL').default
  },
  "position-highest-volatility-30d": {
    id: "position-highest-volatility-30d",
    name: "Highest 30D Volatility (Open Positions)",
    file: "experimental/OpenPositionsVolatilityTop.json",
    Component: require('./OpenPositionsVolatilityTop').default
  },
  "account-buying-power": {
    id: "account-buying-power",
    name: "Current Buying Power",
    file: "experimental/BuyingPower.json",
    Component: require('./BuyingPower').default
  },
  "holdings-downside-correlation": {
    id: "holdings-downside-correlation",
    name: "Holdings Downside Correlation with SPY",
    file: "experimental/HoldingsDownsideCorrelation.json"
  },
  "gap-down-recovery-analysis": {
    id: "gap-down-recovery-analysis",
    name: "Gap-Down Recovery Analysis",
    file: "experimental/GapDownRecoveryAnalysis.json"
  },
  "sector-etf-relative-strength": {
    id: "sector-etf-relative-strength",
    name: "Sector ETF Relative Strength Analysis",
    file: "experimental/SectorETFRelativeStrength.json"
  },
  "positions-weekly-range-tightness": {
    id: "positions-weekly-range-tightness",
    name: "Positions with Tightest Weekly Ranges (Quarterly)",
    file: "experimental/PositionsWeeklyRangeTightness.json"
  },
  "failed-breakdown-analysis": {
    id: "failed-breakdown-analysis",
    name: "Failed Breakdown Analysis (60-Day)",
    file: "experimental/FailedBreakdownAnalysis.json"
  },
  "position-trend-analysis-200day": {
    id: "position-trend-analysis-200day",
    name: "Position 200-Day Trend Analysis",
    file: "experimental/PositionTrendAnalysis200Day.json"
  },
  "etf-volatility-analysis": {
    id: "etf-volatility-analysis",
    name: "ETF Volatility Analysis (30-Day)",
    file: "experimental/ETFVolatilityAnalysis.json"
  },
  "position-skewness-analysis": {
    id: "position-skewness-analysis",
    name: "Position Rolling Skewness Analysis",
    file: "experimental/PositionSkewnessAnalysis.json"
  },
  "position-rolling-skew": {
    id: "position-rolling-skew",
    name: "Position Rolling Skew Analysis",
    file: "experimental/PositionRollingSkew.json"
  },
  "position-200day-trend-steepness": {
    id: "position-200day-trend-steepness",
    name: "Position 200-Day Trend Steepness",
    file: "experimental/Position200DayTrendSteepness.json"
  },
  "etf-monthly-volatility-ranking": {
    id: "etf-monthly-volatility-ranking",
    name: "ETF Monthly Volatility Ranking",
    file: "experimental/ETFMonthlyVolatilityRanking.json"
  },
  "positions-cpi-performance": {
    id: "positions-cpi-performance",
    name: "Position CPI Release Day Performance",
    file: "experimental/PositionsCPIPerformance.json"
  },
  "monday-performance-analysis": {
    id: "monday-performance-analysis",
    name: "Monday Performance Analysis",
    file: "experimental/MondayPerformanceAnalysis.json"
  },
  "tesla-sma-crossover-strategy": {
    id: "tesla-sma-crossover-strategy",
    name: "Tesla SMA Crossover Strategy Analysis",
    file: "experimental/TeslaSMACrossoverStrategy.json"
  },
  "tesla-five-technical-strategies": {
    id: "tesla-five-technical-strategies",
    name: "Tesla Five Technical Strategies Comparison",
    file: "experimental/TeslaFiveTechnicalStrategies.json"
  },
  "aapl-vs-nvda-decision": {
    id: "aapl-vs-nvda-decision",
    name: "AAPL vs NVDA Investment Decision Analysis",
    file: "experimental/AAPLvsNVDADecision.json"
  },
  "bullish-engulfing-today": {
    id: "bullish-engulfing-today",
    name: "Bullish Engulfing Patterns Today",
    file: "experimental/BullishEngulfingToday.json"
  },
  "position-fair-value-gaps": {
    id: "position-fair-value-gaps",
    name: "Position Fair Value Gap Analysis",
    file: "experimental/PositionFairValueGaps.json"
  }
};

export default registryMap;
