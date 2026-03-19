/**
 * Moving Average Signals finBlock
 * Wraps: Table01
 * Description: Price above/below 50/200 day moving averages for each holding
 */

import React from 'react';
import { Table01 } from '../../../blocks/tables/table-01';

export interface MovingAverageCrossoverData {
  rows?: any[];
  columns?: string[];
}

const SAMPLE_DATA: MovingAverageCrossoverData = {
  data: [],
  columns: [],
};

export const MovingAverageCrossover: React.FC<{ data?: MovingAverageCrossoverData }> = ({ data = SAMPLE_DATA }) => {
  return <Table01 {...data} />;
};