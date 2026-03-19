/**
 * Top Dividend Yielders finBlock
 * Wraps: BarList10
 * Description: Holdings ranked by dividend yield
 */

import React from 'react';
import { BarList10 } from '../../../blocks/bar-lists/bar-list-10';

export interface TopDividendYieldersData {
  data?: any[];
}

const SAMPLE_DATA: TopDividendYieldersData = {
  data: [
    { name: 'Item 1', value: 50 },
    { name: 'Item 2', value: 40 },
    { name: 'Item 3', value: 30 },
  ],
};

export const TopDividendYielders: React.FC<{ data?: TopDividendYieldersData }> = ({ data = SAMPLE_DATA }) => {
  return <BarList10 {...data} />;
};