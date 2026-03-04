'use client';

import React from 'react';

interface MetricsTableProps {
  data: Record<string, any>[];
  columns: string[];
  title: string;
  sortBy?: string;
}

export function MetricsTable({
  data,
  columns,
  title,
  sortBy
}: MetricsTableProps) {
  // Sort data if sortBy is specified
  const sortedData = React.useMemo(() => {
    if (!sortBy || !data.length) return data;
    
    return [...data].sort((a, b) => {
      const aVal = a[sortBy];
      const bVal = b[sortBy];
      
      // Handle string percentage values like "96%"
      if (typeof aVal === 'string' && aVal.includes('%')) {
        const aNum = parseFloat(aVal.replace('%', ''));
        const bNum = parseFloat(bVal.replace('%', ''));
        return bNum - aNum; // Descending order for percentages
      }
      
      // Handle numeric values
      if (typeof aVal === 'number' && typeof bVal === 'number') {
        return bVal - aVal; // Descending order
      }
      
      // Handle string values
      return String(aVal).localeCompare(String(bVal));
    });
  }, [data, sortBy]);

  const getCellValue = (row: Record<string, any>, column: string) => {
    const value = row[column];
    
    // Handle percentage styling
    if (typeof value === 'string' && value.includes('%')) {
      const numValue = parseFloat(value.replace('%', ''));
      const colorClass = numValue >= 90 ? 'text-green-600' : 
                        numValue >= 80 ? 'text-yellow-600' : 'text-red-600';
      return <span className={`font-medium ${colorClass}`}>{value}</span>;
    }
    
    // Handle ratio styling
    if (typeof value === 'number' && column.toLowerCase().includes('ratio')) {
      const distance = Math.abs(1 - value);
      const colorClass = distance < 0.1 ? 'text-green-600' :
                        distance < 0.2 ? 'text-yellow-600' : 'text-red-600';
      return <span className={`font-medium ${colorClass}`}>{value.toFixed(2)}</span>;
    }
    
    // Handle up/down day counts
    if (column.toLowerCase().includes('up')) {
      return <span className="text-green-600 font-medium">{value}</span>;
    }
    
    if (column.toLowerCase().includes('down')) {
      return <span className="text-red-600 font-medium">{value}</span>;
    }
    
    // Default rendering
    if (column === 'Symbol' || column === 'symbol') {
      return <span className="font-semibold text-gray-900">{value}</span>;
    }
    
    return value;
  };

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
      <div className="px-6 py-4 border-b border-gray-100">
        <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
        {sortBy && (
          <p className="text-sm text-gray-500 mt-1">Sorted by {sortBy}</p>
        )}
      </div>
      
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="bg-gray-50">
              {columns.map((column) => (
                <th
                  key={column}
                  className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                >
                  {column}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {sortedData.map((row, index) => (
              <tr key={index} className="hover:bg-gray-50">
                {columns.map((column) => (
                  <td key={column} className="px-4 py-4 whitespace-nowrap text-sm">
                    {getCellValue(row, column)}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}