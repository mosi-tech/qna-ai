/**
 * Quarterly Earnings History finBlock
 * Wraps: Table01
 * Description: Last 8 quarters of revenue, EPS, earnings beat/miss
 */

import React from 'react';
import { Table01 } from '../../../blocks/tables/table-01';

export interface EarningsHistoryTableData {
  rows?: any[];
  columns?: string[];
}

const SAMPLE_DATA: EarningsHistoryTableData = {
  data: [],
  columns: [],
};

export const EarningsHistoryTable: React.FC<{ data?: EarningsHistoryTableData }> = ({ data = SAMPLE_DATA }) => {
  return <Table01 {...data} />;
};