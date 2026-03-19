/**
 * Analyst Rating Changes finBlock
 * Wraps: Table01
 * Description: Recent analyst upgrades/downgrades for holdings
 */

import React from 'react';
import { Table01 } from '../../../blocks/tables/table-01';

export interface RatingDowngradeAlertsData {
  rows?: any[];
  columns?: string[];
}

const SAMPLE_DATA: RatingDowngradeAlertsData = {
  data: [],
  columns: [],
};

export const RatingDowngradeAlerts: React.FC<{ data?: RatingDowngradeAlertsData }> = ({ data = SAMPLE_DATA }) => {
  return <Table01 {...data} />;
};