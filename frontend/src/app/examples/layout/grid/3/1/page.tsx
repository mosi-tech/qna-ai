'use client';

import LayoutContainer from '@/components/insights/layout/components/LayoutContainer';
import LayoutHeader from '@/components/insights/layout/components/LayoutHeader';

export default function Grid3Variant1() {
  return (
    <LayoutContainer>
      
      <LayoutHeader>
        <h1 className="text-2xl font-bold text-gray-900">Grid/3/1: Key Financial Metrics</h1>
        <p className="text-gray-600 mt-1">3×1 grid • Revenue, Profit, Growth Analysis</p>
      </LayoutHeader>

      <div className="flex-1 grid grid-cols-3 grid-rows-1 gap-4 min-h-0">
        
        <div className="col-span-1 row-span-1">
          <div className="h-full bg-white rounded-lg border border-gray-200 p-6">
            <div className="text-center">
              <div className="w-16 h-16 bg-blue-500 rounded-full mx-auto mb-4 flex items-center justify-center">
                <span className="text-white text-2xl">💰</span>
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-2">Revenue</h3>
              <div className="text-3xl font-bold text-blue-600 mb-2">$2.4M</div>
              <div className="text-sm text-green-600 mb-4">+12.8% vs Q3</div>
            </div>
            
            <div className="space-y-3 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-600">Q4 Target</span>
                <span className="font-medium">$2.6M</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">YTD Total</span>
                <span className="font-medium">$8.9M</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Growth Rate</span>
                <span className="font-medium text-green-600">+18.2%</span>
              </div>
            </div>

            <div className="mt-6 p-3 bg-blue-50 rounded border border-blue-200">
              <div className="text-blue-800 font-medium text-sm">📈 Strong Growth</div>
              <div className="text-blue-700 text-xs mt-1">Exceeding targets</div>
            </div>
          </div>
        </div>

        <div className="col-span-1 row-span-1">
          <div className="h-full bg-white rounded-lg border border-gray-200 p-6">
            <div className="text-center">
              <div className="w-16 h-16 bg-green-500 rounded-full mx-auto mb-4 flex items-center justify-center">
                <span className="text-white text-2xl">📊</span>
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-2">Net Profit</h3>
              <div className="text-3xl font-bold text-green-600 mb-2">$485K</div>
              <div className="text-sm text-green-600 mb-4">+8.4% vs Q3</div>
            </div>
            
            <div className="space-y-3 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-600">Profit Margin</span>
                <span className="font-medium">20.2%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">YTD Profit</span>
                <span className="font-medium">$1.7M</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">EBITDA</span>
                <span className="font-medium">$625K</span>
              </div>
            </div>

            <div className="mt-6 p-3 bg-green-50 rounded border border-green-200">
              <div className="text-green-800 font-medium text-sm">✓ Healthy Margins</div>
              <div className="text-green-700 text-xs mt-1">Above industry avg</div>
            </div>
          </div>
        </div>

        <div className="col-span-1 row-span-1">
          <div className="h-full bg-white rounded-lg border border-gray-200 p-6">
            <div className="text-center">
              <div className="w-16 h-16 bg-purple-500 rounded-full mx-auto mb-4 flex items-center justify-center">
                <span className="text-white text-2xl">🚀</span>
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-2">Growth Rate</h3>
              <div className="text-3xl font-bold text-purple-600 mb-2">+24.1%</div>
              <div className="text-sm text-green-600 mb-4">YoY Revenue</div>
            </div>
            
            <div className="space-y-3 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-600">Customer Growth</span>
                <span className="font-medium text-green-600">+31.2%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Market Share</span>
                <span className="font-medium">8.4%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Expansion Rate</span>
                <span className="font-medium text-green-600">+15.8%</span>
              </div>
            </div>

            <div className="mt-6 p-3 bg-purple-50 rounded border border-purple-200">
              <div className="text-purple-800 font-medium text-sm">🎯 Accelerating</div>
              <div className="text-purple-700 text-xs mt-1">Outpacing market</div>
            </div>
          </div>
        </div>

      </div>
      
    </LayoutContainer>
  );
}