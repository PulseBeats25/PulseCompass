# PulseCompass - Redesigned Equity Research Platform

## Overview

PulseCompass has been completely redesigned to focus on three core analysis tools for equity research:

1. **Management Integrity Analyzer** - Analyze management credibility through PDF transcript analysis
2. **Financial Ranking System** - Rank companies using fundamental metrics with multiple investment philosophies
3. **Research Report Analyzer** - Coming soon

This redesign aligns with professional equity analysis workflows, removing portfolio/watchlist features in favor of specialized analysis tools.

## Key Changes

### Frontend (Next.js + TypeScript)

#### New Dashboard (`app/page.tsx`)
- **Hero Section**: Professional gradient header with platform description
- **Stats Cards**: Key metrics display (Companies Analyzed, Integrity Score Avg, Top Ranked Stock, Reports Generated)
- **Tool Cards**: Four analysis tool cards with:
  - Feature descriptions
  - Key capabilities
  - Launch buttons (active/coming soon status)
- **Getting Started**: Usage instructions and system requirements

#### New Components

**IntegrityAnalyzer Component** (`components/IntegrityAnalyzer.tsx`)
- PDF upload interface for earnings call transcripts
- Company name input
- Real-time analysis with loading states
- Results display with:
  - Overall integrity score
  - Category scores (Communication, Delivery, Transparency, Strategy)
  - Key findings
  - Guidance statements extraction
- Export functionality

**RankingSystem Component** (`components/RankingSystem.tsx`)
- CSV/Excel file upload for financial data
- Investment philosophy selection:
  - Warren Buffett (Value + Quality)
  - Peter Lynch (GARP)
  - Growth Investing
  - Value Investing
  - Dividend Focus
  - Custom Weights
- Results table with:
  - Company rankings
  - Composite scores
  - Key financial metrics (ROE, ROCE, D/E)
  - Key performance drivers
- Export functionality

### Backend (FastAPI + Python)

#### New Routers

**Integrity Router** (`backend/routers/integrity.py`)
- `POST /api/v1/integrity/analyze` - Analyze PDF transcripts
  - Accepts multiple PDF files
  - Extracts text using PyPDF2
  - Analyzes management integrity with weighted scoring
  - Extracts guidance statements using regex patterns
  - Returns comprehensive analysis with evidence

**Ranking Router** (`backend/routers/ranking.py`)
- `POST /api/v1/ranking/analyze` - Rank companies from financial data
  - Accepts CSV or Excel files
  - Normalizes column names (handles Screener.in format)
  - Applies investment philosophy weights
  - Calculates composite scores
  - Returns ranked list with key drivers
- `GET /api/v1/ranking/philosophies` - Get available philosophies

#### Analysis Logic

**Integrity Analysis**:
- Delivery indicators (positive): delivered, achieved, exceeded, outperformed
- Concern indicators (negative): missed, failed, disappointed, shortfall
- Category scoring: Communication, Delivery, Transparency, Strategy
- Guidance extraction: Revenue, Profitability, Investment, Outlook patterns

**Ranking System**:
- Metric normalization (0-100 scale)
- Weighted composite scoring
- Philosophy-specific weights
- Key driver identification
- Support for multiple file formats

## Installation & Setup

### Prerequisites
- Python 3.8+
- Node.js 16+
- npm or yarn

### Backend Setup

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Start the server
python -m uvicorn main:app --reload --port 8000
```

### Frontend Setup

```bash
# Install dependencies
npm install

# Start development server
npm run dev
```

The app will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Usage Guide

### Management Integrity Analyzer

1. Click "Launch Tool" on the Management Integrity Analyzer card
2. Enter the company name
3. Upload one or more PDF transcripts (earnings calls, conference calls)
4. Click "Analyze Integrity"
5. Review the results:
   - Overall integrity score (0-100)
   - Category breakdowns with evidence
   - Key findings
   - Extracted guidance statements
6. Export the report if needed

**Supported Files**: PDF format only

### Financial Ranking System

1. Click "Launch Tool" on the Financial Ranking System card
2. Upload a CSV or Excel file with company financial data
3. Select an investment philosophy:
   - **Buffett**: Focus on ROE, low debt, strong fundamentals
   - **Lynch**: Growth at reasonable price
   - **Growth**: High growth companies
   - **Value**: Undervalued with strong fundamentals
   - **Dividend**: Income-generating stable companies
   - **Custom**: Define your own weights
4. Click "Rank Companies"
5. Review the rankings table with scores and key drivers
6. Export the rankings if needed

**Required Columns**: Company name, Symbol
**Optional Columns**: ROE, ROCE, Debt/Equity, Profit Growth, FCF

**Supported Files**: CSV, XLSX, XLS

## File Format Examples

### Financial Data CSV Format

```csv
Name,Symbol,ROE,ROCE,Debt/Equity,Profit Growth 3Yr,FCF
TCS,TCS,45.2,38.5,0.12,15.3,8500
Infosys,INFY,28.5,32.1,0.08,12.5,7200
Wipro,WIPRO,18.2,22.5,0.15,8.5,3500
```

### Transcript PDF Requirements

- Earnings call transcripts
- Conference call transcripts
- Management presentations
- Clear text (not scanned images)
- English language

## API Endpoints

### Integrity Analysis

```
POST /api/v1/integrity/analyze
Content-Type: multipart/form-data

Parameters:
- files: List of PDF files
- company_name: String

Response:
{
  "company": "Company Name",
  "overallScore": 78.5,
  "categories": {
    "Communication": { "score": 75, "status": "Good", "evidence": [...] },
    ...
  },
  "guidanceStatements": [...],
  "keyFindings": [...]
}
```

### Financial Ranking

```
POST /api/v1/ranking/analyze
Content-Type: multipart/form-data

Parameters:
- file: CSV or Excel file
- philosophy: String (buffett, lynch, growth, value, dividend, custom)

Response:
{
  "rankings": [
    {
      "rank": 1,
      "company": "TCS",
      "symbol": "TCS",
      "compositeScore": 92.5,
      "buffettScore": 88.0,
      "lynchScore": 95.0,
      "keyDrivers": ["ROE>45%", "Low D/E", "Strong FCF"],
      "metrics": { "roe": 45.2, "roce": 38.5, ... }
    },
    ...
  ],
  "philosophy": "buffett",
  "totalCompanies": 150
}
```

## Technology Stack

### Frontend
- **Framework**: Next.js 13+ with App Router
- **Language**: TypeScript
- **Styling**: TailwindCSS
- **Animations**: Framer Motion
- **Icons**: Lucide React
- **HTTP Client**: Fetch API

### Backend
- **Framework**: FastAPI
- **Language**: Python 3.8+
- **PDF Processing**: PyPDF2, PyMuPDF, pdfplumber
- **Data Processing**: pandas, numpy
- **Excel Support**: openpyxl, xlrd

## Removed Features

The following features were removed to focus on core analysis tools:

- Portfolio management
- Watchlist tracking
- Real-time market data
- Position tracking
- P&L calculations
- Comparison views (generic)

These may be reintroduced as separate modules in future updates.

## Future Enhancements

### Phase 1 (Current)
- ✅ Management Integrity Analyzer
- ✅ Financial Ranking System
- ✅ Modern dashboard UI

### Phase 2 (Planned)
- Research Report Analyzer
- Multi-document analysis
- Advanced NLP for transcript analysis
- Historical integrity tracking

### Phase 3 (Future)
- Portfolio Analytics module
- Real-time data integration
- Advanced visualizations
- Mobile app

## Troubleshooting

### Backend Issues

**Import errors for routers**:
```bash
# Ensure you're in the backend directory
cd backend
python -m uvicorn main:app --reload
```

**PDF parsing errors**:
- Ensure PDFs contain extractable text (not scanned images)
- Check file size limits
- Verify PDF is not password-protected

**Excel file errors**:
- Ensure column names match expected format
- Check for required columns (Name, Symbol)
- Verify numeric columns contain valid numbers

### Frontend Issues

**Component import errors**:
- Ensure all components are in the `components/` directory
- Check file extensions (.tsx)
- Verify export statements

**API connection errors**:
- Ensure backend is running on port 8000
- Check CORS settings in backend
- Verify API endpoints in component files

## Contributing

This is a redesigned architecture focused on professional equity analysis. When contributing:

1. Maintain the three-tool structure
2. Keep UI/UX consistent with the dashboard design
3. Follow existing code patterns
4. Add tests for new analysis logic
5. Update documentation

## License

MIT License

---

**Built for professional equity analysts and investors**
