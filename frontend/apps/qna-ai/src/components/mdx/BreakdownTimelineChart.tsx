'use client';

import React from 'react';
import { Group } from '@visx/group';
import { Circle, Line } from '@visx/shape';
import { scaleTime, scaleLinear, scaleOrdinal } from '@visx/scale';
import { AxisBottom, AxisLeft } from '@visx/axis';
import { schemeSet3 } from 'd3-scale-chromatic';

interface Breakdown {
  symbol: string;
  date: string;
  price: number;
  support: number;
}

interface BreakdownTimelineChartProps {
  breakdowns: Breakdown[];
  symbols: string[];
  dateRange: {
    start: string;
    end: string;
  };
}

export function BreakdownTimelineChart({
  breakdowns,
  symbols,
  dateRange
}: BreakdownTimelineChartProps) {
  const width = 800;
  const height = 400;
  const margin = { top: 20, right: 120, bottom: 60, left: 60 };
  const chartWidth = width - margin.left - margin.right;
  const chartHeight = height - margin.top - margin.bottom;

  // Parse dates
  const parsedBreakdowns = breakdowns.map(d => ({
    ...d,
    parsedDate: new Date(d.date)
  }));

  // Scales
  const xScale = scaleTime({
    range: [0, chartWidth],
    domain: [new Date(dateRange.start), new Date(dateRange.end)]
  });

  const yScale = scaleLinear({
    range: [chartHeight, 0],
    domain: symbols.map((_, i) => i),
    nice: true
  });

  const colorScale = scaleOrdinal({
    domain: symbols,
    range: schemeSet3
  });

  return (
    <div className="w-full bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
      <div className="px-6 py-4 border-b border-gray-100">
        <h3 className="text-lg font-semibold text-gray-900">
          Breakdown Timeline
        </h3>
        <p className="text-sm text-gray-500 mt-1">
          When failed breakdowns occurred by symbol
        </p>
      </div>
      
      <div className="p-6">
        <svg width="100%" height={height} viewBox={`0 0 ${width} ${height}`}>
          <Group left={margin.left} top={margin.top}>
            {/* Symbol lanes */}
            {symbols.map((symbol, i) => (
              <Group key={symbol}>
                {/* Lane line */}
                <Line
                  from={{ x: 0, y: yScale(i) }}
                  to={{ x: chartWidth, y: yScale(i) }}
                  stroke="#E5E7EB"
                  strokeWidth={1}
                />
                
                {/* Symbol label */}
                <text
                  x={chartWidth + 10}
                  y={yScale(i) + 5}
                  fontSize={12}
                  fill="#374151"
                  fontWeight="600"
                >
                  {symbol}
                </text>
              </Group>
            ))}

            {/* Breakdown events */}
            {parsedBreakdowns.map((breakdown, i) => {
              const symbolIndex = symbols.indexOf(breakdown.symbol);
              const x = xScale(breakdown.parsedDate);
              const y = yScale(symbolIndex);
              
              if (symbolIndex === -1) return null;

              return (
                <Group key={i}>
                  <Circle
                    cx={x}
                    cy={y}
                    r={6}
                    fill={colorScale(breakdown.symbol)}
                    stroke="#FFFFFF"
                    strokeWidth={2}
                    className="cursor-pointer hover:r-8 transition-all duration-200"
                  />
                  
                  {/* Breakdown severity line */}
                  <Line
                    from={{ x: x, y: y - 15 }}
                    to={{ x: x, y: y + 15 }}
                    stroke={colorScale(breakdown.symbol)}
                    strokeWidth={Math.abs((breakdown.price - breakdown.support) / breakdown.support * 100)}
                    opacity={0.6}
                  />
                </Group>
              );
            })}

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
            />
            
            <AxisLeft
              scale={yScale}
              stroke="transparent"
              tickStroke="transparent"
              tickLabelProps={() => ({
                fill: 'transparent',
                fontSize: 12
              })}
              numTicks={0}
            />
          </Group>
        </svg>

        {/* Legend */}
        <div className="mt-4 flex flex-wrap gap-4">
          {symbols.map(symbol => (
            <div key={symbol} className="flex items-center space-x-2">
              <div
                className="w-3 h-3 rounded-full"
                style={{ backgroundColor: colorScale(symbol) }}
              ></div>
              <span className="text-sm text-gray-700">{symbol}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}