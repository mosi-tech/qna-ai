'use client';

import LayoutContainer from '@/components/insights/layout/components/LayoutContainer';
import LayoutHeader from '@/components/insights/layout/components/LayoutHeader';

export default function Grid2Variant1() {
  return (
    <LayoutContainer>
      
      <LayoutHeader>
        <h1 className="text-2xl font-bold text-gray-900">Grid/2/1: Side-by-Side Comparison</h1>
        <p className="text-gray-600 mt-1">2×1 grid • Apple vs Microsoft Stock Performance</p>
      </LayoutHeader>

      <div className="flex-1 grid grid-cols-2 grid-rows-1 gap-4 min-h-0">
        
        <div className="col-span-1 row-span-1">
          <div className="h-full bg-white rounded-lg border border-gray-200 p-6">
            <div className="text-center mb-6">
              <h3 className="text-2xl font-bold text-gray-900">AAPL</h3>
              <p className="text-gray-600">Apple Inc.</p>
            </div>
            
            <div className="space-y-4">
              <div className="text-center">
                <div className="text-3xl font-bold text-green-600 mb-2">$175.43</div>
                <div className="text-sm text-green-600">+$2.18 (+1.26%)</div>
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
                  <span className="text-gray-600">YTD Return</span>
                  <span className="font-medium text-green-600">+14.8%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Volatility</span>
                  <span className="font-medium">18.2%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Beta</span>
                  <span className="font-medium">1.12</span>
                </div>
              </div>

              <div className="mt-6 p-3 bg-blue-50 rounded border border-blue-200">
                <div className="text-blue-800 font-medium text-sm mb-1">Analyst Rating</div>
                <div className="text-blue-700 text-sm">Strong Buy • Price Target: $195</div>
              </div>
            </div>
          </div>
        </div>

        <div className="col-span-1 row-span-1">
          <div className="h-full bg-white rounded-lg border border-gray-200 p-6">
            <div className="text-center mb-6">
              <h3 className="text-2xl font-bold text-gray-900">MSFT</h3>
              <p className="text-gray-600">Microsoft Corp.</p>
            </div>
            
            <div className="space-y-4">
              <div className="text-center">
                <div className="text-3xl font-bold text-green-600 mb-2">$412.87</div>
                <div className="text-sm text-green-600">+$5.23 (+1.28%)</div>
              </div>
              
              <div className="space-y-3 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600">Market Cap</span>
                  <span className="font-medium">$3.07T</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">P/E Ratio</span>
                  <span className="font-medium">33.2</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">YTD Return</span>
                  <span className="font-medium text-green-600">+16.2%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Volatility</span>
                  <span className="font-medium">22.1%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Beta</span>
                  <span className="font-medium">0.89</span>
                </div>
              </div>

              <div className="mt-6 p-3 bg-green-50 rounded border border-green-200">
                <div className="text-green-800 font-medium text-sm mb-1">Analyst Rating</div>
                <div className="text-green-700 text-sm">Buy • Price Target: $450</div>
              </div>
            </div>
          </div>
        </div>

      </div>
      
    </LayoutContainer>
  );
}