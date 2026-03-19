/**
 * Portfolio Concentration Risk finBlock
 * Wraps: BarList02
 * Description: Top 10 holdings as % of portfolio - identifies concentration risk
 */

import React from 'react';
import { BarList02 } from '../../../blocks/bar-lists/bar-list-02';

export interface ConcentrationByHoldingData {
  data?: any[];
}

const SAMPLE_DATA: ConcentrationByHoldingData = {
  data: [
    { name: 'NVDA', value: 12.5 },
    { name: 'MSFT', value: 11.2 },
    { name: 'TSLA', value: 8.7 },
    { name: 'AAPL', value: 7.8 },
    { name: 'GOOGL', value: 6.4 },
    { name: 'AMZN', value: 5.9 },
    { name: 'META', value: 4.3 },
    { name: 'NFLX', value: 3.8 },
    { name: 'INTEL', value: 2.9 },
    { name: 'AMDOTHERS', value: 36.5 },
  ],
};

export const ConcentrationByHolding: React.FC<{ data?: ConcentrationByHoldingData }> = ({ data = SAMPLE_DATA }) => {
  return (
    <div className="space-y-4">
      <div>
        <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-50">
          Concentration by Holding
        </h2>
        <p className="text-sm text-gray-600 dark:text-gray-400">
          Top 10 holdings as percentage of portfolio - identifies concentration risk
        </p>
      </div>
      <BarList02 {...data} />
    </div>
  );
};