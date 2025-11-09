'use client'

import { useAnalysis } from '@/contexts/AnalysisContext'
import { useRouter } from 'next/navigation'
import { useEffect, useState } from 'react'
import { 
  ArrowLeft, 
  BarChart3, 
  TrendingUp, 
  AlertTriangle, 
  CheckCircle2, 
  Info, 
  Lightbulb,
  ChevronDown,
  ChevronUp,
  ExternalLink
} from 'lucide-react'
import Link from 'next/link'

export default function AnalysisPage() {
  const { analysisResult: contextResult, isAnalyzing, error } = useAnalysis()
  const router = useRouter()
  const [analysisResult, setAnalysisResult] = useState<any>(contextResult)
  const [expandedSections, setExpandedSections] = useState<Record<string, boolean>>({
    overview: true,
    financials: true,
    investorView: true,
    recommendation: true,
    risks: true,
    catalysts: true
  })

  // Fetch fresh analysis data on mount
  useEffect(() => {
    const fetchAnalysis = async () => {
      try {
        const response = await fetch('http://localhost:8000/company/default-company/analysis')
        if (response.ok) {
          const data = await response.json()
          console.log('✅ Fetched fresh analysis data:', data)
          setAnalysisResult(data)
        }
      } catch (error) {
        console.error('Error fetching analysis:', error)
      }
    }
    
    // Always fetch fresh data on mount
    fetchAnalysis()
    
    console.log('Analysis page - analysisResult:', analysisResult)
    console.log('Analysis page - isAnalyzing:', isAnalyzing)
    console.log('Financial metrics:', analysisResult?.financial_metrics)
  }, [])

  const toggleSection = (section: string) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }))
  }

  if (isAnalyzing) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-t-4 border-b-4 border-primary-600 mx-auto mb-4"></div>
          <h2 className="text-2xl font-semibold text-gray-800">Analyzing Company Data</h2>
          <p className="text-gray-600 mt-2">This may take a moment...</p>
        </div>
      </div>
    )
  }

  if (!analysisResult) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center p-6 max-w-md">
          <div className="bg-red-100 p-4 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
            <Info className="w-8 h-8 text-red-600" />
          </div>
          <h2 className="text-2xl font-semibold text-gray-800 mb-2">No Analysis Found</h2>
          <p className="text-gray-600 mb-6">Please analyze a company first to view detailed insights.</p>
          <button
            onClick={() => router.push('/')}
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
          >
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to Dashboard
          </button>
        </div>
      </div>
    )
  }

  const { 
    company_name, 
    transcript_summary, 
    financial_metrics, 
    investor_views,
    recommendation
  } = analysisResult
  
  // Use first investor view as the main view for display
  const investor_view = investor_views?.warren_buffett || investor_views?.benjamin_graham || null
  
  // Create valuation metrics from financial metrics
  const valuation_metrics = {
    market_cap: (financial_metrics?.revenue || 0) * 2, // Rough estimate
    pe_ratio: financial_metrics?.pe_ratio || 0
  }

  // Format number in Indian style (Crores/Lakhs)
  const formatIndianCurrency = (value: number): string => {
    if (value === 0) return '₹0'
    const absValue = Math.abs(value)
    const sign = value < 0 ? '-' : ''
    
    if (absValue >= 100) {
      return `${sign}₹${absValue.toFixed(2)}Cr`
    } else if (absValue >= 1) {
      return `${sign}₹${(absValue * 100).toFixed(2)}L`
    } else {
      return `${sign}₹${(absValue * 10000).toFixed(2)}K`
    }
  }

  const renderMetricCard = (label: string, value: string, change?: number, prefix?: string) => (
    <div className="bg-white p-4 rounded-lg shadow-sm border">
      <p className="text-sm text-gray-500 mb-1">{label}</p>
      <p className="text-2xl font-bold text-gray-900">{value}</p>
      {change !== undefined && (
        <p className={`text-sm mt-1 ${change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
          {change >= 0 ? '↑' : '↓'} {Math.abs(change).toFixed(1)}%
        </p>
      )}
    </div>
  )

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <header className="bg-white dark:bg-gray-800 shadow">
        <div className="max-w-7xl mx-auto px-4 py-6 sm:px-6 lg:px-8">
          <div className="flex items-center">
            <button
              onClick={() => router.back()}
              className="mr-4 p-1 rounded-full hover:bg-gray-100"
            >
              <ArrowLeft className="h-5 w-5 text-gray-500" />
            </button>
            <div>
              <h1 className="text-2xl font-bold text-gray-900 dark:text-white">{company_name}</h1>
              <p className="text-sm text-gray-500 dark:text-gray-400">Last updated: {new Date(analysisResult.last_updated).toLocaleDateString()}</p>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-6 sm:px-6 lg:px-8">
        {/* Recommendation Banner */}
        <div className="bg-white rounded-lg shadow-sm overflow-hidden mb-6">
          <div className="p-6">
            <div className="flex items-center">
              <div className={`p-3 rounded-lg ${
                recommendation.rating.toLowerCase() === 'buy' ? 'bg-green-100 text-green-800' :
                recommendation.rating.toLowerCase() === 'hold' ? 'bg-yellow-100 text-yellow-800' :
                'bg-red-100 text-red-800'
              }`}>
                {recommendation.rating === 'Buy' ? (
                  <TrendingUp className="h-6 w-6" />
                ) : recommendation.rating === 'Hold' ? (
                  <Info className="h-6 w-6" />
                ) : (
                  <AlertTriangle className="h-6 w-6" />
                )}
              </div>
              <div className="ml-4">
                <h3 className="text-lg font-medium">
                  {recommendation.rating} Recommendation
                </h3>
                <p className="text-sm text-gray-600">
                  Target Price: ${recommendation.target_price.toFixed(2)} 
                  <span className={`ml-2 ${recommendation.margin_of_safety >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                    ({recommendation.margin_of_safety > 0 ? '+' : ''}{recommendation.margin_of_safety.toFixed(1)}% {recommendation.margin_of_safety >= 0 ? 'Upside' : 'Downside'})
                  </span>
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Key Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          {renderMetricCard('Revenue', formatIndianCurrency(financial_metrics?.revenue || 0))}
          {renderMetricCard('P/E Ratio', (valuation_metrics.pe_ratio || 0).toFixed(2))}
          {renderMetricCard('ROE', `${(financial_metrics?.roe || 0).toFixed(1)}%`)}
          {renderMetricCard('Debt/Equity', (financial_metrics?.debt_equity || 0).toFixed(2))}
        </div>

        {/* Ratings Summary */}
        {analysisResult?.ratings_summary && Object.keys(analysisResult.ratings_summary).length > 0 && (
          <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
            <h2 className="text-lg font-medium text-gray-900 mb-4">📊 Comprehensive Ratings</h2>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {Object.entries(analysisResult.ratings_summary).map(([category, rating]) => (
                <div key={category} className="text-center p-4 bg-gray-50 rounded-lg">
                  <p className="text-xs text-gray-500 uppercase mb-2">{category.replace('_', ' ')}</p>
                  <p className="text-lg font-bold">{rating}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Analysis Sections */}
        <div className="space-y-6">
          {/* Company Overview */}
          <div className="bg-white rounded-lg shadow-sm overflow-hidden">
            <button 
              className="w-full px-6 py-4 flex justify-between items-center text-left"
              onClick={() => toggleSection('overview')}
            >
              <h2 className="text-lg font-medium text-gray-900">Company Overview</h2>
              {expandedSections.overview ? <ChevronUp className="h-5 w-5 text-gray-500" /> : <ChevronDown className="h-5 w-5 text-gray-500" />}
            </button>
            {expandedSections.overview && (
              <div className="px-6 pb-6 pt-2">
                <p className="text-gray-700 mb-4">{transcript_summary.summary?.overview || 'No overview available.'}</p>
                <div className="mt-4">
                  <h3 className="text-sm font-medium text-gray-900 mb-2">Key Points</h3>
                  <ul className="space-y-2">
                    {transcript_summary.key_quotes?.map((quote, index) => (
                      <li key={index} className="flex items-start">
                        <CheckCircle2 className="h-5 w-5 text-green-500 mr-2 mt-0.5 flex-shrink-0" />
                        <span className="text-gray-700">{quote}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            )}
          </div>

          {/* Financial Health */}
          <div className="bg-white rounded-lg shadow-sm overflow-hidden">
            <button 
              className="w-full px-6 py-4 flex justify-between items-center text-left"
              onClick={() => toggleSection('financials')}
            >
              <h2 className="text-lg font-medium text-gray-900">Financial Health</h2>
              {expandedSections.financials ? <ChevronUp className="h-5 w-5 text-gray-500" /> : <ChevronDown className="h-5 w-5 text-gray-500" />}
            </button>
            {expandedSections.financials && (
              <div className="px-6 pb-6 pt-2">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                  {renderMetricCard('Revenue', formatIndianCurrency(financial_metrics?.revenue || 0))}
                  {renderMetricCard('Net Profit', formatIndianCurrency(financial_metrics?.net_profit || 0))}
                  {renderMetricCard('ROE', `${(financial_metrics?.roe || 0).toFixed(1)}%`)}
                  {renderMetricCard('Debt/Equity', (financial_metrics?.debt_equity || 0).toFixed(2))}
                </div>
                <div>
                  <h3 className="text-sm font-medium text-gray-900 mb-2">Key Financial Metrics</h3>
                  <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-200">
                      <tbody className="bg-white divide-y divide-gray-200">
                        <tr>
                          <td className="px-4 py-2 whitespace-nowrap text-sm text-gray-500">EPS</td>
                          <td className="px-4 py-2 whitespace-nowrap text-sm font-medium text-gray-900 text-right">
                            ₹{(financial_metrics?.eps || 0).toFixed(2)}
                          </td>
                        </tr>
                        <tr>
                          <td className="px-4 py-2 whitespace-nowrap text-sm text-gray-500">ROCE</td>
                          <td className="px-4 py-2 whitespace-nowrap text-sm font-medium text-gray-900 text-right">
                            {(financial_metrics?.roce || 0).toFixed(1)}%
                          </td>
                        </tr>
                        <tr>
                          <td className="px-4 py-2 whitespace-nowrap text-sm text-gray-500">P/B Ratio</td>
                          <td className="px-4 py-2 whitespace-nowrap text-sm font-medium text-gray-900 text-right">
                            {(financial_metrics?.pb_ratio || 0).toFixed(2)}
                          </td>
                        </tr>
                        <tr>
                          <td className="px-4 py-2 whitespace-nowrap text-sm text-gray-500">EV/EBITDA</td>
                          <td className="px-4 py-2 whitespace-nowrap text-sm font-medium text-gray-900 text-right">
                            {(financial_metrics?.ev_ebitda || 0).toFixed(2)}
                          </td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Investor View */}
          <div className="bg-white rounded-lg shadow-sm overflow-hidden">
            <button 
              className="w-full px-6 py-4 flex justify-between items-center text-left"
              onClick={() => toggleSection('investorView')}
            >
              <h2 className="text-lg font-medium text-gray-900">Investor Perspective</h2>
              {expandedSections.investorView ? <ChevronUp className="h-5 w-5 text-gray-500" /> : <ChevronDown className="h-5 w-5 text-gray-500" />}
            </button>
            {expandedSections.investorView && investor_view && (
              <div className="px-6 pb-6 pt-2">
                <div className="mb-6">
                  <h3 className="text-sm font-medium text-gray-900 mb-2">Overall Assessment</h3>
                  <p className="text-gray-700">{investor_view.assessment}</p>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <h4 className="text-sm font-medium text-gray-900 mb-2">Strengths</h4>
                    <ul className="space-y-2">
                      {investor_view.strengths.map((strength, index) => (
                        <li key={index} className="flex items-start">
                          <CheckCircle2 className="h-5 w-5 text-green-500 mr-2 mt-0.5 flex-shrink-0" />
                          <span className="text-gray-700">{strength}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                  
                  <div>
                    <h4 className="text-sm font-medium text-gray-900 mb-2">Concerns</h4>
                    <ul className="space-y-2">
                      {investor_view.concerns.map((concern, index) => (
                        <li key={index} className="flex items-start">
                          <AlertTriangle className="h-5 w-5 text-yellow-500 mr-2 mt-0.5 flex-shrink-0" />
                          <span className="text-gray-700">{concern}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Recommendation Details */}
          <div className="bg-white rounded-lg shadow-sm overflow-hidden">
            <button 
              className="w-full px-6 py-4 flex justify-between items-center text-left"
              onClick={() => toggleSection('recommendation')}
            >
              <h2 className="text-lg font-medium text-gray-900">Investment Recommendation</h2>
              {expandedSections.recommendation ? <ChevronUp className="h-5 w-5 text-gray-500" /> : <ChevronDown className="h-5 w-5 text-gray-500" />}
            </button>
            {expandedSections.recommendation && recommendation && (
              <div className="px-6 pb-6 pt-2">
                <div className="mb-6">
                  <p className="text-gray-700 mb-4">{recommendation.reasoning}</p>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <h3 className="text-sm font-medium text-gray-900 mb-2">Valuation Metrics</h3>
                      <div className="space-y-2">
                        <div className="flex justify-between">
                          <span className="text-sm text-gray-500">Current Price</span>
                          <span className="text-sm font-medium">₹{recommendation.current_price.toFixed(2)}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-sm text-gray-500">Target Price</span>
                          <span className="text-sm font-medium">₹{recommendation.target_price.toFixed(2)}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-sm text-gray-500">Upside Potential</span>
                          <span className={`text-sm font-medium ${recommendation.margin_of_safety >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                            {recommendation.margin_of_safety > 0 ? '+' : ''}{recommendation.margin_of_safety.toFixed(1)}%
                          </span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-sm text-gray-500">Confidence</span>
                          <span className="text-sm font-medium">
                            {recommendation.confidence_score >= 0.8 ? 'High' : 
                             recommendation.confidence_score >= 0.5 ? 'Medium' : 'Low'} 
                            ({(recommendation.confidence_score * 10).toFixed(1)}/10)
                          </span>
                        </div>
                      </div>
                    </div>
                    
                    <div>
                      <h3 className="text-sm font-medium text-gray-900 mb-2">Key Factors</h3>
                      <ul className="space-y-2">
                        {Object.entries(investor_view?.key_factors || {}).slice(0, 3).map(([key, value]) => (
                          <li key={key} className="flex items-start">
                            <Lightbulb className="h-5 w-5 text-yellow-500 mr-2 mt-0.5 flex-shrink-0" />
                            <span className="text-sm text-gray-700">
                              <span className="font-medium">{key}:</span> {value}
                            </span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Risks & Catalysts */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Risks */}
            <div className="bg-white rounded-lg shadow-sm overflow-hidden">
              <button 
                className="w-full px-6 py-4 flex justify-between items-center text-left"
                onClick={() => toggleSection('risks')}
              >
                <h2 className="text-lg font-medium text-gray-900">Key Risks</h2>
                {expandedSections.risks ? <ChevronUp className="h-5 w-5 text-gray-500" /> : <ChevronDown className="h-5 w-5 text-gray-500" />}
              </button>
              {expandedSections.risks && recommendation?.risk_factors?.length > 0 && (
                <div className="px-6 pb-6 pt-2">
                  <ul className="space-y-3">
                    {recommendation.risk_factors.map((risk, index) => (
                      <li key={index} className="flex items-start">
                        <AlertTriangle className="h-5 w-5 text-red-500 mr-2 mt-0.5 flex-shrink-0" />
                        <span className="text-gray-700">{risk}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>

            {/* Catalysts */}
            <div className="bg-white rounded-lg shadow-sm overflow-hidden">
              <button 
                className="w-full px-6 py-4 flex justify-between items-center text-left"
                onClick={() => toggleSection('catalysts')}
              >
                <h2 className="text-lg font-medium text-gray-900">Potential Catalysts</h2>
                {expandedSections.catalysts ? <ChevronUp className="h-5 w-5 text-gray-500" /> : <ChevronDown className="h-5 w-5 text-gray-500" />}
              </button>
              {expandedSections.catalysts && recommendation?.catalysts?.length > 0 && (
                <div className="px-6 pb-6 pt-2">
                  <ul className="space-y-3">
                    {recommendation.catalysts.map((catalyst, index) => (
                      <li key={index} className="flex items-start">
                        <Lightbulb className="h-5 w-5 text-yellow-500 mr-2 mt-0.5 flex-shrink-0" />
                        <span className="text-gray-700">{catalyst}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-12">
        <div className="max-w-7xl mx-auto px-4 py-6 sm:px-6 lg:px-8">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <div className="text-sm text-gray-500">
              Data as of {new Date().toLocaleDateString()}
            </div>
            <div className="mt-4 md:mt-0">
              <button
                onClick={() => window.print()}
                className="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
              >
                <svg className="-ml-1 mr-2 h-5 w-5 text-gray-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z" />
                </svg>
                Print Report
              </button>
            </div>
          </div>
          <div className="mt-4 text-xs text-gray-500">
            <p>This analysis is for informational purposes only and should not be considered as financial advice. Always conduct your own research before making investment decisions.</p>
          </div>
        </div>
      </footer>
    </div>
  )
}
