/**
 * ETF Performance Comparison finBlock
 * Wraps: LineChart03
 * Description: Cumulative returns comparison for multiple ETFs over time
 */

import React from 'react';
import { LineChart03 } from '../../../blocks/line-charts/line-chart-03';

export interface EtfPerformanceLineData {
  data?: any[];
  categories?: string[];
  summary?: any[];
}

const SAMPLE_DATA: EtfPerformanceLineData = {
  data: [
    { date: '2024-01-01', value: 100 },
    { date: '2024-01-02', value: 120 },
    { date: '2024-01-03', value: 110 },
  ],
  categories: ['value'],
};

export const EtfPerformanceLine: React.FC<{ data?: EtfPerformanceLineData }> = ({ data = SAMPLE_DATA }) => {
  return <LineChart03 {...data} />;
};