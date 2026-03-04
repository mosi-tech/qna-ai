'use client';

import LayoutContainer from '@/components/insights/layout/components/LayoutContainer';
import LayoutHeader from '@/components/insights/layout/components/LayoutHeader';

export default function Grid2Variant5() {
  return (
    <LayoutContainer>
      
      <LayoutHeader>
        <h1 className="text-2xl font-bold text-gray-900">Grid/2/5: Growth vs Value Styles</h1>
        <p className="text-gray-600 mt-1">2×1 grid • Investment Style Comparison</p>
      </LayoutHeader>

      <div className="flex-1 grid grid-cols-2 grid-rows-1 gap-4 min-h-0">
        
        <div className="col-span-1 row-span-1">
          <div className="h-full bg-gradient-to-br from-purple-50 to-indigo-50 rounded-lg border border-purple-200 p-6">
            <div className="text-center mb-6">
              <h3 className="text-2xl font-bold text-purple-900">🚀 Growth Strategy</h3>
              <p className="text-purple-700">High-Growth, High-Potential Stocks</p>
            </div>
            
            <div className="space-y-4">
              <div className="text-center">
                <div className="text-3xl font-bold text-purple-600 mb-2">+24.8%</div>
                <div className="text-sm text-purple-700">YTD Return</div>
              </div>
              
              <div className="space-y-3 text-sm">
                <div className="flex justify-between">
                  <span className="text-purple-700">Avg P/E Ratio</span>
                  <span className="font-medium text-purple-900">38.2</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-purple-700">Revenue Growth</span>
                  <span className="font-medium text-green-600">+28.5%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-purple-700">Earnings Growth</span>
                  <span className="font-medium text-green-600">+35.1%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-purple-700">Volatility</span>
                  <span className="font-medium text-orange-600">24.8%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-purple-700">Beta</span>
                  <span className="font-medium">1.45</span>
                </div>
              </div>

              <div className="mt-6 space-y-2">
                <div className="text-sm font-medium text-purple-800 mb-2">Top Holdings:</div>
                <div className="text-xs text-purple-700 space-y-1">
                  <div>• NVDA - 12.5% (+127.3%)</div>
                  <div>• TSLA - 8.7% (+45.2%)</div>
                  <div>• AMZN - 11.2% (+28.9%)</div>
                  <div>• GOOGL - 9.8% (+22.1%)</div>
                  <div>• META - 7.3% (+89.4%)</div>
                </div>
              </div>

              <div className="mt-6 p-3 bg-purple-100 rounded border border-purple-300">
                <div className="text-purple-800 font-medium text-sm mb-1">Strategy Focus</div>
                <div className="text-purple-700 text-sm">Innovation & future earnings potential</div>
              </div>
            </div>
          </div>
        </div>

        <div className="col-span-1 row-span-1">
          <div className="h-full bg-gradient-to-br from-blue-50 to-cyan-50 rounded-lg border border-blue-200 p-6">
            <div className="text-center mb-6">
              <h3 className="text-2xl font-bold text-blue-900">💰 Value Strategy</h3>
              <p className="text-blue-700">Undervalued, Dividend-Paying Stocks</p>
            </div>
            
            <div className="space-y-4">
              <div className="text-center">
                <div className="text-3xl font-bold text-blue-600 mb-2">+12.4%</div>
                <div className="text-sm text-blue-700">YTD Return</div>
              </div>
              
              <div className="space-y-3 text-sm">
                <div className="flex justify-between">
                  <span className="text-blue-700">Avg P/E Ratio</span>
                  <span className="font-medium text-blue-900">14.6</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-blue-700">Dividend Yield</span>
                  <span className="font-medium text-green-600">3.8%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-blue-700">Price-to-Book</span>
                  <span className="font-medium text-blue-900">1.8</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-blue-700">Volatility</span>
                  <span className="font-medium text-green-600">12.3%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-blue-700">Beta</span>
                  <span className="font-medium">0.78</span>
                </div>
              </div>

              <div className="mt-6 space-y-2">
                <div className="text-sm font-medium text-blue-800 mb-2">Top Holdings:</div>
                <div className="text-xs text-blue-700 space-y-1">
                  <div>• BRK.B - 15.2% (+8.7%)</div>
                  <div>• JPM - 12.1% (+14.3%)</div>
                  <div>• JNJ - 9.8% (+6.2%)</div>
                  <div>• XOM - 8.5% (+18.9%)</div>
                  <div>• PG - 7.9% (+9.1%)</div>
                </div>
              </div>

              <div className="mt-6 p-3 bg-blue-100 rounded border border-blue-300">
                <div className="text-blue-800 font-medium text-sm mb-1">Strategy Focus</div>
                <div className="text-blue-700 text-sm">Stable cash flows & undervalued assets</div>
              </div>
            </div>
          </div>
        </div>

      </div>
      
    </LayoutContainer>
  );
}