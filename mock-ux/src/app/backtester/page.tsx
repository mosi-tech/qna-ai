'use client';

import BacktestResults from '@/components/backtester/output/BacktestResults';
import AnalysisWrapper from '@/components/AnalysisWrapper';
import BacktesterInputs from '@/components/backtester/input/BacktesterInputs';

export default function BacktesterPage() {
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="max-w-4xl mx-auto">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                <span className="text-blue-600 text-xl">📈</span>
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Strategy Backtester Analysis</h1>
                <p className="text-gray-600">Visual strategy backtest results</p>
              </div>
            </div>
            
            <a
              href="/"
              className="px-4 py-2 text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50"
            >
              Back to Chat
            </a>
          </div>
        </div>
      </header>

      {/* Analysis Results - Exactly as it appears in chat */}
      <main className="max-w-4xl mx-auto p-6">
        <AnalysisWrapper 
          moduleKey="strategy_builder" 
          title="Visual Strategy Backtest"
          outputComponent={<BacktestResults />}
          inputComponent={<BacktesterInputs />}
          onSaveToDashboard={() => console.log('Save backtester to dashboard')}
        />
      </main>
    </div>
  );
}