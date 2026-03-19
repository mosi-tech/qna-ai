/**
 * ETF Tax Efficiency finBlock
 * Wraps: KpiCard03
 * Description: Distribution yield vs SEC yield, tracking error, tax loss harvesting potential
 */

import React from 'react';
import { KpiCard03 } from '../../../blocks/kpi-cards/kpi-card-03';

export interface EtfTaxEfficiencyData {
  metrics?: Array<{ name: string; stat: number | string; change: string; changeType: 'positive' | 'negative' | 'neutral' }>;
  cols?: number;
}

const SAMPLE_DATA: EtfTaxEfficiencyData = {
  metrics: [
    { name: 'Metric 1', stat: 100, change: '+5%', changeType: 'positive' },
    { name: 'Metric 2', stat: 200, change: '-2%', changeType: 'negative' },
  ],
  cols: 2,
};

export const EtfTaxEfficiency: React.FC<{ data?: EtfTaxEfficiencyData }> = ({ data = SAMPLE_DATA }) => {
  return <KpiCard03 {...data} />;
};