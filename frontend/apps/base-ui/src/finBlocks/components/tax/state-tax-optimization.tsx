/**
 * State Tax Efficiency finBlock
 * Wraps: KpiCard02
 * Description: Tax implications if moving to different state (state income tax)
 */

import React from 'react';
import { KpiCard02 } from '../../../blocks/kpi-cards/kpi-card-02';

export interface StateTaxOptimizationData {
  metrics?: Array<{ name: string; stat: number | string; change: string; changeType: 'positive' | 'negative' | 'neutral' }>;
  cols?: number;
}

const SAMPLE_DATA: StateTaxOptimizationData = {
  metrics: [
    { name: 'Metric 1', stat: 100, change: '+5%', changeType: 'positive' },
    { name: 'Metric 2', stat: 200, change: '-2%', changeType: 'negative' },
  ],
  cols: 2,
};

export const StateTaxOptimization: React.FC<{ data?: StateTaxOptimizationData }> = ({ data = SAMPLE_DATA }) => {
  return <KpiCard02 {...data} />;
};