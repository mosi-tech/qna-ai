/**
 * Dividend Income by Sector finBlock
 * Wraps: DonutChart01
 * Description: Which sectors contribute to portfolio dividend income
 */

import React from 'react';
import { DonutChart01 } from '../../../blocks/donut-charts/donut-chart-01';

export interface SectorDividendCompositionData {
  data?: any[];
}

const SAMPLE_DATA: SectorDividendCompositionData = {
  data: [
    { name: 'Category A', value: 40 },
    { name: 'Category B', value: 30 },
    { name: 'Category C', value: 30 },
  ],
};

export const SectorDividendComposition: React.FC<{ data?: SectorDividendCompositionData }> = ({ data = SAMPLE_DATA }) => {
  return <DonutChart01 {...data} />;
};