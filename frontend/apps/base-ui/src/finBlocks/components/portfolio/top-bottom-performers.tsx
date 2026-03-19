/**
 * Top and Bottom Performers finBlock
 * Wraps: BarList01
 * Description: Best and worst performing holdings by return %
 */

import React from 'react';
import { BarList01 } from '../../../blocks/bar-lists/bar-list-01';

export interface TopBottomPerformersData {
  data?: any[];
}

const SAMPLE_DATA: TopBottomPerformersData = {
  data: [
    { name: 'Item 1', value: 50 },
    { name: 'Item 2', value: 40 },
    { name: 'Item 3', value: 30 },
  ],
};

export const TopBottomPerformers: React.FC<{ data?: TopBottomPerformersData }> = ({ data = SAMPLE_DATA }) => {
  return <BarList01 {...data} />;
};