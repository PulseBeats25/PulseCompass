/**
 * Application Configuration
 * Centralized configuration management with type safety
 */

interface AppConfig {
  api: {
    baseUrl: string
    timeout: number
    retryAttempts: number
  }
  features: {
    darkMode: boolean
    realTimeUpdates: boolean
    exportData: boolean
    multiCompanyComparison: boolean
  }
  ui: {
    itemsPerPage: number
    chartRefreshInterval: number
    toastDuration: number
  }
  performance: {
    enableCaching: boolean
    cacheTimeout: number
    enableVirtualization: boolean
  }
}

const config: AppConfig = {
  api: {
    baseUrl: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
    timeout: 30000, // 30 seconds
    retryAttempts: 3,
  },
  features: {
    darkMode: true,
    realTimeUpdates: false, // Enable when WebSocket is implemented
    exportData: true,
    multiCompanyComparison: true,
  },
  ui: {
    itemsPerPage: 20,
    chartRefreshInterval: 60000, // 1 minute
    toastDuration: 4000, // 4 seconds
  },
  performance: {
    enableCaching: true,
    cacheTimeout: 300000, // 5 minutes
    enableVirtualization: true,
  },
}

export default config
