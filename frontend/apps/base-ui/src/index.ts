/**
 * Base UI - Canonical Finance-Semantic Blocks
 *
 * This package exports canonical blocks that are thin React wrappers
 * around Tremor components, designed to answer specific financial questions.
 */

// Note: CSS imports are handled separately via the "./css" export in package.json
// Styles should be imported directly: import '@ui-gen/base-ui/css'

// Export all canonical blocks
export * from './blocks';

// Re-export types from Tremor for convenience
export type {
    AvailableChartColorsKeys,
} from './lib/chartUtils';