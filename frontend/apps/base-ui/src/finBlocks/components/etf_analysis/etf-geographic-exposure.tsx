/**
 * Geographic Exposure finBlock
 * Wraps: DonutChart04
 * Description: Country/region breakdown for international ETFs
 */

import React from 'react';
import { DonutChart04 } from '../../../blocks/donut-charts/donut-chart-04';

export interface EtfGeographicExposureData {
  data?: any[];
}

const SAMPLE_DATA: EtfGeographicExposureData = {
  data: [
    { name: 'Category A', value: 40 },
    { name: 'Category B', value: 30 },
    { name: 'Category C', value: 30 },
  ],
};

export const EtfGeographicExposure: React.FC<{ data?: EtfGeographicExposureData }> = ({ data = SAMPLE_DATA }) => {
  return <DonutChart04 {...data} />;
};