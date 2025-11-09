'use client'

import { motion } from 'framer-motion'
import { Lightbulb, Download } from 'lucide-react'
import { exportPhilosophyRankings } from '@/utils/csvExport'

const philosophyDetails = {
  buffett: {
    name: "Warren Buffett Investment Philosophy",
    icon: "🎯",
    description: "Warren Buffett's investment approach focuses on identifying companies with strong fundamentals, sustainable competitive advantages, and excellent management. His philosophy emphasizes long-term value investing rather than short-term market fluctuations.",
    principles: [
      {
        title: "Consistent ROE",
        description: "Return on equity consistently above 15% indicates a company with a sustainable competitive advantage"
      },
      {
        title: "Low Debt",
        description: "Low debt-to-equity ratio (< 0.5) shows strong financial position and reduced risk"
      },
      {
        title: "High Margins",
        description: "High operating profit margins (> 20%) indicate pricing power and competitive advantage"
      },
      {
        title: "Earnings Growth",
        description: "Consistent earnings growth over 5+ years shows business strength and management capability"
      },
      {
        title: "Economic Moat",
        description: "Companies with strong competitive advantages that protect market share and profitability"
      }
    ]
  },
  lynch: {
    name: "Peter Lynch Investment Philosophy",
    icon: "📈",
    description: "Peter Lynch's investment strategy focuses on finding companies with good growth at reasonable prices. He believes in investing in what you know and understand, and looks for companies with strong growth potential that are undervalued by the market.",
    principles: [
      {
        title: "PEG Ratio",
        description: "Price/Earnings to Growth ratio < 1 is excellent, < 2 is good - shows growth at reasonable price"
      },
      {
        title: "Growth Potential",
        description: "Companies with strong growth potential in sales and earnings"
      },
      {
        title: "Reasonable P/E",
        description: "P/E ratio should be reasonable relative to growth rate"
      },
      {
        title: "Strong Balance Sheet",
        description: "Low debt and strong financial position"
      },
      {
        title: "Cash Flow",
        description: "Strong and consistent cash flow generation"
      }
    ]
  }
}

export default function PhilosophiesTab({ result }: any) {
  const renderPhilosophySection = (philosophyKey: 'buffett' | 'lynch', scoreKey: 'buffettScore' | 'lynchScore') => {
    const philosophy = philosophyDetails[philosophyKey]
    const topCompanies = [...result.rankings]
      .sort((a: any, b: any) => b[scoreKey] - a[scoreKey])
      .slice(0, 10)

    return (
      <div className="bg-white dark:bg-dark-surface rounded-xl border border-neutral-200 dark:border-dark-border p-8">
        <div className="flex items-center gap-3 mb-6">
          <span className="text-4xl">{philosophy.icon}</span>
          <div>
            <h2 className="text-2xl font-bold text-neutral-900 dark:text-dark-text">
              {philosophy.name}
            </h2>
            <button 
              onClick={() => exportPhilosophyRankings(result.rankings, philosophyKey, scoreKey)}
              className="text-sm text-primary-600 dark:text-primary-400 hover:underline flex items-center gap-1 mt-1"
            >
              <Download className="w-3 h-3" />
              Download {philosophyKey === 'buffett' ? 'Buffett' : 'Lynch'} Companies CSV
            </button>
          </div>
        </div>

        <p className="text-neutral-600 dark:text-neutral-400 mb-6 leading-relaxed">
          {philosophy.description}
        </p>

        <div className="mb-8">
          <h3 className="text-lg font-semibold text-neutral-900 dark:text-dark-text mb-4">
            Key Principles
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {philosophy.principles.map((principle, idx) => (
              <div key={idx} className="p-4 bg-neutral-50 dark:bg-neutral-800 rounded-lg">
                <div className="flex items-start gap-3">
                  <div className="w-8 h-8 rounded-full bg-primary-100 dark:bg-primary-900/30 flex items-center justify-center flex-shrink-0">
                    <Lightbulb className="w-4 h-4 text-primary-600 dark:text-primary-400" />
                  </div>
                  <div>
                    <h4 className="font-semibold text-neutral-900 dark:text-dark-text mb-1">
                      {principle.title}
                    </h4>
                    <p className="text-sm text-neutral-600 dark:text-neutral-400">
                      {principle.description}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div>
          <h3 className="text-lg font-semibold text-neutral-900 dark:text-dark-text mb-4">
            Top Companies Matching {philosophyKey === 'buffett' ? "Buffett's" : "Lynch's"} Criteria
          </h3>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-neutral-50 dark:bg-neutral-800 border-b border-neutral-200 dark:border-neutral-700">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-neutral-500 dark:text-neutral-400 uppercase">
                    Rank
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-neutral-500 dark:text-neutral-400 uppercase">
                    Name
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-neutral-500 dark:text-neutral-400 uppercase">
                    NSE Code
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-neutral-500 dark:text-neutral-400 uppercase">
                    {philosophyKey === 'buffett' ? 'Buffett' : 'Lynch'} Score
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-neutral-500 dark:text-neutral-400 uppercase">
                    Overall Rank
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-neutral-200 dark:divide-neutral-700">
                {topCompanies.map((company: any, idx: number) => (
                  <tr key={idx} className="hover:bg-neutral-50 dark:hover:bg-neutral-800 transition-colors">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="text-lg font-bold text-primary-600 dark:text-primary-400">
                        {idx + 1}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <div className="font-semibold text-neutral-900 dark:text-dark-text">
                        {company.company}
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="text-sm text-neutral-600 dark:text-neutral-400">
                        {company.symbol}
                      </div>
                    </td>
                    <td className="px-6 py-4 text-right">
                      <span className="text-lg font-bold text-success-600 dark:text-success-400">
                        {company[scoreKey].toFixed(1)}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-right">
                      <span className="text-neutral-700 dark:text-neutral-300">
                        {company.rank}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    )
  }

  return (
    <motion.div
      key="philosophies"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="space-y-6"
    >
      {renderPhilosophySection('buffett', 'buffettScore')}
      {renderPhilosophySection('lynch', 'lynchScore')}
    </motion.div>
  )
}
