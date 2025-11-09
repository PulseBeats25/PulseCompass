'use client'

import { RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, Cell } from 'recharts'
import { useState } from 'react'
import { TrendingUp, TrendingDown, Award } from 'lucide-react'

interface PhilosophyScore {
  name: string
  score: number
  rank: string
  strengths: string[]
  weaknesses: string[]
}

interface PhilosophyComparisonProps {
  scores: Record<string, PhilosophyScore>
  selectedPhilosophy?: string
  bestPhilosophy?: { name: string; score: number }
}

const philosophyColors: Record<string, string> = {
  buffett: '#3b82f6',
  graham: '#10b981',
  lynch: '#8b5cf6',
  munger: '#f97316',
  growth: '#ec4899',
  value: '#14b8a6',
  quality: '#6366f1'
}

const getRankColor = (rank: string) => {
  switch (rank) {
    case 'Excellent': return 'text-green-600 bg-green-50'
    case 'Strong': return 'text-blue-600 bg-blue-50'
    case 'Good': return 'text-yellow-600 bg-yellow-50'
    case 'Fair': return 'text-orange-600 bg-orange-50'
    case 'Poor': return 'text-red-600 bg-red-50'
    default: return 'text-gray-600 bg-gray-50'
  }
}

const getScoreColor = (score: number) => {
  if (score >= 85) return '#10b981' // green
  if (score >= 70) return '#3b82f6' // blue
  if (score >= 55) return '#f59e0b' // yellow
  if (score >= 40) return '#f97316' // orange
  return '#ef4444' // red
}

export default function PhilosophyComparison({
  scores,
  selectedPhilosophy,
  bestPhilosophy
}: PhilosophyComparisonProps) {
  const [chartType, setChartType] = useState<'radar' | 'bar'>('radar')

  // Prepare data for charts
  const radarData = Object.entries(scores)
    .filter(([key]) => key !== 'best_philosophy')
    .map(([key, data]) => ({
      philosophy: data.name.split(' ')[0], // Short name for chart
      score: data.score,
      fullName: data.name
    }))

  const barData = Object.entries(scores)
    .filter(([key]) => key !== 'best_philosophy')
    .map(([key, data]) => ({
      name: data.name.split(' ')[0],
      score: data.score,
      rank: data.rank,
      key: key
    }))
    .sort((a, b) => b.score - a.score)

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload
      return (
        <div className="bg-white p-3 border border-gray-200 rounded-lg shadow-lg">
          <p className="font-semibold text-gray-900">{data.fullName || data.name}</p>
          <p className="text-sm text-gray-600">Score: {data.score.toFixed(1)}</p>
          {data.rank && <p className="text-sm text-gray-600">Rank: {data.rank}</p>}
        </div>
      )
    }
    return null
  }

  return (
    <div className="space-y-6">
      {/* Best Philosophy Banner */}
      {bestPhilosophy && (
        <div className="bg-gradient-to-r from-primary-500 to-primary-600 rounded-lg p-4 text-white">
          <div className="flex items-center gap-3">
            <Award className="w-6 h-6" />
            <div>
              <div className="font-semibold">Best Fit Philosophy</div>
              <div className="text-sm opacity-90">
                {scores[bestPhilosophy.name]?.name} - Score: {bestPhilosophy.score.toFixed(1)}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Chart Type Toggle */}
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-gray-900">Philosophy Comparison</h3>
        <div className="flex gap-2">
          <button
            onClick={() => setChartType('radar')}
            className={`px-3 py-1 rounded-md text-sm font-medium transition-colors ${
              chartType === 'radar'
                ? 'bg-primary-500 text-white'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            Radar
          </button>
          <button
            onClick={() => setChartType('bar')}
            className={`px-3 py-1 rounded-md text-sm font-medium transition-colors ${
              chartType === 'bar'
                ? 'bg-primary-500 text-white'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            Bar
          </button>
        </div>
      </div>

      {/* Charts */}
      <div className="card">
        {chartType === 'radar' ? (
          <ResponsiveContainer width="100%" height={400}>
            <RadarChart data={radarData}>
              <PolarGrid stroke="#e5e7eb" />
              <PolarAngleAxis
                dataKey="philosophy"
                tick={{ fill: '#6b7280', fontSize: 12 }}
              />
              <PolarRadiusAxis
                angle={90}
                domain={[0, 100]}
                tick={{ fill: '#6b7280', fontSize: 10 }}
              />
              <Radar
                name="Score"
                dataKey="score"
                stroke="#3b82f6"
                fill="#3b82f6"
                fillOpacity={0.6}
              />
              <Tooltip content={<CustomTooltip />} />
            </RadarChart>
          </ResponsiveContainer>
        ) : (
          <ResponsiveContainer width="100%" height={400}>
            <BarChart data={barData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis
                dataKey="name"
                stroke="#6b7280"
                style={{ fontSize: '12px' }}
              />
              <YAxis
                domain={[0, 100]}
                stroke="#6b7280"
                style={{ fontSize: '12px' }}
              />
              <Tooltip content={<CustomTooltip />} />
              <Bar dataKey="score" radius={[8, 8, 0, 0]}>
                {barData.map((entry, index) => (
                  <Cell
                    key={`cell-${index}`}
                    fill={philosophyColors[entry.key] || '#3b82f6'}
                  />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        )}
      </div>

      {/* Score Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
        {Object.entries(scores)
          .filter(([key]) => key !== 'best_philosophy')
          .sort(([, a], [, b]) => b.score - a.score)
          .map(([key, data]) => (
            <div
              key={key}
              className={`card ${
                selectedPhilosophy === key ? 'ring-2 ring-primary-500' : ''
              }`}
            >
              <div className="flex items-start justify-between mb-3">
                <div>
                  <div className="font-semibold text-gray-900 text-sm">
                    {data.name.split(' ')[0]}
                  </div>
                  <div className={`inline-block px-2 py-0.5 rounded-full text-xs font-medium mt-1 ${getRankColor(data.rank)}`}>
                    {data.rank}
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-2xl font-bold" style={{ color: getScoreColor(data.score) }}>
                    {data.score.toFixed(0)}
                  </div>
                  <div className="text-xs text-gray-500">/ 100</div>
                </div>
              </div>

              {/* Progress Bar */}
              <div className="w-full bg-gray-200 rounded-full h-2 mb-3">
                <div
                  className="h-2 rounded-full transition-all"
                  style={{
                    width: `${data.score}%`,
                    backgroundColor: getScoreColor(data.score)
                  }}
                />
              </div>

              {/* Strengths */}
              {data.strengths.length > 0 && (
                <div className="mb-2">
                  <div className="flex items-center gap-1 text-xs font-medium text-green-600 mb-1">
                    <TrendingUp className="w-3 h-3" />
                    <span>Strengths</span>
                  </div>
                  <div className="space-y-1">
                    {data.strengths.slice(0, 2).map((strength, idx) => (
                      <div key={idx} className="text-xs text-gray-600 line-clamp-1">
                        • {strength}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Weaknesses */}
              {data.weaknesses.length > 0 && (
                <div>
                  <div className="flex items-center gap-1 text-xs font-medium text-red-600 mb-1">
                    <TrendingDown className="w-3 h-3" />
                    <span>Weaknesses</span>
                  </div>
                  <div className="space-y-1">
                    {data.weaknesses.slice(0, 2).map((weakness, idx) => (
                      <div key={idx} className="text-xs text-gray-600 line-clamp-1">
                        • {weakness}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ))}
      </div>
    </div>
  )
}
