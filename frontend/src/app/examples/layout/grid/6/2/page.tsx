'use client';

import LayoutContainer from '@/components/insights/layout/components/LayoutContainer';
import LayoutHeader from '@/components/insights/layout/components/LayoutHeader';

export default function Grid6Variant2() {
  return (
    <LayoutContainer>
      
      <LayoutHeader>
        <h1 className="text-2xl font-bold text-gray-900">Grid/6/2: Sector Performance</h1>
        <p className="text-gray-600 mt-1">3×2 grid • Technology, Finance, Healthcare, Energy, Consumer, Industrials</p>
      </LayoutHeader>

      <div className="flex-1 grid grid-cols-3 grid-rows-2 gap-4 min-h-0">
        
        <div className="col-span-1 row-span-1">
          <div className="h-full bg-white rounded-lg border border-gray-200 p-4">
            <div className="text-center mb-3">
              <div className="w-12 h-12 bg-blue-500 rounded-full mx-auto mb-2 flex items-center justify-center">
                <span className="text-white text-lg">💻</span>
              </div>
              <h3 className="text-lg font-bold text-gray-900">Technology</h3>
              <div className="text-2xl font-bold text-green-600">+28.4%</div>
              <div className="text-xs text-gray-600">YTD Return</div>
            </div>
            
            <div className="space-y-2 text-xs">
              <div className="flex justify-between">
                <span className="text-gray-600">Weight</span>
                <span className="font-medium">22.5%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Value</span>
                <span className="font-medium">$675K</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">P/E</span>
                <span className="font-medium">31.2</span>
              </div>
            </div>

            <div className="mt-3 p-2 bg-green-50 rounded">
              <div className="text-green-800 font-medium text-xs text-center">🚀 Outperforming</div>
            </div>
          </div>
        </div>

        <div className="col-span-1 row-span-1">
          <div className="h-full bg-white rounded-lg border border-gray-200 p-4">
            <div className="text-center mb-3">
              <div className="w-12 h-12 bg-green-500 rounded-full mx-auto mb-2 flex items-center justify-center">
                <span className="text-white text-lg">🏦</span>
              </div>
              <h3 className="text-lg font-bold text-gray-900">Financials</h3>
              <div className="text-2xl font-bold text-green-600">+18.7%</div>
              <div className="text-xs text-gray-600">YTD Return</div>
            </div>
            
            <div className="space-y-2 text-xs">
              <div className="flex justify-between">
                <span className="text-gray-600">Weight</span>
                <span className="font-medium">18.3%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Value</span>
                <span className="font-medium">$549K</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Dividend</span>
                <span className="font-medium">3.2%</span>
              </div>
            </div>

            <div className="mt-3 p-2 bg-blue-50 rounded">
              <div className="text-blue-800 font-medium text-xs text-center">📊 On Track</div>
            </div>
          </div>
        </div>

        <div className="col-span-1 row-span-1">
          <div className="h-full bg-white rounded-lg border border-gray-200 p-4">
            <div className="text-center mb-3">
              <div className="w-12 h-12 bg-red-500 rounded-full mx-auto mb-2 flex items-center justify-center">
                <span className="text-white text-lg">🏥</span>
              </div>
              <h3 className="text-lg font-bold text-gray-900">Healthcare</h3>
              <div className="text-2xl font-bold text-green-600">+12.1%</div>
              <div className="text-xs text-gray-600">YTD Return</div>
            </div>
            
            <div className="space-y-2 text-xs">
              <div className="flex justify-between">
                <span className="text-gray-600">Weight</span>
                <span className="font-medium">15.7%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Value</span>
                <span className="font-medium">$471K</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Beta</span>
                <span className="font-medium">0.85</span>
              </div>
            </div>

            <div className="mt-3 p-2 bg-yellow-50 rounded">
              <div className="text-yellow-800 font-medium text-xs text-center">⚡ Defensive</div>
            </div>
          </div>
        </div>

        <div className="col-span-1 row-span-1">
          <div className="h-full bg-white rounded-lg border border-gray-200 p-4">
            <div className="text-center mb-3">
              <div className="w-12 h-12 bg-yellow-500 rounded-full mx-auto mb-2 flex items-center justify-center">
                <span className="text-white text-lg">⚡</span>
              </div>
              <h3 className="text-lg font-bold text-gray-900">Energy</h3>
              <div className="text-2xl font-bold text-red-600">-4.2%</div>
              <div className="text-xs text-gray-600">YTD Return</div>
            </div>
            
            <div className="space-y-2 text-xs">
              <div className="flex justify-between">
                <span className="text-gray-600">Weight</span>
                <span className="font-medium">8.1%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Value</span>
                <span className="font-medium">$243K</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Volatility</span>
                <span className="font-medium">28.4%</span>
              </div>
            </div>

            <div className="mt-3 p-2 bg-red-50 rounded">
              <div className="text-red-800 font-medium text-xs text-center">⚠️ Underperforming</div>
            </div>
          </div>
        </div>

        <div className="col-span-1 row-span-1">
          <div className="h-full bg-white rounded-lg border border-gray-200 p-4">
            <div className="text-center mb-3">
              <div className="w-12 h-12 bg-purple-500 rounded-full mx-auto mb-2 flex items-center justify-center">
                <span className="text-white text-lg">🛒</span>
              </div>
              <h3 className="text-lg font-bold text-gray-900">Consumer</h3>
              <div className="text-2xl font-bold text-green-600">+16.3%</div>
              <div className="text-xs text-gray-600">YTD Return</div>
            </div>
            
            <div className="space-y-2 text-xs">
              <div className="flex justify-between">
                <span className="text-gray-600">Weight</span>
                <span className="font-medium">14.2%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Value</span>
                <span className="font-medium">$426K</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Growth</span>
                <span className="font-medium">8.7%</span>
              </div>
            </div>

            <div className="mt-3 p-2 bg-green-50 rounded">
              <div className="text-green-800 font-medium text-xs text-center">📈 Steady Growth</div>
            </div>
          </div>
        </div>

        <div className="col-span-1 row-span-1">
          <div className="h-full bg-white rounded-lg border border-gray-200 p-4">
            <div className="text-center mb-3">
              <div className="w-12 h-12 bg-gray-500 rounded-full mx-auto mb-2 flex items-center justify-center">
                <span className="text-white text-lg">🏭</span>
              </div>
              <h3 className="text-lg font-bold text-gray-900">Industrials</h3>
              <div className="text-2xl font-bold text-green-600">+21.8%</div>
              <div className="text-xs text-gray-600">YTD Return</div>
            </div>
            
            <div className="space-y-2 text-xs">
              <div className="flex justify-between">
                <span className="text-gray-600">Weight</span>
                <span className="font-medium">11.4%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Value</span>
                <span className="font-medium">$342K</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">P/E</span>
                <span className="font-medium">19.6</span>
              </div>
            </div>

            <div className="mt-3 p-2 bg-blue-50 rounded">
              <div className="text-blue-800 font-medium text-xs text-center">🔧 Cyclical Strength</div>
            </div>
          </div>
        </div>

      </div>
      
    </LayoutContainer>
  );
}