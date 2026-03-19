/**
 * Portfolio Dividend Metrics finBlock
 * Wraps: KpiCard02
 * Description: Annual dividend income, current yield, and upcoming distribution dates
 */

import React from 'react';
import { KpiCard02 } from '../../../blocks/kpi-cards/kpi-card-02';

export interface DividendSummaryKpiData {
  metrics?: Array<{ name: string; stat: number | string; change: string; changeType: 'positive' | 'negative' | 'neutral' }>;
  cols?: number;
}

const SAMPLE_DATA: DividendSummaryKpiData = {
  metrics: [
    {
      name: 'Annual Dividend Income',
      stat: '$8,340',
      change: '+12.5%',
      changeType: 'positive'
    },
    {
      name: 'Dividend Yield',
      stat: '1.71%',
      change: '+0.15% YoY',
      changeType: 'positive'
    },
    {
      name: 'Next Ex-Dividend',
      stat: 'Mar 31, 2026',
      change: '+15 days',
      changeType: 'neutral'
    },
  ],
  cols: 3,
};

export const DividendSummaryKpi: React.FC<{ data?: DividendSummaryKpiData }> = ({ data = SAMPLE_DATA }) => {
  return (
    <div className="space-y-4">
      <div>
        <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-50">
          Dividend Summary
        </h2>
        <p className="text-sm text-gray-600 dark:text-gray-400">
          Annual dividend income, current yield, and upcoming distribution dates
        </p>
      </div>
      <KpiCard02 {...data} />
    </div>
  );
};