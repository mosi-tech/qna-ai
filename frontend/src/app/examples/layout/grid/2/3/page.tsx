'use client';

import LayoutContainer from '@/components/insights/layout/components/LayoutContainer';
import LayoutHeader from '@/components/insights/layout/components/LayoutHeader';

export default function Grid2Variant3() {
  return (
    <LayoutContainer>
      
      <LayoutHeader>
        <h1 className="text-2xl font-bold text-gray-900">Grid/2/3: Portfolio vs Benchmark</h1>
        <p className="text-gray-600 mt-1">2×1 grid • Performance Comparison Analysis</p>
      </LayoutHeader>

      <div className="flex-1 grid grid-cols-2 grid-rows-1 gap-4 min-h-0">
        
        <div className="col-span-1 row-span-1">
          <div className="h-full bg-white rounded-lg border border-gray-200 p-6">
            <h3 className="text-xl font-bold text-gray-900 mb-6 text-center">My Portfolio</h3>
            
            <div className="text-center mb-6">
              <div className="text-4xl font-bold text-green-600 mb-2">+18.4%</div>
              <div className="text-sm text-gray-600">YTD Return</div>
            </div>
            
            <div className="space-y-4">
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">1 Month</span>
                <span className="font-medium text-green-600">+2.8%</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">3 Months</span>
                <span className="font-medium text-green-600">+8.1%</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">6 Months</span>
                <span className="font-medium text-green-600">+12.5%</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">1 Year</span>
                <span className="font-medium text-green-600">+22.3%</span>
              </div>
            </div>

            <div className="mt-6 space-y-3">
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Sharpe Ratio</span>
                <span className="font-medium">1.42</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Max Drawdown</span>
                <span className="font-medium text-red-600">-8.2%</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Volatility</span>
                <span className="font-medium">15.8%</span>
              </div>
            </div>

            <div className="mt-6 p-3 bg-green-50 rounded border border-green-200">
              <div className="text-green-800 font-medium text-sm">✓ Outperforming</div>
            </div>
          </div>
        </div>

        <div className="col-span-1 row-span-1">
          <div className="h-full bg-white rounded-lg border border-gray-200 p-6">
            <h3 className="text-xl font-bold text-gray-900 mb-6 text-center">S&P 500 Index</h3>
            
            <div className="text-center mb-6">
              <div className="text-4xl font-bold text-blue-600 mb-2">+14.2%</div>
              <div className="text-sm text-gray-600">YTD Return</div>
            </div>
            
            <div className="space-y-4">
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">1 Month</span>
                <span className="font-medium text-blue-600">+1.9%</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">3 Months</span>
                <span className="font-medium text-blue-600">+6.4%</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">6 Months</span>
                <span className="font-medium text-blue-600">+9.8%</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">1 Year</span>
                <span className="font-medium text-blue-600">+18.7%</span>
              </div>
            </div>

            <div className="mt-6 space-y-3">
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Sharpe Ratio</span>
                <span className="font-medium">1.18</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Max Drawdown</span>
                <span className="font-medium text-red-600">-12.1%</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Volatility</span>
                <span className="font-medium">18.3%</span>
              </div>
            </div>

            <div className="mt-6 p-3 bg-blue-50 rounded border border-blue-200">
              <div className="text-blue-800 font-medium text-sm">📊 Benchmark</div>
            </div>
          </div>
        </div>

      </div>
      
    </LayoutContainer>
  );
}