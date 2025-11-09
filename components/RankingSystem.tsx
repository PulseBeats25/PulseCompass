'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { 
  Upload, 
  FileSpreadsheet, 
  TrendingUp,
  Loader2,
  ArrowLeft,
  Download,
  AlertCircle
} from 'lucide-react'
import CompanyRankingCard from './CompanyRankingCard'

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
    metrics: {
      currentPrice?: number
      marketCap?: number
      peRatio?: number
      roe?: number
      roce?: number
      salesGrowth3Yr?: number
      salesGrowth5Yr?: number
      sales?: number
      pat?: number
      profitGrowth3Yr?: number
      profitGrowth5Yr?: number
      fcf3Yr?: number
      fcf5Yr?: number
      fcf?: number
      peg?: number
      return1Yr?: number
      return3Yr?: number
      return5Yr?: number
      assetTurnover?: number
      priceToSales?: number
      eps?: number
      epsGrowth3Yr?: number
      epsGrowth5Yr?: number
      debtToEquity?: number
      opm?: number
      dividendYield?: number
    }
  }>
  philosophy: string
  philosophyDescription: string
  totalCompanies: number
}

interface RankingSystemProps {
  onBack: () => void
}

const philosophies = [
  {
    id: 'buffett',
    name: 'Warren Buffett',
    description: 'Value investing with focus on quality and moats',
    weights: { roe: 0.35, roce: 0.20, debtToEquity: 0.25, profitGrowth: 0.10, fcf: 0.10 }
  },
  {
    id: 'lynch',
    name: 'Peter Lynch',
    description: 'Growth at reasonable price (GARP)',
    weights: { profitGrowth: 0.40, roe: 0.20, roce: 0.15, debtToEquity: 0.15, fcf: 0.10 }
  },
  {
    id: 'growth',
    name: 'Growth Investing',
    description: 'High growth companies with scalable models',
    weights: { profitGrowth: 0.35, roce: 0.30, roe: 0.25, fcf: 0.10, debtToEquity: 0.00 }
  },
  {
    id: 'value',
    name: 'Value Investing',
    description: 'Undervalued companies with strong fundamentals',
    weights: { debtToEquity: 0.30, roe: 0.25, roce: 0.20, profitGrowth: 0.15, fcf: 0.10 }
  },
  {
    id: 'dividend',
    name: 'Dividend Focus',
    description: 'Income-generating stable companies',
    weights: { roe: 0.30, debtToEquity: 0.25, fcf: 0.25, roce: 0.15, profitGrowth: 0.05 }
  },
  {
    id: 'custom',
    name: 'Custom Weights',
    description: 'Define your own weighting system',
    weights: { roe: 0.20, roce: 0.20, debtToEquity: 0.20, profitGrowth: 0.20, fcf: 0.20 }
  }
]

export default function RankingSystem({ onBack }: RankingSystemProps) {
  const [file, setFile] = useState<File | null>(null)
  const [selectedPhilosophy, setSelectedPhilosophy] = useState('buffett')
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [result, setResult] = useState<RankingResult | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [expandedCards, setExpandedCards] = useState<Set<number>>(new Set([1])) // Expand first card by default

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

  return (
    <div className="min-h-screen bg-neutral-50 dark:bg-dark-bg py-8">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <button
            onClick={onBack}
            className="flex items-center gap-2 text-neutral-600 dark:text-neutral-400 hover:text-neutral-900 dark:hover:text-white mb-4"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to Dashboard
          </button>
          <h1 className="text-3xl font-bold text-neutral-900 dark:text-dark-text mb-2">
            Financial Ranking System
          </h1>
          <p className="text-neutral-600 dark:text-neutral-400">
            Rank companies using fundamental analysis with multiple investment philosophies
          </p>
        </div>

        {!result ? (
          /* Upload Section */
          <div className="max-w-5xl mx-auto">
            <div className="bg-white dark:bg-dark-surface rounded-xl border border-neutral-200 dark:border-dark-border p-8">
              {/* File Upload */}
              <div className="mb-6">
                <label className="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-2">
                  Upload Financial Data
                </label>
                <div className="border-2 border-dashed border-neutral-300 dark:border-neutral-600 rounded-lg p-8 text-center hover:border-primary-500 transition-colors">
                  <input
                    type="file"
                    accept=".csv,.xlsx,.xls"
                    onChange={handleFileChange}
                    className="hidden"
                    id="file-upload"
                  />
                  <label htmlFor="file-upload" className="cursor-pointer">
                    <Upload className="w-12 h-12 text-neutral-400 mx-auto mb-4" />
                    <p className="text-neutral-600 dark:text-neutral-400 mb-2">
                      Click to upload or drag and drop
                    </p>
                    <p className="text-sm text-neutral-500 dark:text-neutral-500">
                      CSV or Excel files (from Screener.in or similar)
                    </p>
                  </label>
                </div>

                {file && (
                  <div className="mt-4 flex items-center gap-2 p-3 bg-neutral-50 dark:bg-neutral-800 rounded-lg">
                    <FileSpreadsheet className="w-5 h-5 text-primary-600 dark:text-primary-400" />
                    <span className="text-sm text-neutral-900 dark:text-dark-text flex-1">
                      {file.name}
                    </span>
                    <span className="text-xs text-neutral-500">
                      {(file.size / 1024).toFixed(2)} KB
                    </span>
                  </div>
                )}
              </div>

              {/* Philosophy Selection */}
              <div className="mb-6">
                <label className="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-3">
                  Select Investment Philosophy
                </label>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {philosophies.map((philosophy) => (
                    <button
                      key={philosophy.id}
                      onClick={() => setSelectedPhilosophy(philosophy.id)}
                      className={`
                        p-4 rounded-lg border-2 text-left transition-all
                        ${selectedPhilosophy === philosophy.id
                          ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20'
                          : 'border-neutral-200 dark:border-neutral-700 hover:border-neutral-300 dark:hover:border-neutral-600'
                        }
                      `}
                    >
                      <div className="font-semibold text-neutral-900 dark:text-dark-text mb-1">
                        {philosophy.name}
                      </div>
                      <div className="text-xs text-neutral-600 dark:text-neutral-400">
                        {philosophy.description}
                      </div>
                    </button>
                  ))}
                </div>
              </div>

              {error && (
                <div className="mb-6 p-4 bg-danger-50 dark:bg-danger-900/20 border border-danger-200 dark:border-danger-800 rounded-lg flex items-start gap-3">
                  <AlertCircle className="w-5 h-5 text-danger-600 dark:text-danger-400 flex-shrink-0 mt-0.5" />
                  <p className="text-sm text-danger-700 dark:text-danger-300">{error}</p>
                </div>
              )}

              {/* Analyze Button */}
              <button
                onClick={handleAnalyze}
                disabled={isAnalyzing || !file}
                className="w-full py-3 px-6 bg-gradient-to-r from-primary-600 to-primary-700 text-white rounded-lg font-medium hover:from-primary-700 hover:to-primary-800 disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center justify-center gap-2"
              >
                {isAnalyzing ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    Analyzing Companies...
                  </>
                ) : (
                  <>
                    <TrendingUp className="w-5 h-5" />
                    Rank Companies
                  </>
                )}
              </button>
            </div>
          </div>
        ) : (
          /* Results Section */
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-6"
          >
            {/* Summary Card */}
            <div className="bg-white dark:bg-dark-surface rounded-xl border border-neutral-200 dark:border-dark-border p-6">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-2xl font-bold text-neutral-900 dark:text-dark-text mb-2">
                    Ranking Results
                  </h2>
                  <p className="text-neutral-600 dark:text-neutral-400">
                    Philosophy: <span className="font-semibold">{philosophies.find(p => p.id === result.philosophy)?.name}</span>
                  </p>
                  <p className="text-sm text-neutral-500 dark:text-neutral-500">
                    {result.totalCompanies} companies analyzed
                  </p>
                </div>
                <div className="text-right">
                  <div className="text-4xl font-bold text-primary-600 dark:text-primary-400">
                    #{1}
                  </div>
                  <div className="text-sm text-neutral-600 dark:text-neutral-400">
                    Top Ranked
                  </div>
                </div>
              </div>
            </div>

            {/* Company Rankings - Expandable Cards */}
            <div className="space-y-4">
              {result.rankings.map((company) => (
                <CompanyRankingCard
                  key={company.rank}
                  rank={company.rank}
                  company={company.company}
                  symbol={company.symbol}
                  compositeScore={company.compositeScore}
                  buffettScore={company.buffettScore}
                  lynchScore={company.lynchScore}
                  growthScore={company.growthScore}
                  keyDrivers={company.keyDrivers}
                  rankingReason={company.rankingReason}
                  metrics={company.metrics}
                  isExpanded={expandedCards.has(company.rank)}
                  onToggle={() => toggleCard(company.rank)}
                />
              ))}
            </div>

            {/* Actions */}
            <div className="flex gap-4">
              <button
                onClick={() => {
                  setResult(null)
                  setFile(null)
                }}
                className="flex-1 py-3 px-6 bg-white dark:bg-dark-surface border border-neutral-300 dark:border-neutral-600 text-neutral-700 dark:text-neutral-300 rounded-lg font-medium hover:bg-neutral-50 dark:hover:bg-neutral-800 transition-all"
              >
                Analyze Another Dataset
              </button>
              <button
                className="flex-1 py-3 px-6 bg-gradient-to-r from-primary-600 to-primary-700 text-white rounded-lg font-medium hover:from-primary-700 hover:to-primary-800 transition-all flex items-center justify-center gap-2"
              >
                <Download className="w-5 h-5" />
                Export Rankings
              </button>
            </div>
          </motion.div>
        )}
      </div>
    </div>
  )
}
