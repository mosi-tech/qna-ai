/**
 * Holdings Detail Table finBlock
 * Wraps: Table01
 * Description: Complete list of all holdings with symbol, shares, cost basis, current value, P&L, P&L %
 */

import React from 'react';
import { Table01 } from '../../../blocks/tables/table-01';

export interface HoldingsTableData {
  rows?: any[];
  columns?: string[];
}

const SAMPLE_DATA: HoldingsTableData = {
  data: [],
  columns: [],
};

export const HoldingsTable: React.FC<{ data?: HoldingsTableData }> = ({ data = SAMPLE_DATA }) => {
  return <Table01 {...data} />;
};