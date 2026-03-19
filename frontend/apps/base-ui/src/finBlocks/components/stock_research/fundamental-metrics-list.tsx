/**
 * Fundamental Metrics Comparison finBlock
 * Wraps: BarList01
 * Description: P/E, P/B, ROE, debt/equity, dividend yield ranked against peers
 */

import React from 'react';
import { BarList01 } from '../../../blocks/bar-lists/bar-list-01';

export interface FundamentalMetricsListData {
  data?: any[];
}

const SAMPLE_DATA: FundamentalMetricsListData = {
  data: [
    { name: 'Item 1', value: 50 },
    { name: 'Item 2', value: 40 },
    { name: 'Item 3', value: 30 },
  ],
};

export const FundamentalMetricsList: React.FC<{ data?: FundamentalMetricsListData }> = ({ data = SAMPLE_DATA }) => {
  return <BarList01 {...data} />;
};