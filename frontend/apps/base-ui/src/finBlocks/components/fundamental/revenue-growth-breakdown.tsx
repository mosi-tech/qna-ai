/**
 * Revenue Growth Sources finBlock
 * Wraps: BarList01
 * Description: Organic growth vs acquisitions vs price increases
 */

import React from 'react';
import { BarList01 } from '../../../blocks/bar-lists/bar-list-01';

export interface RevenueGrowthBreakdownData {
  data?: any[];
}

const SAMPLE_DATA: RevenueGrowthBreakdownData = {
  data: [
    { name: 'Item 1', value: 50 },
    { name: 'Item 2', value: 40 },
    { name: 'Item 3', value: 30 },
  ],
};

export const RevenueGrowthBreakdown: React.FC<{ data?: RevenueGrowthBreakdownData }> = ({ data = SAMPLE_DATA }) => {
  return <BarList01 {...data} />;
};