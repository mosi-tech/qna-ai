/**
 * Best & Worst Performing Periods finBlock
 * Wraps: BarList09
 * Description: Top and bottom N days/weeks/months showing extreme performance
 */

import React from 'react';
import { BarList09 } from '../../../blocks/bar-lists/bar-list-09';

export interface BestWorstPeriodsData {
  data?: any[];
}

const SAMPLE_DATA: BestWorstPeriodsData = {
  data: [
    { name: 'Item 1', value: 50 },
    { name: 'Item 2', value: 40 },
    { name: 'Item 3', value: 30 },
  ],
};

export const BestWorstPeriods: React.FC<{ data?: BestWorstPeriodsData }> = ({ data = SAMPLE_DATA }) => {
  return <BarList09 {...data} />;
};