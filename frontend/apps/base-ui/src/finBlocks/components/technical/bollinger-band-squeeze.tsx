/**
 * Bollinger Band Volatility finBlock
 * Wraps: BarList03
 * Description: Holdings in Bollinger Band squeeze (low volatility, potential breakout)
 */

import React from 'react';
import { BarList03 } from '../../../blocks/bar-lists/bar-list-03';

export interface BollingerBandSqueezeData {
  data?: any[];
}

const SAMPLE_DATA: BollingerBandSqueezeData = {
  data: [
    { name: 'Item 1', value: 50 },
    { name: 'Item 2', value: 40 },
    { name: 'Item 3', value: 30 },
  ],
};

export const BollingerBandSqueeze: React.FC<{ data?: BollingerBandSqueezeData }> = ({ data = SAMPLE_DATA }) => {
  return <BarList03 {...data} />;
};