/**
 * Component Validation System
 * Enforces component limits and space constraints based on layout mapping
 */

import { useEffect } from 'react';

export interface ComponentLimits {
  maxItems?: number;
  maxColumns?: number;
  maxTextLength?: {
    title?: number;
    content?: number;
    description?: number;
  };
  requiredVariant?: string;
  allowedVariants?: string[];
}

export interface ValidationResult {
  isValid: boolean;
  errors: string[];
  warnings: string[];
  suggestedFixes?: {
    variant?: string;
    maxItems?: number;
    truncateContent?: boolean;
  };
}

// Define limits for each component type in each space
const COMPONENT_LIMITS: Record<string, Record<string, ComponentLimits>> = {
  // Quarter width spaces (smallest)
  quarter_width: {
    StatGroup: {
      maxItems: 2,
      maxColumns: 2,
      requiredVariant: 'compact',
      maxTextLength: {
        title: 20,
        content: 15
      }
    },
    CalloutList: {
      maxItems: 3,
      requiredVariant: 'compact',
      maxTextLength: {
        title: 15,
        content: 40
      }
    },
    CalloutNote: {
      maxItems: 1,
      requiredVariant: 'compact',
      maxTextLength: {
        title: 20,
        content: 60
      }
    },
    Section: {
      requiredVariant: 'compact',
      maxTextLength: {
        title: 25
      }
    }
  },
  
  // Half width spaces
  half_width: {
    StatGroup: {
      maxItems: 4,
      maxColumns: 2,
      allowedVariants: ['compact', 'default'],
      maxTextLength: {
        title: 25,
        content: 20
      }
    },
    ComparisonTable: {
      maxItems: 4, // entities
      maxColumns: 4, // metrics
      requiredVariant: 'narrow',
      maxTextLength: {
        title: 30
      }
    },
    CalloutList: {
      maxItems: 4,
      allowedVariants: ['compact', 'default'],
      maxTextLength: {
        title: 20,
        content: 50
      }
    },
    Section: {
      allowedVariants: ['compact', 'default'],
      maxTextLength: {
        title: 30
      }
    }
  },
  
  // Two thirds width spaces
  two_thirds_width: {
    ComparisonTable: {
      maxItems: 6,
      maxColumns: 5,
      allowedVariants: ['default', 'wide'],
      maxTextLength: {
        title: 40
      }
    },
    StatGroup: {
      maxItems: 6,
      maxColumns: 3,
      allowedVariants: ['horizontal', 'default']
    },
    ActionList: {
      maxItems: 5,
      allowedVariants: ['default', 'detailed']
    }
  },
  
  // Full width spaces (largest)
  full_width: {
    ActionList: {
      maxItems: 8,
      allowedVariants: ['default', 'detailed'],
      maxTextLength: {
        title: 50,
        description: 200
      }
    },
    ComparisonTable: {
      maxItems: 10,
      maxColumns: 8,
      allowedVariants: ['default', 'wide']
    },
    SummaryConclusion: {
      requiredVariant: 'default',
      maxTextLength: {
        title: 60,
        content: 1000
      }
    }
  }
};

export const validateComponent = (
  componentType: string,
  spaceType: string,
  props: any
): ValidationResult => {
  const result: ValidationResult = {
    isValid: true,
    errors: [],
    warnings: []
  };

  const limits = COMPONENT_LIMITS[spaceType]?.[componentType];
  if (!limits) {
    result.warnings.push(`No validation rules defined for ${componentType} in ${spaceType} space`);
    return result;
  }

  // Check if component is suitable for this space
  // Note: Layout mapping validation could be added here when JSON module imports are configured

  // Validate variant
  if (limits.requiredVariant && props.variant !== limits.requiredVariant) {
    result.isValid = false;
    result.errors.push(`${componentType} must use '${limits.requiredVariant}' variant in ${spaceType} space`);
    result.suggestedFixes = { variant: limits.requiredVariant };
  }

  if (limits.allowedVariants && props.variant && !limits.allowedVariants.includes(props.variant)) {
    result.warnings.push(`Consider using one of: ${limits.allowedVariants.join(', ')} for better fit`);
  }

  // Validate item count
  if (limits.maxItems) {
    const itemCount = getItemCount(componentType, props);
    if (itemCount > limits.maxItems) {
      result.isValid = false;
      result.errors.push(`Too many items (${itemCount}). Maximum for ${spaceType}: ${limits.maxItems}`);
      result.suggestedFixes = { ...result.suggestedFixes, maxItems: limits.maxItems };
    }
  }

  // Validate column count
  if (limits.maxColumns && props.columns > limits.maxColumns) {
    result.warnings.push(`${props.columns} columns may be too many for ${spaceType}. Consider ${limits.maxColumns} max`);
  }

  // Validate text lengths
  if (limits.maxTextLength) {
    validateTextLengths(componentType, props, limits.maxTextLength, result);
  }

  return result;
};

const getItemCount = (componentType: string, props: any): number => {
  switch (componentType) {
    case 'StatGroup':
      return props.stats?.length || 0;
    case 'CalloutList':
      return props.items?.length || 0;
    case 'ActionList':
      return props.actions?.length || 0;
    case 'ComparisonTable':
      return props.entities?.length || 0;
    default:
      return 1;
  }
};

const validateTextLengths = (
  componentType: string,
  props: any,
  limits: NonNullable<ComponentLimits['maxTextLength']>,
  result: ValidationResult
) => {
  if (limits.title && props.title && props.title.length > limits.title) {
    result.warnings.push(`Title too long (${props.title.length} chars). Max: ${limits.title}`);
    result.suggestedFixes = { ...result.suggestedFixes, truncateContent: true };
  }

  // Check content in arrays
  if (componentType === 'CalloutList' && limits.content) {
    props.items?.forEach((item: any, index: number) => {
      if (item.content?.length > limits.content!) {
        result.warnings.push(`Item ${index + 1} content too long. Max: ${limits.content} chars`);
      }
    });
  }
};

// Auto-fix function that applies suggested fixes
export const autoFixComponent = (
  componentType: string,
  spaceType: string,
  props: any
): any => {
  const validation = validateComponent(componentType, spaceType, props);
  
  if (!validation.suggestedFixes) return props;

  const fixedProps = { ...props };

  // Apply variant fix
  if (validation.suggestedFixes.variant) {
    fixedProps.variant = validation.suggestedFixes.variant;
  }

  // Apply item limit fix
  if (validation.suggestedFixes.maxItems) {
    const maxItems = validation.suggestedFixes.maxItems;
    switch (componentType) {
      case 'StatGroup':
        fixedProps.stats = fixedProps.stats?.slice(0, maxItems);
        break;
      case 'CalloutList':
        fixedProps.items = fixedProps.items?.slice(0, maxItems);
        break;
      case 'ActionList':
        fixedProps.actions = fixedProps.actions?.slice(0, maxItems);
        break;
    }
  }

  // Apply text truncation
  if (validation.suggestedFixes.truncateContent) {
    const limits = COMPONENT_LIMITS[spaceType]?.[componentType]?.maxTextLength;
    if (limits?.title && fixedProps.title) {
      fixedProps.title = truncateText(fixedProps.title, limits.title);
    }
  }

  return fixedProps;
};

const truncateText = (text: string, maxLength: number): string => {
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength - 3) + '...';
};

// Validation hook for React components
export const useComponentValidation = (
  componentType: string,
  spaceType: string,
  props: any
) => {
  const validation = validateComponent(componentType, spaceType, props);
  
  useEffect(() => {
    if (!validation.isValid && process.env.NODE_ENV === 'development') {
      console.warn(`Component validation failed for ${componentType} in ${spaceType}:`, validation.errors);
    }
    if (validation.warnings.length > 0 && process.env.NODE_ENV === 'development') {
      console.info(`Component warnings for ${componentType} in ${spaceType}:`, validation.warnings);
    }
  }, [componentType, spaceType, validation]);

  return validation;
};