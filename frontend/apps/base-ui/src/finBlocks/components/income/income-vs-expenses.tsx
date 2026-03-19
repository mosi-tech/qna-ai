/**
 * Income vs Withdrawal Needs finBlock
 * Wraps: BarChart12
 * Description: Annual dividend income vs target withdrawal for retirement
 */

import React from 'react';
import { BarChart12 } from '../../../blocks/bar-charts/bar-chart-12';

export interface IncomeVsExpensesData {
  data?: any[];
  categories?: string[];
}

const SAMPLE_DATA: IncomeVsExpensesData = {
  data: [
    { date: '2024-01-01', value: 100 },
    { date: '2024-01-02', value: 120 },
    { date: '2024-01-03', value: 110 },
  ],
  categories: ['value'],
};

export const IncomeVsExpenses: React.FC<{ data?: IncomeVsExpensesData }> = ({ data = SAMPLE_DATA }) => {
  return <BarChart12 {...data} />;
};