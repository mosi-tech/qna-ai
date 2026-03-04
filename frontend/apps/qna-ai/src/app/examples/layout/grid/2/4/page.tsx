'use client';

import LayoutContainer from '@/components/insights/layout/components/LayoutContainer';
import LayoutHeader from '@/components/insights/layout/components/LayoutHeader';

export default function Grid2Variant4() {
  return (
    <LayoutContainer>
      
      <LayoutHeader>
        <h1 className="text-2xl font-bold text-gray-900">Grid/2/4: Bull vs Bear Market</h1>
        <p className="text-gray-600 mt-1">2×1 grid • Scenario Analysis & Risk Assessment</p>
      </LayoutHeader>

      <div className="flex-1 grid grid-cols-2 grid-rows-1 gap-4 min-h-0">
        
        <div className="col-span-1 row-span-1">
          <div className="h-full bg-gradient-to-br from-green-50 to-emerald-50 rounded-lg border border-green-200 p-6">
            <div className="text-center mb-6">
              <h3 className="text-2xl font-bold text-green-900">🐂 Bull Market Scenario</h3>
              <p className="text-green-700">Optimistic Economic Growth</p>
            </div>
            
            <div className="space-y-4">
              <div className="text-center">
                <div className="text-3xl font-bold text-green-600 mb-2">+28.5%</div>
                <div className="text-sm text-green-700">Expected Annual Return</div>
              </div>
              
              <div className="space-y-3 text-sm">
                <div className="flex justify-between">
                  <span className="text-green-700">Portfolio Value (1Y)</span>
                  <span className="font-medium text-green-900">$3.86M</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-green-700">Tech Stocks</span>
                  <span className="font-medium text-green-600">+35.2%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-green-700">Growth Stocks</span>
                  <span className="font-medium text-green-600">+32.1%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-green-700">Small Cap</span>
                  <span className="font-medium text-green-600">+41.3%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-green-700">Bonds</span>
                  <span className="font-medium text-green-600">+8.7%</span>
                </div>
              </div>

              <div className="mt-6 space-y-2">
                <div className="text-sm font-medium text-green-800 mb-2">Key Drivers:</div>
                <div className="text-xs text-green-700 space-y-1">
                  <div>• GDP Growth: 4.2%+</div>
                  <div>• Low Interest Rates: 2.5-3.5%</div>
                  <div>• Corporate Earnings: +18%</div>
                  <div>• Consumer Confidence: High</div>
                  <div>• Inflation: Controlled 2-3%</div>
                </div>
              </div>

              <div className="mt-6 p-3 bg-green-100 rounded border border-green-300">
                <div className="text-green-800 font-medium text-sm mb-1">Probability</div>
                <div className="text-green-700 text-sm">35% - Sustained growth cycle</div>
              </div>
            </div>
          </div>
        </div>

        <div className="col-span-1 row-span-1">
          <div className="h-full bg-gradient-to-br from-red-50 to-orange-50 rounded-lg border border-red-200 p-6">
            <div className="text-center mb-6">
              <h3 className="text-2xl font-bold text-red-900">🐻 Bear Market Scenario</h3>
              <p className="text-red-700">Economic Contraction Period</p>
            </div>
            
            <div className="space-y-4">
              <div className="text-center">
                <div className="text-3xl font-bold text-red-600 mb-2">-18.2%</div>
                <div className="text-sm text-red-700">Expected Annual Return</div>
              </div>
              
              <div className="space-y-3 text-sm">
                <div className="flex justify-between">
                  <span className="text-red-700">Portfolio Value (1Y)</span>
                  <span className="font-medium text-red-900">$2.45M</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-red-700">Tech Stocks</span>
                  <span className="font-medium text-red-600">-28.4%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-red-700">Growth Stocks</span>
                  <span className="font-medium text-red-600">-25.7%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-red-700">Small Cap</span>
                  <span className="font-medium text-red-600">-35.1%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-red-700">Bonds</span>
                  <span className="font-medium text-green-600">+4.2%</span>
                </div>
              </div>

              <div className="mt-6 space-y-2">
                <div className="text-sm font-medium text-red-800 mb-2">Key Risks:</div>
                <div className="text-xs text-red-700 space-y-1">
                  <div>• GDP Contraction: -2.1%</div>
                  <div>• High Interest Rates: 6.5%+</div>
                  <div>• Corporate Earnings: -22%</div>
                  <div>• Consumer Confidence: Low</div>
                  <div>• Inflation: Persistent 5%+</div>
                </div>
              </div>

              <div className="mt-6 p-3 bg-red-100 rounded border border-red-300">
                <div className="text-red-800 font-medium text-sm mb-1">Probability</div>
                <div className="text-red-700 text-sm">25% - Economic downturn risk</div>
              </div>
            </div>
          </div>
        </div>

      </div>
      
    </LayoutContainer>
  );
}