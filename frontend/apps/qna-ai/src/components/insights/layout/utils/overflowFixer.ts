/**
 * Overflow Fix Automation System
 * Analyzes recorded overflow issues and generates automated fixes
 */

import { OverflowRecord, ComponentFix } from './overflowTracker';
import layoutMapping from '../layout-component-mapping.json';

// Import space mapping
const spaceMapping: Record<string, string> = {
  "halfWidthTopLeft": "half_width",
  "halfWidthTopRight": "half_width",
  "quarterWidthMiddleLeft": "quarter_width", 
  "halfWidthMiddleCenter": "half_width",
  "quarterWidthMiddleRight": "quarter_width",
  "fullWidthBottom": "full_width",
  "leftPrimary": "half_width",
  "rightPrimary": "half_width",
  "leftSecondary": "half_width",
  "rightSecondary": "half_width",
  "fullWidthBottom2x5": "full_width",
  // Add more mappings as needed
};

interface FixSuggestion {
  type: 'component' | 'variant' | 'remove' | 'redesign';
  confidence: 'high' | 'medium' | 'low';
  reason: string;
  action: string;
  details?: {
    newComponent?: string;
    newVariant?: string;
    alternatives?: string[];
  };
}

export const analyzeOverflowRecord = (record: OverflowRecord): FixSuggestion[] => {
  const suggestions: FixSuggestion[] = [];
  const spaceType = record.spaceType || spaceMapping[record.spaceName] || 'unknown';
  const spaceConfig = layoutMapping.sub_layout_spaces[spaceType as keyof typeof layoutMapping.sub_layout_spaces];
  
  if (!spaceConfig) {
    return [{
      type: 'remove',
      confidence: 'low',
      reason: 'Unknown space type',
      action: `Remove component from ${record.spaceName}`,
    }];
  }

  // Check if component is explicitly unsuitable for this space
  if (spaceConfig.unsuitable_components?.includes(record.componentType)) {
    const alternatives = spaceConfig.suitable_components || [];
    suggestions.push({
      type: 'component',
      confidence: 'high',
      reason: `${record.componentType} is not suitable for ${spaceType} spaces`,
      action: `Replace with a suitable component`,
      details: {
        alternatives: alternatives.slice(0, 3), // Top 3 alternatives
        newComponent: alternatives[0], // Best alternative
      }
    });
  }

  // Check if better variant exists for this space
  const componentVariants = layoutMapping.component_variants[record.componentType as keyof typeof layoutMapping.component_variants];
  if (componentVariants) {
    const bestVariant = findBestVariantForSpace(componentVariants, spaceType);
    if (bestVariant && bestVariant !== 'default') {
      suggestions.push({
        type: 'variant',
        confidence: 'high',
        reason: `${bestVariant} variant is optimized for ${spaceType} spaces`,
        action: `Change to ${bestVariant} variant`,
        details: {
          newVariant: bestVariant
        }
      });
    }
  }

  // Quality-based suggestions
  if (record.qualityRating && record.qualityRating <= 2) {
    suggestions.push({
      type: 'redesign',
      confidence: 'medium',
      reason: `Low quality rating (${record.qualityRating}★) indicates design issues`,
      action: 'Consider redesigning component or content'
    });
  }

  // Issue-specific suggestions
  if (record.issues?.wrongVariant) {
    suggestions.push({
      type: 'variant',
      confidence: 'high',
      reason: 'User marked component as having wrong variant',
      action: 'Update component variant for this space'
    });
  }

  if (record.issues?.misplacedComponent) {
    suggestions.push({
      type: 'component',
      confidence: 'high',
      reason: 'User marked component as misplaced',
      action: 'Move to appropriate space or replace with suitable component'
    });
  }

  if (record.issues?.responsive) {
    suggestions.push({
      type: 'variant',
      confidence: 'medium',
      reason: 'Responsive behavior issues detected',
      action: 'Implement responsive variant or CSS improvements'
    });
  }

  return suggestions;
};

const findBestVariantForSpace = (variants: any, spaceType: string): string | null => {
  // Find variant that lists this space type in best_spaces
  for (const [variantName, variantConfig] of Object.entries(variants)) {
    const config = variantConfig as any;
    if (config.best_spaces?.includes(spaceType)) {
      return variantName;
    }
  }
  return null;
};

export const generateBulkFixes = (records: OverflowRecord[]): ComponentFix[] => {
  const fixes: ComponentFix[] = [];

  records.forEach(record => {
    if (record.fixed) return; // Skip already fixed items

    const suggestions = analyzeOverflowRecord(record);
    const primarySuggestion = suggestions.find(s => s.confidence === 'high') || suggestions[0];

    if (primarySuggestion) {
      fixes.push({
        id: record.id,
        type: mapSuggestionToFixType(primarySuggestion.type),
        originalComponent: record.componentType,
        suggestedComponent: primarySuggestion.details?.newComponent,
        suggestedVariant: primarySuggestion.details?.newVariant,
        reason: primarySuggestion.reason,
        confidence: primarySuggestion.confidence,
        location: `${record.layoutName} → ${record.spaceName}`,
      });
    }
  });

  return fixes;
};

const mapSuggestionToFixType = (suggestionType: string): ComponentFix['type'] => {
  switch (suggestionType) {
    case 'component': return 'replace';
    case 'variant': return 'variant';
    case 'remove': return 'remove';
    case 'redesign': return 'redesign';
    default: return 'variant';
  }
};

export const generateFixReport = (fixes: ComponentFix[]) => {
  const report = {
    totalFixes: fixes.length,
    byType: fixes.reduce((acc, fix) => {
      acc[fix.type] = (acc[fix.type] || 0) + 1;
      return acc;
    }, {} as Record<string, number>),
    byConfidence: fixes.reduce((acc, fix) => {
      acc[fix.confidence] = (acc[fix.confidence] || 0) + 1;
      return acc;
    }, {} as Record<string, number>),
    highPriorityFixes: fixes.filter(f => f.confidence === 'high'),
    componentReplacements: fixes.filter(f => f.type === 'replace'),
    variantChanges: fixes.filter(f => f.type === 'variant'),
    summary: '' as string
  };

  // Generate summary text
  const highPriority = report.highPriorityFixes.length;
  const replacements = report.componentReplacements.length;
  const variants = report.variantChanges.length;

  report.summary = `Generated ${fixes.length} fixes: ${highPriority} high-priority, ${replacements} component replacements, ${variants} variant changes. Ready for bulk application.`;

  return report;
};

export const applyFixesToRandomizer = (fixes: ComponentFix[]) => {
  // This would integrate with the layout-randomizer to update component selections
  // Implementation depends on how you want to persist the changes
  
  const updatedMappings = fixes.map(fix => ({
    layoutName: fix.location.split(' → ')[0],
    spaceName: fix.location.split(' → ')[1],
    oldComponent: fix.originalComponent,
    newComponent: fix.suggestedComponent || fix.originalComponent,
    newVariant: fix.suggestedVariant || 'default',
    fixType: fix.type
  }));

  return {
    appliedFixes: updatedMappings.length,
    mappings: updatedMappings,
    success: true,
    message: `Successfully applied ${updatedMappings.length} fixes to component mappings`
  };
};

// Helper to get component suggestions based on space
export const getComponentSuggestionsForSpace = (spaceType: string) => {
  const spaceConfig = layoutMapping.sub_layout_spaces[spaceType as keyof typeof layoutMapping.sub_layout_spaces];
  return {
    suitable: spaceConfig?.suitable_components || [],
    unsuitable: spaceConfig?.unsuitable_components || [],
    description: spaceConfig?.description || 'Unknown space type'
  };
};

// Export configuration for components
export const generateComponentConfig = (records: OverflowRecord[]) => {
  const config = {
    layoutOptimizations: {} as Record<string, any>,
    componentMappings: {} as Record<string, any>,
    variantPreferences: {} as Record<string, any>
  };

  records.forEach(record => {
    const layoutKey = `${record.layoutName}_${record.spaceName}`;
    
    // Track component performance by location
    if (!config.layoutOptimizations[layoutKey]) {
      config.layoutOptimizations[layoutKey] = {
        spaceType: record.spaceType,
        issues: 0,
        avgQuality: 0,
        problemComponents: []
      };
    }

    config.layoutOptimizations[layoutKey].issues += 1;
    if (record.qualityRating) {
      config.layoutOptimizations[layoutKey].avgQuality = 
        (config.layoutOptimizations[layoutKey].avgQuality + record.qualityRating) / 2;
    }

    if (record.qualityRating && record.qualityRating <= 2) {
      config.layoutOptimizations[layoutKey].problemComponents.push(record.componentType);
    }
  });

  return config;
};