/**
 * Volume Trend Analysis finBlock
 * Wraps: BarChart04
 * Description: Trading volume over last 3 months with average comparison
 */

import React from 'react';
import { BarChart04 } from '../../../blocks/bar-charts/bar-chart-04';

export interface VolumeTrendBarData {
  data?: any[];
  categories?: string[];
}

const SAMPLE_DATA: VolumeTrendBarData = {
  data: [
    { date: '2024-01-01', value: 100 },
    { date: '2024-01-02', value: 120 },
    { date: '2024-01-03', value: 110 },
  ],
  categories: ['value'],
};

export const VolumeTrendBar: React.FC<{ data?: VolumeTrendBarData }> = ({ data = SAMPLE_DATA }) => {
  return <BarChart04 {...data} />;
};