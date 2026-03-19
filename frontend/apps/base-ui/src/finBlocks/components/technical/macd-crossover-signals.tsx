/**
 * MACD Trend Following Signals finBlock
 * Wraps: BarList02
 * Description: Holdings with MACD crossovers (bullish/bearish)
 */

import React from 'react';
import { BarList02 } from '../../../blocks/bar-lists/bar-list-02';

export interface MacdCrossoverSignalsData {
  data?: any[];
}

const SAMPLE_DATA: MacdCrossoverSignalsData = {
  data: [
    { name: 'Item 1', value: 50 },
    { name: 'Item 2', value: 40 },
    { name: 'Item 3', value: 30 },
  ],
};

export const MacdCrossoverSignals: React.FC<{ data?: MacdCrossoverSignalsData }> = ({ data = SAMPLE_DATA }) => {
  return <BarList02 {...data} />;
};