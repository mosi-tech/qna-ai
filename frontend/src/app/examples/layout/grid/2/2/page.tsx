'use client';

import LayoutContainer from '@/components/insights/layout/components/LayoutContainer';
import LayoutHeader from '@/components/insights/layout/components/LayoutHeader';

export default function Grid2Variant2() {
  return (
    <LayoutContainer>
      
      <LayoutHeader>
        <h1 className="text-2xl font-bold text-gray-900">Grid/2/2: Current vs Target</h1>
        <p className="text-gray-600 mt-1">1×2 grid • Portfolio Allocation Analysis</p>
      </LayoutHeader>

      <div className="flex-1 grid grid-cols-1 grid-rows-2 gap-4 min-h-0">
        
        <div className="col-span-1 row-span-1">
          <div className="h-full bg-white rounded-lg border border-gray-200 p-6">
            <h3 className="text-xl font-bold text-gray-900 mb-4">Current Allocation</h3>
            
            <div className="grid grid-cols-4 gap-4">
              <div className="text-center">
                <div className="w-16 h-16 bg-blue-500 rounded-full mx-auto mb-2 flex items-center justify-center">
                  <span className="text-white font-bold text-lg">65%</span>
                </div>
                <div className="text-sm font-medium">Equities</div>
                <div className="text-xs text-gray-600">$1.95M</div>
              </div>
              
              <div className="text-center">
                <div className="w-16 h-16 bg-green-500 rounded-full mx-auto mb-2 flex items-center justify-center">
                  <span className="text-white font-bold text-lg">25%</span>
                </div>
                <div className="text-sm font-medium">Bonds</div>
                <div className="text-xs text-gray-600">$750K</div>
              </div>
              
              <div className="text-center">
                <div className="w-16 h-16 bg-yellow-500 rounded-full mx-auto mb-2 flex items-center justify-center">
                  <span className="text-white font-bold text-lg">8%</span>
                </div>
                <div className="text-sm font-medium">REITs</div>
                <div className="text-xs text-gray-600">$240K</div>
              </div>
              
              <div className="text-center">
                <div className="w-16 h-16 bg-gray-500 rounded-full mx-auto mb-2 flex items-center justify-center">
                  <span className="text-white font-bold text-lg">2%</span>
                </div>
                <div className="text-sm font-medium">Cash</div>
                <div className="text-xs text-gray-600">$60K</div>
              </div>
            </div>

            <div className="mt-6 flex justify-between items-center text-sm">
              <span className="text-gray-600">Total Portfolio Value:</span>
              <span className="font-bold text-lg">$3.0M</span>
            </div>
          </div>
        </div>

        <div className="col-span-1 row-span-1">
          <div className="h-full bg-white rounded-lg border border-gray-200 p-6">
            <h3 className="text-xl font-bold text-gray-900 mb-4">Target Allocation</h3>
            
            <div className="grid grid-cols-4 gap-4">
              <div className="text-center">
                <div className="w-16 h-16 bg-blue-400 rounded-full border-2 border-dashed border-blue-600 mx-auto mb-2 flex items-center justify-center">
                  <span className="text-blue-800 font-bold text-lg">60%</span>
                </div>
                <div className="text-sm font-medium">Equities</div>
                <div className="text-xs text-red-600">-5% (Rebalance)</div>
              </div>
              
              <div className="text-center">
                <div className="w-16 h-16 bg-green-400 rounded-full border-2 border-dashed border-green-600 mx-auto mb-2 flex items-center justify-center">
                  <span className="text-green-800 font-bold text-lg">30%</span>
                </div>
                <div className="text-sm font-medium">Bonds</div>
                <div className="text-xs text-green-600">+5% (Buy)</div>
              </div>
              
              <div className="text-center">
                <div className="w-16 h-16 bg-yellow-400 rounded-full border-2 border-dashed border-yellow-600 mx-auto mb-2 flex items-center justify-center">
                  <span className="text-yellow-800 font-bold text-lg">8%</span>
                </div>
                <div className="text-sm font-medium">REITs</div>
                <div className="text-xs text-gray-600">On Target</div>
              </div>
              
              <div className="text-center">
                <div className="w-16 h-16 bg-gray-400 rounded-full border-2 border-dashed border-gray-600 mx-auto mb-2 flex items-center justify-center">
                  <span className="text-gray-800 font-bold text-lg">2%</span>
                </div>
                <div className="text-sm font-medium">Cash</div>
                <div className="text-xs text-gray-600">On Target</div>
              </div>
            </div>

            <div className="mt-6 p-3 bg-yellow-50 rounded border border-yellow-200">
              <div className="text-yellow-800 font-medium text-sm mb-1">⚠️ Rebalancing Required</div>
              <div className="text-yellow-700 text-sm">Sell $150K equities, buy $150K bonds</div>
            </div>
          </div>
        </div>

      </div>
      
    </LayoutContainer>
  );
}