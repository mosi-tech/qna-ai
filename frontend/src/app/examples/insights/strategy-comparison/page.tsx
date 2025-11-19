'use client';

import Headline from '@/components/insights/Headline';
import ComparisonCard from '@/components/insights/ComparisonCard';
import OptionComparison from '@/components/insights/OptionComparison';
import ScenarioBlock from '@/components/insights/ScenarioBlock';
import DecisionBlock from '@/components/insights/DecisionBlock';

export default function StrategyComparison() {
  const handleApprove = (component: string) => {
    console.log(`Approved: ${component}`);
  };

  return (
    <div className="h-screen bg-gray-50 p-6 overflow-hidden">
      <div className="max-w-5xl mx-auto h-full flex flex-col gap-8">
        
        {/* Header */}
        <Headline 
          text="MACD vs Bollinger Band Strategy for QQQ"
          onApprove={() => handleApprove('Title')}
        />

        {/* Main Comparison */}
        <div className="flex-1">
          <ComparisonCard 
            value={12.3}
            comparisonValue={9.7}
            label="MACD vs Bollinger Band Annual Returns"
            comparisonLabel="Bollinger Band"
            format="percentage"
            onApprove={() => handleApprove('Performance Comparison')}
          />
        </div>

        {/* Final Decision */}
        <div className="flex-1">
          <DecisionBlock 
            decision="Which strategy should I choose for QQQ?"
            pros={[
              "MACD: Higher returns (12.3% vs 9.7%)",
              "MACD: Better Sharpe ratio (1.18 vs 0.94)"
            ]}
            cons={[
              "Bollinger Band: Better risk control (62.1% win rate)",
              "Bollinger Band: Lower drawdown (-12.3% vs -15.8%)"
            ]}
            recommendation="Choose MACD for aggressive growth, Bollinger Band for stability"
            rationale="MACD delivers higher returns but with more volatility. Bollinger Band offers better risk management. Choose based on your risk tolerance."
            confidence="high"
            onApprove={() => handleApprove('Decision')}
          />
        </div>

      </div>
    </div>
  );
}