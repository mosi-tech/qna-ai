'use client';

import { useState } from 'react';
import { validateComponent, ValidationResult } from '../utils/componentValidator';

interface ValidationDisplayProps {
  componentType: string;
  spaceType: string;
  props: any;
  componentName: string;
}

export default function ValidationDisplay({ 
  componentType, 
  spaceType, 
  props, 
  componentName 
}: ValidationDisplayProps) {
  const [showValidation, setShowValidation] = useState(false);
  const validation = validateComponent(componentType, spaceType, props);

  if (validation.isValid && validation.warnings.length === 0) {
    return null; // Don't show anything if there are no issues
  }

  return (
    <div className="absolute top-0 right-0 z-10">
      <button
        onClick={() => setShowValidation(!showValidation)}
        className={`px-2 py-1 text-xs rounded-bl-lg font-medium ${
          !validation.isValid 
            ? 'bg-red-100 text-red-800 hover:bg-red-200' 
            : 'bg-yellow-100 text-yellow-800 hover:bg-yellow-200'
        }`}
      >
        {!validation.isValid ? '❌' : '⚠️'}
      </button>
      
      {showValidation && (
        <div className="absolute top-8 right-0 w-64 bg-white border border-gray-300 rounded-lg shadow-lg p-3 text-xs z-20">
          <div className="font-medium text-gray-900 mb-2">
            {componentName} Validation
          </div>
          
          {validation.errors.length > 0 && (
            <div className="mb-2">
              <div className="font-medium text-red-800 mb-1">Errors:</div>
              {validation.errors.map((error, index) => (
                <div key={index} className="text-red-700 mb-1">
                  • {error}
                </div>
              ))}
            </div>
          )}
          
          {validation.warnings.length > 0 && (
            <div className="mb-2">
              <div className="font-medium text-yellow-800 mb-1">Warnings:</div>
              {validation.warnings.map((warning, index) => (
                <div key={index} className="text-yellow-700 mb-1">
                  • {warning}
                </div>
              ))}
            </div>
          )}
          
          {validation.suggestedFixes && (
            <div>
              <div className="font-medium text-blue-800 mb-1">Suggested Fixes:</div>
              <div className="text-blue-700">
                {validation.suggestedFixes.variant && `Use variant: ${validation.suggestedFixes.variant}`}
                {validation.suggestedFixes.maxItems && `, Limit items: ${validation.suggestedFixes.maxItems}`}
                {validation.suggestedFixes.truncateContent && `, Truncate content`}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}