/**
 * Stock Price & Key Metrics finBlock
 * Wraps: KpiCard01
 * Description: Current price, market cap, P/E ratio, dividend yield, 52-week range
 */

import React from 'react';
import { KpiCard01 } from '../../../blocks/kpi-cards/kpi-card-01';

export interface StockPriceKpiData {
  metrics?: Array<{ name: string; stat: number | string; change: string; changeType: 'positive' | 'negative' | 'neutral' }>;
  cols?: number;
}

const SAMPLE_DATA: StockPriceKpiData = {
  metrics: [
    { name: 'Metric 1', stat: 100, change: '+5%', changeType: 'positive' },
    { name: 'Metric 2', stat: 200, change: '-2%', changeType: 'negative' },
  ],
  cols: 2,
};

export const StockPriceKpi: React.FC<{ data?: StockPriceKpiData }> = ({ data = SAMPLE_DATA }) => {
  return <KpiCard01 {...data} />;
};