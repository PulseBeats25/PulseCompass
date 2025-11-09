'use client'

import { useState, useEffect, useMemo } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Search, 
  TrendingUp, 
  Upload, 
  BarChart3, 
  FileText, 
  Settings,
  Sun,
  Moon,
  Download,
  X
} from 'lucide-react'
import { useDarkMode } from '@/hooks/useDarkMode'

interface Command {
  id: string
  label: string
  icon: React.ComponentType<{ className?: string }>
  action: () => void
  category: string
  keywords?: string[]
}

interface CommandPaletteProps {
  isOpen: boolean
  onClose: () => void
  onNavigate?: (path: string) => void
  onExport?: (format: 'csv' | 'pdf') => void
}

export default function CommandPalette({ 
  isOpen, 
  onClose, 
  onNavigate,
  onExport 
}: CommandPaletteProps) {
  const [search, setSearch] = useState('')
  const [selectedIndex, setSelectedIndex] = useState(0)
  const { toggleTheme, theme } = useDarkMode()

  const commands: Command[] = useMemo(() => [
    {
      id: 'upload',
      label: 'Upload Financial Statement',
      icon: Upload,
      action: () => {
        onNavigate?.('/upload')
        onClose()
      },
      category: 'Actions',
      keywords: ['file', 'import', 'data']
    },
    {
      id: 'analysis',
      label: 'View Analysis',
      icon: BarChart3,
      action: () => {
        onNavigate?.('/analysis')
        onClose()
      },
      category: 'Navigation',
      keywords: ['chart', 'graph', 'metrics']
    },
    {
      id: 'portfolio',
      label: 'Portfolio Overview',
      icon: TrendingUp,
      action: () => {
        onNavigate?.('/portfolio')
        onClose()
      },
      category: 'Navigation',
      keywords: ['stocks', 'holdings', 'investments']
    },
    {
      id: 'export-csv',
      label: 'Export as CSV',
      icon: Download,
      action: () => {
        onExport?.('csv')
        onClose()
      },
      category: 'Actions',
      keywords: ['download', 'save', 'data']
    },
    {
      id: 'export-pdf',
      label: 'Export as PDF',
      icon: FileText,
      action: () => {
        onExport?.('pdf')
        onClose()
      },
      category: 'Actions',
      keywords: ['download', 'save', 'report']
    },
    {
      id: 'theme',
      label: `Switch Theme (Current: ${theme})`,
      icon: theme === 'dark' ? Moon : Sun,
      action: () => {
        toggleTheme()
        onClose()
      },
      category: 'Settings',
      keywords: ['dark', 'light', 'appearance']
    },
  ], [theme, toggleTheme, onNavigate, onExport, onClose])

  const filteredCommands = useMemo(() => {
    if (!search) return commands

    const searchLower = search.toLowerCase()
    return commands.filter(cmd => 
      cmd.label.toLowerCase().includes(searchLower) ||
      cmd.category.toLowerCase().includes(searchLower) ||
      cmd.keywords?.some(k => k.includes(searchLower))
    )
  }, [commands, search])

  useEffect(() => {
    setSelectedIndex(0)
  }, [search])

  useEffect(() => {
    if (!isOpen) {
      setSearch('')
      setSelectedIndex(0)
    }
  }, [isOpen])

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (!isOpen) return

      if (e.key === 'ArrowDown') {
        e.preventDefault()
        setSelectedIndex(i => (i + 1) % filteredCommands.length)
      } else if (e.key === 'ArrowUp') {
        e.preventDefault()
        setSelectedIndex(i => (i - 1 + filteredCommands.length) % filteredCommands.length)
      } else if (e.key === 'Enter' && filteredCommands[selectedIndex]) {
        e.preventDefault()
        filteredCommands[selectedIndex].action()
      } else if (e.key === 'Escape') {
        e.preventDefault()
        onClose()
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [isOpen, filteredCommands, selectedIndex, onClose])

  if (!isOpen) return null

  const groupedCommands = filteredCommands.reduce((acc, cmd) => {
    if (!acc[cmd.category]) acc[cmd.category] = []
    acc[cmd.category].push(cmd)
    return acc
  }, {} as Record<string, Command[]>)

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 z-50 flex items-start justify-center pt-[20vh] px-4 bg-black/50 backdrop-blur-sm"
        onClick={onClose}
      >
        <motion.div
          initial={{ scale: 0.95, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.95, opacity: 0 }}
          transition={{ type: 'spring', stiffness: 300, damping: 30 }}
          className="w-full max-w-2xl bg-white dark:bg-dark-surface rounded-xl shadow-hard border border-neutral-200 dark:border-dark-border overflow-hidden"
          onClick={(e) => e.stopPropagation()}
        >
          {/* Search Input */}
          <div className="flex items-center gap-3 px-4 py-3 border-b border-neutral-200 dark:border-dark-border">
            <Search className="w-5 h-5 text-neutral-400" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Type a command or search..."
              className="flex-1 bg-transparent text-neutral-900 dark:text-dark-text placeholder-neutral-400 focus:outline-none"
              autoFocus
            />
            <button
              onClick={onClose}
              className="p-1 rounded-md hover:bg-neutral-100 dark:hover:bg-neutral-800 transition-colors"
            >
              <X className="w-4 h-4 text-neutral-500" />
            </button>
          </div>

          {/* Commands List */}
          <div className="max-h-[60vh] overflow-y-auto">
            {Object.entries(groupedCommands).map(([category, cmds]) => (
              <div key={category}>
                <div className="px-4 py-2 text-xs font-semibold text-neutral-500 dark:text-neutral-400 uppercase tracking-wider bg-neutral-50 dark:bg-neutral-900">
                  {category}
                </div>
                {cmds.map((cmd, idx) => {
                  const globalIndex = filteredCommands.indexOf(cmd)
                  const Icon = cmd.icon
                  return (
                    <button
                      key={cmd.id}
                      onClick={cmd.action}
                      onMouseEnter={() => setSelectedIndex(globalIndex)}
                      className={`
                        w-full flex items-center gap-3 px-4 py-3 text-left transition-colors
                        ${globalIndex === selectedIndex
                          ? 'bg-primary-50 dark:bg-primary-950/30 text-primary-700 dark:text-primary-400'
                          : 'text-neutral-900 dark:text-dark-text hover:bg-neutral-50 dark:hover:bg-neutral-800'
                        }
                      `}
                    >
                      <Icon className="w-5 h-5 flex-shrink-0" />
                      <span className="flex-1 font-medium">{cmd.label}</span>
                    </button>
                  )
                })}
              </div>
            ))}

            {filteredCommands.length === 0 && (
              <div className="px-4 py-8 text-center text-neutral-500 dark:text-neutral-400">
                No commands found for "{search}"
              </div>
            )}
          </div>

          {/* Footer */}
          <div className="flex items-center justify-between px-4 py-2 text-xs text-neutral-500 dark:text-neutral-400 border-t border-neutral-200 dark:border-dark-border bg-neutral-50 dark:bg-neutral-900">
            <div className="flex items-center gap-4">
              <span className="flex items-center gap-1">
                <kbd className="px-1.5 py-0.5 bg-white dark:bg-neutral-800 border border-neutral-300 dark:border-neutral-700 rounded">↑↓</kbd>
                Navigate
              </span>
              <span className="flex items-center gap-1">
                <kbd className="px-1.5 py-0.5 bg-white dark:bg-neutral-800 border border-neutral-300 dark:border-neutral-700 rounded">↵</kbd>
                Select
              </span>
              <span className="flex items-center gap-1">
                <kbd className="px-1.5 py-0.5 bg-white dark:bg-neutral-800 border border-neutral-300 dark:border-neutral-700 rounded">Esc</kbd>
                Close
              </span>
            </div>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  )
}
