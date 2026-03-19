/**
 * Risk by Sector finBlock
 * Wraps: BarChart06
 * Description: Volatility and risk contribution by sector
 */

import React from 'react';
import { BarChart06 } from '../../../blocks/bar-charts/bar-chart-06';

export interface SectorRiskExposureData {
  data?: any[];
  categories?: string[];
}

const SAMPLE_DATA: SectorRiskExposureData = {
  data: [
    { date: '2024-01-01', value: 100 },
    { date: '2024-01-02', value: 120 },
    { date: '2024-01-03', value: 110 },
  ],
  categories: ['value'],
};

export const SectorRiskExposure: React.FC<{ data?: SectorRiskExposureData }> = ({ data = SAMPLE_DATA }) => {
  return <BarChart06 {...data} />;
};