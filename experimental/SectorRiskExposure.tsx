import React from 'react';

interface Position {
  symbol: string;
  qty: number;
  market_value: number;
  sector?: string;
  percentage?: number;
}

interface SectorData {
  sector: string;
  value: number;
  percentage: number;
  positions: Position[];
  riskLevel: 'Low' | 'Medium' | 'High';
}

const SectorRiskExposure: React.FC = () => {
  // Mock data representing portfolio positions grouped by sector
  const sectorData: SectorData[] = [
    {
      sector: 'Technology',
      value: 45000,
      percentage: 45,
      positions: [
        { symbol: 'AAPL', qty: 100, market_value: 20000, percentage: 20 },
        { symbol: 'MSFT', qty: 80, market_value: 15000, percentage: 15 },
        { symbol: 'GOOGL', qty: 50, market_value: 10000, percentage: 10 }
      ],
      riskLevel: 'High'
    },
    {
      sector: 'Healthcare',
      value: 25000,
      percentage: 25,
      positions: [
        { symbol: 'JNJ', qty: 200, market_value: 15000, percentage: 15 },
        { symbol: 'PFE', qty: 300, market_value: 10000, percentage: 10 }
      ],
      riskLevel: 'Medium'
    },
    {
      sector: 'Financial',
      value: 20000,
      percentage: 20,
      positions: [
        { symbol: 'JPM', qty: 150, market_value: 12000, percentage: 12 },
        { symbol: 'BAC', qty: 200, market_value: 8000, percentage: 8 }
      ],
      riskLevel: 'Medium'
    },
    {
      sector: 'Consumer Goods',
      value: 10000,
      percentage: 10,
      positions: [
        { symbol: 'PG', qty: 80, market_value: 10000, percentage: 10 }
      ],
      riskLevel: 'Low'
    }
  ];

  const totalValue = sectorData.reduce((sum, sector) => sum + sector.value, 0);

  const getRiskColor = (riskLevel: string) => {
    switch (riskLevel) {
      case 'High': return '#ef4444';
      case 'Medium': return '#f59e0b';
      case 'Low': return '#10b981';
      default: return '#6b7280';
    }
  };

  const getSectorColor = (index: number) => {
    const colors = ['#3b82f6', '#10b981', '#f59e0b', '#8b5cf6', '#ef4444'];
    return colors[index % colors.length];
  };

  return (
    <div className="p-6 bg-white rounded-lg shadow-lg max-w-4xl">
      <h2 className="text-2xl font-bold text-gray-800 mb-6">Portfolio Sector Risk Exposure</h2>
      
      {/* Summary Cards */}
      <div className="grid grid-cols-3 gap-4 mb-6">
        <div className="bg-blue-50 p-4 rounded-lg">
          <h3 className="text-sm font-medium text-blue-600">Total Portfolio Value</h3>
          <p className="text-2xl font-bold text-blue-900">${totalValue.toLocaleString()}</p>
        </div>
        <div className="bg-yellow-50 p-4 rounded-lg">
          <h3 className="text-sm font-medium text-yellow-600">Sectors Invested</h3>
          <p className="text-2xl font-bold text-yellow-900">{sectorData.length}</p>
        </div>
        <div className="bg-red-50 p-4 rounded-lg">
          <h3 className="text-sm font-medium text-red-600">High Risk Exposure</h3>
          <p className="text-2xl font-bold text-red-900">{sectorData.filter(s => s.riskLevel === 'High').length}</p>
        </div>
      </div>

      {/* Sector Breakdown */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* Pie Chart Visualization */}
        <div className="bg-gray-50 p-4 rounded-lg">
          <h3 className="text-lg font-semibold mb-4">Sector Allocation</h3>
          <div className="relative w-64 h-64 mx-auto">
            <svg viewBox="0 0 100 100" className="w-full h-full">
              {sectorData.map((sector, index) => {
                const startAngle = sectorData.slice(0, index).reduce((sum, s) => sum + (s.percentage * 3.6), 0);
                const endAngle = startAngle + (sector.percentage * 3.6);
                const largeArcFlag = sector.percentage > 50 ? 1 : 0;
                
                const x1 = 50 + 40 * Math.cos(startAngle * Math.PI / 180);
                const y1 = 50 + 40 * Math.sin(startAngle * Math.PI / 180);
                const x2 = 50 + 40 * Math.cos(endAngle * Math.PI / 180);
                const y2 = 50 + 40 * Math.sin(endAngle * Math.PI / 180);
                
                return (
                  <path
                    key={sector.sector}
                    d={`M 50 50 L ${x1} ${y1} A 40 40 0 ${largeArcFlag} 1 ${x2} ${y2} Z`}
                    fill={getSectorColor(index)}
                    opacity="0.8"
                  />
                );
              })}
            </svg>
          </div>
          
          {/* Legend */}
          <div className="mt-4 space-y-2">
            {sectorData.map((sector, index) => (
              <div key={sector.sector} className="flex items-center justify-between">
                <div className="flex items-center">
                  <div 
                    className="w-4 h-4 rounded mr-2" 
                    style={{ backgroundColor: getSectorColor(index) }}
                  ></div>
                  <span className="text-sm font-medium">{sector.sector}</span>
                </div>
                <span className="text-sm text-gray-600">{sector.percentage}%</span>
              </div>
            ))}
          </div>
        </div>

        {/* Risk Analysis */}
        <div>
          <h3 className="text-lg font-semibold mb-4">Risk Analysis by Sector</h3>
          <div className="space-y-4">
            {sectorData.map((sector) => (
              <div key={sector.sector} className="border border-gray-200 rounded-lg p-4">
                <div className="flex justify-between items-center mb-2">
                  <h4 className="font-medium text-gray-800">{sector.sector}</h4>
                  <div className="flex items-center">
                    <span 
                      className="px-2 py-1 rounded-full text-xs font-medium text-white mr-2"
                      style={{ backgroundColor: getRiskColor(sector.riskLevel) }}
                    >
                      {sector.riskLevel} Risk
                    </span>
                    <span className="text-sm font-bold">${sector.value.toLocaleString()}</span>
                  </div>
                </div>
                
                {/* Progress bar */}
                <div className="w-full bg-gray-200 rounded-full h-2 mb-3">
                  <div 
                    className="bg-blue-500 h-2 rounded-full" 
                    style={{ width: `${sector.percentage}%` }}
                  ></div>
                </div>
                
                {/* Positions */}
                <div className="space-y-1">
                  {sector.positions.map((position) => (
                    <div key={position.symbol} className="flex justify-between text-sm">
                      <span className="text-gray-600">{position.symbol}</span>
                      <span>${position.market_value.toLocaleString()} ({position.percentage}%)</span>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Risk Recommendations */}
      <div className="mt-6 bg-amber-50 border border-amber-200 rounded-lg p-4">
        <h3 className="text-lg font-semibold text-amber-800 mb-2">Risk Assessment & Recommendations</h3>
        <ul className="space-y-1 text-sm text-amber-700">
          <li>• Technology sector represents 45% of portfolio - consider reducing concentration</li>
          <li>• Good diversification across 4 sectors, but add exposure to Energy or Utilities</li>
          <li>• Consumer Goods at 10% provides good defensive allocation</li>
          <li>• Consider rebalancing when any single sector exceeds 40% of total portfolio</li>
        </ul>
      </div>
    </div>
  );
};

export default SectorRiskExposure;