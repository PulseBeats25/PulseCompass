'use client'

import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Upload, 
  FileSpreadsheet, 
  TrendingUp,
  Loader2,
  ArrowLeft,
  AlertCircle,
  BarChart3,
  Table,
  Lightbulb,
  Settings,
  X
} from 'lucide-react'
import RankingsTab from './tabs/RankingsTab'
import VisualizationsTab from './tabs/VisualizationsTab'
import PhilosophiesTab from './tabs/PhilosophiesTab'
import DataExplorerTab from './tabs/DataExplorerTab'

interface RankingResult {
  rankings: Array<{
    rank: number
    company: string
    symbol: string
    compositeScore: number
    buffettScore: number
    lynchScore: number
    growthScore: number
    keyDrivers: string[]
    rankingReason: string
    metrics: any
  }>
  philosophy: string
  philosophyDescription: string
  totalCompanies: number
}

interface AdvancedRankingSystemProps {
  onBack: () => void
}

interface MetricWeight {
  name: string
  label: string
  value: number
  min: number
  max: number
  step: number
}

const philosophies = [
  { id: 'buffett', name: 'Warren Buffett', description: 'Focus on quality companies with strong ROE, low debt, excellent cash flow, and reasonable valuations', icon: '🎯' },
  { id: 'lynch', name: 'Peter Lynch', description: 'Growth at reasonable price (PEG < 1) with strong earnings momentum and cash generation', icon: '📈' },
  { id: 'growth', name: 'Growth Investing', description: 'High growth companies with strong revenue expansion and sustainable cash generation', icon: '🚀' },
  { id: 'value', name: 'Value Investing', description: 'Undervalued companies (low P/E) with strong fundamentals, low debt, and positive cash flow', icon: '💎' },
  { id: 'dividend', name: 'Dividend Focus', description: 'High dividend yield backed by strong cash generation and low debt', icon: '💰' },
  { id: 'quality', name: 'Quality at Fair Price', description: 'High-quality businesses (strong FCF, ROE, ROCE) at reasonable valuations with low debt', icon: '⭐' }
]

export default function AdvancedRankingSystem({ onBack }: AdvancedRankingSystemProps) {
  const [file, setFile] = useState<File | null>(null)
  const [selectedPhilosophy, setSelectedPhilosophy] = useState('buffett')
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [result, setResult] = useState<RankingResult | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [expandedCards, setExpandedCards] = useState<Set<number>>(new Set([1]))
  const [activeTab, setActiveTab] = useState<'rankings' | 'visualizations' | 'philosophies' | 'explorer'>('rankings')
  const [showSidebar, setShowSidebar] = useState(true)
  const [selectedColumns, setSelectedColumns] = useState<string[]>([
    'Name', 'NSE Code', 'Rank', 'Ranking Score', 'Return on equity', 
    'Return on capital employed', 'Free cash flow last year', 'Price to Earning', 'Buffett Score'
  ])

  const [customWeights, setCustomWeights] = useState<MetricWeight[]>([
    { name: 'roe', label: 'Return on Equity', value: 0.15, min: 0, max: 0.5, step: 0.01 },
    { name: 'roce', label: 'Return on Capital', value: 0.10, min: 0, max: 0.5, step: 0.01 },
    { name: 'debt_equity', label: 'Debt to Equity', value: 0.08, min: 0, max: 0.5, step: 0.01 },
    { name: 'profit_growth', label: 'Profit Growth', value: 0.10, min: 0, max: 0.5, step: 0.01 },
    { name: 'sales_growth', label: 'Sales Growth', value: 0.10, min: 0, max: 0.5, step: 0.01 },
    { name: 'fcf', label: 'Free Cash Flow', value: 0.25, min: 0, max: 0.5, step: 0.01 },
    { name: 'pe_ratio', label: 'Price to Earnings', value: 0.08, min: 0, max: 0.5, step: 0.01 },
    { name: 'dividend_yield', label: 'Dividend Yield', value: 0.00, min: 0, max: 0.5, step: 0.01 },
  ])

  const totalWeight = customWeights.reduce((sum, w) => sum + w.value, 0)

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0])
      setError(null)
    }
  }

  const handleAnalyze = async () => {
    if (!file) {
      setError('Please upload a CSV or Excel file')
      return
    }

    setIsAnalyzing(true)
    setError(null)

    try {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('philosophy', selectedPhilosophy)

      const response = await fetch('http://localhost:8000/api/v1/ranking/analyze', {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        throw new Error('Analysis failed')
      }

      const data = await response.json()
      setResult(data)
      setActiveTab('rankings')
    } catch (err) {
      setError('Failed to analyze financial data. Please check your file format.')
      console.error(err)
    } finally {
      setIsAnalyzing(false)
    }
  }

  const toggleCard = (rank: number) => {
    const newExpanded = new Set(expandedCards)
    if (newExpanded.has(rank)) {
      newExpanded.delete(rank)
    } else {
      newExpanded.add(rank)
    }
    setExpandedCards(newExpanded)
  }

  const handleWeightChange = (index: number, newValue: number) => {
    const newWeights = [...customWeights]
    newWeights[index].value = newValue
    setCustomWeights(newWeights)
  }

  const resetWeights = () => {
    setCustomWeights([
      { name: 'roe', label: 'Return on Equity', value: 0.15, min: 0, max: 0.5, step: 0.01 },
      { name: 'roce', label: 'Return on Capital', value: 0.10, min: 0, max: 0.5, step: 0.01 },
      { name: 'debt_equity', label: 'Debt to Equity', value: 0.08, min: 0, max: 0.5, step: 0.01 },
      { name: 'profit_growth', label: 'Profit Growth', value: 0.10, min: 0, max: 0.5, step: 0.01 },
      { name: 'sales_growth', label: 'Sales Growth', value: 0.10, min: 0, max: 0.5, step: 0.01 },
      { name: 'fcf', label: 'Free Cash Flow', value: 0.25, min: 0, max: 0.5, step: 0.01 },
      { name: 'pe_ratio', label: 'Price to Earnings', value: 0.08, min: 0, max: 0.5, step: 0.01 },
      { name: 'dividend_yield', label: 'Dividend Yield', value: 0.00, min: 0, max: 0.5, step: 0.01 },
    ])
  }

  const tabs = [
    { id: 'rankings', label: 'Rankings', icon: TrendingUp },
    { id: 'visualizations', label: 'Visualizations', icon: BarChart3 },
    { id: 'philosophies', label: 'Investment Philosophies', icon: Lightbulb },
    { id: 'explorer', label: 'Data Explorer', icon: Table }
  ]

  const availableColumns = [
    'Name', 'NSE Code', 'Rank', 'Ranking Score', 'Return on equity', 
    'Return on capital employed', 'Free cash flow last year', 'Price to Earning',
    'Buffett Score', 'Lynch Score', 'Market Cap', 'P/E Ratio', 'Sales Growth',
    'Profit Growth', 'EPS', 'Dividend Yield', 'Debt to Equity'
  ]

  return (
    <div className="min-h-screen bg-neutral-50 dark:bg-dark-bg">
      <div className="flex">
        {/* Sidebar - Weight Controls */}
        <AnimatePresence>
          {showSidebar && result && (
            <motion.div
              initial={{ x: -300, opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              exit={{ x: -300, opacity: 0 }}
              className="w-80 bg-white dark:bg-dark-surface border-r border-neutral-200 dark:border-dark-border h-screen sticky top-0 overflow-y-auto"
            >
              <div className="p-6">
                <div className="flex items-center justify-between mb-6">
                  <h3 className="text-lg font-bold text-neutral-900 dark:text-dark-text">
                    Ranking Weights
                  </h3>
                  <button
                    onClick={() => setShowSidebar(false)}
                    className="p-1 hover:bg-neutral-100 dark:hover:bg-neutral-700 rounded"
                  >
                    <X className="w-5 h-5" />
                  </button>
                </div>

                <div className="mb-6 p-4 bg-neutral-50 dark:bg-neutral-800 rounded-lg">
                  <div className="text-sm text-neutral-600 dark:text-neutral-400 mb-1">
                    Total Weight
                  </div>
                  <div className={`text-2xl font-bold ${
                    Math.abs(totalWeight - 1.0) < 0.01 
                      ? 'text-success-600 dark:text-success-400' 
                      : 'text-warning-600 dark:text-warning-400'
                  }`}>
                    {(totalWeight * 100).toFixed(0)}%
                  </div>
                  {Math.abs(totalWeight - 1.0) >= 0.01 && (
                    <div className="text-xs text-warning-600 dark:text-warning-400 mt-1">
                      Should total 100%
                    </div>
                  )}
                </div>

                <div className="space-y-6 mb-6">
                  {customWeights.map((weight, index) => (
                    <div key={weight.name}>
                      <div className="flex justify-between items-center mb-2">
                        <label className="text-sm font-medium text-neutral-700 dark:text-neutral-300">
                          {weight.label}
                        </label>
                        <span className="text-sm font-bold text-primary-600 dark:text-primary-400">
                          {(weight.value * 100).toFixed(0)}%
                        </span>
                      </div>
                      <input
                        type="range"
                        min={weight.min}
                        max={weight.max}
                        step={weight.step}
                        value={weight.value}
                        onChange={(e) => handleWeightChange(index, parseFloat(e.target.value))}
                        className="w-full h-2 bg-neutral-200 dark:bg-neutral-700 rounded-lg appearance-none cursor-pointer accent-primary-600"
                      />
                      <div className="flex justify-between text-xs text-neutral-500 dark:text-neutral-400 mt-1">
                        <span>{(weight.min * 100).toFixed(0)}%</span>
                        <span>{(weight.max * 100).toFixed(0)}%</span>
                      </div>
                    </div>
                  ))}
                </div>

                <button
                  onClick={resetWeights}
                  className="w-full py-2 px-4 bg-neutral-200 dark:bg-neutral-700 text-neutral-700 dark:text-neutral-300 rounded-lg hover:bg-neutral-300 dark:hover:bg-neutral-600 transition-colors text-sm font-medium"
                >
                  Reset to Default
                </button>

                <div className="mt-6 p-4 bg-primary-50 dark:bg-primary-900/20 rounded-lg">
                  <h4 className="text-sm font-semibold text-primary-900 dark:text-primary-300 mb-2">
                    Investment Philosophy Weights
                  </h4>
                  <div className="space-y-2">
                    {philosophies.map((phil) => (
                      <button
                        key={phil.id}
                        onClick={() => setSelectedPhilosophy(phil.id)}
                        className={`w-full text-left p-2 rounded text-sm transition-colors ${
                          selectedPhilosophy === phil.id
                            ? 'bg-primary-600 text-white'
                            : 'bg-white dark:bg-neutral-800 text-neutral-700 dark:text-neutral-300 hover:bg-neutral-100 dark:hover:bg-neutral-700'
                        }`}
                      >
                        <span className="mr-2">{phil.icon}</span>
                        {phil.name}
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Main Content */}
        <div className="flex-1">
          <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-8">
            {/* Header */}
            <div className="mb-8">
              <div className="flex items-center justify-between mb-4">
                <button
                  onClick={onBack}
                  className="flex items-center gap-2 text-neutral-600 dark:text-neutral-400 hover:text-neutral-900 dark:hover:text-white"
                >
                  <ArrowLeft className="w-4 h-4" />
                  Back to Dashboard
                </button>
                {result && !showSidebar && (
                  <button
                    onClick={() => setShowSidebar(true)}
                    className="flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
                  >
                    <Settings className="w-4 h-4" />
                    Show Controls
                  </button>
                )}
              </div>
              <h1 className="text-3xl font-bold text-neutral-900 dark:text-dark-text mb-2">
                Intelligent Stock Ranking System
              </h1>
              <p className="text-neutral-600 dark:text-neutral-400">
                Advanced multi-factor analysis engine that evaluates companies across all sectors using proven investment principles from Warren Buffett and Peter Lynch. Analyzes ROE, ROCE, free cash flow, valuation metrics, and quality factors to identify the best investment opportunities.
              </p>
            </div>

            {/* Upload Section */}
            {!result && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="bg-white dark:bg-dark-surface rounded-xl border border-neutral-200 dark:border-dark-border p-8"
              >
                <div className="max-w-2xl mx-auto">
                  <div className="text-center mb-8">
                    <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-primary-100 dark:bg-primary-900/30 mb-4">
                      <FileSpreadsheet className="w-8 h-8 text-primary-600 dark:text-primary-400" />
                    </div>
                    <h2 className="text-2xl font-bold text-neutral-900 dark:text-dark-text mb-2">
                      Upload Company Financial Data
                    </h2>
                    <p className="text-neutral-600 dark:text-neutral-400">
                      Upload Excel or CSV with financial metrics from any sector - Technology, Finance, Healthcare, Manufacturing, and more
                    </p>
                  </div>

                  {error && (
                    <div className="mb-6 p-4 bg-error-50 dark:bg-error-900/20 border border-error-200 dark:border-error-800 rounded-lg flex items-start gap-3">
                      <AlertCircle className="w-5 h-5 text-error-600 dark:text-error-400 flex-shrink-0 mt-0.5" />
                      <div className="flex-1">
                        <p className="text-sm font-medium text-error-900 dark:text-error-200">
                          {error}
                        </p>
                      </div>
                    </div>
                  )}

                  <div className="mb-6">
                    <label className="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-2">
                      Select Investment Philosophy
                    </label>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                      {philosophies.map((phil) => (
                        <button
                          key={phil.id}
                          onClick={() => setSelectedPhilosophy(phil.id)}
                          className={`p-4 rounded-lg border-2 text-left transition-all ${
                            selectedPhilosophy === phil.id
                              ? 'border-primary-600 bg-primary-50 dark:bg-primary-900/20'
                              : 'border-neutral-200 dark:border-neutral-700 hover:border-neutral-300 dark:hover:border-neutral-600'
                          }`}
                        >
                          <div className="flex items-center gap-3 mb-2">
                            <span className="text-2xl">{phil.icon}</span>
                            <span className="font-semibold text-neutral-900 dark:text-dark-text">
                              {phil.name}
                            </span>
                          </div>
                          <p className="text-xs text-neutral-600 dark:text-neutral-400">
                            {phil.description}
                          </p>
                        </button>
                      ))}
                    </div>
                  </div>

                  <div className="mb-6">
                    <label
                      htmlFor="file-upload"
                      className="flex flex-col items-center justify-center w-full h-48 border-2 border-dashed border-neutral-300 dark:border-neutral-600 rounded-lg cursor-pointer hover:border-primary-500 dark:hover:border-primary-400 transition-colors bg-neutral-50 dark:bg-neutral-800/50"
                    >
                      <div className="flex flex-col items-center justify-center pt-5 pb-6">
                        <Upload className="w-12 h-12 text-neutral-400 dark:text-neutral-500 mb-3" />
                        <p className="mb-2 text-sm text-neutral-600 dark:text-neutral-400">
                          <span className="font-semibold">Click to upload</span> or drag and drop
                        </p>
                        <p className="text-xs text-neutral-500 dark:text-neutral-500">
                          Excel (.xlsx, .xls) or CSV files
                        </p>
                      </div>
                      <input
                        id="file-upload"
                        type="file"
                        className="hidden"
                        accept=".csv,.xlsx,.xls"
                        onChange={handleFileChange}
                      />
                    </label>
                    {file && (
                      <div className="mt-3 flex items-center gap-2 text-sm text-neutral-600 dark:text-neutral-400">
                        <FileSpreadsheet className="w-4 h-4" />
                        <span>{file.name}</span>
                      </div>
                    )}
                  </div>

                  <button
                    onClick={handleAnalyze}
                    disabled={!file || isAnalyzing}
                    className="w-full py-4 px-6 bg-gradient-to-r from-primary-600 to-primary-700 text-white rounded-lg font-semibold hover:from-primary-700 hover:to-primary-800 disabled:from-neutral-400 disabled:to-neutral-500 disabled:cursor-not-allowed transition-all shadow-lg hover:shadow-xl flex items-center justify-center gap-2"
                  >
                    {isAnalyzing ? (
                      <>
                        <Loader2 className="w-5 h-5 animate-spin" />
                        Analyzing...
                      </>
                    ) : (
                      <>
                        <TrendingUp className="w-5 h-5" />
                        Analyze Companies
                      </>
                    )}
                  </button>
                </div>
              </motion.div>
            )}

            {/* Results Section with Tabs */}
            {result && (
              <div className="space-y-6">
                {/* Tab Navigation */}
                <div className="bg-white dark:bg-dark-surface rounded-xl border border-neutral-200 dark:border-dark-border overflow-hidden">
                  <div className="flex border-b border-neutral-200 dark:border-neutral-700 overflow-x-auto">
                    {tabs.map((tab) => {
                      const Icon = tab.icon
                      return (
                        <button
                          key={tab.id}
                          onClick={() => setActiveTab(tab.id as any)}
                          className={`flex items-center gap-2 px-6 py-4 font-medium transition-colors whitespace-nowrap ${
                            activeTab === tab.id
                              ? 'text-primary-600 dark:text-primary-400 border-b-2 border-primary-600 dark:border-primary-400 bg-primary-50 dark:bg-primary-900/20'
                              : 'text-neutral-600 dark:text-neutral-400 hover:text-neutral-900 dark:hover:text-neutral-200 hover:bg-neutral-50 dark:hover:bg-neutral-800'
                          }`}
                        >
                          <Icon className="w-5 h-5" />
                          {tab.label}
                        </button>
                      )
                    })}
                  </div>
                </div>

                {/* Tab Content */}
                <AnimatePresence mode="wait">
                  {activeTab === 'rankings' && (
                    <RankingsTab
                      result={result}
                      expandedCards={expandedCards}
                      toggleCard={toggleCard}
                      setResult={setResult}
                      setFile={setFile}
                    />
                  )}

                  {activeTab === 'visualizations' && (
                    <VisualizationsTab result={result} />
                  )}

                  {activeTab === 'philosophies' && (
                    <PhilosophiesTab result={result} />
                  )}

                  {activeTab === 'explorer' && (
                    <DataExplorerTab
                      result={result}
                      selectedColumns={selectedColumns}
                      setSelectedColumns={setSelectedColumns}
                      availableColumns={availableColumns}
                    />
                  )}
                </AnimatePresence>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
