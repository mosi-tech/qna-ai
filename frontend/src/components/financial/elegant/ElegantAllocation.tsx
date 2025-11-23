'use client';

import React, { useMemo } from 'react';
import { Group } from '@visx/group';
import { Pie } from '@visx/shape';
import { scaleOrdinal } from '@visx/scale';
import { ParentSize } from '@visx/responsive';
import { animated, useSpring, config } from '@react-spring/web';

interface AllocationItem {
  name: string;
  value: number;
  color: string;
  target?: number;
  drift?: number;
  risk?: 'low' | 'medium' | 'high';
  expectedReturn?: number;
  sharpeRatio?: number;
}

interface ElegantAllocationProps {
  allocations: AllocationItem[];
  title?: string;
  showTargets?: boolean;
  showRiskMetrics?: boolean;
  size?: number;
  innerRadius?: number;
}

export function ElegantAllocation({
  allocations,
  title = "Asset Allocation",
  showTargets = true,
  showRiskMetrics = true,
  size = 300,
  innerRadius = 80
}: ElegantAllocationProps) {
  const radius = size / 2;
  const centerX = radius;
  const centerY = radius;

  // Calculate total and percentages
  const total = allocations.reduce((sum, item) => sum + item.value, 0);
  const pieData = allocations.map(item => ({
    ...item,
    percentage: (item.value / total) * 100
  }));

  // Sort by value for better visual hierarchy
  const sortedData = [...pieData].sort((a, b) => b.value - a.value);

  return (
    <div className="w-full">
      {/* Header */}
      <div className="mb-6">
        <h2 className="text-2xl font-light text-gray-900 mb-2">{title}</h2>
        <div className="flex items-center space-x-4 text-sm text-gray-500">
          <span>${total.toLocaleString()} total</span>
          <span>•</span>
          <span>{allocations.length} asset classes</span>
          {showTargets && (
            <>
              <span>•</span>
              <AllocationHealthIndicator allocations={allocations} />
            </>
          )}
        </div>
      </div>

      <div className="flex flex-col lg:flex-row lg:space-x-8">
        {/* Elegant Donut Chart */}
        <div className="flex-shrink-0">
          <div className="relative">
            <svg width={size} height={size}>
              <Group top={centerY} left={centerX}>
                <Pie
                  data={sortedData}
                  pieValue={d => d.value}
                  outerRadius={radius - 20}
                  innerRadius={innerRadius}
                  cornerRadius={2}
                  padAngle={0.02}
                >
                  {pie => 
                    pie.arcs.map((arc, index) => {
                      const [centroidX, centroidY] = pie.path.centroid(arc);
                      const hasSpaceForLabel = arc.endAngle - arc.startAngle >= 0.1;
                      
                      return (
                        <g key={`arc-${index}`}>
                          {/* Main arc with gradient */}
                          <AnimatedArc
                            arc={arc}
                            color={arc.data.color}
                            index={index}
                          />
                          
                          {/* Percentage label */}
                          {hasSpaceForLabel && (
                            <text
                              x={centroidX}
                              y={centroidY}
                              dy=".33em"
                              fontSize={12}
                              fontWeight="600"
                              fill="white"
                              textAnchor="middle"
                              pointerEvents="none"
                            >
                              {arc.data.percentage.toFixed(0)}%
                            </text>
                          )}
                        </g>
                      );
                    })
                  }
                </Pie>
              </Group>
            </svg>
            
            {/* Center content - Portfolio value */}
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="text-center">
                <div className="text-lg font-semibold text-gray-900">
                  ${(total / 1000).toFixed(0)}K
                </div>
                <div className="text-xs text-gray-500 mt-1">
                  Portfolio
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Allocation Details */}
        <div className="flex-1 space-y-4 mt-6 lg:mt-0">
          {sortedData.map((item, index) => (
            <AllocationDetailRow
              key={item.name}
              allocation={item}
              showTargets={showTargets}
              showRiskMetrics={showRiskMetrics}
              rank={index + 1}
            />
          ))}
        </div>
      </div>

      {/* Risk-Return Analysis */}
      {showRiskMetrics && (
        <div className="mt-8">
          <AllocationRiskAnalysis allocations={allocations} />
        </div>
      )}
    </div>
  );
}

// Animated arc component
function AnimatedArc({ arc, color, index }: { arc: any, color: string, index: number }) {
  const animatedStyles = useSpring({
    from: { opacity: 0, transform: 'scale(0.8)' },
    to: { opacity: 1, transform: 'scale(1)' },
    delay: index * 100,
    config: config.gentle
  });

  return (
    <animated.path
      d={arc.path() || undefined}
      fill={`url(#gradient-${index})`}
      style={animatedStyles}
      stroke="white"
      strokeWidth={2}
    >
      <defs>
        <linearGradient id={`gradient-${index}`} gradientUnits="userSpaceOnUse">
          <stop offset="0%" stopColor={color} />
          <stop offset="100%" stopColor={adjustBrightness(color, -20)} />
        </linearGradient>
      </defs>
    </animated.path>
  );
}

// Allocation detail row
interface AllocationDetailRowProps {
  allocation: AllocationItem & { percentage: number };
  showTargets: boolean;
  showRiskMetrics: boolean;
  rank: number;
}

function AllocationDetailRow({ 
  allocation, 
  showTargets, 
  showRiskMetrics, 
  rank 
}: AllocationDetailRowProps) {
  const isDrifted = allocation.target && Math.abs(allocation.percentage - allocation.target) > 2;
  const driftDirection = allocation.target ? allocation.percentage - allocation.target : 0;

  return (
    <div className="flex items-center justify-between py-3 border-b border-gray-50 last:border-b-0">
      <div className="flex items-center space-x-4 flex-1">
        {/* Color indicator */}
        <div 
          className="w-4 h-4 rounded-full shadow-sm"
          style={{ backgroundColor: allocation.color }}
        />
        
        {/* Asset details */}
        <div className="flex-1">
          <div className="flex items-center space-x-3">
            <span className="font-semibold text-gray-900">{allocation.name}</span>
            {allocation.risk && (
              <RiskBadge risk={allocation.risk} />
            )}
          </div>
          
          {showRiskMetrics && (allocation.expectedReturn || allocation.sharpeRatio) && (
            <div className="flex items-center space-x-4 mt-1 text-xs text-gray-600">
              {allocation.expectedReturn && (
                <span>Expected: {allocation.expectedReturn.toFixed(1)}%</span>
              )}
              {allocation.sharpeRatio && (
                <span>Sharpe: {allocation.sharpeRatio.toFixed(2)}</span>
              )}
            </div>
          )}
        </div>
      </div>

      <div className="flex items-center space-x-6">
        {/* Current allocation */}
        <div className="text-right">
          <div className="font-semibold text-gray-900">
            {allocation.percentage.toFixed(1)}%
          </div>
          <div className="text-xs text-gray-500">
            ${allocation.value.toLocaleString()}
          </div>
        </div>

        {/* Target vs actual */}
        {showTargets && allocation.target && (
          <div className="text-right min-w-[80px]">
            <div className="text-sm text-gray-600">
              Target: {allocation.target.toFixed(0)}%
            </div>
            <div className={`text-xs font-medium ${
              Math.abs(driftDirection) <= 2 ? 'text-emerald-600' :
              Math.abs(driftDirection) <= 5 ? 'text-yellow-600' : 'text-red-600'
            }`}>
              {driftDirection > 0 ? '+' : ''}{driftDirection.toFixed(1)}% drift
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

// Risk badge component
function RiskBadge({ risk }: { risk: 'low' | 'medium' | 'high' }) {
  const config = {
    low: { bg: 'bg-emerald-100', text: 'text-emerald-800', label: 'Low Risk' },
    medium: { bg: 'bg-yellow-100', text: 'text-yellow-800', label: 'Med Risk' },
    high: { bg: 'bg-red-100', text: 'text-red-800', label: 'High Risk' }
  };

  return (
    <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${config[risk].bg} ${config[risk].text}`}>
      {config[risk].label}
    </span>
  );
}

// Allocation health indicator
function AllocationHealthIndicator({ allocations }: { allocations: AllocationItem[] }) {
  const drifts = allocations.filter(a => a.target).map(a => 
    Math.abs(((a.value / allocations.reduce((sum, item) => sum + item.value, 0)) * 100) - (a.target || 0))
  );
  
  const maxDrift = Math.max(...drifts, 0);
  const avgDrift = drifts.length > 0 ? drifts.reduce((a, b) => a + b, 0) / drifts.length : 0;
  
  const health = maxDrift <= 2 ? 'Excellent' : maxDrift <= 5 ? 'Good' : 'Needs Rebalancing';
  const color = maxDrift <= 2 ? 'text-emerald-600' : maxDrift <= 5 ? 'text-yellow-600' : 'text-red-600';
  
  return (
    <span className={`font-medium ${color}`}>
      {health} ({avgDrift.toFixed(1)}% avg drift)
    </span>
  );
}

// Risk-return analysis
function AllocationRiskAnalysis({ allocations }: { allocations: AllocationItem[] }) {
  const portfolioReturn = allocations.reduce((sum, a) => {
    const weight = a.value / allocations.reduce((total, item) => total + item.value, 0);
    return sum + (weight * (a.expectedReturn || 0));
  }, 0);

  const portfolioRisk = allocations.reduce((sum, a) => {
    const weight = a.value / allocations.reduce((total, item) => total + item.value, 0);
    const riskScore = a.risk === 'low' ? 1 : a.risk === 'medium' ? 2 : 3;
    return sum + (weight * riskScore);
  }, 0);

  return (
    <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl p-6 border border-blue-100">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Portfolio Analytics</h3>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="text-center">
          <div className="text-2xl font-bold text-blue-600">
            {portfolioReturn.toFixed(1)}%
          </div>
          <div className="text-sm font-medium text-gray-600">Expected Return</div>
          <div className="text-xs text-gray-500 mt-1">Weighted average</div>
        </div>
        
        <div className="text-center">
          <div className="text-2xl font-bold text-purple-600">
            {portfolioRisk.toFixed(1)}/3
          </div>
          <div className="text-sm font-medium text-gray-600">Risk Score</div>
          <div className="text-xs text-gray-500 mt-1">Composite rating</div>
        </div>
        
        <div className="text-center">
          <div className="text-2xl font-bold text-emerald-600">
            {(portfolioReturn / portfolioRisk).toFixed(2)}
          </div>
          <div className="text-sm font-medium text-gray-600">Return/Risk</div>
          <div className="text-xs text-gray-500 mt-1">Efficiency ratio</div>
        </div>
      </div>
    </div>
  );
}

// Utility function to adjust color brightness
function adjustBrightness(color: string, amount: number): string {
  return color; // Simplified for now - could implement actual color manipulation
}