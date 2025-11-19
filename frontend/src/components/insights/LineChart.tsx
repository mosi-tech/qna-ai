/**
 * LineChart
 * 
 * Description: Clean line chart for time series data and trend visualization
 * Use Cases: Performance over time, historical analysis, trend tracking, growth curves
 * Data Format: Array of objects with date/label and value properties, supports multiple series
 * 
 * @param data - Array of chart data points or array of series
 * @param title - Optional chart title
 * @param xAxisLabel - Label for x-axis
 * @param yAxisLabel - Label for y-axis
 * @param format - Value formatting type for y-axis
 * @param showDots - Whether to show data point dots
 * @param showArea - Whether to fill area under line
 * @param colors - Color scheme or array of colors for multiple series
 * @param onApprove - Callback for approve action
 * @param onDisapprove - Callback for disapprove action
 */

'use client';

import { useMemo, useRef, useEffect, useState } from 'react';
import { LinePath, AreaClosed } from '@visx/shape';
import { Group } from '@visx/group';
import { AxisBottom, AxisLeft } from '@visx/axis';
import { scaleLinear, scaleTime, scalePoint } from '@visx/scale';
import { useTooltip, useTooltipInPortal, defaultStyles } from '@visx/tooltip';
import { localPoint } from '@visx/event';
import { bisector } from 'd3-array';
import { insightStyles, cn } from './shared/styles';

interface ChartDataPoint {
  label: string;
  date?: Date;
  value: number;
}

interface ChartSeries {
  name: string;
  data: ChartDataPoint[];
  color?: string;
}

interface LineChartProps {
  data: ChartDataPoint[] | ChartSeries[];
  title?: string;
  xAxisLabel?: string;
  yAxisLabel?: string;
  format?: 'number' | 'percentage' | 'currency';
  showDots?: boolean;
  showArea?: boolean;
  colors?: 'default' | 'business' | 'tech' | 'finance' | string[];
  onApprove?: () => void;
  onDisapprove?: () => void;
}

export default function LineChart({
  data,
  title,
  xAxisLabel,
  yAxisLabel,
  format = 'number',
  showDots = true,
  showArea = false,
  colors = 'default',
  onApprove,
  onDisapprove
}: LineChartProps) {

  const containerRef = useRef<HTMLDivElement>(null);
  const [dimensions, setDimensions] = useState({ width: 500, height: 300 });

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
        const height = Math.max(120, width * 0.6); // Responsive height
        
        console.log('LineChart container:', containerWidth, 'chart:', width, 'available:', availableWidth);
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
      return { top: 5, right: 5, bottom: 20, left: 25 }; // Ultra-minimal for very narrow
    } else if (width < 200) {
      return { top: 8, right: 8, bottom: 25, left: 30 }; 
    } else if (width < 300) {
      return { top: 10, right: 10, bottom: 30, left: 40 };
    } else if (width < 400) {
      return { top: 15, right: 15, bottom: 35, left: 50 };
    } else {
      return { top: 25, right: 25, bottom: 45, left: 60 };
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

  // Normalize data to series format
  const series = useMemo(() => {
    if (!Array.isArray(data) || data.length === 0) return [];
    
    // Check if first item has 'name' and 'data' properties (series format)
    if ('name' in data[0] && 'data' in data[0]) {
      return data as ChartSeries[];
    }
    
    // Convert single series to series array
    return [{
      name: 'Data',
      data: data as ChartDataPoint[],
      color: chartColors[0]
    }];
  }, [data, chartColors]);

  // Get all data points for scales
  const allPoints = useMemo(() => 
    series.flatMap(s => s.data), [series]
  );

  // Determine if using dates or labels
  const usesDates = allPoints.length > 0 && allPoints[0].date instanceof Date;

  // Value formatting
  const formatValue = (value: number) => {
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

  // Scales with responsive adjustments
  const xScale = useMemo(() => {
    if (usesDates) {
      const extent = [
        Math.min(...allPoints.map(d => d.date!.getTime())),
        Math.max(...allPoints.map(d => d.date!.getTime()))
      ];
      return scaleTime({
        domain: extent,
        range: [0, innerWidth],
      });
    } else {
      return scalePoint({
        domain: allPoints.map(d => d.label),
        range: [0, innerWidth],
        padding: width < 200 ? 0.02 : width < 300 ? 0.05 : 0.1, // Tighter padding for narrow containers
        round: true, // Round to pixel boundaries
      });
    }
  }, [allPoints, innerWidth, usesDates, width]);

  const yScale = useMemo(() => {
    const yMin = Math.min(...allPoints.map(d => d.value));
    const yMax = Math.max(...allPoints.map(d => d.value));
    const padding = (yMax - yMin) * 0.1;
    
    return scaleLinear({
      domain: [yMin - padding, yMax + padding],
      range: [innerHeight, 0],
    });
  }, [allPoints, innerHeight]);

  // Accessor functions
  const getX = (d: ChartDataPoint) => usesDates ? d.date! : d.label;
  const getY = (d: ChartDataPoint) => d.value;

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

  const handleTooltip = (event: React.MouseEvent, datum: ChartDataPoint, seriesName: string) => {
    const coords = localPoint(event.target.ownerSVGElement, event);
    showTooltip({
      tooltipData: { ...datum, seriesName },
      tooltipLeft: coords?.x,
      tooltipTop: coords?.y,
    });
  };

  return (
    <div ref={containerRef} className={cn("bg-white rounded-lg overflow-hidden", insightStyles.spacing.component)}>
      {title && (
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className={insightStyles.typography.h3}>{title}</h3>
        </div>
      )}

      <div className="p-4">
        <div className="flex justify-center">
          <svg width={width} height={height} ref={tooltipContainerRef}>
            <Group left={margin.left} top={margin.top}>
              {/* Grid lines */}
              {yScale.ticks(5).map((tick) => (
                <line
                  key={tick}
                  x1={0}
                  x2={innerWidth}
                  y1={yScale(tick)}
                  y2={yScale(tick)}
                  stroke="#F3F4F6"
                  strokeWidth={1}
                />
              ))}

              {/* Area fills */}
              {showArea && series.map((s, i) => (
                <AreaClosed
                  key={s.name}
                  data={s.data}
                  x={(d) => xScale(getX(d)) || 0}
                  y={(d) => yScale(getY(d)) || 0}
                  yScale={yScale}
                  fill={s.color || chartColors[i % chartColors.length]}
                  fillOpacity={0.1}
                />
              ))}

              {/* Lines */}
              {series.map((s, i) => {
                const lineColor = s.color || chartColors[i % chartColors.length];
                return (
                  <Group key={s.name}>
                    <LinePath
                      data={s.data}
                      x={(d) => xScale(getX(d)) || 0}
                      y={(d) => yScale(getY(d)) || 0}
                      stroke={lineColor}
                      strokeWidth={2}
                      fill="transparent"
                    />
                    
                    {/* Data points */}
                    {showDots && s.data.map((d, j) => {
                      const cx = xScale(getX(d)) || 0;
                      const cy = yScale(getY(d)) || 0;
                      
                      // Clamp dots to stay within container bounds
                      const clampedCx = Math.max(2, Math.min(cx, innerWidth - 2));
                      const clampedCy = Math.max(2, Math.min(cy, innerHeight - 2));
                      
                      return (
                        <circle
                          key={j}
                          cx={clampedCx}
                          cy={clampedCy}
                          r={width < 200 ? 1.5 : width < 350 ? 2 : 3}
                          fill={lineColor}
                          className="hover:r-4 transition-all cursor-pointer"
                          onMouseEnter={(event) => handleTooltip(event, d, s.name)}
                          onMouseLeave={hideTooltip}
                        />
                      );
                    })}
                  </Group>
                );
              })}

              {/* X Axis */}
              <AxisBottom
                top={innerHeight}
                scale={xScale}
                stroke="#E5E7EB"
                tickStroke="#E5E7EB"
                tickFormat={usesDates ? 
                  (value) => new Date(value).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }) :
                  (value) => String(value)
                }
                tickLabelProps={() => ({
                  fill: '#6B7280',
                  fontSize: width < 350 ? 10 : 12,
                  textAnchor: 'middle',
                })}
                label={xAxisLabel}
              />

              {/* Y Axis */}
              <AxisLeft
                scale={yScale}
                stroke="#E5E7EB"
                tickStroke="#E5E7EB"
                tickFormat={(value) => formatValue(Number(value))}
                tickLabelProps={() => ({
                  fill: '#6B7280',
                  fontSize: width < 350 ? 10 : 12,
                  textAnchor: 'end',
                  dy: '0.33em',
                })}
                label={yAxisLabel}
              />
            </Group>
          </svg>
        </div>

        {/* Legend for multiple series */}
        {series.length > 1 && width > 300 && (
          <div className="flex justify-center mt-4">
            <div className="flex gap-4">
              {series.map((s, i) => (
                <div key={s.name} className="flex items-center gap-2 text-sm">
                  <div 
                    className="w-3 h-3 rounded-full"
                    style={{ backgroundColor: s.color || chartColors[i % chartColors.length] }}
                  />
                  <span className="text-gray-700">{s.name}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Summary stats for larger charts */}
      {width > 500 && (
        <div className="px-6 py-4 border-t border-gray-100 bg-gray-50">
          <div className="grid grid-cols-3 gap-4 text-sm">
            <div>
              <div className="text-gray-600">Peak Value</div>
              <div className="font-semibold text-gray-900">
                {formatValue(Math.max(...allPoints.map(d => d.value)))}
              </div>
            </div>
            <div>
              <div className="text-gray-600">Average</div>
              <div className="font-semibold text-gray-900">
                {formatValue(allPoints.reduce((sum, d) => sum + d.value, 0) / allPoints.length)}
              </div>
            </div>
            <div>
              <div className="text-gray-600">Data Points</div>
              <div className="font-semibold text-gray-900">{allPoints.length}</div>
            </div>
          </div>
        </div>
      )}

      {/* Action buttons */}
      {(onApprove || onDisapprove) && (
        <div className="px-6 py-4 border-t border-gray-200 bg-gray-50 flex gap-2">
          {onApprove && (
            <button
              onClick={onApprove}
              className={insightStyles.button.approve.base}
            >
              Approve
            </button>
          )}
          {onDisapprove && (
            <button
              onClick={onDisapprove}
              className={insightStyles.button.disapprove.base}
            >
              Disapprove
            </button>
          )}
        </div>
      )}

      {/* Tooltip */}
      {tooltipOpen && tooltipData && (
        <TooltipInPortal
          top={tooltipTop}
          left={tooltipLeft}
          style={{
            ...defaultStyles,
            minWidth: 60,
            backgroundColor: 'rgba(0,0,0,0.9)',
            color: 'white',
          }}
        >
          <div className="text-sm">
            {tooltipData.seriesName && series.length > 1 && (
              <div className="font-semibold">{tooltipData.seriesName}</div>
            )}
            <div>{tooltipData.label}</div>
            <div className="text-blue-300">{formatValue(tooltipData.value)}</div>
          </div>
        </TooltipInPortal>
      )}
    </div>
  );
}