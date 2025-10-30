export interface ParameterDefinition {
  id: string;
  name: string;
  type: 'text' | 'number' | 'select' | 'boolean';
  required?: boolean;
  description?: string;
  validation?: ParameterValidation;
  defaultValue?: any;
}

export interface ParameterValidation {
  min?: number;
  max?: number;
  pattern?: string;
  options?: Array<{ label: string; value: any }>;
  errorMessage?: string;
}

export interface ParameterValue {
  parameterId: string;
  value: any;
  isValid: boolean;
  error?: string;
}

export interface ParameterSet {
  [parameterId: string]: any;
}

export interface AnalysisRun {
  id: string;
  parameters: ParameterSet;
  results: any;
  status: 'running' | 'completed' | 'failed';
  duration?: number;
  createdAt: Date;
  error?: string;
}

export interface AnalysisSession {
  id: string;
  originalQuestion: string;
  chatMessageId?: string;
  createdAt: Date;
  runs: AnalysisRun[];
  activeRunId?: string;
  parameterSchema: ParameterDefinition[];
}

export interface ParameterFormProps {
  schema: ParameterDefinition[];
  values: ParameterSet;
  onChange: (parameterId: string, value: any) => void;
  onValidationChange: (parameterId: string, isValid: boolean, error?: string) => void;
  disabled?: boolean;
}

export interface AnalysisWorkspaceProps {
  sessionId: string;
  initialQuestion?: string;
  initialResults?: any;
}