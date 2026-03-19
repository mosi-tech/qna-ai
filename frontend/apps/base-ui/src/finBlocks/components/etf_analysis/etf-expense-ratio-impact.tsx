/**
 * Expense Ratio Impact on Returns finBlock
 * Wraps: LineChart05
 * Description: Shows how fees compound over time at different return assumptions
 */

import React from 'react';
import { LineChart05 } from '../../../blocks/line-charts/line-chart-05';

export interface EtfExpenseRatioImpactData {
  data?: any[];
  categories?: string[];
  summary?: any[];
}

const SAMPLE_DATA: EtfExpenseRatioImpactData = {
  data: [
    { date: '2024-01-01', value: 100 },
    { date: '2024-01-02', value: 120 },
    { date: '2024-01-03', value: 110 },
  ],
  categories: ['value'],
};

export const EtfExpenseRatioImpact: React.FC<{ data?: EtfExpenseRatioImpactData }> = ({ data = SAMPLE_DATA }) => {
  return <LineChart05 {...data} />;
};