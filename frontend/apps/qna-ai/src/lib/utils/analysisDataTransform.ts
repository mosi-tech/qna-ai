/**
 * Transform LLM analysis response data to match predefined grid config structure
 * Maps analysis_data placeholders to actual values
 * Supports both new (components array) and old (uiConfig) formats
 */

export interface ComponentSpec {
  component: string;
  props: Record<string, unknown>;
}

export interface AnalysisResponse {
  components?: ComponentSpec[];
  configType?: string;
  analysisData?: Record<string, unknown>;
  uiConfig?: Record<string, unknown>; // Old format support
  [key: string]: unknown;
}

/**
 * Parse LLM response and extract structured analysis data
 * Supports both direct data and templated data with {{analysis_data.path}} format
 */
export function transformAnalysisData(rawData: Record<string, unknown>): AnalysisResponse {
  const configType = extractConfigType(rawData);
  
  // If data already has proper structure, use it
  if (rawData.analysisData && typeof rawData.analysisData === 'object') {
    return {
      configType,
      analysisData: rawData.analysisData as Record<string, unknown>,
    };
  }

  // Otherwise, structure the raw data for the grid
  const analysisData = structureAnalysisData(rawData);

  return {
    configType,
    analysisData,
  };
}

/**
 * Extract config type from response (e.g., 'predefined-config-1', 'portfolioAnalysis', etc.)
 */
function extractConfigType(data: Record<string, unknown>): string {
  if (typeof data.configType === 'string') {
    return data.configType;
  }

  // Fallback to default if not specified
  return 'predefined-config-1';
}

/**
 * Structure raw analysis data into a format suitable for grid slots
 * Maps common response patterns to slot data
 */
function structureAnalysisData(data: Record<string, unknown>): Record<string, unknown> {
  const structured: Record<string, unknown> = {};

  // Copy all data as-is (PredefinedGridRenderer will handle template substitution)
  Object.entries(data).forEach(([key, value]) => {
    if (key !== 'configType') {
      structured[key] = value;
    }
  });

  return structured;
}

/**
 * Substitute template placeholders like {{analysis_data.key}} with actual values
 * Used by PredefinedGridRenderer for each slot's props
 */
export function substituteTemplates(
  templateString: string,
  analysisData: Record<string, unknown>
): string | unknown {
  // If not a string, return as-is
  if (typeof templateString !== 'string') {
    return templateString;
  }

  // Match {{analysis_data.path.to.value}} patterns
  const pattern = /\{\{analysis_data\.([^}]+)\}\}/g;

  // Check if there are any templates
  if (!pattern.test(templateString)) {
    return templateString;
  }

  // Reset regex state
  const patternResetter = /\{\{analysis_data\.([^}]+)\}\}/g;
  let result = templateString;
  let hasSubstitution = false;

  result = result.replace(patternResetter, (match, path: string) => {
    const value = getNestedValue(analysisData, path);
    if (value !== undefined) {
      hasSubstitution = true;
      return String(value);
    }
    return match; // Keep original if not found
  });

  return result;
}

/**
 * Get nested object value by dot-notation path
 * e.g., 'metrics.performance.return' -> analysisData.metrics.performance.return
 */
function getNestedValue(obj: Record<string, unknown>, path: string): unknown {
  return path.split('.').reduce((current, key) => {
    if (current && typeof current === 'object' && key in current) {
      return (current as Record<string, unknown>)[key];
    }
    return undefined;
  }, obj as unknown);
}

/**
 * Validate that analysis data contains required fields for a config
 */
export function validateAnalysisData(
  configType: string,
  analysisData: Record<string, unknown>
): { valid: boolean; errors: string[] } {
  const errors: string[] = [];

  // Basic validation - just check that we have data
  if (!analysisData || Object.keys(analysisData).length === 0) {
    errors.push('Analysis data is empty');
  }

  return {
    valid: errors.length === 0,
    errors,
  };
}

/**
 * Convert old uiConfig format to new components format
 * Old format: { selected_components: [...], layout_template: "...", ... }
 * OR: { uiConfig: { component: "...", props: {...}, ... }, ... }
 * New format: { components: [...] }
 */
export function convertOldFormatToNew(data: Record<string, unknown>): ComponentSpec[] {
  // Check if this is old format with selected_components array
  if (Array.isArray(data.selected_components)) {
    return (data.selected_components as any[]).map((item) => ({
      component: item.component_name || item.component,
      props: item.props || item,
    }));
  }

  // Check if uiConfig exists at root level
  if (data.uiConfig && typeof data.uiConfig === 'object') {
    const config = data.uiConfig as Record<string, unknown>;
    
    // If uiConfig.components is an array
    if (Array.isArray(config.components)) {
      return config.components as ComponentSpec[];
    }
    
    // If uiConfig itself has a component property (single component case)
    if (config.component) {
      return [{
        component: config.component as string,
        props: config.props || config,
      }];
    }
    
    // Try to extract components from uiConfig properties by looking for component definitions
    const components: ComponentSpec[] = [];
    Object.entries(config).forEach(([key, value]) => {
      if (value && typeof value === 'object') {
        const obj = value as any;
        // If object has a component property, treat it as a component spec
        if (obj.component_name || obj.component || obj.props) {
          components.push({
            component: obj.component_name || obj.component || key,
            props: obj.props || obj,
          });
        }
      }
    });
    if (components.length > 0) {
      return components;
    }
  }

  // Not old format
  return [];
}

/**
 * Normalize analysis response - converts old formats to new format
 */
export function normalizeAnalysisResponse(data: Record<string, unknown>): {
  components: ComponentSpec[];
  analysisData: Record<string, unknown>;
} {
  // Try old format first
  const oldFormatComponents = convertOldFormatToNew(data);
  if (oldFormatComponents.length > 0) {
    return {
      components: oldFormatComponents,
      analysisData: data,
    };
  }

  // New format
  const components = (data.components || []) as ComponentSpec[];
  return {
    components,
    analysisData: data,
  };
}
