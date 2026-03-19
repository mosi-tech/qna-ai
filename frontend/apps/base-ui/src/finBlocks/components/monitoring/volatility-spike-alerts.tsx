/**
 * Volatility Spike Alerts finBlock
 * Wraps: BarList02
 * Description: Holdings with unusual volatility spikes or VIX alerts
 */

import React from 'react';
import { BarList02 } from '../../../blocks/bar-lists/bar-list-02';

export interface VolatilitySpikeAlertsData {
  data?: any[];
}

const SAMPLE_DATA: VolatilitySpikeAlertsData = {
  data: [
    { name: 'Item 1', value: 50 },
    { name: 'Item 2', value: 40 },
    { name: 'Item 3', value: 30 },
  ],
};

export const VolatilitySpikeAlerts: React.FC<{ data?: VolatilitySpikeAlertsData }> = ({ data = SAMPLE_DATA }) => {
  return <BarList02 {...data} />;
};