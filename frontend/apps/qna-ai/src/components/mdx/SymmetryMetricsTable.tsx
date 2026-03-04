'use client';

import React from 'react';

interface Position {
  symbol: string;
  upDays: number;
  downDays: number;
  ratio: number;
  symmetryScore: number;
}

interface SymmetryMetricsTableProps {
  positions: Position[];
  sortBy: string;
}

export function SymmetryMetricsTable({
  positions,
  sortBy
}: SymmetryMetricsTableProps) {
  const sortedPositions = [...positions].sort((a, b) => {
    if (sortBy === 'symmetryScore') return b.symmetryScore - a.symmetryScore;
    if (sortBy === 'ratio') return Math.abs(1 - a.ratio) - Math.abs(1 - b.ratio);
    return 0;
  });

  const getSymmetryColor = (score: number) => {
    if (score >= 90) return 'text-green-600';
    if (score >= 80) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getSymmetryBg = (score: number) => {
    if (score >= 90) return 'bg-green-100';
    if (score >= 80) return 'bg-yellow-100';
    return 'bg-red-100';
  };

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
      <div className="px-6 py-4 border-b border-gray-100">
        <h3 className="text-lg font-semibold text-gray-900">
          Position Symmetry Rankings
        </h3>
        <p className="text-sm text-gray-500 mt-1">
          Most balanced up vs down day patterns
        </p>
      </div>
      
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="bg-gray-50">
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Symbol
              </th>
              <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase">
                Up Days
              </th>
              <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase">
                Down Days
              </th>
              <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase">
                Ratio
              </th>
              <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase">
                Symmetry
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {sortedPositions.map((position, index) => (
              <tr key={position.symbol} className="hover:bg-gray-50">
                <td className="px-4 py-4">
                  <div className="flex items-center">
                    <span className="text-sm font-medium text-gray-900">
                      {position.symbol}
                    </span>
                    <span className="ml-2 text-xs text-gray-500">
                      #{index + 1}
                    </span>
                  </div>
                </td>
                <td className="px-4 py-4 text-center text-sm text-green-600 font-medium">
                  {position.upDays}
                </td>
                <td className="px-4 py-4 text-center text-sm text-red-600 font-medium">
                  {position.downDays}
                </td>
                <td className="px-4 py-4 text-center">
                  <span className={`text-sm font-medium ${
                    Math.abs(1 - position.ratio) < 0.1 ? 'text-green-600' :
                    Math.abs(1 - position.ratio) < 0.2 ? 'text-yellow-600' : 'text-red-600'
                  }`}>
                    {position.ratio.toFixed(2)}
                  </span>
                </td>
                <td className="px-4 py-4 text-center">
                  <div className="flex items-center justify-center">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getSymmetryBg(position.symmetryScore)} ${getSymmetryColor(position.symmetryScore)}`}>
                      {position.symmetryScore.toFixed(0)}%
                    </span>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}