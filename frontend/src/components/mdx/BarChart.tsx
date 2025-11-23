'use client';

import React from 'react';
import { Group } from '@visx/group';
import { Bar } from '@visx/shape';
import { scaleLinear, scaleBand } from '@visx/scale';
import { AxisLeft, AxisBottom } from '@visx/axis';

interface BarChartProps {
  data: Record<string, any>[];
  xField: string;
  yField: string;
  title: string;
  color?: string;
}

export function BarChart({
  data,
  xField,
  yField,
  title,
  color = '#3B82F6'
}: BarChartProps) {
  const width = 500;
  const height = 300;
  const margin = { top: 20, right: 30, bottom: 50, left: 50 };
  const chartWidth = width - margin.left - margin.right;
  const chartHeight = height - margin.top - margin.bottom;

  if (!data.length) return null;

  // Extract values
  const yValues = data.map(d => Number(d[yField]));
  const maxY = Math.max(...yValues);

  const xScale = scaleBand({
    range: [0, chartWidth],
    domain: data.map(d => String(d[xField])),
    padding: 0.3
  });

  const yScale = scaleLinear({
    range: [chartHeight, 0],
    domain: [0, maxY * 1.1],
    nice: true
  });

  // Dynamic color based on data context
  const getBarColor = (value: any, index: number) => {
    // For symmetry ranges, color based on closeness to 1.0
    if (xField.toLowerCase().includes('range') && String(value).includes('-')) {
      const range = String(value);
      if (range.includes('0.9-1.1')) return '#10B981'; // Green for perfect symmetry range
      if (range.includes('0.7-0.9') || range.includes('1.1-1.3')) return '#F59E0B'; // Yellow for moderate
      return '#EF4444'; // Red for poor symmetry
    }
    
    return color;
  };

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
      <div className="px-6 py-4 border-b border-gray-100">
        <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
      </div>
      
      <div className="p-6">
        <svg width="100%" height={height} viewBox={`0 0 ${width} ${height}`}>
          <Group left={margin.left} top={margin.top}>
            {/* Bars */}
            {data.map((d, i) => {
              const xVal = String(d[xField]);
              const yVal = Number(d[yField]);
              const barHeight = chartHeight - yScale(yVal);
              const barWidth = xScale.bandwidth();
              const barX = xScale(xVal);
              const barY = yScale(yVal);

              return (
                <Group key={i}>
                  <Bar
                    x={barX}
                    y={barY}
                    width={barWidth}
                    height={barHeight}
                    fill={getBarColor(d[xField], i)}
                    fillOpacity={0.8}
                    className="hover:fill-opacity-100 transition-all duration-200"
                  />
                  {/* Value labels on top of bars */}
                  {yVal > 0 && (
                    <text
                      x={(barX || 0) + barWidth / 2}
                      y={(barY || 0) - 5}
                      textAnchor="middle"
                      fontSize={12}
                      fill="#374151"
                      fontWeight="600"
                    >
                      {yVal}
                    </text>
                  )}
                </Group>
              );
            })}

            {/* Reference line for symmetry analysis */}
            {xField.toLowerCase().includes('range') && (
              <line
                x1={xScale('0.9-1.1') || 0}
                x2={(xScale('0.9-1.1') || 0) + (xScale.bandwidth() || 0)}
                y1={chartHeight + 15}
                y2={chartHeight + 15}
                stroke="#10B981"
                strokeWidth={3}
              />
            )}

            {/* Axes */}
            <AxisBottom
              top={chartHeight}
              scale={xScale}
              stroke="#E5E7EB"
              tickStroke="#E5E7EB"
              tickLabelProps={() => ({
                fill: '#6B7280',
                fontSize: 10,
                textAnchor: 'middle'
              })}
              label={xField}
              labelProps={{
                fill: '#374151',
                fontSize: 12,
                textAnchor: 'middle'
              }}
            />
            
            <AxisLeft
              scale={yScale}
              stroke="#E5E7EB"
              tickStroke="#E5E7EB"
              tickLabelProps={() => ({
                fill: '#6B7280',
                fontSize: 10,
                textAnchor: 'end'
              })}
              label={yField}
              labelProps={{
                fill: '#374151',
                fontSize: 12,
                textAnchor: 'middle'
              }}
            />
          </Group>
        </svg>

        {/* Legend for symmetry ranges */}
        {xField.toLowerCase().includes('range') && (
          <div className="mt-4 flex justify-center space-x-4 text-xs">
            <div className="flex items-center space-x-1">
              <div className="w-3 h-2 bg-green-500"></div>
              <span className="text-gray-600">Perfect Symmetry</span>
            </div>
            <div className="flex items-center space-x-1">
              <div className="w-3 h-2 bg-yellow-500"></div>
              <span className="text-gray-600">Moderate</span>
            </div>
            <div className="flex items-center space-x-1">
              <div className="w-3 h-2 bg-red-500"></div>
              <span className="text-gray-600">Poor Symmetry</span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}