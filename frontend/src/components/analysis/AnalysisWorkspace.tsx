'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { AnalysisSession, ParameterSet } from '@/types/parameters';
import ParameterSection from './ParameterSection';
import ResultsSection from './ResultsSection';
import HistorySection from './HistorySection';
import InsightsSection from './InsightsSection';

interface AnalysisWorkspaceProps {
  sessionId: string;
  initialQuestion?: string;
  initialResults?: any;
  analysisId?: string;
  executionId?: string;
}

export default function AnalysisWorkspace({ 
  sessionId, 
  initialQuestion = "Analysis Workspace",
  initialResults,
  analysisId,
  executionId
}: AnalysisWorkspaceProps) {
  const router = useRouter();
  const [session, setSession] = useState<AnalysisSession | null>(null);
  const [currentParameters, setCurrentParameters] = useState<ParameterSet>({});
  const [isRunning, setIsRunning] = useState(false);
  const [hasChanges, setHasChanges] = useState(false);

  // Extract parameter schema from analysis data
  const extractParameterSchema = (resultsData: any) => {
    console.log('Extracting parameters from data:', resultsData);
    
    // Try different paths where parameters might be stored
    const parameters = resultsData?.parameters || 
                     resultsData?.execution?.parameters ||
                     resultsData?.response_data?.analysis_result?.execution?.parameters ||
                     {};
    
    const analysisType = resultsData?.analysis_type || 
                        resultsData?.query_type ||
                        'unknown';
    
    console.log('Found parameters:', parameters, 'Analysis type:', analysisType);
    
    // Convert existing parameters to parameter definitions
    const schema = Object.entries(parameters).map(([key, value]) => {
      // Determine parameter type based on value and key name
      let type: 'text' | 'number' | 'select' | 'boolean' = 'text';
      let validation: any = {};
      
      if (typeof value === 'number') {
        type = 'number';
        // Set reasonable defaults based on common parameter types
        if (key.includes('period') || key.includes('days') || key.includes('window')) {
          validation = { min: 1, max: 1000 };
        } else if (key.includes('percent') || key.includes('ratio')) {
          validation = { min: 0, max: 100, step: 0.1 };
        } else {
          validation = { min: 0, max: 10000 };
        }
      } else if (typeof value === 'boolean') {
        type = 'boolean';
      } else if (Array.isArray(value)) {
        type = 'select';
        validation = {
          options: value.map((v: any) => ({ label: String(v), value: v }))
        };
      } else if (typeof value === 'string') {
        // Check if it looks like a symbol
        if (key.includes('symbol') || key.includes('ticker')) {
          validation = {
            pattern: '^[A-Z]{1,5}$',
            errorMessage: 'Enter a valid stock symbol (1-5 uppercase letters)'
          };
        }
      }
      
      return {
        id: key,
        name: key.split('_').map(word => 
          word.charAt(0).toUpperCase() + word.slice(1)
        ).join(' '),
        type,
        required: true,
        description: `${key.replace('_', ' ')} parameter for ${analysisType} analysis`,
        defaultValue: value,
        validation
      };
    });

    // If no parameters found, provide common analysis parameters
    if (schema.length === 0) {
      return [
        {
          id: 'symbol',
          name: 'Symbol',
          type: 'text' as const,
          required: true,
          description: 'Stock symbol to analyze',
          defaultValue: 'AAPL',
          validation: {
            pattern: '^[A-Z]{1,5}$',
            errorMessage: 'Enter a valid stock symbol (1-5 uppercase letters)'
          }
        },
        {
          id: 'period',
          name: 'Analysis Period',
          type: 'number' as const,
          required: true,
          description: 'Number of trading days to analyze',
          defaultValue: 252,
          validation: {
            min: 30,
            max: 1000,
            errorMessage: 'Period must be between 30 and 1000 days'
          }
        }
      ];
    }

    return schema;
  };

  // Initialize session
  useEffect(() => {
    // Extract parameters from the real analysis data
    const parameterSchema = extractParameterSchema(initialResults);
    
    const mockSession: AnalysisSession = {
      id: sessionId,
      originalQuestion: initialQuestion,
      createdAt: new Date(),
      runs: initialResults ? [{
        id: 'initial',
        parameters: {},
        results: initialResults,
        status: 'completed',
        duration: 0,
        createdAt: new Date()
      }] : [],
      activeRunId: initialResults ? 'initial' : undefined,
      parameterSchema: parameterSchema
    };

    // Initialize current parameters with defaults
    const defaultParams: ParameterSet = {};
    parameterSchema.forEach(param => {
      defaultParams[param.id] = param.defaultValue;
    });

    setSession(mockSession);
    setCurrentParameters(defaultParams);
  }, [sessionId, initialQuestion, initialResults, analysisId, executionId]);

  const handleParameterChange = (parameterId: string, value: any) => {
    setCurrentParameters(prev => ({
      ...prev,
      [parameterId]: value
    }));
    setHasChanges(true);
  };

  const handleRerun = async () => {
    if (!session || isRunning) return;

    setIsRunning(true);
    
    try {
      // Mock API call - replace with actual implementation
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      const newRun = {
        id: `run-${Date.now()}`,
        parameters: { ...currentParameters },
        results: {
          best_day: 'Tuesday',
          average_return: 2.1,
          confidence: 87,
          analysis_type: 'weekday_performance'
        },
        status: 'completed' as const,
        duration: 2000,
        createdAt: new Date()
      };

      setSession(prev => prev ? {
        ...prev,
        runs: [...prev.runs, newRun],
        activeRunId: newRun.id
      } : null);

      setHasChanges(false);
    } catch (error) {
      console.error('Analysis failed:', error);
    } finally {
      setIsRunning(false);
    }
  };

  const handleBackToChat = () => {
    router.back();
  };

  if (!session) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
      </div>
    );
  }

  const activeRun = session.runs.find(run => run.id === session.activeRunId);

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button 
              onClick={handleBackToChat}
              className="flex items-center gap-2 text-gray-600 hover:text-gray-900"
            >
              <span>←</span>
              <span>Back to Chat</span>
            </button>
            <div className="h-6 w-px bg-gray-300" />
            <div>
              <h1 className="text-xl font-semibold text-gray-900">Analysis Workspace</h1>
              <p className="text-sm text-gray-600">{session.originalQuestion}</p>
            </div>
          </div>
          <div className="flex items-center gap-2 text-sm text-gray-500">
            {session.runs.length > 0 && (
              <span>{session.runs.length} run{session.runs.length !== 1 ? 's' : ''}</span>
            )}
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="p-6">
        <div className="grid grid-cols-2 gap-6 max-w-7xl mx-auto">
          {/* Parameters Section */}
          <ParameterSection
            schema={session.parameterSchema}
            values={currentParameters}
            onChange={handleParameterChange}
            onRerun={handleRerun}
            hasChanges={hasChanges}
            isRunning={isRunning}
          />

          {/* Results Section */}
          <ResultsSection
            results={activeRun?.results}
            isRunning={isRunning}
            runCount={session.runs.length}
          />

          {/* History Section */}
          <HistorySection
            runs={session.runs}
            activeRunId={session.activeRunId}
            onSelectRun={(runId) => setSession(prev => prev ? { ...prev, activeRunId: runId } : null)}
          />

          {/* Insights Section */}
          <InsightsSection
            results={activeRun?.results}
            runs={session.runs}
            parameters={currentParameters}
          />
        </div>
      </div>
    </div>
  );
}