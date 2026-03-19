/**
 * Balance Sheet Strength finBlock
 * Wraps: KpiCard03
 * Description: Current ratio, quick ratio, working capital metrics
 */

import React from 'react';
import { KpiCard03 } from '../../../blocks/kpi-cards/kpi-card-03';

export interface BalanceSheetHealthData {
  metrics?: Array<{ name: string; stat: number | string; change: string; changeType: 'positive' | 'negative' | 'neutral' }>;
  cols?: number;
}

const SAMPLE_DATA: BalanceSheetHealthData = {
  metrics: [
    { name: 'Metric 1', stat: 100, change: '+5%', changeType: 'positive' },
    { name: 'Metric 2', stat: 200, change: '-2%', changeType: 'negative' },
  ],
  cols: 2,
};

export const BalanceSheetHealth: React.FC<{ data?: BalanceSheetHealthData }> = ({ data = SAMPLE_DATA }) => {
  return <KpiCard03 {...data} />;
};