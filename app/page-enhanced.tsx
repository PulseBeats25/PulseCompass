'use client'

import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  TrendingUp, 
  TrendingDown,
  BarChart3, 
  Target,
  Users,
  AlertCircle,
  DollarSign,
  Activity,
  Briefcase
} from 'lucide-react'
import Header from '@/components/Header'
import MetricCard from '@/components/MetricCard'
import EnhancedDataTable, { Column } from '@/components/EnhancedDataTable'
import ComparisonView from '@/components/ComparisonView'
import UploadBox from '@/components/UploadBox'
import { AnalysisProvider, useAnalysis } from '@/contexts/AnalysisContext'

interface PortfolioPosition {
  symbol: string
  name: string
  shares: number
  avgPrice: number
  currentPrice: number
  value: number
  change: number
  changePercent: number
}

interface Alert {
  id: number
  type: 'warning' | 'info' | 'error'
  message: string
  date: string
}

function HomePageContent() {
  const [activeTab, setActiveTab] = useState('overview')
  const { analysisResult, isAnalyzing, error } = useAnalysis()
  
  const [portfolioData, setPortfolioData] = useState<any>(null)
  const [watchlistCompanies, setWatchlistCompanies] = useState<any[]>([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const fetchData = async () => {
      try {
        setIsLoading(true)
        
        // Fetch portfolio data
        const portfolioResponse = await fetch('http://localhost:8000/portfolio')
        if (portfolioResponse.ok) {
          const portfolio = await portfolioResponse.json()
          setPortfolioData(portfolio)
        }

        // Fetch watchlist companies
        const watchlistResponse = await fetch('http://localhost:8000/companies/watchlist')
        if (watchlistResponse.ok) {
          const watchlist = await watchlistResponse.json()
          setWatchlistCompanies(watchlist)
        }
      } catch (error) {
        console.error('Error fetching data:', error)
      } finally {
        setIsLoading(false)
      }
    }

    fetchData()
  }, [])

  // Table columns for positions
  const positionColumns: Column<PortfolioPosition>[] = [
    {
      key: 'symbol',
      label: 'Symbol',
      sortable: true,
      format: (value, row) => (
        <div>
          <div className="font-semibold text-neutral-900 dark:text-dark-text">{value}</div>
          <div className="text-xs text-neutral-500 dark:text-neutral-400">{row.name}</div>
        </div>
      ),
    },
    {
      key: 'shares',
      label: 'Shares',
      sortable: true,
      align: 'right',
      format: (value) => value.toLocaleString(),
    },
    {
      key: 'avgPrice',
      label: 'Avg Price',
      sortable: true,
      align: 'right',
      format: (value) => `$${value.toFixed(2)}`,
    },
    {
      key: 'currentPrice',
      label: 'Current',
      sortable: true,
      align: 'right',
      format: (value) => `$${value.toFixed(2)}`,
    },
    {
      key: 'value',
      label: 'Value',
      sortable: true,
      align: 'right',
      format: (value) => `$${value.toLocaleString()}`,
      className: 'font-semibold',
    },
    {
      key: 'changePercent',
      label: 'Change',
      sortable: true,
      align: 'right',
      format: (value, row) => (
        <div className="flex items-center justify-end gap-1">
          {value >= 0 ? (
            <TrendingUp className="w-4 h-4 text-success-600 dark:text-success-400" />
          ) : (
            <TrendingDown className="w-4 h-4 text-danger-600 dark:text-danger-400" />
          )}
          <span className={value >= 0 ? 'text-success-600 dark:text-success-400' : 'text-danger-600 dark:text-danger-400'}>
            {value >= 0 ? '+' : ''}{value.toFixed(2)}%
          </span>
        </div>
      ),
    },
  ]

  // Mock data for demonstration
  const mockPositions: PortfolioPosition[] = [
    {
      symbol: 'AAPL',
      name: 'Apple Inc.',
      shares: 100,
      avgPrice: 150.00,
      currentPrice: 175.50,
      value: 17550,
      change: 2550,
      changePercent: 17.00,
    },
    {
      symbol: 'MSFT',
      name: 'Microsoft Corp.',
      shares: 50,
      avgPrice: 280.00,
      currentPrice: 310.25,
      value: 15512.50,
      change: 1512.50,
      changePercent: 10.80,
    },
    {
      symbol: 'GOOGL',
      name: 'Alphabet Inc.',
      shares: 75,
      avgPrice: 120.00,
      currentPrice: 118.75,
      value: 8906.25,
      change: -93.75,
      changePercent: -1.04,
    },
  ]

  const mockComparisonData = [
    {
      symbol: 'AAPL',
      name: 'Apple Inc.',
      price: 175.50,
      marketCap: 2800000000000,
      peRatio: 28.5,
      pbRatio: 45.2,
      debtToEquity: 1.73,
      roe: 147.4,
      dividendYield: 0.52,
      revenue: 394328000000,
      netIncome: 96995000000,
      change: 2.50,
      changePercent: 1.45,
    },
    {
      symbol: 'MSFT',
      name: 'Microsoft Corp.',
      price: 310.25,
      marketCap: 2300000000000,
      peRatio: 32.1,
      pbRatio: 12.8,
      debtToEquity: 0.35,
      roe: 43.7,
      dividendYield: 0.89,
      revenue: 211915000000,
      netIncome: 72361000000,
      change: 3.75,
      changePercent: 1.22,
    },
  ]

  return (
    <div className="min-h-screen bg-neutral-50 dark:bg-dark-bg">
      <Header />

      <main className="container mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Hero Metrics */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-8"
        >
          <MetricCard
            title="Portfolio Value"
            value={portfolioData?.totalValue || 125000}
            change={portfolioData?.dayChangePercent || 1.01}
            changeLabel="Today"
            icon={DollarSign}
            format="currency"
            color="primary"
            loading={isLoading}
          />
          <MetricCard
            title="Total Gain"
            value={portfolioData?.totalGain || 12500}
            change={10.5}
            changeLabel="All time"
            icon={TrendingUp}
            format="currency"
            color="success"
            loading={isLoading}
          />
          <MetricCard
            title="Active Positions"
            value={portfolioData?.positions?.length || mockPositions.length}
            subtitle="Across portfolio"
            icon={Briefcase}
            format="number"
            color="neutral"
            loading={isLoading}
          />
          <MetricCard
            title="Watchlist"
            value={watchlistCompanies?.length || 8}
            subtitle="Companies tracked"
            icon={Users}
            format="number"
            color="warning"
            loading={isLoading}
          />
        </motion.div>

        {/* Tabs */}
        <div className="mb-8">
          <div className="border-b border-neutral-200 dark:border-dark-border">
            <nav className="flex gap-8">
              {[
                { id: 'overview', label: 'Overview', icon: BarChart3 },
                { id: 'positions', label: 'Positions', icon: Target },
                { id: 'comparison', label: 'Comparison', icon: Activity },
                { id: 'upload', label: 'Upload', icon: TrendingUp },
              ].map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`
                    flex items-center gap-2 px-1 py-4 border-b-2 font-medium text-sm transition-colors
                    ${activeTab === tab.id
                      ? 'border-primary-600 text-primary-600 dark:text-primary-400'
                      : 'border-transparent text-neutral-600 dark:text-neutral-400 hover:text-neutral-900 dark:hover:text-white hover:border-neutral-300'
                    }
                  `}
                >
                  <tab.icon className="w-4 h-4" />
                  {tab.label}
                </button>
              ))}
            </nav>
          </div>
        </div>

        {/* Tab Content */}
        <AnimatePresence mode="wait">
          {activeTab === 'overview' && (
            <motion.div
              key="overview"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="space-y-8"
            >
              {/* Recent Activity */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                <div className="card">
                  <h3 className="text-lg font-semibold text-neutral-900 dark:text-dark-text mb-4">
                    Recent Activity
                  </h3>
                  <div className="space-y-3">
                    {[1, 2, 3].map((i) => (
                      <div key={i} className="flex items-center gap-3 p-3 rounded-lg hover:bg-neutral-50 dark:hover:bg-neutral-800 transition-colors">
                        <div className="w-10 h-10 rounded-full bg-primary-100 dark:bg-primary-950/30 flex items-center justify-center">
                          <TrendingUp className="w-5 h-5 text-primary-600 dark:text-primary-400" />
                        </div>
                        <div className="flex-1">
                          <p className="text-sm font-medium text-neutral-900 dark:text-dark-text">
                            Bought 10 shares of AAPL
                          </p>
                          <p className="text-xs text-neutral-500 dark:text-neutral-400">
                            2 hours ago
                          </p>
                        </div>
                        <span className="text-sm font-semibold text-success-600 dark:text-success-400">
                          +$1,755
                        </span>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="card">
                  <h3 className="text-lg font-semibold text-neutral-900 dark:text-dark-text mb-4 flex items-center gap-2">
                    <AlertCircle className="w-5 h-5 text-warning-600" />
                    Alerts
                  </h3>
                  <div className="space-y-3">
                    {[
                      { type: 'warning', message: 'High volatility in tech sector', time: '1h ago' },
                      { type: 'info', message: 'AAPL earnings report due next week', time: '3h ago' },
                    ].map((alert, i) => (
                      <div key={i} className="flex items-start gap-3 p-3 rounded-lg bg-warning-50 dark:bg-warning-950/20 border border-warning-200 dark:border-warning-900">
                        <AlertCircle className="w-5 h-5 text-warning-600 dark:text-warning-400 flex-shrink-0 mt-0.5" />
                        <div className="flex-1">
                          <p className="text-sm font-medium text-neutral-900 dark:text-dark-text">
                            {alert.message}
                          </p>
                          <p className="text-xs text-neutral-500 dark:text-neutral-400 mt-1">
                            {alert.time}
                          </p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </motion.div>
          )}

          {activeTab === 'positions' && (
            <motion.div
              key="positions"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
            >
              <EnhancedDataTable
                data={mockPositions}
                columns={positionColumns}
                title="Portfolio Positions"
                subtitle="Your current holdings and performance"
                exportFilename="portfolio-positions"
                highlightPositive
              />
            </motion.div>
          )}

          {activeTab === 'comparison' && (
            <motion.div
              key="comparison"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
            >
              <ComparisonView companies={mockComparisonData} />
            </motion.div>
          )}

          {activeTab === 'upload' && (
            <motion.div
              key="upload"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
            >
              <div className="card max-w-3xl mx-auto">
                <h3 className="text-lg font-semibold text-neutral-900 dark:text-dark-text mb-4">
                  Upload Financial Documents
                </h3>
                <UploadBox />
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </main>
    </div>
  )
}

export default function HomePage() {
  return (
    <AnalysisProvider>
      <HomePageContent />
    </AnalysisProvider>
  )
}
