/**
 * Sector Analysis Template - Hydrated Example
 * Shows: Sector allocation (donut), performance by sector (bar), top holdings (list), sector details (table)
 */

import React from 'react';
import { DonutChart01 } from '../blocks/donut-charts';
import { BarChart01 } from '../blocks/bar-charts';
import { BarList01 } from '../blocks/bar-lists';
import { Table01 } from '../blocks/tables';

export interface SectorAnalysisData {
  sectorWeights: {
    data: Array<{ name: string; value: number }>;
  };
  sectorPerformance: {
    data: Array<{ [key: string]: any }>;
    categories: string[];
  };
  sectorComposition: {
    data: Array<{ name: string; value: number }>;
  };
  sectorStats: {
    rows: Array<{
      Sector: string;
      'Weight %': number;
      '1Y Return': number;
      'Holdings Count': number;
      'Avg P/E': number;
      'Dividend Yield': number;
    }>;
    columns: string[];
  };
}

const SAMPLE_DATA: SectorAnalysisData = {
  sectorWeights: {
    data: [
      { name: 'Technology', value: 35.8 },
      { name: 'Healthcare', value: 18.2 },
      { name: 'Financials', value: 14.5 },
      { name: 'Industrials', value: 12.3 },
      { name: 'Consumer Disc.', value: 10.2 },
      { name: 'Energy', value: 5.0 },
      { name: 'Utilities', value: 4.0 },
    ],
  },
  sectorPerformance: {
    data: [
      { date: '2025-03-31', Technology: 22.5, Healthcare: 15.2, Financials: 18.7, Industrials: 12.3, Energy: 8.5 },
      { date: '2025-06-30', Technology: 25.3, Healthcare: 16.8, Financials: 19.2, Industrials: 14.5, Energy: 11.2 },
      { date: '2025-09-30', Technology: 28.1, Healthcare: 18.2, Financials: 21.5, Industrials: 16.7, Energy: 13.8 },
      { date: '2025-12-31', Technology: 32.4, Healthcare: 19.8, Financials: 23.6, Industrials: 19.2, Energy: 16.5 },
      { date: '2026-03-19', Technology: 35.8, Healthcare: 21.4, Financials: 25.3, Industrials: 21.8, Energy: 19.2 },
    ],
    categories: ['Technology', 'Healthcare', 'Financials', 'Industrials', 'Energy'],
  },
  sectorComposition: {
    data: [
      { name: 'Technology: AAPL, MSFT, NVDA', value: 18500 },
      { name: 'Healthcare: UNH, JNJ', value: 12300 },
      { name: 'Financials: JPM, BAC', value: 9800 },
      { name: 'Industrials: BA, CAT', value: 8200 },
      { name: 'Consumer: AMZN, MCD', value: 6800 },
    ],
  },
  sectorStats: {
    rows: [
      { Sector: 'Technology', 'Weight %': 35.8, '1Y Return': 35.8, 'Holdings Count': 12, 'Avg P/E': 28.5, 'Dividend Yield': 1.2 },
      { Sector: 'Healthcare', 'Weight %': 18.2, '1Y Return': 21.4, 'Holdings Count': 8, 'Avg P/E': 22.3, 'Dividend Yield': 2.1 },
      { Sector: 'Financials', 'Weight %': 14.5, '1Y Return': 25.3, 'Holdings Count': 6, 'Avg P/E': 11.2, 'Dividend Yield': 3.5 },
      { Sector: 'Industrials', 'Weight %': 12.3, '1Y Return': 21.8, 'Holdings Count': 5, 'Avg P/E': 16.8, 'Dividend Yield': 2.3 },
      { Sector: 'Consumer Disc.', 'Weight %': 10.2, '1Y Return': 28.5, 'Holdings Count': 4, 'Avg P/E': 24.1, 'Dividend Yield': 0.8 },
      { Sector: 'Energy', 'Weight %': 5.0, '1Y Return': 19.2, 'Holdings Count': 2, 'Avg P/E': 8.5, 'Dividend Yield': 4.2 },
      { Sector: 'Utilities', 'Weight %': 4.0, '1Y Return': 12.3, 'Holdings Count': 2, 'Avg P/E': 19.2, 'Dividend Yield': 3.8 },
    ],
    columns: ['Sector', 'Weight %', '1Y Return', 'Holdings Count', 'Avg P/E', 'Dividend Yield'],
  },
};

export const SectorAnalysisTemplate: React.FC<{ data?: SectorAnalysisData }> = ({ data = SAMPLE_DATA }) => {
  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-50">Sector Analysis</h2>

      {/* Two-column top layout */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Sector Allocation */}
        <DonutChart01 title="Sector Allocation" data={data.sectorWeights.data} />

        {/* Sector Performance */}
        <BarChart01
          title="Sector Performance (1Y Return)"
          description="Annual returns by sector"
          data={data.sectorPerformance.data}
          indexField="date"
          defaultCategories={['Technology']}
          comparisonCategories={data.sectorPerformance.categories}
        />
      </div>

      {/* Top Holdings by Sector */}
      <BarList01 title="Top Holdings by Sector" subtitle="Market Value" data={data.sectorComposition.data} />

      {/* Detailed Sector Stats */}
      <Table01
        data={data.sectorStats.rows}
        columns={data.sectorStats.columns.map((name) => ({
          key: name,
          label: name,
          align: (name.includes('%') || name.includes('P/E') || name.includes('Yield') || name.includes('Count'))
            ? ('right' as const)
            : 'left',
        }))}
      />
    </div>
  );
};
