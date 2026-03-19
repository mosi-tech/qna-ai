/**
 * Portfolio KPI Summary finBlock
 * Wraps: KpiCard01
 * Description: Overview of your portfolio's total value, profitability, and year-to-date performance
 */

import React from 'react';
import { KpiCard01 } from '../../../blocks/kpi-cards/kpi-card-01';

export interface PortfolioKpiSummaryData {
  metrics?: Array<{ name: string; stat: number | string; change: string; changeType: 'positive' | 'negative' | 'neutral' }>;
  cols?: number;
}

const SAMPLE_DATA: PortfolioKpiSummaryData = {
  metrics: [
    {
      name: 'Portfolio Value',
      stat: '$487,250',
      change: '+8.3%',
      changeType: 'positive'
    },
    {
      name: 'Total P&L',
      stat: '+$52,150',
      change: '+12.0%',
      changeType: 'positive'
    },
    {
      name: 'YTD Return',
      stat: '18.3%',
      change: '+2.1% vs benchmark',
      changeType: 'positive'
    },
  ],
  cols: 3,
};

export const PortfolioKpiSummary: React.FC<{ data?: PortfolioKpiSummaryData }> = ({ data = SAMPLE_DATA }) => {
  return (
    <div className="space-y-4">
      <div>
        <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-50">
          Portfolio KPI Summary
        </h2>
        <p className="text-sm text-gray-600 dark:text-gray-400">
          Overview of your portfolio's total value, profitability, and year-to-date performance
        </p>
      </div>
      <KpiCard01 {...data} />
    </div>
  );
};