'use client';

import React, { useMemo, useState } from 'react';
import { Group } from '@visx/group';
import { LinePath, AreaClosed, Circle } from '@visx/shape';
import { curveCardinal, curveLinear } from '@visx/curve';
import { LinearGradient } from '@visx/gradient';
import { scaleTime, scaleLinear } from '@visx/scale';
import { AxisBottom, AxisLeft } from '@visx/axis';
import { Tooltip, TooltipWithBounds } from '@visx/tooltip';
import { localPoint } from '@visx/event';
import { bisector } from '@visx/vendor/d3-array';

interface ReturnDataPoint {
  date: Date;
  portfolio: number;
  benchmark?: number;
  drawdown?: number;
}

interface ElegantCumulativeReturnsProps {
  portfolio: ReturnDataPoint[];
  benchmark?: ReturnDataPoint[];
  title?: string;
  portfolioLabel?: string;
  benchmarkLabel?: string;
  height?: number;
  showDrawdown?: boolean;
  showVolatility?: boolean;
  annotations?: Array<{
    date: Date;
    label: string;
    description?: string;
  }>;
}

export function ElegantCumulativeReturns({
  portfolio,
  benchmark = [],
  title = "Cumulative Performance",
  portfolioLabel = "Portfolio",
  benchmarkLabel = "Benchmark",
  height = 500,
  showDrawdown = true,
  showVolatility = false,
  annotations = []
}: ElegantCumulativeReturnsProps) {
  const [tooltipData, setTooltipData] = useState<ReturnDataPoint | null>(null);
  const [tooltipLeft, setTooltipLeft] = useState(0);
  const [tooltipTop, setTooltipTop] = useState(0);

  const width = 800;
  const margin = { top: 20, right: 80, bottom: 60, left: 80 };
  const chartWidth = width - margin.left - margin.right;
  const chartHeight = height - margin.top - margin.bottom;

  // Calculate performance metrics
  const metrics = useMemo(() => {
    if (portfolio.length === 0) return null;
    
    const startValue = portfolio[0].portfolio;
    const endValue = portfolio[portfolio.length - 1].portfolio;
    const totalReturn = ((endValue - startValue) / startValue) * 100;
    
    const benchmarkReturn = benchmark.length > 0 
      ? ((benchmark[benchmark.length - 1].portfolio - benchmark[0].portfolio) / benchmark[0].portfolio) * 100
      : undefined;
    
    const outperformance = benchmarkReturn ? totalReturn - benchmarkReturn : undefined;
    
    // Calculate volatility (simplified)
    const returns = portfolio.slice(1).map((d, i) => 
      ((d.portfolio - portfolio[i].portfolio) / portfolio[i].portfolio) * 100
    );
    const avgReturn = returns.reduce((sum, r) => sum + r, 0) / returns.length;
    const variance = returns.reduce((sum, r) => sum + Math.pow(r - avgReturn, 2), 0) / returns.length;
    const volatility = Math.sqrt(variance * 252); // Annualized

    return {
      totalReturn,
      benchmarkReturn,
      outperformance,
      volatility,
      periods: portfolio.length,
      sharpe: totalReturn / volatility
    };
  }, [portfolio, benchmark]);

  // Create scales
  const timeExtent = useMemo(() => {
    const allDates = [...portfolio, ...benchmark].map(d => d.date);
    return [Math.min(...allDates), Math.max(...allDates)] as [Date, Date];
  }, [portfolio, benchmark]);

  const valueExtent = useMemo(() => {
    const allValues = [...portfolio, ...benchmark].map(d => d.portfolio);
    return [Math.min(...allValues), Math.max(...allValues)] as [number, number];
  }, [portfolio, benchmark]);

  const timeScale = scaleTime({
    range: [0, chartWidth],
    domain: timeExtent
  });

  const valueScale = scaleLinear({
    range: [chartHeight, 0],
    domain: valueExtent,
    nice: true
  });

  // Tooltip handlers
  const bisectDate = bisector<ReturnDataPoint, Date>(d => d.date).left;
  
  const handleTooltip = (event: any) => {
    const { x } = localPoint(event) || { x: 0 };
    const x0 = timeScale.invert(x - margin.left);
    const index = bisectDate(portfolio, x0, 1);
    const d0 = portfolio[index - 1];
    const d1 = portfolio[index];
    let d = d0;
    if (d1 && d0) {
      d = x0.valueOf() - d0.date.valueOf() > d1.date.valueOf() - x0.valueOf() ? d1 : d0;
    }
    setTooltipData(d);
    setTooltipLeft(timeScale(d.date));
    setTooltipTop(valueScale(d.portfolio));
  };

  return (
    <div className="w-full">
      {/* Header with Key Metrics */}
      <div className="mb-6">
        <h2 className="text-2xl font-light text-gray-900 mb-4">{title}</h2>
        
        {metrics && (
          <div className="grid grid-cols-2 lg:grid-cols-5 gap-4 mb-4">
            <div className="bg-gradient-to-r from-blue-50 to-blue-100 p-4 rounded-lg border border-blue-200">
              <div className="text-lg font-bold text-blue-600">
                {metrics.totalReturn >= 0 ? '+' : ''}{metrics.totalReturn.toFixed(1)}%
              </div>
              <div className="text-xs text-blue-700">Total Return</div>
            </div>
            
            {metrics.outperformance && (
              <div className={`p-4 rounded-lg border ${
                metrics.outperformance >= 0 
                  ? 'bg-gradient-to-r from-emerald-50 to-emerald-100 border-emerald-200'
                  : 'bg-gradient-to-r from-red-50 to-red-100 border-red-200'
              }`}>
                <div className={`text-lg font-bold ${
                  metrics.outperformance >= 0 ? 'text-emerald-600' : 'text-red-600'
                }`}>
                  {metrics.outperformance >= 0 ? '+' : ''}{metrics.outperformance.toFixed(1)}%
                </div>
                <div className={`text-xs ${
                  metrics.outperformance >= 0 ? 'text-emerald-700' : 'text-red-700'
                }`}>
                  vs {benchmarkLabel}
                </div>
              </div>
            )}
            
            <div className="bg-gradient-to-r from-purple-50 to-purple-100 p-4 rounded-lg border border-purple-200">
              <div className="text-lg font-bold text-purple-600">
                {metrics.volatility.toFixed(1)}%
              </div>
              <div className="text-xs text-purple-700">Volatility</div>
            </div>
            
            <div className="bg-gradient-to-r from-orange-50 to-orange-100 p-4 rounded-lg border border-orange-200">
              <div className="text-lg font-bold text-orange-600">
                {metrics.sharpe.toFixed(2)}
              </div>
              <div className="text-xs text-orange-700">Sharpe Ratio</div>
            </div>
            
            <div className="bg-gradient-to-r from-gray-50 to-gray-100 p-4 rounded-lg border border-gray-200">
              <div className="text-lg font-bold text-gray-600">
                {metrics.periods}
              </div>
              <div className="text-xs text-gray-700">Data Points</div>
            </div>
          </div>
        )}
      </div>

      {/* Chart Container */}
      <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-100">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold text-gray-900">Performance Chart</h3>
            <div className="flex items-center space-x-4 text-sm">
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
                <span>{portfolioLabel}</span>
              </div>
              {benchmark.length > 0 && (
                <div className="flex items-center space-x-2">
                  <div className="w-3 h-3 bg-gray-500 rounded-full"></div>
                  <span>{benchmarkLabel}</span>
                </div>
              )}
            </div>
          </div>
        </div>
        
        <div className="relative">
          <svg 
            width="100%" 
            height={height} 
            viewBox={`0 0 ${width} ${height}`}
            onMouseMove={handleTooltip}
            onMouseLeave={() => setTooltipData(null)}
          >
            <defs>
              <LinearGradient 
                id="portfolio-gradient" 
                from="#3B82F6" 
                to="#3B82F6" 
                fromOpacity={0.3} 
                toOpacity={0} 
              />
              <LinearGradient 
                id="benchmark-gradient" 
                from="#6B7280" 
                to="#6B7280" 
                fromOpacity={0.2} 
                toOpacity={0} 
              />
            </defs>
            
            <Group left={margin.left} top={margin.top}>
              {/* Grid lines */}
              {valueScale.ticks(6).map(tick => (
                <line
                  key={tick}
                  x1={0}
                  x2={chartWidth}
                  y1={valueScale(tick)}
                  y2={valueScale(tick)}
                  stroke="#F3F4F6"
                  strokeWidth={1}
                />
              ))}

              {/* Benchmark area and line */}
              {benchmark.length > 0 && (
                <>
                  <AreaClosed
                    data={benchmark}
                    x={d => timeScale(d.date)}
                    y={d => valueScale(d.portfolio)}
                    yScale={valueScale}
                    fill="url(#benchmark-gradient)"
                    curve={curveCardinal}
                  />
                  <LinePath
                    data={benchmark}
                    x={d => timeScale(d.date)}
                    y={d => valueScale(d.portfolio)}
                    stroke="#6B7280"
                    strokeWidth={2}
                    curve={curveCardinal}
                  />
                </>
              )}

              {/* Portfolio area and line */}
              <AreaClosed
                data={portfolio}
                x={d => timeScale(d.date)}
                y={d => valueScale(d.portfolio)}
                yScale={valueScale}
                fill="url(#portfolio-gradient)"
                curve={curveCardinal}
              />
              
              <LinePath
                data={portfolio}
                x={d => timeScale(d.date)}
                y={d => valueScale(d.portfolio)}
                stroke="#3B82F6"
                strokeWidth={3}
                curve={curveCardinal}
              />

              {/* Annotations */}
              {annotations.map((annotation, i) => (
                <Group key={i}>
                  <line
                    x1={timeScale(annotation.date)}
                    x2={timeScale(annotation.date)}
                    y1={0}
                    y2={chartHeight}
                    stroke="#F59E0B"
                    strokeWidth={2}
                    strokeDasharray="4,4"
                    opacity={0.7}
                  />
                  <Circle
                    cx={timeScale(annotation.date)}
                    cy={20}
                    r={4}
                    fill="#F59E0B"
                  />
                  <text
                    x={timeScale(annotation.date)}
                    y={15}
                    fontSize={10}
                    fontWeight="600"
                    fill="#D97706"
                    textAnchor="middle"
                  >
                    {annotation.label}
                  </text>
                </Group>
              ))}

              {/* Tooltip crosshair */}
              {tooltipData && (
                <Group>
                  <line
                    x1={tooltipLeft}
                    x2={tooltipLeft}
                    y1={0}
                    y2={chartHeight}
                    stroke="#9CA3AF"
                    strokeWidth={1}
                    strokeDasharray="3,3"
                  />
                  <Circle
                    cx={tooltipLeft}
                    cy={tooltipTop}
                    r={4}
                    fill="#3B82F6"
                    stroke="white"
                    strokeWidth={2}
                  />
                </Group>
              )}

              {/* Axes */}
              <AxisBottom
                top={chartHeight}
                scale={timeScale}
                numTicks={6}
                stroke="transparent"
                tickStroke="#E5E7EB"
                tickLabelProps={() => ({
                  fill: '#6B7280',
                  fontSize: 12,
                  textAnchor: 'middle'
                })}
              />
              
              <AxisLeft
                scale={valueScale}
                numTicks={6}
                stroke="transparent"
                tickStroke="#E5E7EB"
                tickLabelProps={() => ({
                  fill: '#6B7280',
                  fontSize: 12,
                  textAnchor: 'end'
                })}
                tickFormat={(value) => {
                  if (typeof value === 'number') {
                    return value >= 1000 ? `$${(value/1000).toFixed(1)}K` : `$${value.toFixed(0)}`;
                  }
                  return '';
                }}
              />
            </Group>
          </svg>

          {/* Tooltip */}
          {tooltipData && (
            <TooltipWithBounds
              left={tooltipLeft + margin.left}
              top={tooltipTop + margin.top}
              style={{
                backgroundColor: 'white',
                border: '1px solid #E5E7EB',
                borderRadius: '8px',
                padding: '12px',
                fontSize: '14px',
                boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
              }}
            >
              <div className="space-y-2">
                <div className="font-semibold text-gray-900">
                  {tooltipData.date.toLocaleDateString()}
                </div>
                <div className="text-blue-600">
                  {portfolioLabel}: ${tooltipData.portfolio.toLocaleString()}
                </div>
                {tooltipData.benchmark && (
                  <div className="text-gray-600">
                    {benchmarkLabel}: ${tooltipData.benchmark.toLocaleString()}
                  </div>
                )}
                {tooltipData.drawdown && (
                  <div className="text-red-600">
                    Drawdown: {tooltipData.drawdown.toFixed(1)}%
                  </div>
                )}
              </div>
            </TooltipWithBounds>
          )}
        </div>
      </div>

      {/* Performance Summary */}
      <div className="mt-6 p-6 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-2xl border border-blue-200">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Performance Summary</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h4 className="font-medium text-gray-800 mb-2">Return Analysis</h4>
            <p className="text-sm text-gray-700">
              {getReturnAnalysis(metrics?.totalReturn || 0, metrics?.outperformance)}
            </p>
          </div>
          <div>
            <h4 className="font-medium text-gray-800 mb-2">Risk Assessment</h4>
            <p className="text-sm text-gray-700">
              {getRiskAnalysis(metrics?.volatility || 0, metrics?.sharpe || 0)}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

// Utility Functions
function getReturnAnalysis(totalReturn: number, outperformance?: number): string {
  let analysis = `The portfolio generated a ${totalReturn.toFixed(1)}% total return over the period. `;
  
  if (totalReturn >= 20) {
    analysis += "This represents exceptional performance well above market averages.";
  } else if (totalReturn >= 10) {
    analysis += "This demonstrates strong performance meeting institutional expectations.";
  } else if (totalReturn >= 5) {
    analysis += "This shows solid performance in line with reasonable return targets.";
  } else if (totalReturn >= 0) {
    analysis += "This indicates modest positive performance with room for improvement.";
  } else {
    analysis += "Negative performance requires careful strategy review and risk assessment.";
  }

  if (outperformance !== undefined) {
    analysis += ` The portfolio ${outperformance >= 0 ? 'outperformed' : 'underperformed'} the benchmark by ${Math.abs(outperformance).toFixed(1)}%.`;
  }

  return analysis;
}

function getRiskAnalysis(volatility: number, sharpe: number): string {
  let analysis = `Portfolio volatility of ${volatility.toFixed(1)}% indicates `;
  
  if (volatility <= 10) {
    analysis += "low risk with conservative characteristics. ";
  } else if (volatility <= 20) {
    analysis += "moderate risk appropriate for balanced strategies. ";
  } else if (volatility <= 30) {
    analysis += "elevated risk requiring active monitoring. ";
  } else {
    analysis += "high risk demanding careful risk management. ";
  }

  analysis += `The Sharpe ratio of ${sharpe.toFixed(2)} suggests `;
  
  if (sharpe >= 1.5) {
    analysis += "excellent risk-adjusted returns.";
  } else if (sharpe >= 1.0) {
    analysis += "good risk efficiency.";
  } else if (sharpe >= 0.5) {
    analysis += "moderate risk-adjusted performance.";
  } else {
    analysis += "below-average risk efficiency requiring optimization.";
  }

  return analysis;
}