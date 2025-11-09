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
  Download,
  Calendar,
  Target,
  Award,
  LineChart as LineChartIcon
} from 'lucide-react'
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend, 
  ResponsiveContainer,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar
} from 'recharts'

interface QuarterAnalysis {
  quarter: string
  score: number
  highlights: string[]
  concerns: string[]
  guidance: Array<{
    type: string
    details: string
  }>
  ai_analysis?: {
    financial_performance: {
      revenue_growth: string
      margin_trend: string
      profitability: string
      key_metrics: string[]
    }
    strategic_initiatives: string[]
    market_position: {
      competitive_advantage: string
      market_share: string
      customer_dynamics: string
    }
    management_quality: {
      credibility_score: number
      transparency: string
      execution: string
    }
    risks_concerns: string[]
    forward_guidance: string[]
    key_insights: string[]
    investment_thesis: string
  }
  metrics: {
    revenue_mentions: number
    margin_mentions: number
    growth_mentions: number
    positive_indicators: number
    concern_indicators: number
  }
}

interface GuidanceTracking {
  quarter: string
  guidance: string
  next_quarter: string
  status: string
  evidence: string
}

interface IntegrityResult {
  company: string
  overallScore: number
  quartersAnalyzed: number
  quarters: QuarterAnalysis[]
  comparison: {
    trend: string
    guidance_tracking: GuidanceTracking[]
    performance_summary: string
    score_progression: Array<{
      quarter: string
      score: number
    }>
  }
  summary: {
    trend: string
    averageScore: number
    guidanceDelivery: string
  }
}

interface IntegrityAnalyzerProps {
  onBack: () => void
}

export default function IntegrityAnalyzerAdvanced({ onBack }: IntegrityAnalyzerProps) {
  const [files, setFiles] = useState<File[]>([])
  const [companyName, setCompanyName] = useState('')
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [result, setResult] = useState<IntegrityResult | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [model, setModel] = useState<string>('')
  const [temperature, setTemperature] = useState<number>(0.1)
  const [excelFile, setExcelFile] = useState<File | null>(null)
  const [excelResult, setExcelResult] = useState<any | null>(null)

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setFiles(Array.from(e.target.files))
      setError(null)
    }
  }

  const handleExcelFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setExcelFile(e.target.files[0])
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
      if (model) formData.append('model', model)
      formData.append('temperature', String(temperature))

      const response = await fetch('http://localhost:8000/api/v1/integrity/analyze', {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        const errorText = await response.text()
        console.error('API Error:', errorText)
        throw new Error(`Analysis failed: ${response.status}`)
      }

      const data = await response.json()
      console.log('Analysis result:', data)
      
      // Validate the response structure
      if (!data || !data.quarters || !Array.isArray(data.quarters)) {
        console.error('Invalid response structure:', data)
        throw new Error('Invalid response from server')
      }
      
      setResult(data)
    } catch (err: any) {
      const errorMsg = err.message || 'Failed to analyze transcripts. Please try again.'
      setError(errorMsg)
      console.error('Analysis error:', err)
    } finally {
      setIsAnalyzing(false)
    }
  }

  const handleExport = async () => {
    if (!result) return
    try {
      const response = await fetch('http://localhost:8000/api/v1/integrity/export', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(result)
      })
      if (!response.ok) throw new Error('Export failed')
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `${result.company.replace(/\s+/g,'_')}_integrity_report.csv`
      document.body.appendChild(a)
      a.click()
      a.remove()
      window.URL.revokeObjectURL(url)
    } catch (e) {
      console.error('Export error', e)
      setError('Failed to export report')
    }
  }

  const handleRankExcel = async () => {
    if (!excelFile) {
      setError('Please upload an Excel file (.xlsx or .xls)')
      return
    }
    setIsAnalyzing(true)
    setError(null)
    try {
      const formData = new FormData()
      formData.append('file', excelFile)
      const response = await fetch('http://localhost:8000/api/v1/integrity/rank_excel', {
        method: 'POST',
        body: formData,
      })
      if (!response.ok) {
        const t = await response.text()
        throw new Error(t || 'Failed to rank Excel')
      }
      const data = await response.json()
      setExcelResult(data)
    } catch (e: any) {
      console.error('Rank excel error:', e)
      setError(e.message || 'Failed to rank Excel')
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

  const getTrendIcon = (trend: string) => {
    if (trend === 'Improving') return <TrendingUp className="w-5 h-5 text-success-600" />
    if (trend === 'Declining') return <TrendingDown className="w-5 h-5 text-danger-600" />
    return <Target className="w-5 h-5 text-neutral-600" />
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
          <h1 className="text-3xl font-bold text-neutral-900 dark:text-white mb-2">
            Management Integrity Analyzer
          </h1>
          <p className="text-neutral-600 dark:text-neutral-400">
            Multi-quarter analysis with guidance tracking and performance comparison
          </p>
        </div>

        {!result && !excelResult ? (
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
                  placeholder="e.g., Kaynes Technology"
                  className="w-full px-4 py-3 rounded-lg border border-neutral-300 dark:border-neutral-600 bg-white dark:bg-neutral-900 text-neutral-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                />
              </div>

              {/* Excel Ranking Upload */}
              <div className="mb-6">
                <label className="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-2">
                  Rank Stocks from Excel (.xlsx/.xls)
                </label>
                <div className="border-2 border-dashed border-neutral-300 dark:border-neutral-600 rounded-lg p-6 text-center hover:border-primary-500 transition-colors">
                  <input
                    type="file"
                    accept=".xlsx,.xls"
                    onChange={handleExcelFileChange}
                    className="hidden"
                    id="excel-upload"
                  />
                  <label htmlFor="excel-upload" className="cursor-pointer">
                    <Upload className="w-10 h-10 text-neutral-400 mx-auto mb-3" />
                    <p className="text-neutral-600 dark:text-neutral-400 mb-1">
                      Click to select Excel file
                    </p>
                    <p className="text-sm text-neutral-500">
                      First row should contain finance columns (Name, P/E, ROE %, ROCE %, etc.)
                    </p>
                  </label>
                  {excelFile && (
                    <div className="mt-3 text-sm text-neutral-700 dark:text-neutral-300">Selected: {excelFile.name}</div>
                  )}
                </div>
              </div>

              {/* File Upload (PDF) */}
              <div className="mb-6">
                <label className="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-2">
                  Upload Transcripts (PDF) - Multiple Quarters
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
                    <p className="text-sm text-neutral-500">
                      Upload multiple quarters for comparison (e.g., Q1_FY2024.pdf, Q2_FY2024.pdf)
                    </p>
                  </label>
                </div>

                {files.length > 0 && (
                  <div className="mt-4 space-y-2">
                    {files.map((file, idx) => (
                      <div
                        key={idx}
                        className="flex items-center gap-2 p-3 bg-neutral-50 dark:bg-neutral-900 rounded-lg"
                      >
                        <FileText className="w-5 h-5 text-primary-600 dark:text-primary-400" />
                        <span className="text-sm text-neutral-900 dark:text-white flex-1">
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

              {/* Model Controls */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                <div>
                  <label className="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-2">AI Model (optional)</label>
                  <input
                    type="text"
                    value={model}
                    onChange={(e) => setModel(e.target.value)}
                    placeholder="llama3.1:8b"
                    className="w-full px-4 py-3 rounded-lg border border-neutral-300 dark:border-neutral-600 bg-white dark:bg-neutral-900 text-neutral-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  />
                  <p className="text-xs text-neutral-500 dark:text-neutral-400 mt-1">Leave empty to use server default.</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-2">Temperature</label>
                  <input
                    type="number"
                    step="0.05"
                    min={0}
                    max={1}
                    value={temperature}
                    onChange={(e) => setTemperature(parseFloat(e.target.value))}
                    className="w-full px-4 py-3 rounded-lg border border-neutral-300 dark:border-neutral-600 bg-white dark:bg-neutral-900 text-neutral-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  />
                </div>
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
                    Analyzing {files.length} Quarter{files.length > 1 ? 's' : ''}...
                  </>
                ) : (
                  <>
                    <CheckCircle className="w-5 h-5" />
                    Analyze Multi-Quarter Performance
                  </>
                )}
              </button>

              {/* Rank Excel Button */}
              <button
                onClick={handleRankExcel}
                disabled={isAnalyzing || !excelFile}
                className="w-full mt-3 py-3 px-6 bg-gradient-to-r from-indigo-600 to-indigo-700 text-white rounded-lg font-medium hover:from-indigo-700 hover:to-indigo-800 disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center justify-center gap-2"
              >
                <CheckCircle className="w-5 h-5" /> Rank Excel (Fundamentals)
              </button>
            </div>
          </div>
        ) : result ? (
          /* Results Section */
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-6"
          >
            {/* Overall Summary Card */}
            <div className="bg-white dark:bg-neutral-800 rounded-xl border border-neutral-200 dark:border-neutral-700 p-8">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="text-center">
                  <h2 className="text-2xl font-bold text-neutral-900 dark:text-white mb-2">
                    {result.company}
                  </h2>
                  <div className={`text-6xl font-bold ${getScoreColor(result.overallScore)} mb-2`}>
                    {result.overallScore}
                  </div>
                  <div className="text-sm text-neutral-600 dark:text-neutral-400">
                    Overall Integrity Score
                  </div>
                </div>
                
                <div className="text-center border-l border-r border-neutral-200 dark:border-neutral-700">
                  <div className="flex items-center justify-center gap-2 mb-2">
                    {getTrendIcon(result.summary.trend)}
                    <span className="text-2xl font-bold text-neutral-900 dark:text-white">
                      {result.summary.trend}
                    </span>
                  </div>
                  <div className="text-sm text-neutral-600 dark:text-neutral-400 mb-4">
                    Performance Trend
                  </div>
                  <div className="text-lg font-semibold text-neutral-900 dark:text-white">
                    {result.quartersAnalyzed} Quarters
                  </div>
                  <div className="text-xs text-neutral-500">
                    Analyzed
                  </div>
                </div>
                
                <div className="text-center">
                  <div className="text-2xl font-bold text-primary-600 dark:text-primary-400 mb-2">
                    {result.summary.averageScore}
                  </div>
                  <div className="text-sm text-neutral-600 dark:text-neutral-400 mb-4">
                    Average Score
                  </div>
                  <div className="text-sm text-neutral-700 dark:text-neutral-300">
                    {result.summary.guidanceDelivery}
                  </div>
                </div>
              </div>

              {/* Model Controls */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                <div>
                  <label className="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-2">AI Model (optional)</label>
                  <input
                    type="text"
                    value={model}
                    onChange={(e) => setModel(e.target.value)}
                    placeholder="llama3.1:8b"
                    className="w-full px-4 py-3 rounded-lg border border-neutral-300 dark:border-neutral-600 bg-white dark:bg-neutral-900 text-neutral-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  />
                  <p className="text-xs text-neutral-500 dark:text-neutral-400 mt-1">Leave empty to use server default.</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-2">Temperature</label>
                  <input
                    type="number"
                    step="0.05"
                    min={0}
                    max={1}
                    value={temperature}
                    onChange={(e) => setTemperature(parseFloat(e.target.value))}
                    className="w-full px-4 py-3 rounded-lg border border-neutral-300 dark:border-neutral-600 bg-white dark:bg-neutral-900 text-neutral-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  />
                </div>
              </div>
            </div>

            {/* Executive Summary */}
            <div className="bg-gradient-to-r from-indigo-50 to-purple-50 dark:from-indigo-900/20 dark:to-purple-900/20 rounded-xl border-2 border-indigo-200 dark:border-indigo-800 p-6">
              <h3 className="text-xl font-bold text-indigo-900 dark:text-indigo-300 mb-4 flex items-center gap-2">
                <Award className="w-6 h-6" />
                Executive Summary
              </h3>
              <div className="space-y-4">
                <p className="text-sm text-indigo-700 dark:text-indigo-200 leading-relaxed">
                  {result.company} shows {result.summary.averageScore >= 80 ? 'consistently high' : result.summary.averageScore >= 60 ? 'good' : 'moderate'} management integrity with a {result.summary.trend.toLowerCase()} trend. 
                  {result.quartersAnalyzed > 1 && ` Analysis of ${result.quartersAnalyzed} quarters reveals ${result.summary.trend === 'Improving' ? 'strengthening' : result.summary.trend === 'Declining' ? 'emerging' : 'stable'} ${result.summary.trend === 'Improving' ? 'execution capabilities' : result.summary.trend === 'Declining' ? 'competitive or operational pressures' : 'performance'}.`}
                </p>
                
                {/* Quarterly Comparison Table */}
                <div className="overflow-x-auto">
                  <h4 className="font-semibold text-indigo-800 dark:text-indigo-300 mb-3">Quarterly Comparison</h4>
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b-2 border-indigo-300 dark:border-indigo-700">
                        <th className="text-left py-2 px-3 text-indigo-900 dark:text-indigo-200 font-semibold">Quarter</th>
                        <th className="text-center py-2 px-3 text-indigo-900 dark:text-indigo-200 font-semibold">Score</th>
                        <th className="text-left py-2 px-3 text-indigo-900 dark:text-indigo-200 font-semibold">Revenue Growth</th>
                        <th className="text-left py-2 px-3 text-indigo-900 dark:text-indigo-200 font-semibold">Key Highlights</th>
                      </tr>
                    </thead>
                    <tbody>
                      {result.quarters.map((quarter, idx) => (
                        <tr key={idx} className="border-b border-indigo-200 dark:border-indigo-800">
                          <td className="py-3 px-3 font-medium text-indigo-800 dark:text-indigo-300">{quarter.quarter}</td>
                          <td className="py-3 px-3 text-center">
                            <span className={`inline-block px-3 py-1 rounded-full font-bold ${getScoreBackground(quarter.score)} ${getScoreColor(quarter.score)}`}>
                              {quarter.score}
                            </span>
                          </td>
                          <td className="py-3 px-3 text-indigo-700 dark:text-indigo-300">
                            {quarter.ai_analysis?.financial_performance?.revenue_growth || 'Not specified'}
                          </td>
                          <td className="py-3 px-3 text-indigo-700 dark:text-indigo-300 text-xs">
                            {quarter.ai_analysis?.financial_performance?.profitability?.substring(0, 120) || quarter.highlights[0]?.substring(0, 120) || 'N/A'}...
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>

                {/* Performance Highlights */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-2">
                  <div className="bg-white/50 dark:bg-neutral-900/30 rounded-lg p-3">
                    <div className="text-xs text-indigo-600 dark:text-indigo-400 font-medium mb-1">Revenue Trend</div>
                    <div className="text-sm text-indigo-900 dark:text-indigo-100 font-semibold">
                      {result.quarters.map(q => q.ai_analysis?.financial_performance?.revenue_growth).filter(Boolean).join(' → ') || 'Not available'}
                    </div>
                  </div>
                  <div className="bg-white/50 dark:bg-neutral-900/30 rounded-lg p-3">
                    <div className="text-xs text-indigo-600 dark:text-indigo-400 font-medium mb-1">Margin Trend</div>
                    <div className="text-sm text-indigo-900 dark:text-indigo-100 font-semibold">
                      {result.quarters.map(q => q.ai_analysis?.financial_performance?.margin_trend).filter(Boolean).join(' → ') || 'Not available'}
                    </div>
                  </div>
                  <div className="bg-white/50 dark:bg-neutral-900/30 rounded-lg p-3">
                    <div className="text-xs text-indigo-600 dark:text-indigo-400 font-medium mb-1">Management Credibility</div>
                    <div className="text-sm text-indigo-900 dark:text-indigo-100 font-semibold">
                      {result.quarters.map(q => q.ai_analysis?.management_quality?.credibility_score).filter(Boolean).join(' → ') || 'Not available'}/100
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Performance Charts */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Score Progression Chart */}
              <div className="bg-white dark:bg-neutral-800 rounded-xl border border-neutral-200 dark:border-neutral-700 p-6">
                <h3 className="text-lg font-bold text-neutral-900 dark:text-white mb-4 flex items-center gap-2">
                  <LineChartIcon className="w-5 h-5" />
                  Score Progression
                </h3>
                <ResponsiveContainer width="100%" height={250}>
                  <LineChart data={result.comparison.score_progression}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                    <XAxis dataKey="quarter" stroke="#9ca3af" style={{ fontSize: '12px' }} />
                    <YAxis stroke="#9ca3af" style={{ fontSize: '12px' }} domain={[0, 100]} />
                    <Tooltip 
                      contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151', borderRadius: '8px' }}
                      labelStyle={{ color: '#f3f4f6' }}
                    />
                    <Legend />
                    <Line type="monotone" dataKey="score" stroke="#3b82f6" strokeWidth={3} name="Integrity Score" />
                  </LineChart>
                </ResponsiveContainer>
              </div>

              {/* Management Quality Radar */}
              <div className="bg-white dark:bg-neutral-800 rounded-xl border border-neutral-200 dark:border-neutral-700 p-6">
                <h3 className="text-lg font-bold text-neutral-900 dark:text-white mb-4 flex items-center gap-2">
                  <Target className="w-5 h-5" />
                  Latest Quarter Analysis
                </h3>
                <ResponsiveContainer width="100%" height={250}>
                  <RadarChart data={(() => {
                    const lastQuarter = result.quarters[result.quarters.length - 1]
                    if (lastQuarter?.ai_analysis?.management_quality) {
                      return [
                        { category: 'Credibility', value: lastQuarter.ai_analysis.management_quality.credibility_score },
                        { category: 'Score', value: lastQuarter.score },
                      ]
                    }
                    return [
                      { category: 'Credibility', value: 0 },
                      { category: 'Score', value: 0 },
                    ]
                  })()}>
                    <PolarGrid stroke="#374151" />
                    <PolarAngleAxis dataKey="category" stroke="#9ca3af" style={{ fontSize: '12px' }} />
                    <PolarRadiusAxis angle={90} domain={[0, 100]} stroke="#9ca3af" style={{ fontSize: '10px' }} />
                    <Radar name="Performance" dataKey="value" stroke="#10b981" fill="#10b981" fillOpacity={0.6} />
                  </RadarChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Guidance vs Delivery Tracking */}
            {result.comparison.guidance_tracking && result.comparison.guidance_tracking.length > 0 && (
              <div className="bg-white dark:bg-neutral-800 rounded-xl border border-neutral-200 dark:border-neutral-700 p-6">
                <h3 className="text-xl font-bold text-neutral-900 dark:text-white mb-4 flex items-center gap-2">
                  <Award className="w-6 h-6" />
                  Guidance vs Delivery Tracking
                </h3>
                <div className="space-y-4">
                  {result.comparison.guidance_tracking.map((track, idx) => (
                    <div key={idx} className="border-l-4 border-primary-500 pl-4 py-2 bg-neutral-50 dark:bg-neutral-900 rounded-r-lg">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm font-semibold text-neutral-900 dark:text-white">
                          {track.quarter} → {track.next_quarter}
                        </span>
                        <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                          track.status === 'Delivered' 
                            ? 'bg-success-100 dark:bg-success-900/30 text-success-700 dark:text-success-400'
                            : 'bg-danger-100 dark:bg-danger-900/30 text-danger-700 dark:text-danger-400'
                        }`}>
                          {track.status}
                        </span>
                      </div>
                      <p className="text-sm text-neutral-700 dark:text-neutral-300 mb-1">
                        <strong>Guidance:</strong> {track.guidance}
                      </p>
                      <p className="text-xs text-neutral-500">
                        {track.evidence}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Quarter-by-Quarter Analysis */}
            <div className="space-y-4">
              <h3 className="text-xl font-bold text-neutral-900 dark:text-white flex items-center gap-2">
                <Calendar className="w-6 h-6" />
                Quarter-by-Quarter Detailed Analysis
              </h3>
              
              {result.quarters.map((quarter, idx) => (
                <div
                  key={idx}
                  className="bg-white dark:bg-neutral-800 rounded-xl border border-neutral-200 dark:border-neutral-700 p-6"
                >
                  <div className="flex items-start justify-between mb-4">
                    <div>
                      <h4 className="text-lg font-semibold text-neutral-900 dark:text-white mb-1">
                        {quarter.quarter}
                      </h4>
                      <p className="text-sm text-neutral-500">
                        {quarter.metrics.revenue_mentions} revenue mentions • {quarter.metrics.growth_mentions} growth indicators
                      </p>
                    </div>
                    <div className={`px-4 py-2 rounded-full text-lg font-bold ${getScoreBackground(quarter.score)} ${getScoreColor(quarter.score)}`}>
                      {quarter.score}
                    </div>
                  </div>

                  {/* AI Analysis Section */}
                  {quarter.ai_analysis ? (
                    <div className="space-y-4 mb-4">
                      {/* Financial Performance */}
                      <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4 border border-blue-200 dark:border-blue-800">
                        <h5 className="text-sm font-bold text-blue-900 dark:text-blue-300 mb-2 flex items-center gap-2">
                          <TrendingUp className="w-4 h-4" />
                          Financial Performance
                        </h5>
                        <div className="space-y-1 text-sm text-blue-800 dark:text-blue-200">
                          <p><strong>Revenue Growth:</strong> {quarter.ai_analysis.financial_performance.revenue_growth}</p>
                          <p><strong>Margin Trend:</strong> {quarter.ai_analysis.financial_performance.margin_trend}</p>
                          <p><strong>Profitability:</strong> {quarter.ai_analysis.financial_performance.profitability}</p>
                          {quarter.ai_analysis.financial_performance.key_metrics.length > 0 && (
                            <div className="mt-2">
                              <strong>Key Metrics:</strong>
                              <ul className="list-disc list-inside ml-2 mt-1">
                                {quarter.ai_analysis.financial_performance.key_metrics.map((metric, midx) => (
                                  <li key={midx}>{metric}</li>
                                ))}
                              </ul>
                            </div>
                          )}
                        </div>
                      </div>

                      {/* Strategic Initiatives */}
                      {quarter.ai_analysis.strategic_initiatives.length > 0 && (
                        <div className="bg-purple-50 dark:bg-purple-900/20 rounded-lg p-4 border border-purple-200 dark:border-purple-800">
                          <h5 className="text-sm font-bold text-purple-900 dark:text-purple-300 mb-2">Strategic Initiatives</h5>
                          <ul className="space-y-1 text-sm text-purple-800 dark:text-purple-200">
                            {quarter.ai_analysis.strategic_initiatives.map((initiative, iidx) => (
                              <li key={iidx} className="flex items-start gap-2">
                                <CheckCircle className="w-4 h-4 text-purple-600 flex-shrink-0 mt-0.5" />
                                <span>{initiative}</span>
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}

                      {/* Market Position */}
                      <div className="bg-green-50 dark:bg-green-900/20 rounded-lg p-4 border border-green-200 dark:border-green-800">
                        <h5 className="text-sm font-bold text-green-900 dark:text-green-300 mb-2">Market Position</h5>
                        <div className="space-y-1 text-sm text-green-800 dark:text-green-200">
                          <p><strong>Competitive Advantage:</strong> {quarter.ai_analysis.market_position.competitive_advantage}</p>
                          <p><strong>Market Share:</strong> {quarter.ai_analysis.market_position.market_share}</p>
                          <p><strong>Customer Dynamics:</strong> {quarter.ai_analysis.market_position.customer_dynamics}</p>
                        </div>
                      </div>

                      {/* Management Quality */}
                      <div className="bg-amber-50 dark:bg-amber-900/20 rounded-lg p-4 border border-amber-200 dark:border-amber-800">
                        <h5 className="text-sm font-bold text-amber-900 dark:text-amber-300 mb-2">Management Quality</h5>
                        <div className="space-y-1 text-sm text-amber-800 dark:text-amber-200">
                          <p><strong>Credibility Score:</strong> {quarter.ai_analysis.management_quality.credibility_score}/100</p>
                          <p><strong>Transparency:</strong> {quarter.ai_analysis.management_quality.transparency}</p>
                          <p><strong>Execution:</strong> {quarter.ai_analysis.management_quality.execution}</p>
                        </div>
                      </div>

                      {/* Key Insights */}
                      {quarter.ai_analysis.key_insights.length > 0 && (
                        <div className="bg-indigo-50 dark:bg-indigo-900/20 rounded-lg p-4 border border-indigo-200 dark:border-indigo-800">
                          <h5 className="text-sm font-bold text-indigo-900 dark:text-indigo-300 mb-2">Key Investment Insights</h5>
                          <ul className="space-y-2 text-sm text-indigo-800 dark:text-indigo-200">
                            {quarter.ai_analysis.key_insights.map((insight, iidx) => (
                              <li key={iidx} className="flex items-start gap-2">
                                <Award className="w-4 h-4 text-indigo-600 flex-shrink-0 mt-0.5" />
                                <span>{insight}</span>
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}

                      {/* Investment Thesis */}
                      {quarter.ai_analysis.investment_thesis && (
                        <div className="bg-gradient-to-r from-primary-50 to-primary-100 dark:from-primary-900/20 dark:to-primary-800/20 rounded-lg p-4 border-2 border-primary-300 dark:border-primary-700">
                          <h5 className="text-sm font-bold text-primary-900 dark:text-primary-300 mb-2">Investment Thesis</h5>
                          <p className="text-sm text-primary-800 dark:text-primary-200 leading-relaxed">
                            {quarter.ai_analysis.investment_thesis}
                          </p>
                        </div>
                      )}

                      {/* Risks */}
                      {quarter.ai_analysis.risks_concerns.length > 0 && (
                        <div className="bg-red-50 dark:bg-red-900/20 rounded-lg p-4 border border-red-200 dark:border-red-800">
                          <h5 className="text-sm font-bold text-red-900 dark:text-red-300 mb-2">Risks & Concerns</h5>
                          <ul className="space-y-1 text-sm text-red-800 dark:text-red-200">
                            {quarter.ai_analysis.risks_concerns.map((risk, ridx) => (
                              <li key={ridx} className="flex items-start gap-2">
                                <AlertCircle className="w-4 h-4 text-red-600 flex-shrink-0 mt-0.5" />
                                <span>{risk}</span>
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  ) : (
                    /* Fallback to basic highlights if no AI analysis */
                    <div className="mb-4">
                      <p className="text-sm font-semibold text-neutral-700 dark:text-neutral-300 mb-2">
                        Key Highlights:
                      </p>
                      <div className="space-y-2">
                        {quarter.highlights.map((highlight, hidx) => (
                          <div key={hidx} className="flex items-start gap-2">
                            <CheckCircle className="w-4 h-4 text-success-500 flex-shrink-0 mt-0.5" />
                            <span className="text-sm text-neutral-700 dark:text-neutral-300">{highlight}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Guidance Provided */}
                  {quarter.guidance.length > 0 && (
                    <div className="mb-4">
                      <p className="text-sm font-semibold text-neutral-700 dark:text-neutral-300 mb-2">
                        Guidance Provided:
                      </p>
                      <div className="space-y-2">
                        {quarter.guidance.map((g, gidx) => (
                          <div key={gidx} className="flex items-start gap-2 pl-4 border-l-2 border-primary-500">
                            <span className="text-sm text-neutral-700 dark:text-neutral-300">
                              <strong>{g.type}:</strong> {g.details}
                            </span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Concerns */}
                  {quarter.concerns.length > 0 && quarter.concerns[0] !== "No major concerns highlighted" && (
                    <div>
                      <p className="text-sm font-semibold text-neutral-700 dark:text-neutral-300 mb-2">
                        Concerns:
                      </p>
                      <div className="space-y-2">
                        {quarter.concerns.map((concern, cidx) => (
                          <div key={cidx} className="flex items-start gap-2">
                            <AlertCircle className="w-4 h-4 text-warning-500 flex-shrink-0 mt-0.5" />
                            <span className="text-sm text-neutral-700 dark:text-neutral-300">{concern}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>

            {/* Guidance Tracking */}
            {result.comparison.guidance_tracking.length > 0 && (
              <div className="bg-white dark:bg-neutral-800 rounded-xl border border-neutral-200 dark:border-neutral-700 p-6">
                <h3 className="text-xl font-bold text-neutral-900 dark:text-white mb-4 flex items-center gap-2">
                  <Award className="w-6 h-6" />
                  Guidance vs Delivery Tracking
                </h3>
                <div className="space-y-4">
                  {result.comparison.guidance_tracking.map((track, idx) => (
                    <div key={idx} className="border-l-4 border-primary-500 pl-4 py-2">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm font-semibold text-neutral-900 dark:text-white">
                          {track.quarter} → {track.next_quarter}
                        </span>
                        <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                          track.status === 'Delivered' 
                            ? 'bg-success-100 dark:bg-success-900/30 text-success-700 dark:text-success-400'
                            : 'bg-danger-100 dark:bg-danger-900/30 text-danger-700 dark:text-danger-400'
                        }`}>
                          {track.status}
                        </span>
                      </div>
                      <p className="text-sm text-neutral-700 dark:text-neutral-300 mb-1">
                        <strong>Guidance:</strong> {track.guidance}
                      </p>
                      <p className="text-xs text-neutral-500">
                        {track.evidence}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Analyst Summary */}
            <div className="bg-gradient-to-br from-slate-50 to-neutral-100 dark:from-slate-900 dark:to-neutral-900 rounded-xl border-2 border-slate-300 dark:border-slate-700 p-6">
              <h3 className="text-xl font-bold text-slate-900 dark:text-slate-100 mb-4 flex items-center gap-2">
                <Award className="w-6 h-6 text-primary-600" />
                Analyst Summary
              </h3>
              <div className="space-y-4">
                <div className="bg-white dark:bg-neutral-800 rounded-lg p-4 border border-slate-200 dark:border-slate-700">
                  <h4 className="font-semibold text-slate-800 dark:text-slate-200 mb-2">Overall Assessment</h4>
                  <p className="text-sm text-slate-700 dark:text-slate-300 leading-relaxed">
                    {result.company} demonstrates {result.summary.averageScore >= 85 ? 'exemplary' : result.summary.averageScore >= 70 ? 'strong' : 'moderate'} management integrity and {result.quarters[result.quarters.length - 1]?.ai_analysis?.management_quality?.transparency?.toLowerCase() || 'transparent'} operations.
                    {result.summary.trend === 'Declining' && ' However, competitive pressure is starting to impact growth momentum.'}
                    {result.summary.trend === 'Improving' && ' The improving trend indicates strengthening execution capabilities.'}
                    {result.summary.trend === 'Stable' && ' The stable performance reflects consistent management quality.'}
                  </p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="bg-white dark:bg-neutral-800 rounded-lg p-4 border border-slate-200 dark:border-slate-700">
                    <h4 className="font-semibold text-slate-800 dark:text-slate-200 mb-2 flex items-center gap-2">
                      <CheckCircle className="w-4 h-4 text-green-600" />
                      Key Strengths
                    </h4>
                    <ul className="space-y-1 text-sm text-slate-700 dark:text-slate-300">
                      {result.quarters.slice(-1).map(q => 
                        q.ai_analysis?.key_insights?.slice(0, 3).map((insight, idx) => (
                          <li key={idx} className="flex items-start gap-2">
                            <span className="text-green-600 mt-1">•</span>
                            <span>{insight}</span>
                          </li>
                        ))
                      )}
                    </ul>
                  </div>

                  <div className="bg-white dark:bg-neutral-800 rounded-lg p-4 border border-slate-200 dark:border-slate-700">
                    <h4 className="font-semibold text-slate-800 dark:text-slate-200 mb-2 flex items-center gap-2">
                      <AlertCircle className="w-4 h-4 text-orange-600" />
                      Key Risks
                    </h4>
                    <ul className="space-y-1 text-sm text-slate-700 dark:text-slate-300">
                      {result.quarters.slice(-1).map(q => 
                        q.ai_analysis?.risks_concerns?.slice(0, 3).map((risk, idx) => (
                          <li key={idx} className="flex items-start gap-2">
                            <span className="text-orange-600 mt-1">•</span>
                            <span>{risk}</span>
                          </li>
                        ))
                      )}
                    </ul>
                  </div>
                </div>

                <div className="bg-primary-50 dark:bg-primary-900/20 rounded-lg p-4 border border-primary-200 dark:border-primary-800">
                  <h4 className="font-semibold text-primary-900 dark:text-primary-200 mb-2">Investment Outlook</h4>
                  <p className="text-sm text-primary-800 dark:text-primary-300 leading-relaxed">
                    {result.quarters[result.quarters.length - 1]?.ai_analysis?.investment_thesis || 
                     `Overall outlook ${result.summary.trend === 'Improving' ? 'remains positive' : result.summary.trend === 'Declining' ? 'requires monitoring' : 'is stable'} given ${result.summary.trend === 'Improving' ? 'strengthening fundamentals' : result.summary.trend === 'Declining' ? 'emerging headwinds' : 'consistent performance'}.`}
                  </p>
                </div>
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
                onClick={handleExport}
                className="flex-1 py-3 px-6 bg-gradient-to-r from-primary-600 to-primary-700 text-white rounded-lg font-medium hover:from-primary-700 hover:to-primary-800 transition-all flex items-center justify-center gap-2"
              >
                <Download className="w-5 h-5" />
                Export Report (CSV)
              </button>
            </div>
          </motion.div>
        ) : (
          /* Excel Ranking Results */
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-6"
          >
            <div className="bg-white dark:bg-neutral-800 rounded-xl border border-neutral-200 dark:border-neutral-700 p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-bold text-neutral-900 dark:text-white">Excel Ranking</h2>
                <button
                  onClick={() => { setExcelResult(null); setExcelFile(null); }}
                  className="px-3 py-2 text-sm rounded-lg border border-neutral-300 dark:border-neutral-600"
                >Back</button>
              </div>
              <div className="overflow-auto">
                <table className="min-w-full text-sm">
                  <thead>
                    <tr className="border-b border-neutral-200 dark:border-neutral-700">
                      {excelResult.columns.map((c: string) => (
                        <th key={c} className="text-left py-2 px-3 text-neutral-700 dark:text-neutral-300 font-semibold">{c}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {excelResult.items.map((row: any, idx: number) => (
                      <tr key={idx} className="border-b border-neutral-100 dark:border-neutral-700/50">
                        {excelResult.columns.map((c: string) => (
                          <td key={c} className="py-2 px-3 text-neutral-800 dark:text-neutral-200">{row[c] ?? ''}</td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </motion.div>
        )}
      </div>
    </div>
  )
}
