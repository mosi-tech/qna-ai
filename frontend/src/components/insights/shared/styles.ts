/**
 * Unified Style Configuration for Insight Components
 * 
 * Professional color palette using slate as the primary neutral with semantic colors
 * that are vibrant enough to be engaging but professional enough for business use.
 */

export const insightStyles = {
  // Base surfaces - using slate for more modern, professional feel
  surface: {
    primary: 'bg-white',
    secondary: 'bg-slate-50', 
    tertiary: 'bg-slate-100',
    elevated: 'bg-white border border-slate-200 shadow-sm'
  },
  
  // Borders - consistent slate palette
  border: {
    light: 'border-slate-200',
    medium: 'border-slate-300', 
    dark: 'border-slate-400',
    divider: 'border-t border-slate-200'
  },
  
  // Text hierarchy - clear contrast levels
  text: {
    primary: 'text-slate-900',      // Main headings, primary content
    secondary: 'text-slate-700',    // Subheadings, secondary content  
    tertiary: 'text-slate-500',     // Labels, captions
    quaternary: 'text-slate-400',   // Placeholders, disabled text
    inverse: 'text-white'
  },
  
  // Semantic colors - professional but vibrant
  status: {
    success: {
      bg: 'bg-emerald-50',
      bgMedium: 'bg-emerald-100',
      text: 'text-emerald-800',
      textLight: 'text-emerald-700',
      border: 'border-emerald-200',
      accent: 'bg-emerald-500',
      hover: 'hover:bg-emerald-100'
    },
    warning: {
      bg: 'bg-amber-50',
      bgMedium: 'bg-amber-100', 
      text: 'text-amber-800',
      textLight: 'text-amber-700',
      border: 'border-amber-200',
      accent: 'bg-amber-500',
      hover: 'hover:bg-amber-100'
    },
    error: {
      bg: 'bg-rose-50',
      bgMedium: 'bg-rose-100',
      text: 'text-rose-800', 
      textLight: 'text-rose-700',
      border: 'border-rose-200',
      accent: 'bg-rose-500',
      hover: 'hover:bg-rose-100'
    },
    info: {
      bg: 'bg-sky-50',
      bgMedium: 'bg-sky-100',
      text: 'text-sky-800',
      textLight: 'text-sky-700',
      border: 'border-sky-200',
      accent: 'bg-sky-500',
      hover: 'hover:bg-sky-100'
    },
    neutral: {
      bg: 'bg-slate-50',
      bgMedium: 'bg-slate-100',
      text: 'text-slate-700',
      textLight: 'text-slate-600',
      border: 'border-slate-200',
      accent: 'bg-slate-500',
      hover: 'hover:bg-slate-100'
    }
  },
  
  // Interactive elements
  button: {
    // Standard approve/disapprove buttons
    approve: {
      base: 'px-4 py-2 bg-emerald-50 text-emerald-700 rounded-lg hover:bg-emerald-100 transition-colors text-sm font-medium',
      compact: 'px-3 py-1.5 bg-emerald-50 text-emerald-700 rounded-md hover:bg-emerald-100 transition-colors text-sm'
    },
    disapprove: {
      base: 'px-4 py-2 bg-rose-50 text-rose-700 rounded-lg hover:bg-rose-100 transition-colors text-sm font-medium',
      compact: 'px-3 py-1.5 bg-rose-50 text-rose-700 rounded-md hover:bg-rose-100 transition-colors text-sm'
    },
    // Primary action buttons
    primary: 'px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors text-sm font-medium',
    secondary: 'px-4 py-2 bg-slate-100 text-slate-700 rounded-lg hover:bg-slate-200 transition-colors text-sm font-medium'
  },
  
  // Responsive typography
  typography: {
    // Component headings
    h1: 'text-xl md:text-2xl lg:text-3xl font-bold text-slate-900',
    h2: 'text-lg md:text-xl lg:text-2xl font-semibold text-slate-900', 
    h3: 'text-base md:text-lg lg:text-xl font-medium text-slate-900',
    h4: 'text-sm md:text-base font-medium text-slate-900',
    
    // Body text
    body: 'text-sm md:text-base text-slate-700',
    caption: 'text-xs md:text-sm text-slate-500',
    
    // Special text
    stat: 'text-2xl md:text-3xl lg:text-4xl font-bold text-slate-900',
    statSmall: 'text-lg md:text-xl lg:text-2xl font-semibold text-slate-900'
  },
  
  // Responsive spacing
  spacing: {
    // Component padding
    component: 'p-4 md:p-6',
    componentCompact: 'p-3 md:p-4',
    section: 'p-4 md:p-6 lg:p-8',
    
    // Gaps and margins
    gap: 'gap-4 md:gap-6',
    gapSmall: 'gap-2 md:gap-3',
    margin: 'mb-4 md:mb-6',
    marginSmall: 'mb-2 md:mb-3'
  },
  
  // Responsive grid layouts
  grid: {
    cols2: 'grid-cols-1 sm:grid-cols-2',
    cols3: 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-3',
    cols4: 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-4',
    cols6: 'grid-cols-2 sm:grid-cols-3 lg:grid-cols-6'
  },
  
  // Common component patterns
  card: {
    base: 'bg-white border border-slate-200 rounded-lg shadow-sm',
    elevated: 'bg-white border border-slate-200 rounded-lg shadow-md',
    padding: 'p-4 md:p-6'
  },
  
  // Progress/loading indicators
  progress: {
    bg: 'bg-slate-200',
    fill: 'bg-indigo-500',
    success: 'bg-emerald-500',
    warning: 'bg-amber-500',
    error: 'bg-rose-500'
  }
} as const;

// Utility function to combine classes
export const cn = (...classes: (string | undefined | null | boolean)[]) => {
  return classes.filter(Boolean).join(' ');
};