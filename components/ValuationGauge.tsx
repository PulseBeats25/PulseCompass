'use client'

import { motion } from 'framer-motion'

interface ValuationGaugeProps {
  score: number // 0-10 scale
  label: string
  description?: string
}

export default function ValuationGauge({ score, label, description }: ValuationGaugeProps) {
  const getColor = (score: number) => {
    if (score >= 8) return '#22c55e' // green
    if (score >= 6) return '#f59e0b' // yellow
    if (score >= 4) return '#f97316' // orange
    return '#ef4444' // red
  }

  const getRecommendation = (score: number) => {
    if (score >= 8) return 'Strong Buy'
    if (score >= 6) return 'Buy'
    if (score >= 4) return 'Hold'
    return 'Avoid'
  }

  const circumference = 2 * Math.PI * 45
  const strokeDasharray = circumference
  const strokeDashoffset = circumference - (score / 10) * circumference

  return (
    <div className="flex flex-col items-center p-6 bg-white rounded-xl shadow-sm border border-gray-200">
      <div className="relative w-32 h-32 mb-4">
        <svg className="w-32 h-32 transform -rotate-90" viewBox="0 0 100 100">
          {/* Background circle */}
          <circle
            cx="50"
            cy="50"
            r="45"
            stroke="#e5e7eb"
            strokeWidth="8"
            fill="none"
          />
          
          {/* Progress circle */}
          <motion.circle
            cx="50"
            cy="50"
            r="45"
            stroke={getColor(score)}
            strokeWidth="8"
            fill="none"
            strokeLinecap="round"
            strokeDasharray={strokeDasharray}
            strokeDashoffset={strokeDashoffset}
            initial={{ strokeDashoffset: circumference }}
            animate={{ strokeDashoffset }}
            transition={{ duration: 1.5, ease: "easeOut" }}
          />
        </svg>
        
        {/* Score display */}
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="text-center">
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ duration: 0.5, delay: 0.5 }}
              className="text-2xl font-bold text-gray-900"
            >
              {score.toFixed(1)}
            </motion.div>
            <div className="text-xs text-gray-500">/ 10</div>
          </div>
        </div>
      </div>
      
      <div className="text-center">
        <h3 className="text-lg font-semibold text-gray-900 mb-1">{label}</h3>
        <div className={`inline-block px-3 py-1 rounded-full text-sm font-medium ${
          score >= 8 ? 'bg-success-100 text-success-800' :
          score >= 6 ? 'bg-warning-100 text-warning-800' :
          score >= 4 ? 'bg-orange-100 text-orange-800' :
          'bg-danger-100 text-danger-800'
        }`}>
          {getRecommendation(score)}
        </div>
        {description && (
          <p className="text-sm text-gray-600 mt-2">{description}</p>
        )}
      </div>
    </div>
  )
}
