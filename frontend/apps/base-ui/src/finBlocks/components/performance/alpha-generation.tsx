/**
 * Alpha Generation Analysis finBlock
 * Wraps: KpiCard04
 * Description: Excess return (alpha) vs benchmark with statistical significance
 */

import React from 'react';
import { KpiCard04 } from '../../../blocks/kpi-cards/kpi-card-04';

export interface AlphaGenerationData {
  metrics?: Array<{ name: string; stat: number | string; change: string; changeType: 'positive' | 'negative' | 'neutral' }>;
  cols?: number;
}

const SAMPLE_DATA: AlphaGenerationData = {
  metrics: [
    { name: 'Metric 1', stat: 100, change: '+5%', changeType: 'positive' },
    { name: 'Metric 2', stat: 200, change: '-2%', changeType: 'negative' },
  ],
  cols: 2,
};

export const AlphaGeneration: React.FC<{ data?: AlphaGenerationData }> = ({ data = SAMPLE_DATA }) => {
  return <KpiCard04 {...data} />;
};