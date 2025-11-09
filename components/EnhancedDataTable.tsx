'use client'

import { useState, useMemo } from 'react'
import { motion } from 'framer-motion'
import { 
  ArrowUpDown, 
  ArrowUp, 
  ArrowDown,
  TrendingUp,
  TrendingDown,
  Minus
} from 'lucide-react'
import ExportMenu from './ExportMenu'

export interface Column<T> {
  key: keyof T | string
  label: string
  sortable?: boolean
  format?: (value: any, row: T) => React.ReactNode
  align?: 'left' | 'center' | 'right'
  width?: string
  className?: string
}

interface EnhancedDataTableProps<T> {
  data: T[]
  columns: Column<T>[]
  title?: string
  subtitle?: string
  exportFilename?: string
  onRowClick?: (row: T) => void
  highlightPositive?: boolean
  compact?: boolean
}

type SortDirection = 'asc' | 'desc' | null

export default function EnhancedDataTable<T extends Record<string, any>>({
  data,
  columns,
  title,
  subtitle,
  exportFilename = 'data',
  onRowClick,
  highlightPositive = false,
  compact = false,
}: EnhancedDataTableProps<T>) {
  const [sortKey, setSortKey] = useState<string | null>(null)
  const [sortDirection, setSortDirection] = useState<SortDirection>(null)

  const sortedData = useMemo(() => {
    if (!sortKey || !sortDirection) return data

    return [...data].sort((a, b) => {
      const aVal = a[sortKey]
      const bVal = b[sortKey]

      if (aVal === bVal) return 0

      const comparison = aVal < bVal ? -1 : 1
      return sortDirection === 'asc' ? comparison : -comparison
    })
  }, [data, sortKey, sortDirection])

  const handleSort = (key: string) => {
    if (sortKey === key) {
      if (sortDirection === 'asc') {
        setSortDirection('desc')
      } else if (sortDirection === 'desc') {
        setSortKey(null)
        setSortDirection(null)
      }
    } else {
      setSortKey(key)
      setSortDirection('asc')
    }
  }

  const getCellValue = (row: T, column: Column<T>) => {
    const value = row[column.key as keyof T]
    return column.format ? column.format(value, row) : value
  }

  const getTrendIcon = (value: number) => {
    if (value > 0) return <TrendingUp className="w-4 h-4 text-success-600 dark:text-success-400" />
    if (value < 0) return <TrendingDown className="w-4 h-4 text-danger-600 dark:text-danger-400" />
    return <Minus className="w-4 h-4 text-neutral-400" />
  }

  const exportData = {
    headers: columns.map(col => col.label),
    rows: sortedData.map(row => 
      columns.map(col => {
        const value = row[col.key as keyof T]
        return typeof value === 'object' ? JSON.stringify(value) : value
      })
    ),
    filename: exportFilename,
    title,
  }

  return (
    <div className="card">
      {/* Header */}
      {(title || subtitle) && (
        <div className="flex items-start justify-between mb-4 pb-4 border-b border-neutral-200 dark:border-dark-border">
          <div>
            {title && (
              <h3 className="text-lg font-semibold text-neutral-900 dark:text-dark-text">
                {title}
              </h3>
            )}
            {subtitle && (
              <p className="text-sm text-neutral-600 dark:text-neutral-400 mt-1">
                {subtitle}
              </p>
            )}
          </div>
          <ExportMenu data={sortedData} filename={exportFilename} />
        </div>
      )}

      {/* Table */}
      <div className="overflow-x-auto -mx-6">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-neutral-200 dark:border-dark-border">
              {columns.map((column, idx) => (
                <th
                  key={idx}
                  className={`
                    px-6 py-3 text-xs font-semibold uppercase tracking-wider
                    ${column.align === 'right' ? 'text-right' : column.align === 'center' ? 'text-center' : 'text-left'}
                    ${column.sortable ? 'cursor-pointer hover:bg-neutral-50 dark:hover:bg-neutral-800 transition-colors' : ''}
                    text-neutral-700 dark:text-neutral-300
                    ${compact ? 'py-2' : 'py-3'}
                  `}
                  style={{ width: column.width }}
                  onClick={() => column.sortable && handleSort(column.key as string)}
                >
                  <div className="flex items-center gap-2 justify-between">
                    <span>{column.label}</span>
                    {column.sortable && (
                      <span className="text-neutral-400">
                        {sortKey === column.key ? (
                          sortDirection === 'asc' ? (
                            <ArrowUp className="w-4 h-4" />
                          ) : (
                            <ArrowDown className="w-4 h-4" />
                          )
                        ) : (
                          <ArrowUpDown className="w-4 h-4 opacity-30" />
                        )}
                      </span>
                    )}
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {sortedData.map((row, rowIdx) => (
              <motion.tr
                key={rowIdx}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: rowIdx * 0.02 }}
                onClick={() => onRowClick?.(row)}
                className={`
                  border-b border-neutral-200 dark:border-dark-border last:border-0
                  ${onRowClick ? 'cursor-pointer hover:bg-neutral-50 dark:hover:bg-neutral-800' : ''}
                  transition-colors
                `}
              >
                {columns.map((column, colIdx) => {
                  const value = getCellValue(row, column)
                  const numericValue = typeof row[column.key as keyof T] === 'number' 
                    ? row[column.key as keyof T] 
                    : null

                  return (
                    <td
                      key={colIdx}
                      className={`
                        px-6 text-neutral-900 dark:text-dark-text
                        ${column.align === 'right' ? 'text-right' : column.align === 'center' ? 'text-center' : 'text-left'}
                        ${compact ? 'py-2' : 'py-3'}
                        ${column.className || ''}
                      `}
                    >
                      <div className="flex items-center gap-2 justify-between">
                        {highlightPositive && numericValue !== null && (
                          <span className="flex-shrink-0">
                            {getTrendIcon(numericValue)}
                          </span>
                        )}
                        <span className={`
                          ${highlightPositive && numericValue !== null
                            ? numericValue > 0
                              ? 'text-success-600 dark:text-success-400 font-semibold'
                              : numericValue < 0
                              ? 'text-danger-600 dark:text-danger-400 font-semibold'
                              : ''
                            : ''
                          }
                        `}>
                          {value}
                        </span>
                      </div>
                    </td>
                  )
                })}
              </motion.tr>
            ))}
          </tbody>
        </table>

        {sortedData.length === 0 && (
          <div className="text-center py-12 text-neutral-500 dark:text-neutral-400">
            No data available
          </div>
        )}
      </div>

      {/* Footer */}
      {sortedData.length > 0 && (
        <div className="mt-4 pt-4 border-t border-neutral-200 dark:border-dark-border">
          <p className="text-xs text-neutral-600 dark:text-neutral-400">
            Showing {sortedData.length} {sortedData.length === 1 ? 'row' : 'rows'}
          </p>
        </div>
      )}
    </div>
  )
}
