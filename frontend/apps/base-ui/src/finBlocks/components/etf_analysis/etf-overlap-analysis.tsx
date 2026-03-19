/**
 * ETF Overlap & Redundancy finBlock
 * Wraps: BarList05
 * Description: Shows common holdings between multiple ETFs to identify overlap
 */

import React from 'react';
import { BarList05 } from '../../../blocks/bar-lists/bar-list-05';

export interface EtfOverlapAnalysisData {
  data?: any[];
}

const SAMPLE_DATA: EtfOverlapAnalysisData = {
  data: [
    { name: 'Item 1', value: 50 },
    { name: 'Item 2', value: 40 },
    { name: 'Item 3', value: 30 },
  ],
};

export const EtfOverlapAnalysis: React.FC<{ data?: EtfOverlapAnalysisData }> = ({ data = SAMPLE_DATA }) => {
  return <BarList05 {...data} />;
};