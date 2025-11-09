/**
 * CSV Export Utilities
 * Functions for exporting data to CSV format
 */

export interface ExportColumn {
  key: string
  label: string
  format?: (value: any) => string
}

/**
 * Convert array of objects to CSV string
 */
export function arrayToCSV(data: any[], columns: ExportColumn[]): string {
  if (!data || data.length === 0) {
    return ''
  }

  // Create header row
  const headers = columns.map(col => `"${col.label}"`).join(',')
  
  // Create data rows
  const rows = data.map(item => {
    return columns.map(col => {
      let value = item[col.key]
      
      // Apply custom formatting if provided
      if (col.format && value !== null && value !== undefined) {
        value = col.format(value)
      }
      
      // Handle null/undefined
      if (value === null || value === undefined) {
        return '""'
      }
      
      // Convert to string and escape quotes
      const stringValue = String(value).replace(/"/g, '""')
      return `"${stringValue}"`
    }).join(',')
  })
  
  return [headers, ...rows].join('\n')
}

/**
 * Download CSV file
 */
export function downloadCSV(csvContent: string, filename: string): void {
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  
  if (link.download !== undefined) {
    const url = URL.createObjectURL(blob)
    link.setAttribute('href', url)
    link.setAttribute('download', filename)
    link.style.visibility = 'hidden'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
  }
}

/**
 * Export rankings to CSV
 */
export function exportRankingsToCSV(rankings: any[], philosophy: string): void {
  const columns: ExportColumn[] = [
    { key: 'rank', label: 'Rank' },
    { key: 'company', label: 'Company Name' },
    { key: 'symbol', label: 'NSE Code' },
    { key: 'compositeScore', label: 'Ranking Score', format: (v) => v.toFixed(1) },
    { key: 'buffettScore', label: 'Buffett Score', format: (v) => v.toFixed(1) },
    { key: 'lynchScore', label: 'Lynch Score', format: (v) => v.toFixed(1) },
    { key: 'growthScore', label: 'Growth Score', format: (v) => v.toFixed(1) },
    { key: 'qualityScore', label: 'Quality Score', format: (v) => (v * 100).toFixed(0) + '%' },
    { key: 'cashFlowQuality', label: 'Cash Flow Quality', format: (v) => (v * 100).toFixed(0) + '%' },
    { key: 'valuationScore', label: 'Valuation Score', format: (v) => (v * 100).toFixed(0) + '%' },
    { key: 'metrics.roe', label: 'ROE (%)', format: (v) => v?.toFixed(1) || 'N/A' },
    { key: 'metrics.roce', label: 'ROCE (%)', format: (v) => v?.toFixed(1) || 'N/A' },
    { key: 'metrics.debtToEquity', label: 'Debt/Equity', format: (v) => v?.toFixed(2) || 'N/A' },
    { key: 'metrics.peRatio', label: 'P/E Ratio', format: (v) => v?.toFixed(1) || 'N/A' },
    { key: 'metrics.peg', label: 'PEG Ratio', format: (v) => v?.toFixed(2) || 'N/A' },
    { key: 'metrics.fcf', label: 'Free Cash Flow (Cr)', format: (v) => v?.toFixed(2) || 'N/A' },
    { key: 'metrics.marketCap', label: 'Market Cap (Cr)', format: (v) => v?.toFixed(2) || 'N/A' },
    { key: 'metrics.opm', label: 'OPM (%)', format: (v) => v?.toFixed(1) || 'N/A' },
    { key: 'metrics.profitGrowth3Yr', label: 'Profit Growth 3Y (%)', format: (v) => v?.toFixed(1) || 'N/A' },
    { key: 'metrics.salesGrowth5Yr', label: 'Sales Growth 5Y (%)', format: (v) => v?.toFixed(1) || 'N/A' },
    { key: 'metrics.epsGrowth3Yr', label: 'EPS Growth 3Y (%)', format: (v) => v?.toFixed(1) || 'N/A' },
    { key: 'metrics.dividendYield', label: 'Dividend Yield (%)', format: (v) => v?.toFixed(2) || 'N/A' },
    { key: 'metrics.return1Yr', label: '1Y Return (%)', format: (v) => v?.toFixed(1) || 'N/A' },
    { key: 'metrics.return3Yr', label: '3Y Return (%)', format: (v) => v?.toFixed(1) || 'N/A' },
    { key: 'metrics.return5Yr', label: '5Y Return (%)', format: (v) => v?.toFixed(1) || 'N/A' },
    { key: 'rankingReason', label: 'Ranking Reason' },
    { key: 'riskWarnings', label: 'Risk Warnings', format: (v) => v?.join('; ') || 'None' },
    { key: 'valuationWarnings', label: 'Valuation Warnings', format: (v) => v?.join('; ') || 'None' },
  ]
  
  // Flatten nested metrics
  const flattenedData = rankings.map(item => ({
    ...item,
    'metrics.roe': item.metrics?.roe,
    'metrics.roce': item.metrics?.roce,
    'metrics.debtToEquity': item.metrics?.debtToEquity,
    'metrics.peRatio': item.metrics?.peRatio,
    'metrics.peg': item.metrics?.peg,
    'metrics.fcf': item.metrics?.fcf,
    'metrics.marketCap': item.metrics?.marketCap,
    'metrics.opm': item.metrics?.opm,
    'metrics.profitGrowth3Yr': item.metrics?.profitGrowth3Yr,
    'metrics.salesGrowth5Yr': item.metrics?.salesGrowth5Yr,
    'metrics.epsGrowth3Yr': item.metrics?.epsGrowth3Yr,
    'metrics.dividendYield': item.metrics?.dividendYield,
    'metrics.return1Yr': item.metrics?.return1Yr,
    'metrics.return3Yr': item.metrics?.return3Yr,
    'metrics.return5Yr': item.metrics?.return5Yr,
  }))
  
  const csv = arrayToCSV(flattenedData, columns)
  const timestamp = new Date().toISOString().split('T')[0]
  const filename = `stock_rankings_${philosophy}_${timestamp}.csv`
  
  downloadCSV(csv, filename)
}

/**
 * Export custom data with selected columns
 */
export function exportCustomDataToCSV(data: any[], selectedColumns: string[], columnMap: Record<string, string>): void {
  const columns: ExportColumn[] = selectedColumns.map(col => ({
    key: col,
    label: col
  }))
  
  const csv = arrayToCSV(data, columns)
  const timestamp = new Date().toISOString().split('T')[0]
  const filename = `stock_data_export_${timestamp}.csv`
  
  downloadCSV(csv, filename)
}

/**
 * Export philosophy-specific rankings
 */
export function exportPhilosophyRankings(rankings: any[], philosophy: 'buffett' | 'lynch', scoreKey: string): void {
  const columns: ExportColumn[] = [
    { key: 'rank', label: 'Rank' },
    { key: 'company', label: 'Company Name' },
    { key: 'symbol', label: 'NSE Code' },
    { key: scoreKey, label: `${philosophy === 'buffett' ? 'Buffett' : 'Lynch'} Score`, format: (v) => v.toFixed(1) },
    { key: 'compositeScore', label: 'Overall Score', format: (v) => v.toFixed(1) },
    { key: 'metrics.roe', label: 'ROE (%)', format: (v) => v?.toFixed(1) || 'N/A' },
    { key: 'metrics.roce', label: 'ROCE (%)', format: (v) => v?.toFixed(1) || 'N/A' },
    { key: 'metrics.debtToEquity', label: 'Debt/Equity', format: (v) => v?.toFixed(2) || 'N/A' },
    { key: 'metrics.fcf', label: 'Free Cash Flow (Cr)', format: (v) => v?.toFixed(2) || 'N/A' },
    { key: 'metrics.peRatio', label: 'P/E Ratio', format: (v) => v?.toFixed(1) || 'N/A' },
    { key: 'metrics.peg', label: 'PEG Ratio', format: (v) => v?.toFixed(2) || 'N/A' },
  ]
  
  // Sort by philosophy score
  const sortedRankings = [...rankings].sort((a, b) => b[scoreKey] - a[scoreKey])
  
  // Flatten nested metrics
  const flattenedData = sortedRankings.map(item => ({
    ...item,
    'metrics.roe': item.metrics?.roe,
    'metrics.roce': item.metrics?.roce,
    'metrics.debtToEquity': item.metrics?.debtToEquity,
    'metrics.fcf': item.metrics?.fcf,
    'metrics.peRatio': item.metrics?.peRatio,
    'metrics.peg': item.metrics?.peg,
  }))
  
  const csv = arrayToCSV(flattenedData, columns)
  const timestamp = new Date().toISOString().split('T')[0]
  const filename = `${philosophy}_companies_${timestamp}.csv`
  
  downloadCSV(csv, filename)
}
