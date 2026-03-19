/**
 * Concentration Risk Index finBlock
 * Wraps: BarList06
 * Description: Top 10 holdings as % of portfolio, HHI concentration index
 */

import React from 'react';
import { BarList06 } from '../../../blocks/bar-lists/bar-list-06';

export interface ConcentrationRiskData {
  data?: any[];
}

const SAMPLE_DATA: ConcentrationRiskData = {
  data: [
    { name: 'Item 1', value: 50 },
    { name: 'Item 2', value: 40 },
    { name: 'Item 3', value: 30 },
  ],
};

export const ConcentrationRisk: React.FC<{ data?: ConcentrationRiskData }> = ({ data = SAMPLE_DATA }) => {
  return <BarList06 {...data} />;
};