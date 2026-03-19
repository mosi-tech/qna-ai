/**
 * Upside/Downside Capture Ratios finBlock
 * Wraps: KpiCard03
 * Description: % of benchmark upside captured vs % of downside avoided
 */

import React from 'react';
import { KpiCard03 } from '../../../blocks/kpi-cards/kpi-card-03';

export interface UpsideDownsideCaptureData {
  metrics?: Array<{ name: string; stat: number | string; change: string; changeType: 'positive' | 'negative' | 'neutral' }>;
  cols?: number;
}

const SAMPLE_DATA: UpsideDownsideCaptureData = {
  metrics: [
    { name: 'Metric 1', stat: 100, change: '+5%', changeType: 'positive' },
    { name: 'Metric 2', stat: 200, change: '-2%', changeType: 'negative' },
  ],
  cols: 2,
};

export const UpsideDownsideCapture: React.FC<{ data?: UpsideDownsideCaptureData }> = ({ data = SAMPLE_DATA }) => {
  return <KpiCard03 {...data} />;
};