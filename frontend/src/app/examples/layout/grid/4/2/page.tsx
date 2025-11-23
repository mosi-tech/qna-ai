'use client';

import LayoutContainer from '@/components/insights/layout/components/LayoutContainer';
import LayoutHeader from '@/components/insights/layout/components/LayoutHeader';

export default function Grid4Variant2() {
  return (
    <LayoutContainer>
      
      <LayoutHeader>
        <h1 className="text-2xl font-bold text-gray-900">Grid/4/2: Style Box Analysis</h1>
        <p className="text-gray-600 mt-1">2×2 grid • Large/Small Cap × Growth/Value Matrix</p>
      </LayoutHeader>

      <div className="flex-1 grid grid-cols-2 grid-rows-2 gap-4 min-h-0">
        
        <div className="col-span-1 row-span-1">
          <div className="h-full bg-white rounded-lg border-2 border-blue-300 p-6">
            <div className="text-center mb-4">
              <h3 className="text-lg font-bold text-blue-600">Large Cap Growth</h3>
              <p className="text-sm text-gray-600">High Growth, High Valuation</p>
            </div>
            
            <div className="space-y-3 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-600">Allocation</span>
                <span className="font-bold text-blue-600">35%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Value</span>
                <span className="font-medium">$1.05M</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">YTD Return</span>
                <span className="font-medium text-green-600">+22.4%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">P/E Ratio</span>
                <span className="font-medium">28.5</span>
              </div>
            </div>

            <div className="mt-4 text-xs text-gray-600">
              <div className="font-medium mb-2">Top Holdings:</div>
              <div>• AAPL (8.2%) • MSFT (7.8%)</div>
              <div>• GOOGL (6.4%) • AMZN (5.9%)</div>
            </div>

            <div className="mt-4 p-2 bg-blue-50 rounded text-center">
              <div className="text-blue-800 font-medium text-xs">✓ Overweight</div>
            </div>
          </div>
        </div>

        <div className="col-span-1 row-span-1">
          <div className="h-full bg-white rounded-lg border-2 border-green-300 p-6">
            <div className="text-center mb-4">
              <h3 className="text-lg font-bold text-green-600">Large Cap Value</h3>
              <p className="text-sm text-gray-600">Stable Dividends, Lower Valuation</p>
            </div>
            
            <div className="space-y-3 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-600">Allocation</span>
                <span className="font-bold text-green-600">25%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Value</span>
                <span className="font-medium">$750K</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">YTD Return</span>
                <span className="font-medium text-green-600">+14.2%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Dividend Yield</span>
                <span className="font-medium">2.8%</span>
              </div>
            </div>

            <div className="mt-4 text-xs text-gray-600">
              <div className="font-medium mb-2">Top Holdings:</div>
              <div>• BRK.B (4.1%) • JPM (3.8%)</div>
              <div>• JNJ (3.2%) • PG (2.9%)</div>
            </div>

            <div className="mt-4 p-2 bg-green-50 rounded text-center">
              <div className="text-green-800 font-medium text-xs">= Target Weight</div>
            </div>
          </div>
        </div>

        <div className="col-span-1 row-span-1">
          <div className="h-full bg-white rounded-lg border-2 border-purple-300 p-6">
            <div className="text-center mb-4">
              <h3 className="text-lg font-bold text-purple-600">Small Cap Growth</h3>
              <p className="text-sm text-gray-600">High Risk, High Reward</p>
            </div>
            
            <div className="space-y-3 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-600">Allocation</span>
                <span className="font-bold text-purple-600">15%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Value</span>
                <span className="font-medium">$450K</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">YTD Return</span>
                <span className="font-medium text-green-600">+31.8%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Volatility</span>
                <span className="font-medium">24.2%</span>
              </div>
            </div>

            <div className="mt-4 text-xs text-gray-600">
              <div className="font-medium mb-2">Top Holdings:</div>
              <div>• ROKU (2.1%) • SNOW (1.8%)</div>
              <div>• ZM (1.6%) • PLTR (1.4%)</div>
            </div>

            <div className="mt-4 p-2 bg-purple-50 rounded text-center">
              <div className="text-purple-800 font-medium text-xs">↑ Overweight</div>
            </div>
          </div>
        </div>

        <div className="col-span-1 row-span-1">
          <div className="h-full bg-white rounded-lg border-2 border-orange-300 p-6">
            <div className="text-center mb-4">
              <h3 className="text-lg font-bold text-orange-600">Small Cap Value</h3>
              <p className="text-sm text-gray-600">Contrarian Opportunities</p>
            </div>
            
            <div className="space-y-3 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-600">Allocation</span>
                <span className="font-bold text-orange-600">25%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Value</span>
                <span className="font-medium">$750K</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">YTD Return</span>
                <span className="font-medium text-green-600">+18.9%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">P/B Ratio</span>
                <span className="font-medium">1.2</span>
              </div>
            </div>

            <div className="mt-4 text-xs text-gray-600">
              <div className="font-medium mb-2">Top Holdings:</div>
              <div>• Regional Banks (12.4%)</div>
              <div>• Energy (8.7%) • Materials (6.1%)</div>
            </div>

            <div className="mt-4 p-2 bg-orange-50 rounded text-center">
              <div className="text-orange-800 font-medium text-xs">= Target Weight</div>
            </div>
          </div>
        </div>

      </div>
      
    </LayoutContainer>
  );
}