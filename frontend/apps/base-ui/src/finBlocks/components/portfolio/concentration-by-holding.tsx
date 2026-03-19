/**
 * Portfolio Concentration Risk finBlock
 * Wraps: BarList02
 * Description: Top 10 holdings as % of portfolio - identifies concentration risk
 */

import React from 'react';
import { BarList02 } from '../../../blocks/bar-lists/bar-list-02';

export interface ConcentrationByHoldingData {
  data?: any[];
}

const SAMPLE_DATA: ConcentrationByHoldingData = {
  data: [
    { name: 'Item 1', value: 50 },
    { name: 'Item 2', value: 40 },
    { name: 'Item 3', value: 30 },
  ],
};

export const ConcentrationByHolding: React.FC<{ data?: ConcentrationByHoldingData }> = ({ data = SAMPLE_DATA }) => {
  return <BarList02 {...data} />;
};