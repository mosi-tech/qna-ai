/**
 * Win Rate & Consistency finBlock
 * Wraps: KpiCard01
 * Description: % positive months, best/worst month, average monthly return
 */

import React from 'react';
import { KpiCard01 } from '../../../blocks/kpi-cards/kpi-card-01';

export interface WinRateMetricsData {
  metrics?: Array<{ name: string; stat: number | string; change: string; changeType: 'positive' | 'negative' | 'neutral' }>;
  cols?: number;
}

const SAMPLE_DATA: WinRateMetricsData = {
  metrics: [
    { name: 'Metric 1', stat: 100, change: '+5%', changeType: 'positive' },
    { name: 'Metric 2', stat: 200, change: '-2%', changeType: 'negative' },
  ],
  cols: 2,
};

export const WinRateMetrics: React.FC<{ data?: WinRateMetricsData }> = ({ data = SAMPLE_DATA }) => {
  return <KpiCard01 {...data} />;
};