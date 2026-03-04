/**
 * Clean UI-specific chat message types
 * These exclude internal metadata and database fields
 */

export interface UIAnalysisResult {
  // Core analysis data for display
  type: string;
  summary: string;
  
  // Key results in user-friendly format
  keyFindings: {
    label: string;
    value: string | number;
    description?: string;
  }[];
  
  // Execution status for real-time updates
  execution?: {
    status: 'queued' | 'running' | 'completed' | 'failed';
    progress?: number;
    logs?: string[];
    error?: string;
  };
  
  // Parameters used (for workspace navigation)
  parameters?: Record<string, any>;
  
  // Confidence/quality indicators
  confidence?: number;
  
  // Action buttons data
  canRerun?: boolean;
  canExport?: boolean;
}

export interface UIChatMessage {
  id: string;
  type: 'user' | 'assistant' | 'error' | 'clarification' | 'analysis';
  content: string;
  timestamp: Date;
  
  // Analysis-specific data (only for analysis messages)
  analysisResult?: UIAnalysisResult;
  
  // Reference IDs for backend operations
  analysisId?: string;
  executionId?: string;
  
  // Clarification data (only for clarification messages)
  clarificationData?: {
    originalQuery: string;
    expandedQuery: string;
    suggestions?: string[];
    confidence?: number;
  };
}

/**
 * Transform raw backend message to clean UI message
 */
export function transformToUIMessage(rawMessage: any): UIChatMessage {
  const baseMessage: UIChatMessage = {
    id: rawMessage.id || rawMessage.messageId,
    type: determineMessageType(rawMessage),
    content: rawMessage.content || '',
    timestamp: new Date(rawMessage.timestamp || rawMessage.createdAt || Date.now()),
    analysisId: rawMessage.analysisId,
    executionId: rawMessage.executionId,
  };

  // Transform analysis data if present
  if (baseMessage.type === 'analysis' && rawMessage.metadata) {
    baseMessage.analysisResult = transformAnalysisData(rawMessage.metadata);
  }

  // Transform clarification data if present
  if (baseMessage.type === 'clarification' && rawMessage.metadata) {
    baseMessage.clarificationData = {
      originalQuery: rawMessage.metadata.original_query || '',
      expandedQuery: rawMessage.metadata.expanded_query || '',
      suggestions: rawMessage.metadata.suggestions || [],
      confidence: rawMessage.metadata.confidence,
    };
  }

  return baseMessage;
}

/**
 * Determine clean message type from raw data
 */
function determineMessageType(rawMessage: any): UIChatMessage['type'] {
  if (rawMessage.role === 'user') return 'user';
  
  if (rawMessage.role === 'assistant') {
    // Check if it contains analysis results
    if (rawMessage.metadata?.response_type === 'analysis' || 
        rawMessage.metadata?.analysis_result ||
        rawMessage.metadata?.best_day ||
        rawMessage.metadata?.query_type) {
      return 'analysis';
    }
    
    // Check if it's a clarification request
    if (rawMessage.metadata?.response_type === 'clarification' ||
        rawMessage.metadata?.needs_clarification) {
      return 'clarification';
    }
    
    return 'assistant';
  }
  
  return 'assistant';
}

/**
 * Transform raw analysis metadata to clean UI format
 */
function transformAnalysisData(metadata: any): UIAnalysisResult {
  // Extract analysis type
  const analysisType = metadata.analysis_type || metadata.query_type || 'Financial Analysis';
  
  // Extract key findings
  const keyFindings: UIAnalysisResult['keyFindings'] = [];
  
  // Handle weekday performance analysis
  if (metadata.best_day && metadata.average_return) {
    keyFindings.push(
      {
        label: 'Best Performing Day',
        value: metadata.best_day,
        description: 'Day of the week with highest average returns'
      },
      {
        label: 'Average Return',
        value: `${Number(metadata.average_return).toFixed(2)}%`,
        description: 'Average return on the best performing day'
      }
    );
  }
  
  // Handle generic analysis results
  if (metadata.response_data?.analysis_result) {
    const result = metadata.response_data.analysis_result;
    Object.entries(result).forEach(([key, value]) => {
      // Skip internal fields
      if (['execution', 'metadata', '_id', 'createdAt', 'updatedAt'].includes(key)) {
        return;
      }
      
      keyFindings.push({
        label: key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
        value: typeof value === 'number' ? Number(value).toFixed(2) : String(value),
      });
    });
  }
  
  // Extract parameters
  const parameters = metadata.response_data?.analysis_result?.execution?.parameters || {};
  
  return {
    type: analysisType,
    summary: generateSummary(analysisType, keyFindings),
    keyFindings,
    execution: {
      status: metadata.execution_status || 'completed',
      progress: metadata.execution_progress,
      logs: metadata.execution_logs,
      error: metadata.execution_error,
    },
    parameters,
    confidence: metadata.confidence,
    canRerun: true,
    canExport: true,
  };
}

/**
 * Generate a user-friendly summary
 */
function generateSummary(type: string, findings: UIAnalysisResult['keyFindings']): string {
  if (findings.length === 0) {
    return `${type} completed successfully.`;
  }
  
  if (type.includes('weekday') || type.includes('performance')) {
    const bestDay = findings.find(f => f.label.includes('Day'))?.value;
    const avgReturn = findings.find(f => f.label.includes('Return'))?.value;
    if (bestDay && avgReturn) {
      return `Analysis shows ${bestDay} performs best with ${avgReturn} average return.`;
    }
  }
  
  return `${type} completed with ${findings.length} key finding${findings.length !== 1 ? 's' : ''}.`;
}