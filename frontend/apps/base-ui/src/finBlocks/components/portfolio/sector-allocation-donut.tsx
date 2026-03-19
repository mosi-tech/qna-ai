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
    { name: 'Technology', value: 38 },
    { name: 'Healthcare', value: 18 },
    { name: 'Financials', value: 16 },
    { name: 'Consumer', value: 12 },
    { name: 'Energy', value: 8 },
    { name: 'Industrials', value: 8 },
  ],
};

export const SectorAllocationDonut: React.FC<{ data?: SectorAllocationDonutData }> = ({ data = SAMPLE_DATA }) => {
  return (
    <div className="space-y-4">
      <div>
        <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-50">
          Sector Allocation
        </h2>
        <p className="text-sm text-gray-600 dark:text-gray-400">
          Portfolio distribution across business sectors
        </p>
      </div>
      <DonutChart01 {...data} />
    </div>
  );
};