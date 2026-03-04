'use client';

import LayoutContainer from '@/components/insights/layout/components/LayoutContainer';
import LayoutHeader from '@/components/insights/layout/components/LayoutHeader';

export default function Grid3Variant4() {
  return (
    <LayoutContainer>
      
      <LayoutHeader>
        <h1 className="text-2xl font-bold text-gray-900">Grid/3/4: Asset Class Breakdown</h1>
        <p className="text-gray-600 mt-1">3×1 grid • Stocks, Bonds, Alternatives Analysis</p>
      </LayoutHeader>

      <div className="flex-1 grid grid-cols-3 grid-rows-1 gap-4 min-h-0">
        
        <div className="col-span-1 row-span-1">
          <div className="h-full bg-white rounded-lg border border-gray-200 p-6">
            <div className="text-center">
              <div className="w-16 h-16 bg-blue-500 rounded-full mx-auto mb-4 flex items-center justify-center">
                <span className="text-white text-2xl">📈</span>
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-2">Equities</h3>
              <div className="text-3xl font-bold text-blue-600 mb-2">65%</div>
              <div className="text-sm text-green-600 mb-4">$1.95M</div>
            </div>
            
            <div className="space-y-3 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-600">YTD Return</span>
                <span className="font-medium text-green-600">+18.4%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Volatility</span>
                <span className="font-medium">16.2%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Sharpe Ratio</span>
                <span className="font-medium">1.34</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Beta</span>
                <span className="font-medium">1.12</span>
              </div>
            </div>

            <div className="mt-6 p-3 bg-blue-50 rounded border border-blue-200">
              <div className="text-blue-800 font-medium text-sm">📊 Core Holdings</div>
              <div className="text-blue-700 text-xs mt-1">US Large Cap 45% • International 20%</div>
            </div>
          </div>
        </div>

        <div className="col-span-1 row-span-1">
          <div className="h-full bg-white rounded-lg border border-gray-200 p-6">
            <div className="text-center">
              <div className="w-16 h-16 bg-green-500 rounded-full mx-auto mb-4 flex items-center justify-center">
                <span className="text-white text-2xl">🏛️</span>
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-2">Fixed Income</h3>
              <div className="text-3xl font-bold text-green-600 mb-2">30%</div>
              <div className="text-sm text-gray-600 mb-4">$900K</div>
            </div>
            
            <div className="space-y-3 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-600">YTD Return</span>
                <span className="font-medium text-green-600">+6.2%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Duration</span>
                <span className="font-medium">4.8 years</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Yield</span>
                <span className="font-medium">4.6%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Credit Quality</span>
                <span className="font-medium">AA-</span>
              </div>
            </div>

            <div className="mt-6 p-3 bg-green-50 rounded border border-green-200">
              <div className="text-green-800 font-medium text-sm">🛡️ Stability</div>
              <div className="text-green-700 text-xs mt-1">Gov 60% • Corp 30% • TIPS 10%</div>
            </div>
          </div>
        </div>

        <div className="col-span-1 row-span-1">
          <div className="h-full bg-white rounded-lg border border-gray-200 p-6">
            <div className="text-center">
              <div className="w-16 h-16 bg-purple-500 rounded-full mx-auto mb-4 flex items-center justify-center">
                <span className="text-white text-2xl">🏢</span>
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-2">Alternatives</h3>
              <div className="text-3xl font-bold text-purple-600 mb-2">5%</div>
              <div className="text-sm text-gray-600 mb-4">$150K</div>
            </div>
            
            <div className="space-y-3 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-600">YTD Return</span>
                <span className="font-medium text-green-600">+12.7%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Correlation</span>
                <span className="font-medium">0.32</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Illiquidity</span>
                <span className="font-medium">Medium</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Inflation Hedge</span>
                <span className="font-medium text-green-600">High</span>
              </div>
            </div>

            <div className="mt-6 p-3 bg-purple-50 rounded border border-purple-200">
              <div className="text-purple-800 font-medium text-sm">🎯 Diversifier</div>
              <div className="text-purple-700 text-xs mt-1">REITs 60% • Commodities 40%</div>
            </div>
          </div>
        </div>

      </div>
      
    </LayoutContainer>
  );
}