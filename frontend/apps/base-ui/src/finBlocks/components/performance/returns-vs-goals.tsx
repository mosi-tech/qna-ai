/**
 * Returns vs Investment Goals finBlock
 * Wraps: BarChart09
 * Description: Current return rate vs target for retirement/goals
 */

import React from 'react';
import { BarChart09 } from '../../../blocks/bar-charts/bar-chart-09';

export interface ReturnsVsGoalsData {
  data?: any[];
  categories?: string[];
}

const SAMPLE_DATA: ReturnsVsGoalsData = {
  data: [
    { date: '2024-01-01', value: 100 },
    { date: '2024-01-02', value: 120 },
    { date: '2024-01-03', value: 110 },
  ],
  categories: ['value'],
};

export const ReturnsVsGoals: React.FC<{ data?: ReturnsVsGoalsData }> = ({ data = SAMPLE_DATA }) => {
  return <BarChart09 {...data} />;
};