/**
 * Average Valuation by Sector finBlock
 * Wraps: BarList01
 * Description: Average P/E and P/B ratios for sectors in portfolio
 */

import React from 'react';
import { BarList01 } from '../../../blocks/bar-lists/bar-list-01';

export interface SectorValuationMetricsData {
  data?: any[];
}

const SAMPLE_DATA: SectorValuationMetricsData = {
  data: [
    { name: 'Item 1', value: 50 },
    { name: 'Item 2', value: 40 },
    { name: 'Item 3', value: 30 },
  ],
};

export const SectorValuationMetrics: React.FC<{ data?: SectorValuationMetricsData }> = ({ data = SAMPLE_DATA }) => {
  return <BarList01 {...data} />;
};