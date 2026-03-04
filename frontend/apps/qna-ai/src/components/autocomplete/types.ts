export interface FormField {
  id: string;
  label: string;
  type: 'select' | 'input' | 'multiselect' | 'range';
  options?: string[];
  placeholder?: string;
  value?: string | string[] | number;
  min?: number;
  max?: number;
  step?: number;
}

export interface PredictedCategory {
  id: string;
  title: string;
  description: string;
  emoji: string;
  fields: FormField[];
  expandedFields?: FormField[];
  suggestedQuestion: string;
}

export interface SuggestedQuestion {
  id: string;
  text: string;
  emoji: string;
  confidence: 'high' | 'medium' | 'low';
}

export interface SelectedSettings {
  [key: string]: string;
}

export interface SettingType {
  id: string;
  label: string;
  emoji: string;
}

export interface SettingSuggestion {
  id: string;
  title: string;
  description: string;
  emoji: string;
}