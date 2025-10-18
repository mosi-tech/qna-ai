'use client';

import { useState } from 'react';
import { modules } from '@/config/modules';
import { ParameterValues, Parameter } from '@/types/modules';
import ParameterControl from '@/components/ParameterControl';
import SymbolSelector from '@/components/backtester/input/SymbolSelector';
import StrategyBuilder from '@/components/backtester/input/StrategyBuilder';
import SettingsPanel from '@/components/backtester/input/SettingsPanel';
import ConversationalForm from '@/components/ConversationalForm';

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
  const [useConversationalForm, setUseConversationalForm] = useState(false);

  if (!selectedModule) return null;

  const moduleData = modules[selectedModule];
  if (!moduleData) return null;

  const handleParameterChange = (paramKey: string, value: string | number | boolean | string[]) => {
    const newValues = { ...parameterValues };
    newValues[paramKey] = value;
    setParameterValues(newValues);
  };

  const handleConversationalFormComplete = (data: any) => {
    console.log('Conversational form completed:', data);
    // Convert conversational data to parameter values
    const newParameterValues: ParameterValues = {};
    
    // Map the conversational data to module parameters
    if (moduleData.params) {
      moduleData.params.forEach((param, index) => {
        const paramKey = `param_${index}`;
        // Map based on parameter label/type
        if (param.label.toLowerCase().includes('frequency') && data.timeframe) {
          newParameterValues[paramKey] = data.timeframe;
        } else if (param.label.toLowerCase().includes('investment') && data.investment) {
          newParameterValues[paramKey] = `$${data.investment.toLocaleString()}`;
        } else if (param.label.toLowerCase().includes('risk') && data.riskTolerance) {
          newParameterValues[paramKey] = data.riskTolerance;
        } else {
          newParameterValues[paramKey] = param.defaultValue || '';
        }
      });
    }
    
    setParameterValues(newParameterValues);
    setUseConversationalForm(false);
    onSubmit(); // Auto-submit after conversational form
  };

  const handleConversationalFormCancel = () => {
    setUseConversationalForm(false);
  };

  // Show conversational form
  if (useConversationalForm) {
    return (
      <ConversationalForm
        onComplete={handleConversationalFormComplete}
        onCancel={handleConversationalFormCancel}
      />
    );
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-4xl max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex justify-between items-center p-6 border-b border-gray-200">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center">
              <span className="text-blue-600 text-lg">⚙️</span>
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-900">
                Customize Analysis
              </h3>
              <p className="text-sm text-gray-600">{moduleData.title}</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 p-2"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Content */}
        <div className="p-6">
          {selectedModule === 'strategy_builder' ? (
            <BacktesterForm />
          ) : (
            <div className="space-y-4">
              {/* AI Assistant Option */}
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <div className="flex items-start gap-3">
                  <div className="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center flex-shrink-0">
                    <span className="text-blue-600 text-lg">🤖</span>
                  </div>
                  <div className="flex-1">
                    <h4 className="font-medium text-blue-900 mb-1">AI-Powered Setup</h4>
                    <p className="text-sm text-blue-700 mb-3">
                      Let our AI guide you through customizing this analysis with intelligent suggestions and explanations.
                    </p>
                    <button
                      onClick={() => setUseConversationalForm(true)}
                      className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium"
                    >
                      🚀 Start AI Setup
                    </button>
                  </div>
                </div>
              </div>

              {/* Traditional Form */}
              <div className="border-t border-gray-200 pt-4">
                <h4 className="font-medium text-gray-900 mb-4">Manual Configuration</h4>
                <StandardParameterForm 
                  moduleData={moduleData}
                  parameterValues={parameterValues}
                  onParameterChange={handleParameterChange}
                />
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="flex justify-end gap-3 p-6 border-t border-gray-200">
          <button
            onClick={onClose}
            className="px-4 py-2 text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50"
          >
            Cancel
          </button>
          <button
            onClick={onSubmit}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Run Analysis
          </button>
        </div>
      </div>
    </div>
  );
}

function StandardParameterForm({ 
  moduleData, 
  parameterValues, 
  onParameterChange 
}: {
  moduleData: {
    params?: Parameter[];
  };
  parameterValues: ParameterValues;
  onParameterChange: (key: string, value: string | number | boolean | string[]) => void;
}) {
  return (
    <div className="space-y-6">
      <div>
        <h4 className="font-medium text-gray-900 mb-4">Analysis Parameters</h4>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {moduleData.params?.map((param, index) => (
            <ParameterControl
              key={index}
              parameter={param}
              value={parameterValues[`param_${index}`] || param.defaultValue || ''}
              onChange={(value) => onParameterChange(`param_${index}`, value)}
            />
          ))}
        </div>
      </div>
    </div>
  );
}

function BacktesterForm() {
  // Backtester state
  const [selectedSymbols, setSelectedSymbols] = useState<string[]>(['AAPL']);
  const [entryConditions, setEntryConditions] = useState([
    {
      id: Math.random().toString(36).substr(2, 9),
      indicatorA: 'SMA(10)',
      operator: 'crosses_above',
      indicatorB: 'SMA(20)'
    }
  ]);
  const [exitConditions, setExitConditions] = useState([
    {
      id: Math.random().toString(36).substr(2, 9),
      indicatorA: 'SMA(10)',
      operator: 'crosses_below',
      indicatorB: 'SMA(20)'
    }
  ]);

  // Settings state
  const [initialInvestment, setInitialInvestment] = useState(100000);
  const [startDate, setStartDate] = useState('2023-01-01');
  const [endDate, setEndDate] = useState('2024-01-01');
  const [stopLoss, setStopLoss] = useState(5.0);
  const [takeProfit, setTakeProfit] = useState(10.0);
  const [slippage, setSlippage] = useState(0.05);
  const [transactionCost, setTransactionCost] = useState(1.0);

  return (
    <div className="space-y-6 max-h-[60vh] overflow-y-auto">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column - Symbol Selector */}
        <div className="lg:col-span-1">
          <SymbolSelector
            selectedSymbols={selectedSymbols}
            onSymbolsChange={setSelectedSymbols}
          />
        </div>

        {/* Middle Column - Strategy Builder */}
        <div className="lg:col-span-1">
          <StrategyBuilder
            entryConditions={entryConditions}
            exitConditions={exitConditions}
            onEntryConditionsChange={setEntryConditions}
            onExitConditionsChange={setExitConditions}
          />
        </div>

        {/* Right Column - Settings */}
        <div className="lg:col-span-1">
          <SettingsPanel
            initialInvestment={initialInvestment}
            startDate={startDate}
            endDate={endDate}
            stopLoss={stopLoss}
            takeProfit={takeProfit}
            slippage={slippage}
            transactionCost={transactionCost}
            onInitialInvestmentChange={setInitialInvestment}
            onStartDateChange={setStartDate}
            onEndDateChange={setEndDate}
            onStopLossChange={setStopLoss}
            onTakeProfitChange={setTakeProfit}
            onSlippageChange={setSlippage}
            onTransactionCostChange={setTransactionCost}
          />
        </div>
      </div>

      {/* Strategy Summary */}
      <div className="mt-6 p-4 bg-gray-50 rounded-lg">
        <h5 className="text-sm font-medium text-gray-900 mb-2">Strategy Summary</h5>
        <div className="text-sm text-gray-600 grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <strong>Symbols:</strong> {selectedSymbols.join(', ')}
          </div>
          <div>
            <strong>Entry Conditions:</strong> {entryConditions.length}
          </div>
          <div>
            <strong>Exit Conditions:</strong> {exitConditions.length}
          </div>
        </div>
      </div>
    </div>
  );
}