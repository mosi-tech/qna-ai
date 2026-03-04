'use client';

import LayoutContainer from '@/components/insights/layout/components/LayoutContainer';
import LayoutHeader from '@/components/insights/layout/components/LayoutHeader';

export default function Grid8Variant1() {
  return (
    <LayoutContainer>
      
      <LayoutHeader>
        <h1 className="text-2xl font-bold text-gray-900">Grid/8/1: Performance Timeline</h1>
        <p className="text-gray-600 mt-1">8×1 grid • Eight Period Portfolio Performance Analysis</p>
      </LayoutHeader>

      <div className="flex-1 grid grid-cols-8 grid-rows-1 gap-3 min-h-0">
        
        <div className="col-span-1 row-span-1">
          <div className="h-full bg-white rounded-lg border border-gray-200 p-3">
            <div className="text-center">
              <h3 className="text-sm font-bold text-gray-900 mb-2">Q1 2023</h3>
              <div className="text-xl font-bold text-green-600 mb-1">+7.2%</div>
              <div className="text-xs text-gray-600 mb-2">$2.68M</div>
            </div>
            <div className="text-xs space-y-1">
              <div className="flex justify-between">
                <span className="text-gray-600">Best</span>
                <span className="font-medium">Tech</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Vol</span>
                <span className="font-medium">12.4%</span>
              </div>
            </div>
            <div className="mt-2 text-center">
              <div className="w-4 h-4 bg-green-500 rounded-full mx-auto"></div>
            </div>
          </div>
        </div>

        <div className="col-span-1 row-span-1">
          <div className="h-full bg-white rounded-lg border border-gray-200 p-3">
            <div className="text-center">
              <h3 className="text-sm font-bold text-gray-900 mb-2">Q2 2023</h3>
              <div className="text-xl font-bold text-green-600 mb-1">+4.8%</div>
              <div className="text-xs text-gray-600 mb-2">$2.81M</div>
            </div>
            <div className="text-xs space-y-1">
              <div className="flex justify-between">
                <span className="text-gray-600">Best</span>
                <span className="font-medium">Health</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Vol</span>
                <span className="font-medium">10.8%</span>
              </div>
            </div>
            <div className="mt-2 text-center">
              <div className="w-4 h-4 bg-green-400 rounded-full mx-auto"></div>
            </div>
          </div>
        </div>

        <div className="col-span-1 row-span-1">
          <div className="h-full bg-white rounded-lg border border-gray-200 p-3">
            <div className="text-center">
              <h3 className="text-sm font-bold text-gray-900 mb-2">Q3 2023</h3>
              <div className="text-xl font-bold text-red-600 mb-1">-2.1%</div>
              <div className="text-xs text-gray-600 mb-2">$2.75M</div>
            </div>
            <div className="text-xs space-y-1">
              <div className="flex justify-between">
                <span className="text-gray-600">Worst</span>
                <span className="font-medium">Energy</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Vol</span>
                <span className="font-medium">16.2%</span>
              </div>
            </div>
            <div className="mt-2 text-center">
              <div className="w-4 h-4 bg-red-500 rounded-full mx-auto"></div>
            </div>
          </div>
        </div>

        <div className="col-span-1 row-span-1">
          <div className="h-full bg-white rounded-lg border border-gray-200 p-3">
            <div className="text-center">
              <h3 className="text-sm font-bold text-gray-900 mb-2">Q4 2023</h3>
              <div className="text-xl font-bold text-green-600 mb-1">+9.4%</div>
              <div className="text-xs text-gray-600 mb-2">$3.01M</div>
            </div>
            <div className="text-xs space-y-1">
              <div className="flex justify-between">
                <span className="text-gray-600">Best</span>
                <span className="font-medium">Finance</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Vol</span>
                <span className="font-medium">11.7%</span>
              </div>
            </div>
            <div className="mt-2 text-center">
              <div className="w-4 h-4 bg-green-600 rounded-full mx-auto"></div>
            </div>
          </div>
        </div>

        <div className="col-span-1 row-span-1">
          <div className="h-full bg-white rounded-lg border border-gray-200 p-3">
            <div className="text-center">
              <h3 className="text-sm font-bold text-gray-900 mb-2">Q1 2024</h3>
              <div className="text-xl font-bold text-green-600 mb-1">+6.1%</div>
              <div className="text-xs text-gray-600 mb-2">$3.19M</div>
            </div>
            <div className="text-xs space-y-1">
              <div className="flex justify-between">
                <span className="text-gray-600">Best</span>
                <span className="font-medium">Tech</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Vol</span>
                <span className="font-medium">9.8%</span>
              </div>
            </div>
            <div className="mt-2 text-center">
              <div className="w-4 h-4 bg-green-500 rounded-full mx-auto"></div>
            </div>
          </div>
        </div>

        <div className="col-span-1 row-span-1">
          <div className="h-full bg-white rounded-lg border border-gray-200 p-3">
            <div className="text-center">
              <h3 className="text-sm font-bold text-gray-900 mb-2">Q2 2024</h3>
              <div className="text-xl font-bold text-green-600 mb-1">+3.2%</div>
              <div className="text-xs text-gray-600 mb-2">$3.29M</div>
            </div>
            <div className="text-xs space-y-1">
              <div className="flex justify-between">
                <span className="text-gray-600">Best</span>
                <span className="font-medium">Cons</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Vol</span>
                <span className="font-medium">8.4%</span>
              </div>
            </div>
            <div className="mt-2 text-center">
              <div className="w-4 h-4 bg-green-400 rounded-full mx-auto"></div>
            </div>
          </div>
        </div>

        <div className="col-span-1 row-span-1">
          <div className="h-full bg-white rounded-lg border border-gray-200 p-3">
            <div className="text-center">
              <h3 className="text-sm font-bold text-gray-900 mb-2">Q3 2024</h3>
              <div className="text-xl font-bold text-yellow-600 mb-1">+1.8%</div>
              <div className="text-xs text-gray-600 mb-2">$3.35M</div>
            </div>
            <div className="text-xs space-y-1">
              <div className="flex justify-between">
                <span className="text-gray-600">Best</span>
                <span className="font-medium">Util</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Vol</span>
                <span className="font-medium">7.2%</span>
              </div>
            </div>
            <div className="mt-2 text-center">
              <div className="w-4 h-4 bg-yellow-500 rounded-full mx-auto"></div>
            </div>
          </div>
        </div>

        <div className="col-span-1 row-span-1">
          <div className="h-full bg-white rounded-lg border-2 border-blue-400 p-3">
            <div className="text-center">
              <h3 className="text-sm font-bold text-blue-600 mb-2">Q4 2024</h3>
              <div className="text-xl font-bold text-green-600 mb-1">+4.7%</div>
              <div className="text-xs text-gray-600 mb-2">$3.51M</div>
            </div>
            <div className="text-xs space-y-1">
              <div className="flex justify-between">
                <span className="text-gray-600">Best</span>
                <span className="font-medium">Tech</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Vol</span>
                <span className="font-medium">9.1%</span>
              </div>
            </div>
            <div className="mt-2 text-center">
              <div className="w-4 h-4 bg-blue-500 rounded-full mx-auto border-2 border-white shadow"></div>
            </div>
          </div>
        </div>

      </div>
      
    </LayoutContainer>
  );
}