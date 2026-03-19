/**
 * Portfolio vs Benchmark Returns finBlock
 * Wraps: LineChart01
 * Description: Compare portfolio cumulative returns against S&P 500 or custom benchmark
 */

import React from 'react';
import { LineChart01 } from '../../../blocks/line-charts/line-chart-01';

export interface PortfolioPerformanceVsBenchmarkData {
  data?: any[];
  categories?: string[];
  summary?: any[];
}

const SAMPLE_DATA: PortfolioPerformanceVsBenchmarkData = {
  data: [
    { date: '2024-01-01', value: 100 },
    { date: '2024-01-02', value: 120 },
    { date: '2024-01-03', value: 110 },
  ],
  categories: ['value'],
};

export const PortfolioPerformanceVsBenchmark: React.FC<{ data?: PortfolioPerformanceVsBenchmarkData }> = ({ data = SAMPLE_DATA }) => {
  return <LineChart01 {...data} />;
};