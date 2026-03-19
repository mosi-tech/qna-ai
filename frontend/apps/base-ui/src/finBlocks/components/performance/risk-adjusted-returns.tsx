/**
 * Risk-Adjusted Return Metrics finBlock
 * Wraps: KpiCard02
 * Description: Sharpe ratio, Sortino ratio, Calmar ratio, information ratio
 */

import React from 'react';
import { KpiCard02 } from '../../../blocks/kpi-cards/kpi-card-02';

export interface RiskAdjustedReturnsData {
  metrics?: Array<{ name: string; stat: number | string; change: string; changeType: 'positive' | 'negative' | 'neutral' }>;
  cols?: number;
}

const SAMPLE_DATA: RiskAdjustedReturnsData = {
  metrics: [
    { name: 'Metric 1', stat: 100, change: '+5%', changeType: 'positive' },
    { name: 'Metric 2', stat: 200, change: '-2%', changeType: 'negative' },
  ],
  cols: 2,
};

export const RiskAdjustedReturns: React.FC<{ data?: RiskAdjustedReturnsData }> = ({ data = SAMPLE_DATA }) => {
  return <KpiCard02 {...data} />;
};