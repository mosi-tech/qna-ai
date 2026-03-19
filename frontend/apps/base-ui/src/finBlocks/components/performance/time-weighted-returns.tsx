/**
 * Time-Weighted vs Money-Weighted Returns finBlock
 * Wraps: KpiCard01
 * Description: TWR (manager performance) vs MWR (investor returns) comparison
 */

import React from 'react';
import { KpiCard01 } from '../../../blocks/kpi-cards/kpi-card-01';

export interface TimeWeightedReturnsData {
  metrics?: Array<{ name: string; stat: number | string; change: string; changeType: 'positive' | 'negative' | 'neutral' }>;
  cols?: number;
}

const SAMPLE_DATA: TimeWeightedReturnsData = {
  metrics: [
    { name: 'Metric 1', stat: 100, change: '+5%', changeType: 'positive' },
    { name: 'Metric 2', stat: 200, change: '-2%', changeType: 'negative' },
  ],
  cols: 2,
};

export const TimeWeightedReturns: React.FC<{ data?: TimeWeightedReturnsData }> = ({ data = SAMPLE_DATA }) => {
  return <KpiCard01 {...data} />;
};