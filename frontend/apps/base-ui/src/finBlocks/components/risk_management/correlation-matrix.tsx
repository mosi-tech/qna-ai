/**
 * Correlation Matrix finBlock
 * Wraps: Heatmap01
 * Description: Correlation between top holdings showing diversification benefits
 */

import React from 'react';
import { Heatmap01 } from '../../../blocks/heatmaps/heatmap-01';

export interface CorrelationMatrixData {
  data?: number[][];
  labels?: string[];
}

const SAMPLE_DATA: CorrelationMatrixData = {
  data: [[0.5, 0.3], [0.3, 0.5]],
  labels: ['A', 'B'],
};

export const CorrelationMatrix: React.FC<{ data?: CorrelationMatrixData }> = ({ data = SAMPLE_DATA }) => {
  return <Heatmap01 {...data} />;
};