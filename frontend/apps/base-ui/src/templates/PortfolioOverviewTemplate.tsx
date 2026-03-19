/**
 * Portfolio Overview Template - Hydrated Example
 * Shows: Holdings table, KPI summary, sector allocation, recent price movements
 */

import React from 'react';
import { KpiCard01 } from '../blocks/kpi-cards';
import { Table01 } from '../blocks/tables';
import { DonutChart01 } from '../blocks/donut-charts';
import { SparkChart01 } from '../blocks/spark-charts';

export interface PortfolioOverviewData {
  holdings: {
    rows: Array<{
      Symbol: string;
      Shares: number;
      'Avg Cost': number;
      'Market Value': number;
      'P&L': number;
      'P&L %': number;
    }>;
    columns: string[];
  };
  kpiMetrics: {
    metrics: Array<{
      name: string;
      stat: number;
      change: string;
      changeType: 'positive' | 'negative' | 'neutral';
    }>;
    cols: number;
  };
  sectorAllocation: {
    data: Array<{
      name: string;
      value: number;
    }>;
  };
  priceMovements: {
    data: Array<{
      date: string;
      [key: string]: any;
    }>;
    items: Array<{
      id: string;
      name: string;
      dataKey: string;
      value: string;
      change: string;
      changeType: 'positive' | 'negative' | 'neutral';
    }>;
  };
}

const SAMPLE_DATA: PortfolioOverviewData = {
  holdings: {
    rows: [
      { Symbol: 'AAPL', Shares: 150, 'Avg Cost': 145.50, 'Market Value': 27225, 'P&L': 1224.50, 'P&L %': 4.7 },
      { Symbol: 'MSFT', Shares: 75, 'Avg Cost': 380, 'Market Value': 31500, 'P&L': 375, 'P&L %': 1.2 },
      { Symbol: 'GOOGL', Shares: 40, 'Avg Cost': 140.25, 'Market Value': 6280, 'P&L': 158.75, 'P&L %': 2.6 },
      { Symbol: 'NVDA', Shares: 50, 'Avg Cost': 520, 'Market Value': 28000, 'P&L': -1000, 'P&L %': -3.4 },
      { Symbol: 'TSLA', Shares: 100, 'Avg Cost': 250, 'Market Value': 27500, 'P&L': 2500, 'P&L %': 10.0 },
    ],
    columns: ['Symbol', 'Shares', 'Avg Cost', 'Market Value', 'P&L', 'P&L %'],
  },
  kpiMetrics: {
    metrics: [
      { name: 'Total Value', stat: 120505, change: '+2.3%', changeType: 'positive' },
      { name: 'Total P&L', stat: 3258.25, change: '+2.8%', changeType: 'positive' },
      { name: '1Y Return', stat: 12.4, change: '+5.6%', changeType: 'positive' },
      { name: 'Sharpe Ratio', stat: 1.85, change: '+0.3', changeType: 'positive' },
    ],
    cols: 4,
  },
  sectorAllocation: {
    data: [
      { name: 'Technology', value: 68.5 },
      { name: 'Healthcare', value: 12.3 },
      { name: 'Finance', value: 10.2 },
      { name: 'Consumer', value: 9.0 },
    ],
  },
  priceMovements: {
    data: [
      { date: '2026-03-05', AAPL: 178.25, MSFT: 415.50, GOOGL: 155.75, NVDA: 560.25, TSLA: 267.50 },
      { date: '2026-03-06', AAPL: 179.10, MSFT: 416.25, GOOGL: 156.50, NVDA: 558.75, TSLA: 268.25 },
      { date: '2026-03-07', AAPL: 177.50, MSFT: 414.75, GOOGL: 155.25, NVDA: 555.50, TSLA: 265.75 },
      { date: '2026-03-10', AAPL: 181.50, MSFT: 420.00, GOOGL: 157.00, NVDA: 560.00, TSLA: 275.00 },
      { date: '2026-03-11', AAPL: 182.25, MSFT: 421.50, GOOGL: 157.50, NVDA: 563.50, TSLA: 276.25 },
      { date: '2026-03-12', AAPL: 181.75, MSFT: 420.75, GOOGL: 157.25, NVDA: 562.00, TSLA: 275.75 },
      { date: '2026-03-13', AAPL: 183.00, MSFT: 423.00, GOOGL: 158.25, NVDA: 565.25, TSLA: 277.50 },
      { date: '2026-03-14', AAPL: 184.50, MSFT: 425.00, GOOGL: 159.00, NVDA: 568.00, TSLA: 279.00 },
      { date: '2026-03-17', AAPL: 185.25, MSFT: 426.50, GOOGL: 159.75, NVDA: 570.50, TSLA: 280.50 },
      { date: '2026-03-18', AAPL: 186.00, MSFT: 427.25, GOOGL: 160.25, NVDA: 572.25, TSLA: 281.75 },
      { date: '2026-03-19', AAPL: 181.50, MSFT: 420.00, GOOGL: 157.00, NVDA: 560.00, TSLA: 275.00 },
    ],
    items: [
      { id: 'AAPL', name: 'Apple Inc', dataKey: 'AAPL', value: '$181.50', change: '+2.8%', changeType: 'positive' },
      { id: 'MSFT', name: 'Microsoft', dataKey: 'MSFT', value: '$420.00', change: '+1.2%', changeType: 'positive' },
      { id: 'GOOGL', name: 'Alphabet', dataKey: 'GOOGL', value: '$157.00', change: '+2.6%', changeType: 'positive' },
      { id: 'NVDA', name: 'NVIDIA', dataKey: 'NVDA', value: '$560.00', change: '-3.4%', changeType: 'negative' },
      { id: 'TSLA', name: 'Tesla', dataKey: 'TSLA', value: '$275.00', change: '+10.0%', changeType: 'positive' },
    ],
  },
};

export const PortfolioOverviewTemplate: React.FC<{ data?: PortfolioOverviewData }> = ({
  data = SAMPLE_DATA,
}) => {
  return (
    <div className="space-y-6">
      {/* KPI Summary */}
      <div>
        <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-50 mb-4">Portfolio Overview</h2>
        <KpiCard01 metrics={data.kpiMetrics.metrics} cols={data.kpiMetrics.cols} />
      </div>

      {/* Two-column layout */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Sector Allocation */}
        <div>
          <DonutChart01 title="Sector Allocation" data={data.sectorAllocation.data} />
        </div>

        {/* Recent Price Movements */}
        <div>
          <SparkChart01
            title="Recent Price Movements"
            description="Last 2 weeks of price action"
            data={data.priceMovements.data}
            items={data.priceMovements.items}
            dataIndex="date"
          />
        </div>
      </div>

      {/* Holdings Table */}
      <div>
        <Table01
          data={data.holdings.rows}
          columns={data.holdings.columns.map((name) => ({
            key: name,
            label: name,
            align: (name.toLowerCase().includes('p&l') ||
              name.toLowerCase().includes('value') ||
              name.toLowerCase().includes('%') ||
              name.toLowerCase().includes('cost') ||
              name.toLowerCase().includes('price')) as any
              ? 'right'
              : 'left',
          }))}
        />
      </div>
    </div>
  );
};
