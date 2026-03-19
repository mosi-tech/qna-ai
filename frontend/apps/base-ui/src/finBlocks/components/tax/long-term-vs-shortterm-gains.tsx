/**
 * Long-term vs Short-term Gains Tax Analysis finBlock
 * Wraps: BarChart01
 * Description: Unrealized gains categorized by holding period (tax efficiency)
 */

import React from 'react';
import { BarChart01 } from '../../../blocks/bar-charts/bar-chart-01';

export interface LongTermVsShorttermGainsData {
  data?: any[];
  categories?: string[];
}

const SAMPLE_DATA: LongTermVsShorttermGainsData = {
  data: [
    { date: '2024-01-01', value: 100 },
    { date: '2024-01-02', value: 120 },
    { date: '2024-01-03', value: 110 },
  ],
  categories: ['value'],
};

export const LongTermVsShorttermGains: React.FC<{ data?: LongTermVsShorttermGainsData }> = ({ data = SAMPLE_DATA }) => {
  return <BarChart01 {...data} />;
};