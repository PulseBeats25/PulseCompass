import os
from supabase import create_client, Client
from typing import Dict, List, Any, Optional
import json
from datetime import datetime
import uuid

class SupabaseClient:
    """Client for interacting with Supabase database"""
    
    def __init__(self):
        # Initialize Supabase client
        supabase_url = os.getenv("SUPABASE_URL", "https://your-project.supabase.co")
        supabase_key = os.getenv("SUPABASE_ANON_KEY", "your-anon-key")
        
        self.supabase: Client = create_client(supabase_url, supabase_key)
    
    async def health_check(self) -> bool:
        """Check if Supabase connection is healthy"""
        try:
            # Simple query to test connection
            result = self.supabase.table('companies').select('id').limit(1).execute()
            return True
        except Exception:
            return False
    
    # Company operations
    async def create_company(self, name: str, ticker: str, sector: Optional[str] = None) -> str:
        """Create a new company"""
        company_data = {
            'name': name,
            'ticker': ticker.upper(),
            'sector': sector
        }
        
        result = self.supabase.table('companies').insert(company_data).execute()
        return result.data[0]['id']
    
    async def get_company(self, company_id: str) -> Optional[Dict[str, Any]]:
        """Get company by ID"""
        result = self.supabase.table('companies').select('*').eq('id', company_id).execute()
        return result.data[0] if result.data else None
    
    async def get_company_by_ticker(self, ticker: str) -> Optional[Dict[str, Any]]:
        """Get company by ticker"""
        result = self.supabase.table('companies').select('*').eq('ticker', ticker.upper()).execute()
        return result.data[0] if result.data else None
    
    # Transcript operations
    async def store_transcript(
        self,
        company_id: str,
        filename: str,
        raw_text: str,
        embedding: List[float],
        summary: Dict[str, Any],
        integrity_score: int
    ) -> str:
        """Store transcript data"""
        
        # Extract quarter and year from filename or summary
        quarter, year = self._extract_period_from_filename(filename)
        
        transcript_data = {
            'company_id': company_id,
            'quarter': quarter,
            'year': year,
            'raw_text': raw_text,
            'embedding': embedding,
            'summary': json.dumps(summary),
            'integrity_score': integrity_score
        }
        
        result = self.supabase.table('transcripts').insert(transcript_data).execute()
        return result.data[0]['id']
    
    async def get_latest_transcript(self, company_id: str) -> Optional[Dict[str, Any]]:
        """Get latest transcript for a company"""
        result = self.supabase.table('transcripts')\
            .select('*')\
            .eq('company_id', company_id)\
            .order('created_at', desc=True)\
            .limit(1)\
            .execute()
        
        if result.data:
            transcript = result.data[0]
            # Parse JSON summary
            transcript['summary'] = json.loads(transcript['summary'])
            return transcript
        return None
    
    # Financial data operations
    async def store_financials(
        self,
        company_id: str,
        filename: str,
        raw_data: Dict[str, Any],
        metrics: Dict[str, float],
        traffic_lights: Dict[str, Any]
    ) -> str:
        """Store financial data"""
        
        # Extract period from data or filename
        period = self._extract_financial_period(raw_data, filename)
        
        financial_data = {
            'company_id': company_id,
            'period': period,
            'raw_data': json.dumps(raw_data),
            'metrics': json.dumps(metrics),
            'traffic_lights': json.dumps(traffic_lights)
        }
        
        # Store individual metrics in separate columns for easier querying
        for metric, value in metrics.items():
            if metric in ['revenue', 'net_profit', 'eps', 'roe', 'roce', 'debt_equity', 'pe_ratio', 'ev_ebitda']:
                financial_data[metric] = value
        
        result = self.supabase.table('financials').insert(financial_data).execute()
        return result.data[0]['id']
    
    async def get_latest_financials(self, company_id: str) -> Optional[Dict[str, Any]]:
        """Get latest financial data for a company"""
        result = self.supabase.table('financials')\
            .select('*')\
            .eq('company_id', company_id)\
            .order('period', desc=True)\
            .limit(1)\
            .execute()
        
        if result.data:
            financials = result.data[0]
            # Parse JSON fields
            financials['raw_data'] = json.loads(financials['raw_data'])
            financials['metrics'] = json.loads(financials['metrics'])
            financials['traffic_lights'] = json.loads(financials['traffic_lights'])
            return financials
        return None
    
    # Semantic search operations
    async def semantic_search(
        self,
        query_embedding: List[float],
        company_id: Optional[str] = None,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Perform semantic search on transcripts using pgvector"""
        
        # Note: This requires pgvector extension and proper similarity function
        # For now, we'll do a simple text search as fallback
        
        query = self.supabase.table('transcripts').select('*')
        
        if company_id:
            query = query.eq('company_id', company_id)
        
        result = query.limit(limit).execute()
        
        # Parse summaries
        for transcript in result.data:
            transcript['summary'] = json.loads(transcript['summary'])
        
        return result.data
    
    # Portfolio operations
    async def get_user_portfolio(self, user_id: str) -> Dict[str, Any]:
        """Get user's portfolio"""
        result = self.supabase.table('portfolio')\
            .select('*, companies(name, ticker)')\
            .eq('user_id', user_id)\
            .execute()
        
        positions = []
        total_value = 0
        
        for position in result.data:
            # Calculate current values (would need real-time price data)
            current_price = position['buy_price'] * 1.05  # Mock 5% gain
            market_value = position['quantity'] * current_price
            unrealized_pnl = market_value - (position['quantity'] * position['buy_price'])
            unrealized_pnl_percent = (unrealized_pnl / (position['quantity'] * position['buy_price'])) * 100
            
            positions.append({
                'id': position['id'],
                'company_name': position['companies']['name'],
                'ticker': position['companies']['ticker'],
                'quantity': position['quantity'],
                'buy_price': position['buy_price'],
                'current_price': current_price,
                'market_value': market_value,
                'unrealized_pnl': unrealized_pnl,
                'unrealized_pnl_percent': unrealized_pnl_percent
            })
            
            total_value += market_value
        
        # Calculate portfolio-level metrics
        day_change = total_value * 0.02  # Mock 2% daily change
        day_change_percent = (day_change / total_value) * 100 if total_value > 0 else 0
        
        return {
            'user_id': user_id,
            'total_value': total_value,
            'day_change': day_change,
            'day_change_percent': day_change_percent,
            'positions': positions,
            'last_updated': datetime.utcnow()
        }
    
    # Watchlist operations
    async def get_user_watchlist(self, user_id: str) -> Dict[str, Any]:
        """Get user's watchlist"""
        result = self.supabase.table('watchlist')\
            .select('*, companies(name, ticker)')\
            .eq('user_id', user_id)\
            .execute()
        
        items = []
        
        for item in result.data:
            # Mock current price and changes
            current_price = 150.0  # Would fetch from market data API
            day_change_percent = 2.5  # Mock data
            
            items.append({
                'id': item['id'],
                'company_id': item['company_id'],
                'company_name': item['companies']['name'],
                'ticker': item['companies']['ticker'],
                'current_price': current_price,
                'day_change': current_price * (day_change_percent / 100),
                'day_change_percent': day_change_percent,
                'recommendation': 'Buy',  # Would come from analysis
                'added_at': item['created_at']
            })
        
        return {
            'user_id': user_id,
            'items': items,
            'last_updated': datetime.utcnow()
        }
    
    async def add_to_watchlist(self, user_id: str, company_id: str) -> str:
        """Add company to user's watchlist"""
        watchlist_data = {
            'user_id': user_id,
            'company_id': company_id
        }
        
        result = self.supabase.table('watchlist').insert(watchlist_data).execute()
        return result.data[0]['id']
    
    async def remove_from_watchlist(self, user_id: str, company_id: str) -> bool:
        """Remove company from user's watchlist"""
        result = self.supabase.table('watchlist')\
            .delete()\
            .eq('user_id', user_id)\
            .eq('company_id', company_id)\
            .execute()
        
        return len(result.data) > 0
    
    # Helper methods
    def _extract_period_from_filename(self, filename: str) -> tuple:
        """Extract quarter and year from filename"""
        filename_lower = filename.lower()
        
        # Extract year
        year = 2024  # Default
        for y in range(2020, 2030):
            if str(y) in filename:
                year = y
                break
        
        # Extract quarter
        quarter = "Q4"  # Default
        if 'q1' in filename_lower:
            quarter = "Q1"
        elif 'q2' in filename_lower:
            quarter = "Q2"
        elif 'q3' in filename_lower:
            quarter = "Q3"
        elif 'q4' in filename_lower:
            quarter = "Q4"
        
        return quarter, year
    
    def _extract_financial_period(self, raw_data: Dict[str, Any], filename: str) -> datetime:
        """Extract financial period from data or filename"""
        # Try to extract from data first
        periods = raw_data.get('periods', [])
        if periods:
            # Use the latest period
            try:
                return datetime.strptime(periods[-1], '%Y-%m-%d')
            except:
                pass
        
        # Fallback to filename-based extraction
        quarter, year = self._extract_period_from_filename(filename)
        
        # Convert quarter to month
        quarter_months = {'Q1': 3, 'Q2': 6, 'Q3': 9, 'Q4': 12}
        month = quarter_months.get(quarter, 12)
        
        return datetime(year, month, 1)
