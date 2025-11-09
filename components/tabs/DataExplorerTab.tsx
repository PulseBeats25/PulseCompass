'use client'

import { motion } from 'framer-motion'
import { Table, Filter, X } from 'lucide-react'
import { useState } from 'react'
import { exportCustomDataToCSV } from '@/utils/csvExport'

export default function DataExplorerTab({ result, selectedColumns, setSelectedColumns, availableColumns }: any) {
  const [showColumnSelector, setShowColumnSelector] = useState(false)

  const toggleColumn = (column: string) => {
    if (selectedColumns.includes(column)) {
      setSelectedColumns(selectedColumns.filter((c: string) => c !== column))
    } else {
      setSelectedColumns([...selectedColumns, column])
    }
  }

  const getMetricValue = (company: any, column: string) => {
    const metricMap: any = {
      'Name': company.company,
      'NSE Code': company.symbol,
      'Rank': company.rank,
      'Ranking Score': company.compositeScore.toFixed(1),
      'Return on equity': company.metrics.roe?.toFixed(1) + '%' || 'N/A',
      'Return on capital employed': company.metrics.roce?.toFixed(1) + '%' || 'N/A',
      'Free cash flow last year': company.metrics.fcf?.toFixed(2) || 'N/A',
      'Price to Earning': company.metrics.peRatio?.toFixed(1) || 'N/A',
      'Buffett Score': company.buffettScore.toFixed(1),
      'Lynch Score': company.lynchScore.toFixed(1),
      'Market Cap': company.metrics.marketCap?.toFixed(2) || 'N/A',
      'P/E Ratio': company.metrics.peRatio?.toFixed(1) || 'N/A',
      'Sales Growth': company.metrics.salesGrowth5Yr?.toFixed(1) + '%' || 'N/A',
      'Profit Growth': company.metrics.profitGrowth3Yr?.toFixed(1) + '%' || 'N/A',
      'EPS': company.metrics.eps?.toFixed(2) || 'N/A',
      'Dividend Yield': company.metrics.dividendYield?.toFixed(2) + '%' || 'N/A',
      'Debt to Equity': company.metrics.debtToEquity?.toFixed(2) || 'N/A'
    }
    return metricMap[column] || 'N/A'
  }

  return (
    <motion.div
      key="explorer"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="space-y-6"
    >
      <div className="bg-white dark:bg-dark-surface rounded-xl border border-neutral-200 dark:border-dark-border p-8">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <Table className="w-6 h-6 text-primary-600 dark:text-primary-400" />
            <div>
              <h2 className="text-2xl font-bold text-neutral-900 dark:text-dark-text">
                Data Explorer
              </h2>
              <p className="text-sm text-neutral-600 dark:text-neutral-400">
                Explore the complete dataset with all calculated metrics
              </p>
            </div>
          </div>
          <button
            onClick={() => setShowColumnSelector(!showColumnSelector)}
            className="flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
          >
            <Filter className="w-4 h-4" />
            Select Columns
          </button>
        </div>

        {/* Column Selector */}
        {showColumnSelector && (
          <div className="mb-6 p-4 bg-neutral-50 dark:bg-neutral-800 rounded-lg">
            <div className="flex items-center justify-between mb-3">
              <h3 className="font-semibold text-neutral-900 dark:text-dark-text">
                Select columns to display
              </h3>
              <button
                onClick={() => setShowColumnSelector(false)}
                className="p-1 hover:bg-neutral-200 dark:hover:bg-neutral-700 rounded"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
            <div className="flex flex-wrap gap-2">
              {availableColumns.map((column: string) => (
                <button
                  key={column}
                  onClick={() => toggleColumn(column)}
                  className={`px-3 py-1.5 rounded-full text-sm font-medium transition-colors ${
                    selectedColumns.includes(column)
                      ? 'bg-primary-600 text-white'
                      : 'bg-white dark:bg-neutral-700 text-neutral-700 dark:text-neutral-300 border border-neutral-300 dark:border-neutral-600 hover:border-primary-400'
                  }`}
                >
                  {column}
                  {selectedColumns.includes(column) && (
                    <X className="w-3 h-3 inline ml-1" />
                  )}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Selected Columns Display */}
        <div className="mb-4">
          <div className="flex flex-wrap gap-2">
            {selectedColumns.map((column: string) => (
              <span
                key={column}
                className="px-3 py-1 bg-primary-100 dark:bg-primary-900/30 text-primary-700 dark:text-primary-400 rounded-full text-sm font-medium flex items-center gap-2"
              >
                {column}
                <button
                  onClick={() => toggleColumn(column)}
                  className="hover:bg-primary-200 dark:hover:bg-primary-800 rounded-full p-0.5"
                >
                  <X className="w-3 h-3" />
                </button>
              </span>
            ))}
          </div>
        </div>

        {/* Data Table */}
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-neutral-50 dark:bg-neutral-800 border-b border-neutral-200 dark:border-neutral-700 sticky top-0">
              <tr>
                {selectedColumns.map((column: string) => (
                  <th
                    key={column}
                    className="px-4 py-3 text-left text-xs font-medium text-neutral-500 dark:text-neutral-400 uppercase tracking-wider whitespace-nowrap"
                  >
                    {column}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-neutral-200 dark:divide-neutral-700">
              {result.rankings.map((company: any, idx: number) => (
                <tr
                  key={idx}
                  className="hover:bg-neutral-50 dark:hover:bg-neutral-800 transition-colors"
                >
                  {selectedColumns.map((column: string) => (
                    <td
                      key={column}
                      className="px-4 py-3 text-sm text-neutral-700 dark:text-neutral-300 whitespace-nowrap"
                    >
                      {getMetricValue(company, column)}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Table Footer */}
        <div className="mt-4 flex items-center justify-between text-sm text-neutral-600 dark:text-neutral-400">
          <div>
            Showing {result.rankings.length} companies with {selectedColumns.length} columns
          </div>
          <button 
            onClick={() => {
              // Prepare data with selected columns
              const exportData = result.rankings.map((company: any) => {
                const row: any = {}
                selectedColumns.forEach((col: string) => {
                  row[col] = getMetricValue(company, col)
                })
                return row
              })
              exportCustomDataToCSV(exportData, selectedColumns, {})
            }}
            className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors font-medium"
          >
            Export to CSV
          </button>
        </div>
      </div>
    </motion.div>
  )
}
