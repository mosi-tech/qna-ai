/**
 * Dividend Yield by Sector finBlock
 * Wraps: BarChart11
 * Description: Average dividend yield for each sector in portfolio
 */

import React from 'react';
import { BarChart11 } from '../../../blocks/bar-charts/bar-chart-11';

export interface SectorDividendYieldData {
  data?: any[];
  categories?: string[];
}

const SAMPLE_DATA: SectorDividendYieldData = {
  data: [
    { date: '2024-01-01', value: 100 },
    { date: '2024-01-02', value: 120 },
    { date: '2024-01-03', value: 110 },
  ],
  categories: ['value'],
};

export const SectorDividendYield: React.FC<{ data?: SectorDividendYieldData }> = ({ data = SAMPLE_DATA }) => {
  return <BarChart11 {...data} />;
};