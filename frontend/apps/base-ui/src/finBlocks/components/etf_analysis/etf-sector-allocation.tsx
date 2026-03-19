/**
 * ETF Sector Composition finBlock
 * Wraps: DonutChart03
 * Description: Sector breakdown within an ETF
 */

import React from 'react';
import { DonutChart03 } from '../../../blocks/donut-charts/donut-chart-03';

export interface EtfSectorAllocationData {
  data?: any[];
}

const SAMPLE_DATA: EtfSectorAllocationData = {
  data: [
    { name: 'Category A', value: 40 },
    { name: 'Category B', value: 30 },
    { name: 'Category C', value: 30 },
  ],
};

export const EtfSectorAllocation: React.FC<{ data?: EtfSectorAllocationData }> = ({ data = SAMPLE_DATA }) => {
  return <DonutChart03 {...data} />;
};