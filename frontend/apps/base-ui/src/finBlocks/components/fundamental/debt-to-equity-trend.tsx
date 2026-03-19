/**
 * Leverage & Debt Metrics finBlock
 * Wraps: BarChart01
 * Description: Debt-to-equity, debt-to-assets, interest coverage trend
 */

import React from 'react';
import { BarChart01 } from '../../../blocks/bar-charts/bar-chart-01';

export interface DebtToEquityTrendData {
  data?: any[];
  categories?: string[];
}

const SAMPLE_DATA: DebtToEquityTrendData = {
  data: [
    { date: '2024-01-01', value: 100 },
    { date: '2024-01-02', value: 120 },
    { date: '2024-01-03', value: 110 },
  ],
  categories: ['value'],
};

export const DebtToEquityTrend: React.FC<{ data?: DebtToEquityTrendData }> = ({ data = SAMPLE_DATA }) => {
  return <BarChart01 {...data} />;
};