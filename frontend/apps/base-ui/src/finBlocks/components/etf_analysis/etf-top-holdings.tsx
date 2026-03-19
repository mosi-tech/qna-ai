/**
 * Top 10 ETF Holdings finBlock
 * Wraps: BarList04
 * Description: Largest positions within an ETF
 */

import React from 'react';
import { BarList04 } from '../../../blocks/bar-lists/bar-list-04';

export interface EtfTopHoldingsData {
  data?: any[];
}

const SAMPLE_DATA: EtfTopHoldingsData = {
  data: [
    { name: 'Item 1', value: 50 },
    { name: 'Item 2', value: 40 },
    { name: 'Item 3', value: 30 },
  ],
};

export const EtfTopHoldings: React.FC<{ data?: EtfTopHoldingsData }> = ({ data = SAMPLE_DATA }) => {
  return <BarList04 {...data} />;
};