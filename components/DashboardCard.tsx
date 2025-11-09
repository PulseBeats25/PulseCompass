'use client'

import { LucideIcon } from 'lucide-react'
import { motion } from 'framer-motion'

interface DashboardCardProps {
  title: string
  value: string
  change?: number
  changePercent?: number
  subtitle?: string
  icon: LucideIcon
  variant?: 'default' | 'success' | 'warning' | 'danger'
}

export default function DashboardCard({
  title,
  value,
  change,
  changePercent,
  subtitle,
  icon: Icon,
  variant = 'default'
}: DashboardCardProps) {
  const getVariantStyles = () => {
    switch (variant) {
      case 'success':
        return 'border-l-success-500 bg-gradient-to-br from-success-50 to-white'
      case 'warning':
        return 'border-l-warning-500 bg-gradient-to-br from-warning-50 to-white'
      case 'danger':
        return 'border-l-danger-500 bg-gradient-to-br from-danger-50 to-white'
      default:
        return 'border-l-primary-500 bg-gradient-to-br from-primary-50 to-white'
    }
  }

  const getIconColor = () => {
    switch (variant) {
      case 'success':
        return 'text-success-600'
      case 'warning':
        return 'text-warning-600'
      case 'danger':
        return 'text-danger-600'
      default:
        return 'text-primary-600'
    }
  }

  const getChangeColor = () => {
    if (!change) return ''
    return change >= 0 ? 'text-success-600' : 'text-danger-600'
  }

  return (
    <motion.div
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      className={`card card-hover border-l-4 ${getVariantStyles()}`}
    >
      <div className="flex items-center justify-between">
        <div className="flex-1">
          <p className="text-sm font-medium text-gray-600 mb-1">{title}</p>
          <p className="text-2xl font-bold text-gray-900 mb-1">{value}</p>
          
          {change !== undefined && changePercent !== undefined && (
            <div className={`flex items-center text-sm ${getChangeColor()}`}>
              <span className="font-medium">
                {change >= 0 ? '+' : ''}₹{change.toLocaleString()}
              </span>
              <span className="ml-2">
                ({changePercent >= 0 ? '+' : ''}{typeof changePercent === 'number' ? changePercent.toFixed(2) : '0.00'}%)
              </span>
            </div>
          )}
          
          {subtitle && (
            <p className="text-sm text-gray-500">{subtitle}</p>
          )}
        </div>
        
        <div className={`p-3 rounded-xl bg-white shadow-sm ${getIconColor()}`}>
          <Icon className="w-6 h-6" />
        </div>
      </div>
    </motion.div>
  )
}
