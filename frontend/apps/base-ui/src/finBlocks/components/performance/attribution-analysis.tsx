/**
 * Performance Attribution finBlock
 * Wraps: BarList08
 * Description: Breakdown of returns by holding - which positions drove performance
 */

import React from 'react';
import { BarList08 } from '../../../blocks/bar-lists/bar-list-08';

export interface AttributionAnalysisData {
  data?: any[];
}

const SAMPLE_DATA: AttributionAnalysisData = {
  data: [
    { name: 'Item 1', value: 50 },
    { name: 'Item 2', value: 40 },
    { name: 'Item 3', value: 30 },
  ],
};

export const AttributionAnalysis: React.FC<{ data?: AttributionAnalysisData }> = ({ data = SAMPLE_DATA }) => {
  return <BarList08 {...data} />;
};