/**
 * Price Alert Monitoring finBlock
 * Wraps: Table01
 * Description: Holdings with active price alerts (above/below target)
 */

import React from 'react';
import { Table01 } from '../../../blocks/tables/table-01';

export interface PriceAlertSetupData {
  rows?: any[];
  columns?: string[];
}

const SAMPLE_DATA: PriceAlertSetupData = {
  data: [],
  columns: [],
};

export const PriceAlertSetup: React.FC<{ data?: PriceAlertSetupData }> = ({ data = SAMPLE_DATA }) => {
  return <Table01 {...data} />;
};