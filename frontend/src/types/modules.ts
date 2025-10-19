export type ParameterType = 'dropdown' | 'input' | 'date' | 'checkbox';

export interface Parameter {
  type: ParameterType;
  label: string;
  options?: string[];
  defaultValue?: string | number | boolean | string[];
  placeholder?: string;
}

export interface Module {
  title: string;
  description?: string;
  category?: string;
  difficulty?: 'Beginner' | 'Intermediate' | 'Advanced';
  estimatedTime?: string;
  type?: string;
  params: Parameter[];
}

export interface ModuleConfig {
  [key: string]: Module;
}

export interface ParameterValues {
  [key: string]: string | number | boolean | string[];
}