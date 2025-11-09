/**
 * API Service Layer
 * Centralized API calls with proper error handling
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

class APIError extends Error {
  constructor(
    message: string,
    public status: number,
    public data?: any
  ) {
    super(message)
    this.name = 'APIError'
  }
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }))
    throw new APIError(
      error.detail || `HTTP ${response.status}`,
      response.status,
      error
    )
  }
  return response.json()
}

// Upload API
export const uploadAPI = {
  async uploadPDF(files: File[], companyId?: string) {
    const formData = new FormData()
    files.forEach(file => formData.append('files', file))
    if (companyId) formData.append('company_id', companyId)

    const response = await fetch(`${API_BASE_URL}/upload/pdf`, {
      method: 'POST',
      body: formData,
    })
    return handleResponse(response)
  },

  async uploadExcel(files: File[], companyId?: string) {
    const formData = new FormData()
    files.forEach(file => formData.append('files', file))
    if (companyId) formData.append('company_id', companyId)

    const response = await fetch(`${API_BASE_URL}/upload/excel`, {
      method: 'POST',
      body: formData,
    })
    return handleResponse(response)
  },

  async testUpload(file: File) {
    const formData = new FormData()
    formData.append('file', file)

    const response = await fetch(`${API_BASE_URL}/upload/test`, {
      method: 'POST',
      body: formData,
    })
    return handleResponse(response)
  },
}

// Analysis API
export const analysisAPI = {
  async getCompanyAnalysis(companyId: string) {
    const response = await fetch(`${API_BASE_URL}/company/${companyId}/analysis`)
    return handleResponse(response)
  },

  async semanticQuery(query: string, companyId?: string) {
    const params = new URLSearchParams({ query })
    if (companyId) params.append('company_id', companyId)

    const response = await fetch(`${API_BASE_URL}/company/query?${params}`, {
      method: 'POST',
    })
    return handleResponse(response)
  },
}

// Portfolio API
export const portfolioAPI = {
  async getDefaultPortfolio() {
    const response = await fetch(`${API_BASE_URL}/portfolio`)
    return handleResponse(response)
  },

  async getUserPortfolio(userId: string) {
    const response = await fetch(`${API_BASE_URL}/portfolio/${userId}`)
    return handleResponse(response)
  },

  async getWatchlist(userId: string) {
    const response = await fetch(`${API_BASE_URL}/portfolio/watchlist/${userId}`)
    return handleResponse(response)
  },
}

// Companies API
export const companiesAPI = {
  async getDefaultWatchlist() {
    const response = await fetch(`${API_BASE_URL}/companies/watchlist`)
    return handleResponse(response)
  },

  async createCompany(name: string, ticker: string, sector?: string) {
    const params = new URLSearchParams({ name, ticker })
    if (sector) params.append('sector', sector)

    const response = await fetch(`${API_BASE_URL}/companies?${params}`, {
      method: 'POST',
    })
    return handleResponse(response)
  },
}

// Health API
export const healthAPI = {
  async check() {
    const response = await fetch(`${API_BASE_URL}/health`)
    return handleResponse(response)
  },
}

export { APIError }
