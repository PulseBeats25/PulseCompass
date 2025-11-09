'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { 
  Upload, 
  FileText, 
  CheckCircle, 
  AlertCircle,
  TrendingUp,
  TrendingDown,
  Loader2,
  ArrowLeft,
  Download
} from 'lucide-react'

interface IntegrityResult {
  company: string
  overallScore: number
  categories: {
    [key: string]: {
      score: number
      status: string
      evidence: string[]
    }
  }
  guidanceStatements: Array<{
    category: string
    statement: string
    confidence: string
    sentiment: string
  }>
  keyFindings: string[]
}

interface IntegrityAnalyzerProps {
  onBack: () => void
}

export default function IntegrityAnalyzer({ onBack }: IntegrityAnalyzerProps) {
  const [files, setFiles] = useState<File[]>([])
  const [companyName, setCompanyName] = useState('')
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [result, setResult] = useState<IntegrityResult | null>(null)
  const [error, setError] = useState<string | null>(null)

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setFiles(Array.from(e.target.files))
      setError(null)
    }
  }

  const handleAnalyze = async () => {
    if (files.length === 0) {
      setError('Please upload at least one PDF transcript')
      return
    }

    if (!companyName.trim()) {
      setError('Please enter a company name')
      return
    }

    setIsAnalyzing(true)
    setError(null)

    try {
      const formData = new FormData()
      files.forEach(file => formData.append('files', file))
      formData.append('company_name', companyName)

      const response = await fetch('http://localhost:8000/api/v1/integrity/analyze', {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        throw new Error('Analysis failed')
      }

      const data = await response.json()
      setResult(data)
    } catch (err) {
      setError('Failed to analyze transcripts. Please try again.')
      console.error(err)
    } finally {
      setIsAnalyzing(false)
    }
  }

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-success-600 dark:text-success-400'
    if (score >= 60) return 'text-warning-600 dark:text-warning-400'
    return 'text-danger-600 dark:text-danger-400'
  }

  const getScoreBackground = (score: number) => {
    if (score >= 80) return 'bg-success-100 dark:bg-success-900/30'
    if (score >= 60) return 'bg-warning-100 dark:bg-warning-900/30'
    return 'bg-danger-100 dark:bg-danger-900/30'
  }

  return (
    <div className="min-h-screen bg-neutral-50 dark:bg-neutral-900 py-8">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <button
            onClick={onBack}
            className="flex items-center gap-2 text-neutral-600 dark:text-neutral-400 hover:text-neutral-900 dark:hover:text-white mb-4"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to Dashboard
          </button>
          <h1 className="text-3xl font-bold text-neutral-900 dark:text-dark-text mb-2">
            Management Integrity Analyzer
          </h1>
          <p className="text-neutral-600 dark:text-neutral-400">
            Upload earnings call transcripts to analyze management credibility and guidance delivery
          </p>
        </div>

        {!result ? (
          /* Upload Section */
          <div className="max-w-3xl mx-auto">
            <div className="bg-white dark:bg-neutral-800 rounded-xl border border-neutral-200 dark:border-neutral-700 p-8">
              {/* Company Name Input */}
              <div className="mb-6">
                <label className="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-2">
                  Company Name
                </label>
                <input
                  type="text"
                  value={companyName}
                  onChange={(e) => setCompanyName(e.target.value)}
                  placeholder="e.g., Infosys Limited"
                  className="w-full px-4 py-3 rounded-lg border border-neutral-300 dark:border-neutral-600 bg-white dark:bg-neutral-800 text-neutral-900 dark:text-dark-text focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                />
              </div>

              {/* File Upload */}
              <div className="mb-6">
                <label className="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-2">
                  Upload Transcripts (PDF)
                </label>
                <div className="border-2 border-dashed border-neutral-300 dark:border-neutral-600 rounded-lg p-8 text-center hover:border-primary-500 transition-colors">
                  <input
                    type="file"
                    accept=".pdf"
                    multiple
                    onChange={handleFileChange}
                    className="hidden"
                    id="file-upload"
                  />
                  <label htmlFor="file-upload" className="cursor-pointer">
                    <Upload className="w-12 h-12 text-neutral-400 mx-auto mb-4" />
                    <p className="text-neutral-600 dark:text-neutral-400 mb-2">
                      Click to upload or drag and drop
                    </p>
                    <p className="text-sm text-neutral-500 dark:text-neutral-500">
                      PDF files only (multiple files supported)
                    </p>
                  </label>
                </div>

                {files.length > 0 && (
                  <div className="mt-4 space-y-2">
                    {files.map((file, idx) => (
                      <div
                        key={idx}
                        className="flex items-center gap-2 p-3 bg-neutral-50 dark:bg-neutral-800 rounded-lg"
                      >
                        <FileText className="w-5 h-5 text-primary-600 dark:text-primary-400" />
                        <span className="text-sm text-neutral-900 dark:text-dark-text flex-1">
                          {file.name}
                        </span>
                        <span className="text-xs text-neutral-500">
                          {(file.size / 1024 / 1024).toFixed(2)} MB
                        </span>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {error && (
                <div className="mb-6 p-4 bg-danger-50 dark:bg-danger-900/20 border border-danger-200 dark:border-danger-800 rounded-lg flex items-start gap-3">
                  <AlertCircle className="w-5 h-5 text-danger-600 dark:text-danger-400 flex-shrink-0 mt-0.5" />
                  <p className="text-sm text-danger-700 dark:text-danger-300">{error}</p>
                </div>
              )}

              {/* Analyze Button */}
              <button
                onClick={handleAnalyze}
                disabled={isAnalyzing || files.length === 0 || !companyName.trim()}
                className="w-full py-3 px-6 bg-gradient-to-r from-primary-600 to-primary-700 text-white rounded-lg font-medium hover:from-primary-700 hover:to-primary-800 disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center justify-center gap-2"
              >
                {isAnalyzing ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    Analyzing Transcripts...
                  </>
                ) : (
                  <>
                    <CheckCircle className="w-5 h-5" />
                    Analyze Integrity
                  </>
                )}
              </button>
            </div>
          </div>
        ) : (
          /* Results Section */
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-6"
          >
            {/* Overall Score Card */}
            <div className="bg-white dark:bg-neutral-800 rounded-xl border border-neutral-200 dark:border-neutral-700 p-8">
              <div className="text-center">
                <h2 className="text-2xl font-bold text-neutral-900 dark:text-dark-text mb-2">
                  {result.company}
                </h2>
                <div className="flex items-center justify-center gap-4 mb-4">
                  <div className={`text-6xl font-bold ${getScoreColor(result.overallScore)}`}>
                    {result.overallScore}
                  </div>
                  <div className="text-left">
                    <div className="text-sm text-neutral-600 dark:text-neutral-400">
                      Overall Integrity Score
                    </div>
                    <div className="flex items-center gap-2">
                      {result.overallScore >= 80 ? (
                        <TrendingUp className="w-5 h-5 text-success-600" />
                      ) : (
                        <TrendingDown className="w-5 h-5 text-warning-600" />
                      )}
                      <span className="text-sm font-medium text-neutral-700 dark:text-neutral-300">
                        {result.overallScore >= 80 ? 'Excellent' : result.overallScore >= 60 ? 'Good' : 'Fair'}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Category Scores */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {Object.entries(result.categories).map(([category, data]) => (
                <div
                  key={category}
                  className="bg-white dark:bg-neutral-800 rounded-xl border border-neutral-200 dark:border-neutral-700 p-6"
                >
                  <div className="flex items-start justify-between mb-4">
                    <h3 className="text-lg font-semibold text-neutral-900 dark:text-dark-text">
                      {category}
                    </h3>
                    <div className={`px-3 py-1 rounded-full text-sm font-medium ${getScoreBackground(data.score)} ${getScoreColor(data.score)}`}>
                      {data.score}%
                    </div>
                  </div>
                  <div className="mb-3">
                    <span className="text-sm font-medium text-neutral-700 dark:text-neutral-300">
                      Status: {data.status}
                    </span>
                  </div>
                  <div className="space-y-2">
                    {data.evidence.map((evidence, idx) => (
                      <div key={idx} className="text-sm text-neutral-600 dark:text-neutral-400 pl-4 border-l-2 border-neutral-200 dark:border-neutral-700">
                        {evidence}
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>

            {/* Key Findings */}
            <div className="bg-white dark:bg-neutral-800 rounded-xl border border-neutral-200 dark:border-neutral-700 p-6">
              <h3 className="text-lg font-semibold text-neutral-900 dark:text-dark-text mb-4">
                Key Findings
              </h3>
              <div className="space-y-3">
                {result.keyFindings.map((finding, idx) => (
                  <div key={idx} className="flex items-start gap-3">
                    <CheckCircle className="w-5 h-5 text-primary-600 dark:text-primary-400 flex-shrink-0 mt-0.5" />
                    <p className="text-neutral-700 dark:text-neutral-300">{finding}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* Actions */}
            <div className="flex gap-4">
              <button
                onClick={() => {
                  setResult(null)
                  setFiles([])
                  setCompanyName('')
                }}
                className="flex-1 py-3 px-6 bg-white dark:bg-neutral-800 border border-neutral-300 dark:border-neutral-600 text-neutral-700 dark:text-neutral-300 rounded-lg font-medium hover:bg-neutral-50 dark:hover:bg-neutral-700 transition-all"
              >
                Analyze Another Company
              </button>
              <button
                className="flex-1 py-3 px-6 bg-gradient-to-r from-primary-600 to-primary-700 text-white rounded-lg font-medium hover:from-primary-700 hover:to-primary-800 transition-all flex items-center justify-center gap-2"
              >
                <Download className="w-5 h-5" />
                Export Report
              </button>
            </div>
          </motion.div>
        )}
      </div>
    </div>
  )
}
