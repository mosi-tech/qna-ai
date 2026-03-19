/**
 * Risk Metrics Summary finBlock
 * Wraps: KpiCard01
 * Description: VaR (95%), Volatility (annual), Max Drawdown, Beta, Sharpe ratio
 */

import React from 'react';
import { KpiCard01 } from '../../../blocks/kpi-cards/kpi-card-01';

export interface RiskMetricsKpiData {
  metrics?: Array<{ name: string; stat: number | string; change: string; changeType: 'positive' | 'negative' | 'neutral' }>;
  cols?: number;
}

const SAMPLE_DATA: RiskMetricsKpiData = {
  metrics: [
    { name: 'Metric 1', stat: 100, change: '+5%', changeType: 'positive' },
    { name: 'Metric 2', stat: 200, change: '-2%', changeType: 'negative' },
  ],
  cols: 2,
};

export const RiskMetricsKpi: React.FC<{ data?: RiskMetricsKpiData }> = ({ data = SAMPLE_DATA }) => {
  return <KpiCard01 {...data} />;
};