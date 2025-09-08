import React from 'react';
import BarChart from './BarChart';
import StatsCard from './StatsCard';
import AccountOverview from './AccountOverview';
import ForexRatesCard from './ForexRatesCard';
import NewsList from './NewsList';
import SectorRiskExposure from './SectorRiskExposure';
import StockVolatilityScreener from './StockVolatilityScreener';
import TradingPerformanceDashboard from './TradingPerformanceDashboard';

export type VisualDef = {
  id: string;
  name: string;
  description?: string;
  file: string; // relative file path for persistence/display
  Component: React.ComponentType<any>;
};

export const registry: VisualDef[] = [
  {
    id: 'news-aapl',
    name: 'News: AAPL (24h)',
    description: 'Latest news headlines for AAPL in the last 24h.',
    file: 'experimental/NewsList.tsx',
    Component: NewsList,
  },
  {
    id: 'forex-usdjpy',
    name: 'Forex USD/JPY',
    description: 'Latest and recent mid prices for USD/JPY.',
    file: 'experimental/ForexRatesCard.tsx',
    Component: ForexRatesCard,
  },
  {
    id: 'account-overview',
    name: 'Account Overview',
    description: 'Buying power, cash, and top positions from Trading API.',
    file: 'experimental/AccountOverview.tsx',
    Component: AccountOverview,
  },
  {
    id: 'bar-chart',
    name: 'Bar Chart',
    description: 'Simple sample bar chart visualization.',
    file: 'experimental/BarChart.tsx',
    Component: BarChart,
  },
  {
    id: 'stats-card',
    name: 'Stats Card',
    description: 'Summary metric cards with trends.',
    file: 'experimental/StatsCard.tsx',
    Component: StatsCard,
  },
  {
    id: 'sector-risk-exposure',
    name: 'Sector Risk Exposure',
    description: 'Portfolio diversification and risk analysis by sector.',
    file: 'experimental/SectorRiskExposure.tsx',
    Component: SectorRiskExposure,
  },
  {
    id: 'stock-volatility-screener',
    name: 'Stock Volatility Screener',
    description: 'Identify stocks with highest price volatility over 30-day period.',
    file: 'experimental/StockVolatilityScreener.tsx',
    Component: StockVolatilityScreener,
  },
  {
    id: 'trading-performance-dashboard',
    name: 'Trading Performance Dashboard',
    description: 'Comprehensive view of trading performance and account activity over past 30 days.',
    file: 'experimental/TradingPerformanceDashboard.tsx',
    Component: TradingPerformanceDashboard,
  },
];

export const registryMap: Record<string, VisualDef> = Object.fromEntries(
  registry.map((d) => [d.id, d])
);
