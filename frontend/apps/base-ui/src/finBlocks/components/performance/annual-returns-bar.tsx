/**
 * Annual Returns Comparison finBlock
 * Wraps: BarChart07
 * Description: Year-by-year returns vs benchmark for last 5-10 years
 */

import React from 'react';
import { BarChart07 } from '../../../blocks/bar-charts/bar-chart-07';

export interface AnnualReturnsBarData {
  data?: any[];
  categories?: string[];
}

const SAMPLE_DATA: AnnualReturnsBarData = {
  data: [
    { date: '2024-01-01', value: 100 },
    { date: '2024-01-02', value: 120 },
    { date: '2024-01-03', value: 110 },
  ],
  categories: ['value'],
};

export const AnnualReturnsBar: React.FC<{ data?: AnnualReturnsBarData }> = ({ data = SAMPLE_DATA }) => {
  return <BarChart07 {...data} />;
};