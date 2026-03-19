/**
 * Recent Trades and Turnover finBlock
 * Wraps: Table01
 * Description: Recent buy/sell activity and portfolio turnover rate
 */

import React from 'react';
import { Table01 } from '../../../blocks/tables/table-01';

export interface PortfolioTurnoverTableData {
  rows?: any[];
  columns?: string[];
}

const SAMPLE_DATA: PortfolioTurnoverTableData = {
  data: [],
  columns: [],
};

export const PortfolioTurnoverTable: React.FC<{ data?: PortfolioTurnoverTableData }> = ({ data = SAMPLE_DATA }) => {
  return <Table01 {...data} />;
};