'use client'

import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { X, Plus, TrendingUp, TrendingDown } from 'lucide-react'
import { formatCurrency, formatPercentage, formatNumber } from '@/utils/exportData'

interface CompanyMetrics {
  symbol: string
  name: string
  price: number
  marketCap: number
  peRatio: number
  pbRatio: number
  debtToEquity: number
  roe: number
  dividendYield: number
  revenue: number
  netIncome: number
  change: number
  changePercent: number
}

interface ComparisonViewProps {
  companies: CompanyMetrics[]
  onAddCompany?: () => void
  onRemoveCompany?: (symbol: string) => void
}

export default function ComparisonView({ 
  companies, 
  onAddCompany,
  onRemoveCompany 
}: ComparisonViewProps) {
  const [selectedMetric, setSelectedMetric] = useState<string | null>(null)

  const metrics = [
    { key: 'price', label: 'Price', format: (v: number) => formatCurrency(v) },
    { key: 'marketCap', label: 'Market Cap', format: (v: number) => formatCurrency(v) },
    { key: 'peRatio', label: 'P/E Ratio', format: (v: number) => formatNumber(v, 2) },
    { key: 'pbRatio', label: 'P/B Ratio', format: (v: number) => formatNumber(v, 2) },
    { key: 'debtToEquity', label: 'Debt/Equity', format: (v: number) => formatNumber(v, 2) },
    { key: 'roe', label: 'ROE', format: (v: number) => formatPercentage(v) },
    { key: 'dividendYield', label: 'Dividend Yield', format: (v: number) => formatPercentage(v) },
    { key: 'revenue', label: 'Revenue', format: (v: number) => formatCurrency(v) },
    { key: 'netIncome', label: 'Net Income', format: (v: number) => formatCurrency(v) },
  ]

  const getBestValue = (key: string) => {
    const values = companies.map(c => (c as any)[key])
    const betterHigher = ['roe', 'dividendYield', 'revenue', 'netIncome']
    const betterLower = ['peRatio', 'pbRatio', 'debtToEquity']

    if (betterHigher.includes(key)) {
      return Math.max(...values)
    } else if (betterLower.includes(key)) {
      return Math.min(...values)
    }
    return null
  }

  const isHighlighted = (company: CompanyMetrics, key: string) => {
    const bestValue = getBestValue(key)
    return bestValue !== null && (company as any)[key] === bestValue
  }

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-2xl font-bold text-neutral-900 dark:text-dark-text">
            Company Comparison
          </h2>
          <p className="text-sm text-neutral-600 dark:text-neutral-400 mt-1">
            Compare key metrics across multiple companies
          </p>
        </div>
        {onAddCompany && companies.length < 5 && (
          <button
            onClick={onAddCompany}
            className="btn-primary btn-sm flex items-center gap-2"
          >
            <Plus className="w-4 h-4" />
            Add Company
          </button>
        )}
      </div>

      {companies.length === 0 ? (
        <div className="text-center py-12">
          <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-neutral-100 dark:bg-neutral-800 flex items-center justify-center">
            <TrendingUp className="w-8 h-8 text-neutral-400" />
          </div>
          <h3 className="text-lg font-semibold text-neutral-900 dark:text-dark-text mb-2">
            No companies to compare
          </h3>
          <p className="text-neutral-600 dark:text-neutral-400 mb-4">
            Add companies to start comparing their metrics
          </p>
          {onAddCompany && (
            <button onClick={onAddCompany} className="btn-primary">
              Add Your First Company
            </button>
          )}
        </div>
      ) : (
        <div className="overflow-x-auto -mx-6">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b-2 border-neutral-200 dark:border-dark-border">
                <th className="px-6 py-4 text-left text-xs font-semibold text-neutral-700 dark:text-neutral-300 uppercase tracking-wider sticky left-0 bg-white dark:bg-dark-surface">
                  Metric
                </th>
                {companies.map((company) => (
                  <th
                    key={company.symbol}
                    className="px-6 py-4 text-left min-w-[200px]"
                  >
                    <div className="flex items-start justify-between">
                      <div>
                        <div className="text-base font-bold text-neutral-900 dark:text-dark-text">
                          {company.symbol}
                        </div>
                        <div className="text-xs text-neutral-600 dark:text-neutral-400 font-normal">
                          {company.name}
                        </div>
                        <div className="flex items-center gap-1 mt-2">
                          {company.changePercent >= 0 ? (
                            <TrendingUp className="w-4 h-4 text-success-600 dark:text-success-400" />
                          ) : (
                            <TrendingDown className="w-4 h-4 text-danger-600 dark:text-danger-400" />
                          )}
                          <span className={`text-sm font-semibold ${
                            company.changePercent >= 0
                              ? 'text-success-600 dark:text-success-400'
                              : 'text-danger-600 dark:text-danger-400'
                          }`}>
                            {formatPercentage(company.changePercent)}
                          </span>
                        </div>
                      </div>
                      {onRemoveCompany && (
                        <button
                          onClick={() => onRemoveCompany(company.symbol)}
                          className="p-1 rounded-md hover:bg-neutral-100 dark:hover:bg-neutral-800 transition-colors"
                        >
                          <X className="w-4 h-4 text-neutral-400" />
                        </button>
                      )}
                    </div>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {metrics.map((metric, idx) => (
                <motion.tr
                  key={metric.key}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: idx * 0.05 }}
                  className="border-b border-neutral-200 dark:border-dark-border hover:bg-neutral-50 dark:hover:bg-neutral-800 transition-colors"
                >
                  <td className="px-6 py-4 font-medium text-neutral-900 dark:text-dark-text sticky left-0 bg-white dark:bg-dark-surface">
                    {metric.label}
                  </td>
                  {companies.map((company) => {
                    const value = (company as any)[metric.key]
                    const highlighted = isHighlighted(company, metric.key)
                    
                    return (
                      <td
                        key={company.symbol}
                        className={`
                          px-6 py-4 text-neutral-900 dark:text-dark-text
                          ${highlighted ? 'bg-primary-50 dark:bg-primary-950/30 font-semibold' : ''}
                        `}
                      >
                        <div className="flex items-center gap-2">
                          {metric.format(value)}
                          {highlighted && (
                            <span className="text-xs text-primary-600 dark:text-primary-400">
                              ★
                            </span>
                          )}
                        </div>
                      </td>
                    )
                  })}
                </motion.tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <div className="mt-6 pt-4 border-t border-neutral-200 dark:border-dark-border">
        <p className="text-xs text-neutral-600 dark:text-neutral-400">
          ★ Best value in category • Comparing {companies.length} {companies.length === 1 ? 'company' : 'companies'}
        </p>
      </div>
    </div>
  )
}
