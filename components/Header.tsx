'use client'

import { useState } from 'react'
import Link from 'next/link'
import { motion } from 'framer-motion'
import { 
  TrendingUp, 
  Search, 
  Bell, 
  Settings,
  Menu,
  X
} from 'lucide-react'
import ThemeToggle from './ThemeToggle'
import CommandPalette from './CommandPalette'
import { useKeyboardShortcuts } from '@/hooks/useKeyboardShortcuts'

export default function Header() {
  const [isCommandPaletteOpen, setIsCommandPaletteOpen] = useState(false)
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false)

  // Keyboard shortcuts
  useKeyboardShortcuts([
    {
      key: 'k',
      metaKey: true,
      action: () => setIsCommandPaletteOpen(true),
      description: 'Open command palette',
      category: 'Navigation'
    },
    {
      key: 'k',
      ctrlKey: true,
      action: () => setIsCommandPaletteOpen(true),
      description: 'Open command palette',
      category: 'Navigation'
    },
  ])

  const navigation = [
    { name: 'Dashboard', href: '/' },
    { name: 'Analysis', href: '/analysis' },
    { name: 'Portfolio', href: '/portfolio' },
    { name: 'Watchlist', href: '/watchlist' },
  ]

  return (
    <>
      <header className="sticky top-0 z-40 w-full border-b border-neutral-200 dark:border-dark-border bg-white/80 dark:bg-dark-surface/80 backdrop-blur-md">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex h-16 items-center justify-between">
            {/* Logo */}
            <Link href="/" className="flex items-center gap-2 group">
              <div className="relative">
                <TrendingUp className="w-8 h-8 text-primary-600 dark:text-primary-400 transition-transform group-hover:scale-110" />
                <div className="absolute inset-0 bg-primary-500 blur-xl opacity-0 group-hover:opacity-30 transition-opacity" />
              </div>
              <div className="flex flex-col">
                <span className="text-xl font-bold text-neutral-900 dark:text-dark-text">
                  PulseCompass
                </span>
                <span className="text-xs text-neutral-500 dark:text-neutral-400 -mt-1">
                  Elite Financial Analysis
                </span>
              </div>
            </Link>

            {/* Desktop Navigation */}
            <nav className="hidden md:flex items-center gap-1">
              {navigation.map((item) => (
                <Link
                  key={item.name}
                  href={item.href}
                  className="px-4 py-2 text-sm font-medium text-neutral-700 dark:text-neutral-300 hover:text-neutral-900 dark:hover:text-white hover:bg-neutral-100 dark:hover:bg-neutral-800 rounded-lg transition-colors"
                >
                  {item.name}
                </Link>
              ))}
            </nav>

            {/* Actions */}
            <div className="flex items-center gap-2">
              {/* Command Palette Trigger */}
              <button
                onClick={() => setIsCommandPaletteOpen(true)}
                className="hidden sm:flex items-center gap-2 px-3 py-1.5 text-sm text-neutral-600 dark:text-neutral-400 bg-neutral-100 dark:bg-neutral-800 hover:bg-neutral-200 dark:hover:bg-neutral-700 rounded-lg transition-colors"
              >
                <Search className="w-4 h-4" />
                <span className="hidden lg:inline">Quick actions</span>
                <kbd className="hidden lg:inline-flex items-center gap-1 px-1.5 py-0.5 text-xs font-mono bg-white dark:bg-neutral-900 border border-neutral-300 dark:border-neutral-600 rounded">
                  ⌘K
                </kbd>
              </button>

              {/* Notifications */}
              <button className="p-2 text-neutral-600 dark:text-neutral-400 hover:text-neutral-900 dark:hover:text-white hover:bg-neutral-100 dark:hover:bg-neutral-800 rounded-lg transition-colors relative">
                <Bell className="w-5 h-5" />
                <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-danger-500 rounded-full" />
              </button>

              {/* Theme Toggle */}
              <ThemeToggle />

              {/* Settings */}
              <button className="hidden sm:block p-2 text-neutral-600 dark:text-neutral-400 hover:text-neutral-900 dark:hover:text-white hover:bg-neutral-100 dark:hover:bg-neutral-800 rounded-lg transition-colors">
                <Settings className="w-5 h-5" />
              </button>

              {/* Mobile Menu Toggle */}
              <button
                onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
                className="md:hidden p-2 text-neutral-600 dark:text-neutral-400 hover:text-neutral-900 dark:hover:text-white hover:bg-neutral-100 dark:hover:bg-neutral-800 rounded-lg transition-colors"
              >
                {isMobileMenuOpen ? (
                  <X className="w-5 h-5" />
                ) : (
                  <Menu className="w-5 h-5" />
                )}
              </button>
            </div>
          </div>

          {/* Mobile Navigation */}
          {isMobileMenuOpen && (
            <motion.nav
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="md:hidden py-4 border-t border-neutral-200 dark:border-dark-border"
            >
              {navigation.map((item) => (
                <Link
                  key={item.name}
                  href={item.href}
                  onClick={() => setIsMobileMenuOpen(false)}
                  className="block px-4 py-2 text-base font-medium text-neutral-700 dark:text-neutral-300 hover:text-neutral-900 dark:hover:text-white hover:bg-neutral-100 dark:hover:bg-neutral-800 rounded-lg transition-colors"
                >
                  {item.name}
                </Link>
              ))}
            </motion.nav>
          )}
        </div>
      </header>

      {/* Command Palette */}
      <CommandPalette
        isOpen={isCommandPaletteOpen}
        onClose={() => setIsCommandPaletteOpen(false)}
      />
    </>
  )
}
