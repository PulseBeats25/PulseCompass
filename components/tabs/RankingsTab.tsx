'use client'

import { motion } from 'framer-motion'
import { Download, RefreshCw } from 'lucide-react'
import CompanyRankingCard from '../CompanyRankingCard'
import { exportRankingsToCSV } from '@/utils/csvExport'

export default function RankingsTab({ result, expandedCards, toggleCard, setResult, setFile }: any) {
  return (
    <motion.div
      key="rankings"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
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

      {/* Company Rankings */}
      <div className="space-y-4">
        {result.rankings.map((company: any) => (
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
            riskWarnings={company.riskWarnings || []}
            qualityScore={company.qualityScore || 1.0}
            cashFlowQuality={company.cashFlowQuality || 1.0}
            valuationScore={company.valuationScore || 1.0}
            valuationWarnings={company.valuationWarnings || []}
            sector={company.sector}
            sectorAdjustment={company.sectorAdjustment}
            sectorInsights={company.sectorInsights}
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
          New Analysis
        </button>
        <button
          onClick={() => exportRankingsToCSV(result.rankings, result.philosophy)}
          className="flex-1 py-3 px-6 bg-gradient-to-r from-primary-600 to-primary-700 text-white rounded-lg font-medium hover:from-primary-700 hover:to-primary-800 transition-all shadow-lg hover:shadow-xl flex items-center justify-center gap-2"
        >
          <Download className="w-5 h-5" />
          Export to CSV
        </button>
      </div>
    </motion.div>
  )
}
