import React from 'react';

// Data interface for Geographic Exposure
interface EtfGeographicExposureProps {
  title?: string;
  data: any;
  loading?: boolean;
  error?: string;
}


// Sample data for development
export const SAMPLE_DATA: EtfGeographicExposureProps = {
  title: 'Geographic Exposure',
  data: {
    "data": [
        {
            "name": "Technology",
            "value": 35
        },
        {
            "name": "Healthcare",
            "value": 20
        },
        {
            "name": "Finance",
            "value": 25
        },
        {
            "name": "Other",
            "value": 20
        }
    ]
},
  loading: false,
  error: undefined,
};

/**
 * Geographic Exposure finBlock
 *
 * @description Country/region breakdown for international ETFs
 * @blockType donut-chart
 * @concepts geographic diversification
 * @mcpRequired get_fundamentals
 */
export const EtfGeographicExposure: React.FC<EtfGeographicExposureProps> = ({
  title = 'Geographic Exposure',
  data,
  loading = false,
  error,
}) => {
  if (loading) {
    return <div className="p-4">Loading...</div>;
  }

  if (error) {
    return <div className="p-4 text-red-500">Error: {error}</div>;
  }

  return (
    <div className="finblock etf-geographic-exposure rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
      <h3 className="mb-3 font-semibold text-gray-800">{title}</h3>
      {/* Block Type: donut-chart */}
      <pre className="max-h-96 overflow-auto rounded bg-gray-50 p-3 text-xs">
        {JSON.stringify(data, null, 2)}
      </pre>
    </div>
  );
};

export default EtfGeographicExposure;
