/**
 * Layout 1: Executive Analysis Layout
 * 
 * Grid Structure: 4x6 (4 columns, 6 rows)
 * 
 * Layout Map:
 * [2x2] [2x2]     <- Top: Half+Half
 * [1x3] [2x3] [1x3] <- Middle: Quarter+Half+Quarter  
 * [4x1]             <- Bottom: Full width
 * 
 * When to Use This Layout:
 * ✅ Portfolio performance analysis
 * ✅ Risk assessment summaries  
 * ✅ Investment recommendations
 * ✅ Executive dashboards
 * ✅ Single-focus analysis with supporting data
 * ✅ Any analysis needing: Summary + Metrics + Details + Actions
 * 
 * Don't Use For:
 * ❌ Multi-entity comparisons (use Layout2)
 * ❌ Time-series analysis (use Layout3) 
 * ❌ Complex data tables (use Layout4)
 * ❌ Side-by-side comparisons (use Layout2)
 */

'use client';

import HalfWidthTopLeft from './components/HalfWidthTopLeft';
import HalfWidthTopRight from './components/HalfWidthTopRight';
import QuarterWidthMiddleLeft from './components/QuarterWidthMiddleLeft';

interface Layout1Props {
  title?: React.ReactNode;
  topLeft?: React.ReactNode;      // 2x2 - Executive summary
  topRight?: React.ReactNode;     // 2x2 - Key metrics
  middleLeft?: React.ReactNode;   // 1x3 - Highlights
  middleCenter?: React.ReactNode; // 2x3 - Detailed breakdown
  middleRight?: React.ReactNode;  // 1x3 - Insights
  bottom?: React.ReactNode;       // 4x1 - Actions
}

export default function Layout1({
  title,
  topLeft,
  topRight,
  middleLeft,
  middleCenter,
  middleRight,
  bottom
}: Layout1Props) {
  return (
    <div className="h-screen bg-gray-50 p-6 overflow-hidden">
      <div className="max-w-7xl mx-auto h-full flex flex-col gap-4">

        {/* Header */}
        {title && (
          <div className="mb-2">
            {title}
          </div>
        )}

        {/* Main Grid */}
        <div className="flex-1 grid grid-cols-4 grid-rows-6 gap-4 min-h-0">

          {/* Top Row */}
          <HalfWidthTopLeft>
            {topLeft || (
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-3">Executive Summary</h3>
                <div className="space-y-2 text-sm text-gray-700">
                  <p><strong>Key Finding:</strong> [Main conclusion]</p>
                  <p><strong>Performance:</strong> [Quantified result]</p>
                  <p><strong>Recommendation:</strong> [Action needed]</p>
                </div>
              </div>
            )}
          </HalfWidthTopLeft>

          <HalfWidthTopRight>
            {topRight || (
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-3">Key Metrics</h3>
                <div className="grid grid-cols-2 gap-4">
                  <div className="text-center p-3 bg-gray-50 rounded">
                    <div className="text-2xl font-bold text-gray-900">[VALUE]</div>
                    <div className="text-xs text-gray-600">[METRIC 1]</div>
                  </div>
                  <div className="text-center p-3 bg-gray-50 rounded">
                    <div className="text-2xl font-bold text-gray-900">[VALUE]</div>
                    <div className="text-xs text-gray-600">[METRIC 2]</div>
                  </div>
                </div>
              </div>
            )}
          </HalfWidthTopRight>

          {/* Middle Row */}
          <QuarterWidthMiddleLeft>
            {middleLeft || (
              <div>
                <h3 className="font-semibold text-gray-900 mb-3">Highlights</h3>
                <div className="space-y-3">
                  <div className="border-l-4 border-green-400 pl-3 py-2">
                    <div className="text-sm font-medium">[Positive]</div>
                  </div>
                  <div className="border-l-4 border-amber-400 pl-3 py-2">
                    <div className="text-sm font-medium">[Concern]</div>
                  </div>
                </div>
              </div>
            )}
          </QuarterWidthMiddleLeft>

          {/* Middle Center */}
          <div className="col-span-2 row-span-3">
            <div className="h-full bg-white rounded-lg  p-4">
              {middleCenter || (
                <div>
                  <h3 className="font-semibold text-gray-900 mb-3">Detailed Analysis</h3>
                  <div className="text-sm text-gray-600">
                    [Tables, charts, detailed breakdowns go here]
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Middle Right */}
          <div className="col-span-1 row-span-3">
            <div className="h-full bg-white rounded-lg  p-4">
              {middleRight || (
                <div>
                  <h3 className="font-semibold text-gray-900 mb-3">Insights</h3>
                  <div className="space-y-3 text-sm">
                    <div className="bg-blue-50 p-3 rounded">
                      <div className="font-medium text-blue-800">[Insight]</div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Bottom Row */}
          <div className="col-span-4 row-span-1">
            <div className="h-full bg-white rounded-lg  p-4">
              {bottom || (
                <div>
                  <h3 className="font-semibold text-gray-900 mb-2">Actions & Timeline</h3>
                  <div className="flex justify-between items-center">
                    <div className="flex gap-6 text-sm">
                      <span className="text-gray-700">[Action items and priorities]</span>
                    </div>
                    <div className="text-xs text-gray-500">
                      Last Updated: [Date]
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>

        </div>
      </div>
    </div>
  );
}