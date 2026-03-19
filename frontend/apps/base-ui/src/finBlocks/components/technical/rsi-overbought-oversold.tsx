/**
 * RSI Overbought/Oversold Signals finBlock
 * Wraps: BarList01
 * Description: Holdings with RSI > 70 (overbought) or < 30 (oversold)
 */

import React from 'react';
import { BarList01 } from '../../../blocks/bar-lists/bar-list-01';

export interface RsiOverboughtOversoldData {
  data?: any[];
}

const SAMPLE_DATA: RsiOverboughtOversoldData = {
  data: [
    { name: 'Item 1', value: 50 },
    { name: 'Item 2', value: 40 },
    { name: 'Item 3', value: 30 },
  ],
};

export const RsiOverboughtOversold: React.FC<{ data?: RsiOverboughtOversoldData }> = ({ data = SAMPLE_DATA }) => {
  return <BarList01 {...data} />;
};