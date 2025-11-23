/**
 * BarChart
 * 
 * Description: Clean bar chart for comparing values across categories
 * Use Cases: Rankings, category comparisons, performance metrics, distribution analysis
 * Data Format: Array of objects with label and value properties
 * 
 * @param data - Array of chart data points
 * @param title - Optional chart title
 * @param orientation - Bar orientation (horizontal or vertical)
 * @param format - Value formatting type
 * @param color - Bar color scheme
 * @param showValues - Whether to show values on bars
 */

'use client';

import { useMemo, useRef, useEffect, useState } from 'react';
import { BarStackHorizontal, BarStack } from '@visx/shape';
import { Group } from '@visx/group';
import { AxisBottom, AxisLeft } from '@visx/axis';
import { scaleBand, scaleLinear } from '@visx/scale';
import { useTooltip, useTooltipInPortal, defaultStyles } from '@visx/tooltip';
import { localPoint } from '@visx/event';
import { insightStyles, cn } from './shared/styles';
import Container from './Container';

interface ChartDataPoint {
  label: string;
  value: number;
  color?: string;
}

interface BarChartProps {
  data: ChartDataPoint[];
  title?: string;
  orientation?: 'horizontal' | 'vertical';
  format?: 'number' | 'percentage' | 'currency';
  color?: 'blue' | 'green' | 'purple' | 'orange';
  showValues?: boolean;
}

export default function BarChart({
  data,
  title,
  orientation = 'vertical',
  format = 'number',
  color = 'blue',
  showValues = true,
}: BarChartProps) {

  const containerRef = useRef<HTMLDivElement>(null);
  const [dimensions, setDimensions] = useState({ width: 400, height: 300 });

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
        const width = Math.max(100, availableWidth); // Absolute minimum 100px
        const height = Math.max(120, Math.min(300, width * 0.7)); // Responsive height

        console.log('BarChart container:', containerWidth, 'chart:', width, 'available:', availableWidth);
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

  // Responsive margins - much more aggressive
  const margin = useMemo(() => {
    const { width } = dimensions;
    if (width < 150) {
      return { top: 5, right: 5, bottom: 20, left: 20 }; // Ultra-minimal for very narrow
    } else if (width < 200) {
      return { top: 8, right: 8, bottom: 25, left: 25 };
    } else if (width < 300) {
      return { top: 10, right: 10, bottom: 30, left: 35 };
    } else if (width < 400) {
      return { top: 15, right: 15, bottom: 35, left: 45 };
    } else {
      return { top: 25, right: 25, bottom: 45, left: 60 };
    }
  }, [dimensions]);

  const { width, height } = dimensions;
  const innerWidth = width - margin.left - margin.right;
  const innerHeight = height - margin.top - margin.bottom;

  // Debug logging
  console.log('BarChart dimensions:', {
    container: width,
    margin,
    innerWidth,
    dataLength: data.length
  });

  // Color schemes
  const colorSchemes = {
    blue: '#3B82F6',
    green: '#10B981',
    purple: '#8B5CF6',
    orange: '#F59E0B'
  };

  const barColor = colorSchemes[color];

  // Value formatting with compact mode for narrow containers
  const formatValue = (value: number | string, compact = false) => {
    // Convert to number if it's a string
    const numValue = typeof value === 'string' ? parseFloat(value) : value;

    // Return original value if conversion failed
    if (isNaN(numValue)) {
      return String(value);
    }

    if (compact && width < 200) {
      // Very compact formatting for narrow containers
      switch (format) {
        case 'percentage':
          return `${numValue.toFixed(0)}%`;
        case 'currency':
          if (numValue >= 1000000) return `$${(numValue / 1000000).toFixed(0)}M`;
          if (numValue >= 1000) return `$${(numValue / 1000).toFixed(0)}K`;
          return `$${Math.round(numValue)}`;
        case 'number':
        default:
          if (numValue >= 1000000) return `${(numValue / 1000000).toFixed(0)}M`;
          if (numValue >= 1000) return `${(numValue / 1000).toFixed(0)}K`;
          return Math.round(numValue).toString();
      }
    } else {
      // Normal formatting
      switch (format) {
        case 'percentage':
          return `${numValue.toFixed(1)}%`;
        case 'currency':
          return `$${numValue.toLocaleString()}`;
        case 'number':
        default:
          return numValue.toLocaleString();
      }
    }
  };

  // Fallback for empty or invalid data
  const validData = Array.isArray(data) && data.length > 0 ? data : [];

  // Scales with responsive padding - ensure bars always fit
  const xScale = scaleBand({
    domain: validData.map(d => d.label),
    range: [0, innerWidth],
    padding: width < 150 ? 0.02 : width < 200 ? 0.05 : width < 300 ? 0.1 : 0.2, // Even tighter padding for narrow containers
    round: true, // Round to pixel boundaries
  });

  const yScale = scaleLinear({
    domain: [0, validData.length > 0 ? Math.max(...validData.map(d => d.value)) * 1.1 : 100],
    range: [innerHeight, 0],
  });

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
    const svgElement = (event.target as SVGElement).ownerSVGElement;
    if (svgElement) {
      const coords = localPoint(svgElement, event);
      showTooltip({
        tooltipData: datum,
        tooltipLeft: coords?.x,
        tooltipTop: coords?.y,
      });
    }
  };

  return (
    <div ref={containerRef} className="p-4 overflow-visible">
      <div className="flex justify-center overflow-visible">
        <svg width={width} height={height} ref={tooltipContainerRef} className="overflow-visible">
          <Group left={margin.left} top={margin.top}>
            {validData.map((d, i) => {
              const barWidth = xScale.bandwidth();
              const barHeight = innerHeight - yScale(d.value);
              const x = xScale(d.label);
              const y = yScale(d.value);

              // Clamp bar width and position to ensure it fits in container
              const clampedX = Math.max(0, Math.min(x || 0, innerWidth - barWidth));
              const clampedWidth = Math.min(barWidth, innerWidth - (x || 0));

              return (
                <Group key={d.label}>
                  <rect
                    x={clampedX}
                    y={y}
                    width={clampedWidth}
                    height={barHeight}
                    fill={d.color || barColor}
                    className="hover:opacity-80 transition-opacity cursor-pointer"
                    onMouseEnter={(event) => handleTooltip(event, d)}
                    onMouseLeave={hideTooltip}
                  />
                  {showValues && width > 250 && (
                    <text
                      x={clampedX + clampedWidth / 2}
                      y={(y || 0) - 3}
                      textAnchor="middle"
                      className={cn("fill-gray-700", width < 300 ? "text-xs" : "text-xs")}
                      fontSize={width < 300 ? 10 : 12}
                    >
                      {formatValue(d.value)}
                    </text>
                  )}
                </Group>
              );
            })}

            {/* X Axis */}
            <AxisBottom
              top={innerHeight}
              scale={xScale}
              stroke="#E5E7EB"
              tickStroke="#E5E7EB"
              tickLabelProps={() => ({
                fill: '#6B7280',
                fontSize: width < 200 ? 8 : width < 300 ? 10 : 12,
                textAnchor: 'middle',
              })}
            />

            {/* Y Axis */}
            <AxisLeft
              scale={yScale}
              stroke="#E5E7EB"
              tickStroke="#E5E7EB"
              numTicks={width < 200 ? 3 : width < 300 ? 4 : 5}
              tickFormat={(value) => formatValue(Number(value), true)}
              tickLabelProps={() => ({
                fill: '#6B7280',
                fontSize: width < 200 ? 8 : width < 300 ? 10 : 12,
                textAnchor: 'end',
                dy: '0.33em',
              })}
            />
          </Group>
        </svg>
      </div>

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
            <div className="font-semibold">{(tooltipData as ChartDataPoint).label}</div>
            <div>{formatValue((tooltipData as ChartDataPoint).value)}</div>
          </div>
        </TooltipInPortal>
      )}
    </div>
  );
}