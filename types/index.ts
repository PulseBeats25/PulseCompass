/**
 * PulseCompass Type Definitions
 * Centralized type system for type-safe development
 */

// ============================================================================
// API Response Types
// ============================================================================

export interface APIResponse<T = any> {
  success: boolean
  data?: T
  error?: APIError
  timestamp: string
}

export interface APIError {
  code: string
  message: string
  details?: Record<string, any>
}

// ============================================================================
// Company & Analysis Types
// ============================================================================

export interface Company {
  id: string
  name: string
  ticker: string
  sector?: string
  industry?: string
  marketCap?: number
  createdAt: string
  updatedAt: string
}

export interface TranscriptSummary {
  id: string
  companyId: string
  quarter: string
  year: number
  rawText: string
  summary: Record<string, any>
  integrityScore: number
  keyQuotes: string[]
  managementTone: 'positive' | 'neutral' | 'negative' | 'cautious'
  createdAt: string
}

export interface FinancialMetrics {
  id: string
  companyId: string
  period: string
  revenue: number
  netProfit: number
  eps: number
  roe: number
  roce: number
  debtEquity: number
  peRatio: number
  pbRatio: number
  evEbitda: number
  trafficLights: Record<string, TrafficLight>
  createdAt: string
}

export interface TrafficLight {
  status: 'good' | 'neutral' | 'bad'
  value: number
  threshold: {
    good: number
    bad: number
  }
  label: string
}

// ============================================================================
// Investor Analysis Types
// ============================================================================

export interface InvestorView {
  investorName: string
  score: number // 0-10
  strengths: string[]
  concerns: string[]
  assessment: string
  keyFactors: Record<string, string>
  reasoning: string
}

export interface InvestorViews {
  warrenBuffett: InvestorView
  benjaminGraham: InvestorView
  peterLynch: InvestorView
  charlieMunger: InvestorView
  consensus: {
    overallScore: number
    recommendation: RecommendationRating
  }
}

// ============================================================================
// Recommendation Types
// ============================================================================

export type RecommendationRating = 'Strong Buy' | 'Buy' | 'Hold' | 'Sell' | 'Strong Sell'

export interface Recommendation {
  rating: RecommendationRating
  targetPrice: number
  currentPrice: number
  marginOfSafety: number // 0-1 (percentage as decimal)
  confidenceScore: number // 0-1
  reasoning: string
  riskFactors: string[]
  catalysts: string[]
  timeHorizon: '3M' | '6M' | '12M' | '24M'
}

export interface CompanyAnalysis {
  companyId: string
  companyName: string
  transcriptSummary: TranscriptSummary
  financialMetrics: FinancialMetrics
  investorViews: InvestorViews
  recommendation: Recommendation
  lastUpdated: string
  analysisId?: string
  status?: 'completed' | 'failed' | 'processing'
  error?: string
}

// ============================================================================
// Portfolio Types
// ============================================================================

export interface PortfolioPosition {
  id: string
  userId: string
  companyId: string
  companyName: string
  ticker: string
  quantity: number
  buyPrice: number
  currentPrice: number
  marketValue: number
  unrealizedPnL: number
  unrealizedPnLPercent: number
  weight: number // Portfolio weight as percentage
  recommendation?: RecommendationRating
}

export interface Portfolio {
  userId: string
  totalValue: number
  dayChange: number
  dayChangePercent: number
  positions: PortfolioPosition[]
  lastUpdated: string
}

// ============================================================================
// Watchlist Types
// ============================================================================

export interface WatchlistItem {
  id: string
  userId: string
  companyId: string
  companyName: string
  ticker: string
  currentPrice: number
  dayChange: number
  dayChangePercent: number
  recommendation?: RecommendationRating
  addedAt: string
}

export interface Watchlist {
  userId: string
  items: WatchlistItem[]
  lastUpdated: string
}

// ============================================================================
// Upload Types
// ============================================================================

export interface UploadedFile {
  id: string
  name: string
  size: number
  type: 'pdf' | 'excel' | 'csv'
  status: 'uploaded' | 'processing' | 'processed' | 'failed'
  integrityScore?: number
  metricsCount?: number
  error?: string
}

export interface UploadResponse {
  success: boolean
  message: string
  files: UploadedFile[]
}

// ============================================================================
// Chart & Visualization Types
// ============================================================================

export interface ChartDataPoint {
  date: string
  value: number
  label?: string
}

export interface TimeSeriesData {
  metric: string
  data: ChartDataPoint[]
  unit: string
  trend: 'up' | 'down' | 'stable'
}

export interface ComparisonData {
  companies: Company[]
  metrics: Record<string, number[]>
  period: string
}

// ============================================================================
// User & Authentication Types
// ============================================================================

export interface User {
  id: string
  email: string
  name: string
  role: 'admin' | 'analyst' | 'viewer'
  preferences: UserPreferences
  createdAt: string
}

export interface UserPreferences {
  theme: 'light' | 'dark' | 'system'
  defaultView: 'overview' | 'analysis' | 'portfolio'
  notifications: boolean
  compactMode: boolean
}

// ============================================================================
// Filter & Search Types
// ============================================================================

export interface SearchFilters {
  query?: string
  sector?: string[]
  marketCap?: {
    min: number
    max: number
  }
  recommendation?: RecommendationRating[]
  sortBy?: 'name' | 'ticker' | 'marketCap' | 'recommendation'
  sortOrder?: 'asc' | 'desc'
}

export interface PaginationParams {
  page: number
  pageSize: number
  total?: number
}

// ============================================================================
// Utility Types
// ============================================================================

export type LoadingState = 'idle' | 'loading' | 'success' | 'error'

export interface AsyncState<T> {
  data: T | null
  loading: boolean
  error: string | null
}

export type Nullable<T> = T | null
export type Optional<T> = T | undefined
