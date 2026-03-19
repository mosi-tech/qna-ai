/**
 * Quarterly Estimated Tax Payments finBlock
 * Wraps: Table01
 * Description: Expected quarterly tax payments based on dividend and capital gains
 */

import React from 'react';
import { Table01 } from '../../../blocks/tables/table-01';

export interface QuarterlyEstimatedTaxesData {
  rows?: any[];
  columns?: string[];
}

const SAMPLE_DATA: QuarterlyEstimatedTaxesData = {
  data: [],
  columns: [],
};

export const QuarterlyEstimatedTaxes: React.FC<{ data?: QuarterlyEstimatedTaxesData }> = ({ data = SAMPLE_DATA }) => {
  return <Table01 {...data} />;
};