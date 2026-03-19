/**
 * Return Distribution Analysis finBlock
 * Wraps: BarChart08
 * Description: Histogram of monthly returns showing distribution shape
 */

import React from 'react';
import { BarChart08 } from '../../../blocks/bar-charts/bar-chart-08';

export interface ReturnDistributionData {
  data?: any[];
  categories?: string[];
}

const SAMPLE_DATA: ReturnDistributionData = {
  data: [
    { date: '2024-01-01', value: 100 },
    { date: '2024-01-02', value: 120 },
    { date: '2024-01-03', value: 110 },
  ],
  categories: ['value'],
};

export const ReturnDistribution: React.FC<{ data?: ReturnDistributionData }> = ({ data = SAMPLE_DATA }) => {
  return <BarChart08 {...data} />;
};