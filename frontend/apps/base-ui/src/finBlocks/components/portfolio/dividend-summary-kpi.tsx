/**
 * Portfolio Dividend Metrics finBlock
 * Wraps: KpiCard02
 * Description: Annual dividend income, yield, next ex-dividend date
 */

import React from 'react';
import { KpiCard02 } from '../../../blocks/kpi-cards/kpi-card-02';

export interface DividendSummaryKpiData {
  metrics?: Array<{ name: string; stat: number | string; change: string; changeType: 'positive' | 'negative' | 'neutral' }>;
  cols?: number;
}

const SAMPLE_DATA: DividendSummaryKpiData = {
  metrics: [
    { name: 'Metric 1', stat: 100, change: '+5%', changeType: 'positive' },
    { name: 'Metric 2', stat: 200, change: '-2%', changeType: 'negative' },
  ],
  cols: 2,
};

export const DividendSummaryKpi: React.FC<{ data?: DividendSummaryKpiData }> = ({ data = SAMPLE_DATA }) => {
  return <KpiCard02 {...data} />;
};