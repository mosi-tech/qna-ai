/**
 * Risk Dashboard Template - Hydrated Example
 * Shows: Risk KPIs (VaR, volatility, concentration), volatility by holding, concentration breakdown, drawdown history
 */

import React from 'react';
import { KpiCard01 } from '../blocks/kpi-cards';
import { BarChart01 } from '../blocks/bar-charts';
import { BarList01 } from '../blocks/bar-lists';
import { LineChart01 } from '../blocks/line-charts';

export interface RiskDashboardData {
  riskKpis: {
    metrics: Array<{
      name: string;
      stat: number;
      change: string;
      changeType: 'positive' | 'negative' | 'neutral';
    }>;
    cols: number;
  };
  holdingVolatility: {
    data: Array<{ [key: string]: any }>;
    categories: string[];
  };
  concentrationRisk: {
    data: Array<{ name: string; value: number }>;
  };
  drawdownHistory: {
    data: Array<{ [key: string]: any }>;
    categories: string[];
    summary: Array<{ name: string; value: number }>;
  };
}

const SAMPLE_DATA: RiskDashboardData = {
  riskKpis: {
    metrics: [
      { name: 'Value at Risk (95%)', stat: 8500, change: '+2.3%', changeType: 'negative' },
      { name: 'Portfolio Volatility', stat: 18.5, change: '+0.8%', changeType: 'negative' },
      { name: 'Max Drawdown (1Y)', stat: -12.5, change: '-2.3%', changeType: 'positive' },
      { name: 'Concentration Index', stat: 0.32, change: '-0.05', changeType: 'positive' },
    ],
    cols: 4,
  },
  holdingVolatility: {
    data: [
      { name: 'AAPL', Volatility: 22.5 },
      { name: 'MSFT', Volatility: 19.8 },
      { name: 'GOOGL', Volatility: 23.2 },
      { name: 'NVDA', Volatility: 35.6 },
      { name: 'TSLA', Volatility: 42.1 },
      { name: 'JPM', Volatility: 28.3 },
    ],
    categories: ['Volatility'],
  },
  concentrationRisk: {
    data: [
      { name: 'AAPL (Top 1)', value: 22.6 },
      { name: 'MSFT (Top 2)', value: 26.1 },
      { name: 'NVDA (Top 3)', value: 23.2 },
      { name: 'TSLA (Top 4)', value: 22.8 },
      { name: 'GOOGL (Top 5)', value: 5.2 },
    ],
  },
  drawdownHistory: {
    data: [
      { date: '2025-03-31', Drawdown: 0, 'Portfolio Value': 110000 },
      { date: '2025-04-30', Drawdown: -2.5, 'Portfolio Value': 107250 },
      { date: '2025-05-31', Drawdown: -1.2, 'Portfolio Value': 108700 },
      { date: '2025-06-30', Drawdown: 0, 'Portfolio Value': 110000 },
      { date: '2025-07-31', Drawdown: -3.5, 'Portfolio Value': 106150 },
      { date: '2025-08-31', Drawdown: -8.2, 'Portfolio Value': 101020 },
      { date: '2025-09-30', Drawdown: -5.3, 'Portfolio Value': 104130 },
      { date: '2025-10-31', Drawdown: 0, 'Portfolio Value': 110000 },
      { date: '2025-11-30', Drawdown: -2.1, 'Portfolio Value': 107690 },
      { date: '2025-12-31', Drawdown: 1.2, 'Portfolio Value': 111320 },
      { date: '2026-01-31', Drawdown: -0.8, 'Portfolio Value': 110420 },
      { date: '2026-02-28', Drawdown: -1.5, 'Portfolio Value': 108350 },
      { date: '2026-03-19', Drawdown: 0.5, 'Portfolio Value': 111550 },
    ],
    categories: ['Drawdown', 'Portfolio Value'],
    summary: [
      { name: 'Current Drawdown', value: 0.5 },
      { name: 'Max Drawdown (1Y)', value: -12.5 },
      { name: 'Recovery Time', value: 45 },
    ],
  },
};

export const RiskDashboardTemplate: React.FC<{ data?: RiskDashboardData }> = ({ data = SAMPLE_DATA }) => {
  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-50">Risk Dashboard</h2>

      {/* Risk KPIs */}
      <div className="bg-amber-50 dark:bg-amber-950/20 border border-amber-200 dark:border-amber-800 rounded-lg p-4 mb-2">
        <p className="text-sm text-amber-800 dark:text-amber-300 font-medium">
          ⚠️ Risk Metrics Monitor - Track portfolio volatility, concentration, and drawdown exposure
        </p>
      </div>

      <KpiCard01 metrics={data.riskKpis.metrics} cols={data.riskKpis.cols} />

      {/* Two-column middle section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Volatility by Holding */}
        <BarChart01
          title="Volatility by Holding (Annual)"
          description="Individual stock volatility - higher = more risky"
          data={data.holdingVolatility.data}
          indexField="name"
          defaultCategories={['Volatility']}
          comparisonCategories={data.holdingVolatility.categories}
        />

        {/* Concentration Risk */}
        <BarList01 title="Concentration Risk" subtitle="% of Portfolio" data={data.concentrationRisk.data} />
      </div>

      {/* Drawdown History */}
      <LineChart01
        title="Drawdown History & Portfolio Value"
        description="Peak-to-trough declines and portfolio growth over 12 months"
        data={data.drawdownHistory.data}
        categories={data.drawdownHistory.categories}
        summary={data.drawdownHistory.summary}
        indexField="date"
      />

      {/* Risk Summary */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-slate-50 dark:bg-slate-800 rounded-lg p-4 border border-slate-200 dark:border-slate-700">
          <p className="text-xs font-semibold text-gray-600 dark:text-gray-400 uppercase">Diversification Health</p>
          <p className="text-lg font-bold text-green-600 dark:text-green-400 mt-2">Good</p>
          <p className="text-xs text-gray-500 dark:text-gray-500 mt-1">HHI: 0.32 (< 0.50)</p>
        </div>

        <div className="bg-slate-50 dark:bg-slate-800 rounded-lg p-4 border border-slate-200 dark:border-slate-700">
          <p className="text-xs font-semibold text-gray-600 dark:text-gray-400 uppercase">Volatility Regime</p>
          <p className="text-lg font-bold text-orange-600 dark:text-orange-400 mt-2">Elevated</p>
          <p className="text-xs text-gray-500 dark:text-gray-500 mt-1">18.5% annualized</p>
        </div>

        <div className="bg-slate-50 dark:bg-slate-800 rounded-lg p-4 border border-slate-200 dark:border-slate-700">
          <p className="text-xs font-semibold text-gray-600 dark:text-gray-400 uppercase">Drawdown Recovery</p>
          <p className="text-lg font-bold text-blue-600 dark:text-blue-400 mt-2">Stable</p>
          <p className="text-xs text-gray-500 dark:text-gray-500 mt-1">+0.5% from peak</p>
        </div>
      </div>
    </div>
  );
};
