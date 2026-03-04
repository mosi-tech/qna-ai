'use client';

import React from 'react';
import { Group } from '@visx/group';
import { Circle, Line } from '@visx/shape';
import { scaleLinear } from '@visx/scale';
import { AxisBottom, AxisLeft } from '@visx/axis';

interface SymmetryData {
  symbol: string;
  upDays: number;
  downDays: number;
}

interface SymmetryScatterChartProps {
  data: SymmetryData[];
  height: number;
}

export function SymmetryScatterChart({
  data,
  height = 300
}: SymmetryScatterChartProps) {
  const width = 400;
  const margin = { top: 20, right: 20, bottom: 50, left: 50 };
  const chartWidth = width - margin.left - margin.right;
  const chartHeight = height - margin.top - margin.bottom;

  const maxValue = Math.max(
    ...data.map(d => Math.max(d.upDays, d.downDays))
  ) * 1.1;

  const xScale = scaleLinear({
    range: [0, chartWidth],
    domain: [0, maxValue]
  });

  const yScale = scaleLinear({
    range: [chartHeight, 0],
    domain: [0, maxValue]
  });

  const getSymmetryColor = (upDays: number, downDays: number) => {
    const ratio = upDays / downDays;
    const distance = Math.abs(1 - ratio);
    if (distance < 0.1) return '#10B981'; // green - very symmetric
    if (distance < 0.2) return '#F59E0B'; // yellow - moderately symmetric
    return '#EF4444'; // red - asymmetric
  };

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
      <div className="px-6 py-4 border-b border-gray-100">
        <h3 className="text-lg font-semibold text-gray-900">
          Up vs Down Days Scatter
        </h3>
        <p className="text-sm text-gray-500 mt-1">
          Perfect symmetry falls on diagonal line
        </p>
      </div>
      
      <div className="p-6">
        <svg width="100%" height={height} viewBox={`0 0 ${width} ${height}`}>
          <Group left={margin.left} top={margin.top}>
            {/* Perfect symmetry diagonal line */}
            <Line
              from={{ x: 0, y: chartHeight }}
              to={{ x: chartWidth, y: 0 }}
              stroke="#E5E7EB"
              strokeWidth={2}
              strokeDasharray="5,5"
            />
            
            {/* Grid lines */}
            {[0.25, 0.5, 0.75, 1].map(factor => (
              <Group key={factor}>
                <Line
                  from={{ x: 0, y: yScale(maxValue * factor) }}
                  to={{ x: chartWidth, y: yScale(maxValue * factor) }}
                  stroke="#F3F4F6"
                  strokeWidth={1}
                />
                <Line
                  from={{ x: xScale(maxValue * factor), y: 0 }}
                  to={{ x: xScale(maxValue * factor), y: chartHeight }}
                  stroke="#F3F4F6"
                  strokeWidth={1}
                />
              </Group>
            ))}

            {/* Data points */}
            {data.map((d, i) => (
              <Circle
                key={d.symbol}
                cx={xScale(d.upDays)}
                cy={yScale(d.downDays)}
                r={8}
                fill={getSymmetryColor(d.upDays, d.downDays)}
                fillOpacity={0.8}
                stroke="#FFFFFF"
                strokeWidth={2}
                className="cursor-pointer hover:r-10 transition-all duration-200"
              />
            ))}

            {/* Symbol labels */}
            {data.map((d, i) => (
              <text
                key={`label-${d.symbol}`}
                x={xScale(d.upDays)}
                y={yScale(d.downDays) - 12}
                textAnchor="middle"
                fontSize={10}
                fill="#374151"
                fontWeight="600"
              >
                {d.symbol}
              </text>
            ))}

            {/* Axes */}
            <AxisBottom
              top={chartHeight}
              scale={xScale}
              stroke="#E5E7EB"
              tickStroke="#E5E7EB"
              numTicks={5}
              tickLabelProps={() => ({
                fill: '#6B7280',
                fontSize: 12,
                textAnchor: 'middle'
              })}
              label="Up Days"
              labelProps={{
                fill: '#374151',
                fontSize: 14,
                textAnchor: 'middle'
              }}
            />
            
            <AxisLeft
              scale={yScale}
              stroke="#E5E7EB"
              tickStroke="#E5E7EB"
              numTicks={5}
              tickLabelProps={() => ({
                fill: '#6B7280',
                fontSize: 12,
                textAnchor: 'end'
              })}
              label="Down Days"
              labelProps={{
                fill: '#374151',
                fontSize: 14,
                textAnchor: 'middle'
              }}
            />
          </Group>
        </svg>

        {/* Legend */}
        <div className="mt-4 flex justify-center space-x-6 text-xs">
          <div className="flex items-center space-x-1">
            <div className="w-3 h-3 rounded-full bg-green-500"></div>
            <span className="text-gray-600">Very Symmetric</span>
          </div>
          <div className="flex items-center space-x-1">
            <div className="w-3 h-3 rounded-full bg-yellow-500"></div>
            <span className="text-gray-600">Moderate</span>
          </div>
          <div className="flex items-center space-x-1">
            <div className="w-3 h-3 rounded-full bg-red-500"></div>
            <span className="text-gray-600">Asymmetric</span>
          </div>
        </div>
      </div>
    </div>
  );
}