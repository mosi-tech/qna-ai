/**
 * Dividend-Paying Holdings finBlock
 * Wraps: Table01
 * Description: All dividend payers with symbol, yield, annual payment, next ex-date
 */

import React from 'react';
import { Table01 } from '../../../blocks/tables/table-01';

export interface DividendPayersTableData {
  rows?: any[];
  columns?: string[];
}

const SAMPLE_DATA: DividendPayersTableData = {
  data: [],
  columns: [],
};

export const DividendPayersTable: React.FC<{ data?: DividendPayersTableData }> = ({ data = SAMPLE_DATA }) => {
  return <Table01 {...data} />;
};