/**
 * Monthly Dividend Income Trend finBlock
 * Wraps: LineChart08
 * Description: Monthly dividend income over last 12 months showing seasonality
 */

import React from 'react';
import { LineChart08 } from '../../../blocks/line-charts/line-chart-08';

export interface MonthlyDividendTrendData {
  data?: any[];
  categories?: string[];
  summary?: any[];
}

const SAMPLE_DATA: MonthlyDividendTrendData = {
  data: [
    { date: '2024-01-01', value: 100 },
    { date: '2024-01-02', value: 120 },
    { date: '2024-01-03', value: 110 },
  ],
  categories: ['value'],
};

export const MonthlyDividendTrend: React.FC<{ data?: MonthlyDividendTrendData }> = ({ data = SAMPLE_DATA }) => {
  return <LineChart08 {...data} />;
};