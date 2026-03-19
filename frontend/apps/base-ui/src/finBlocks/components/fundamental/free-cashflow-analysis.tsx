/**
 * Free Cash Flow & Sustainability finBlock
 * Wraps: LineChart02
 * Description: Operating cash flow vs capital expenditure showing cash generation
 */

import React from 'react';
import { LineChart02 } from '../../../blocks/line-charts/line-chart-02';

export interface FreeCashflowAnalysisData {
  data?: any[];
  categories?: string[];
  summary?: any[];
}

const SAMPLE_DATA: FreeCashflowAnalysisData = {
  data: [
    { date: '2024-01-01', value: 100 },
    { date: '2024-01-02', value: 120 },
    { date: '2024-01-03', value: 110 },
  ],
  categories: ['value'],
};

export const FreeCashflowAnalysis: React.FC<{ data?: FreeCashflowAnalysisData }> = ({ data = SAMPLE_DATA }) => {
  return <LineChart02 {...data} />;
};