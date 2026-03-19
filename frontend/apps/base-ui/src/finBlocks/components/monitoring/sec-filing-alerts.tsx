/**
 * SEC Filing Monitoring finBlock
 * Wraps: Table01
 * Description: Recent 10-K, 10-Q, 8-K filings for holdings
 */

import React from 'react';
import { Table01 } from '../../../blocks/tables/table-01';

export interface SecFilingAlertsData {
  rows?: any[];
  columns?: string[];
}

const SAMPLE_DATA: SecFilingAlertsData = {
  data: [],
  columns: [],
};

export const SecFilingAlerts: React.FC<{ data?: SecFilingAlertsData }> = ({ data = SAMPLE_DATA }) => {
  return <Table01 {...data} />;
};