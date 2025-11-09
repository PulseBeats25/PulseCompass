'use client'

import { motion } from 'framer-motion'
import { LucideIcon, TrendingUp, TrendingDown, Minus } from 'lucide-react'
import { formatCurrency, formatNumber, formatPercentage } from '@/utils/exportData'

interface MetricCardProps {
  title: string
  value: number | string
  change?: number
  changeLabel?: string
  icon?: LucideIcon
  format?: 'currency' | 'percentage' | 'number' | 'custom'
  trend?: 'up' | 'down' | 'neutral'
  subtitle?: string
  color?: 'primary' | 'success' | 'warning' | 'danger' | 'neutral'
  size?: 'sm' | 'md' | 'lg'
  loading?: boolean
}

export default function MetricCard({
  title,
  value,
  change,
  changeLabel,
  icon: Icon,
  format = 'number',
  trend,
  subtitle,
  color = 'primary',
  size = 'md',
  loading = false,
}: MetricCardProps) {
  const formatValue = (val: number | string) => {
    if (typeof val === 'string') return val
    
    switch (format) {
      case 'currency':
        return formatCurrency(val)
      case 'percentage':
        return formatPercentage(val)
      case 'number':
        return formatNumber(val)
      default:
        return val
    }
  }

  const getTrendIcon = () => {
    if (trend === 'up' || (change !== undefined && change > 0)) {
      return <TrendingUp className="w-4 h-4" />
    }
    if (trend === 'down' || (change !== undefined && change < 0)) {
      return <TrendingDown className="w-4 h-4" />
    }
    return <Minus className="w-4 h-4" />
  }

  const getTrendColor = () => {
    if (trend === 'up' || (change !== undefined && change > 0)) {
      return 'text-success-600 dark:text-success-400 bg-success-50 dark:bg-success-950/30'
    }
    if (trend === 'down' || (change !== undefined && change < 0)) {
      return 'text-danger-600 dark:text-danger-400 bg-danger-50 dark:bg-danger-950/30'
    }
    return 'text-neutral-600 dark:text-neutral-400 bg-neutral-50 dark:bg-neutral-900'
  }

  const getColorClasses = () => {
    const colors = {
      primary: 'text-primary-600 dark:text-primary-400 bg-primary-50 dark:bg-primary-950/30',
      success: 'text-success-600 dark:text-success-400 bg-success-50 dark:bg-success-950/30',
      warning: 'text-warning-600 dark:text-warning-400 bg-warning-50 dark:bg-warning-950/30',
      danger: 'text-danger-600 dark:text-danger-400 bg-danger-50 dark:bg-danger-950/30',
      neutral: 'text-neutral-600 dark:text-neutral-400 bg-neutral-50 dark:bg-neutral-900',
    }
    return colors[color]
  }

  const getSizeClasses = () => {
    const sizes = {
      sm: {
        container: 'p-4',
        value: 'text-2xl',
        title: 'text-xs',
        icon: 'w-8 h-8 p-1.5',
      },
      md: {
        container: 'p-6',
        value: 'text-3xl',
        title: 'text-sm',
        icon: 'w-10 h-10 p-2',
      },
      lg: {
        container: 'p-8',
        value: 'text-4xl',
        title: 'text-base',
        icon: 'w-12 h-12 p-2.5',
      },
    }
    return sizes[size]
  }

  const sizeClasses = getSizeClasses()

  if (loading) {
    return (
      <div className={`card ${sizeClasses.container}`}>
        <div className="animate-pulse">
          <div className="h-4 bg-neutral-200 dark:bg-neutral-800 rounded w-1/2 mb-4" />
          <div className="h-8 bg-neutral-200 dark:bg-neutral-800 rounded w-3/4 mb-2" />
          <div className="h-3 bg-neutral-200 dark:bg-neutral-800 rounded w-1/3" />
        </div>
      </div>
    )
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ y: -4, boxShadow: '0 8px 24px rgba(0, 0, 0, 0.12)' }}
      transition={{ type: 'spring', stiffness: 300, damping: 20 }}
      className={`card ${sizeClasses.container} relative overflow-hidden group`}
    >
      {/* Background Gradient */}
      <div className="absolute inset-0 bg-gradient-to-br from-transparent to-neutral-50 dark:to-neutral-900/50 opacity-0 group-hover:opacity-100 transition-opacity" />

      <div className="relative">
        {/* Header */}
        <div className="flex items-start justify-between mb-4">
          <div className="flex-1">
            <p className={`${sizeClasses.title} font-medium text-neutral-600 dark:text-neutral-400 uppercase tracking-wide`}>
              {title}
            </p>
          </div>
          {Icon && (
            <div className={`${sizeClasses.icon} ${getColorClasses()} rounded-lg flex items-center justify-center flex-shrink-0`}>
              <Icon className="w-full h-full" />
            </div>
          )}
        </div>

        {/* Value */}
        <div className={`${sizeClasses.value} font-bold text-neutral-900 dark:text-dark-text tabular-nums mb-2`}>
          {formatValue(value)}
        </div>

        {/* Change & Subtitle */}
        <div className="flex items-center gap-3">
          {change !== undefined && (
            <div className={`flex items-center gap-1 px-2 py-1 rounded-md text-sm font-semibold ${getTrendColor()}`}>
              {getTrendIcon()}
              <span>
                {change > 0 && '+'}
                {format === 'percentage' ? formatPercentage(change) : formatNumber(change, 2)}
              </span>
            </div>
          )}
          {(changeLabel || subtitle) && (
            <span className="text-sm text-neutral-600 dark:text-neutral-400">
              {changeLabel || subtitle}
            </span>
          )}
        </div>
      </div>

      {/* Decorative Element */}
      <div className="absolute -right-4 -bottom-4 w-24 h-24 bg-gradient-to-br from-primary-500/10 to-transparent rounded-full blur-2xl opacity-0 group-hover:opacity-100 transition-opacity" />
    </motion.div>
  )
}
