/**
 * API Client
 * Type-safe HTTP client with error handling, retries, and caching
 */

import config from './config'
import type { APIResponse, APIError } from '@/types'

class APIClient {
  private baseUrl: string
  private timeout: number
  private retryAttempts: number
  private cache: Map<string, { data: any; timestamp: number }>

  constructor() {
    this.baseUrl = config.api.baseUrl
    this.timeout = config.api.timeout
    this.retryAttempts = config.api.retryAttempts
    this.cache = new Map()
  }

  /**
   * Generic request method with retry logic
   */
  private async request<T>(
    endpoint: string,
    options: RequestInit = {},
    attempt = 1
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`
    const controller = new AbortController()
    const timeoutId = setTimeout(() => controller.abort(), this.timeout)

    try {
      const response = await fetch(url, {
        ...options,
        signal: controller.signal,
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
      })

      clearTimeout(timeoutId)

      if (!response.ok) {
        const error = await this.handleErrorResponse(response)
        throw error
      }

      const data = await response.json()
      return data
    } catch (error) {
      clearTimeout(timeoutId)

      // Retry logic for network errors
      if (attempt < this.retryAttempts && this.isRetryableError(error)) {
        await this.delay(Math.pow(2, attempt) * 1000) // Exponential backoff
        return this.request<T>(endpoint, options, attempt + 1)
      }

      throw this.normalizeError(error)
    }
  }

  /**
   * GET request with optional caching
   */
  async get<T>(endpoint: string, useCache = true): Promise<T> {
    const cacheKey = `GET:${endpoint}`

    // Check cache
    if (useCache && config.performance.enableCaching) {
      const cached = this.cache.get(cacheKey)
      if (cached && Date.now() - cached.timestamp < config.performance.cacheTimeout) {
        return cached.data
      }
    }

    const data = await this.request<T>(endpoint, { method: 'GET' })

    // Store in cache
    if (useCache && config.performance.enableCaching) {
      this.cache.set(cacheKey, { data, timestamp: Date.now() })
    }

    return data
  }

  /**
   * POST request
   */
  async post<T>(endpoint: string, body?: any): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'POST',
      body: body ? JSON.stringify(body) : undefined,
    })
  }

  /**
   * POST request with FormData (for file uploads)
   */
  async postFormData<T>(endpoint: string, formData: FormData): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`
    const controller = new AbortController()
    const timeoutId = setTimeout(() => controller.abort(), this.timeout)

    try {
      const response = await fetch(url, {
        method: 'POST',
        body: formData,
        signal: controller.signal,
      })

      clearTimeout(timeoutId)

      if (!response.ok) {
        const error = await this.handleErrorResponse(response)
        throw error
      }

      return await response.json()
    } catch (error) {
      clearTimeout(timeoutId)
      throw this.normalizeError(error)
    }
  }

  /**
   * PUT request
   */
  async put<T>(endpoint: string, body?: any): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'PUT',
      body: body ? JSON.stringify(body) : undefined,
    })
  }

  /**
   * DELETE request
   */
  async delete<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, { method: 'DELETE' })
  }

  /**
   * Clear cache
   */
  clearCache(pattern?: string): void {
    if (pattern) {
      for (const key of this.cache.keys()) {
        if (key.includes(pattern)) {
          this.cache.delete(key)
        }
      }
    } else {
      this.cache.clear()
    }
  }

  /**
   * Handle error responses
   */
  private async handleErrorResponse(response: Response): Promise<APIError> {
    let errorData: any
    try {
      errorData = await response.json()
    } catch {
      errorData = { message: response.statusText }
    }

    return {
      code: `HTTP_${response.status}`,
      message: errorData.detail || errorData.message || 'An error occurred',
      details: errorData,
    }
  }

  /**
   * Normalize errors to APIError format
   */
  private normalizeError(error: any): APIError {
    if (error.name === 'AbortError') {
      return {
        code: 'TIMEOUT',
        message: 'Request timeout. Please try again.',
      }
    }

    if (error.code && error.message) {
      return error as APIError
    }

    return {
      code: 'UNKNOWN_ERROR',
      message: error.message || 'An unexpected error occurred',
      details: error,
    }
  }

  /**
   * Check if error is retryable
   */
  private isRetryableError(error: any): boolean {
    return (
      error.name === 'AbortError' ||
      error.code === 'ECONNRESET' ||
      error.code === 'ETIMEDOUT' ||
      (error.code && error.code.startsWith('HTTP_5'))
    )
  }

  /**
   * Delay helper for retry logic
   */
  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms))
  }
}

// Export singleton instance
export const apiClient = new APIClient()

// Export class for testing
export default APIClient
