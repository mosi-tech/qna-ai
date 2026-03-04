'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { AnalysisSession, ParameterSet } from '@/types/parameters';
import ParameterDrawer from './ParameterDrawer';
import AnalysisResultSection from './AnalysisResultSection';
import HistorySection from './HistorySection';
import { api } from '@/lib/api';
// Using emoji icons instead of @heroicons/react

interface AnalysisWorkspaceProps {
  sessionId: string;
  initialQuestion?: string;
  initialResults?: any;
  analysisId?: string;
  executionId?: string;
  messageId?: string;  // Add messageId prop
}

export default function AnalysisWorkspace({ 
  sessionId, 
  initialQuestion = "Analysis Workspace",
  initialResults,
  analysisId,
  executionId,
  messageId
}: AnalysisWorkspaceProps) {
  const router = useRouter();
  const [session, setSession] = useState<AnalysisSession | null>(null);
  const [currentParameters, setCurrentParameters] = useState<ParameterSet>({});
  const [isRunning, setIsRunning] = useState(false);
  const [hasChanges, setHasChanges] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastSavedParameters, setLastSavedParameters] = useState<ParameterSet>({});
  const [resolvedAnalysisId, setResolvedAnalysisId] = useState<string | undefined>(analysisId);
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);

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
    const initializeSession = async () => {
      try {
        let analysisData = initialResults;
        let question = initialQuestion;
        let currentAnalysisId = analysisId;
        
        // If no initial data provided, try to get it from the analysis, message, or session
        if (!analysisData) {
          if (messageId) {
            // Primary approach: Get analysis via message ID (new structured route)
            try {
              console.log('Loading analysis via message ID:', messageId);
              const analysis = await api.analysis.getAnalysisByMessageId(messageId);
              if (analysis) {
                analysisData = analysis;
                question = analysis.originalQuestion || analysis.title || 'Analysis';
                // Extract analysisId from the response for execution history
                currentAnalysisId = analysis.analysisId;
                setResolvedAnalysisId(currentAnalysisId);
                console.log('✓ Successfully loaded analysis via message ID, analysisId:', currentAnalysisId);
              }
            } catch (error) {
              console.warn('Failed to fetch analysis by message ID:', error);
              // Continue to fallbacks
            }
          }
          
          if (!analysisData && currentAnalysisId) {
            // Fallback 1: Get analysis details using analysis ID (legacy route or direct access)
            try {
              console.log('Loading analysis via analysis ID:', currentAnalysisId);
              const analysis = await api.analysis.getAnalysisById(currentAnalysisId);
              if (analysis) {
                analysisData = analysis;
                question = analysis.originalQuestion || analysis.title || 'Analysis';
                console.log('✓ Successfully loaded analysis via analysis ID');
              }
            } catch (error) {
              console.warn('Failed to fetch analysis details:', error);
              // Continue to fallbacks
            }
          }
          
          if (!analysisData && sessionId) {
            // Fallback 2: Get session execution history to find the latest analysis
            try {
              console.log('Loading analysis via session execution history:', sessionId);
              const executions = await api.analysis.getExecutionHistory(sessionId, 1);
              if (executions.length > 0) {
                const latestExecution = executions[0];
                analysisData = latestExecution.results || latestExecution;
                question = latestExecution.originalQuestion || 'Analysis';
                console.log('✓ Successfully loaded analysis via execution history');
              }
            } catch (error) {
              console.warn('Failed to fetch execution history:', error);
            }
          }
        }
        
        // Use parameterSchema from API response if available, otherwise extract from data
        let parameterSchema = analysisData?.parameterSchema || [];
        
        if (parameterSchema.length === 0) {
          // Fallback to old extraction method for legacy data
          parameterSchema = extractParameterSchema(analysisData);
        }
        
        const session: AnalysisSession = {
          id: sessionId,
          originalQuestion: question || 'Analysis Workspace',
          createdAt: new Date(),
          runs: analysisData ? [{
            id: 'initial',
            parameters: analysisData?.parameters || {},
            results: analysisData,
            status: 'completed',
            duration: analysisData?.execution_time || 0,
            createdAt: new Date(analysisData?.created_at || Date.now())
          }] : [],
          activeRunId: analysisData ? 'initial' : undefined,
          parameterSchema: parameterSchema
        };

        // Initialize current parameters with defaults
        const defaultParams: ParameterSet = {};
        parameterSchema.forEach((param: any) => {
          defaultParams[param.id] = param.defaultValue;
        });

        // Try to load saved parameters from localStorage
        let loadedParams = defaultParams;
        try {
          const savedParams = localStorage.getItem(`analysis-params-${sessionId}`);
          if (savedParams) {
            const parsed = JSON.parse(savedParams);
            // Merge with defaults to ensure all required parameters exist
            loadedParams = { ...defaultParams, ...parsed };
          }
        } catch (err) {
          console.warn('Failed to load saved parameters from localStorage:', err);
        }

        setSession(session);
        setCurrentParameters(loadedParams);
        setLastSavedParameters(defaultParams); // Keep defaults as the baseline
        
        // Store the resolved analysisId for execution operations
        if (currentAnalysisId && currentAnalysisId !== analysisId) {
          // analysisId was resolved from messageId, store it for later use
          console.log('Analysis ID resolved from message:', currentAnalysisId);
        }
        
      } catch (error) {
        console.error('Failed to initialize session:', error);
        setError(error instanceof Error ? error.message : 'Failed to load analysis data');
        
        // Don't create a fallback session - let the error state be shown instead
        setSession(null);
      }
    };
    
    initializeSession();
  }, [sessionId, initialQuestion, initialResults, analysisId, executionId, messageId]);

  const handleParameterChange = (parameterId: string, value: any) => {
    setCurrentParameters(prev => {
      const newParams = {
        ...prev,
        [parameterId]: value
      };
      
      // Auto-save parameters to localStorage
      try {
        localStorage.setItem(`analysis-params-${sessionId}`, JSON.stringify(newParams));
      } catch (err) {
        console.warn('Failed to save parameters to localStorage:', err);
      }
      
      return newParams;
    });
    
    // Check if parameters have actually changed from last saved state
    const hasRealChanges = JSON.stringify(lastSavedParameters) !== JSON.stringify({
      ...currentParameters,
      [parameterId]: value
    });
    setHasChanges(hasRealChanges);
  };

  const handleRerun = async () => {
    if (!session || isRunning) return;

    setIsRunning(true);
    setError(null);
    
    try {
      let executionResult;
      
      // If we have an analysisId, execute that specific analysis using the new API
      if (resolvedAnalysisId) {
        console.log('Executing analysis:', resolvedAnalysisId, 'with parameters:', currentParameters);
        
        try {
          // Try the new analysis API first
          const execution = await api.analysis.executeAnalysisNew(resolvedAnalysisId, currentParameters, sessionId);
          console.log('Execution started (new API):', execution);
          
          // Poll for completion if we get an execution ID
          if (execution.execution_id) {
            executionResult = await api.analysis.pollExecutionStatus(
              execution.execution_id,
              (status) => {
                console.log('Execution progress:', status);
                // You could update UI with progress here if needed
              }
            );
          } else {
            // Direct result returned
            executionResult = execution;
          }
          
          console.log('Execution completed (new API):', executionResult);
        } catch (error) {
          console.warn('New API failed, falling back to legacy API:', error);
          
          // Fallback to legacy API
          const execution = await api.analysis.executeAnalysis(resolvedAnalysisId, currentParameters, sessionId);
          console.log('Execution started (legacy):', execution);
          
          // Poll for completion
          executionResult = await api.analysis.pollExecutionStatus(
            execution.execution_id,
            (status) => {
              console.log('Execution progress:', status);
              // You could update UI with progress here if needed
            }
          );
          
          console.log('Execution completed (legacy):', executionResult);
        }
      } else {
        // Fallback: try to re-run using session-based execution
        const analyses = await api.analysis.getUserAnalyses(50);
        const latestAnalysis = analyses.find((a: any) => 
          a.session_id === sessionId || a.originalQuestion === session.originalQuestion
        );
        
        if (latestAnalysis) {
          const execution = await api.analysis.executeAnalysis(
            latestAnalysis.id, 
            currentParameters, 
            sessionId
          );
          
          executionResult = await api.analysis.pollExecutionStatus(execution.execution_id);
        } else {
          throw new Error('No analysis found to re-run. Please create a new analysis.');
        }
      }
      
      const newRun = {
        id: `run-${Date.now()}`,
        parameters: { ...currentParameters },
        results: executionResult.results || executionResult,
        status: 'completed' as const,
        duration: executionResult.execution_time || 0,
        createdAt: new Date()
      };

      setSession(prev => prev ? {
        ...prev,
        runs: [...prev.runs, newRun],
        activeRunId: newRun.id
      } : null);

      setHasChanges(false);
      setLastSavedParameters(currentParameters);
    } catch (error) {
      console.error('Analysis execution failed:', error);
      setError(error instanceof Error ? error.message : 'Analysis execution failed');
      
      // Add a failed run to history
      const failedRun = {
        id: `run-${Date.now()}`,
        parameters: { ...currentParameters },
        results: null,
        status: 'failed' as const,
        duration: 0,
        createdAt: new Date(),
        error: error instanceof Error ? error.message : 'Unknown error'
      };

      setSession(prev => prev ? {
        ...prev,
        runs: [...prev.runs, failedRun],
        activeRunId: failedRun.id
      } : null);
    } finally {
      setIsRunning(false);
    }
  };

  const handleBackToChat = () => {
    router.back();
  };

  if (!session) {
    // Show error state if there's an error, otherwise show loading
    if (error) {
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
                  <p className="text-sm text-gray-600">Failed to load analysis</p>
                </div>
              </div>
            </div>
          </div>

          {/* Error Content */}
          <div className="p-6">
            <div className="max-w-2xl mx-auto">
              <div className="bg-red-50 border border-red-200 rounded-lg p-6">
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-10 h-10 bg-red-100 rounded-full flex items-center justify-center">
                    <span className="text-red-600 text-xl">⚠</span>
                  </div>
                  <div>
                    <h2 className="text-lg font-semibold text-red-800">Something went wrong</h2>
                    <p className="text-sm text-red-600">Failed to load the analysis workspace</p>
                  </div>
                </div>
                
                <div className="bg-red-100 rounded-md p-4 mb-4">
                  <p className="text-sm text-red-700 font-mono">{error}</p>
                </div>
                
                <div className="flex gap-3">
                  <button 
                    onClick={handleBackToChat}
                    className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors"
                  >
                    Back to Chat
                  </button>
                  <button 
                    onClick={() => window.location.reload()}
                    className="px-4 py-2 bg-white text-red-600 border border-red-300 rounded-md hover:bg-red-50 transition-colors"
                  >
                    Retry
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      );
    }

    // Show loading state
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

      {/* Error Message */}
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-800 px-4 py-3 mx-6 mt-4 rounded-lg">
          <div className="flex justify-between items-center">
            <span>{error}</span>
            <button 
              onClick={() => setError(null)}
              className="text-red-600 hover:text-red-800"
            >
              ✕
            </button>
          </div>
        </div>
      )}

      {/* Main Content */}
      <div className="p-6">
        <div className="max-w-7xl mx-auto">
          {/* Grid layout with Analysis Result on left */}
          <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
            {/* Analysis Result Section - Main content */}
            <div className="lg:col-span-3">
              <AnalysisResultSection
                results={activeRun?.results}
                isRunning={isRunning}
                onConfigureParameters={() => setIsDrawerOpen(true)}
                hasParameterChanges={hasChanges}
              />
            </div>

            {/* Right sidebar with History only */}
            <div className="space-y-6">
              {/* History Section */}
              <HistorySection
                runs={session.runs}
                activeRunId={session.activeRunId}
                onSelectRun={(runId) => setSession(prev => prev ? { ...prev, activeRunId: runId } : null)}
                analysisId={resolvedAnalysisId}
                sessionId={sessionId}
              />
            </div>
          </div>
        </div>
      </div>

      {/* Parameter Drawer */}
      <ParameterDrawer
        isOpen={isDrawerOpen}
        onClose={() => setIsDrawerOpen(false)}
        schema={session.parameterSchema}
        values={currentParameters}
        onChange={handleParameterChange}
        onRerun={handleRerun}
        hasChanges={hasChanges}
        isRunning={isRunning}
        analysisTitle={session.originalQuestion}
      />
    </div>
  );
}