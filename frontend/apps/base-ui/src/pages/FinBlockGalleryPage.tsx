/**
 * FinBlock Gallery Page
 * Showcases all 110 finBlocks with filtering, search, and interactive preview
 */

import React, { useState, useMemo } from 'react';

// Import all finBlocks organized by category
import {
  PortfolioKpiSummary,
  HoldingsTable,
  SectorAllocationDonut,
  AssetClassAllocation,
  PortfolioPerformanceVsBenchmark,
  PriceMovementsSpark,
  TopBottomPerformers,
  MonthlyReturnsBar,
  ConcentrationByHolding,
  PortfolioTurnoverTable,
  DividendSummaryKpi,
  PortfolioRiskSummary,
} from '../finBlocks/components/portfolio';

import {
  StockPriceKpi,
  PriceHistoryWithMa,
  FundamentalMetricsList,
  EarningsHistoryTable,
  AnalystRatingsBar,
  DividendHistoryLine,
  ValuationComparison,
  InsiderTransactionsTable,
  TechnicalIndicatorsKpi,
  VolumeTrendBar,
  GrowthMetricsComparison,
} from '../finBlocks/components/stock_research';

import {
  EtfComparisonMetrics,
  EtfPerformanceLine,
  EtfSectorAllocation,
  EtfTopHoldings,
  EtfRiskMetrics,
  EtfDividendYieldTrend,
  EtfOverlapAnalysis,
  EtfExpenseRatioImpact,
  EtfGeographicExposure,
  EtfTaxEfficiency,
} from '../finBlocks/components/etf_analysis';

import {
  RiskMetricsKpi,
  VolatilityByHolding,
  ConcentrationRisk,
  CorrelationMatrix,
  DrawdownHistory,
  VarByScenario,
  BetaAnalysis,
  DownsideRiskAnalysis,
  SectorRiskExposure,
  StressTestResults,
  RiskLimitsMonitoring,
} from '../finBlocks/components/risk_management';

import {
  AnnualReturnsBar,
  ReturnDistribution,
  WinRateMetrics,
  RiskAdjustedReturns,
  AttributionAnalysis,
  UpsideDownsideCapture,
  RollingReturns,
  BestWorstPeriods,
  AlphaGeneration,
  ReturnsVsGoals,
  TimeWeightedReturns,
} from '../finBlocks/components/performance';

import {
  DividendIncomeKpi,
  DividendPayersTable,
  MonthlyDividendTrend,
  TopDividendYielders,
  DividendGrowthAnalysis,
  SectorDividendYield,
  DividendCoverageRatio,
  IncomeVsExpenses,
  DistributionCalendar,
} from '../finBlocks/components/income';

import {
  SectorPerformanceBar,
  SectorHoldingsTable,
  SectorVolatilityComparison,
  SectorValuationMetrics,
  SectorRotationSignals,
  SectorCorrelation,
  EconomicCyclePositioning,
  SectorRebalancingRecommendation,
  SectorDividendComposition,
} from '../finBlocks/components/sector';

import {
  RsiOverboughtOversold,
  MacdCrossoverSignals,
  MovingAverageCrossover,
  BollingerBandSqueeze,
  SupportResistanceLevels,
  VolumeTrendTechnical,
  PatternRecognition,
  TrendStrengthIndicator,
} from '../finBlocks/components/technical';

import {
  EarningsPerShare,
  PriceToEarningsRatio,
  DebtToEquityRatio,
  FreeCashFlowTrend,
  RoeProfitMargin,
  DividendPayoutRatio,
  AssetQualityScore,
  RevenueGrowthAnalysis,
} from '../finBlocks/components/fundamental';

import {
  TaxLossHarvestingOpportunities,
  CapitalGainsSummary,
  TaxLiabilityProjection,
  TaxAverageVsCost,
  TaxEfficiencyRatio,
  StateLocalTaxExposure,
  HarvestingCalendar,
  TaxRiskAssessment,
} from '../finBlocks/components/tax';

import {
  PriceAlertsSummary,
  EarningsCalendar,
  NewsHeadlinesWidget,
  RatingsConsensus,
  MarketMoversList,
  EconomicCalendar,
  PortfolioHealthScore,
  ComplianceMonitoring,
  RegulatoryUpdates,
  SecurityAnalysis,
} from '../finBlocks/components/monitoring';

interface FinBlockItem {
  id: string;
  name: string;
  category: string;
  component: React.FC<any>;
  description: string;
}

const FINBLOCKS: FinBlockItem[] = [
  // Portfolio
  { id: 'portfolio-kpi-summary', name: 'Portfolio KPI Summary', category: 'portfolio', component: PortfolioKpiSummary, description: 'Overview of key portfolio metrics' },
  { id: 'holdings-table', name: 'Holdings Table', category: 'portfolio', component: HoldingsTable, description: 'Detailed holdings breakdown' },
  { id: 'sector-allocation-donut', name: 'Sector Allocation', category: 'portfolio', component: SectorAllocationDonut, description: 'Sector distribution visualization' },
  { id: 'asset-class-allocation', name: 'Asset Class Allocation', category: 'portfolio', component: AssetClassAllocation, description: 'Asset class breakdown' },
  { id: 'portfolio-performance-vs-benchmark', name: 'Performance vs Benchmark', category: 'portfolio', component: PortfolioPerformanceVsBenchmark, description: 'Returns comparison' },
  { id: 'price-movements-spark', name: 'Price Movements', category: 'portfolio', component: PriceMovementsSpark, description: 'Sparkline price trends' },
  { id: 'top-bottom-performers', name: 'Top/Bottom Performers', category: 'portfolio', component: TopBottomPerformers, description: 'Best and worst performers' },
  { id: 'monthly-returns-bar', name: 'Monthly Returns', category: 'portfolio', component: MonthlyReturnsBar, description: 'Monthly return distribution' },
  { id: 'concentration-by-holding', name: 'Concentration Analysis', category: 'portfolio', component: ConcentrationByHolding, description: 'Position concentration risk' },
  { id: 'portfolio-turnover-table', name: 'Portfolio Turnover', category: 'portfolio', component: PortfolioTurnoverTable, description: 'Trading activity analysis' },
  { id: 'dividend-summary-kpi', name: 'Dividend Summary', category: 'portfolio', component: DividendSummaryKpi, description: 'Dividend income overview' },
  { id: 'portfolio-risk-summary', name: 'Portfolio Risk Summary', category: 'portfolio', component: PortfolioRiskSummary, description: 'Risk metrics overview' },

  // Stock Research
  { id: 'stock-price-kpi', name: 'Stock Price KPI', category: 'stock_research', component: StockPriceKpi, description: 'Current price and change' },
  { id: 'price-history-with-ma', name: 'Price History with MA', category: 'stock_research', component: PriceHistoryWithMa, description: 'Historical price with moving averages' },
  { id: 'fundamental-metrics-list', name: 'Fundamental Metrics', category: 'stock_research', component: FundamentalMetricsList, description: 'Key fundamental ratios' },
  { id: 'earnings-history-table', name: 'Earnings History', category: 'stock_research', component: EarningsHistoryTable, description: 'Historical earnings data' },
  { id: 'analyst-ratings-bar', name: 'Analyst Ratings', category: 'stock_research', component: AnalystRatingsBar, description: 'Analyst consensus' },
  { id: 'dividend-history-line', name: 'Dividend History', category: 'stock_research', component: DividendHistoryLine, description: 'Historical dividend trends' },
  { id: 'valuation-comparison', name: 'Valuation Comparison', category: 'stock_research', component: ValuationComparison, description: 'Valuation vs peers' },
  { id: 'insider-transactions-table', name: 'Insider Transactions', category: 'stock_research', component: InsiderTransactionsTable, description: 'Insider trading activity' },
  { id: 'technical-indicators-kpi', name: 'Technical Indicators', category: 'stock_research', component: TechnicalIndicatorsKpi, description: 'Technical analysis metrics' },
  { id: 'volume-trend-bar', name: 'Volume Trend', category: 'stock_research', component: VolumeTrendBar, description: 'Trading volume analysis' },
  { id: 'growth-metrics-comparison', name: 'Growth Metrics', category: 'stock_research', component: GrowthMetricsComparison, description: 'Growth rates comparison' },

  // ETF Analysis
  { id: 'etf-comparison-metrics', name: 'ETF Comparison', category: 'etf_analysis', component: EtfComparisonMetrics, description: 'ETF comparison metrics' },
  { id: 'etf-performance-line', name: 'ETF Performance', category: 'etf_analysis', component: EtfPerformanceLine, description: 'ETF return trends' },
  { id: 'etf-sector-allocation', name: 'ETF Sector Allocation', category: 'etf_analysis', component: EtfSectorAllocation, description: 'Sector distribution' },
  { id: 'etf-top-holdings', name: 'ETF Top Holdings', category: 'etf_analysis', component: EtfTopHoldings, description: 'Top holdings list' },
  { id: 'etf-risk-metrics', name: 'ETF Risk Metrics', category: 'etf_analysis', component: EtfRiskMetrics, description: 'Risk analysis' },
  { id: 'etf-dividend-yield-trend', name: 'ETF Dividend Yield Trend', category: 'etf_analysis', component: EtfDividendYieldTrend, description: 'Dividend yield analysis' },
  { id: 'etf-overlap-analysis', name: 'ETF Overlap Analysis', category: 'etf_analysis', component: EtfOverlapAnalysis, description: 'Portfolio overlap detection' },
  { id: 'etf-expense-ratio-impact', name: 'ETF Expense Impact', category: 'etf_analysis', component: EtfExpenseRatioImpact, description: 'Fee impact analysis' },
  { id: 'etf-geographic-exposure', name: 'ETF Geographic Exposure', category: 'etf_analysis', component: EtfGeographicExposure, description: 'Geographic diversification' },
  { id: 'etf-tax-efficiency', name: 'ETF Tax Efficiency', category: 'etf_analysis', component: EtfTaxEfficiency, description: 'Tax efficiency metrics' },

  // Risk Management
  { id: 'risk-metrics-kpi', name: 'Risk Metrics KPI', category: 'risk_management', component: RiskMetricsKpi, description: 'Key risk metrics' },
  { id: 'volatility-by-holding', name: 'Volatility by Holding', category: 'risk_management', component: VolatilityByHolding, description: 'Volatility breakdown' },
  { id: 'concentration-risk', name: 'Concentration Risk', category: 'risk_management', component: ConcentrationRisk, description: 'Concentration analysis' },
  { id: 'correlation-matrix', name: 'Correlation Matrix', category: 'risk_management', component: CorrelationMatrix, description: 'Asset correlations' },
  { id: 'drawdown-history', name: 'Drawdown History', category: 'risk_management', component: DrawdownHistory, description: 'Drawdown visualization' },
  { id: 'var-by-scenario', name: 'VaR by Scenario', category: 'risk_management', component: VarByScenario, description: 'Value at risk scenarios' },
  { id: 'beta-analysis', name: 'Beta Analysis', category: 'risk_management', component: BetaAnalysis, description: 'Systematic risk analysis' },
  { id: 'downside-risk-analysis', name: 'Downside Risk Analysis', category: 'risk_management', component: DownsideRiskAnalysis, description: 'Downside risk metrics' },
  { id: 'sector-risk-exposure', name: 'Sector Risk Exposure', category: 'risk_management', component: SectorRiskExposure, description: 'Sector risk breakdown' },
  { id: 'stress-test-results', name: 'Stress Test Results', category: 'risk_management', component: StressTestResults, description: 'Stress test scenarios' },
  { id: 'risk-limits-monitoring', name: 'Risk Limits Monitoring', category: 'risk_management', component: RiskLimitsMonitoring, description: 'Risk limit tracking' },

  // Performance
  { id: 'annual-returns-bar', name: 'Annual Returns', category: 'performance', component: AnnualReturnsBar, description: 'Yearly return breakdown' },
  { id: 'return-distribution', name: 'Return Distribution', category: 'performance', component: ReturnDistribution, description: 'Return distribution analysis' },
  { id: 'win-rate-metrics', name: 'Win Rate Metrics', category: 'performance', component: WinRateMetrics, description: 'Win rate statistics' },
  { id: 'risk-adjusted-returns', name: 'Risk-Adjusted Returns', category: 'performance', component: RiskAdjustedReturns, description: 'Sharpe, Sortino, Calmar' },
  { id: 'attribution-analysis', name: 'Attribution Analysis', category: 'performance', component: AttributionAnalysis, description: 'Return attribution' },
  { id: 'upside-downside-capture', name: 'Upside/Downside Capture', category: 'performance', component: UpsideDownsideCapture, description: 'Capture ratios' },
  { id: 'rolling-returns', name: 'Rolling Returns', category: 'performance', component: RollingReturns, description: 'Rolling return analysis' },
  { id: 'best-worst-periods', name: 'Best/Worst Periods', category: 'performance', component: BestWorstPeriods, description: 'Performance extremes' },
  { id: 'alpha-generation', name: 'Alpha Generation', category: 'performance', component: AlphaGeneration, description: 'Excess return analysis' },
  { id: 'returns-vs-goals', name: 'Returns vs Goals', category: 'performance', component: ReturnsVsGoals, description: 'Goal tracking' },
  { id: 'time-weighted-returns', name: 'Time-Weighted Returns', category: 'performance', component: TimeWeightedReturns, description: 'TWR calculation' },

  // Income
  { id: 'dividend-income-kpi', name: 'Dividend Income KPI', category: 'income', component: DividendIncomeKpi, description: 'Income overview' },
  { id: 'dividend-payers-table', name: 'Dividend Payers', category: 'income', component: DividendPayersTable, description: 'Dividend payers list' },
  { id: 'monthly-dividend-trend', name: 'Monthly Dividend Trend', category: 'income', component: MonthlyDividendTrend, description: 'Income trend over time' },
  { id: 'top-dividend-yielders', name: 'Top Dividend Yielders', category: 'income', component: TopDividendYielders, description: 'Highest yield holdings' },
  { id: 'dividend-growth-analysis', name: 'Dividend Growth Analysis', category: 'income', component: DividendGrowthAnalysis, description: 'Growth rate analysis' },
  { id: 'sector-dividend-yield', name: 'Sector Dividend Yield', category: 'income', component: SectorDividendYield, description: 'Sector yield breakdown' },
  { id: 'dividend-coverage-ratio', name: 'Dividend Coverage Ratio', category: 'income', component: DividendCoverageRatio, description: 'Coverage analysis' },
  { id: 'income-vs-expenses', name: 'Income vs Expenses', category: 'income', component: IncomeVsExpenses, description: 'Income vs fees' },
  { id: 'distribution-calendar', name: 'Distribution Calendar', category: 'income', component: DistributionCalendar, description: 'Upcoming distributions' },

  // Sector
  { id: 'sector-performance-bar', name: 'Sector Performance', category: 'sector', component: SectorPerformanceBar, description: 'Sector returns' },
  { id: 'sector-holdings-table', name: 'Sector Holdings', category: 'sector', component: SectorHoldingsTable, description: 'Holdings by sector' },
  { id: 'sector-volatility-comparison', name: 'Sector Volatility', category: 'sector', component: SectorVolatilityComparison, description: 'Volatility by sector' },
  { id: 'sector-valuation-metrics', name: 'Sector Valuation', category: 'sector', component: SectorValuationMetrics, description: 'Valuation by sector' },
  { id: 'sector-rotation-signals', name: 'Sector Rotation Signals', category: 'sector', component: SectorRotationSignals, description: 'Rotation analysis' },
  { id: 'sector-correlation', name: 'Sector Correlation', category: 'sector', component: SectorCorrelation, description: 'Correlation matrix' },
  { id: 'economic-cycle-positioning', name: 'Economic Cycle Positioning', category: 'sector', component: EconomicCyclePositioning, description: 'Cycle analysis' },
  { id: 'sector-rebalancing-recommendation', name: 'Rebalancing Recommendation', category: 'sector', component: SectorRebalancingRecommendation, description: 'Rebalance advice' },
  { id: 'sector-dividend-composition', name: 'Sector Dividend Composition', category: 'sector', component: SectorDividendComposition, description: 'Dividend breakdown' },

  // Technical
  { id: 'rsi-overbought-oversold', name: 'RSI Overbought/Oversold', category: 'technical', component: RsiOverboughtOversold, description: 'RSI levels' },
  { id: 'macd-crossover-signals', name: 'MACD Crossover Signals', category: 'technical', component: MacdCrossoverSignals, description: 'MACD signals' },
  { id: 'moving-average-crossover', name: 'Moving Average Crossover', category: 'technical', component: MovingAverageCrossover, description: 'MA crossover' },
  { id: 'bollinger-band-squeeze', name: 'Bollinger Band Squeeze', category: 'technical', component: BollingerBandSqueeze, description: 'BB analysis' },
  { id: 'support-resistance-levels', name: 'Support/Resistance Levels', category: 'technical', component: SupportResistanceLevels, description: 'Price levels' },
  { id: 'volume-trend-technical', name: 'Volume Trend', category: 'technical', component: VolumeTrendTechnical, description: 'Volume analysis' },
  { id: 'pattern-recognition', name: 'Pattern Recognition', category: 'technical', component: PatternRecognition, description: 'Chart patterns' },
  { id: 'trend-strength-indicator', name: 'Trend Strength Indicator', category: 'technical', component: TrendStrengthIndicator, description: 'Trend analysis' },

  // Fundamental
  { id: 'earnings-per-share', name: 'Earnings Per Share', category: 'fundamental', component: EarningsPerShare, description: 'EPS analysis' },
  { id: 'price-to-earnings-ratio', name: 'Price to Earnings Ratio', category: 'fundamental', component: PriceToEarningsRatio, description: 'P/E ratio' },
  { id: 'debt-to-equity-ratio', name: 'Debt to Equity Ratio', category: 'fundamental', component: DebtToEquityRatio, description: 'Leverage analysis' },
  { id: 'free-cash-flow-trend', name: 'Free Cash Flow Trend', category: 'fundamental', component: FreeCashFlowTrend, description: 'FCF analysis' },
  { id: 'roe-profit-margin', name: 'ROE & Profit Margin', category: 'fundamental', component: RoeProfitMargin, description: 'Profitability metrics' },
  { id: 'dividend-payout-ratio', name: 'Dividend Payout Ratio', category: 'fundamental', component: DividendPayoutRatio, description: 'Payout analysis' },
  { id: 'asset-quality-score', name: 'Asset Quality Score', category: 'fundamental', component: AssetQualityScore, description: 'Balance sheet quality' },
  { id: 'revenue-growth-analysis', name: 'Revenue Growth Analysis', category: 'fundamental', component: RevenueGrowthAnalysis, description: 'Growth trends' },

  // Tax
  { id: 'tax-loss-harvesting-opportunities', name: 'Tax Loss Harvesting', category: 'tax', component: TaxLossHarvestingOpportunities, description: 'Harvesting opportunities' },
  { id: 'capital-gains-summary', name: 'Capital Gains Summary', category: 'tax', component: CapitalGainsSummary, description: 'Gains/losses breakdown' },
  { id: 'tax-liability-projection', name: 'Tax Liability Projection', category: 'tax', component: TaxLiabilityProjection, description: 'Projected tax bill' },
  { id: 'tax-average-vs-cost', name: 'Tax Average vs Cost', category: 'tax', component: TaxAverageVsCost, description: 'Cost basis analysis' },
  { id: 'tax-efficiency-ratio', name: 'Tax Efficiency Ratio', category: 'tax', component: TaxEfficiencyRatio, description: 'Efficiency metrics' },
  { id: 'state-local-tax-exposure', name: 'State/Local Tax Exposure', category: 'tax', component: StateLocalTaxExposure, description: 'State tax analysis' },
  { id: 'harvesting-calendar', name: 'Harvesting Calendar', category: 'tax', component: HarvestingCalendar, description: 'Calendar view' },
  { id: 'tax-risk-assessment', name: 'Tax Risk Assessment', category: 'tax', component: TaxRiskAssessment, description: 'Risk analysis' },

  // Monitoring
  { id: 'price-alerts-summary', name: 'Price Alerts Summary', category: 'monitoring', component: PriceAlertsSummary, description: 'Active alerts' },
  { id: 'earnings-calendar', name: 'Earnings Calendar', category: 'monitoring', component: EarningsCalendar, description: 'Upcoming earnings' },
  { id: 'news-headlines-widget', name: 'News Headlines', category: 'monitoring', component: NewsHeadlinesWidget, description: 'Latest news' },
  { id: 'ratings-consensus', name: 'Ratings Consensus', category: 'monitoring', component: RatingsConsensus, description: 'Analyst ratings' },
  { id: 'market-movers-list', name: 'Market Movers', category: 'monitoring', component: MarketMoversList, description: 'Top movers' },
  { id: 'economic-calendar', name: 'Economic Calendar', category: 'monitoring', component: EconomicCalendar, description: 'Macro events' },
  { id: 'portfolio-health-score', name: 'Portfolio Health Score', category: 'monitoring', component: PortfolioHealthScore, description: 'Health assessment' },
  { id: 'compliance-monitoring', name: 'Compliance Monitoring', category: 'monitoring', component: ComplianceMonitoring, description: 'Compliance status' },
  { id: 'regulatory-updates', name: 'Regulatory Updates', category: 'monitoring', component: RegulatoryUpdates, description: 'Regulatory news' },
  { id: 'security-analysis', name: 'Security Analysis', category: 'monitoring', component: SecurityAnalysis, description: 'Security overview' },
];

const CATEGORIES = ['All', 'portfolio', 'stock_research', 'etf_analysis', 'risk_management', 'performance', 'income', 'sector', 'technical', 'fundamental', 'tax', 'monitoring'];

export const FinBlockGalleryPage: React.FC = () => {
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedBlock, setSelectedBlock] = useState<FinBlockItem | null>(FINBLOCKS[0]);

  const filtered = useMemo(() => {
    return FINBLOCKS.filter((block) => {
      const matchCategory = selectedCategory === 'All' || block.category === selectedCategory;
      const matchSearch = block.name.toLowerCase().includes(searchQuery.toLowerCase()) || block.description.toLowerCase().includes(searchQuery.toLowerCase());
      return matchCategory && matchSearch;
    });
  }, [selectedCategory, searchQuery]);

  const categories = CATEGORIES.map((cat) => {
    const count = FINBLOCKS.filter((b) => cat === 'All' || b.category === cat).length;
    return { name: cat, count };
  });

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800">
      {/* Header */}
      <div className="sticky top-0 z-40 bg-white dark:bg-slate-800 border-b border-slate-200 dark:border-slate-700 shadow-sm">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">finBlock Gallery</h1>
          <p className="text-gray-600 dark:text-gray-300 mb-4">Browse and preview all 110 financial UI components</p>

          {/* Search */}
          <div className="mb-4">
            <input
              type="text"
              placeholder="Search finBlocks..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full px-4 py-2 bg-slate-50 dark:bg-slate-700 border border-slate-200 dark:border-slate-600 rounded-lg text-gray-900 dark:text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          {/* Category Tabs */}
          <div className="flex flex-wrap gap-2 overflow-x-auto pb-2">
            {categories.map((cat) => (
              <button
                key={cat.name}
                onClick={() => setSelectedCategory(cat.name)}
                className={`px-4 py-2 rounded-full whitespace-nowrap font-medium transition ${
                  selectedCategory === cat.name
                    ? 'bg-blue-500 text-white'
                    : 'bg-slate-200 dark:bg-slate-700 text-gray-700 dark:text-gray-300 hover:bg-slate-300 dark:hover:bg-slate-600'
                }`}
              >
                {cat.name === 'All' ? 'All' : cat.name.replace(/_/g, ' ')} ({cat.count})
              </button>
            ))}
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Sidebar - List */}
          <div className="lg:col-span-1">
            <div className="bg-white dark:bg-slate-800 rounded-lg shadow p-4 max-h-[600px] overflow-y-auto sticky top-24">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                Components ({filtered.length})
              </h2>
              <div className="space-y-2">
                {filtered.map((block) => (
                  <button
                    key={block.id}
                    onClick={() => setSelectedBlock(block)}
                    className={`w-full text-left px-3 py-2 rounded transition text-sm ${
                      selectedBlock?.id === block.id
                        ? 'bg-blue-100 dark:bg-blue-900 text-blue-900 dark:text-blue-100 font-medium'
                        : 'text-gray-700 dark:text-gray-300 hover:bg-slate-100 dark:hover:bg-slate-700'
                    }`}
                  >
                    <div className="font-medium">{block.name}</div>
                    <div className="text-xs text-gray-500 dark:text-gray-400">{block.category}</div>
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Main - Preview */}
          <div className="lg:col-span-3">
            {selectedBlock ? (
              <div className="bg-white dark:bg-slate-800 rounded-lg shadow-lg p-8">
                {/* Header */}
                <div className="mb-6 border-b border-slate-200 dark:border-slate-700 pb-6">
                  <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">{selectedBlock.name}</h2>
                  <p className="text-gray-600 dark:text-gray-300 mb-4">{selectedBlock.description}</p>
                  <div className="flex flex-wrap gap-2">
                    <span className="px-3 py-1 bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-100 rounded-full text-sm font-medium">
                      {selectedBlock.category.replace(/_/g, ' ')}
                    </span>
                    <span className="px-3 py-1 bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200 rounded-full text-sm font-mono">
                      {selectedBlock.id}
                    </span>
                  </div>
                </div>

                {/* Preview */}
                <div className="bg-slate-50 dark:bg-slate-900 rounded-lg p-6 border border-slate-200 dark:border-slate-700 overflow-x-auto">
                  <selectedBlock.component />
                </div>

                {/* Info */}
                <div className="mt-6 text-sm text-gray-600 dark:text-gray-400">
                  <p>📍 Location: <code className="text-xs bg-slate-100 dark:bg-slate-700 px-2 py-1 rounded">finBlocks/components/{selectedBlock.category}/{selectedBlock.id}.tsx</code></p>
                </div>
              </div>
            ) : (
              <div className="bg-white dark:bg-slate-800 rounded-lg shadow-lg p-8 text-center">
                <p className="text-gray-600 dark:text-gray-300">Select a component to preview</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default FinBlockGalleryPage;
