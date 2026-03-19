/**
 * Volume Trend Signals finBlock
 * Wraps: BarList04
 * Description: Above/below average volume confirming price moves
 */

import React from 'react';
import { BarList04 } from '../../../blocks/bar-lists/bar-list-04';

export interface VolumeTrendTechnicalData {
  data?: any[];
}

const SAMPLE_DATA: VolumeTrendTechnicalData = {
  data: [
    { name: 'Item 1', value: 50 },
    { name: 'Item 2', value: 40 },
    { name: 'Item 3', value: 30 },
  ],
};

export const VolumeTrendTechnical: React.FC<{ data?: VolumeTrendTechnicalData }> = ({ data = SAMPLE_DATA }) => {
  return <BarList04 {...data} />;
};