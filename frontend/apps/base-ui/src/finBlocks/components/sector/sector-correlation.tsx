/**
 * Sector Correlation Analysis finBlock
 * Wraps: Heatmap01
 * Description: How sectors move together - diversification within sectors
 */

import React from 'react';
import { Heatmap01 } from '../../../blocks/heatmaps/heatmap-01';

export interface SectorCorrelationData {
  data?: number[][];
  labels?: string[];
}

const SAMPLE_DATA: SectorCorrelationData = {
  data: [[0.5, 0.3], [0.3, 0.5]],
  labels: ['A', 'B'],
};

export const SectorCorrelation: React.FC<{ data?: SectorCorrelationData }> = ({ data = SAMPLE_DATA }) => {
  return <Heatmap01 {...data} />;
};