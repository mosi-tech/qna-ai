'use client';

import LayoutContainer from '@/components/insights/layout/components/LayoutContainer';
import LayoutHeader from '@/components/insights/layout/components/LayoutHeader';

export default function Grid3Variant3() {
  return (
    <LayoutContainer>
      
      <LayoutHeader>
        <h1 className="text-2xl font-bold text-gray-900">Grid/3/3: Two Stocks + Market</h1>
        <p className="text-gray-600 mt-1">2+1 layout • Stock Analysis with Market Context</p>
      </LayoutHeader>

      <div className="flex-1 grid grid-cols-2 grid-rows-2 gap-4 min-h-0">
        
        <div className="col-span-1 row-span-1">
          <div className="h-full bg-white rounded-lg border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="text-xl font-bold text-blue-900">AAPL</h3>
                <p className="text-gray-600 text-sm">Apple Inc.</p>
              </div>
              <div className="text-right">
                <div className="text-2xl font-bold text-green-600">$175.43</div>
                <div className="text-sm text-green-600">+$2.18 (+1.26%)</div>
              </div>
            </div>
            
            <div className="space-y-3 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-600">Market Cap</span>
                <span className="font-medium">$2.73T</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">P/E Ratio</span>
                <span className="font-medium">29.8</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Volume</span>
                <span className="font-medium">45.2M</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">52W High</span>
                <span className="font-medium">$199.62</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">52W Low</span>
                <span className="font-medium">$164.08</span>
              </div>
            </div>

            <div className="mt-4 p-3 bg-blue-50 rounded border border-blue-200">
              <div className="text-blue-800 font-medium text-sm mb-1">Analyst Rating</div>
              <div className="text-blue-700 text-sm">Strong Buy • Target: $195</div>
            </div>
          </div>
        </div>

        <div className="col-span-1 row-span-1">
          <div className="h-full bg-white rounded-lg border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="text-xl font-bold text-purple-900">NVDA</h3>
                <p className="text-gray-600 text-sm">NVIDIA Corp.</p>
              </div>
              <div className="text-right">
                <div className="text-2xl font-bold text-green-600">$478.32</div>
                <div className="text-sm text-green-600">+$12.87 (+2.77%)</div>
              </div>
            </div>
            
            <div className="space-y-3 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-600">Market Cap</span>
                <span className="font-medium">$1.18T</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">P/E Ratio</span>
                <span className="font-medium">71.2</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Volume</span>
                <span className="font-medium">87.4M</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">52W High</span>
                <span className="font-medium">$502.66</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">52W Low</span>
                <span className="font-medium">$180.96</span>
              </div>
            </div>

            <div className="mt-4 p-3 bg-purple-50 rounded border border-purple-200">
              <div className="text-purple-800 font-medium text-sm mb-1">Analyst Rating</div>
              <div className="text-purple-700 text-sm">Buy • Target: $525</div>
            </div>
          </div>
        </div>

        <div className="col-span-2 row-span-1">
          <div className="h-full bg-white rounded-lg border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="text-xl font-bold text-gray-900">📊 Market Overview</h3>
                <p className="text-gray-600 text-sm">Major Indices & Market Sentiment</p>
              </div>
              <div className="text-right">
                <div className="text-sm text-green-600">Market Open</div>
                <div className="text-lg font-medium text-gray-900">Strong Bullish</div>
              </div>
            </div>
            
            <div className="grid grid-cols-4 gap-6">
              <div className="text-center">
                <h4 className="text-sm font-medium text-gray-700 mb-2">S&P 500</h4>
                <div className="text-2xl font-bold text-green-600">4,742.83</div>
                <div className="text-sm text-green-600">+0.85%</div>
                <div className="text-xs text-gray-500 mt-1">+39.78 pts</div>
              </div>
              
              <div className="text-center">
                <h4 className="text-sm font-medium text-gray-700 mb-2">NASDAQ</h4>
                <div className="text-2xl font-bold text-green-600">14,857.71</div>
                <div className="text-sm text-green-600">+1.12%</div>
                <div className="text-xs text-gray-500 mt-1">+164.12 pts</div>
              </div>
              
              <div className="text-center">
                <h4 className="text-sm font-medium text-gray-700 mb-2">Dow Jones</h4>
                <div className="text-2xl font-bold text-green-600">37,248.92</div>
                <div className="text-sm text-green-600">+0.64%</div>
                <div className="text-xs text-gray-500 mt-1">+236.28 pts</div>
              </div>
              
              <div className="text-center">
                <h4 className="text-sm font-medium text-gray-700 mb-2">VIX</h4>
                <div className="text-2xl font-bold text-red-600">12.47</div>
                <div className="text-sm text-red-600">-0.23%</div>
                <div className="text-xs text-gray-500 mt-1">Low Fear</div>
              </div>
            </div>

            <div className="mt-6 flex justify-between items-center">
              <div className="flex space-x-6 text-sm">
                <div>
                  <span className="text-gray-600">Advancing:</span>
                  <span className="font-medium text-green-600 ml-1">2,847</span>
                </div>
                <div>
                  <span className="text-gray-600">Declining:</span>
                  <span className="font-medium text-red-600 ml-1">1,423</span>
                </div>
                <div>
                  <span className="text-gray-600">Unchanged:</span>
                  <span className="font-medium text-gray-600 ml-1">267</span>
                </div>
              </div>
              
              <div className="text-sm">
                <span className="text-gray-600">Market Cap:</span>
                <span className="font-medium text-gray-900 ml-1">$47.2T</span>
              </div>
            </div>
          </div>
        </div>

      </div>
      
    </LayoutContainer>
  );
}