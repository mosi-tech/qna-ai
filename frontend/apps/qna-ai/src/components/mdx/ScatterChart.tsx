'use client';

import React from 'react';
import { Group } from '@visx/group';
import { Circle, Line } from '@visx/shape';
import { scaleLinear } from '@visx/scale';
import { AxisBottom, AxisLeft } from '@visx/axis';

interface ScatterChartProps {
  data: Record<string, any>[];
  xField: string;
  yField: string;
  labelField: string;
  title: string;
  height?: number;
}

export function ScatterChart({
  data,
  xField,
  yField,
  labelField,
  title,
  height = 300
}: ScatterChartProps) {
  const width = 400;
  const margin = { top: 20, right: 20, bottom: 50, left: 50 };
  const chartWidth = width - margin.left - margin.right;
  const chartHeight = height - margin.top - margin.bottom;

  if (!data.length) return null;

  // Extract values and determine scales
  const xValues = data.map(d => Number(d[xField]));
  const yValues = data.map(d => Number(d[yField]));
  
  const xExtent = [Math.min(...xValues), Math.max(...xValues)];
  const yExtent = [Math.min(...yValues), Math.max(...yValues)];
  
  // Add some padding to the extents
  const xPadding = (xExtent[1] - xExtent[0]) * 0.1;
  const yPadding = (yExtent[1] - yExtent[0]) * 0.1;

  const xScale = scaleLinear({
    range: [0, chartWidth],
    domain: [xExtent[0] - xPadding, xExtent[1] + xPadding]
  });

  const yScale = scaleLinear({
    range: [chartHeight, 0],
    domain: [yExtent[0] - yPadding, yExtent[1] + yPadding]
  });

  // Determine if this is a symmetry analysis based on field names
  const isSymmetryAnalysis = xField.toLowerCase().includes('up') && yField.toLowerCase().includes('down');

  // Color points based on their distance from perfect balance (for symmetry analysis)
  const getPointColor = (xVal: number, yVal: number) => {
    if (!isSymmetryAnalysis) return '#3B82F6'; // Default blue
    
    const ratio = xVal / yVal;
    const distance = Math.abs(1 - ratio);
    
    if (distance < 0.1) return '#10B981'; // green - very symmetric
    if (distance < 0.2) return '#F59E0B'; // yellow - moderately symmetric
    return '#EF4444'; // red - asymmetric
  };

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
      <div className="px-6 py-4 border-b border-gray-100">
        <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
        {isSymmetryAnalysis && (
          <p className="text-sm text-gray-500 mt-1">Perfect symmetry falls on diagonal line</p>
        )}
      </div>
      
      <div className="p-6">
        <svg width="100%" height={height} viewBox={`0 0 ${width} ${height}`}>
          <Group left={margin.left} top={margin.top}>
            {/* Add diagonal reference line for symmetry analysis */}
            {isSymmetryAnalysis && (
              <Line
                from={{ x: 0, y: chartHeight }}
                to={{ x: chartWidth, y: 0 }}
                stroke="#E5E7EB"
                strokeWidth={2}
                strokeDasharray="5,5"
              />
            )}
            
            {/* Grid lines */}
            {[0.25, 0.5, 0.75].map(factor => (
              <Group key={factor}>
                <Line
                  from={{ x: 0, y: yScale(yExtent[0] + (yExtent[1] - yExtent[0]) * factor) }}
                  to={{ x: chartWidth, y: yScale(yExtent[0] + (yExtent[1] - yExtent[0]) * factor) }}
                  stroke="#F3F4F6"
                  strokeWidth={1}
                />
                <Line
                  from={{ x: xScale(xExtent[0] + (xExtent[1] - xExtent[0]) * factor), y: 0 }}
                  to={{ x: xScale(xExtent[0] + (xExtent[1] - xExtent[0]) * factor), y: chartHeight }}
                  stroke="#F3F4F6"
                  strokeWidth={1}
                />
              </Group>
            ))}

            {/* Data points */}
            {data.map((d, i) => {
              const xVal = Number(d[xField]);
              const yVal = Number(d[yField]);
              
              return (
                <Circle
                  key={i}
                  cx={xScale(xVal)}
                  cy={yScale(yVal)}
                  r={8}
                  fill={getPointColor(xVal, yVal)}
                  fillOpacity={0.8}
                  stroke="#FFFFFF"
                  strokeWidth={2}
                  className="cursor-pointer hover:r-10 transition-all duration-200"
                />
              );
            })}

            {/* Labels */}
            {data.map((d, i) => {
              const xVal = Number(d[xField]);
              const yVal = Number(d[yField]);
              
              return (
                <text
                  key={`label-${i}`}
                  x={xScale(xVal)}
                  y={yScale(yVal) - 12}
                  textAnchor="middle"
                  fontSize={10}
                  fill="#374151"
                  fontWeight="600"
                >
                  {d[labelField]}
                </text>
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

        {/* Legend for symmetry analysis */}
        {isSymmetryAnalysis && (
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
        )}
      </div>
    </div>
  );
}