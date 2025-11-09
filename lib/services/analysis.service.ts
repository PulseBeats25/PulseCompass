/**
 * Analysis Service
 * Business logic for company analysis operations
 */

import { apiClient } from '../api-client'
import type { CompanyAnalysis, UploadResponse } from '@/types'

export class AnalysisService {
  /**
   * Upload PDF transcript files
   */
  async uploadPDF(files: File[], companyId?: string): Promise<UploadResponse> {
    const formData = new FormData()
    files.forEach(file => formData.append('files', file))
    if (companyId) {
      formData.append('company_id', companyId)
    }

    return apiClient.postFormData<UploadResponse>('/upload/pdf', formData)
  }

  /**
   * Upload Excel/CSV financial files
   */
  async uploadExcel(files: File[], companyId?: string): Promise<UploadResponse> {
    const formData = new FormData()
    files.forEach(file => formData.append('files', file))
    if (companyId) {
      formData.append('company_id', companyId)
    }

    return apiClient.postFormData<UploadResponse>('/upload/excel', formData)
  }

  /**
   * Get company analysis
   */
  async getCompanyAnalysis(companyId: string, useCache = true): Promise<CompanyAnalysis> {
    return apiClient.get<CompanyAnalysis>(`/company/${companyId}/analysis`, useCache)
  }

  /**
   * Start analysis for a company
   */
  async startAnalysis(companyId: string): Promise<CompanyAnalysis> {
    // Clear cache for this company
    apiClient.clearCache(`/company/${companyId}`)
    
    return this.getCompanyAnalysis(companyId, false)
  }

  /**
   * Get analysis history
   */
  async getAnalysisHistory(userId?: string): Promise<CompanyAnalysis[]> {
    const endpoint = userId ? `/analysis/history?user_id=${userId}` : '/analysis/history'
    return apiClient.get<CompanyAnalysis[]>(endpoint)
  }

  /**
   * Get analysis by ID
   */
  async getAnalysisById(analysisId: string): Promise<CompanyAnalysis> {
    return apiClient.get<CompanyAnalysis>(`/analysis/${analysisId}`)
  }

  /**
   * Delete analysis
   */
  async deleteAnalysis(analysisId: string): Promise<void> {
    return apiClient.delete(`/analysis/${analysisId}`)
  }

  /**
   * Export analysis to PDF
   */
  async exportAnalysisPDF(analysisId: string): Promise<Blob> {
    const url = `${apiClient['baseUrl']}/analysis/${analysisId}/export/pdf`
    const response = await fetch(url)
    
    if (!response.ok) {
      throw new Error('Failed to export analysis')
    }
    
    return response.blob()
  }

  /**
   * Export analysis to CSV
   */
  async exportAnalysisCSV(analysisId: string): Promise<Blob> {
    const url = `${apiClient['baseUrl']}/analysis/${analysisId}/export/csv`
    const response = await fetch(url)
    
    if (!response.ok) {
      throw new Error('Failed to export analysis')
    }
    
    return response.blob()
  }
}

export const analysisService = new AnalysisService()
