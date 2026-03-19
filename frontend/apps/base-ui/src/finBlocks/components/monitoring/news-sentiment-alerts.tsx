/**
 * News & Sentiment Monitoring finBlock
 * Wraps: Table01
 * Description: Recent news and sentiment (bullish/bearish) for holdings
 */

import React from 'react';
import { Table01 } from '../../../blocks/tables/table-01';

export interface NewsSentimentAlertsData {
  rows?: any[];
  columns?: string[];
}

const SAMPLE_DATA: NewsSentimentAlertsData = {
  data: [],
  columns: [],
};

export const NewsSentimentAlerts: React.FC<{ data?: NewsSentimentAlertsData }> = ({ data = SAMPLE_DATA }) => {
  return <Table01 {...data} />;
};