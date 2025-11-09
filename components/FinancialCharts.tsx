'use client'

import { LineChart, Line, BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

interface TrendData {
  period: string
  revenue: number
  profit: number
  eps?: number
}

interface RatioData {
  name: string
  value: number
  status: 'good' | 'neutral' | 'bad'
}

interface FinancialChartsProps {
  trendData?: TrendData[]
  ratioData?: RatioData[]
  showTrends?: boolean
  showRatios?: boolean
}

const COLORS = {
  good: '#10b981',
  neutral: '#f59e0b',
  bad: '#ef4444',
  primary: '#3b82f6',
  secondary: '#8b5cf6'
}

export default function FinancialCharts({ 
  trendData = [], 
  ratioData = [],
  showTrends = true,
  showRatios = true
}: FinancialChartsProps) {
  
  // Default sample data if none provided
  const defaultTrendData: TrendData[] = [
    { period: 'Q1 2023', revenue: 350, profit: 85, eps: 2.1 },
    { period: 'Q2 2023', revenue: 380, profit: 92, eps: 2.3 },
    { period: 'Q3 2023', revenue: 410, profit: 98, eps: 2.5 },
    { period: 'Q4 2023', revenue: 445, profit: 105, eps: 2.7 },
  ]

  const defaultRatioData: RatioData[] = [
    { name: 'ROE', value: 15.5, status: 'good' },
    { name: 'ROA', value: 8.2, status: 'neutral' },
    { name: 'Debt/Equity', value: 0.45, status: 'good' },
    { name: 'Current Ratio', value: 1.8, status: 'good' },
    { name: 'Net Margin', value: 12.3, status: 'good' },
    { name: 'P/E Ratio', value: 22.5, status: 'neutral' },
  ]

  const displayTrendData = trendData.length > 0 ? trendData : defaultTrendData
  const displayRatioData = ratioData.length > 0 ? ratioData : defaultRatioData

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white p-3 border border-gray-200 rounded-lg shadow-lg">
          <p className="font-semibold text-gray-900 mb-1">{label}</p>
          {payload.map((entry: any, index: number) => (
            <p key={index} className="text-sm" style={{ color: entry.color }}>
              {entry.name}: {typeof entry.value === 'number' ? entry.value.toFixed(2) : entry.value}
            </p>
          ))}
        </div>
      )
    }
    return null
  }

  return (
    <div className="space-y-8">
      {/* Revenue & Profit Trend Chart */}
      {showTrends && (
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Revenue & Profit Trends</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={displayTrendData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis 
                dataKey="period" 
                stroke="#6b7280"
                style={{ fontSize: '12px' }}
              />
              <YAxis 
                stroke="#6b7280"
                style={{ fontSize: '12px' }}
              />
              <Tooltip content={<CustomTooltip />} />
              <Legend 
                wrapperStyle={{ fontSize: '14px' }}
                iconType="line"
              />
              <Line 
                type="monotone" 
                dataKey="revenue" 
                stroke={COLORS.primary} 
                strokeWidth={2}
                name="Revenue"
                dot={{ fill: COLORS.primary, r: 4 }}
                activeDot={{ r: 6 }}
              />
              <Line 
                type="monotone" 
                dataKey="profit" 
                stroke={COLORS.secondary} 
                strokeWidth={2}
                name="Net Profit"
                dot={{ fill: COLORS.secondary, r: 4 }}
                activeDot={{ r: 6 }}
              />
              {displayTrendData[0]?.eps !== undefined && (
                <Line 
                  type="monotone" 
                  dataKey="eps" 
                  stroke={COLORS.good} 
                  strokeWidth={2}
                  name="EPS"
                  dot={{ fill: COLORS.good, r: 4 }}
                  activeDot={{ r: 6 }}
                />
              )}
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Financial Ratios Bar Chart */}
      {showRatios && (
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Key Financial Ratios</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={displayRatioData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis 
                dataKey="name" 
                stroke="#6b7280"
                style={{ fontSize: '12px' }}
              />
              <YAxis 
                stroke="#6b7280"
                style={{ fontSize: '12px' }}
              />
              <Tooltip content={<CustomTooltip />} />
              <Bar dataKey="value" radius={[8, 8, 0, 0]}>
                {displayRatioData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[entry.status]} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
          
          {/* Legend for status colors */}
          <div className="flex items-center justify-center gap-6 mt-4 text-sm">
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full" style={{ backgroundColor: COLORS.good }}></div>
              <span className="text-gray-600">Good</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full" style={{ backgroundColor: COLORS.neutral }}></div>
              <span className="text-gray-600">Neutral</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full" style={{ backgroundColor: COLORS.bad }}></div>
              <span className="text-gray-600">Concerning</span>
            </div>
          </div>
        </div>
      )}

      {/* Ratio Distribution Pie Chart */}
      {showRatios && displayRatioData.length > 0 && (
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Ratio Health Distribution</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={displayRatioData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                outerRadius={100}
                fill="#8884d8"
                dataKey="value"
              >
                {displayRatioData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[entry.status]} />
                ))}
              </Pie>
              <Tooltip content={<CustomTooltip />} />
            </PieChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  )
}
