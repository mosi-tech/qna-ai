/**
 * ScatterChart
 * 
 * Description: Clean scatter plot for exploring relationships between two variables
 * Use Cases: Correlation analysis, risk vs return plots, performance comparisons, outlier detection
 * Data Format: Array of objects with x, y values and optional labels/colors
 * 
 * @param data - Array of chart data points with x and y coordinates
 * @param title - Optional chart title
 * @param xAxis - X-axis configuration (label, format)
 * @param yAxis - Y-axis configuration (label, format)
 * @param showTrendLine - Whether to show linear regression line
 * @param pointSize - Size of scatter points
 * @param colors - Color scheme or array of colors
 * @param onApprove - Callback for approve action
 * @param onDisapprove - Callback for disapprove action
 */

'use client';

import { useMemo, useRef, useEffect, useState } from 'react';
import { Group } from '@visx/group';
import { AxisBottom, AxisLeft } from '@visx/axis';
import { scaleLinear } from '@visx/scale';
import { LinePath } from '@visx/shape';
import { useTooltip, useTooltipInPortal, defaultStyles } from '@visx/tooltip';
import { localPoint } from '@visx/event';
// Removed @visx/stats import - implementing linear regression manually
import { insightStyles, cn } from './shared/styles';
import Container from './Container';

interface ChartDataPoint {
  x: number;
  y: number;
  label?: string;
  color?: string;
  size?: number;
}

interface AxisConfig {
  label: string;
  format?: 'number' | 'percentage' | 'currency';
}

interface ScatterChartProps {
  data: ChartDataPoint[];
  title?: string;
  xAxis: AxisConfig;
  yAxis: AxisConfig;
  showTrendLine?: boolean;
  pointSize?: number;
  colors?: 'default' | 'business' | 'tech' | 'finance' | string[];
}

export default function ScatterChart({
  data,
  title,
  xAxis,
  yAxis,
  showTrendLine = false,
  pointSize = 4,
  colors = 'default'
}: ScatterChartProps) {

  const containerRef = useRef<HTMLDivElement>(null);
  const [dimensions, setDimensions] = useState({ width: 500, height: 350 });

  // Responsive sizing based on container
  useEffect(() => {
    const updateDimensions = () => {
      if (containerRef.current) {
        const rect = containerRef.current.getBoundingClientRect();
        const containerWidth = rect.width;
        
        // Use nearly all available width (very aggressive)
        const padding = 16; // Minimal padding
        const availableWidth = containerWidth - padding;
        
        // Force the chart to fit the container
        const width = Math.max(150, availableWidth); // Lower minimum for narrow containers
        const height = Math.max(120, width * 0.7); // Responsive height
        
        console.log('ScatterChart container:', containerWidth, 'chart:', width, 'available:', availableWidth);
        setDimensions({ width, height });
      }
    };

    // Use ResizeObserver for better container tracking
    const resizeObserver = new ResizeObserver(updateDimensions);
    if (containerRef.current) {
      resizeObserver.observe(containerRef.current);
    }
    
    updateDimensions();
    
    return () => {
      resizeObserver.disconnect();
    };
  }, []);

  // Responsive margins based on size - much more aggressive
  const margin = useMemo(() => {
    const { width } = dimensions;
    if (width < 150) {
      return { top: 5, right: 5, bottom: 25, left: 30 }; // Ultra-minimal for very narrow
    } else if (width < 200) {
      return { top: 8, right: 8, bottom: 30, left: 35 }; 
    } else if (width < 300) {
      return { top: 10, right: 10, bottom: 35, left: 45 };
    } else if (width < 400) {
      return { top: 15, right: 15, bottom: 40, left: 55 };
    } else {
      return { top: 25, right: 25, bottom: 50, left: 70 };
    }
  }, [dimensions]);

  const { width, height } = dimensions;
  const innerWidth = width - margin.left - margin.right;
  const innerHeight = height - margin.top - margin.bottom;

  // Color schemes
  const colorSchemes = {
    default: ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#06B6D4'],
    business: ['#1E40AF', '#059669', '#D97706', '#DC2626', '#7C3AED', '#0891B2'],
    tech: ['#6366F1', '#8B5CF6', '#EC4899', '#F59E0B', '#10B981', '#06B6D4'],
    finance: ['#065F46', '#1F2937', '#374151', '#6B7280', '#9CA3AF', '#D1D5DB']
  };

  const getColors = () => {
    if (Array.isArray(colors)) return colors;
    return colorSchemes[colors as keyof typeof colorSchemes] || colorSchemes.default;
  };

  const chartColors = getColors();

  // Value formatting functions
  const formatValue = (value: number, format?: string) => {
    switch (format) {
      case 'percentage':
        return `${value.toFixed(1)}%`;
      case 'currency':
        return `$${value.toLocaleString()}`;
      case 'number':
      default:
        return value.toLocaleString();
    }
  };

  // Scales
  const xScale = useMemo(() => {
    const xMin = Math.min(...data.map(d => d.x));
    const xMax = Math.max(...data.map(d => d.x));
    const xPadding = (xMax - xMin) * 0.05;
    
    return scaleLinear({
      domain: [xMin - xPadding, xMax + xPadding],
      range: [0, innerWidth],
    });
  }, [data, innerWidth]);

  const yScale = useMemo(() => {
    const yMin = Math.min(...data.map(d => d.y));
    const yMax = Math.max(...data.map(d => d.y));
    const yPadding = (yMax - yMin) * 0.05;
    
    return scaleLinear({
      domain: [yMin - yPadding, yMax + yPadding],
      range: [innerHeight, 0],
    });
  }, [data, innerHeight]);

  // Calculate trend line using linear regression
  const trendLine = useMemo(() => {
    if (!showTrendLine || data.length < 2) return null;
    
    const n = data.length;
    const sumX = data.reduce((sum, d) => sum + d.x, 0);
    const sumY = data.reduce((sum, d) => sum + d.y, 0);
    const sumXY = data.reduce((sum, d) => sum + d.x * d.y, 0);
    const sumX2 = data.reduce((sum, d) => sum + d.x * d.x, 0);
    
    // Calculate slope and y-intercept
    const slope = (n * sumXY - sumX * sumY) / (n * sumX2 - sumX * sumX);
    const yIntercept = (sumY - slope * sumX) / n;
    
    const xMin = Math.min(...data.map(d => d.x));
    const xMax = Math.max(...data.map(d => d.x));
    
    return [
      { x: xMin, y: slope * xMin + yIntercept },
      { x: xMax, y: slope * xMax + yIntercept }
    ];
  }, [data, showTrendLine]);

  // Calculate correlation coefficient
  const correlation = useMemo(() => {
    if (data.length < 2) return 0;
    
    const n = data.length;
    const sumX = data.reduce((sum, d) => sum + d.x, 0);
    const sumY = data.reduce((sum, d) => sum + d.y, 0);
    const sumXY = data.reduce((sum, d) => sum + d.x * d.y, 0);
    const sumX2 = data.reduce((sum, d) => sum + d.x * d.x, 0);
    const sumY2 = data.reduce((sum, d) => sum + d.y * d.y, 0);
    
    const numerator = n * sumXY - sumX * sumY;
    const denominator = Math.sqrt((n * sumX2 - sumX * sumX) * (n * sumY2 - sumY * sumY));
    
    return denominator === 0 ? 0 : numerator / denominator;
  }, [data]);

  // Tooltip
  const {
    tooltipData,
    tooltipLeft,
    tooltipTop,
    tooltipOpen,
    showTooltip,
    hideTooltip,
  } = useTooltip();

  const { containerRef: tooltipContainerRef, TooltipInPortal } = useTooltipInPortal({
    detectBounds: true,
    scroll: true,
  });

  const handleTooltip = (event: React.MouseEvent, datum: ChartDataPoint) => {
    const coords = localPoint(event.target.ownerSVGElement, event);
    showTooltip({
      tooltipData: datum,
      tooltipLeft: coords?.x,
      tooltipTop: coords?.y,
    });
  };

  return (
    <Container title={title}>
      <div ref={containerRef} className="p-4">
        <div className="flex justify-center">
          <svg width={width} height={height} ref={tooltipContainerRef}>
            <Group left={margin.left} top={margin.top}>
              {/* Grid lines */}
              {xScale.ticks(5).map((tick) => (
                <line
                  key={`x-grid-${tick}`}
                  x1={xScale(tick)}
                  x2={xScale(tick)}
                  y1={0}
                  y2={innerHeight}
                  stroke="#F3F4F6"
                  strokeWidth={1}
                />
              ))}
              {yScale.ticks(5).map((tick) => (
                <line
                  key={`y-grid-${tick}`}
                  x1={0}
                  x2={innerWidth}
                  y1={yScale(tick)}
                  y2={yScale(tick)}
                  stroke="#F3F4F6"
                  strokeWidth={1}
                />
              ))}

              {/* Trend line */}
              {trendLine && (
                <LinePath
                  data={trendLine}
                  x={(d) => xScale(d.x)}
                  y={(d) => yScale(d.y)}
                  stroke="#EF4444"
                  strokeWidth={2}
                  strokeDasharray="4,4"
                  fill="transparent"
                />
              )}

              {/* Scatter points */}
              {data.map((point, i) => {
                const cx = xScale(point.x) || 0;
                const cy = yScale(point.y) || 0;
                const radius = point.size || (width < 200 ? 2 : width < 300 ? 3 : pointSize);
                
                // Clamp points to stay within container bounds
                const clampedCx = Math.max(radius, Math.min(cx, innerWidth - radius));
                const clampedCy = Math.max(radius, Math.min(cy, innerHeight - radius));
                
                console.log(`Point ${i}:`, {
                  x: point.x, y: point.y,
                  cx, cy,
                  clampedCx, clampedCy,
                  innerWidth, innerHeight,
                  fitsX: (cx >= 0 && cx <= innerWidth),
                  fitsY: (cy >= 0 && cy <= innerHeight)
                });

                return (
                  <circle
                    key={i}
                    cx={clampedCx}
                    cy={clampedCy}
                    r={radius}
                    fill={point.color || chartColors[i % chartColors.length]}
                    className="hover:opacity-70 transition-opacity cursor-pointer"
                    onMouseEnter={(event) => handleTooltip(event, point)}
                    onMouseLeave={hideTooltip}
                  />
                );
              })}

              {/* X Axis */}
              <AxisBottom
                top={innerHeight}
                scale={xScale}
                stroke="#E5E7EB"
                tickStroke="#E5E7EB"
                tickFormat={(value) => formatValue(Number(value), xAxis.format)}
                tickLabelProps={() => ({
                  fill: '#6B7280',
                  fontSize: width < 400 ? 10 : 12,
                  textAnchor: 'middle',
                })}
                label={xAxis.label}
                labelProps={{
                  fontSize: 14,
                  textAnchor: 'middle',
                  fill: '#374151',
                  fontWeight: 500,
                }}
              />

              {/* Y Axis */}
              <AxisLeft
                scale={yScale}
                stroke="#E5E7EB"
                tickStroke="#E5E7EB"
                tickFormat={(value) => formatValue(Number(value), yAxis.format)}
                tickLabelProps={() => ({
                  fill: '#6B7280',
                  fontSize: width < 400 ? 10 : 12,
                  textAnchor: 'end',
                  dy: '0.33em',
                })}
                label={yAxis.label}
                labelProps={{
                  fontSize: 14,
                  textAnchor: 'middle',
                  fill: '#374151',
                  fontWeight: 500,
                }}
              />
            </Group>
          </svg>
        </div>
      </div>

      {/* Summary stats for larger charts */}
      {width > 500 && (
        <div className="px-6 py-4 border-t border-gray-100 bg-gray-50">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
            <div>
              <div className="text-gray-600">Data Points</div>
              <div className="font-semibold text-gray-900">{data.length}</div>
            </div>
            <div>
              <div className="text-gray-600">Correlation</div>
              <div className={cn("font-semibold", 
                Math.abs(correlation) > 0.7 ? 'text-green-600' :
                Math.abs(correlation) > 0.3 ? 'text-yellow-600' :
                'text-gray-600'
              )}>
                {correlation.toFixed(3)}
              </div>
            </div>
            <div>
              <div className="text-gray-600">{xAxis.label} Range</div>
              <div className="font-semibold text-gray-900">
                {formatValue(Math.min(...data.map(d => d.x)), xAxis.format)} - {formatValue(Math.max(...data.map(d => d.x)), xAxis.format)}
              </div>
            </div>
            <div>
              <div className="text-gray-600">{yAxis.label} Range</div>
              <div className="font-semibold text-gray-900">
                {formatValue(Math.min(...data.map(d => d.y)), yAxis.format)} - {formatValue(Math.max(...data.map(d => d.y)), yAxis.format)}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Tooltip */}
      {tooltipOpen && tooltipData && (
        <TooltipInPortal
          top={tooltipTop}
          left={tooltipLeft}
          style={{
            ...defaultStyles,
            minWidth: 120,
            backgroundColor: 'rgba(0,0,0,0.9)',
            color: 'white',
          }}
        >
          <div className="text-sm">
            {tooltipData.label && (
              <div className="font-semibold">{tooltipData.label}</div>
            )}
            <div>{xAxis.label}: {formatValue(tooltipData.x, xAxis.format)}</div>
            <div>{yAxis.label}: {formatValue(tooltipData.y, yAxis.format)}</div>
          </div>
        </TooltipInPortal>
      )}
    </Container>
  );
}