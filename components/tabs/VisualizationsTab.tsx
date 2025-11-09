'use client'

import { motion } from 'framer-motion'
import { PieChart, BarChart3 } from 'lucide-react'

export default function VisualizationsTab({ result }: any) {
  return (
    <motion.div
      key="visualizations"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="space-y-6"
    >
      <div className="bg-white dark:bg-dark-surface rounded-xl border border-neutral-200 dark:border-dark-border p-8">
        <div className="flex items-center gap-3 mb-6">
          <PieChart className="w-6 h-6 text-primary-600 dark:text-primary-400" />
          <h2 className="text-2xl font-bold text-neutral-900 dark:text-dark-text">
            Performance Visualizations
          </h2>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Top Performers Bar Chart */}
          <div className="p-6 bg-neutral-50 dark:bg-neutral-800 rounded-lg">
            <h3 className="text-lg font-semibold text-neutral-900 dark:text-dark-text mb-4">
              Top 10 Performers
            </h3>
            <div className="space-y-3">
              {result.rankings.slice(0, 10).map((company: any, idx: number) => (
                <div key={idx} className="flex items-center justify-between">
                  <span className="text-sm text-neutral-700 dark:text-neutral-300 truncate w-32">
                    {company.company}
                  </span>
                  <div className="flex items-center gap-2 flex-1 ml-4">
                    <div className="flex-1 h-2 bg-neutral-200 dark:bg-neutral-700 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-gradient-to-r from-primary-600 to-primary-400 rounded-full"
                        style={{ width: `${company.compositeScore}%` }}
                      />
                    </div>
                    <span className="text-sm font-semibold text-neutral-900 dark:text-dark-text w-12 text-right">
                      {company.compositeScore.toFixed(1)}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Score Distribution */}
          <div className="p-6 bg-neutral-50 dark:bg-neutral-800 rounded-lg">
            <h3 className="text-lg font-semibold text-neutral-900 dark:text-dark-text mb-4">
              Score Distribution
            </h3>
            <div className="space-y-4">
              {[
                { range: '80-100', count: result.rankings.filter((c: any) => c.compositeScore >= 80).length, color: 'bg-success-500' },
                { range: '60-79', count: result.rankings.filter((c: any) => c.compositeScore >= 60 && c.compositeScore < 80).length, color: 'bg-warning-500' },
                { range: '40-59', count: result.rankings.filter((c: any) => c.compositeScore >= 40 && c.compositeScore < 60).length, color: 'bg-orange-500' },
                { range: '0-39', count: result.rankings.filter((c: any) => c.compositeScore < 40).length, color: 'bg-error-500' }
              ].map((bucket, idx) => (
                <div key={idx}>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-neutral-700 dark:text-neutral-300">{bucket.range}</span>
                    <span className="font-semibold text-neutral-900 dark:text-dark-text">{bucket.count} companies</span>
                  </div>
                  <div className="h-3 bg-neutral-200 dark:bg-neutral-700 rounded-full overflow-hidden">
                    <div
                      className={`h-full ${bucket.color} rounded-full transition-all`}
                      style={{ width: `${(bucket.count / result.rankings.length) * 100}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Philosophy Comparison */}
          <div className="p-6 bg-neutral-50 dark:bg-neutral-800 rounded-lg md:col-span-2">
            <h3 className="text-lg font-semibold text-neutral-900 dark:text-dark-text mb-4 flex items-center gap-2">
              <BarChart3 className="w-5 h-5" />
              Philosophy Score Comparison (Top 5)
            </h3>
            <div className="space-y-4">
              {result.rankings.slice(0, 5).map((company: any, idx: number) => (
                <div key={idx} className="space-y-2">
                  <div className="font-medium text-neutral-900 dark:text-dark-text">
                    {idx + 1}. {company.company}
                  </div>
                  <div className="grid grid-cols-3 gap-3">
                    <div>
                      <div className="text-xs text-neutral-600 dark:text-neutral-400 mb-1">Buffett</div>
                      <div className="flex items-center gap-2">
                        <div className="flex-1 h-2 bg-neutral-200 dark:bg-neutral-700 rounded-full overflow-hidden">
                          <div
                            className="h-full bg-blue-500 rounded-full"
                            style={{ width: `${company.buffettScore}%` }}
                          />
                        </div>
                        <span className="text-xs font-semibold w-8">{company.buffettScore.toFixed(0)}</span>
                      </div>
                    </div>
                    <div>
                      <div className="text-xs text-neutral-600 dark:text-neutral-400 mb-1">Lynch</div>
                      <div className="flex items-center gap-2">
                        <div className="flex-1 h-2 bg-neutral-200 dark:bg-neutral-700 rounded-full overflow-hidden">
                          <div
                            className="h-full bg-green-500 rounded-full"
                            style={{ width: `${company.lynchScore}%` }}
                          />
                        </div>
                        <span className="text-xs font-semibold w-8">{company.lynchScore.toFixed(0)}</span>
                      </div>
                    </div>
                    <div>
                      <div className="text-xs text-neutral-600 dark:text-neutral-400 mb-1">Growth</div>
                      <div className="flex items-center gap-2">
                        <div className="flex-1 h-2 bg-neutral-200 dark:bg-neutral-700 rounded-full overflow-hidden">
                          <div
                            className="h-full bg-purple-500 rounded-full"
                            style={{ width: `${company.growthScore}%` }}
                          />
                        </div>
                        <span className="text-xs font-semibold w-8">{company.growthScore.toFixed(0)}</span>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  )
}
