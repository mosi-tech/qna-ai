/**
 * Rolling Returns Analysis finBlock
 * Wraps: LineChart07
 * Description: Rolling 12-month, 3-year, 5-year returns showing consistency
 */

import React from 'react';
import { LineChart07 } from '../../../blocks/line-charts/line-chart-07';

export interface RollingReturnsData {
  data?: any[];
  categories?: string[];
  summary?: any[];
}

const SAMPLE_DATA: RollingReturnsData = {
  data: [
    { date: '2024-01-01', value: 100 },
    { date: '2024-01-02', value: 120 },
    { date: '2024-01-03', value: 110 },
  ],
  categories: ['value'],
};

export const RollingReturns: React.FC<{ data?: RollingReturnsData }> = ({ data = SAMPLE_DATA }) => {
  return <LineChart07 {...data} />;
};