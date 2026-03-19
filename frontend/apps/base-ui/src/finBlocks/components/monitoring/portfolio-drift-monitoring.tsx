/**
 * Portfolio Drift from Target finBlock
 * Wraps: BarList01
 * Description: Holdings that have drifted from target allocation requiring rebalancing
 */

import React from 'react';
import { BarList01 } from '../../../blocks/bar-lists/bar-list-01';

export interface PortfolioDriftMonitoringData {
  data?: any[];
}

const SAMPLE_DATA: PortfolioDriftMonitoringData = {
  data: [
    { name: 'Item 1', value: 50 },
    { name: 'Item 2', value: 40 },
    { name: 'Item 3', value: 30 },
  ],
};

export const PortfolioDriftMonitoring: React.FC<{ data?: PortfolioDriftMonitoringData }> = ({ data = SAMPLE_DATA }) => {
  return <BarList01 {...data} />;
};