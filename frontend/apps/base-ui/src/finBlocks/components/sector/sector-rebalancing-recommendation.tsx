/**
 * Sector Rebalancing Opportunities finBlock
 * Wraps: BarList02
 * Description: Sectors over/underweight vs target allocation
 */

import React from 'react';
import { BarList02 } from '../../../blocks/bar-lists/bar-list-02';

export interface SectorRebalancingRecommendationData {
  data?: any[];
}

const SAMPLE_DATA: SectorRebalancingRecommendationData = {
  data: [
    { name: 'Item 1', value: 50 },
    { name: 'Item 2', value: 40 },
    { name: 'Item 3', value: 30 },
  ],
};

export const SectorRebalancingRecommendation: React.FC<{ data?: SectorRebalancingRecommendationData }> = ({ data = SAMPLE_DATA }) => {
  return <BarList02 {...data} />;
};