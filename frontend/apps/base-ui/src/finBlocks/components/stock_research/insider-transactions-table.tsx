/**
 * Insider Buying/Selling Activity finBlock
 * Wraps: Table01
 * Description: Recent insider transactions and net ownership changes
 */

import React from 'react';
import { Table01 } from '../../../blocks/tables/table-01';

export interface InsiderTransactionsTableData {
  rows?: any[];
  columns?: string[];
}

const SAMPLE_DATA: InsiderTransactionsTableData = {
  data: [],
  columns: [],
};

export const InsiderTransactionsTable: React.FC<{ data?: InsiderTransactionsTableData }> = ({ data = SAMPLE_DATA }) => {
  return <Table01 {...data} />;
};