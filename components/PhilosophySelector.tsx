'use client'

import { useState } from 'react'
import { ChevronDown, Info } from 'lucide-react'

interface Philosophy {
  name: string
  description: string
  key_principles: string[]
}

interface PhilosophySelectorProps {
  philosophies: Record<string, Philosophy>
  selectedPhilosophy: string
  onSelect: (philosophy: string) => void
}

const philosophyIcons: Record<string, string> = {
  buffett: '🎯',
  graham: '📊',
  lynch: '📈',
  munger: '🧠',
  growth: '🚀',
  value: '💎',
  quality: '⭐'
}

const philosophyColors: Record<string, string> = {
  buffett: 'from-blue-500 to-blue-600',
  graham: 'from-green-500 to-green-600',
  lynch: 'from-purple-500 to-purple-600',
  munger: 'from-orange-500 to-orange-600',
  growth: 'from-pink-500 to-pink-600',
  value: 'from-teal-500 to-teal-600',
  quality: 'from-indigo-500 to-indigo-600'
}

export default function PhilosophySelector({
  philosophies,
  selectedPhilosophy,
  onSelect
}: PhilosophySelectorProps) {
  const [isOpen, setIsOpen] = useState(false)
  const [showInfo, setShowInfo] = useState<string | null>(null)

  const selected = philosophies[selectedPhilosophy]

  return (
    <div className="relative">
      {/* Selector Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center justify-between px-4 py-3 bg-white border-2 border-gray-200 rounded-lg hover:border-primary-500 transition-colors"
      >
        <div className="flex items-center gap-3">
          <span className="text-2xl">{philosophyIcons[selectedPhilosophy]}</span>
          <div className="text-left">
            <div className="font-semibold text-gray-900">{selected?.name}</div>
            <div className="text-sm text-gray-500 line-clamp-1">{selected?.description}</div>
          </div>
        </div>
        <ChevronDown className={`w-5 h-5 text-gray-400 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
      </button>

      {/* Dropdown Menu */}
      {isOpen && (
        <div className="absolute z-50 w-full mt-2 bg-white border border-gray-200 rounded-lg shadow-xl max-h-96 overflow-y-auto">
          {Object.entries(philosophies).map(([key, philosophy]) => (
            <div key={key} className="relative">
              <button
                onClick={() => {
                  onSelect(key)
                  setIsOpen(false)
                  setShowInfo(null)
                }}
                className={`w-full flex items-center gap-3 px-4 py-3 hover:bg-gray-50 transition-colors ${
                  selectedPhilosophy === key ? 'bg-primary-50' : ''
                }`}
              >
                <span className="text-2xl">{philosophyIcons[key]}</span>
                <div className="flex-1 text-left">
                  <div className="font-semibold text-gray-900">{philosophy.name}</div>
                  <div className="text-sm text-gray-500 line-clamp-1">{philosophy.description}</div>
                </div>
                <button
                  onClick={(e) => {
                    e.stopPropagation()
                    setShowInfo(showInfo === key ? null : key)
                  }}
                  className="p-1 hover:bg-gray-200 rounded-full transition-colors"
                >
                  <Info className="w-4 h-4 text-gray-400" />
                </button>
              </button>

              {/* Philosophy Info Popup */}
              {showInfo === key && (
                <div className="px-4 py-3 bg-gray-50 border-t border-gray-200">
                  <div className="text-sm font-medium text-gray-700 mb-2">Key Principles:</div>
                  <ul className="space-y-1">
                    {philosophy.key_principles.map((principle, idx) => (
                      <li key={idx} className="text-sm text-gray-600 flex items-start gap-2">
                        <span className="text-primary-500 mt-0.5">•</span>
                        <span>{principle}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Overlay */}
      {isOpen && (
        <div
          className="fixed inset-0 z-40"
          onClick={() => {
            setIsOpen(false)
            setShowInfo(null)
          }}
        />
      )}
    </div>
  )
}
