/**
 * Tax-Loss Harvesting Candidates finBlock
 * Wraps: Table01
 * Description: Holdings with unrealized losses available for tax-loss harvesting
 */

import React from 'react';
import { Table01 } from '../../../blocks/tables/table-01';

export interface TaxLossHarvestingOpportunitiesData {
  rows?: any[];
  columns?: string[];
}

const SAMPLE_DATA: TaxLossHarvestingOpportunitiesData = {
  data: [],
  columns: [],
};

export const TaxLossHarvestingOpportunities: React.FC<{ data?: TaxLossHarvestingOpportunitiesData }> = ({ data = SAMPLE_DATA }) => {
  return <Table01 {...data} />;
};