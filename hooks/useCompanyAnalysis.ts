/**
 * useCompanyAnalysis Hook
 * Manages company analysis state and operations
 */

import { useState, useCallback } from 'react'
import { analysisService } from '@/lib/services'
import type { CompanyAnalysis, AsyncState } from '@/types'
import toast from 'react-hot-toast'

export function useCompanyAnalysis() {
  const [state, setState] = useState<AsyncState<CompanyAnalysis>>({
    data: null,
    loading: false,
    error: null,
  })

  const [history, setHistory] = useState<CompanyAnalysis[]>([])

  /**
   * Fetch company analysis
   */
  const fetchAnalysis = useCallback(async (companyId: string, useCache = true) => {
    setState(prev => ({ ...prev, loading: true, error: null }))

    try {
      const data = await analysisService.getCompanyAnalysis(companyId, useCache)
      setState({ data, loading: false, error: null })
      return data
    } catch (error: any) {
      const errorMessage = error.message || 'Failed to fetch analysis'
      setState({ data: null, loading: false, error: errorMessage })
      toast.error(errorMessage)
      throw error
    }
  }, [])

  /**
   * Start new analysis
   */
  const startAnalysis = useCallback(async (companyId: string) => {
    setState(prev => ({ ...prev, loading: true, error: null }))

    try {
      const data = await analysisService.startAnalysis(companyId)
      setState({ data, loading: false, error: null })
      
      // Add to history
      setHistory(prev => [
        { ...data, analysisId: `analysis_${Date.now()}`, status: 'completed' },
        ...prev,
      ])
      
      toast.success('Analysis completed successfully!')
      return data
    } catch (error: any) {
      const errorMessage = error.message || 'Analysis failed'
      setState({ data: null, loading: false, error: errorMessage })
      toast.error(errorMessage)
      throw error
    }
  }, [])

  /**
   * Clear analysis data
   */
  const clearAnalysis = useCallback(() => {
    setState({ data: null, loading: false, error: null })
  }, [])

  /**
   * Clear error
   */
  const clearError = useCallback(() => {
    setState(prev => ({ ...prev, error: null }))
  }, [])

  /**
   * Export analysis
   */
  const exportAnalysis = useCallback(async (analysisId: string, format: 'pdf' | 'csv') => {
    try {
      const blob = format === 'pdf'
        ? await analysisService.exportAnalysisPDF(analysisId)
        : await analysisService.exportAnalysisCSV(analysisId)
      
      // Create download link
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `analysis_${analysisId}.${format}`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      window.URL.revokeObjectURL(url)
      
      toast.success(`Analysis exported as ${format.toUpperCase()}`)
    } catch (error: any) {
      toast.error(`Failed to export analysis: ${error.message}`)
      throw error
    }
  }, [])

  return {
    analysis: state.data,
    loading: state.loading,
    error: state.error,
    history,
    fetchAnalysis,
    startAnalysis,
    clearAnalysis,
    clearError,
    exportAnalysis,
  }
}
