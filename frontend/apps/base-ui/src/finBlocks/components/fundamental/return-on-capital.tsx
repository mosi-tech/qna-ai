/**
 * Return on Capital (ROIC/ROE/ROA) finBlock
 * Wraps: KpiCard02
 * Description: Capital efficiency metrics showing how well company uses capital
 */

import React from 'react';
import { KpiCard02 } from '../../../blocks/kpi-cards/kpi-card-02';

export interface ReturnOnCapitalData {
  metrics?: Array<{ name: string; stat: number | string; change: string; changeType: 'positive' | 'negative' | 'neutral' }>;
  cols?: number;
}

const SAMPLE_DATA: ReturnOnCapitalData = {
  metrics: [
    { name: 'Metric 1', stat: 100, change: '+5%', changeType: 'positive' },
    { name: 'Metric 2', stat: 200, change: '-2%', changeType: 'negative' },
  ],
  cols: 2,
};

export const ReturnOnCapital: React.FC<{ data?: ReturnOnCapitalData }> = ({ data = SAMPLE_DATA }) => {
  return <KpiCard02 {...data} />;
};