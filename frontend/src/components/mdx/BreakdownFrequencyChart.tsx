'use client';

import React from 'react';
import { Group } from '@visx/group';
import { Bar } from '@visx/shape';
import { scaleLinear, scaleBand } from '@visx/scale';
import { AxisLeft, AxisBottom } from '@visx/axis';

interface BreakdownData {
  symbol: string;
  count: number;
}

interface BreakdownFrequencyChartProps {
  data: BreakdownData[];
  period: string;
  height: number;
}

export function BreakdownFrequencyChart({
  data,
  period,
  height = 400
}: BreakdownFrequencyChartProps) {
  const width = 600;
  const margin = { top: 20, right: 30, bottom: 60, left: 60 };
  const chartWidth = width - margin.left - margin.right;
  const chartHeight = height - margin.top - margin.bottom;

  // Scales
  const xScale = scaleBand({
    range: [0, chartWidth],
    domain: data.map(d => d.symbol),
    padding: 0.3
  });

  const yScale = scaleLinear({
    range: [chartHeight, 0],
    domain: [0, Math.max(...data.map(d => d.count)) * 1.1],
    nice: true
  });

  return (
    <div className="w-full bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
      <div className="px-6 py-4 border-b border-gray-100">
        <h3 className="text-lg font-semibold text-gray-900">
          Breakdown Frequency Distribution
        </h3>
        <p className="text-sm text-gray-500 mt-1">
          Failed breakdowns by symbol over {period}
        </p>
      </div>
      
      <div className="p-6">
        <svg width="100%" height={height} viewBox={`0 0 ${width} ${height}`}>
          <Group left={margin.left} top={margin.top}>
            {/* Bars */}
            {data.map((d, i) => {
              const barHeight = chartHeight - yScale(d.count);
              const barWidth = xScale.bandwidth();
              const barX = xScale(d.symbol);
              const barY = yScale(d.count);

              return (
                <Group key={`bar-${d.symbol}`}>
                  <Bar
                    x={barX}
                    y={barY}
                    width={barWidth}
                    height={barHeight}
                    fill="#EF4444"
                    fillOpacity={0.8}
                    className="hover:fill-opacity-100 transition-all duration-200"
                  />
                  {/* Value labels on top of bars */}
                  <text
                    x={(barX || 0) + barWidth / 2}
                    y={(barY || 0) - 5}
                    textAnchor="middle"
                    fontSize={12}
                    fill="#374151"
                    fontWeight="600"
                  >
                    {d.count}
                  </text>
                </Group>
              );
            })}

            {/* Axes */}
            <AxisBottom
              top={chartHeight}
              scale={xScale}
              stroke="#E5E7EB"
              tickStroke="#E5E7EB"
              tickLabelProps={() => ({
                fill: '#6B7280',
                fontSize: 12,
                textAnchor: 'middle'
              })}
            />
            
            <AxisLeft
              scale={yScale}
              stroke="#E5E7EB"
              tickStroke="#E5E7EB"
              tickLabelProps={() => ({
                fill: '#6B7280',
                fontSize: 12,
                textAnchor: 'end'
              })}
              label="Failed Breakdowns"
              labelProps={{
                fill: '#374151',
                fontSize: 14,
                textAnchor: 'middle'
              }}
            />
          </Group>
        </svg>
      </div>
    </div>
  );
}