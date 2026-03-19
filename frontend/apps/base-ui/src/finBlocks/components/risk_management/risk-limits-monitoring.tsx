/**
 * Risk Limits Monitoring finBlock
 * Wraps: Table01
 * Description: Current vs target for VaR limit, volatility limit, concentration limit
 */

import React from 'react';
import { Table01 } from '../../../blocks/tables/table-01';

export interface RiskLimitsMonitoringData {
  rows?: any[];
  columns?: string[];
}

const SAMPLE_DATA: RiskLimitsMonitoringData = {
  data: [],
  columns: [],
};

export const RiskLimitsMonitoring: React.FC<{ data?: RiskLimitsMonitoringData }> = ({ data = SAMPLE_DATA }) => {
  return <Table01 {...data} />;
};