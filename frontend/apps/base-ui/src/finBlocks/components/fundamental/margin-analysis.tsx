/**
 * Profitability Margins Over Time finBlock
 * Wraps: LineChart01
 * Description: Gross, operating, net margins trend showing profitability
 */

import React from 'react';
import { LineChart01 } from '../../../blocks/line-charts/line-chart-01';

export interface MarginAnalysisData {
  data?: any[];
  categories?: string[];
  summary?: any[];
}

const SAMPLE_DATA: MarginAnalysisData = {
  data: [
    { date: '2024-01-01', value: 100 },
    { date: '2024-01-02', value: 120 },
    { date: '2024-01-03', value: 110 },
  ],
  categories: ['value'],
};

export const MarginAnalysis: React.FC<{ data?: MarginAnalysisData }> = ({ data = SAMPLE_DATA }) => {
  return <LineChart01 {...data} />;
};