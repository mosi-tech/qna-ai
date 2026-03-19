/**
 * Economic Cycle Positioning finBlock
 * Wraps: BarChart03
 * Description: Sector positions aligned with growth/value/defensive cycles
 */

import React from 'react';
import { BarChart03 } from '../../../blocks/bar-charts/bar-chart-03';

export interface EconomicCyclePositioningData {
  data?: any[];
  categories?: string[];
}

const SAMPLE_DATA: EconomicCyclePositioningData = {
  data: [
    { date: '2024-01-01', value: 100 },
    { date: '2024-01-02', value: 120 },
    { date: '2024-01-03', value: 110 },
  ],
  categories: ['value'],
};

export const EconomicCyclePositioning: React.FC<{ data?: EconomicCyclePositioningData }> = ({ data = SAMPLE_DATA }) => {
  return <BarChart03 {...data} />;
};