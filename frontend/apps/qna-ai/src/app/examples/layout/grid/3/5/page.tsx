'use client';

import LayoutContainer from '@/components/insights/layout/components/LayoutContainer';
import LayoutHeader from '@/components/insights/layout/components/LayoutHeader';

export default function Grid3Variant5() {
  return (
    <LayoutContainer>
      
      <LayoutHeader>
        <h1 className="text-2xl font-bold text-gray-900">Grid/3/5: Geographic Allocation</h1>
        <p className="text-gray-600 mt-1">3×1 grid • US, International, Emerging Market Exposure</p>
      </LayoutHeader>

      <div className="flex-1 grid grid-cols-3 grid-rows-1 gap-4 min-h-0">
        
        <div className="col-span-1 row-span-1">
          <div className="h-full bg-gradient-to-br from-blue-50 to-red-50 rounded-lg border border-blue-200 p-6">
            <div className="text-center mb-6">
              <h3 className="text-2xl font-bold text-blue-900">🇺🇸 United States</h3>
              <p className="text-blue-700">Domestic Market Exposure</p>
            </div>
            
            <div className="space-y-4">
              <div className="text-center">
                <div className="text-4xl font-bold text-blue-600 mb-2">68%</div>
                <div className="text-lg font-medium text-blue-800">$2.04M</div>
                <div className="text-sm text-green-600">+15.2% YTD</div>
              </div>
              
              <div className="space-y-3 text-sm">
                <div className="flex justify-between">
                  <span className="text-blue-700">S&P 500</span>
                  <span className="font-medium">55% • $1.65M</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-blue-700">Mid/Small Cap</span>
                  <span className="font-medium">25% • $750K</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-blue-700">Tech Focus</span>
                  <span className="font-medium">20% • $600K</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-blue-700">Dollar Weight</span>
                  <span className="font-medium text-blue-600">100%</span>
                </div>
              </div>

              <div className="mt-6 space-y-2">
                <div className="text-sm font-medium text-blue-800">Top Holdings:</div>
                <div className="space-y-1 text-xs">
                  <div className="flex justify-between">
                    <span className="text-blue-700">Apple Inc.</span>
                    <span className="text-blue-800">8.2%</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-blue-700">Microsoft</span>
                    <span className="text-blue-800">7.1%</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-blue-700">NVIDIA</span>
                    <span className="text-blue-800">4.8%</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-blue-700">Amazon</span>
                    <span className="text-blue-800">3.9%</span>
                  </div>
                </div>
              </div>

              <div className="mt-6 p-3 bg-blue-100 rounded border border-blue-300">
                <div className="text-blue-800 font-medium text-sm">Market Outlook</div>
                <div className="text-blue-700 text-xs">Strong fundamentals, innovation leader</div>
              </div>
            </div>
          </div>
        </div>

        <div className="col-span-1 row-span-1">
          <div className="h-full bg-gradient-to-br from-green-50 to-blue-50 rounded-lg border border-green-200 p-6">
            <div className="text-center mb-6">
              <h3 className="text-2xl font-bold text-green-900">🌍 International</h3>
              <p className="text-green-700">Developed Market Exposure</p>
            </div>
            
            <div className="space-y-4">
              <div className="text-center">
                <div className="text-4xl font-bold text-green-600 mb-2">22%</div>
                <div className="text-lg font-medium text-green-800">$660K</div>
                <div className="text-sm text-green-600">+9.4% YTD</div>
              </div>
              
              <div className="space-y-3 text-sm">
                <div className="flex justify-between">
                  <span className="text-green-700">Europe</span>
                  <span className="font-medium">45% • $297K</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-green-700">Japan</span>
                  <span className="font-medium">30% • $198K</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-green-700">Asia-Pacific ex Japan</span>
                  <span className="font-medium">25% • $165K</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-green-700">Currency Hedge</span>
                  <span className="font-medium text-orange-600">60%</span>
                </div>
              </div>

              <div className="mt-6 space-y-2">
                <div className="text-sm font-medium text-green-800">Regional Breakdown:</div>
                <div className="space-y-1 text-xs">
                  <div className="flex justify-between">
                    <span className="text-green-700">Germany</span>
                    <span className="text-green-800">12%</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-green-700">United Kingdom</span>
                    <span className="text-green-800">11%</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-green-700">Japan</span>
                    <span className="text-green-800">30%</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-green-700">Others</span>
                    <span className="text-green-800">47%</span>
                  </div>
                </div>
              </div>

              <div className="mt-6 p-3 bg-green-100 rounded border border-green-300">
                <div className="text-green-800 font-medium text-sm">Diversification</div>
                <div className="text-green-700 text-xs">Geographic risk mitigation</div>
              </div>
            </div>
          </div>
        </div>

        <div className="col-span-1 row-span-1">
          <div className="h-full bg-gradient-to-br from-orange-50 to-red-50 rounded-lg border border-orange-200 p-6">
            <div className="text-center mb-6">
              <h3 className="text-2xl font-bold text-orange-900">🌏 Emerging Markets</h3>
              <p className="text-orange-700">Growth Market Exposure</p>
            </div>
            
            <div className="space-y-4">
              <div className="text-center">
                <div className="text-4xl font-bold text-orange-600 mb-2">10%</div>
                <div className="text-lg font-medium text-orange-800">$300K</div>
                <div className="text-sm text-red-600">-2.1% YTD</div>
              </div>
              
              <div className="space-y-3 text-sm">
                <div className="flex justify-between">
                  <span className="text-orange-700">China</span>
                  <span className="font-medium">35% • $105K</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-orange-700">India</span>
                  <span className="font-medium">25% • $75K</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-orange-700">Brazil</span>
                  <span className="font-medium">15% • $45K</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-orange-700">Others</span>
                  <span className="font-medium">25% • $75K</span>
                </div>
              </div>

              <div className="mt-6 space-y-2">
                <div className="text-sm font-medium text-orange-800">Sector Focus:</div>
                <div className="space-y-1 text-xs">
                  <div className="flex justify-between">
                    <span className="text-orange-700">Technology</span>
                    <span className="text-orange-800">28%</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-orange-700">Financial</span>
                    <span className="text-orange-800">22%</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-orange-700">Consumer</span>
                    <span className="text-orange-800">18%</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-orange-700">Materials</span>
                    <span className="text-orange-800">32%</span>
                  </div>
                </div>
              </div>

              <div className="mt-6 p-3 bg-orange-100 rounded border border-orange-300">
                <div className="text-orange-800 font-medium text-sm">Growth Potential</div>
                <div className="text-orange-700 text-xs">High risk, high reward opportunity</div>
              </div>
            </div>
          </div>
        </div>

      </div>
      
    </LayoutContainer>
  );
}