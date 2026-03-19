/**
 * Valuation vs Sector & Market finBlock
 * Wraps: BarChart03
 * Description: Compare stock P/E, P/B, dividend yield to sector average and S&P 500
 */

import React from 'react';
import { BarChart03 } from '../../../blocks/bar-charts/bar-chart-03';

export interface ValuationComparisonData {
  data?: any[];
  categories?: string[];
}

const SAMPLE_DATA: ValuationComparisonData = {
  data: [
    { date: '2024-01-01', value: 100 },
    { date: '2024-01-02', value: 120 },
    { date: '2024-01-03', value: 110 },
  ],
  categories: ['value'],
};

export const ValuationComparison: React.FC<{ data?: ValuationComparisonData }> = ({ data = SAMPLE_DATA }) => {
  return <BarChart03 {...data} />;
};