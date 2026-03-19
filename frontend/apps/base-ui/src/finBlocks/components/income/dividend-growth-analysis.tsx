/**
 * Dividend Growth Rate finBlock
 * Wraps: BarChart10
 * Description: YoY dividend per share growth showing dividend growth trajectory
 */

import React from 'react';
import { BarChart10 } from '../../../blocks/bar-charts/bar-chart-10';

export interface DividendGrowthAnalysisData {
  data?: any[];
  categories?: string[];
}

const SAMPLE_DATA: DividendGrowthAnalysisData = {
  data: [
    { date: '2024-01-01', value: 100 },
    { date: '2024-01-02', value: 120 },
    { date: '2024-01-03', value: 110 },
  ],
  categories: ['value'],
};

export const DividendGrowthAnalysis: React.FC<{ data?: DividendGrowthAnalysisData }> = ({ data = SAMPLE_DATA }) => {
  return <BarChart10 {...data} />;
};