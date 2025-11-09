# PulseCompass 📈

Advanced Stock Market Analysis Platform with AI-powered insights, built for equity analysts and investors.

## 🌟 Features

- **📄 Document Processing**: Upload and analyze PDF transcripts and Excel financial data
- **🤖 AI Analysis**: Ollama-powered LLM integration for intelligent insights
- **👥 Investor Views**: Analysis from Buffett, Graham, Lynch, and Munger perspectives
- **📊 Financial Metrics**: Comprehensive financial health assessment with traffic-light indicators
- **🎯 Recommendations**: AI-generated buy/hold/sell recommendations with reasoning
- **💼 Portfolio Management**: Track your investments and performance
- **👀 Watchlist**: Monitor companies of interest
- **🔍 Semantic Search**: Query transcripts using natural language
- **📈 Valuation Engine**: Multiple valuation methods (DCF, Graham, PE, PEG)

## 🏗️ Architecture

### Frontend (Next.js + TypeScript)
- **Framework**: Next.js 13+ with App Router
- **Styling**: TailwindCSS with custom fintech theme
- **Components**: Modern React components with Framer Motion animations
- **Icons**: Lucide React icons
- **State**: React hooks and context

### Backend (FastAPI + Python)
- **API**: FastAPI with automatic OpenAPI documentation
- **Database**: Supabase (PostgreSQL + pgvector for embeddings)
- **LLM**: Ollama integration for local AI processing
- **Parsing**: PyMuPDF, pdfplumber for PDFs; pandas, openpyxl for Excel
- **Analysis**: Custom recommendation engine with multi-factor scoring

### Database Schema
- **Users**: Authentication and user management
- **Companies**: Company master data
- **Transcripts**: Earnings call transcripts with embeddings
- **Financials**: Financial metrics and ratios
- **Portfolio**: User investment positions
- **Watchlist**: Companies being monitored
- **Analysis**: Cached analysis results

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- Supabase account (for database)
- Ollama (for local LLM, optional)

### 1. Clone and Setup
```bash
cd PulseCompass
```

### 2. Backend Setup
```bash
cd backend
pip install -r requirements.txt

# Copy and configure environment
cp .env.example .env
# Edit .env with your Supabase credentials
```

### 3. Database Setup
1. Create a new Supabase project
2. Run the SQL schema from `backend/database/schema.sql`
3. Enable the `vector` extension for embeddings
4. Update `.env` with your Supabase URL and keys

### 4. Frontend Setup
```bash
npm install
```

### 5. Start Development Servers
```bash
# Option 1: Use the startup script
python start_dev.py

# Option 2: Start manually
# Terminal 1 - Backend
cd backend && python -m uvicorn main:app --reload

# Terminal 2 - Frontend  
npm run dev
```

### 6. Test with Real Data
```bash
python test_real_data.py
```

## 📊 Usage

### 1. Upload Documents
- **PDFs**: Earnings call transcripts, annual reports
- **Excel/CSV**: Financial data, screener outputs

### 2. Company Analysis
- View comprehensive analysis combining transcript and financial data
- Get investor-style perspectives from legendary investors
- See AI-generated recommendations with reasoning

### 3. Portfolio Management
- Add positions to your portfolio
- Track performance and P&L
- Get portfolio-level insights

### 4. Semantic Search
- Query transcripts using natural language
- Find specific management commentary
- Discover insights across multiple quarters

## 🔧 Configuration

### Environment Variables (.env)
```bash
# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-key

# Ollama (optional)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2

# API
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=True
```

### Ollama Setup (Optional)
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull a model
ollama pull llama2

# Start Ollama server
ollama serve
```

## 📁 Project Structure

```
PulseCompass/
├── app/                    # Next.js app directory
│   ├── globals.css        # Global styles
│   ├── layout.tsx         # Root layout
│   └── page.tsx           # Homepage
├── components/            # React components
│   ├── CompanyTable.tsx   # Company watchlist table
│   ├── DashboardCard.tsx  # Metric cards
│   ├── UploadBox.tsx      # File upload component
│   └── ValuationGauge.tsx # Valuation score gauge
├── backend/               # FastAPI backend
│   ├── database/          # Database client and schema
│   ├── models/            # Pydantic schemas
│   ├── services/          # Business logic services
│   └── main.py            # FastAPI app
├── package.json           # Frontend dependencies
├── tailwind.config.js     # TailwindCSS configuration
└── README.md              # This file
```

## 🧪 Testing

### Real Data Testing
The system includes real data from EXICOM and KAYNES companies:
```bash
python test_real_data.py
```

### API Testing
Visit `http://localhost:8000/docs` for interactive API documentation.

## 🎨 UI/UX Design

- **Theme**: Professional fintech dashboard with clean, modern aesthetics
- **Colors**: Light theme with soft blue/gray accents
- **Typography**: Inter font for readability
- **Components**: Card-based layout with traffic-light indicators
- **Responsive**: Mobile-friendly design

## 🔍 Key Features Deep Dive

### Investor Views
- **Warren Buffett**: Focus on moats, management quality, long-term value
- **Benjamin Graham**: Value investing, margin of safety, financial strength
- **Peter Lynch**: Growth at reasonable price, industry knowledge
- **Charlie Munger**: Quality businesses, rational thinking, patience

### Recommendation Engine
Multi-factor scoring system considering:
- Financial health (40%)
- Management integrity (25%)
- Valuation attractiveness (20%)
- Growth prospects (10%)
- Risk factors (5%)

### Traffic Light System
- 🟢 **Green**: Strong/Healthy metrics
- 🟡 **Yellow**: Moderate/Watch metrics  
- 🔴 **Red**: Weak/Concerning metrics

## 🚧 Roadmap

- [ ] Real-time market data integration
- [ ] TradingView widget for technical analysis
- [ ] Advanced portfolio analytics
- [ ] Email alerts and notifications
- [ ] Mobile app (React Native)
- [ ] Multi-language support
- [ ] Advanced charting and visualization

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For support and questions:
- Check the API documentation at `/docs`
- Review the test files for usage examples
- Open an issue on GitHub

---

**Built with ❤️ for equity analysts and investors**
