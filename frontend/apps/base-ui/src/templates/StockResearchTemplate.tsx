/**
 * Stock Research Template - Hydrated Example
 * Shows: Stock snapshot (KPI), price history (line chart), fundamentals (list), quarterly data (table)
 */

import React from 'react';
import { KpiCard01 } from '../blocks/kpi-cards';
import { LineChart01 } from '../blocks/line-charts';
import { BarList01 } from '../blocks/bar-lists';
import { Table01 } from '../blocks/tables';

export interface StockResearchData {
  stockMetrics: {
    metrics: Array<{
      name: string;
      stat: number;
      change: string;
      changeType: 'positive' | 'negative' | 'neutral';
    }>;
    cols: number;
  };
  priceHistory: {
    data: Array<{ [key: string]: any }>;
    categories: string[];
    summary: Array<{ name: string; value: number }>;
  };
  fundamentals: {
    data: Array<{ name: string; value: number }>;
  };
  quarterlyData: {
    rows: Array<{
      Quarter: string;
      'Revenue (B)': number;
      'EPS': number;
      'Margin %': number;
      'Growth %': number;
    }>;
    columns: string[];
  };
}

const SAMPLE_DATA: StockResearchData = {
  stockMetrics: {
    metrics: [
      { name: 'Price', stat: 181.50, change: '+2.8%', changeType: 'positive' },
      { name: 'Market Cap', stat: 2840000000000, change: '+3.2%', changeType: 'positive' },
      { name: 'P/E Ratio', stat: 28.5, change: '-0.5', changeType: 'negative' },
      { name: 'Div Yield', stat: 0.42, change: '+0.05%', changeType: 'positive' },
    ],
    cols: 4,
  },
  priceHistory: {
    data: [
      { date: '2025-03-19', AAPL: 145.25, 'SMA-50': 142.50, 'SMA-200': 140.25 },
      { date: '2025-04-19', AAPL: 150.75, 'SMA-50': 145.10, 'SMA-200': 141.30 },
      { date: '2025-05-19', AAPL: 155.50, 'SMA-50': 147.75, 'SMA-200': 142.45 },
      { date: '2025-06-19', AAPL: 165.25, 'SMA-50': 153.20, 'SMA-200': 144.50 },
      { date: '2025-07-19', AAPL: 172.50, 'SMA-50': 159.35, 'SMA-200': 146.75 },
      { date: '2025-08-19', AAPL: 168.75, 'SMA-50': 162.45, 'SMA-200': 148.20 },
      { date: '2025-09-19', AAPL: 175.25, 'SMA-50': 166.50, 'SMA-200': 150.15 },
      { date: '2025-10-19', AAPL: 180.50, 'SMA-50': 171.20, 'SMA-200': 152.40 },
      { date: '2025-11-19', AAPL: 178.25, 'SMA-50': 173.75, 'SMA-200': 154.60 },
      { date: '2025-12-19', AAPL: 182.75, 'SMA-50': 176.80, 'SMA-200': 156.85 },
      { date: '2026-01-19', AAPL: 185.50, 'SMA-50': 179.45, 'SMA-200': 158.75 },
      { date: '2026-02-19', AAPL: 183.25, 'SMA-50': 180.90, 'SMA-200': 160.25 },
      { date: '2026-03-19', AAPL: 181.50, 'SMA-50': 181.25, 'SMA-200': 161.50 },
    ],
    categories: ['AAPL', 'SMA-50', 'SMA-200'],
    summary: [
      { name: 'AAPL', value: 181.50 },
      { name: 'Target', value: 195.00 },
      { name: 'Resistance', value: 190.25 },
    ],
  },
  fundamentals: {
    data: [
      { name: 'P/E Ratio', value: 28.5 },
      { name: 'P/B Ratio', value: 45.8 },
      { name: 'ROE', value: 156.2 },
      { name: 'Dividend Yield', value: 0.42 },
      { name: 'Debt/Equity', value: 0.15 },
    ],
  },
  quarterlyData: {
    rows: [
      { Quarter: 'Q2 2025', 'Revenue (B)': 85.8, 'EPS': 1.52, 'Margin %': 29.6, 'Growth %': 4.3 },
      { Quarter: 'Q3 2025', 'Revenue (B)': 89.5, 'EPS': 1.63, 'Margin %': 30.1, 'Growth %': 4.3 },
      { Quarter: 'Q4 2025', 'Revenue (B)': 114.3, 'EPS': 2.18, 'Margin %': 31.5, 'Growth %': 5.2 },
      { Quarter: 'Q1 2026', 'Revenue (B)': 94.7, 'EPS': 1.72, 'Margin %': 29.8, 'Growth %': 3.8 },
    ],
    columns: ['Quarter', 'Revenue (B)', 'EPS', 'Margin %', 'Growth %'],
  },
};

export const StockResearchTemplate: React.FC<{ ticker?: string; data?: StockResearchData }> = ({
  ticker = 'AAPL',
  data = SAMPLE_DATA,
}) => {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-50 mb-2">{ticker} - Apple Inc</h2>
        <p className="text-sm text-gray-600 dark:text-gray-400">NASDAQ · Technology · Market Cap: $2.84T</p>
      </div>

      {/* Stock Metrics */}
      <KpiCard01 metrics={data.stockMetrics.metrics} cols={data.stockMetrics.cols} />

      {/* Two-column layout */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Price History */}
        <LineChart01
          title="Price History & Moving Averages"
          data={data.priceHistory.data}
          categories={data.priceHistory.categories}
          summary={data.priceHistory.summary}
          indexField="date"
        />

        {/* Fundamentals */}
        <BarList01 title="Fundamental Metrics" subtitle="Value" data={data.fundamentals.data} />
      </div>

      {/* Quarterly Performance */}
      <Table01
        data={data.quarterlyData.rows}
        columns={data.quarterlyData.columns.map((name) => ({
          key: name,
          label: name,
          align: (name.includes('Revenue') || name.includes('EPS') || name.includes('Margin') || name.includes('Growth'))
            ? ('right' as const)
            : 'left',
        }))}
      />
    </div>
  );
};
