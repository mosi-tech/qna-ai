/**
 * Sector Performance Comparison finBlock
 * Wraps: BarChart01
 * Description: Annual returns by sector showing best/worst performing sectors
 */

import React from 'react';
import { BarChart01 } from '../../../blocks/bar-charts/bar-chart-01';

export interface SectorPerformanceBarData {
  data?: any[];
  categories?: string[];
}

const SAMPLE_DATA: SectorPerformanceBarData = {
  data: [
    { date: '2024-01-01', value: 100 },
    { date: '2024-01-02', value: 120 },
    { date: '2024-01-03', value: 110 },
  ],
  categories: ['value'],
};

export const SectorPerformanceBar: React.FC<{ data?: SectorPerformanceBarData }> = ({ data = SAMPLE_DATA }) => {
  return <BarChart01 {...data} />;
};