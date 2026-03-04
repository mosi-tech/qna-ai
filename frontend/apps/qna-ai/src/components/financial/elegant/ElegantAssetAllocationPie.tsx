'use client';

import React, { useMemo, useState } from 'react';
import { Group } from '@visx/group';
import { Pie } from '@visx/shape';
import { scaleOrdinal } from '@visx/scale';
import { LinearGradient } from '@visx/gradient';
import { Text } from '@visx/text';
import { animated, useSpring } from '@react-spring/web';

interface AllocationItem {
  name: string;
  value: number;
  percentage?: number;
  color?: string;
  target?: number;
  yield?: number;
  risk?: 'low' | 'medium' | 'high';
  category?: string;
}

interface ElegantAssetAllocationPieProps {
  allocations: AllocationItem[];
  title?: string;
  subtitle?: string;
  showPercentage?: boolean;
  showTargets?: boolean;
  showRiskMetrics?: boolean;
  size?: number;
  innerRadius?: number;
  totalValue?: number;
}

export function ElegantAssetAllocationPie({
  allocations,
  title = "Asset Allocation",
  subtitle = "Portfolio composition and target analysis",
  showPercentage = true,
  showTargets = true,
  showRiskMetrics = true,
  size = 400,
  innerRadius = 120,
  totalValue
}: ElegantAssetAllocationPieProps) {
  const [hoveredSlice, setHoveredSlice] = useState<string | null>(null);

  const radius = size / 2;
  const centerX = radius;
  const centerY = radius;

  // Calculate total and prepare data
  const total = totalValue || allocations.reduce((sum, item) => sum + item.value, 0);
  const pieData = allocations.map(item => ({
    ...item,
    percentage: (item.value / total) * 100,
    color: item.color || getDefaultColor(item.name)
  })).sort((a, b) => b.value - a.value);

  // Calculate key metrics
  const metrics = useMemo(() => {
    const avgYield = pieData
      .filter(d => d.yield)
      .reduce((sum, d, _, arr) => sum + (d.yield! * d.percentage / 100) / arr.length, 0);
    
    const riskScore = pieData.reduce((score, d) => {
      const weight = d.percentage / 100;
      const risk = d.risk === 'low' ? 1 : d.risk === 'medium' ? 2 : 3;
      return score + (weight * risk);
    }, 0);

    const diversificationScore = Math.min(100, (1 - Math.pow(pieData.reduce((sum, d) => 
      sum + Math.pow(d.percentage / 100, 2), 0), 2)) * 200);

    return {
      portfolioYield: avgYield,
      riskScore,
      diversificationScore,
      concentration: pieData.slice(0, 3).reduce((sum, d) => sum + d.percentage, 0)
    };
  }, [pieData]);

  return (
    <div className="w-full">
      {/* Header */}
      <div className="mb-6">
        <h2 className="text-2xl font-light text-gray-900 mb-1">{title}</h2>
        <p className="text-sm text-gray-500">{subtitle}</p>
        <div className="mt-3 flex items-center space-x-6 text-sm">
          <span className="text-gray-600">
            Total: <span className="font-semibold">${total.toLocaleString()}</span>
          </span>
          <span className="text-gray-600">
            Assets: <span className="font-semibold">{allocations.length}</span>
          </span>
          <span className="text-gray-600">
            Top 3: <span className="font-semibold">{metrics.concentration.toFixed(1)}%</span>
          </span>
        </div>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-8">
        {/* Pie Chart */}
        <div className="xl:col-span-2">
          <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-8">
            <div className="flex justify-center">
              <div className="relative">
                <svg width={size} height={size}>
                  <Group top={centerY} left={centerX}>
                    <Pie
                      data={pieData}
                      pieValue={d => d.value}
                      outerRadius={radius - 40}
                      innerRadius={innerRadius}
                      cornerRadius={3}
                      padAngle={0.01}
                    >
                      {pie =>
                        pie.arcs.map((arc, index) => {
                          const [centroidX, centroidY] = pie.path.centroid(arc);
                          const hasSpaceForLabel = arc.endAngle - arc.startAngle >= 0.1;
                          const isHovered = hoveredSlice === arc.data.name;
                          
                          return (
                            <Group key={`arc-${index}`}>
                              <defs>
                                <LinearGradient 
                                  id={`gradient-${index}`} 
                                  from={arc.data.color} 
                                  to={adjustBrightness(arc.data.color, -20)}
                                />
                              </defs>
                              
                              <AnimatedSlice
                                arc={arc}
                                color={`url(#gradient-${index})`}
                                isHovered={isHovered}
                                onMouseEnter={() => setHoveredSlice(arc.data.name)}
                                onMouseLeave={() => setHoveredSlice(null)}
                              />
                              
                              {/* Percentage label */}
                              {hasSpaceForLabel && showPercentage && (
                                <Text
                                  x={centroidX}
                                  y={centroidY}
                                  dy=".33em"
                                  fontSize={14}
                                  fontWeight="600"
                                  fill="white"
                                  textAnchor="middle"
                                  pointerEvents="none"
                                >
                                  {arc.data.percentage.toFixed(1)}%
                                </Text>
                              )}
                            </Group>
                          );
                        })
                      }
                    </Pie>
                  </Group>
                </svg>
                
                {/* Center content */}
                <div className="absolute inset-0 flex items-center justify-center">
                  <div className="text-center">
                    <div className="text-2xl font-bold text-gray-900">
                      ${(total / 1000).toFixed(0)}K
                    </div>
                    <div className="text-sm text-gray-500 mt-1">Total Value</div>
                    {showRiskMetrics && (
                      <div className="mt-2 space-y-1">
                        <div className="text-xs text-gray-600">
                          Risk: <span className="font-medium">{metrics.riskScore.toFixed(1)}/3</span>
                        </div>
                        <div className="text-xs text-gray-600">
                          Diversity: <span className="font-medium">{metrics.diversificationScore.toFixed(0)}</span>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Allocation Details */}
        <div className="space-y-4">
          {pieData.map((item, index) => (
            <AllocationDetailCard
              key={item.name}
              item={item}
              index={index}
              showTargets={showTargets}
              showRiskMetrics={showRiskMetrics}
              isHovered={hoveredSlice === item.name}
              onHover={() => setHoveredSlice(item.name)}
              onLeave={() => setHoveredSlice(null)}
            />
          ))}
        </div>
      </div>

      {/* Portfolio Analytics */}
      <div className="mt-8 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <AnalyticsCard
          title="Portfolio Yield"
          value={`${metrics.portfolioYield.toFixed(2)}%`}
          description="Weighted average yield"
          color="emerald"
          score={metrics.portfolioYield >= 3 ? 'high' : metrics.portfolioYield >= 2 ? 'medium' : 'low'}
        />
        
        <AnalyticsCard
          title="Risk Level"
          value={`${metrics.riskScore.toFixed(1)}/3`}
          description="Composite risk score"
          color="purple"
          score={metrics.riskScore <= 1.5 ? 'low' : metrics.riskScore <= 2.5 ? 'medium' : 'high'}
        />
        
        <AnalyticsCard
          title="Diversification"
          value={`${metrics.diversificationScore.toFixed(0)}`}
          description="Portfolio diversity index"
          color="blue"
          score={metrics.diversificationScore >= 80 ? 'high' : metrics.diversificationScore >= 60 ? 'medium' : 'low'}
        />
        
        <AnalyticsCard
          title="Concentration"
          value={`${metrics.concentration.toFixed(1)}%`}
          description="Top 3 holdings weight"
          color="orange"
          score={metrics.concentration <= 50 ? 'low' : metrics.concentration <= 70 ? 'medium' : 'high'}
        />
      </div>

      {/* Investment Insights */}
      {showTargets && (
        <div className="mt-8 p-6 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-2xl border border-blue-200">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Allocation Insights</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h4 className="font-medium text-gray-800 mb-2">Portfolio Balance</h4>
              <p className="text-sm text-gray-700">
                {getAllocationInsight(pieData, metrics)}
              </p>
            </div>
            <div>
              <h4 className="font-medium text-gray-800 mb-2">Rebalancing Recommendations</h4>
              <p className="text-sm text-gray-700">
                {getRebalancingAdvice(pieData)}
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// Animated Slice Component
function AnimatedSlice({ 
  arc, 
  color, 
  isHovered, 
  onMouseEnter, 
  onMouseLeave 
}: { 
  arc: any; 
  color: string; 
  isHovered: boolean; 
  onMouseEnter: () => void; 
  onMouseLeave: () => void; 
}) {
  const animatedStyles = useSpring({
    transform: isHovered ? 'scale(1.05)' : 'scale(1)',
    opacity: isHovered ? 1 : 0.9,
    config: { tension: 300, friction: 30 }
  });

  return (
    <animated.path
      d={arc.path() || undefined}
      fill={color}
      stroke="white"
      strokeWidth={2}
      style={animatedStyles}
      onMouseEnter={onMouseEnter}
      onMouseLeave={onMouseLeave}
      className="cursor-pointer"
    />
  );
}

// Allocation Detail Card
interface AllocationDetailCardProps {
  item: AllocationItem & { percentage: number; color: string };
  index: number;
  showTargets: boolean;
  showRiskMetrics: boolean;
  isHovered: boolean;
  onHover: () => void;
  onLeave: () => void;
}

function AllocationDetailCard({ 
  item, 
  index, 
  showTargets, 
  showRiskMetrics, 
  isHovered,
  onHover,
  onLeave
}: AllocationDetailCardProps) {
  const targetDrift = item.target ? item.percentage - item.target : null;

  return (
    <div 
      className={`p-4 rounded-xl border transition-all cursor-pointer ${
        isHovered 
          ? 'bg-blue-50 border-blue-200 shadow-md' 
          : 'bg-white border-gray-200 hover:bg-gray-50'
      }`}
      onMouseEnter={onHover}
      onMouseLeave={onLeave}
    >
      <div className="flex items-start space-x-3">
        <div 
          className="w-4 h-4 rounded-full mt-1 shadow-sm"
          style={{ backgroundColor: item.color }}
        />
        
        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between mb-2">
            <h4 className="font-semibold text-gray-900 truncate">{item.name}</h4>
            <div className="text-right">
              <div className="font-semibold text-gray-900">
                {item.percentage.toFixed(1)}%
              </div>
              <div className="text-xs text-gray-500">
                ${(item.value / 1000).toFixed(0)}K
              </div>
            </div>
          </div>

          <div className="space-y-2">
            {/* Target Progress */}
            {showTargets && item.target && (
              <div>
                <div className="flex justify-between text-xs text-gray-600 mb-1">
                  <span>Target: {item.target.toFixed(0)}%</span>
                  <span className={`font-medium ${
                    Math.abs(targetDrift!) <= 2 ? 'text-emerald-600' :
                    Math.abs(targetDrift!) <= 5 ? 'text-yellow-600' : 'text-red-600'
                  }`}>
                    {targetDrift! > 0 ? '+' : ''}{targetDrift!.toFixed(1)}%
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-1.5">
                  <div 
                    className={`h-1.5 rounded-full ${
                      Math.abs(targetDrift!) <= 2 ? 'bg-emerald-500' :
                      Math.abs(targetDrift!) <= 5 ? 'bg-yellow-500' : 'bg-red-500'
                    }`}
                    style={{ width: `${(item.percentage / Math.max(item.target, item.percentage)) * 100}%` }}
                  />
                </div>
              </div>
            )}

            {/* Risk and Yield */}
            {showRiskMetrics && (item.risk || item.yield) && (
              <div className="flex items-center justify-between text-xs">
                {item.risk && (
                  <span className={`px-2 py-1 rounded-full font-medium ${
                    item.risk === 'low' ? 'bg-emerald-100 text-emerald-800' :
                    item.risk === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                    'bg-red-100 text-red-800'
                  }`}>
                    {item.risk} risk
                  </span>
                )}
                {item.yield && (
                  <span className="text-gray-600">
                    Yield: <span className="font-medium">{item.yield.toFixed(1)}%</span>
                  </span>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

// Analytics Card Component
interface AnalyticsCardProps {
  title: string;
  value: string;
  description: string;
  color: string;
  score: 'low' | 'medium' | 'high';
}

function AnalyticsCard({ title, value, description, color, score }: AnalyticsCardProps) {
  const scoreConfig = {
    low: { bg: 'bg-gray-100', text: 'text-gray-700' },
    medium: { bg: 'bg-yellow-100', text: 'text-yellow-800' },
    high: { bg: 'bg-emerald-100', text: 'text-emerald-800' }
  };

  return (
    <div className={`bg-gradient-to-br from-${color}-50 to-${color}-100 p-6 rounded-xl border border-${color}-200`}>
      <div className="text-center">
        <div className={`text-2xl font-bold text-${color}-600 mb-2`}>
          {value}
        </div>
        <h4 className="font-semibold text-gray-900 mb-1">{title}</h4>
        <p className="text-xs text-gray-600 mb-3">{description}</p>
        <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${scoreConfig[score].bg} ${scoreConfig[score].text}`}>
          {score.charAt(0).toUpperCase() + score.slice(1)}
        </span>
      </div>
    </div>
  );
}

// Utility Functions
function getDefaultColor(name: string): string {
  const colors = [
    '#10B981', '#3B82F6', '#8B5CF6', '#F59E0B', '#EF4444',
    '#6366F1', '#EC4899', '#14B8A6', '#F97316', '#84CC16'
  ];
  const index = name.length % colors.length;
  return colors[index];
}

function adjustBrightness(color: string, amount: number): string {
  // Simplified brightness adjustment
  return color; // In a real implementation, you'd adjust the hex color
}

function getAllocationInsight(
  pieData: Array<AllocationItem & { percentage: number }>, 
  metrics: any
): string {
  const topAllocation = pieData[0];
  const diversificationLevel = metrics.diversificationScore >= 80 ? 'excellent' : 
                              metrics.diversificationScore >= 60 ? 'good' : 'limited';
  
  return `Portfolio shows ${diversificationLevel} diversification with ${topAllocation.name} as the largest allocation (${topAllocation.percentage.toFixed(1)}%). ${metrics.riskScore <= 2 ? 'Conservative' : 'Moderate to aggressive'} risk profile aligns with diversification strategy.`;
}

function getRebalancingAdvice(pieData: Array<AllocationItem & { percentage: number }>): string {
  const drifted = pieData.filter(item => 
    item.target && Math.abs(item.percentage - item.target) > 5
  );
  
  if (drifted.length === 0) {
    return "Portfolio is well-balanced and within target ranges. Continue monitoring for drift and consider quarterly rebalancing reviews.";
  }
  
  const mostDrifted = drifted.sort((a, b) => 
    Math.abs(b.percentage - (b.target || 0)) - Math.abs(a.percentage - (a.target || 0))
  )[0];
  
  const direction = mostDrifted.percentage > (mostDrifted.target || 0) ? 'reduce' : 'increase';
  
  return `Consider rebalancing ${mostDrifted.name} allocation. Current drift of ${Math.abs(mostDrifted.percentage - (mostDrifted.target || 0)).toFixed(1)}% suggests need to ${direction} exposure to restore target allocation.`;
}