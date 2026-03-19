/**
 * Price History with Moving Averages finBlock
 * Wraps: LineChart01
 * Description: 12-month price history with 50-day and 200-day moving averages
 */

import React from 'react';
import { LineChart01 } from '../../../blocks/line-charts/line-chart-01';

export interface PriceHistoryWithMaData {
  data?: any[];
  categories?: string[];
  summary?: any[];
}

const SAMPLE_DATA: PriceHistoryWithMaData = {
  data: [
    { date: '2024-01-01', value: 100 },
    { date: '2024-01-02', value: 120 },
    { date: '2024-01-03', value: 110 },
  ],
  categories: ['value'],
};

export const PriceHistoryWithMa: React.FC<{ data?: PriceHistoryWithMaData }> = ({ data = SAMPLE_DATA }) => {
  return <LineChart01 {...data} />;
};