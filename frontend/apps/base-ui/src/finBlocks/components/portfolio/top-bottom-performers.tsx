/**
 * Top and Bottom Performers finBlock
 * Wraps: BarList01
 * Description: Best and worst performing holdings by return percentage
 */

import React from 'react';
import { BarList01 } from '../../../blocks/bar-lists/bar-list-01';

export interface TopBottomPerformersData {
  data?: any[];
}

const SAMPLE_DATA: TopBottomPerformersData = {
  data: [
    { name: 'NVDA', value: 42.3 },
    { name: 'MSFT', value: 28.5 },
    { name: 'TSLA', value: 35.7 },
    { name: 'IBM', value: -8.2 },
    { name: 'XOM', value: -4.5 },
    { name: 'GE', value: -12.1 },
  ],
};

export const TopBottomPerformers: React.FC<{ data?: TopBottomPerformersData }> = ({ data = SAMPLE_DATA }) => {
  return (
    <div className="space-y-4">
      <div>
        <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-50">
          Top & Bottom Performers
        </h2>
        <p className="text-sm text-gray-600 dark:text-gray-400">
          Best and worst performing holdings by return percentage
        </p>
      </div>
      <BarList01 {...data} />
    </div>
  );
};