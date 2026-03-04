'use client';

import { useState } from 'react';
import IndicatorBlock from './IndicatorBlock';

interface Condition {
  id: string;
  indicatorA: string;
  operator: string;
  indicatorB: string;
}

interface StrategyBuilderProps {
  entryConditions: Condition[];
  exitConditions: Condition[];
  onEntryConditionsChange: (conditions: Condition[]) => void;
  onExitConditionsChange: (conditions: Condition[]) => void;
}

export default function StrategyBuilder({
  entryConditions,
  exitConditions,
  onEntryConditionsChange,
  onExitConditionsChange
}: StrategyBuilderProps) {
  const [activeTab, setActiveTab] = useState<'entry' | 'exit'>('entry');

  const generateId = () => Math.random().toString(36).substr(2, 9);

  const addEntryCondition = () => {
    const newCondition: Condition = {
      id: generateId(),
      indicatorA: '',
      operator: '',
      indicatorB: ''
    };
    onEntryConditionsChange([...entryConditions, newCondition]);
  };

  const addExitCondition = () => {
    const newCondition: Condition = {
      id: generateId(),
      indicatorA: '',
      operator: '',
      indicatorB: ''
    };
    onExitConditionsChange([...exitConditions, newCondition]);
  };

  const updateEntryCondition = (id: string, field: keyof Condition, value: string) => {
    onEntryConditionsChange(
      entryConditions.map(condition =>
        condition.id === id ? { ...condition, [field]: value } : condition
      )
    );
  };

  const updateExitCondition = (id: string, field: keyof Condition, value: string) => {
    onExitConditionsChange(
      exitConditions.map(condition =>
        condition.id === id ? { ...condition, [field]: value } : condition
      )
    );
  };

  const removeEntryCondition = (id: string) => {
    onEntryConditionsChange(entryConditions.filter(condition => condition.id !== id));
  };

  const removeExitCondition = (id: string) => {
    onExitConditionsChange(exitConditions.filter(condition => condition.id !== id));
  };

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Strategy Builder</h3>

      {/* Tab Navigation */}
      <div className="flex border-b border-gray-200 mb-6">
        <button
          onClick={() => setActiveTab('entry')}
          className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
            activeTab === 'entry'
              ? 'border-blue-500 text-blue-600'
              : 'border-transparent text-gray-500 hover:text-gray-700'
          }`}
        >
          Entry Conditions
          {entryConditions.length > 0 && (
            <span className="ml-2 px-2 py-0.5 bg-blue-100 text-blue-800 rounded-full text-xs">
              {entryConditions.length}
            </span>
          )}
        </button>
        <button
          onClick={() => setActiveTab('exit')}
          className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
            activeTab === 'exit'
              ? 'border-blue-500 text-blue-600'
              : 'border-transparent text-gray-500 hover:text-gray-700'
          }`}
        >
          Exit Conditions
          {exitConditions.length > 0 && (
            <span className="ml-2 px-2 py-0.5 bg-blue-100 text-blue-800 rounded-full text-xs">
              {exitConditions.length}
            </span>
          )}
        </button>
      </div>

      {/* Entry Conditions Tab */}
      {activeTab === 'entry' && (
        <div>
          <div className="flex justify-between items-center mb-4">
            <h4 className="font-medium text-gray-900">Entry Conditions</h4>
            <button
              onClick={addEntryCondition}
              className="px-3 py-1 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors text-sm"
            >
              + Add Condition
            </button>
          </div>

          {entryConditions.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <p>No entry conditions defined</p>
              <p className="text-sm mt-1">Add a condition to define when to buy</p>
            </div>
          ) : (
            <div className="space-y-3">
              {entryConditions.map((condition, index) => (
                <div key={condition.id}>
                  {index > 0 && (
                    <div className="text-center py-2">
                      <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-xs font-medium">
                        AND
                      </span>
                    </div>
                  )}
                  <IndicatorBlock
                    id={condition.id}
                    indicatorA={condition.indicatorA}
                    operator={condition.operator}
                    indicatorB={condition.indicatorB}
                    onIndicatorAChange={(value) => updateEntryCondition(condition.id, 'indicatorA', value)}
                    onOperatorChange={(value) => updateEntryCondition(condition.id, 'operator', value)}
                    onIndicatorBChange={(value) => updateEntryCondition(condition.id, 'indicatorB', value)}
                    onRemove={() => removeEntryCondition(condition.id)}
                    canRemove={entryConditions.length > 1}
                  />
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Exit Conditions Tab */}
      {activeTab === 'exit' && (
        <div>
          <div className="flex justify-between items-center mb-4">
            <h4 className="font-medium text-gray-900">Exit Conditions</h4>
            <button
              onClick={addExitCondition}
              className="px-3 py-1 bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors text-sm"
            >
              + Add Condition
            </button>
          </div>

          {exitConditions.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <p>No exit conditions defined</p>
              <p className="text-sm mt-1">Add a condition to define when to sell</p>
            </div>
          ) : (
            <div className="space-y-3">
              {exitConditions.map((condition, index) => (
                <div key={condition.id}>
                  {index > 0 && (
                    <div className="text-center py-2">
                      <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-xs font-medium">
                        AND
                      </span>
                    </div>
                  )}
                  <IndicatorBlock
                    id={condition.id}
                    indicatorA={condition.indicatorA}
                    operator={condition.operator}
                    indicatorB={condition.indicatorB}
                    onIndicatorAChange={(value) => updateExitCondition(condition.id, 'indicatorA', value)}
                    onOperatorChange={(value) => updateExitCondition(condition.id, 'operator', value)}
                    onIndicatorBChange={(value) => updateExitCondition(condition.id, 'indicatorB', value)}
                    onRemove={() => removeExitCondition(condition.id)}
                    canRemove={exitConditions.length > 1}
                  />
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Strategy Summary */}
      <div className="mt-6 p-4 bg-gray-50 rounded-lg">
        <h5 className="text-sm font-medium text-gray-900 mb-2">Strategy Summary</h5>
        <div className="text-sm text-gray-600">
          <p>Entry: {entryConditions.length} condition{entryConditions.length !== 1 ? 's' : ''}</p>
          <p>Exit: {exitConditions.length} condition{exitConditions.length !== 1 ? 's' : ''}</p>
        </div>
      </div>
    </div>
  );
}