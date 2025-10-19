'use client';

import { modules } from '@/config/modules';
import { ParameterValues } from '@/types/modules';

interface CustomizationFormProps {
  selectedModule: string | null;
  parameterValues: ParameterValues;
  setParameterValues: (values: ParameterValues) => void;
  onClose: () => void;
  onSubmit: () => void;
}

export default function CustomizationForm({
  selectedModule,
  parameterValues,
  setParameterValues,
  onClose,
  onSubmit
}: CustomizationFormProps) {
  if (!selectedModule) return null;

  const moduleData = modules[selectedModule];
  if (!moduleData) return null;

  const handleParameterChange = (paramKey: string, value: string | number | boolean) => {
    setParameterValues({
      ...parameterValues,
      [paramKey]: value
    });
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit();
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-2xl">
        <div className="flex justify-between items-center p-6 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">
            Customize {moduleData.title}
          </h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {moduleData.params && moduleData.params.length > 0 ? (
            <>
              {moduleData.params.map((param, idx) => {
                const paramKey = `param_${idx}`;
                const value = parameterValues[paramKey] || '';

                return (
                  <div key={paramKey} className="space-y-2">
                    <label className="block text-sm font-medium text-gray-700">
                      {param.label}
                    </label>
                    {param.type === 'select' ? (
                      <select
                        value={value}
                        onChange={(e) => handleParameterChange(paramKey, e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                      >
                        <option value="">Select {param.label}</option>
                        {param.options?.map((opt) => (
                          <option key={opt} value={opt}>
                            {opt}
                          </option>
                        ))}
                      </select>
                    ) : (
                      <input
                        type={param.type === 'number' ? 'number' : 'text'}
                        value={value}
                        onChange={(e) => handleParameterChange(paramKey, e.target.value)}
                        placeholder={param.label}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                    )}
                  </div>
                );
              })}
            </>
          ) : (
            <p className="text-gray-600">No parameters available for customization</p>
          )}

          <div className="flex gap-2 justify-end pt-4 border-t border-gray-200">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              Apply
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
