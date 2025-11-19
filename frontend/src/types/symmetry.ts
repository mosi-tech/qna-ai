// Type definitions for position symmetry analysis components

export interface PositionSymmetryData {
  symbol: string;
  name: string;
  symmetryScore: number; // 0-1, where 1 is perfectly symmetric
  upDays: number;
  downDays: number;
  upDayAvg: number; // Average percentage gain on up days
  downDayAvg: number; // Average percentage loss on down days
  totalDays: number;
  volatility: number;
  beta: number;
}

export interface PortfolioSymmetryData {
  totalPositions: number;
  avgSymmetryScore: number;
  mostSymmetricPosition: string;
  leastSymmetricPosition: string;
  symmetricPositions: number; // Count of positions with score >= 0.7
  asymmetricPositions: number; // Count of positions with score < 0.5
  portfolioUpDays: number;
  portfolioDownDays: number;
  overallBalance: number; // Portfolio-level up/down balance metric
}

export interface SymmetryAnalysisProps {
  data: PositionSymmetryData | PortfolioSymmetryData | PositionSymmetryData[];
  onApprove?: () => void;
  onDisapprove?: () => void;
  variant?: 'default' | 'compact' | 'detailed';
}

export interface SymmetryRankingItem extends PositionSymmetryData {
  rank: number;
  symmetryCategory: 'Highly Symmetric' | 'Moderately Symmetric' | 'Somewhat Symmetric' | 'Asymmetric';
}