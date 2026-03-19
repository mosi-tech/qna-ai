/**
 * Sector Allocation Breakdown finBlock
 * Wraps: DonutChart01
 * Description: Portfolio allocation across business sectors (Technology, Healthcare, Finance, etc.)
 */

import React from 'react';
import { DonutChart01 } from '../../../blocks/donut-charts/donut-chart-01';

export interface SectorAllocationDonutData {
  data?: any[];
}

const SAMPLE_DATA: SectorAllocationDonutData = {
  data: [
    { name: 'Category A', value: 40 },
    { name: 'Category B', value: 30 },
    { name: 'Category C', value: 30 },
  ],
};

export const SectorAllocationDonut: React.FC<{ data?: SectorAllocationDonutData }> = ({ data = SAMPLE_DATA }) => {
  return <DonutChart01 {...data} />;
};