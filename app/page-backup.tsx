'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { motion } from 'framer-motion'
import { 
  TrendingUp, 
  Upload as UploadIcon, 
  BarChart3, 
  Users, 
  Target,
  FileText,
  Database as DatabaseIcon,
  Brain,
  AlertCircle
} from 'lucide-react'
import DashboardCard from '@/components/DashboardCard'
import UploadBox from '@/components/UploadBox'
import CompanyTable from '@/components/CompanyTable'
import ValuationGauge from '@/components/ValuationGauge'
import FinancialCharts from '@/components/FinancialCharts'
import PhilosophySelector from '@/components/PhilosophySelector'
import PhilosophyComparison from '@/components/PhilosophyComparison'
import { AnalysisProvider, useAnalysis } from '@/contexts/AnalysisContext'

function HomePageContent() {
  const [activeTab, setActiveTab] = useState('overview')
  const [selectedPhilosophy, setSelectedPhilosophy] = useState('buffett')
  const { analysisResult, isAnalyzing, error, clearError } = useAnalysis()
  
  // Mock data for portfolio - replace with actual data from your API
  const portfolioData = {
    totalValue: 125000,
    dayChange: 1250,
    dayChangePercent: 1.01,
    positions: [
      { id: 1, symbol: 'AAPL', name: 'Apple Inc.', shares: 10, avgPrice: 150, currentPrice: 175, change: 25, changePercent: 16.67 },
      { id: 2, symbol: 'MSFT', name: 'Microsoft Corp.', shares: 8, avgPrice: 250, currentPrice: 300, change: 50, changePercent: 20.00 },
    ],
    alerts: [
      { id: 1, type: 'warning', message: 'High volatility in tech sector', date: '2023-06-15' },
      { id: 2, type: 'info', message: 'Earnings report due next week', date: '2023-06-20' },
    ]
  }
  interface PortfolioPosition {
    id: number;
    symbol: string;
    name: string;
    shares: number;
    avgPrice: number;
    currentPrice: number;
    change: number;
    changePercent: number;
  }

  interface Alert {
    id: number;
    type: 'warning' | 'info' | 'error';
    message: string;
    date: string;
  }

  interface PortfolioData {
    totalValue: number;
    dayChange: number;
    dayChangePercent: number;
    positions: PortfolioPosition[];
    alerts: Alert[];
  }

  const [localPortfolioData, setLocalPortfolioData] = useState<PortfolioData | null>(null);
  const [watchlistCompanies, setWatchlistCompanies] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [localError, setLocalError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setIsLoading(true);
        // Fetch portfolio data
        const portfolioResponse = await fetch('http://localhost:8000/portfolio');
        if (!portfolioResponse.ok) {
          throw new Error('Failed to fetch portfolio data');
        }
        const portfolio = await portfolioResponse.json();
        setLocalPortfolioData(portfolio);

        // Fetch watchlist companies
        const watchlistResponse = await fetch('http://localhost:8000/companies/watchlist');
        if (!watchlistResponse.ok) {
          throw new Error('Failed to fetch watchlist data');
        }
        const watchlist = await watchlistResponse.json();
        setWatchlistCompanies(watchlist);
      } catch (error: unknown) {
        const errorMessage = error instanceof Error ? error.message : 'An unknown error occurred';
        console.error('Error fetching data:', errorMessage);
        setLocalError(`Failed to fetch data: ${errorMessage}`);
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, []);

  // Mock philosophy data - replace with actual API data
  const mockPhilosophies = {
    buffett: {
      name: 'Warren Buffett Style',
      description: 'Focus on high ROE, low debt, strong cash flows',
      key_principles: [
        'High return on equity (>15%)',
        'Low debt-to-equity ratio (<0.5)',
        'Consistent profitability',
        'Strong competitive moats'
      ]
    },
    graham: {
      name: 'Benjamin Graham Style',
      description: 'Value investing with margin of safety',
      key_principles: [
        'Trading below intrinsic value',
        'Strong balance sheet (D/E < 0.5)',
        'Current ratio > 1.5',
        'Margin of safety (30%+)'
      ]
    },
    lynch: {
      name: 'Peter Lynch Style',
      description: 'Growth at reasonable price',
      key_principles: [
        'Strong earnings growth (>15%)',
        'Reasonable valuation (PEG < 1)',
        'Understandable business model',
        'Market leadership'
      ]
    },
    munger: {
      name: 'Charlie Munger Style',
      description: 'Quality businesses with durable advantages',
      key_principles: [
        'High and stable ROE/ROCE',
        'Strong competitive moats',
        'Predictable cash flows',
        'Quality management'
      ]
    },
    growth: {
      name: 'Growth Investing',
      description: 'High growth companies with strong returns',
      key_principles: [
        'High profit growth (>20%)',
        'Excellent ROCE (>20%)',
        'Scalable business model',
        'Large addressable market'
      ]
    },
    value: {
      name: 'Value Investing',
      description: 'Undervalued companies with strong fundamentals',
      key_principles: [
        'Trading below intrinsic value',
        'Strong balance sheet',
        'Consistent cash flows',
        'Margin of safety'
      ]
    },
    quality: {
      name: 'Quality Investing',
      description: 'High-quality companies with competitive advantages',
      key_principles: [
        'High and stable ROE/ROCE (>20%)',
        'Strong competitive moats',
        'Predictable cash flows',
        'Market leadership'
      ]
    }
  }

  const mockPhilosophyScores = {
    buffett: {
      name: 'Warren Buffett Style',
      score: 88.5,
      rank: 'Excellent',
      strengths: ['Excellent ROE (45.2%)', 'Very low debt (0.12)'],
      weaknesses: ['Moderate growth (18.5%)']
    },
    graham: {
      name: 'Benjamin Graham Style',
      score: 82.3,
      rank: 'Strong',
      strengths: ['Strong balance sheet', 'Good current ratio (2.1)'],
      weaknesses: ['High P/E ratio']
    },
    lynch: {
      name: 'Peter Lynch Style',
      score: 85.7,
      rank: 'Excellent',
      strengths: ['Strong growth (18.5%)', 'Excellent ROE'],
      weaknesses: []
    },
    munger: {
      name: 'Charlie Munger Style',
      score: 90.2,
      rank: 'Excellent',
      strengths: ['Outstanding ROCE (52.1%)', 'High margins'],
      weaknesses: []
    },
    growth: {
      name: 'Growth Investing',
      score: 87.1,
      rank: 'Excellent',
      strengths: ['Outstanding ROCE', 'Strong growth'],
      weaknesses: []
    },
    value: {
      name: 'Value Investing',
      score: 79.4,
      rank: 'Strong',
      strengths: ['Low debt', 'Strong fundamentals'],
      weaknesses: ['Premium valuation']
    },
    quality: {
      name: 'Quality Investing',
      score: 91.5,
      rank: 'Excellent',
      strengths: ['Exceptional ROE', 'High ROCE', 'Strong margins'],
      weaknesses: []
    },
    best_philosophy: {
      name: 'quality',
      score: 91.5
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-br from-primary-500 to-primary-700 rounded-xl flex items-center justify-center">
                <TrendingUp className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">PulseCompass</h1>
                <p className="text-sm text-gray-500">Advanced Stock Analysis</p>
              </div>
            </div>
            
            <nav className="flex space-x-8">
              {[
                { id: 'overview', label: 'Overview', icon: BarChart3 },
                { id: 'analysis', label: 'Analysis', icon: Brain },
                { id: 'portfolio', label: 'Portfolio', icon: Target },
                { id: 'watchlist', label: 'Watchlist', icon: Users },
              ].map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center space-x-2 px-3 py-2 rounded-lg font-medium transition-colors ${
                    activeTab === tab.id
                      ? 'bg-primary-100 text-primary-700'
                      : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                  }`}
                >
                  <tab.icon className="w-4 h-4" />
                  <span>{tab.label}</span>
                </button>
              ))}
            </nav>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === 'overview' && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            {/* Portfolio Summary */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
              {isLoading ? (
                // Loading state
                Array(4).fill(0).map((_, i) => (
                  <div key={i} className="bg-white rounded-xl border border-gray-200 p-6 animate-pulse h-32" />
                ))
              ) : error ? (
                // Error state
                <div className="col-span-4 bg-red-50 border border-red-200 text-red-700 p-4 rounded-lg">
                  Error loading data: {error}
                </div>
              ) : (
                // Success state
                <>
                  <DashboardCard
                    title="Portfolio Value"
                    value={`$${portfolioData?.totalValue?.toLocaleString() || '0'}`}
                    change={portfolioData?.dayChange}
                    changePercent={portfolioData?.dayChangePercent}
                    icon={BarChart3}
                    variant="success"
                  />
                  <DashboardCard
                    title="Positions"
                    value={portfolioData?.positions?.toString() || '0'}
                    icon={DatabaseIcon}
                  />
                  <DashboardCard
                    title="Alerts"
                    value={portfolioData?.alerts?.toString() || '0'}
                    icon={Target}
                    variant="warning"
                  />
                  <DashboardCard
                    title="Watchlist"
                    value={watchlistCompanies?.length?.toString() || '0'}
                    icon={Users}
                  />
                </>
              )}
            </div>

            {/* Quick Actions */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
              <div className="card">
                <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                  <UploadIcon className="w-5 h-5 mr-2 text-primary-600" />
                  Upload Documents
                </h3>
                <UploadBox />
              </div>

              <div className="card">
                <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                  <DatabaseIcon className="w-5 h-5 mr-2 text-primary-600" />
                  Recent Analysis
                  {isAnalyzing && (
                    <span className="ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                      Analyzing...
                    </span>
                  )}
                </h3>
                
                {error && (
                  <div className="mb-4 p-3 bg-red-50 text-red-700 rounded-md text-sm">
                    <div className="flex items-center">
                      <AlertCircle className="w-5 h-5 mr-2" />
                      <span>{error}</span>
                    </div>
                    <button 
                      onClick={clearError}
                      className="mt-2 text-red-600 hover:text-red-800 text-xs"
                    >
                      Dismiss
                    </button>
                  </div>
                )}

                <div className="space-y-3">
                  {isAnalyzing && !analysisResult ? (
                    <div className="space-y-4">
                      <div className="h-24 bg-gray-100 rounded-lg animate-pulse" />
                      <div className="h-4 bg-gray-100 rounded w-3/4 animate-pulse" />
                    </div>
                  ) : analysisResult ? (
                    <div className="space-y-3">
                      <Link href="/analysis" className="block">
                        <div className="hover:bg-gray-50 p-4 rounded-lg transition-colors">
                          <div className="flex items-start justify-between">
                            <div>
                              <h4 className="font-medium text-gray-900">
                                {analysisResult.company_name || 'Company Analysis'}
                              </h4>
                              <p className="text-sm text-gray-500 mt-1">
                                Last updated: {new Date(analysisResult.last_updated).toLocaleString()}
                              </p>
                              
                              {analysisResult.financial_metrics && (
                                <div className="mt-2 grid grid-cols-2 gap-2 text-sm">
                                  <div>
                                    <span className="text-gray-500">Revenue:</span>{' '}
                                    <span className="font-medium">
                                      ${(analysisResult.financial_metrics.revenue / 1000000).toFixed(1)}M
                                    </span>
                                  </div>
                                  <div>
                                    <span className="text-gray-500">P/E:</span>{' '}
                                    <span className="font-medium">
                                      {analysisResult.financial_metrics.pe_ratio.toFixed(1)}x
                                    </span>
                                  </div>
                                </div>
                              )}
                            </div>
                            <div className="flex flex-col items-end">
                              <span className={`px-3 py-1 rounded-full text-sm font-medium mb-2 ${
                                analysisResult.recommendation?.rating === 'Strong Buy' || analysisResult.recommendation?.rating === 'Buy' 
                                  ? 'bg-green-100 text-green-800' 
                                  : analysisResult.recommendation?.rating === 'Hold' 
                                    ? 'bg-yellow-100 text-yellow-800' 
                                    : 'bg-red-100 text-red-800'
                              }`}>
                                {analysisResult.recommendation?.rating || 'N/A'}
                              </span>
                              {analysisResult.recommendation?.confidence_score && (
                                <div className="text-xs text-gray-500 mt-1">
                                  Confidence: {Math.round(analysisResult.recommendation.confidence_score * 100)}%
                                </div>
                              )}
                            </div>
                          </div>
                          <div className="text-sm text-primary-600 font-medium mt-2">
                            View Full Analysis →
                          </div>
                        </div>
                      </Link>
                      
                      <div className="grid grid-cols-2 gap-3 text-sm">
                        <div className="p-3 bg-blue-50 rounded-lg">
                          <div className="font-medium text-blue-800">Target Price</div>
                          <div className="text-2xl font-bold text-blue-900">
                            ${analysisResult.recommendation?.target_price?.toFixed(2) || 'N/A'}
                          </div>
                          {analysisResult.recommendation?.current_price > 0 && (
                            <div className="text-xs text-blue-600 mt-1">
                              {analysisResult.recommendation.target_price > analysisResult.recommendation.current_price ? '↑ ' : '↓ '}
                              {Math.abs(
                                ((analysisResult.recommendation.target_price - analysisResult.recommendation.current_price) / 
                                 analysisResult.recommendation.current_price) * 100
                              ).toFixed(1)}% from current
                            </div>
                          )}
                        </div>
                        
                        <div className="p-3 bg-green-50 rounded-lg">
                          <div className="font-medium text-green-800">Margin of Safety</div>
                          <div className="text-2xl font-bold text-green-900">
                            {analysisResult.recommendation?.margin_of_safety ? 
                              `${Math.round(analysisResult.recommendation.margin_of_safety * 100)}%` : 'N/A'}
                          </div>
                          <div className="text-xs text-green-600 mt-1">
                            Based on intrinsic value
                          </div>
                        </div>
                      </div>
                      
                      {analysisResult.recommendation?.risk_factors?.length > 0 && (
                        <div className="mt-2">
                          <h5 className="text-sm font-medium text-gray-700 mb-1">Key Risks</h5>
                          <div className="space-y-1">
                            {analysisResult.recommendation.risk_factors.slice(0, 3).map((risk: string, i: number) => (
                              <div key={i} className="flex items-start text-sm text-gray-600">
                                <span className="text-red-500 mr-2">•</span>
                                <span>{risk}</span>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                      
                      <button 
                        className="w-full mt-3 text-sm text-primary-600 hover:text-primary-800 font-medium"
                        onClick={() => {
                          // Navigate to detailed analysis view
                          console.log('View detailed analysis', analysisResult.analysis_id);
                        }}
                      >
                        View Full Analysis →
                      </button>
                    </div>
                  ) : (
                    <div className="text-center p-6 border-2 border-dashed border-gray-300 rounded-lg">
                      <DatabaseIcon className="w-10 h-10 mx-auto text-gray-400" />
                      <h4 className="mt-2 text-sm font-medium text-gray-900">No analysis yet</h4>
                      <p className="mt-1 text-sm text-gray-500">
                        Upload company documents to get started with your analysis
                      </p>
                      <button 
                        className="mt-4 inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700"
                        onClick={() => {
                          const uploadButton = document.querySelector('button[type="button"]') as HTMLButtonElement;
                          if (uploadButton) {
                            uploadButton.click();
                          }
                        }}
                      >
                        <UploadIcon className="w-4 h-4 mr-2" />
                        Upload Documents
                      </button>
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Watchlist */}
            <div className="card">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-semibold text-gray-900">Watchlist</h3>
              </div>
              {isLoading ? (
                <div className="space-y-4">
                  {Array(3).fill(0).map((_, i) => (
                    <div key={i} className="h-16 bg-gray-100 rounded-lg animate-pulse" />
                  ))}
                </div>
              ) : error ? (
                <div className="text-red-600 p-4 bg-red-50 rounded-lg">
                  Error loading watchlist: {error}
                </div>
              ) : !watchlistCompanies || watchlistCompanies.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                  No companies in watchlist. Add companies to get started.
                </div>
              ) : (
                <CompanyTable companies={watchlistCompanies} />
              )}
            </div>

            {/* Financial Charts */}
            <FinancialCharts 
              showTrends={true}
              showRatios={true}
            />

            {/* Investment Philosophy Analysis */}
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <h2 className="text-2xl font-bold text-gray-900">Investment Philosophy Analysis</h2>
              </div>

              {/* Philosophy Selector */}
              <PhilosophySelector
                philosophies={mockPhilosophies}
                selectedPhilosophy={selectedPhilosophy}
                onSelect={setSelectedPhilosophy}
              />

              {/* Philosophy Comparison */}
              <PhilosophyComparison
                scores={mockPhilosophyScores}
                selectedPhilosophy={selectedPhilosophy}
                bestPhilosophy={mockPhilosophyScores.best_philosophy}
              />
            </div>
          </motion.div>
        )}

        {activeTab === 'analysis' && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
              {/* Company Analysis */}
              <div className="lg:col-span-2">
                <div className="card mb-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Company Analysis</h3>
                  {analysisResult ? (
                    <div className="space-y-6">
                      <div className="border-b border-gray-200 pb-4">
                        <h4 className="text-xl font-bold text-gray-900">{analysisResult.company_name}</h4>
                        <p className="text-sm text-gray-500">Last updated: {new Date(analysisResult.last_updated).toLocaleDateString()}</p>
                      </div>
                      
                      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 p-6 rounded-lg">
                        <h5 className="font-semibold text-gray-900 mb-2">Recommendation</h5>
                        <div className="flex items-center space-x-3">
                          <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                            analysisResult.recommendation.action === 'Strong Buy' ? 'bg-green-100 text-green-800' :
                            analysisResult.recommendation.action === 'Buy' ? 'bg-blue-100 text-blue-800' :
                            analysisResult.recommendation.action === 'Hold' ? 'bg-yellow-100 text-yellow-800' :
                            'bg-red-100 text-red-800'
                          }`}>
                            {analysisResult.recommendation.action}
                          </span>
                          <span className="text-sm text-gray-600">
                            Confidence: {analysisResult.recommendation.confidence !== undefined 
                              ? `${(analysisResult.recommendation.confidence * 100).toFixed(0)}%` 
                              : 'N/A'}
                          </span>
                        </div>
                        <p className="text-sm text-gray-700 mt-3">{analysisResult.recommendation.reasoning}</p>
                      </div>
                    </div>
                  ) : isAnalyzing ? (
                    <div className="text-center py-12">
                      <motion.div
                        animate={{ rotate: 360 }}
                        transition={{ duration: 1, repeat: Infinity }}
                      >
                        <Brain className="w-12 h-12 mx-auto mb-4 text-blue-500" />
                      </motion.div>
                      <p className="text-gray-600">Analyzing documents...</p>
                    </div>
                  ) : (
                    <div className="text-center py-12 text-gray-500">
                      <Brain className="w-12 h-12 mx-auto mb-4 text-gray-400" />
                      <p>Upload documents to start analysis</p>
                    </div>
                  )}
                </div>
              </div>

              {/* Investor Views */}
              <div className="space-y-6">
                <div className="investor-card border-l-blue-500">
                  <h4 className="font-semibold text-gray-900 mb-2">Warren Buffett View</h4>
                  <p className="text-sm text-gray-600">Focus on moat, ROE, debt control</p>
                  <div className="mt-3">
                    <span className="text-xs text-gray-500">Score: </span>
                    <span className="font-medium">
                      {analysisResult?.investor_views?.warren_buffett ? 
                        `${analysisResult.investor_views.warren_buffett.score}/10` : 
                        'Pending Analysis'
                      }
                    </span>
                  </div>
                  {analysisResult?.investor_views?.warren_buffett && (
                    <p className="text-xs text-gray-600 mt-2">{analysisResult.investor_views.warren_buffett.reasoning}</p>
                  )}
                </div>

                <div className="investor-card border-l-green-500">
                  <h4 className="font-semibold text-gray-900 mb-2">Benjamin Graham View</h4>
                  <p className="text-sm text-gray-600">Intrinsic value vs market price</p>
                  <div className="mt-3">
                    <span className="text-xs text-gray-500">Score: </span>
                    <span className="font-medium">
                      {analysisResult?.investor_views?.benjamin_graham ? 
                        `${analysisResult.investor_views.benjamin_graham.score}/10` : 
                        'Pending Analysis'
                      }
                    </span>
                  </div>
                  {analysisResult?.investor_views?.benjamin_graham && (
                    <p className="text-xs text-gray-600 mt-2">{analysisResult.investor_views.benjamin_graham.reasoning}</p>
                  )}
                </div>

                <div className="investor-card border-l-purple-500">
                  <h4 className="font-semibold text-gray-900 mb-2">Peter Lynch View</h4>
                  <p className="text-sm text-gray-600">PEG ratio, growth prospects</p>
                  <div className="mt-3">
                    <span className="text-xs text-gray-500">Score: </span>
                    <span className="font-medium">
                      {analysisResult?.investor_views?.peter_lynch ? 
                        `${analysisResult.investor_views.peter_lynch.score}/10` : 
                        'Pending Analysis'
                      }
                    </span>
                  </div>
                  {analysisResult?.investor_views?.peter_lynch && (
                    <p className="text-xs text-gray-600 mt-2">{analysisResult.investor_views.peter_lynch.reasoning}</p>
                  )}
                </div>

                <div className="investor-card border-l-orange-500">
                  <h4 className="font-semibold text-gray-900 mb-2">Charlie Munger View</h4>
                  <p className="text-sm text-gray-600">Long-term durability, quality</p>
                  <div className="mt-3">
                    <span className="text-xs text-gray-500">Score: </span>
                    <span className="font-medium">
                      {analysisResult?.investor_views?.charlie_munger ? 
                        `${analysisResult.investor_views.charlie_munger.score}/10` : 
                        'Pending Analysis'
                      }
                    </span>
                  </div>
                  {analysisResult?.investor_views?.charlie_munger && (
                    <p className="text-xs text-gray-600 mt-2">{analysisResult.investor_views.charlie_munger.reasoning}</p>
                  )}
                </div>
              </div>
            </div>
          </motion.div>
        )}

        {activeTab === 'portfolio' && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <div className="card">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Portfolio Management</h3>
              <div className="text-center py-12 text-gray-500">
                <Target className="w-12 h-12 mx-auto mb-4 text-gray-400" />
                <p>Portfolio features coming soon</p>
              </div>
            </div>
          </motion.div>
        )}

        {activeTab === 'watchlist' && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <div className="card">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-semibold text-gray-900">Watchlist</h3>
              </div>
              {isLoading ? (
                <div className="space-y-4">
                  {Array(3).fill(0).map((_, i) => (
                    <div key={i} className="h-16 bg-gray-100 rounded-lg animate-pulse" />
                  ))}
                </div>
              ) : error ? (
                <div className="text-red-600 p-4 bg-red-50 rounded-lg">
                  Error loading watchlist: {error}
                </div>
              ) : !watchlistCompanies || watchlistCompanies.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                  No companies in watchlist. Add companies to get started.
                </div>
              ) : (
                <CompanyTable companies={watchlistCompanies} />
              )}
            </div>
          </motion.div>
        )}
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
