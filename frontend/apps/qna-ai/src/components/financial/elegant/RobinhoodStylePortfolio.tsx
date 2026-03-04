'use client';

import React, { useMemo } from 'react';
import { Group } from '@visx/group';
import { AreaClosed, LinePath } from '@visx/shape';
import { curveCardinal } from '@visx/curve';
import { LinearGradient } from '@visx/gradient';
import { scaleTime, scaleLinear } from '@visx/scale';
import { AxisBottom, AxisLeft } from '@visx/axis';
import { ParentSize } from '@visx/responsive';

interface DataPoint {
  date: Date;
  value: number;
  benchmark?: number;
}

interface RobinhoodStylePortfolioProps {
  data: DataPoint[];
  currentValue: number;
  dayChange: number;
  dayChangePercent: number;
  title?: string;
  showBenchmark?: boolean;
  height?: number;
}

export function RobinhoodStylePortfolio({
  data,
  currentValue,
  dayChange,
  dayChangePercent,
  title = "Portfolio",
  showBenchmark = true,
  height = 400
}: RobinhoodStylePortfolioProps) {
  const isPositive = dayChange >= 0;
  
  return (
    <div className="w-full">
      {/* Header - Robinhood Style */}
      <div className="px-6 pt-8 pb-6">
        <div className="flex items-baseline space-x-4 mb-2">
          <h1 className="text-3xl font-light text-gray-900 tracking-tight">
            ${currentValue.toLocaleString('en-US', { 
              minimumFractionDigits: 2,
              maximumFractionDigits: 2 
            })}
          </h1>
          <div className={`flex items-center space-x-1 text-lg font-medium ${
            isPositive ? 'text-emerald-500' : 'text-red-500'
          }`}>
            <span>{isPositive ? '+' : ''}${Math.abs(dayChange).toFixed(2)}</span>
            <span>({isPositive ? '+' : ''}{dayChangePercent.toFixed(2)}%)</span>
          </div>
        </div>
        <p className="text-gray-500 text-sm font-medium">Today</p>
      </div>

      {/* Chart Area - Clean and Modern */}
      <div className="relative">
        <ParentSize>
          {({ width }) => (
            <ElegantChart
              data={data}
              width={width}
              height={height}
              showBenchmark={showBenchmark}
              isPositive={isPositive}
            />
          )}
        </ParentSize>
      </div>

      {/* Time Period Selector - TradingView Style */}
      <div className="px-6 py-4">
        <div className="flex space-x-1">
          {['1D', '1W', '1M', '3M', '1Y', 'ALL'].map((period, idx) => (
            <button
              key={period}
              className={`px-3 py-1.5 text-sm font-medium rounded-full transition-colors ${
                idx === 2 
                  ? 'bg-gray-900 text-white' 
                  : 'text-gray-500 hover:text-gray-900 hover:bg-gray-100'
              }`}
            >
              {period}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}

interface ElegantChartProps {
  data: DataPoint[];
  width: number;
  height: number;
  showBenchmark: boolean;
  isPositive: boolean;
}

function ElegantChart({ data, width, height, showBenchmark, isPositive }: ElegantChartProps) {
  const margin = { top: 20, right: 20, bottom: 40, left: 60 };
  const chartWidth = width - margin.left - margin.right;
  const chartHeight = height - margin.top - margin.bottom;

  // Accessors
  const getDate = (d: DataPoint) => d.date;
  const getValue = (d: DataPoint) => d.value;
  const getBenchmark = (d: DataPoint) => d.benchmark || 0;

  // Scales
  const timeScale = useMemo(
    () =>
      scaleTime<number>({
        range: [0, chartWidth],
        domain: [
          Math.min(...data.map(getDate)) as any,
          Math.max(...data.map(getDate)) as any,
        ],
      }),
    [chartWidth, data]
  );

  const valueScale = useMemo(() => {
    const allValues = data.flatMap(d => [getValue(d), getBenchmark(d)]);
    const min = Math.min(...allValues);
    const max = Math.max(...allValues);
    const padding = (max - min) * 0.1;
    
    return scaleLinear<number>({
      range: [chartHeight, 0],
      domain: [min - padding, max + padding],
      nice: true,
    });
  }, [chartHeight, data]);

  // Colors - Robinhood/TradingView style
  const portfolioColor = isPositive ? '#10B981' : '#EF4444';
  const benchmarkColor = '#6B7280';

  return (
    <svg width={width} height={height}>
      <defs>
        <LinearGradient
          id="portfolio-gradient"
          from={portfolioColor}
          fromOpacity={0.3}
          to={portfolioColor}
          toOpacity={0.05}
        />
        <LinearGradient
          id="benchmark-gradient"
          from={benchmarkColor}
          fromOpacity={0.2}
          to={benchmarkColor}
          toOpacity={0.02}
        />
      </defs>
      
      <Group left={margin.left} top={margin.top}>
        {/* Benchmark Area (behind) */}
        {showBenchmark && (
          <>
            <AreaClosed
              data={data}
              x={d => timeScale(getDate(d))}
              y={d => valueScale(getBenchmark(d))}
              yScale={valueScale}
              fill="url(#benchmark-gradient)"
              curve={curveCardinal}
            />
            <LinePath
              data={data}
              x={d => timeScale(getDate(d))}
              y={d => valueScale(getBenchmark(d))}
              stroke={benchmarkColor}
              strokeWidth={1.5}
              strokeOpacity={0.6}
              curve={curveCardinal}
            />
          </>
        )}

        {/* Portfolio Area (foreground) */}
        <AreaClosed
          data={data}
          x={d => timeScale(getDate(d))}
          y={d => valueScale(getValue(d))}
          yScale={valueScale}
          fill="url(#portfolio-gradient)"
          curve={curveCardinal}
        />
        
        <LinePath
          data={data}
          x={d => timeScale(getDate(d))}
          y={d => valueScale(getValue(d))}
          stroke={portfolioColor}
          strokeWidth={2.5}
          curve={curveCardinal}
        />

        {/* Clean Axes - Minimal Style */}
        <AxisBottom
          top={chartHeight}
          scale={timeScale}
          numTicks={width > 520 ? 5 : 3}
          stroke="transparent"
          tickStroke="#E5E7EB"
          tickLabelProps={() => ({
            fill: '#9CA3AF',
            fontSize: 12,
            fontWeight: 500,
            textAnchor: 'middle',
          })}
        />
        
        <AxisLeft
          scale={valueScale}
          numTicks={4}
          stroke="transparent"
          tickStroke="#E5E7EB"
          tickLabelProps={() => ({
            fill: '#9CA3AF',
            fontSize: 12,
            fontWeight: 500,
            textAnchor: 'end',
          })}
          tickFormat={(value) => `$${(value as number).toLocaleString()}`}
        />
      </Group>
    </svg>
  );
}

// Sample component with metrics - Clean Layout
interface PortfolioMetricsProps {
  metrics: {
    totalReturn: number;
    dayChange: number;
    dayChangePercent: number;
    sharpeRatio?: number;
    maxDrawdown?: number;
    ytdReturn?: number;
  };
}

export function ElegantPortfolioMetrics({ metrics }: PortfolioMetricsProps) {
  const isPositive = metrics.dayChange >= 0;
  
  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-6 px-6 py-4">
      {/* Total Return */}
      <div className="space-y-1">
        <p className="text-sm font-medium text-gray-500">Total Return</p>
        <p className={`text-xl font-semibold ${
          metrics.totalReturn >= 0 ? 'text-emerald-600' : 'text-red-600'
        }`}>
          {metrics.totalReturn >= 0 ? '+' : ''}{metrics.totalReturn.toFixed(1)}%
        </p>
      </div>

      {/* YTD Return */}
      {metrics.ytdReturn !== undefined && (
        <div className="space-y-1">
          <p className="text-sm font-medium text-gray-500">YTD</p>
          <p className={`text-xl font-semibold ${
            metrics.ytdReturn >= 0 ? 'text-emerald-600' : 'text-red-600'
          }`}>
            {metrics.ytdReturn >= 0 ? '+' : ''}{metrics.ytdReturn.toFixed(1)}%
          </p>
        </div>
      )}

      {/* Sharpe Ratio */}
      {metrics.sharpeRatio !== undefined && (
        <div className="space-y-1">
          <p className="text-sm font-medium text-gray-500">Sharpe Ratio</p>
          <p className="text-xl font-semibold text-gray-900">
            {metrics.sharpeRatio.toFixed(2)}
          </p>
        </div>
      )}

      {/* Max Drawdown */}
      {metrics.maxDrawdown !== undefined && (
        <div className="space-y-1">
          <p className="text-sm font-medium text-gray-500">Max Drawdown</p>
          <p className="text-xl font-semibold text-red-600">
            {metrics.maxDrawdown.toFixed(1)}%
          </p>
        </div>
      )}
    </div>
  );
}