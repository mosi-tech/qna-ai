/**
 * Overflow Tracking System
 * Records component overflow issues, quality ratings, and notes for bulk fixing
 */

export interface OverflowRecord {
  id: string;
  componentName: string;
  componentType: string; // StatGroup, Section, etc.
  layoutName: string; // Layout1, Layout2, etc.
  spaceName: string; // halfWidthTopLeft, quarterWidth, etc.
  spaceType: string; // quarter_width, half_width, etc.
  timestamp: number;
  fixed?: boolean;
  
  // Quality tracking
  hasOverflow?: boolean;
  qualityRating?: 1 | 2 | 3 | 4 | 5; // 1 = poor, 5 = excellent
  userNotes?: string;
  
  // Issue categories
  issues?: {
    overflow?: boolean;
    poorDesign?: boolean;
    wrongVariant?: boolean;
    misplacedComponent?: boolean;
    responsive?: boolean;
    other?: boolean;
  };
}

export interface ComponentFix {
  id: string;
  type: 'replace' | 'variant' | 'remove' | 'redesign';
  originalComponent: string;
  suggestedComponent?: string;
  suggestedVariant?: string;
  reason: string;
  confidence: 'high' | 'medium' | 'low';
  location: string;
  basedOnRating?: boolean;
}

const STORAGE_KEY = 'component-overflow-data';

// Storage utilities
export const saveOverflowData = (records: OverflowRecord[]): void => {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(records));
  } catch (error) {
    console.error('Failed to save overflow data:', error);
  }
};

export const getOverflowData = (): OverflowRecord[] => {
  try {
    const data = localStorage.getItem(STORAGE_KEY);
    return data ? JSON.parse(data) : [];
  } catch (error) {
    console.error('Failed to load overflow data:', error);
    return [];
  }
};

export const addOverflowRecord = (record: Omit<OverflowRecord, 'id' | 'timestamp'>): void => {
  const existingData = getOverflowData();
  
  // Check if this exact combination already exists
  const existingIndex = existingData.findIndex(
    existing => 
      existing.componentName === record.componentName &&
      existing.layoutName === record.layoutName &&
      existing.spaceName === record.spaceName
  );

  if (existingIndex !== -1) {
    // Update existing record instead of creating duplicate
    existingData[existingIndex] = {
      ...existingData[existingIndex],
      ...record,
      timestamp: Date.now(),
      fixed: false, // Reset fixed status
    };
  } else {
    const newRecord: OverflowRecord = {
      ...record,
      id: `${record.layoutName}-${record.spaceName}-${record.componentName}-${Date.now()}`,
      timestamp: Date.now(),
    };
    existingData.push(newRecord);
  }

  saveOverflowData(existingData);
};

export const updateOverflowRecord = (recordId: string, updates: Partial<OverflowRecord>): void => {
  const data = getOverflowData();
  const record = data.find(r => r.id === recordId);
  if (record) {
    Object.assign(record, updates);
    record.timestamp = Date.now(); // Update timestamp
    saveOverflowData(data);
  }
};

export const markRecordAsFixed = (recordId: string): void => {
  updateOverflowRecord(recordId, { fixed: true });
};

export const removeOverflowRecord = (recordId: string): void => {
  const data = getOverflowData();
  const filteredData = data.filter(r => r.id !== recordId);
  saveOverflowData(filteredData);
};

export const clearAllOverflowData = (): void => {
  localStorage.removeItem(STORAGE_KEY);
};

export const getOverflowStats = () => {
  const data = getOverflowData();
  return {
    total: data.length,
    fixed: data.filter(r => r.fixed).length,
    unfixed: data.filter(r => !r.fixed).length,
    hasOverflow: data.filter(r => r.hasOverflow).length,
    
    // Quality stats
    qualityStats: {
      excellent: data.filter(r => r.qualityRating === 5).length,
      good: data.filter(r => r.qualityRating === 4).length,
      average: data.filter(r => r.qualityRating === 3).length,
      poor: data.filter(r => r.qualityRating === 2).length,
      veryPoor: data.filter(r => r.qualityRating === 1).length,
      avgRating: data.length > 0 ? 
        data.reduce((sum, r) => sum + (r.qualityRating || 0), 0) / data.filter(r => r.qualityRating).length 
        : 0,
    },
    
    // Issue breakdown
    issueStats: {
      overflow: data.filter(r => r.issues?.overflow).length,
      poorDesign: data.filter(r => r.issues?.poorDesign).length,
      wrongVariant: data.filter(r => r.issues?.wrongVariant).length,
      misplacedComponent: data.filter(r => r.issues?.misplacedComponent).length,
      responsive: data.filter(r => r.issues?.responsive).length,
      other: data.filter(r => r.issues?.other).length,
    },
    
    byLayout: data.reduce((acc, record) => {
      acc[record.layoutName] = (acc[record.layoutName] || 0) + 1;
      return acc;
    }, {} as Record<string, number>),
    
    byComponent: data.reduce((acc, record) => {
      acc[record.componentType] = (acc[record.componentType] || 0) + 1;
      return acc;
    }, {} as Record<string, number>),
    
    bySpace: data.reduce((acc, record) => {
      acc[record.spaceType] = (acc[record.spaceType] || 0) + 1;
      return acc;
    }, {} as Record<string, number>)
  };
};

// Export overflow data for analysis
export const exportOverflowData = () => {
  const data = getOverflowData();
  const stats = getOverflowStats();
  
  const exportData = {
    exportDate: new Date().toISOString(),
    records: data,
    statistics: stats,
    summary: {
      totalIssues: data.length,
      averageQuality: stats.qualityStats.avgRating.toFixed(1),
      topIssues: Object.entries(stats.issueStats)
        .sort(([,a], [,b]) => b - a)
        .slice(0, 3)
        .map(([issue, count]) => ({ issue, count })),
      problematicLayouts: Object.entries(stats.byLayout)
        .sort(([,a], [,b]) => b - a)
        .slice(0, 3)
        .map(([layout, count]) => ({ layout, count })),
    }
  };
  
  return exportData;
};

// Helper to get records for specific layout
export const getRecordsForLayout = (layoutName: string): OverflowRecord[] => {
  return getOverflowData().filter(record => record.layoutName === layoutName);
};

// Helper to get low quality components (rating 1-2)
export const getLowQualityRecords = (): OverflowRecord[] => {
  return getOverflowData().filter(record => 
    record.qualityRating && record.qualityRating <= 2
  );
};