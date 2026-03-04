'use client';

import { useState } from 'react';
import ConversationalForm from './ConversationalForm';

interface AnalysisWrapperProps {
  outputComponent: React.ReactNode;
  inputComponent: React.ReactNode;
  moduleKey?: string;
  title?: string;
  startInInputMode?: boolean;
  onSaveToDashboard?: () => void;
  onExportData?: () => void;
  onShareAnalysis?: () => void;
}

export default function AnalysisWrapper({
  outputComponent,
  inputComponent,
  moduleKey,
  title,
  startInInputMode = false,
  onSaveToDashboard,
  onExportData,
  onShareAnalysis
}: AnalysisWrapperProps) {
  const [showActions, setShowActions] = useState(false);
  const [showInput, setShowInput] = useState(startInInputMode);
  const [showConversationalForm, setShowConversationalForm] = useState(false);

  const handleToggleView = () => {
    setShowInput(!showInput);
  };

  const handleCustomizeClick = () => {
    setShowConversationalForm(true);
  };

  const handleConversationalFormComplete = (data: any) => {
    console.log('Conversational form completed with:', data);
    setShowConversationalForm(false);
    // Here you would process the form data and potentially switch to input mode
    // or run the analysis directly
  };

  const handleConversationalFormCancel = () => {
    setShowConversationalForm(false);
  };

  const handleSaveToDashboard = () => {
    if (onSaveToDashboard) {
      onSaveToDashboard();
    } else {
      console.log('Save to dashboard:', moduleKey);
    }
  };

  const handleExportData = () => {
    if (onExportData) {
      onExportData();
    } else {
      console.log('Export data for:', moduleKey);
    }
  };

  const handleShareAnalysis = () => {
    if (onShareAnalysis) {
      onShareAnalysis();
    } else {
      console.log('Share analysis:', moduleKey);
    }
  };

  return (
    <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
      {/* Header with Actions */}
      <div className="border-b border-gray-100 px-4 py-3 bg-gray-50">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 bg-green-500 rounded-full"></div>
            <span className="text-sm font-medium text-gray-700">
              {title || 'Analysis Results'}
            </span>
          </div>
          
          <div className="flex items-center gap-2">
            <button
              onClick={handleCustomizeClick}
              className="px-3 py-1.5 text-xs bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
            >
              🤖 AI Customize
            </button>
            
            <div className="relative">
              <button
                onClick={() => setShowActions(!showActions)}
                className="p-1.5 text-gray-500 hover:text-gray-700 rounded-md hover:bg-gray-100 transition-colors"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 5v.01M12 12v.01M12 19v.01M12 6a1 1 0 110-2 1 1 0 010 2zM12 13a1 1 0 110-2 1 1 0 010 2zM12 20a1 1 0 110-2 1 1 0 010 2z" />
                </svg>
              </button>
              
              {showActions && (
                <div className="absolute right-0 top-full mt-1 w-48 bg-white border border-gray-200 rounded-lg shadow-lg z-10">
                  <div className="py-1">
                    <button
                      onClick={handleSaveToDashboard}
                      className="w-full px-3 py-2 text-left text-sm text-gray-700 hover:bg-gray-50 flex items-center gap-2"
                    >
                      <span>📊</span>
                      Save to Dashboard
                    </button>
                    <button
                      onClick={handleExportData}
                      className="w-full px-3 py-2 text-left text-sm text-gray-700 hover:bg-gray-50 flex items-center gap-2"
                    >
                      <span>📁</span>
                      Export Data
                    </button>
                    <button
                      onClick={handleShareAnalysis}
                      className="w-full px-3 py-2 text-left text-sm text-gray-700 hover:bg-gray-50 flex items-center gap-2"
                    >
                      <span>🔗</span>
                      Share Analysis
                    </button>
                    <hr className="my-1" />
                    <button
                      onClick={() => window.print()}
                      className="w-full px-3 py-2 text-left text-sm text-gray-700 hover:bg-gray-50 flex items-center gap-2"
                    >
                      <span>🖨️</span>
                      Print Results
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="p-4">
        {showInput ? inputComponent : outputComponent}
      </div>

      {/* Footer */}
      <div className="border-t border-gray-100 px-4 py-2 bg-gray-50">
        <div className="flex items-center justify-between text-xs text-gray-500">
          <span>Generated {new Date().toLocaleString()}</span>
          <div className="flex items-center gap-4">
            <span>✨ AI-Powered Analysis</span>
            <span>📈 Real-time Data</span>
          </div>
        </div>
      </div>

      {/* Conversational Form Modal */}
      {showConversationalForm && (
        <ConversationalForm
          onComplete={handleConversationalFormComplete}
          onCancel={handleConversationalFormCancel}
        />
      )}
    </div>
  );
}