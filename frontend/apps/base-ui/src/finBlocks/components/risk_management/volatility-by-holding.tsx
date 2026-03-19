/**
 * Volatility Breakdown by Holding finBlock
 * Wraps: BarChart05
 * Description: Individual stock volatility ranked from highest to lowest
 */

import React from 'react';
import { BarChart05 } from '../../../blocks/bar-charts/bar-chart-05';

export interface VolatilityByHoldingData {
  data?: any[];
  categories?: string[];
}

const SAMPLE_DATA: VolatilityByHoldingData = {
  data: [
    { date: '2024-01-01', value: 100 },
    { date: '2024-01-02', value: 120 },
    { date: '2024-01-03', value: 110 },
  ],
  categories: ['value'],
};

export const VolatilityByHolding: React.FC<{ data?: VolatilityByHoldingData }> = ({ data = SAMPLE_DATA }) => {
  return <BarChart05 {...data} />;
};