/**
 * Competitive Advantage Indicators finBlock
 * Wraps: BarList02
 * Description: Metrics suggesting durable competitive moat (pricing power, retention, uniqueness)
 */

import React from 'react';
import { BarList02 } from '../../../blocks/bar-lists/bar-list-02';

export interface CompetitiveMoatAnalysisData {
  data?: any[];
}

const SAMPLE_DATA: CompetitiveMoatAnalysisData = {
  data: [
    { name: 'Item 1', value: 50 },
    { name: 'Item 2', value: 40 },
    { name: 'Item 3', value: 30 },
  ],
};

export const CompetitiveMoatAnalysis: React.FC<{ data?: CompetitiveMoatAnalysisData }> = ({ data = SAMPLE_DATA }) => {
  return <BarList02 {...data} />;
};