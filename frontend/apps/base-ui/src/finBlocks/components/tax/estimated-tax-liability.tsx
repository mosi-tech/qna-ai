/**
 * Estimated Tax Liability finBlock
 * Wraps: KpiCard01
 * Description: Unrealized gains and expected tax liability if liquidated
 */

import React from 'react';
import { KpiCard01 } from '../../../blocks/kpi-cards/kpi-card-01';

export interface EstimatedTaxLiabilityData {
  metrics?: Array<{ name: string; stat: number | string; change: string; changeType: 'positive' | 'negative' | 'neutral' }>;
  cols?: number;
}

const SAMPLE_DATA: EstimatedTaxLiabilityData = {
  metrics: [
    { name: 'Metric 1', stat: 100, change: '+5%', changeType: 'positive' },
    { name: 'Metric 2', stat: 200, change: '-2%', changeType: 'negative' },
  ],
  cols: 2,
};

export const EstimatedTaxLiability: React.FC<{ data?: EstimatedTaxLiabilityData }> = ({ data = SAMPLE_DATA }) => {
  return <KpiCard01 {...data} />;
};