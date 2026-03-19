/**
 * Asset Class Allocation finBlock
 * Wraps: DonutChart02
 * Description: Breakdown of stocks vs ETFs vs bonds vs cash
 */

import React from 'react';
import { DonutChart02 } from '../../../blocks/donut-charts/donut-chart-02';

export interface AssetClassAllocationData {
  data?: any[];
}

const SAMPLE_DATA: AssetClassAllocationData = {
  data: [
    { name: 'Category A', value: 40 },
    { name: 'Category B', value: 30 },
    { name: 'Category C', value: 30 },
  ],
};

export const AssetClassAllocation: React.FC<{ data?: AssetClassAllocationData }> = ({ data = SAMPLE_DATA }) => {
  return <DonutChart02 {...data} />;
};