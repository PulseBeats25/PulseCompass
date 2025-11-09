'use client'

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react'

export interface InvestorView {
  investor_name: string;
  score: number;
  strengths: string[];
  concerns: string[];
  assessment: string;
  key_factors: Record<string, string>;
  reasoning: string;
}

export interface Recommendation {
  rating: string;
  target_price: number;
  current_price: number;
  margin_of_safety: number;
  confidence_score: number;
  reasoning: string;
  risk_factors: string[];
  catalysts: string[];
}

export interface TranscriptSummary {
  id: string;
  company_id: string;
  quarter: string;
  year: number;
  raw_text: string;
  summary: Record<string, any>;
  integrity_score: number;
  key_quotes: string[];
  management_tone: string;
  created_at: string;
}

export interface FinancialMetrics {
  id: string;
  company_id: string;
  period: string;
  revenue: number;
  net_profit: number;
  eps: number;
  roe: number;
  roce: number;
  debt_equity: number;
  pe_ratio: number;
  ev_ebitda: number;
  pb_ratio: number;
  traffic_lights: Record<string, string>;
  created_at: string;
}

export interface InvestorViews {
  warren_buffett: InvestorView;
  benjamin_graham: InvestorView;
  peter_lynch: InvestorView;
  charlie_munger: InvestorView;
  consensus: {
    overall_score: number;
    recommendation: string;
  };
}

export interface AnalysisResult {
  company_id: string;
  company_name: string;
  transcript_summary: TranscriptSummary;
  financial_metrics: FinancialMetrics;
  investor_views: InvestorViews;
  recommendation: Recommendation;
  ratings_summary?: Record<string, string>;
  last_updated: string;
  analysis_id?: string;
  status?: 'completed' | 'failed' | 'processing';
  error?: string;
}

interface AnalysisContextType {
  analysisResult: AnalysisResult | null;
  analysisHistory: AnalysisResult[];
  isAnalyzing: boolean;
  error: string | null;
  setAnalysisResult: (result: AnalysisResult | null) => void;
  setIsAnalyzing: (analyzing: boolean) => void;
  setError: (error: string | null) => void;
  startAnalysis: (companyId: string) => Promise<void>;
  getAnalysisHistory: () => Promise<AnalysisResult[]>;
  getAnalysisById: (analysisId: string) => Promise<AnalysisResult | null>;
  clearError: () => void;
}

const AnalysisContext = createContext<AnalysisContextType | undefined>(undefined)

export function AnalysisProvider({ children }: { children: ReactNode }) {
  const [analysisResult, setAnalysisResultState] = useState<AnalysisResult | null>(null)
  const [analysisHistory, setAnalysisHistory] = useState<AnalysisResult[]>([])
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Wrapper to save to sessionStorage when setting analysis result
  const setAnalysisResult = (result: AnalysisResult | null) => {
    setAnalysisResultState(result)
    if (typeof window !== 'undefined') {
      if (result) {
        sessionStorage.setItem('analysisResult', JSON.stringify(result))
        console.log('✅ Analysis result saved to sessionStorage')
      } else {
        sessionStorage.removeItem('analysisResult')
        console.log('🗑️ Analysis result cleared from sessionStorage')
      }
    }
  }

  const clearError = () => setError(null)

  const startAnalysis = async (companyId: string) => {
    setIsAnalyzing(true)
    setError(null)
    
    try {
      // Start analysis
      const startResponse = await fetch(`http://localhost:8000/company/${companyId}/analysis`)
      if (!startResponse.ok) {
        const errorData = await startResponse.json().catch(() => ({}))
        throw new Error(errorData.detail || 'Failed to start analysis')
      }
      
      const result = await startResponse.json()
      console.log('Analysis result received:', result)
      
      // Add to history
      setAnalysisHistory(prev => [{
        ...result,
        analysis_id: `analysis_${Date.now()}`,
        status: 'completed'
      }, ...prev])
      
      setAnalysisResult(result)
      console.log('Analysis result set in context')
      return result
      
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'An unknown error occurred'
      console.error('Analysis error:', errorMessage)
      setError(errorMessage)
      throw err
    } finally {
      setIsAnalyzing(false)
    }
  }

  const getAnalysisHistory = async () => {
    try {
      // In a real app, this would fetch from your backend
      // For now, we'll just return the in-memory history
      return analysisHistory
    } catch (err) {
      console.error('Failed to fetch analysis history:', err)
      setError('Failed to load analysis history')
      return []
    }
  }

  const getAnalysisById = async (analysisId: string) => {
    try {
      // In a real app, this would fetch from your backend
      return analysisHistory.find(a => a.analysis_id === analysisId) || null
    } catch (err) {
      console.error(`Failed to fetch analysis ${analysisId}:`, err)
      setError(`Failed to load analysis ${analysisId}`)
      return null
    }
  }

  return (
    <AnalysisContext.Provider value={{
      analysisResult,
      analysisHistory,
      isAnalyzing,
      error,
      setAnalysisResult,
      setIsAnalyzing,
      setError,
      startAnalysis,
      getAnalysisHistory,
      getAnalysisById,
      clearError
    }}>
      {children}
    </AnalysisContext.Provider>
  )
}

export function useAnalysis() {
  const context = useContext(AnalysisContext)
  if (context === undefined) {
    throw new Error('useAnalysis must be used within an AnalysisProvider')
  }
  return context
}
