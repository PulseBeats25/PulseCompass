'use client'

import { Sun, Moon, Monitor } from 'lucide-react'
import { useDarkMode } from '@/hooks/useDarkMode'
import { motion } from 'framer-motion'

export default function ThemeToggle() {
  const { theme, setTheme } = useDarkMode()

  const themes = [
    { value: 'light' as const, icon: Sun, label: 'Light' },
    { value: 'dark' as const, icon: Moon, label: 'Dark' },
    { value: 'system' as const, icon: Monitor, label: 'System' },
  ]

  return (
    <div className="flex items-center gap-1 p-1 bg-neutral-100 dark:bg-neutral-800 rounded-lg">
      {themes.map(({ value, icon: Icon, label }) => (
        <motion.button
          key={value}
          onClick={() => setTheme(value)}
          className={`
            relative px-3 py-2 rounded-md text-sm font-medium transition-colors
            ${theme === value 
              ? 'text-neutral-900 dark:text-white' 
              : 'text-neutral-600 dark:text-neutral-400 hover:text-neutral-900 dark:hover:text-white'
            }
          `}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          aria-label={`Switch to ${label} theme`}
        >
          {theme === value && (
            <motion.div
              layoutId="theme-indicator"
              className="absolute inset-0 bg-white dark:bg-neutral-700 rounded-md shadow-sm"
              transition={{ type: 'spring', stiffness: 300, damping: 30 }}
            />
          )}
          <Icon className="relative w-4 h-4" />
        </motion.button>
      ))}
    </div>
  )
}
