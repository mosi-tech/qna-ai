'use client';

import LayoutContainer from '@/components/insights/layout/components/LayoutContainer';
import LayoutHeader from '@/components/insights/layout/components/LayoutHeader';

export default function Grid3Variant2() {
  return (
    <LayoutContainer>
      
      <LayoutHeader>
        <h1 className="text-2xl font-bold text-gray-900">Grid/3/2: Risk Level Analysis</h1>
        <p className="text-gray-600 mt-1">1×3 grid • Conservative, Moderate, Aggressive Portfolios</p>
      </LayoutHeader>

      <div className="flex-1 grid grid-cols-1 grid-rows-3 gap-4 min-h-0">
        
        <div className="col-span-1 row-span-1">
          <div className="h-full bg-gradient-to-r from-green-50 to-emerald-50 rounded-lg border border-green-200 p-6">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="text-xl font-bold text-green-900">🛡️ Conservative Portfolio</h3>
                <p className="text-green-700 text-sm">Capital Preservation Strategy</p>
              </div>
              <div className="text-right">
                <div className="text-2xl font-bold text-green-600">+4.8%</div>
                <div className="text-sm text-green-600">Expected Return</div>
              </div>
            </div>
            
            <div className="grid grid-cols-3 gap-4">
              <div className="text-center">
                <div className="w-12 h-12 bg-green-500 rounded-full mx-auto mb-2 flex items-center justify-center">
                  <span className="text-white font-bold text-sm">60%</span>
                </div>
                <div className="text-xs font-medium">Bonds</div>
                <div className="text-xs text-gray-600">$1.8M</div>
              </div>
              
              <div className="text-center">
                <div className="w-12 h-12 bg-blue-500 rounded-full mx-auto mb-2 flex items-center justify-center">
                  <span className="text-white font-bold text-sm">30%</span>
                </div>
                <div className="text-xs font-medium">Large Cap</div>
                <div className="text-xs text-gray-600">$900K</div>
              </div>
              
              <div className="text-center">
                <div className="w-12 h-12 bg-gray-500 rounded-full mx-auto mb-2 flex items-center justify-center">
                  <span className="text-white font-bold text-sm">10%</span>
                </div>
                <div className="text-xs font-medium">Cash</div>
                <div className="text-xs text-gray-600">$300K</div>
              </div>
            </div>

            <div className="mt-4 flex justify-between text-sm">
              <span className="text-green-700">Risk Level: <span className="font-medium">Low</span></span>
              <span className="text-green-700">Volatility: <span className="font-medium">6.2%</span></span>
            </div>
          </div>
        </div>

        <div className="col-span-1 row-span-1">
          <div className="h-full bg-gradient-to-r from-yellow-50 to-orange-50 rounded-lg border border-yellow-200 p-6">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="text-xl font-bold text-orange-900">⚖️ Moderate Portfolio</h3>
                <p className="text-orange-700 text-sm">Balanced Growth Strategy</p>
              </div>
              <div className="text-right">
                <div className="text-2xl font-bold text-orange-600">+8.2%</div>
                <div className="text-sm text-orange-600">Expected Return</div>
              </div>
            </div>
            
            <div className="grid grid-cols-4 gap-3">
              <div className="text-center">
                <div className="w-12 h-12 bg-green-500 rounded-full mx-auto mb-2 flex items-center justify-center">
                  <span className="text-white font-bold text-sm">40%</span>
                </div>
                <div className="text-xs font-medium">Bonds</div>
                <div className="text-xs text-gray-600">$1.2M</div>
              </div>
              
              <div className="text-center">
                <div className="w-12 h-12 bg-blue-500 rounded-full mx-auto mb-2 flex items-center justify-center">
                  <span className="text-white font-bold text-sm">40%</span>
                </div>
                <div className="text-xs font-medium">Large Cap</div>
                <div className="text-xs text-gray-600">$1.2M</div>
              </div>
              
              <div className="text-center">
                <div className="w-12 h-12 bg-purple-500 rounded-full mx-auto mb-2 flex items-center justify-center">
                  <span className="text-white font-bold text-sm">15%</span>
                </div>
                <div className="text-xs font-medium">Mid Cap</div>
                <div className="text-xs text-gray-600">$450K</div>
              </div>
              
              <div className="text-center">
                <div className="w-12 h-12 bg-gray-500 rounded-full mx-auto mb-2 flex items-center justify-center">
                  <span className="text-white font-bold text-sm">5%</span>
                </div>
                <div className="text-xs font-medium">Cash</div>
                <div className="text-xs text-gray-600">$150K</div>
              </div>
            </div>

            <div className="mt-4 flex justify-between text-sm">
              <span className="text-orange-700">Risk Level: <span className="font-medium">Medium</span></span>
              <span className="text-orange-700">Volatility: <span className="font-medium">11.8%</span></span>
            </div>
          </div>
        </div>

        <div className="col-span-1 row-span-1">
          <div className="h-full bg-gradient-to-r from-red-50 to-pink-50 rounded-lg border border-red-200 p-6">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="text-xl font-bold text-red-900">🚀 Aggressive Portfolio</h3>
                <p className="text-red-700 text-sm">Maximum Growth Strategy</p>
              </div>
              <div className="text-right">
                <div className="text-2xl font-bold text-red-600">+14.7%</div>
                <div className="text-sm text-red-600">Expected Return</div>
              </div>
            </div>
            
            <div className="grid grid-cols-5 gap-2">
              <div className="text-center">
                <div className="w-10 h-10 bg-green-500 rounded-full mx-auto mb-1 flex items-center justify-center">
                  <span className="text-white font-bold text-xs">20%</span>
                </div>
                <div className="text-xs font-medium">Bonds</div>
                <div className="text-xs text-gray-600">$600K</div>
              </div>
              
              <div className="text-center">
                <div className="w-10 h-10 bg-blue-500 rounded-full mx-auto mb-1 flex items-center justify-center">
                  <span className="text-white font-bold text-xs">30%</span>
                </div>
                <div className="text-xs font-medium">Large</div>
                <div className="text-xs text-gray-600">$900K</div>
              </div>
              
              <div className="text-center">
                <div className="w-10 h-10 bg-purple-500 rounded-full mx-auto mb-1 flex items-center justify-center">
                  <span className="text-white font-bold text-xs">25%</span>
                </div>
                <div className="text-xs font-medium">Mid</div>
                <div className="text-xs text-gray-600">$750K</div>
              </div>
              
              <div className="text-center">
                <div className="w-10 h-10 bg-red-500 rounded-full mx-auto mb-1 flex items-center justify-center">
                  <span className="text-white font-bold text-xs">20%</span>
                </div>
                <div className="text-xs font-medium">Small</div>
                <div className="text-xs text-gray-600">$600K</div>
              </div>
              
              <div className="text-center">
                <div className="w-10 h-10 bg-yellow-500 rounded-full mx-auto mb-1 flex items-center justify-center">
                  <span className="text-white font-bold text-xs">5%</span>
                </div>
                <div className="text-xs font-medium">Spec</div>
                <div className="text-xs text-gray-600">$150K</div>
              </div>
            </div>

            <div className="mt-4 flex justify-between text-sm">
              <span className="text-red-700">Risk Level: <span className="font-medium">High</span></span>
              <span className="text-red-700">Volatility: <span className="font-medium">19.3%</span></span>
            </div>
          </div>
        </div>

      </div>
      
    </LayoutContainer>
  );
}