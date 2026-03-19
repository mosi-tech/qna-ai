/**
 * Sector Rotation Signals finBlock
 * Wraps: KpiCard01
 * Description: Technical indicators (momentum, trend) for sector rotation
 */

import React from 'react';
import { KpiCard01 } from '../../../blocks/kpi-cards/kpi-card-01';

export interface SectorRotationSignalsData {
  metrics?: Array<{ name: string; stat: number | string; change: string; changeType: 'positive' | 'negative' | 'neutral' }>;
  cols?: number;
}

const SAMPLE_DATA: SectorRotationSignalsData = {
  metrics: [
    { name: 'Metric 1', stat: 100, change: '+5%', changeType: 'positive' },
    { name: 'Metric 2', stat: 200, change: '-2%', changeType: 'negative' },
  ],
  cols: 2,
};

export const SectorRotationSignals: React.FC<{ data?: SectorRotationSignalsData }> = ({ data = SAMPLE_DATA }) => {
  return <KpiCard01 {...data} />;
};