/**
 * Upcoming Earnings Dates finBlock
 * Wraps: Table01
 * Description: Next earnings announcements for portfolio holdings
 */

import React from 'react';
import { Table01 } from '../../../blocks/tables/table-01';

export interface EarningsCalendarData {
  rows?: any[];
  columns?: string[];
}

const SAMPLE_DATA: EarningsCalendarData = {
  data: [],
  columns: [],
};

export const EarningsCalendar: React.FC<{ data?: EarningsCalendarData }> = ({ data = SAMPLE_DATA }) => {
  return <Table01 {...data} />;
};