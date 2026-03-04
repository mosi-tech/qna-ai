'use client';

import React from 'react';
import { Group } from '@visx/group';
import { Bar } from '@visx/shape';
import { scaleLinear, scaleBand } from '@visx/scale';
import { AxisLeft, AxisBottom } from '@visx/axis';

interface SymmetryDistributionChartProps {
  ratios: number[];
  bins: number;
}

export function SymmetryDistributionChart({
  ratios,
  bins = 10
}: SymmetryDistributionChartProps) {
  const width = 500;
  const height = 300;
  const margin = { top: 20, right: 30, bottom: 50, left: 50 };
  const chartWidth = width - margin.left - margin.right;
  const chartHeight = height - margin.top - margin.bottom;

  // Create histogram bins
  const minRatio = Math.min(...ratios);
  const maxRatio = Math.max(...ratios);
  const binWidth = (maxRatio - minRatio) / bins;
  
  const histogramBins = Array.from({ length: bins }, (_, i) => {
    const binStart = minRatio + (i * binWidth);
    const binEnd = binStart + binWidth;
    const binCenter = (binStart + binEnd) / 2;
    const count = ratios.filter(r => r >= binStart && r < binEnd).length;
    
    return {
      binStart,
      binEnd,
      binCenter,
      count,
      label: binCenter.toFixed(2)
    };
  });

  // Add the last value to the final bin
  if (histogramBins.length > 0) {
    const lastBin = histogramBins[histogramBins.length - 1];
    const maxCount = ratios.filter(r => r >= lastBin.binStart && r <= maxRatio).length;
    lastBin.count = maxCount;
  }

  const xScale = scaleBand({
    range: [0, chartWidth],
    domain: histogramBins.map(d => d.label),
    padding: 0.1
  });

  const yScale = scaleLinear({
    range: [chartHeight, 0],
    domain: [0, Math.max(...histogramBins.map(d => d.count)) * 1.1],
    nice: true
  });

  const getBarColor = (binCenter: number) => {
    const distance = Math.abs(1 - binCenter);
    if (distance < 0.1) return '#10B981'; // green - near perfect symmetry
    if (distance < 0.2) return '#F59E0B'; // yellow - moderate symmetry
    return '#EF4444'; // red - poor symmetry
  };

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
      <div className="px-6 py-4 border-b border-gray-100">
        <h3 className="text-lg font-semibold text-gray-900">
          Symmetry Distribution
        </h3>
        <p className="text-sm text-gray-500 mt-1">
          Portfolio-wide up/down day ratio distribution
        </p>
      </div>
      
      <div className="p-6">
        <svg width="100%" height={height} viewBox={`0 0 ${width} ${height}`}>
          <Group left={margin.left} top={margin.top}>
            {/* Perfect symmetry reference line */}
            <line
              x1={xScale('1.00') || 0}
              x2={xScale('1.00') || 0}
              y1={0}
              y2={chartHeight}
              stroke="#10B981"
              strokeWidth={2}
              strokeDasharray="3,3"
              opacity={0.7}
            />

            {/* Bars */}
            {histogramBins.map((bin, i) => {
              const barHeight = chartHeight - yScale(bin.count);
              const barWidth = xScale.bandwidth();
              const barX = xScale(bin.label);
              const barY = yScale(bin.count);

              return (
                <Group key={i}>
                  <Bar
                    x={barX}
                    y={barY}
                    width={barWidth}
                    height={barHeight}
                    fill={getBarColor(bin.binCenter)}
                    fillOpacity={0.8}
                    className="hover:fill-opacity-100 transition-all duration-200"
                  />
                  {/* Count labels on bars */}
                  {bin.count > 0 && (
                    <text
                      x={(barX || 0) + barWidth / 2}
                      y={(barY || 0) - 5}
                      textAnchor="middle"
                      fontSize={10}
                      fill="#374151"
                      fontWeight="600"
                    >
                      {bin.count}
                    </text>
                  )}
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
                fontSize: 10,
                textAnchor: 'middle'
              })}
              label="Up/Down Ratio"
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
              label="Positions"
              labelProps={{
                fill: '#374151',
                fontSize: 12,
                textAnchor: 'middle'
              }}
            />
          </Group>
        </svg>

        {/* Reference line explanation */}
        <div className="mt-4 text-xs text-center text-gray-600">
          <span className="inline-flex items-center">
            <div className="w-3 h-0.5 bg-green-500 mr-2" style={{borderTop: '2px dashed'}}></div>
            Perfect Symmetry (1.00 ratio)
          </span>
        </div>
      </div>
    </div>
  );
}