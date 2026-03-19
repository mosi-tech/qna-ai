/**
 * ETF Dividend Yield Over Time finBlock
 * Wraps: LineChart04
 * Description: Dividend yield trend for distribution-focused ETF
 */

import React from 'react';
import { LineChart04 } from '../../../blocks/line-charts/line-chart-04';

export interface EtfDividendYieldTrendData {
  data?: any[];
  categories?: string[];
  summary?: any[];
}

const SAMPLE_DATA: EtfDividendYieldTrendData = {
  data: [
    { date: '2024-01-01', value: 100 },
    { date: '2024-01-02', value: 120 },
    { date: '2024-01-03', value: 110 },
  ],
  categories: ['value'],
};

export const EtfDividendYieldTrend: React.FC<{ data?: EtfDividendYieldTrendData }> = ({ data = SAMPLE_DATA }) => {
  return <LineChart04 {...data} />;
};