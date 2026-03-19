/**
 * Holdings by Sector finBlock
 * Wraps: Table01
 * Description: All holdings organized by sector with allocation and performance
 */

import React from 'react';
import { Table01 } from '../../../blocks/tables/table-01';

export interface SectorHoldingsTableData {
  rows?: any[];
  columns?: string[];
}

const SAMPLE_DATA: SectorHoldingsTableData = {
  data: [],
  columns: [],
};

export const SectorHoldingsTable: React.FC<{ data?: SectorHoldingsTableData }> = ({ data = SAMPLE_DATA }) => {
  return <Table01 {...data} />;
};