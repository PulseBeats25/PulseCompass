'use client'

import { motion, AnimatePresence } from 'framer-motion'
import { ChevronDown, ChevronUp, Award, TrendingUp, DollarSign, BarChart3 } from 'lucide-react'

interface CompanyMetrics {
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

interface CompanyRankingCardProps {
  rank: number
  company: string
  symbol: string
  compositeScore: number
  buffettScore: number
  lynchScore: number
  growthScore: number
  keyDrivers: string[]
  rankingReason: string
  riskWarnings?: string[]
  qualityScore?: number
  cashFlowQuality?: number
  valuationScore?: number
  valuationWarnings?: string[]
  sector?: string
  sectorAdjustment?: number
  sectorInsights?: string
  metrics: CompanyMetrics
  isExpanded: boolean
  onToggle: () => void
}

export default function CompanyRankingCard({
  rank,
  company,
  symbol,
  compositeScore,
  buffettScore,
  lynchScore,
  growthScore,
  keyDrivers,
  rankingReason,
  riskWarnings = [],
  qualityScore = 1.0,
  cashFlowQuality = 1.0,
  valuationScore = 1.0,
  valuationWarnings = [],
  sector = 'General',
  sectorAdjustment = 0,
  sectorInsights = '',
  metrics,
  isExpanded,
  onToggle
}: CompanyRankingCardProps) {
  const getRankColor = (rank: number) => {
    if (rank === 1) return 'text-yellow-600 dark:text-yellow-400 bg-yellow-50 dark:bg-yellow-900/20'
    if (rank === 2) return 'text-gray-500 dark:text-gray-400 bg-gray-50 dark:bg-gray-900/20'
    if (rank === 3) return 'text-orange-600 dark:text-orange-400 bg-orange-50 dark:bg-orange-900/20'
    return 'text-neutral-600 dark:text-neutral-400 bg-neutral-50 dark:bg-neutral-900/20'
  }

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-success-600 dark:text-success-400'
    if (score >= 60) return 'text-warning-600 dark:text-warning-400'
    return 'text-neutral-600 dark:text-neutral-400'
  }

  const formatNumber = (num: number | undefined, decimals: number = 2) => {
    if (num === undefined || num === null) return 'N/A'
    return num.toFixed(decimals)
  }

  const formatCurrency = (num: number | undefined) => {
    if (num === undefined || num === null) return 'N/A'
    if (num >= 1000) return `₹${(num / 1000).toFixed(2)}K Cr`
    return `₹${num.toFixed(2)} Cr`
  }

  const formatPercent = (num: number | undefined, decimals: number = 1) => {
    if (num === undefined || num === null) return 'N/A'
    return `${num.toFixed(decimals)}%`
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-white dark:bg-dark-surface rounded-xl border border-neutral-200 dark:border-dark-border overflow-hidden hover:shadow-lg transition-shadow"
    >
      {/* Card Header - Always Visible */}
      <div
        className="p-6 cursor-pointer"
        onClick={onToggle}
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4 flex-1">
            {/* Rank Badge */}
            <div className={`flex items-center justify-center w-16 h-16 rounded-full ${getRankColor(rank)}`}>
              {rank <= 3 && <Award className="w-6 h-6 mb-1" />}
              <span className="text-2xl font-bold">#{rank}</span>
            </div>

            {/* Company Info */}
            <div className="flex-1">
              <h3 className="text-xl font-bold text-neutral-900 dark:text-dark-text mb-1">
                {company}
              </h3>
              <div className="flex items-center gap-2">
                <p className="text-sm text-neutral-500 dark:text-neutral-400">{symbol}</p>
                {sector && sector !== 'General' && (
                  <span className="px-2 py-0.5 text-xs font-medium bg-primary-100 dark:bg-primary-900/30 text-primary-700 dark:text-primary-400 rounded">
                    {sector}
                  </span>
                )}
                {sectorAdjustment !== 0 && (
                  <span className={`px-2 py-0.5 text-xs font-medium rounded ${
                    sectorAdjustment > 0 
                      ? 'bg-success-100 dark:bg-success-900/30 text-success-700 dark:text-success-400'
                      : 'bg-warning-100 dark:bg-warning-900/30 text-warning-700 dark:text-warning-400'
                  }`}>
                    {sectorAdjustment > 0 ? '+' : ''}{sectorAdjustment.toFixed(1)}% sector adj.
                  </span>
                )}
              </div>
            </div>

            {/* Score */}
            <div className="text-right">
              <div className={`text-3xl font-bold ${getScoreColor(compositeScore)}`}>
                {compositeScore.toFixed(1)}
              </div>
              <div className="text-xs text-neutral-500 dark:text-neutral-400">Ranking Score</div>
            </div>

            {/* Expand Icon */}
            <div className="ml-4">
              {isExpanded ? (
                <ChevronUp className="w-6 h-6 text-neutral-400" />
              ) : (
                <ChevronDown className="w-6 h-6 text-neutral-400" />
              )}
            </div>
          </div>
        </div>

        {/* Key Metrics Preview */}
        <div className="mt-4 grid grid-cols-2 md:grid-cols-4 gap-4">
          <div>
            <div className="text-xs text-neutral-500 dark:text-neutral-400 mb-1">ROE</div>
            <div className="text-lg font-semibold text-neutral-900 dark:text-dark-text">
              {formatPercent(metrics.roe)}
            </div>
          </div>
          <div>
            <div className="text-xs text-neutral-500 dark:text-neutral-400 mb-1">ROCE</div>
            <div className="text-lg font-semibold text-neutral-900 dark:text-dark-text">
              {formatPercent(metrics.roce)}
            </div>
          </div>
          <div>
            <div className="text-xs text-neutral-500 dark:text-neutral-400 mb-1">P/E Ratio</div>
            <div className="text-lg font-semibold text-neutral-900 dark:text-dark-text">
              {formatNumber(metrics.peRatio, 1)}
            </div>
          </div>
          <div>
            <div className="text-xs text-neutral-500 dark:text-neutral-400 mb-1">Debt/Equity</div>
            <div className="text-lg font-semibold text-neutral-900 dark:text-dark-text">
              {formatNumber(metrics.debtToEquity)}
            </div>
          </div>
        </div>

        {/* Risk Warnings & Quality Scores */}
        {(riskWarnings.length > 0 || valuationWarnings.length > 0 || qualityScore < 0.9) && (
          <div className="mt-4 space-y-3">
            {/* Risk Warnings */}
            {riskWarnings.length > 0 && (
              <div className="p-3 bg-warning-50 dark:bg-warning-900/20 border border-warning-200 dark:border-warning-800 rounded-lg">
                <div className="text-xs font-semibold text-warning-900 dark:text-warning-200 mb-2">
                  ⚠️ Risk Warnings
                </div>
                <div className="flex flex-wrap gap-2">
                  {riskWarnings.map((warning, idx) => (
                    <span
                      key={idx}
                      className="text-xs px-2 py-1 bg-warning-100 dark:bg-warning-900/40 text-warning-800 dark:text-warning-300 rounded"
                    >
                      {warning}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Valuation Warnings */}
            {valuationWarnings.length > 0 && (
              <div className="p-3 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg">
                <div className="text-xs font-semibold text-blue-900 dark:text-blue-200 mb-2">
                  💰 Valuation Concerns
                </div>
                <div className="flex flex-wrap gap-2">
                  {valuationWarnings.map((warning, idx) => (
                    <span
                      key={idx}
                      className="text-xs px-2 py-1 bg-blue-100 dark:bg-blue-900/40 text-blue-800 dark:text-blue-300 rounded"
                    >
                      {warning}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Quality Metrics */}
            <div className="grid grid-cols-3 gap-3">
              <div className="p-3 bg-neutral-100 dark:bg-neutral-800 rounded-lg">
                <div className="text-xs text-neutral-600 dark:text-neutral-400 mb-1">
                  Quality Score
                </div>
                <div className={`text-lg font-bold ${
                  qualityScore >= 0.8 ? 'text-success-600' : 
                  qualityScore >= 0.6 ? 'text-warning-600' : 
                  'text-error-600'
                }`}>
                  {(qualityScore * 100).toFixed(0)}%
                </div>
              </div>

              <div className="p-3 bg-neutral-100 dark:bg-neutral-800 rounded-lg">
                <div className="text-xs text-neutral-600 dark:text-neutral-400 mb-1">
                  Cash Flow Quality
                </div>
                <div className={`text-lg font-bold ${
                  cashFlowQuality >= 1.1 ? 'text-success-600' : 
                  cashFlowQuality >= 0.9 ? 'text-neutral-600' : 
                  'text-warning-600'
                }`}>
                  {(cashFlowQuality * 100).toFixed(0)}%
                </div>
              </div>

              <div className="p-3 bg-neutral-100 dark:bg-neutral-800 rounded-lg">
                <div className="text-xs text-neutral-600 dark:text-neutral-400 mb-1">
                  Valuation Score
                </div>
                <div className={`text-lg font-bold ${
                  valuationScore >= 1.1 ? 'text-success-600' : 
                  valuationScore >= 0.9 ? 'text-neutral-600' : 
                  'text-warning-600'
                }`}>
                  {(valuationScore * 100).toFixed(0)}%
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Expanded Content */}
      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.3 }}
            className="border-t border-neutral-200 dark:border-neutral-700"
          >
            <div className="p-6 space-y-6">
              {/* Philosophy Scores */}
              <div>
                <h4 className="text-sm font-semibold text-neutral-700 dark:text-neutral-300 mb-3">
                  Investment Philosophy Scores
                </h4>
                <div className="grid grid-cols-3 gap-4">
                  <div className="bg-primary-50 dark:bg-primary-900/20 p-3 rounded-lg">
                    <div className="text-xs text-neutral-600 dark:text-neutral-400 mb-1">Buffett Score</div>
                    <div className="text-2xl font-bold text-primary-600 dark:text-primary-400">
                      {buffettScore.toFixed(1)}
                    </div>
                  </div>
                  <div className="bg-success-50 dark:bg-success-900/20 p-3 rounded-lg">
                    <div className="text-xs text-neutral-600 dark:text-neutral-400 mb-1">Lynch Score</div>
                    <div className="text-2xl font-bold text-success-600 dark:text-success-400">
                      {lynchScore.toFixed(1)}
                    </div>
                  </div>
                  <div className="bg-warning-50 dark:bg-warning-900/20 p-3 rounded-lg">
                    <div className="text-xs text-neutral-600 dark:text-neutral-400 mb-1">Growth Score</div>
                    <div className="text-2xl font-bold text-warning-600 dark:text-warning-400">
                      {growthScore.toFixed(1)}
                    </div>
                  </div>
                </div>
              </div>

              {/* Ranking Reason */}
              <div className="bg-neutral-50 dark:bg-neutral-800/50 p-4 rounded-lg">
                <p className="text-sm text-neutral-700 dark:text-neutral-300 italic">
                  {rankingReason}
                </p>
              </div>

              {/* Key Drivers */}
              <div>
                <h4 className="text-sm font-semibold text-neutral-700 dark:text-neutral-300 mb-3">
                  Key Performance Drivers
                </h4>
                <div className="flex flex-wrap gap-2">
                  {keyDrivers.map((driver, idx) => (
                    <span
                      key={idx}
                      className="px-3 py-1.5 text-sm bg-primary-100 dark:bg-primary-900/30 text-primary-700 dark:text-primary-400 rounded-full font-medium"
                    >
                      {driver}
                    </span>
                  ))}
                </div>
              </div>

              {/* Detailed Metrics */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {/* Valuation Metrics */}
                <div>
                  <h4 className="text-sm font-semibold text-neutral-700 dark:text-neutral-300 mb-3 flex items-center gap-2">
                    <DollarSign className="w-4 h-4" />
                    Valuation
                  </h4>
                  <div className="space-y-2">
                    <MetricRow label="Market Cap" value={formatCurrency(metrics.marketCap)} />
                    <MetricRow label="Current Price" value={`₹${formatNumber(metrics.currentPrice)}`} />
                    <MetricRow label="P/E Ratio" value={formatNumber(metrics.peRatio, 1)} />
                    <MetricRow label="PEG Ratio" value={formatNumber(metrics.peg)} />
                    <MetricRow label="Price/Sales" value={formatNumber(metrics.priceToSales)} />
                  </div>
                </div>

                {/* Profitability Metrics */}
                <div>
                  <h4 className="text-sm font-semibold text-neutral-700 dark:text-neutral-300 mb-3 flex items-center gap-2">
                    <TrendingUp className="w-4 h-4" />
                    Profitability
                  </h4>
                  <div className="space-y-2">
                    <MetricRow label="ROE" value={formatPercent(metrics.roe)} />
                    <MetricRow label="ROCE" value={formatPercent(metrics.roce)} />
                    <MetricRow label="OPM" value={formatPercent(metrics.opm)} />
                    <MetricRow label="EPS" value={`₹${formatNumber(metrics.eps)}`} />
                    <MetricRow label="PAT" value={formatCurrency(metrics.pat)} />
                  </div>
                </div>

                {/* Growth Metrics */}
                <div>
                  <h4 className="text-sm font-semibold text-neutral-700 dark:text-neutral-300 mb-3 flex items-center gap-2">
                    <BarChart3 className="w-4 h-4" />
                    Growth
                  </h4>
                  <div className="space-y-2">
                    <MetricRow label="Sales Growth (3Y)" value={formatPercent(metrics.salesGrowth3Yr)} />
                    <MetricRow label="Sales Growth (5Y)" value={formatPercent(metrics.salesGrowth5Yr)} />
                    <MetricRow label="Profit Growth (3Y)" value={formatPercent(metrics.profitGrowth3Yr)} />
                    <MetricRow label="Profit Growth (5Y)" value={formatPercent(metrics.profitGrowth5Yr)} />
                    <MetricRow label="EPS Growth (3Y)" value={formatPercent(metrics.epsGrowth3Yr)} />
                  </div>
                </div>

                {/* Financial Health */}
                <div>
                  <h4 className="text-sm font-semibold text-neutral-700 dark:text-neutral-300 mb-3">
                    Financial Health
                  </h4>
                  <div className="space-y-2">
                    <MetricRow label="Debt/Equity" value={formatNumber(metrics.debtToEquity)} />
                    <MetricRow label="Free Cash Flow" value={formatCurrency(metrics.fcf)} />
                    <MetricRow label="FCF (3Y)" value={formatCurrency(metrics.fcf3Yr)} />
                    <MetricRow label="FCF (5Y)" value={formatCurrency(metrics.fcf5Yr)} />
                    <MetricRow label="Asset Turnover" value={formatNumber(metrics.assetTurnover)} />
                  </div>
                </div>

                {/* Returns */}
                <div>
                  <h4 className="text-sm font-semibold text-neutral-700 dark:text-neutral-300 mb-3">
                    Returns
                  </h4>
                  <div className="space-y-2">
                    <MetricRow label="1 Year Return" value={formatPercent(metrics.return1Yr)} />
                    <MetricRow label="3 Year Return" value={formatPercent(metrics.return3Yr)} />
                    <MetricRow label="5 Year Return" value={formatPercent(metrics.return5Yr)} />
                    <MetricRow label="Dividend Yield" value={formatPercent(metrics.dividendYield)} />
                  </div>
                </div>

                {/* Other Metrics */}
                <div>
                  <h4 className="text-sm font-semibold text-neutral-700 dark:text-neutral-300 mb-3">
                    Other Metrics
                  </h4>
                  <div className="space-y-2">
                    <MetricRow label="Sales" value={formatCurrency(metrics.sales)} />
                    <MetricRow label="EPS Growth (5Y)" value={formatPercent(metrics.epsGrowth5Yr)} />
                  </div>
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  )
}

function MetricRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex justify-between items-center text-sm">
      <span className="text-neutral-600 dark:text-neutral-400">{label}:</span>
      <span className="font-semibold text-neutral-900 dark:text-dark-text">{value}</span>
    </div>
  )
}
