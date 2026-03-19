/**
 * Cost Basis Summary finBlock
 * Wraps: Table01
 * Description: Aggregate cost basis, current value, unrealized gains/losses
 */

import React from 'react';
import { Table01 } from '../../../blocks/tables/table-01';

export interface CostBasisAnalysisData {
  rows?: any[];
  columns?: string[];
}

const SAMPLE_DATA: CostBasisAnalysisData = {
  data: [],
  columns: [],
};

export const CostBasisAnalysis: React.FC<{ data?: CostBasisAnalysisData }> = ({ data = SAMPLE_DATA }) => {
  return <Table01 {...data} />;
};