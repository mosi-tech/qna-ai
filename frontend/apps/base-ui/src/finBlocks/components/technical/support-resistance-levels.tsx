/**
 * Support & Resistance Levels finBlock
 * Wraps: Table01
 * Description: Key support and resistance prices for top holdings
 */

import React from 'react';
import { Table01 } from '../../../blocks/tables/table-01';

export interface SupportResistanceLevelsData {
  rows?: any[];
  columns?: string[];
}

const SAMPLE_DATA: SupportResistanceLevelsData = {
  data: [],
  columns: [],
};

export const SupportResistanceLevels: React.FC<{ data?: SupportResistanceLevelsData }> = ({ data = SAMPLE_DATA }) => {
  return <Table01 {...data} />;
};