/**
 * Stress Test Scenarios finBlock
 * Wraps: BarList07
 * Description: Portfolio impact under historical stress scenarios (2008, 2020, etc.)
 */

import React from 'react';
import { BarList07 } from '../../../blocks/bar-lists/bar-list-07';

export interface StressTestResultsData {
  data?: any[];
}

const SAMPLE_DATA: StressTestResultsData = {
  data: [
    { name: 'Item 1', value: 50 },
    { name: 'Item 2', value: 40 },
    { name: 'Item 3', value: 30 },
  ],
};

export const StressTestResults: React.FC<{ data?: StressTestResultsData }> = ({ data = SAMPLE_DATA }) => {
  return <BarList07 {...data} />;
};