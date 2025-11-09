/**
 * Portfolio Service
 * Business logic for portfolio operations
 */

import { apiClient } from '../api-client'
import type { Portfolio, PortfolioPosition } from '@/types'

export class PortfolioService {
  /**
   * Get user portfolio
   */
  async getPortfolio(userId?: string): Promise<Portfolio> {
    const endpoint = userId ? `/portfolio/${userId}` : '/portfolio'
    return apiClient.get<Portfolio>(endpoint)
  }

  /**
   * Add position to portfolio
   */
  async addPosition(position: Omit<PortfolioPosition, 'id' | 'marketValue' | 'unrealizedPnL' | 'unrealizedPnLPercent' | 'weight'>): Promise<PortfolioPosition> {
    return apiClient.post<PortfolioPosition>('/portfolio/positions', position)
  }

  /**
   * Update position
   */
  async updatePosition(positionId: string, updates: Partial<PortfolioPosition>): Promise<PortfolioPosition> {
    return apiClient.put<PortfolioPosition>(`/portfolio/positions/${positionId}`, updates)
  }

  /**
   * Delete position
   */
  async deletePosition(positionId: string): Promise<void> {
    return apiClient.delete(`/portfolio/positions/${positionId}`)
  }

  /**
   * Get portfolio performance
   */
  async getPerformance(userId: string, period: '1D' | '1W' | '1M' | '3M' | '1Y' | 'ALL'): Promise<any> {
    return apiClient.get(`/portfolio/${userId}/performance?period=${period}`)
  }

  /**
   * Export portfolio to CSV
   */
  async exportPortfolio(userId: string): Promise<Blob> {
    const url = `${apiClient['baseUrl']}/portfolio/${userId}/export`
    const response = await fetch(url)
    
    if (!response.ok) {
      throw new Error('Failed to export portfolio')
    }
    
    return response.blob()
  }
}

export const portfolioService = new PortfolioService()
