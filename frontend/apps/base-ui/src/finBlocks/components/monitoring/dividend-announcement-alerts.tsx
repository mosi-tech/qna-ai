/**
 * Dividend Announcements finBlock
 * Wraps: Table01
 * Description: Recent dividend announcements, increases, cuts, suspensions
 */

import React from 'react';
import { Table01 } from '../../../blocks/tables/table-01';

export interface DividendAnnouncementAlertsData {
  rows?: any[];
  columns?: string[];
}

const SAMPLE_DATA: DividendAnnouncementAlertsData = {
  data: [],
  columns: [],
};

export const DividendAnnouncementAlerts: React.FC<{ data?: DividendAnnouncementAlertsData }> = ({ data = SAMPLE_DATA }) => {
  return <Table01 {...data} />;
};