'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { 
  FileText, 
  TrendingUp,
  BarChart3, 
  FileSpreadsheet,
  CheckCircle,
  Clock,
  ArrowRight,
  Award,
  Target
} from 'lucide-react'
import Header from '@/components/Header'
import { AnalysisProvider } from '@/contexts/AnalysisContext'
import IntegrityAnalyzerAdvanced from '@/components/IntegrityAnalyzerAdvanced'
import AdvancedRankingSystem from '@/components/AdvancedRankingSystem'

interface ToolCardProps {
  title: string
  description: string
  features: string[]
  icon: any
  status: 'active' | 'coming-soon'
  onClick?: () => void
}

const ToolCard = ({ title, description, features, icon: Icon, status, onClick }: ToolCardProps) => (
  <motion.div
    whileHover={{ y: -4, boxShadow: '0 12px 24px rgba(0,0,0,0.15)' }}
    className="bg-white dark:bg-neutral-800 rounded-xl border border-neutral-200 dark:border-neutral-700 p-6 transition-all"
  >
    <div className="flex items-start justify-between mb-4">
      <div className="w-12 h-12 rounded-lg bg-gradient-to-br from-primary-500 to-primary-600 flex items-center justify-center">
        <Icon className="w-6 h-6 text-white" />
      </div>
      {status === 'coming-soon' && (
        <span className="px-3 py-1 text-xs font-medium bg-warning-100 dark:bg-warning-900/30 text-warning-700 dark:text-warning-400 rounded-full">
          Coming Soon
        </span>
      )}
    </div>
    
    <h3 className="text-xl font-semibold text-neutral-900 dark:text-dark-text mb-2">
      {title}
    </h3>
    
    <p className="text-neutral-600 dark:text-neutral-400 text-sm mb-4 leading-relaxed">
      {description}
    </p>
    
    <div className="space-y-2 mb-6">
      <p className="text-xs font-semibold text-neutral-700 dark:text-neutral-300 uppercase tracking-wide">
        Key Features:
      </p>
      {features.map((feature, idx) => (
        <div key={idx} className="flex items-start gap-2">
          <CheckCircle className="w-4 h-4 text-success-500 flex-shrink-0 mt-0.5" />
          <span className="text-sm text-neutral-600 dark:text-neutral-400">{feature}</span>
        </div>
      ))}
    </div>
    
    <button
      onClick={onClick}
      disabled={status === 'coming-soon'}
      className={`
        w-full py-3 px-4 rounded-lg font-medium transition-all flex items-center justify-center gap-2
        ${status === 'active'
          ? 'bg-gradient-to-r from-primary-600 to-primary-700 text-white hover:from-primary-700 hover:to-primary-800 shadow-md hover:shadow-lg'
          : 'bg-neutral-200 dark:bg-neutral-700 text-neutral-500 dark:text-neutral-400 cursor-not-allowed'
        }
      `}
    >
      {status === 'active' ? (
        <>
          Launch Tool
          <ArrowRight className="w-4 h-4" />
        </>
      ) : (
        <>
          <Clock className="w-4 h-4" />
          Coming Soon
        </>
      )}
    </button>
  </motion.div>
)

function HomePageContent() {
  const [activeModule, setActiveModule] = useState<'dashboard' | 'integrity' | 'ranking' | 'reports'>('dashboard')

  const stats = [
    { label: 'Companies Analyzed', value: '47', icon: Target },
    { label: 'Integrity Score Avg', value: '78.5', icon: Award },
    { label: 'Top Ranked Stock', value: 'TCS', icon: TrendingUp },
    { label: 'Reports Generated', value: '156', icon: FileText },
  ]

  // Render different modules based on activeModule state
  if (activeModule === 'integrity') {
    return <IntegrityAnalyzerAdvanced onBack={() => setActiveModule('dashboard')} />
  }

  if (activeModule === 'ranking') {
    return <AdvancedRankingSystem onBack={() => setActiveModule('dashboard')} />
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-neutral-50 via-white to-neutral-100 dark:from-dark-bg dark:via-dark-bg dark:to-neutral-900">
      <Header />

      <main className="container mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Hero Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-12"
        >
          <h1 className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-primary-600 to-primary-800 bg-clip-text text-transparent mb-4">
            PulseCompass Equity Research Platform
          </h1>
          <p className="text-lg text-neutral-600 dark:text-neutral-400 max-w-2xl mx-auto">
            Professional-grade equity analysis with AI-powered insights
          </p>
        </motion.div>

        {/* Stats Row */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-12"
        >
          {stats.map((stat, idx) => {
            const Icon = stat.icon
            return (
              <div
                key={idx}
                className="bg-white dark:bg-neutral-800 rounded-lg border border-neutral-200 dark:border-neutral-700 p-4 text-center"
              >
                <div className="flex justify-center mb-2">
                  <div className="w-10 h-10 rounded-full bg-primary-100 dark:bg-primary-900/30 flex items-center justify-center">
                    <Icon className="w-5 h-5 text-primary-600 dark:text-primary-400" />
                  </div>
                </div>
                <div className="text-2xl font-bold text-neutral-900 dark:text-dark-text mb-1">
                  {stat.value}
                </div>
                <div className="text-xs text-neutral-600 dark:text-neutral-400">
                  {stat.label}
                </div>
              </div>
            )
          })}
        </motion.div>

        {/* Analysis Tools Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="mb-12"
        >
          <h2 className="text-2xl font-bold text-neutral-900 dark:text-dark-text mb-6">
            Analysis Tools
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
            <ToolCard
              title="Management Integrity Analyzer"
              description="Analyze management credibility through guidance vs delivery tracking. Upload earnings call transcripts and get AI-powered integrity scores with evidence-based insights."
              features={[
                'PDF transcript parsing',
                'AI guidance extraction',
                'Delivery tracking',
                'Evidence-based scoring'
              ]}
              icon={FileText}
              status="active"
              onClick={() => setActiveModule('integrity')}
            />
            
            <ToolCard
              title="Intelligent Stock Ranking System"
              description="Multi-factor analysis engine for all sectors. Ranks companies using proven investment principles with advanced valuation, cash flow quality, and risk assessment."
              features={[
                'Buffett, Lynch & Quality philosophies',
                'Cash flow & valuation analysis',
                'Risk warnings & quality scores',
                'Custom metric weighting'
              ]}
              icon={BarChart3}
              status="active"
              onClick={() => setActiveModule('ranking')}
            />
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <ToolCard
              title="Research Report Analyzer"
              description="Advanced document analysis for research reports, annual reports, and financial statements. Extract key insights and generate comprehensive summaries."
              features={[
                'Multi-document analysis',
                'Key metrics extraction',
                'Trend identification',
                'Risk assessment'
              ]}
              icon={FileSpreadsheet}
              status="coming-soon"
            />
            
            <ToolCard
              title="Portfolio Analytics"
              description="Comprehensive portfolio analysis and optimization tools. Analyze risk-return profiles and generate allocation recommendations."
              features={[
                'Risk-return analysis',
                'Correlation matrices',
                'Optimization algorithms',
                'Performance attribution'
              ]}
              icon={Target}
              status="coming-soon"
            />
          </div>
        </motion.div>

        {/* Getting Started Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="grid grid-cols-1 md:grid-cols-2 gap-6"
        >
          <div className="bg-white dark:bg-neutral-800 rounded-xl border border-neutral-200 dark:border-neutral-700 p-6">
            <h3 className="text-lg font-semibold text-neutral-900 dark:text-dark-text mb-4">
              How to Use
            </h3>
            <div className="space-y-4 text-sm text-neutral-600 dark:text-neutral-400">
              <div>
                <p className="font-semibold text-neutral-900 dark:text-dark-text mb-1">1. Management Integrity Analysis:</p>
                <ul className="list-disc list-inside space-y-1 ml-2">
                  <li>Upload PDF transcripts of earnings calls</li>
                  <li>System extracts guidance statements</li>
                  <li>Get integrity scores with evidence</li>
                </ul>
              </div>
              <div>
                <p className="font-semibold text-neutral-900 dark:text-dark-text mb-1">2. Financial Ranking:</p>
                <ul className="list-disc list-inside space-y-1 ml-2">
                  <li>Upload CSV/Excel data from screeners</li>
                  <li>Apply investment philosophies</li>
                  <li>Get ranked company lists</li>
                </ul>
              </div>
            </div>
          </div>
          
          <div className="bg-white dark:bg-neutral-800 rounded-xl border border-neutral-200 dark:border-neutral-700 p-6">
            <h3 className="text-lg font-semibold text-neutral-900 dark:text-dark-text mb-4">
              System Requirements
            </h3>
            <div className="space-y-4 text-sm text-neutral-600 dark:text-neutral-400">
              <div>
                <p className="font-semibold text-neutral-900 dark:text-dark-text mb-1">Supported File Types:</p>
                <ul className="list-disc list-inside space-y-1 ml-2">
                  <li>PDF files for transcripts</li>
                  <li>CSV/Excel files for financial data</li>
                  <li>DOCX files for reports</li>
                </ul>
              </div>
              <div>
                <p className="font-semibold text-neutral-900 dark:text-dark-text mb-1">Analysis Features:</p>
                <ul className="list-disc list-inside space-y-1 ml-2">
                  <li>AI-powered text extraction</li>
                  <li>Multiple investment philosophies</li>
                  <li>Evidence-based scoring</li>
                </ul>
              </div>
            </div>
          </div>
        </motion.div>
      </main>
    </div>
  )
}

export default function HomePage() {
  return (
    <AnalysisProvider>
      <HomePageContent />
    </AnalysisProvider>
  )
}
