'use client';

import { PredictedCategory } from './types';

interface AnalysisSelectorProps {
  categories: PredictedCategory[];
  onSelect: (category: PredictedCategory) => void;
}

export default function AnalysisSelector({ categories, onSelect }: AnalysisSelectorProps) {
  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold text-gray-900">
        Suggested analyses:
      </h3>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {categories.map((category) => (
          <div
            key={category.id}
            className="bg-white rounded-lg border border-gray-200 p-4 hover:border-blue-300 transition-all cursor-pointer"
            onClick={() => onSelect(category)}
          >
            {/* Category Header */}
            <div className="flex items-start gap-3 mb-4">
              <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                <span className="text-lg">{category.emoji}</span>
              </div>
              <div className="flex-1">
                <h4 className="font-semibold text-gray-900 text-sm">
                  {category.title}
                </h4>
                <p className="text-xs text-gray-600 mt-1">
                  {category.description}
                </p>
              </div>
              
              {/* Select Analysis Button */}
              <div className="p-1 text-gray-400 hover:text-blue-500 transition-colors">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </div>
            </div>

            {/* Quick Preview */}
            <div className="space-y-2 mb-4">
              <p className="text-xs text-gray-500">
                Configurable settings: {category.fields.length} parameters
              </p>
              <div className="flex flex-wrap gap-1">
                {category.fields.slice(0, 2).map((field, idx) => (
                  <span key={idx} className="px-2 py-0.5 bg-gray-100 text-gray-600 rounded-full text-xs">
                    {field.label}
                  </span>
                ))}
              </div>
            </div>

            {/* Select Button */}
            <div className="w-full px-3 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors text-xs font-medium text-center">
              📋 Customize This Analysis
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}