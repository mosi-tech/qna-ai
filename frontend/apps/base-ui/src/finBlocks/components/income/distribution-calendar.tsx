/**
 * Upcoming Dividend/Distribution Calendar finBlock
 * Wraps: Table01
 * Description: Next 90 days of ex-dates, record dates, and payment dates
 */

import React from 'react';
import { Table01 } from '../../../blocks/tables/table-01';

export interface DistributionCalendarData {
  rows?: any[];
  columns?: string[];
}

const SAMPLE_DATA: DistributionCalendarData = {
  data: [],
  columns: [],
};

export const DistributionCalendar: React.FC<{ data?: DistributionCalendarData }> = ({ data = SAMPLE_DATA }) => {
  return <Table01 {...data} />;
};