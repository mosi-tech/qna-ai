/**
 * VaR Under Different Scenarios finBlock
 * Wraps: KpiCard02
 * Description: Value at Risk at different confidence levels (90%, 95%, 99%)
 */

import React from 'react';
import { KpiCard02 } from '../../../blocks/kpi-cards/kpi-card-02';

export interface VarByScenarioData {
  metrics?: Array<{ name: string; stat: number | string; change: string; changeType: 'positive' | 'negative' | 'neutral' }>;
  cols?: number;
}

const SAMPLE_DATA: VarByScenarioData = {
  metrics: [
    { name: 'Metric 1', stat: 100, change: '+5%', changeType: 'positive' },
    { name: 'Metric 2', stat: 200, change: '-2%', changeType: 'negative' },
  ],
  cols: 2,
};

export const VarByScenario: React.FC<{ data?: VarByScenarioData }> = ({ data = SAMPLE_DATA }) => {
  return <KpiCard02 {...data} />;
};