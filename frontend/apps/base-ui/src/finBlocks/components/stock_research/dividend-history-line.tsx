/**
 * Dividend History & Growth finBlock
 * Wraps: LineChart02
 * Description: Dividend per share over last 10 years showing growth trend
 */

import React from 'react';
import { LineChart02 } from '../../../blocks/line-charts/line-chart-02';

export interface DividendHistoryLineData {
  data?: any[];
  categories?: string[];
  summary?: any[];
}

const SAMPLE_DATA: DividendHistoryLineData = {
  data: [
    { date: '2024-01-01', value: 100 },
    { date: '2024-01-02', value: 120 },
    { date: '2024-01-03', value: 110 },
  ],
  categories: ['value'],
};

export const DividendHistoryLine: React.FC<{ data?: DividendHistoryLineData }> = ({ data = SAMPLE_DATA }) => {
  return <LineChart02 {...data} />;
};