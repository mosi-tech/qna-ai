/**
 * Downside Risk (Sortino Ratio) finBlock
 * Wraps: KpiCard04
 * Description: Downside deviation vs full volatility, Sortino ratio
 */

import React from 'react';
import { KpiCard04 } from '../../../blocks/kpi-cards/kpi-card-04';

export interface DownsideRiskAnalysisData {
  metrics?: Array<{ name: string; stat: number | string; change: string; changeType: 'positive' | 'negative' | 'neutral' }>;
  cols?: number;
}

const SAMPLE_DATA: DownsideRiskAnalysisData = {
  metrics: [
    { name: 'Metric 1', stat: 100, change: '+5%', changeType: 'positive' },
    { name: 'Metric 2', stat: 200, change: '-2%', changeType: 'negative' },
  ],
  cols: 2,
};

export const DownsideRiskAnalysis: React.FC<{ data?: DownsideRiskAnalysisData }> = ({ data = SAMPLE_DATA }) => {
  return <KpiCard04 {...data} />;
};