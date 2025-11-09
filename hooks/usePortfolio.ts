'use client'

import { useState, useEffect } from 'react'
import { portfolioAPI } from '@/services/api'
import type { AsyncState } from '@/types'

interface PortfolioData {
  totalValue: number
  dayChange: number
  dayChangePercent: number
  positions: number
  alerts: number
}

export function usePortfolio(userId?: string) {
  const [state, setState] = useState<AsyncState<PortfolioData>>({
    data: null,
    loading: true,
    error: null,
  })

  useEffect(() => {
    const fetchPortfolio = async () => {
      try {
        setState(prev => ({ ...prev, loading: true, error: null }))
        
        const data = userId
          ? await portfolioAPI.getUserPortfolio(userId)
          : await portfolioAPI.getDefaultPortfolio()
        
        setState({ data, loading: false, error: null })
      } catch (error) {
        setState({
          data: null,
          loading: false,
          error: error instanceof Error ? error.message : 'Failed to fetch portfolio',
        })
      }
    }

    fetchPortfolio()
  }, [userId])

  const refetch = async () => {
    try {
      setState(prev => ({ ...prev, loading: true }))
      
      const data = userId
        ? await portfolioAPI.getUserPortfolio(userId)
        : await portfolioAPI.getDefaultPortfolio()
      
      setState({ data, loading: false, error: null })
    } catch (error) {
      setState(prev => ({
        ...prev,
        loading: false,
        error: error instanceof Error ? error.message : 'Failed to fetch portfolio',
      }))
    }
  }

  return {
    ...state,
    refetch,
  }
}
