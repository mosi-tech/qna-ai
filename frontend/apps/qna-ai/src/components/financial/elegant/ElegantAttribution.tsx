'use client';

import React, { useMemo } from 'react';
import { Group } from '@visx/group';
import { Bar } from '@visx/shape';
import { scaleBand, scaleLinear } from '@visx/scale';
import { AxisBottom, AxisLeft } from '@visx/axis';
import { LinearGradient } from '@visx/gradient';
import { Text } from '@visx/text';

interface AttributionFactor {
  name: string;
  selection: number;  // Stock selection contribution
  allocation: number; // Asset allocation contribution
  interaction: number; // Interaction effect
  total: number; // Total contribution
  description?: string;
  category?: 'sector' | 'factor' | 'style' | 'geography';
}

interface ElegantAttributionProps {
  factors: AttributionFactor[];
  totalAlpha: number;
  benchmarkReturn: number;
  portfolioReturn: number;
  title?: string;
  timeframe?: string;
  height?: number;
}

export function ElegantAttribution({
  factors,
  totalAlpha,
  benchmarkReturn,
  portfolioReturn,
  title = "Performance Attribution",
  timeframe = "Last 12 Months",
  height = 500
}: ElegantAttributionProps) {
  const width = 800;
  const margin = { top: 40, right: 120, bottom: 60, left: 100 };
  const chartWidth = width - margin.left - margin.right;
  const chartHeight = height - margin.top - margin.bottom;

  // Sort factors by total contribution
  const sortedFactors = [...factors].sort((a, b) => b.total - a.total);
  
  // Create scales
  const yScale = scaleBand({
    range: [chartHeight, 0],
    domain: sortedFactors.map(d => d.name),
    padding: 0.3
  });

  const maxContribution = Math.max(...sortedFactors.flatMap(d => [
    Math.abs(d.selection), Math.abs(d.allocation), Math.abs(d.total)
  ]));

  const xScale = scaleLinear({
    range: [0, chartWidth],
    domain: [-maxContribution * 1.2, maxContribution * 1.2],
    nice: true
  });

  return (
    <div className="w-full space-y-8">
      {/* Header Section */}
      <div className="text-center space-y-4">
        <h1 className="text-3xl font-light text-gray-900">{title}</h1>
        <div className="flex items-center justify-center space-x-8 text-sm">
          <div className="flex items-center space-x-2">
            <span className="text-gray-600">Portfolio:</span>
            <span className="font-semibold text-blue-600">
              {portfolioReturn.toFixed(2)}%
            </span>
          </div>
          <div className="flex items-center space-x-2">
            <span className="text-gray-600">Benchmark:</span>
            <span className="font-semibold text-gray-600">
              {benchmarkReturn.toFixed(2)}%
            </span>
          </div>
          <div className="flex items-center space-x-2">
            <span className="text-gray-600">Alpha:</span>
            <span className={`font-bold text-lg ${
              totalAlpha >= 0 ? 'text-emerald-600' : 'text-red-600'
            }`}>
              {totalAlpha >= 0 ? '+' : ''}{totalAlpha.toFixed(2)}%
            </span>
          </div>
        </div>
        <p className="text-gray-500">{timeframe}</p>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <AttributionSummaryCard
          title="Stock Selection"
          value={sortedFactors.reduce((sum, f) => sum + f.selection, 0)}
          description="Alpha from individual security picks"
        />
        <AttributionSummaryCard
          title="Asset Allocation"
          value={sortedFactors.reduce((sum, f) => sum + f.allocation, 0)}
          description="Alpha from sector/style timing"
        />
        <AttributionSummaryCard
          title="Interaction Effects"
          value={sortedFactors.reduce((sum, f) => sum + f.interaction, 0)}
          description="Combined allocation & selection"
        />
      </div>

      {/* Attribution Chart */}
      <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-100">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold text-gray-900">
              Factor Attribution Breakdown
            </h3>
            <div className="flex items-center space-x-4 text-xs">
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 rounded bg-blue-500"></div>
                <span>Selection</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 rounded bg-emerald-500"></div>
                <span>Allocation</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 rounded bg-purple-500"></div>
                <span>Total</span>
              </div>
            </div>
          </div>
        </div>
        
        <div className="p-6">
          <svg width="100%" height={height} viewBox={`0 0 ${width} ${height}`}>
            <defs>
              <LinearGradient id="selection-gradient" from="#3B82F6" to="#1D4ED8" />
              <LinearGradient id="allocation-gradient" from="#10B981" to="#047857" />
              <LinearGradient id="total-gradient" from="#8B5CF6" to="#7C3AED" />
            </defs>
            
            <Group left={margin.left} top={margin.top}>
              {/* Zero line */}
              <line
                x1={xScale(0)}
                x2={xScale(0)}
                y1={0}
                y2={chartHeight}
                stroke="#E5E7EB"
                strokeWidth={2}
              />

              {sortedFactors.map((factor, index) => {
                const y = yScale(factor.name) || 0;
                const barHeight = yScale.bandwidth();
                
                return (
                  <Group key={factor.name}>
                    {/* Selection Effect Bar */}
                    <Bar
                      x={factor.selection >= 0 ? xScale(0) : xScale(factor.selection)}
                      y={y}
                      width={Math.abs(xScale(factor.selection) - xScale(0))}
                      height={barHeight * 0.25}
                      fill="url(#selection-gradient)"
                      rx={2}
                    />
                    
                    {/* Allocation Effect Bar */}
                    <Bar
                      x={factor.allocation >= 0 ? xScale(0) : xScale(factor.allocation)}
                      y={y + barHeight * 0.3}
                      width={Math.abs(xScale(factor.allocation) - xScale(0))}
                      height={barHeight * 0.25}
                      fill="url(#allocation-gradient)"
                      rx={2}
                    />
                    
                    {/* Total Effect Bar (thicker) */}
                    <Bar
                      x={factor.total >= 0 ? xScale(0) : xScale(factor.total)}
                      y={y + barHeight * 0.65}
                      width={Math.abs(xScale(factor.total) - xScale(0))}
                      height={barHeight * 0.3}
                      fill="url(#total-gradient)"
                      rx={2}
                    />

                    {/* Value labels */}
                    <Text
                      x={xScale(factor.total) + (factor.total >= 0 ? 8 : -8)}
                      y={y + barHeight * 0.8}
                      fontSize={12}
                      fontWeight="600"
                      fill={factor.total >= 0 ? '#10B981' : '#EF4444'}
                      textAnchor={factor.total >= 0 ? 'start' : 'end'}
                      dy="0.33em"
                    >
                      {factor.total >= 0 ? '+' : ''}{factor.total.toFixed(2)}%
                    </Text>
                  </Group>
                );
              })}

              {/* Y-Axis (factor names) */}
              <AxisLeft
                scale={yScale}
                stroke="transparent"
                tickStroke="transparent"
                tickLabelProps={() => ({
                  fill: '#374151',
                  fontSize: 14,
                  fontWeight: '500',
                  textAnchor: 'end',
                  dy: '0.33em'
                })}
              />

              {/* X-Axis */}
              <AxisBottom
                top={chartHeight}
                scale={xScale}
                stroke="#E5E7EB"
                tickStroke="#E5E7EB"
                numTicks={6}
                tickLabelProps={() => ({
                  fill: '#6B7280',
                  fontSize: 12,
                  textAnchor: 'middle'
                })}
                tickFormat={(value) => `${value}%`}
              />
            </Group>
          </svg>
        </div>
      </div>

      {/* Detailed Attribution Table */}
      <AttributionDetailTable factors={sortedFactors} />

      {/* Insights */}
      <AttributionInsights factors={sortedFactors} totalAlpha={totalAlpha} />
    </div>
  );
}

// Attribution Summary Card
function AttributionSummaryCard({
  title,
  value,
  description
}: {
  title: string;
  value: number;
  description: string;
}) {
  return (
    <div className="bg-gradient-to-br from-white to-gray-50 rounded-xl p-6 border border-gray-200 shadow-sm">
      <div className="text-center">
        <div className={`text-3xl font-bold mb-2 ${
          value >= 0 ? 'text-emerald-600' : 'text-red-600'
        }`}>
          {value >= 0 ? '+' : ''}{value.toFixed(2)}%
        </div>
        <h3 className="font-semibold text-gray-900 mb-2">{title}</h3>
        <p className="text-sm text-gray-600">{description}</p>
      </div>
    </div>
  );
}

// Attribution Detail Table
function AttributionDetailTable({ factors }: { factors: AttributionFactor[] }) {
  return (
    <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
      <div className="px-6 py-4 border-b border-gray-100">
        <h3 className="text-lg font-semibold text-gray-900">
          Detailed Attribution Analysis
        </h3>
      </div>
      
      <div className="overflow-x-auto">
        <table className="min-w-full">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Factor
              </th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                Selection
              </th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                Allocation
              </th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                Interaction
              </th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                Total
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Impact
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {factors.map((factor, index) => (
              <tr key={factor.name} className="hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap">
                  <div>
                    <div className="text-sm font-semibold text-gray-900">
                      {factor.name}
                    </div>
                    {factor.description && (
                      <div className="text-xs text-gray-500">
                        {factor.description}
                      </div>
                    )}
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right">
                  <ContributionCell value={factor.selection} />
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right">
                  <ContributionCell value={factor.allocation} />
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right">
                  <ContributionCell value={factor.interaction} />
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right">
                  <div className={`text-sm font-bold ${
                    factor.total >= 0 ? 'text-emerald-600' : 'text-red-600'
                  }`}>
                    {factor.total >= 0 ? '+' : ''}{factor.total.toFixed(2)}%
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <ImpactIndicator value={factor.total} />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

// Contribution Cell Component
function ContributionCell({ value }: { value: number }) {
  return (
    <div className={`text-sm ${
      value >= 0 ? 'text-emerald-600' : 'text-red-600'
    }`}>
      {value >= 0 ? '+' : ''}{value.toFixed(2)}%
    </div>
  );
}

// Impact Indicator Component
function ImpactIndicator({ value }: { value: number }) {
  const absValue = Math.abs(value);
  const impact = absValue >= 1.0 ? 'High' : absValue >= 0.5 ? 'Medium' : 'Low';
  const color = value >= 0 ? 'emerald' : 'red';
  
  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-${color}-100 text-${color}-800`}>
      {impact}
    </span>
  );
}

// Attribution Insights Component
function AttributionInsights({ 
  factors, 
  totalAlpha 
}: { 
  factors: AttributionFactor[]; 
  totalAlpha: number; 
}) {
  const insights = useMemo(() => {
    const bestSelection = factors.reduce((max, f) => f.selection > max.selection ? f : max);
    const worstSelection = factors.reduce((min, f) => f.selection < min.selection ? f : min);
    const bestAllocation = factors.reduce((max, f) => f.allocation > max.allocation ? f : max);
    
    const selectionContrib = factors.reduce((sum, f) => sum + f.selection, 0);
    const allocationContrib = factors.reduce((sum, f) => sum + f.allocation, 0);
    
    return {
      primaryDriver: Math.abs(selectionContrib) > Math.abs(allocationContrib) ? 'Stock Selection' : 'Asset Allocation',
      bestSelection,
      worstSelection,
      bestAllocation,
      selectionDominance: (Math.abs(selectionContrib) / Math.abs(totalAlpha)) * 100
    };
  }, [factors, totalAlpha]);

  return (
    <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-2xl p-8 border border-blue-100">
      <h3 className="text-xl font-semibold text-gray-900 mb-6">Key Insights</h3>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="space-y-4">
          <div>
            <h4 className="font-semibold text-gray-800 mb-2">Primary Alpha Driver</h4>
            <p className="text-gray-700">
              <span className="font-medium text-blue-600">{insights.primaryDriver}</span> was the 
              primary source of alpha generation, accounting for approximately{' '}
              <span className="font-medium">{insights.selectionDominance.toFixed(0)}%</span> of total outperformance.
            </p>
          </div>
          
          <div>
            <h4 className="font-semibold text-gray-800 mb-2">Best Performers</h4>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span>Selection:</span>
                <span className="font-medium text-emerald-600">
                  {insights.bestSelection.name} (+{insights.bestSelection.selection.toFixed(2)}%)
                </span>
              </div>
              <div className="flex justify-between">
                <span>Allocation:</span>
                <span className="font-medium text-emerald-600">
                  {insights.bestAllocation.name} (+{insights.bestAllocation.allocation.toFixed(2)}%)
                </span>
              </div>
            </div>
          </div>
        </div>
        
        <div className="space-y-4">
          <div>
            <h4 className="font-semibold text-gray-800 mb-2">Performance Summary</h4>
            <p className="text-gray-700">
              The portfolio generated <span className="font-medium text-blue-600">{totalAlpha.toFixed(2)}%</span> of 
              alpha through active management decisions across {factors.length} key factors.
            </p>
          </div>
          
          <div>
            <h4 className="font-semibold text-gray-800 mb-2">Biggest Detractor</h4>
            <div className="text-sm">
              <span className="font-medium text-red-600">
                {insights.worstSelection.name}
              </span> selection effect was the largest drag on performance 
              ({insights.worstSelection.selection.toFixed(2)}% contribution).
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}