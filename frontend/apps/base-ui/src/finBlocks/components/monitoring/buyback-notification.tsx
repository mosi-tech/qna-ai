/**
 * Stock Buyback Announcements finBlock
 * Wraps: Table01
 * Description: Companies announcing or executing share buybacks
 */

import React from 'react';
import { Table01 } from '../../../blocks/tables/table-01';

export interface BuybackNotificationData {
  rows?: any[];
  columns?: string[];
}

const SAMPLE_DATA: BuybackNotificationData = {
  data: [],
  columns: [],
};

export const BuybackNotification: React.FC<{ data?: BuybackNotificationData }> = ({ data = SAMPLE_DATA }) => {
  return <Table01 {...data} />;
};