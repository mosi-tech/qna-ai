'use client';

import Headline from '@/components/insights/Headline';
import RankedList from '@/components/insights/RankedList';
import StatGroup from '@/components/insights/StatGroup';
import ComparisonTable from '@/components/insights/ComparisonTable';
import Grid from '@/components/insights/Grid';

export default function DefensiveLeadershipAnalysis() {
  const holdingsPerformance = [
    { symbol: 'PG', name: 'Procter & Gamble', avg_return: 1.5, outperform_rate: 100, correlation: 0.68 },
    { symbol: 'JNJ', name: 'Johnson & Johnson', avg_return: 1.8, outperform_rate: 80, correlation: 0.72 },
    { symbol: 'KO', name: 'Coca-Cola', avg_return: 1.3, outperform_rate: 80, correlation: 0.65 },
    { symbol: 'WMT', name: 'Walmart', avg_return: 1.1, outperform_rate: 60, correlation: 0.58 },
    { symbol: 'VZ', name: 'Verizon', avg_return: 0.9, outperform_rate: 60, correlation: 0.71 },
    { symbol: 'T', name: 'AT&T', avg_return: 0.7, outperform_rate: 40, correlation: 0.69 }
  ];

  const performanceData = {
    'PG': { avg_return: 1.5, outperform_rate: 100, correlation: 0.68 },
    'JNJ': { avg_return: 1.8, outperform_rate: 80, correlation: 0.72 },
    'KO': { avg_return: 1.3, outperform_rate: 80, correlation: 0.65 },
    'WMT': { avg_return: 1.1, outperform_rate: 60, correlation: 0.58 },
    'VZ': { avg_return: 0.9, outperform_rate: 60, correlation: 0.71 },
    'T': { avg_return: 0.7, outperform_rate: 40, correlation: 0.69 }
  };

  return (
    <div className="h-screen bg-gray-50 p-6 overflow-hidden">
      <div className="max-w-6xl mx-auto h-full flex flex-col gap-6">
        
        <Headline text="Holdings Performance During Defensive Leadership Days" />
        
        <StatGroup 
          stats={[
            { value: 5, label: "Defensive Days Analyzed", format: "number" },
            { value: 70, label: "Avg Outperformance Rate", format: "percentage" },
            { value: 1.2, label: "Avg Return on Defense Days", format: "percentage" }
          ]}
          columns={3}
        />

        <div className="flex-1 grid grid-cols-2 gap-6 min-h-0">
          
          <RankedList 
            title="Top Outperformers"
            items={holdingsPerformance
              .sort((a, b) => b.outperform_rate - a.outperform_rate)
              .map(stock => ({
                id: stock.symbol,
                name: stock.symbol,
                subtitle: stock.name,
                value: `${stock.outperform_rate}%`,
                changeType: stock.avg_return > 1.0 ? 'positive' as const : 'neutral' as const,
                change: `+${stock.avg_return}%`
              }))
            }
          />

          <ComparisonTable 
            title="Performance Details"
            entities={holdingsPerformance.map(stock => ({
              id: stock.symbol,
              name: stock.symbol,
              subtitle: stock.name
            }))}
            metrics={[
              { id: 'outperform_rate', name: 'Success Rate', format: 'percentage' },
              { id: 'avg_return', name: 'Avg Return', format: 'percentage' },
              { id: 'correlation', name: 'Defensive Corr', format: 'number' }
            ]}
            data={performanceData}
          />

        </div>

      </div>
    </div>
  );
}