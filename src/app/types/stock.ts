export interface Stock {
  id: string;
  code: string;
  name: string;
  price: number;
  change: number;
  changePercent: number;
  volume: number;
  marketCap: number;
}

export interface Position {
  id: string;
  stockCode: string;
  stockName: string;
  shares: number;
  buyPrice: number;
  currentPrice: number;
  buyDate: string;
  profit: number;
  profitPercent: number;
  totalValue: number;
  cost: number;
}

export interface DiagnosisResult {
  stockCode: string;
  stockName: string;
  technicalScore: number;
  fundamentalScore: number;
  marketScore: number;
  overallScore: number;
  rating: 'excellent' | 'good' | 'neutral' | 'poor' | 'risk';
  strengths: string[];
  weaknesses: string[];
  recommendation: string;
}

export interface AIRecommendation {
  type: 'buy' | 'sell' | 'hold';
  confidence: number;
  reason: string;
  targetPrice?: number;
  stopLoss?: number;
  timeframe: string;
}

export interface RiskAnalysis {
  level: 'low' | 'medium' | 'high' | 'extreme';
  score: number;
  factors: Array<{
    name: string;
    impact: number;
    description: string;
  }>;
}

export interface ChanTheoryAnalysis {
  trend: 'up' | 'down' | 'sideways';
  level: number;
  pivots: Array<{
    type: 'high' | 'low';
    price: number;
    date: string;
  }>;
  segments: string[];
  buyPoints: Array<{ price: number; date: string; confidence: number }>;
  sellPoints: Array<{ price: number; date: string; confidence: number }>;
}

export interface LivermoreAnalysis {
  marketPhase: 'accumulation' | 'markup' | 'distribution' | 'markdown';
  pivotalPoints: Array<{ price: number; type: string }>;
  trendStrength: number;
  volumeAnalysis: string;
  recommendation: string;
}
