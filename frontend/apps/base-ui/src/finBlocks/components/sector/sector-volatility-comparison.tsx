/**
 * Volatility by Sector finBlock
 * Wraps: BarChart02
 * Description: Risk level (volatility) for each sector in portfolio
 */

import React from 'react';
import { BarChart02 } from '../../../blocks/bar-charts/bar-chart-02';

export interface SectorVolatilityComparisonData {
  data?: any[];
  categories?: string[];
}

const SAMPLE_DATA: SectorVolatilityComparisonData = {
  data: [
    { date: '2024-01-01', value: 100 },
    { date: '2024-01-02', value: 120 },
    { date: '2024-01-03', value: 110 },
  ],
  categories: ['value'],
};

export const SectorVolatilityComparison: React.FC<{ data?: SectorVolatilityComparisonData }> = ({ data = SAMPLE_DATA }) => {
  return <BarChart02 {...data} />;
};