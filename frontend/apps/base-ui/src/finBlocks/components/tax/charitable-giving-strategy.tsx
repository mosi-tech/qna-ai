/**
 * Charitable Giving Opportunity (Donate Appreciated Stock) finBlock
 * Wraps: BarList01
 * Description: Identify appreciated holdings suitable for charitable donations
 */

import React from 'react';
import { BarList01 } from '../../../blocks/bar-lists/bar-list-01';

export interface CharitableGivingStrategyData {
  data?: any[];
}

const SAMPLE_DATA: CharitableGivingStrategyData = {
  data: [
    { name: 'Item 1', value: 50 },
    { name: 'Item 2', value: 40 },
    { name: 'Item 3', value: 30 },
  ],
};

export const CharitableGivingStrategy: React.FC<{ data?: CharitableGivingStrategyData }> = ({ data = SAMPLE_DATA }) => {
  return <BarList01 {...data} />;
};