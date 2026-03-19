/**
 * Growth Rates (Revenue, EPS, Free Cash Flow) finBlock
 * Wraps: BarList03
 * Description: YoY growth rates for key metrics showing business acceleration/deceleration
 */

import React from 'react';
import { BarList03 } from '../../../blocks/bar-lists/bar-list-03';

export interface GrowthMetricsComparisonData {
  data?: any[];
}

const SAMPLE_DATA: GrowthMetricsComparisonData = {
  data: [
    { name: 'Item 1', value: 50 },
    { name: 'Item 2', value: 40 },
    { name: 'Item 3', value: 30 },
  ],
};

export const GrowthMetricsComparison: React.FC<{ data?: GrowthMetricsComparisonData }> = ({ data = SAMPLE_DATA }) => {
  return <BarList03 {...data} />;
};