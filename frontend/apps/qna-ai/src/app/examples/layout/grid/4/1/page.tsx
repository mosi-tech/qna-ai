'use client';

import LayoutContainer from '@/components/insights/layout/components/LayoutContainer';
import LayoutHeader from '@/components/insights/layout/components/LayoutHeader';

export default function Grid4Variant1() {
  return (
    <LayoutContainer>
      
      <LayoutHeader>
        <h1 className="text-2xl font-bold text-gray-900">Grid/4/1: Quarterly Performance</h1>
        <p className="text-gray-600 mt-1">4×1 grid • Q1, Q2, Q3, Q4 Financial Timeline</p>
      </LayoutHeader>

      <div className="flex-1 grid grid-cols-4 grid-rows-1 gap-4 min-h-0">
        
        <div className="col-span-1 row-span-1">
          <div className="h-full bg-gradient-to-br from-green-50 to-emerald-50 rounded-lg border border-green-200 p-6">
            <div className="text-center mb-6">
              <h3 className="text-2xl font-bold text-green-900">Q1 2023</h3>
              <p className="text-green-700">Jan - Mar</p>
            </div>
            
            <div className="space-y-4">
              <div className="text-center">
                <div className="text-3xl font-bold text-green-600 mb-2">+8.4%</div>
                <div className="text-sm text-green-700">Portfolio Return</div>
              </div>
              
              <div className="space-y-3 text-sm">
                <div className="flex justify-between">
                  <span className="text-green-700">Revenue</span>
                  <span className="font-medium">$219.8B</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-green-700">Net Income</span>
                  <span className="font-medium">$48.2B</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-green-700">EPS</span>
                  <span className="font-medium">$1.87</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-green-700">Market Cap</span>
                  <span className="font-medium">$2.41T</span>
                </div>
              </div>

              <div className="mt-6 space-y-2 text-xs">
                <div className="text-green-800 font-medium mb-1">Key Events:</div>
                <div className="text-green-700">
                  • Strong earnings beat<br/>
                  • Product launch success<br/>
                  • Market expansion
                </div>
              </div>

              <div className="mt-6 p-2 bg-green-100 rounded border border-green-300">
                <div className="text-green-800 font-medium text-xs">Status</div>
                <div className="text-green-700 text-xs">Excellent Start</div>
              </div>
            </div>
          </div>
        </div>

        <div className="col-span-1 row-span-1">
          <div className="h-full bg-gradient-to-br from-blue-50 to-cyan-50 rounded-lg border border-blue-200 p-6">
            <div className="text-center mb-6">
              <h3 className="text-2xl font-bold text-blue-900">Q2 2023</h3>
              <p className="text-blue-700">Apr - Jun</p>
            </div>
            
            <div className="space-y-4">
              <div className="text-center">
                <div className="text-3xl font-bold text-blue-600 mb-2">+5.2%</div>
                <div className="text-sm text-blue-700">Portfolio Return</div>
              </div>
              
              <div className="space-y-3 text-sm">
                <div className="flex justify-between">
                  <span className="text-blue-700">Revenue</span>
                  <span className="font-medium">$201.2B</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-blue-700">Net Income</span>
                  <span className="font-medium">$43.2B</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-blue-700">EPS</span>
                  <span className="font-medium">$1.69</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-blue-700">Market Cap</span>
                  <span className="font-medium">$2.54T</span>
                </div>
              </div>

              <div className="mt-6 space-y-2 text-xs">
                <div className="text-blue-800 font-medium mb-1">Key Events:</div>
                <div className="text-blue-700">
                  • Seasonal slowdown<br/>
                  • Supply chain issues<br/>
                  • Cost management
                </div>
              </div>

              <div className="mt-6 p-2 bg-blue-100 rounded border border-blue-300">
                <div className="text-blue-800 font-medium text-xs">Status</div>
                <div className="text-blue-700 text-xs">Solid Performance</div>
              </div>
            </div>
          </div>
        </div>

        <div className="col-span-1 row-span-1">
          <div className="h-full bg-gradient-to-br from-purple-50 to-violet-50 rounded-lg border border-purple-200 p-6">
            <div className="text-center mb-6">
              <h3 className="text-2xl font-bold text-purple-900">Q3 2023</h3>
              <p className="text-purple-700">Jul - Sep</p>
            </div>
            
            <div className="space-y-4">
              <div className="text-center">
                <div className="text-3xl font-bold text-purple-600 mb-2">+6.7%</div>
                <div className="text-sm text-purple-700">Portfolio Return</div>
              </div>
              
              <div className="space-y-3 text-sm">
                <div className="flex justify-between">
                  <span className="text-purple-700">Revenue</span>
                  <span className="font-medium">$206.8B</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-purple-700">Net Income</span>
                  <span className="font-medium">$46.8B</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-purple-700">EPS</span>
                  <span className="font-medium">$1.84</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-purple-700">Market Cap</span>
                  <span className="font-medium">$2.71T</span>
                </div>
              </div>

              <div className="mt-6 space-y-2 text-xs">
                <div className="text-purple-800 font-medium mb-1">Key Events:</div>
                <div className="text-purple-700">
                  • Back-to-school surge<br/>
                  • New partnerships<br/>
                  • Innovation progress
                </div>
              </div>

              <div className="mt-6 p-2 bg-purple-100 rounded border border-purple-300">
                <div className="text-purple-800 font-medium text-xs">Status</div>
                <div className="text-purple-700 text-xs">Recovery Mode</div>
              </div>
            </div>
          </div>
        </div>

        <div className="col-span-1 row-span-1">
          <div className="h-full bg-gradient-to-br from-orange-50 to-red-50 rounded-lg border border-orange-200 p-6">
            <div className="text-center mb-6">
              <h3 className="text-2xl font-bold text-orange-900">Q4 2023</h3>
              <p className="text-orange-700">Oct - Dec</p>
            </div>
            
            <div className="space-y-4">
              <div className="text-center">
                <div className="text-3xl font-bold text-orange-600 mb-2">+9.1%</div>
                <div className="text-sm text-orange-700">Portfolio Return</div>
              </div>
              
              <div className="space-y-3 text-sm">
                <div className="flex justify-between">
                  <span className="text-orange-700">Revenue</span>
                  <span className="font-medium">$219.4B</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-orange-700">Net Income</span>
                  <span className="font-medium">$52.1B</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-orange-700">EPS</span>
                  <span className="font-medium">$2.04</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-orange-700">Market Cap</span>
                  <span className="font-medium">$2.73T</span>
                </div>
              </div>

              <div className="mt-6 space-y-2 text-xs">
                <div className="text-orange-800 font-medium mb-1">Key Events:</div>
                <div className="text-orange-700">
                  • Holiday season boost<br/>
                  • Record-breaking sales<br/>
                  • Market leadership
                </div>
              </div>

              <div className="mt-6 p-2 bg-orange-100 rounded border border-orange-300">
                <div className="text-orange-800 font-medium text-xs">Status</div>
                <div className="text-orange-700 text-xs">Strong Finish</div>
              </div>
            </div>
          </div>
        </div>

      </div>
      
    </LayoutContainer>
  );
}