import { Parameter } from '@/types/modules';

interface ParameterControlProps {
  parameter: Parameter;
  value: string | number | boolean | string[];
  onChange: (value: string | number | boolean | string[]) => void;
}

export default function ParameterControl({ parameter, value, onChange }: ParameterControlProps) {
  const { type, label, options } = parameter;

  switch (type) {
    case 'dropdown':
      return (
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            {label}
          </label>
          <select
            value={value as string}
            onChange={(e) => onChange(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            {options?.map((option) => (
              <option key={option} value={option}>
                {option}
              </option>
            ))}
          </select>
        </div>
      );

    case 'input':
      return (
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            {label}
          </label>
          <input
            type="text"
            value={value as string}
            onChange={(e) => onChange(e.target.value)}
            placeholder={parameter.placeholder}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
      );

    case 'date':
      return (
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            {label}
          </label>
          <input
            type="date"
            value={value as string}
            onChange={(e) => onChange(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
      );

    case 'checkbox':
      const checkedValues = value as string[];
      return (
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            {label}
          </label>
          <div className="space-y-2">
            {options?.map((option) => (
              <label key={option} className="flex items-center">
                <input
                  type="checkbox"
                  checked={checkedValues.includes(option)}
                  onChange={(e) => {
                    if (e.target.checked) {
                      onChange([...checkedValues, option]);
                    } else {
                      onChange(checkedValues.filter(v => v !== option));
                    }
                  }}
                  className="mr-2"
                />
                {option}
              </label>
            ))}
          </div>
        </div>
      );

    default:
      return null;
  }
}