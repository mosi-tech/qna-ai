/**
 * Beta & Systematic Risk finBlock
 * Wraps: KpiCard03
 * Description: Portfolio beta vs S&P 500, sensitivity to market movements
 */

import React from 'react';
import { KpiCard03 } from '../../../blocks/kpi-cards/kpi-card-03';

export interface BetaAnalysisData {
  metrics?: Array<{ name: string; stat: number | string; change: string; changeType: 'positive' | 'negative' | 'neutral' }>;
  cols?: number;
}

const SAMPLE_DATA: BetaAnalysisData = {
  metrics: [
    { name: 'Metric 1', stat: 100, change: '+5%', changeType: 'positive' },
    { name: 'Metric 2', stat: 200, change: '-2%', changeType: 'negative' },
  ],
  cols: 2,
};

export const BetaAnalysis: React.FC<{ data?: BetaAnalysisData }> = ({ data = SAMPLE_DATA }) => {
  return <KpiCard03 {...data} />;
};