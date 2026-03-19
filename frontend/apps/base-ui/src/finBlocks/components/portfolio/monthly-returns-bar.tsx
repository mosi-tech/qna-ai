/**
 * Monthly Portfolio Returns finBlock
 * Wraps: BarChart01
 * Description: Bar chart of portfolio returns by month for last 12 months
 */

import React from 'react';
import { BarChart01 } from '../../../blocks/bar-charts/bar-chart-01';

export interface MonthlyReturnsBarData {
  data?: any[];
  categories?: string[];
}

const SAMPLE_DATA: MonthlyReturnsBarData = {
  data: [
    { date: '2024-01-01', value: 100 },
    { date: '2024-01-02', value: 120 },
    { date: '2024-01-03', value: 110 },
  ],
  categories: ['value'],
};

export const MonthlyReturnsBar: React.FC<{ data?: MonthlyReturnsBarData }> = ({ data = SAMPLE_DATA }) => {
  return <BarChart01 {...data} />;
};