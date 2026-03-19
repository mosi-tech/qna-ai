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
    { name: 'Equities', value: 72 },
    { name: 'Bonds', value: 15 },
    { name: 'ETFs', value: 10 },
    { name: 'Cash', value: 3 },
  ],
};

export const AssetClassAllocation: React.FC<{ data?: AssetClassAllocationData }> = ({ data = SAMPLE_DATA }) => {
  return (
    <div className="space-y-4">
      <div>
        <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-50">
          Asset Class Allocation
        </h2>
        <p className="text-sm text-gray-600 dark:text-gray-400">
          Breakdown of stocks vs ETFs vs bonds vs cash
        </p>
      </div>
      <DonutChart02 {...data} />
    </div>
  );
};