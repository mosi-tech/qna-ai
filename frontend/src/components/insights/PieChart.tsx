/**
 * PieChart
 * 
 * Description: Clean pie/donut chart for showing proportional data and distributions
 * Use Cases: Portfolio allocations, category distributions, market share, composition analysis
 * Data Format: Array of objects with label, value, and optional color properties
 * 
 * @param data - Array of chart data points
 * @param title - Optional chart title
 * @param showLegend - Whether to display legend
 * @param showPercentages - Whether to show percentage labels
 * @param innerRadius - Inner radius for donut chart (0 for pie)
 * @param colors - Color scheme or array of colors
 * @param onApprove - Callback for approve action
 * @param onDisapprove - Callback for disapprove action
 */

'use client';

import { useMemo, useRef, useEffect, useState } from 'react';
import { Pie } from '@visx/shape';
import { Group } from '@visx/group';
import { useTooltip, useTooltipInPortal, defaultStyles } from '@visx/tooltip';
import { localPoint } from '@visx/event';
import { insightStyles, cn } from './shared/styles';

interface ChartDataPoint {
  label: string;
  value: number;
  color?: string;
}

interface PieChartProps {
  data: ChartDataPoint[];
  title?: string;
  showLegend?: boolean;
  showPercentages?: boolean;
  innerRadius?: number;
  colors?: 'default' | 'business' | 'tech' | 'finance' | string[];
  onApprove?: () => void;
  onDisapprove?: () => void;
}

export default function PieChart({
  data,
  title,
  showLegend = true,
  showPercentages = true,
  innerRadius = 0,
  colors = 'default',
  onApprove,
  onDisapprove
}: PieChartProps) {

  const containerRef = useRef<HTMLDivElement>(null);
  const [dimensions, setDimensions] = useState({ width: 400, height: 280 });
  const [containerWidth, setContainerWidth] = useState(400);

  // Responsive sizing based on container
  useEffect(() => {
    const updateDimensions = () => {
      if (containerRef.current) {
        const actualContainerWidth = containerRef.current.getBoundingClientRect().width;
        const padding = 32;
        const availableWidth = actualContainerWidth - padding;
        
        const minSize = 200;
        const maxSize = 400;
        const size = Math.max(minSize, Math.min(maxSize, availableWidth * 0.8));
        
        setContainerWidth(actualContainerWidth); // Track actual container width separately
        setDimensions({ width: size, height: size * 0.7 });
      }
    };

    updateDimensions();
    window.addEventListener('resize', updateDimensions);
    return () => window.removeEventListener('resize', updateDimensions);
  }, []);

  const { width, height } = dimensions;
  const margin = width < 300 ? 15 : 25;
  const radius = Math.min(width, height) / 2 - margin;

  // Color schemes
  const colorSchemes = {
    default: ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#06B6D4', '#84CC16', '#F97316'],
    business: ['#1E40AF', '#059669', '#D97706', '#DC2626', '#7C3AED', '#0891B2'],
    tech: ['#6366F1', '#8B5CF6', '#EC4899', '#F59E0B', '#10B981', '#06B6D4'],
    finance: ['#065F46', '#1F2937', '#374151', '#6B7280', '#9CA3AF', '#D1D5DB']
  };

  const getColors = () => {
    if (Array.isArray(colors)) return colors;
    return colorSchemes[colors as keyof typeof colorSchemes] || colorSchemes.default;
  };

  const chartColors = getColors();

  // Calculate total and percentages
  const total = useMemo(() => data.reduce((sum, d) => sum + d.value, 0), [data]);
  
  const dataWithPercentages = useMemo(() => 
    data.map((d, i) => ({
      ...d,
      percentage: (d.value / total) * 100,
      color: d.color || chartColors[i % chartColors.length]
    })), [data, total, chartColors]
  );

  // Value formatting
  const formatValue = (value: number) => {
    if (value >= 1000000) return `${(value / 1000000).toFixed(1)}M`;
    if (value >= 1000) return `${(value / 1000).toFixed(1)}K`;
    return value.toLocaleString();
  };

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

  const handleTooltip = (event: React.MouseEvent, datum: any) => {
    const coords = localPoint(event.target.ownerSVGElement, event);
    showTooltip({
      tooltipData: datum,
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

      <div className={cn("p-4", showLegend && containerWidth > 450 ? "grid grid-cols-2 gap-4" : "")}>
        {/* Chart */}
        <div className="flex justify-center">
          <svg width={width} height={height} ref={tooltipContainerRef}>
            <Group top={height / 2} left={width / 2}>
              <Pie
                data={dataWithPercentages}
                pieValue={(d) => d.value}
                outerRadius={radius}
                innerRadius={innerRadius}
                cornerRadius={2}
                padAngle={0.02}
              >
                {(pie) =>
                  pie.arcs.map((arc, index) => {
                    const { label, value, percentage, color } = arc.data;
                    const [centroidX, centroidY] = pie.path.centroid(arc);
                    const hasSpaceForLabel = arc.endAngle - arc.startAngle >= 0.1;
                    
                    return (
                      <Group key={label}>
                        <path
                          d={pie.path(arc) || ''}
                          fill={color}
                          className="hover:opacity-80 transition-opacity cursor-pointer"
                          onMouseEnter={(event) => handleTooltip(event, arc.data)}
                          onMouseLeave={hideTooltip}
                        />
                        {hasSpaceForLabel && showPercentages && width > 200 && percentage > 5 && (
                          <text
                            x={centroidX}
                            y={centroidY}
                            dy=".33em"
                            fontSize={width < 250 ? 9 : width < 300 ? 10 : 12}
                            textAnchor="middle"
                            className="fill-white font-medium"
                          >
                            {percentage.toFixed(0)}%
                          </text>
                        )}
                      </Group>
                    );
                  })
                }
              </Pie>
            </Group>
          </svg>
        </div>

        {/* Legend - Smart responsive positioning */}
        {showLegend && containerWidth > 250 && (
          <div className={containerWidth > 450 ? "" : "mt-3"}>
            {containerWidth > 450 ? (
              // Side-by-side legend for medium+ containers
              <div className="space-y-2">
                <h4 className="text-sm font-medium text-gray-900 mb-2">Breakdown</h4>
                <div className="space-y-1.5">
                  {dataWithPercentages.map((item, index) => (
                    <div key={item.label} className="flex items-center justify-between text-sm">
                      <div className="flex items-center gap-2 min-w-0">
                        <div 
                          className="w-3 h-3 rounded-full flex-shrink-0"
                          style={{ backgroundColor: item.color }}
                        />
                        <span className="text-gray-700 truncate">{item.label}</span>
                      </div>
                      <div className="text-right ml-2 flex-shrink-0">
                        <div className="text-gray-900 font-medium">{formatValue(item.value)}</div>
                        <div className="text-gray-500 text-xs">{item.percentage.toFixed(1)}%</div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              // Compact horizontal legend below for narrow containers
              <div className="space-y-1">
                <h4 className="text-xs font-medium text-gray-900">Breakdown</h4>
                <div className="flex flex-wrap gap-x-3 gap-y-1">
                  {dataWithPercentages.map((item, index) => (
                    <div key={item.label} className="flex items-center gap-1.5 text-xs">
                      <div 
                        className="w-2.5 h-2.5 rounded-full flex-shrink-0"
                        style={{ backgroundColor: item.color }}
                      />
                      <span className="text-gray-700 truncate max-w-16">
                        {item.label.length > 8 ? item.label.slice(0, 8) + '...' : item.label}
                      </span>
                      <span className="text-gray-600 font-medium">{item.percentage.toFixed(0)}%</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Summary stats for larger charts */}
      {width > 400 && (
        <div className="px-6 py-4 border-t border-gray-100 bg-gray-50">
          <div className="grid grid-cols-3 gap-4 text-sm">
            <div>
              <div className="text-gray-600">Total Value</div>
              <div className="font-semibold text-gray-900">{formatValue(total)}</div>
            </div>
            <div>
              <div className="text-gray-600">Largest Segment</div>
              <div className="font-semibold text-gray-900">
                {dataWithPercentages.reduce((max, d) => d.value > max.value ? d : max).label}
              </div>
            </div>
            <div>
              <div className="text-gray-600">Categories</div>
              <div className="font-semibold text-gray-900">{data.length}</div>
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
            <div className="font-semibold">{tooltipData.label}</div>
            <div>{formatValue(tooltipData.value)}</div>
            <div className="text-xs text-gray-300">{tooltipData.percentage.toFixed(1)}%</div>
          </div>
        </TooltipInPortal>
      )}
    </div>
  );
}