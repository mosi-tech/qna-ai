/**
 * Technical Indicators Summary finBlock
 * Wraps: KpiCard03
 * Description: RSI, MACD, Bollinger Bands status - overbought/oversold signals
 */

import React from 'react';
import { KpiCard03 } from '../../../blocks/kpi-cards/kpi-card-03';

export interface TechnicalIndicatorsKpiData {
  metrics?: Array<{ name: string; stat: number | string; change: string; changeType: 'positive' | 'negative' | 'neutral' }>;
  cols?: number;
}

const SAMPLE_DATA: TechnicalIndicatorsKpiData = {
  metrics: [
    { name: 'Metric 1', stat: 100, change: '+5%', changeType: 'positive' },
    { name: 'Metric 2', stat: 200, change: '-2%', changeType: 'negative' },
  ],
  cols: 2,
};

export const TechnicalIndicatorsKpi: React.FC<{ data?: TechnicalIndicatorsKpiData }> = ({ data = SAMPLE_DATA }) => {
  return <KpiCard03 {...data} />;
};