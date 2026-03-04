'use client';

import React from 'react';
import { Group } from '@visx/group';
import { LinePath } from '@visx/shape';
import { scaleTime, scaleLinear } from '@visx/scale';
import { AxisBottom, AxisLeft } from '@visx/axis';
import { curveCardinal } from '@visx/curve';

interface LineChartProps {
  data: Record<string, any>[];
  xField: string;
  yField: string;
  title: string;
  height?: number;
}

export function LineChart({
  data,
  xField,
  yField,
  title,
  height = 300
}: LineChartProps) {
  const width = 600;
  const margin = { top: 20, right: 30, bottom: 50, left: 60 };
  const chartWidth = width - margin.left - margin.right;
  const chartHeight = height - margin.top - margin.bottom;

  if (!data.length) return null;

  // Parse dates if xField contains date data
  const processedData = data.map(d => ({
    ...d,
    [xField]: xField.toLowerCase().includes('date') || xField.toLowerCase().includes('week') 
      ? new Date(d[xField]) 
      : d[xField]
  }));

  // Determine scale types
  const xValues = processedData.map(d => d[xField]);
  const yValues = processedData.map(d => Number(d[yField]));
  
  const isTimeScale = xValues[0] instanceof Date;
  
  const xScale = isTimeScale 
    ? scaleTime({
        range: [0, chartWidth],
        domain: [Math.min(...xValues), Math.max(...xValues)]
      })
    : scaleLinear({
        range: [0, chartWidth],
        domain: [Math.min(...xValues), Math.max(...xValues)]
      });

  const yScale = scaleLinear({
    range: [chartHeight, 0],
    domain: [Math.min(...yValues) * 0.95, Math.max(...yValues) * 1.05],
    nice: true
  });

  // Color based on data context
  const getLineColor = () => {
    if (title.toLowerCase().includes('range') || title.toLowerCase().includes('volatility')) {
      return '#EF4444'; // Red for volatility/range analysis
    }
    if (title.toLowerCase().includes('trend')) {
      return '#10B981'; // Green for trend analysis
    }
    return '#3B82F6'; // Default blue
  };

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
      <div className="px-6 py-4 border-b border-gray-100">
        <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
        <p className="text-sm text-gray-500 mt-1">
          {isTimeScale ? 'Time series analysis' : 'Data progression'}
        </p>
      </div>
      
      <div className="p-6">
        <svg width="100%" height={height} viewBox={`0 0 ${width} ${height}`}>
          <Group left={margin.left} top={margin.top}>
            {/* Grid lines */}
            {[0.25, 0.5, 0.75].map(factor => (
              <line
                key={factor}
                x1={0}
                x2={chartWidth}
                y1={yScale(Math.min(...yValues) + (Math.max(...yValues) - Math.min(...yValues)) * factor)}
                y2={yScale(Math.min(...yValues) + (Math.max(...yValues) - Math.min(...yValues)) * factor)}
                stroke="#F3F4F6"
                strokeWidth={1}
              />
            ))}

            {/* Main line */}
            <LinePath
              data={processedData}
              x={d => xScale(d[xField])}
              y={d => yScale(Number(d[yField]))}
              stroke={getLineColor()}
              strokeWidth={2.5}
              curve={curveCardinal}
              opacity={0.9}
            />

            {/* Data points */}
            {processedData.map((d, i) => (
              <circle
                key={i}
                cx={xScale(d[xField])}
                cy={yScale(Number(d[yField]))}
                r={4}
                fill={getLineColor()}
                stroke="#FFFFFF"
                strokeWidth={2}
                className="cursor-pointer hover:r-6 transition-all duration-200"
              />
            ))}

            {/* Axes */}
            <AxisBottom
              top={chartHeight}
              scale={xScale}
              stroke="#E5E7EB"
              tickStroke="#E5E7EB"
              numTicks={isTimeScale ? 4 : 5}
              tickLabelProps={() => ({
                fill: '#6B7280',
                fontSize: 12,
                textAnchor: 'middle'
              })}
              label={xField}
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
              label={yField}
              labelProps={{
                fill: '#374151',
                fontSize: 14,
                textAnchor: 'middle'
              }}
            />
          </Group>
        </svg>

        {/* Summary stats */}
        <div className="mt-4 grid grid-cols-3 gap-4 text-center text-sm">
          <div>
            <div className="font-semibold text-gray-900">
              {Math.min(...yValues).toFixed(2)}
            </div>
            <div className="text-gray-500">Minimum</div>
          </div>
          <div>
            <div className="font-semibold text-gray-900">
              {(yValues.reduce((a, b) => a + b, 0) / yValues.length).toFixed(2)}
            </div>
            <div className="text-gray-500">Average</div>
          </div>
          <div>
            <div className="font-semibold text-gray-900">
              {Math.max(...yValues).toFixed(2)}
            </div>
            <div className="text-gray-500">Maximum</div>
          </div>
        </div>
      </div>
    </div>
  );
}