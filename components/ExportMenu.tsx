'use client'

import { useState } from 'react'
import { Download, FileText, Table, Copy, Check } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import { exportToCSV, exportToJSON, copyToClipboard } from '@/utils/exportData'

interface ExportMenuProps {
  data: any
  filename: string
  onExport?: (format: 'csv' | 'json') => void
}

export default function ExportMenu({ data, filename, onExport }: ExportMenuProps) {
  const [isOpen, setIsOpen] = useState(false)
  const [copied, setCopied] = useState(false)

  const handleExportCSV = () => {
    if (onExport) {
      onExport('csv')
    } else if (data) {
      exportToCSV({
        headers: Object.keys(data[0] || {}),
        rows: data.map((row: any) => Object.values(row)),
        filename,
      })
    }
    setIsOpen(false)
  }

  const handleExportJSON = () => {
    if (onExport) {
      onExport('json')
    } else if (data) {
      exportToJSON(data, filename)
    }
    setIsOpen(false)
  }

  const handleCopy = async () => {
    const success = await copyToClipboard(JSON.stringify(data, null, 2))
    if (success) {
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    }
    setIsOpen(false)
  }

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="btn-secondary btn-sm flex items-center gap-2"
      >
        <Download className="w-4 h-4" />
        Export
      </button>

      <AnimatePresence>
        {isOpen && (
          <>
            {/* Backdrop */}
            <div
              className="fixed inset-0 z-40"
              onClick={() => setIsOpen(false)}
            />

            {/* Menu */}
            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: -10 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: -10 }}
              transition={{ duration: 0.1 }}
              className="absolute right-0 mt-2 w-56 bg-white dark:bg-dark-surface rounded-lg shadow-hard border border-neutral-200 dark:border-dark-border overflow-hidden z-50"
            >
              <div className="py-1">
                <button
                  onClick={handleExportCSV}
                  className="w-full flex items-center gap-3 px-4 py-2.5 text-sm text-neutral-700 dark:text-neutral-300 hover:bg-neutral-50 dark:hover:bg-neutral-800 transition-colors"
                >
                  <Table className="w-4 h-4" />
                  <div className="flex-1 text-left">
                    <div className="font-medium">Export as CSV</div>
                    <div className="text-xs text-neutral-500 dark:text-neutral-400">
                      Spreadsheet format
                    </div>
                  </div>
                </button>

                <button
                  onClick={handleExportJSON}
                  className="w-full flex items-center gap-3 px-4 py-2.5 text-sm text-neutral-700 dark:text-neutral-300 hover:bg-neutral-50 dark:hover:bg-neutral-800 transition-colors"
                >
                  <FileText className="w-4 h-4" />
                  <div className="flex-1 text-left">
                    <div className="font-medium">Export as JSON</div>
                    <div className="text-xs text-neutral-500 dark:text-neutral-400">
                      Raw data format
                    </div>
                  </div>
                </button>

                <div className="border-t border-neutral-200 dark:border-dark-border my-1" />

                <button
                  onClick={handleCopy}
                  className="w-full flex items-center gap-3 px-4 py-2.5 text-sm text-neutral-700 dark:text-neutral-300 hover:bg-neutral-50 dark:hover:bg-neutral-800 transition-colors"
                >
                  {copied ? (
                    <Check className="w-4 h-4 text-success-600" />
                  ) : (
                    <Copy className="w-4 h-4" />
                  )}
                  <div className="flex-1 text-left">
                    <div className="font-medium">
                      {copied ? 'Copied!' : 'Copy to Clipboard'}
                    </div>
                    <div className="text-xs text-neutral-500 dark:text-neutral-400">
                      JSON format
                    </div>
                  </div>
                </button>
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </div>
  )
}
