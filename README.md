# PulseCompass

## Quick Start
- Backend: uvicorn backend.main:app --reload
- Frontend: npm ci && npm run dev

## API
- POST /api/v1/ranking/analyze (fields: file, philosophy, fcfDQMode)

## Excel formats
- Screener-style and new format supported.

## Scoring
- V1 philosophies + V2 sub-scores (Quality/Growth/Valuation/Cashflow), sector-aware.
