/**
 * ETF Comparison Metrics finBlock
 * Wraps: Table01
 * Description: Compare expense ratio, AUM, dividend yield, 1Y/3Y/5Y returns across ETFs
 */

import React from 'react';
import { Table01 } from '../../../blocks/tables/table-01';

export interface EtfComparisonMetricsData {
  rows?: any[];
  columns?: string[];
}

const SAMPLE_DATA: EtfComparisonMetricsData = {
  data: [],
  columns: [],
};

export const EtfComparisonMetrics: React.FC<{ data?: EtfComparisonMetricsData }> = ({ data = SAMPLE_DATA }) => {
  return <Table01 {...data} />;
};