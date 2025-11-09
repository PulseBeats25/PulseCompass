from pydantic import BaseModel
from typing import List, Dict, Optional, Any
from datetime import datetime

class UploadResponse(BaseModel):
    success: bool
    message: str
    files: List[Dict[str, Any]]

class TranscriptSummary(BaseModel):
    id: str
    company_id: str
    quarter: str
    year: int
    raw_text: str
    summary: Dict[str, Any]
    integrity_score: int
    key_quotes: List[str]
    management_tone: str
    created_at: datetime

class FinancialMetrics(BaseModel):
    id: str
    company_id: str
    period: datetime
    revenue: Optional[float]
    net_profit: Optional[float]
    eps: Optional[float]
    roe: Optional[float]
    roce: Optional[float]
    debt_equity: Optional[float]
    pe_ratio: Optional[float]
    pb_ratio: Optional[float]
    ev_ebitda: Optional[float]
    traffic_lights: Dict[str, Dict[str, Any]]
    created_at: datetime

class InvestorView(BaseModel):
    investor_name: str = ""
    score: float = 0.0
    strengths: List[str] = []
    concerns: List[str] = []
    assessment: str = ""
    key_factors: Dict[str, str] = {}
    reasoning: str = ""

class InvestorViews(BaseModel):
    warren_buffett: Optional[InvestorView] = None
    benjamin_graham: Optional[InvestorView] = None
    peter_lynch: Optional[InvestorView] = None
    charlie_munger: Optional[InvestorView] = None
    consensus: Dict[str, Any] = {}

class Recommendation(BaseModel):
    rating: str  # Strong Buy, Buy, Hold, Avoid
    target_price: Optional[float]
    current_price: Optional[float]
    margin_of_safety: Optional[float]
    confidence_score: float
    reasoning: str
    risk_factors: List[str]
    catalysts: List[str]

class CompanyAnalysis(BaseModel):
    company_id: str
    company_name: str
    transcript_summary: TranscriptSummary
    financial_metrics: FinancialMetrics
    investor_views: InvestorViews
    recommendation: Recommendation
    ratings_summary: Optional[Dict[str, str]] = {}
    last_updated: datetime

class Company(BaseModel):
    id: str
    name: str
    ticker: str
    sector: Optional[str]
    created_at: datetime

class PortfolioPosition(BaseModel):
    id: str
    user_id: str
    company_id: str
    company_name: str
    ticker: str
    quantity: int
    buy_price: float
    current_price: float
    market_value: float
    unrealized_pnl: float
    unrealized_pnl_percent: float
    weight: float

class Portfolio(BaseModel):
    user_id: str
    total_value: float
    day_change: float
    day_change_percent: float
    positions: List[PortfolioPosition]
    last_updated: datetime

class WatchlistItem(BaseModel):
    id: str
    user_id: str
    company_id: str
    company_name: str
    ticker: str
    current_price: float
    day_change: float
    day_change_percent: float
    recommendation: Optional[str]
    added_at: datetime

class Watchlist(BaseModel):
    user_id: str
    items: List[Dict[str, Any]]
    last_updated: datetime
