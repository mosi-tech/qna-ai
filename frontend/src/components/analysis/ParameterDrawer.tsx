'use client';

import { useEffect } from 'react';
import ParameterSection from './ParameterSection';
import { ParameterDefinition, ParameterSet } from '@/types/parameters';

interface ParameterDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  schema: ParameterDefinition[];
  values: ParameterSet;
  onChange: (parameterId: string, value: any) => void;
  onRerun: () => void;
  hasChanges: boolean;
  isRunning: boolean;
  analysisTitle?: string;
}

export default function ParameterDrawer({
  isOpen,
  onClose,
  schema,
  values,
  onChange,
  onRerun,
  hasChanges,
  isRunning,
  analysisTitle = "Analysis"
}: ParameterDrawerProps) {
  // Handle escape key
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };

    if (isOpen) {
      document.addEventListener('keydown', handleEscape);
      return () => document.removeEventListener('keydown', handleEscape);
    }
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <>
      {/* Backdrop */}
      <div 
        className="fixed inset-0 z-40"
        style={{ backgroundColor: 'rgba(0, 0, 0, 0.25)' }}
        onClick={onClose}
      />
      
      {/* Drawer */}
      <div className="fixed top-0 right-0 h-full w-96 bg-white shadow-xl z-50 flex flex-col">
        {/* Header */}
        <div className="bg-blue-600 px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <span className="text-xl">⚙️</span>
              <h2 className="text-lg font-semibold text-white">
                Parameters
              </h2>
            </div>
            <button
              onClick={onClose}
              className="text-blue-200 hover:text-white"
            >
              <span className="text-xl">✕</span>
            </button>
          </div>
          <p className="mt-1 text-sm text-blue-100">
            Configure parameters for "{analysisTitle}"
          </p>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto">
          {/* Status */}
          {hasChanges && (
            <div className="mx-6 mt-4 mb-4 rounded-md bg-amber-50 p-3 border border-amber-200">
              <div className="flex items-center gap-2">
                <span className="text-amber-600">⚠️</span>
                <span className="text-sm font-medium text-amber-800">
                  Parameters Modified
                </span>
              </div>
              <p className="mt-1 text-sm text-amber-700">
                Changes have been made. Run analysis to apply them.
              </p>
            </div>
          )}

          {/* Parameter Form */}
          <ParameterSection
            schema={schema}
            values={values}
            onChange={onChange}
            hasChanges={hasChanges}
            isRunning={isRunning}
          />
        </div>

        {/* Fixed Footer */}
        <div className="border-t border-gray-200 p-6 bg-white">
          <button
            onClick={() => {
              onRerun();
              onClose();
            }}
            disabled={!hasChanges || isRunning}
            className={`w-full px-4 py-3 rounded-lg font-medium transition-colors ${
              hasChanges && !isRunning
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
              '🚀 Re-run Analysis'
            )}
          </button>
          
          {hasChanges && !isRunning && (
            <p className="mt-2 text-sm text-blue-600 text-center">
              Parameters have been modified. Click to run analysis with new settings.
            </p>
          )}
        </div>
      </div>
    </>
  );
}