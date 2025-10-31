'use client';

import { ParameterDefinition, ParameterSet } from '@/types/parameters';
import { useState } from 'react';

interface ParameterSectionProps {
  schema: ParameterDefinition[];
  values: ParameterSet;
  onChange: (parameterId: string, value: any) => void;
  onRerun: () => void;
  hasChanges: boolean;
  isRunning: boolean;
}

export default function ParameterSection({
  schema,
  values,
  onChange,
  onRerun,
  hasChanges,
  isRunning
}: ParameterSectionProps) {
  const [validationErrors, setValidationErrors] = useState<Record<string, string>>({});

  const validateParameter = (param: ParameterDefinition, value: any): string | null => {
    if (param.required && (value === undefined || value === null || value === '')) {
      return `${param.name} is required`;
    }

    if (param.validation) {
      const validation = param.validation;

      if (param.type === 'number' && typeof value === 'number') {
        if (validation.min !== undefined && value < validation.min) {
          return validation.errorMessage || `Must be at least ${validation.min}`;
        }
        if (validation.max !== undefined && value > validation.max) {
          return validation.errorMessage || `Must be at most ${validation.max}`;
        }
      }

      if (param.type === 'text' && typeof value === 'string' && validation.pattern) {
        const regex = new RegExp(validation.pattern);
        if (!regex.test(value)) {
          return validation.errorMessage || 'Invalid format';
        }
      }
    }

    return null;
  };

  const handleInputChange = (param: ParameterDefinition, newValue: any) => {
    const error = validateParameter(param, newValue);
    
    setValidationErrors(prev => ({
      ...prev,
      [param.id]: error || ''
    }));

    onChange(param.id, newValue);
  };

  const renderInput = (param: ParameterDefinition) => {
    const value = values[param.id];
    const error = validationErrors[param.id];

    switch (param.type) {
      case 'text':
        return (
          <input
            type="text"
            value={value || ''}
            onChange={(e) => handleInputChange(param, e.target.value)}
            className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
              error ? 'border-red-300' : 'border-gray-300'
            }`}
            placeholder={param.description}
          />
        );

      case 'number':
        return (
          <input
            type="number"
            value={value || ''}
            onChange={(e) => handleInputChange(param, parseInt(e.target.value) || 0)}
            min={param.validation?.min}
            max={param.validation?.max}
            className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
              error ? 'border-red-300' : 'border-gray-300'
            }`}
            placeholder={param.description}
          />
        );

      case 'select':
        return (
          <select
            value={value || ''}
            onChange={(e) => handleInputChange(param, e.target.value)}
            className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
              error ? 'border-red-300' : 'border-gray-300'
            }`}
          >
            {param.validation?.options?.map(option => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        );

      case 'boolean':
        return (
          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              checked={value || false}
              onChange={(e) => handleInputChange(param, e.target.checked)}
              className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            />
            <span className="text-sm text-gray-700">Yes</span>
          </label>
        );

      default:
        return null;
    }
  };

  const isValid = schema.every(param => !validationErrors[param.id]);

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6">
      <div className="flex items-center gap-2 mb-4">
        <h2 className="text-lg font-semibold text-gray-900">Parameters</h2>
        {hasChanges && (
          <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full">
            Modified
          </span>
        )}
      </div>

      <div className="space-y-4">
        {schema.map(param => (
          <div key={param.id}>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              {param.name}
              {param.required && <span className="text-red-500 ml-1">*</span>}
            </label>
            
            {renderInput(param)}
            
            {validationErrors[param.id] && (
              <p className="mt-1 text-sm text-red-600">
                {validationErrors[param.id]}
              </p>
            )}
            
            {param.description && !validationErrors[param.id] && (
              <p className="mt-1 text-sm text-gray-500">
                {param.description}
              </p>
            )}
          </div>
        ))}
      </div>

      <div className="mt-6 pt-4 border-t border-gray-200">
        <button
          onClick={onRerun}
          disabled={!hasChanges || !isValid || isRunning}
          className={`w-full px-4 py-2 rounded-lg font-medium transition-colors ${
            hasChanges && isValid && !isRunning
              ? 'bg-blue-600 text-white hover:bg-blue-700'
              : 'bg-gray-100 text-gray-400 cursor-not-allowed'
          }`}
        >
          {isRunning ? (
            <div className="flex items-center justify-center gap-2">
              <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
              Running Analysis...
            </div>
          ) : (
            '🔄 Re-run Analysis'
          )}
        </button>
        
        {hasChanges && isValid && !isRunning && (
          <p className="mt-2 text-sm text-blue-600 text-center">
            Parameters have been modified. Click to run analysis with new settings.
          </p>
        )}
      </div>
    </div>
  );
}