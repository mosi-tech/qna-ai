/**
 * Historical Drawdown Analysis finBlock
 * Wraps: LineChart06
 * Description: Peak-to-trough declines over last 3 years with recovery times
 */

import React from 'react';
import { LineChart06 } from '../../../blocks/line-charts/line-chart-06';

export interface DrawdownHistoryData {
  data?: any[];
  categories?: string[];
  summary?: any[];
}

const SAMPLE_DATA: DrawdownHistoryData = {
  data: [
    { date: '2024-01-01', value: 100 },
    { date: '2024-01-02', value: 120 },
    { date: '2024-01-03', value: 110 },
  ],
  categories: ['value'],
};

export const DrawdownHistory: React.FC<{ data?: DrawdownHistoryData }> = ({ data = SAMPLE_DATA }) => {
  return <LineChart06 {...data} />;
};