# PulseCompass - Quick Start Guide

## What Changed?

Your PulseCompass app has been completely redesigned to match the ManusAI-Research functionality with three core analysis tools:

1. **Management Integrity Analyzer** - Upload PDF transcripts, get integrity scores
2. **Financial Ranking System** - Upload Excel/CSV data, rank companies by investment philosophy
3. **Research Reports** - Coming soon
4. **Portfolio Analytics** - Coming soon

## Starting the Application

### Step 1: Install Backend Dependencies

```bash
cd "Z:\PROJECTS  APP\stocks analyzer\PulseCompass\backend"
pip install -r requirements.txt
```

### Step 2: Start Backend Server

```bash
cd "Z:\PROJECTS  APP\stocks analyzer\PulseCompass\backend"
python -m uvicorn main:app --reload --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

### Step 3: Install Frontend Dependencies (if needed)

```bash
cd "Z:\PROJECTS  APP\stocks analyzer\PulseCompass"
npm install
```

### Step 4: Start Frontend

```bash
cd "Z:\PROJECTS  APP\stocks analyzer\PulseCompass"
npm run dev
```

You should see:
```
- ready started server on 0.0.0.0:3000, url: http://localhost:3000
```

### Step 5: Open in Browser

Navigate to: **http://localhost:3000**

## Using the New Interface

### Dashboard View

You'll see:
- **Hero Section**: "PulseCompass Equity Research Platform"
- **Stats Cards**: 4 metric cards showing platform statistics
- **Analysis Tools**: 4 tool cards (2 active, 2 coming soon)
- **Getting Started**: Usage instructions

### Management Integrity Analyzer

1. Click **"Launch Tool"** on the Management Integrity Analyzer card
2. Enter company name (e.g., "Infosys Limited")
3. Click the upload area and select PDF transcript files
4. Click **"Analyze Integrity"**
5. View results:
   - Overall integrity score
   - Category scores (Communication, Delivery, Transparency, Strategy)
   - Key findings
   - Guidance statements

**Test with**: Any earnings call transcript PDF

### Financial Ranking System

1. Click **"Launch Tool"** on the Financial Ranking System card
2. Click upload area and select CSV or Excel file
3. Select investment philosophy:
   - Warren Buffett (Value + Quality)
   - Peter Lynch (GARP)
   - Growth Investing
   - Value Investing
   - Dividend Focus
   - Custom Weights
4. Click **"Rank Companies"**
5. View rankings table with scores and key drivers

**Test with**: CSV file from Screener.in or similar with columns: Name, Symbol, ROE, ROCE, Debt/Equity, Profit Growth

## Sample CSV Format

Create a test file `test_companies.csv`:

```csv
Name,Symbol,ROE,ROCE,Debt/Equity,Profit Growth 3Yr,FCF
TCS,TCS,45.2,38.5,0.12,15.3,8500
Infosys,INFY,28.5,32.1,0.08,12.5,7200
Wipro,WIPRO,18.2,22.5,0.15,8.5,3500
HCL Tech,HCLTECH,22.8,28.3,0.05,10.2,5200
Tech Mahindra,TECHM,15.5,19.8,0.22,6.5,2800
```

## API Documentation

Once backend is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Key API Endpoints

### Integrity Analysis
```
POST http://localhost:8000/api/v1/integrity/analyze
```

### Financial Ranking
```
POST http://localhost:8000/api/v1/ranking/analyze
```

### Get Philosophies
```
GET http://localhost:8000/api/v1/ranking/philosophies
```

## What Was Removed

The following features were removed to focus on analysis tools:
- Portfolio value tracking
- Watchlist companies
- Position management
- Recent activity feed
- Alerts system
- Generic comparison views

These were replaced with specialized analysis tools.

## Troubleshooting

### Backend won't start

**Error**: `ModuleNotFoundError: No module named 'routers'`

**Solution**: Make sure you're in the backend directory:
```bash
cd "Z:\PROJECTS  APP\stocks analyzer\PulseCompass\backend"
python -m uvicorn main:app --reload
```

### Frontend shows errors

**Error**: `Cannot find module '@/components/IntegrityAnalyzer'`

**Solution**: The components are created but may need TypeScript to recognize them. Try:
```bash
npm run dev
```

If issues persist, restart the dev server.

### PDF upload fails

**Check**:
- PDF is not password-protected
- PDF contains extractable text (not scanned image)
- File size is reasonable (< 10MB)

### Excel upload fails

**Check**:
- File has required columns: Name, Symbol
- Numeric columns contain valid numbers
- File format is CSV, XLSX, or XLS

## Next Steps

1. **Test with Real Data**: Use actual earnings transcripts and financial data
2. **Customize Philosophies**: Modify weights in `backend/routers/ranking.py`
3. **Add More Analysis**: Extend the integrity analysis logic
4. **Export Reports**: Implement PDF export functionality

## File Locations

### Frontend
- Main page: `app/page.tsx`
- Integrity component: `components/IntegrityAnalyzer.tsx`
- Ranking component: `components/RankingSystem.tsx`

### Backend
- Main app: `backend/main.py`
- Integrity router: `backend/routers/integrity.py`
- Ranking router: `backend/routers/ranking.py`

## Support

For issues or questions:
1. Check `REDESIGN_README.md` for detailed documentation
2. Review API docs at http://localhost:8000/docs
3. Check browser console for frontend errors
4. Check terminal for backend errors

---

**Your app is now focused on professional equity analysis tools!**
