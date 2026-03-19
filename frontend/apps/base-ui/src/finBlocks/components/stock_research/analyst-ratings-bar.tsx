/**
 * Analyst Ratings & Target Price finBlock
 * Wraps: BarChart02
 * Description: Buy/hold/sell consensus and average price target
 */

import React from 'react';
import { BarChart02 } from '../../../blocks/bar-charts/bar-chart-02';

export interface AnalystRatingsBarData {
  data?: any[];
  categories?: string[];
}

const SAMPLE_DATA: AnalystRatingsBarData = {
  data: [
    { date: '2024-01-01', value: 100 },
    { date: '2024-01-02', value: 120 },
    { date: '2024-01-03', value: 110 },
  ],
  categories: ['value'],
};

export const AnalystRatingsBar: React.FC<{ data?: AnalystRatingsBarData }> = ({ data = SAMPLE_DATA }) => {
  return <BarChart02 {...data} />;
};