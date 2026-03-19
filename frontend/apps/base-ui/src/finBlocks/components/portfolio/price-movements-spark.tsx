/**
 * Top Holdings Recent Price Action finBlock
 * Wraps: SparkChart01
 * Description: Last 2 weeks of price movements for top 5-10 holdings with sparklines
 */

import React from 'react';
import { SparkChart01 } from '../../../blocks/spark-charts/spark-chart-01';

export interface PriceMovementsSparkData {
  data?: any[];
  items?: any[];
}

const SAMPLE_DATA: PriceMovementsSparkData = {
  data: [],
  items: [],
};

export const PriceMovementsSpark: React.FC<{ data?: PriceMovementsSparkData }> = ({ data = SAMPLE_DATA }) => {
  return <SparkChart01 {...data} />;
};