"""
Market Data Fetcher
Fetches actual stock returns from Yahoo Finance for validation
"""
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import time
import json
import os


class MarketDataFetcher:
    """
    Fetches historical stock prices and calculates returns
    """
    
    def __init__(self):
        self.nse_suffix = ".NS"  # NSE stocks
        self.bse_suffix = ".BO"  # BSE stocks (fallback)
        self.symbol_mapping = self._load_symbol_mapping()
        self._normalized_map = self._build_normalized_map(self.symbol_mapping)
    
    def _load_symbol_mapping(self) -> Dict[str, str]:
        """Load symbol mapping from JSON file"""
        try:
            mapping_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                'data', 'symbol_mapping.json'
            )
            if os.path.exists(mapping_path):
                with open(mapping_path, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"⚠️ Could not load symbol mapping: {e}")
        return {}

    def _normalize_key(self, s: str) -> str:
        s = (s or "").strip()
        # Unescape common encodings and unify connectors
        s = s.replace("\\u0026", "&")
        s = s.replace(" and ", " & ")
        # Remove common punctuation and collapse spaces
        for ch in ['.', ',', '(', ')', '-', '_']:
            s = s.replace(ch, ' ')
        s = ' '.join(s.split())
        # Lowercase and remove spaces for normalized compare
        return s.lower().replace(' ', '')

    def _build_normalized_map(self, mapping: Dict[str, str]) -> Dict[str, str]:
        nm = {}
        for k, v in (mapping or {}).items():
            nk = self._normalize_key(k)
            if nk and nk not in nm:
                nm[nk] = v
            # Add variant replacing '&' with 'and' and vice versa
            if '&' in k:
                alt = self._normalize_key(k.replace('&', ' and '))
                if alt and alt not in nm:
                    nm[alt] = v
        return nm
    
    def _resolve_symbol(self, symbol: str) -> str:
        """Resolve company name to ticker symbol"""
        # Check if it's already a ticker (contains .NS or .BO)
        if '.NS' in symbol or '.BO' in symbol:
            return symbol.replace('.NS', '').replace('.BO', '')
        
        s_clean = (symbol or "").strip()
        # Try exact match in mapping
        if s_clean in self.symbol_mapping:
            return self.symbol_mapping[s_clean]
        
        # Try case-insensitive match
        sl = s_clean.lower()
        for key, value in self.symbol_mapping.items():
            if key.lower() == sl:
                return value
        
        # Try normalized lookup (handles punctuation, spaces, '&' vs 'and')
        nk = self._normalize_key(s_clean)
        mapped = self._normalized_map.get(nk)
        if mapped:
            return mapped
        # Try alternate '&' vs 'and'
        if '&' in s_clean:
            alt = self._normalize_key(s_clean.replace('&', ' and '))
            mapped = self._normalized_map.get(alt)
            if mapped:
                return mapped
        elif ' and ' in s_clean.lower():
            alt = self._normalize_key(s_clean.lower().replace(' and ', ' & '))
            mapped = self._normalized_map.get(alt)
            if mapped:
                return mapped
        
        # Return as-is if no mapping found
        return symbol
    
    def get_stock_returns(
        self,
        symbols: List[str],
        start_date: datetime,
        end_date: Optional[datetime] = None,
        period_months: Optional[int] = None
    ) -> Dict[str, float]:
        """
        Get actual returns for a list of stock symbols
        
        Args:
            symbols: List of NSE stock symbols (without .NS suffix)
            start_date: Start date for return calculation
            end_date: End date (default: today)
            period_months: Alternative to end_date - calculate returns over N months
            
        Returns:
            Dict mapping symbols to percentage returns
        """
        if end_date is None:
            if period_months:
                end_date = start_date + timedelta(days=period_months * 30)
            else:
                end_date = datetime.now()
        
        returns_data = {}
        failed_symbols = []
        
        print(f"📊 Fetching returns for {len(symbols)} stocks from {start_date.date()} to {end_date.date()}")
        
        for symbol in symbols:
            try:
                # Resolve symbol to ticker
                ticker_symbol = self._resolve_symbol(symbol)
                returns = self._get_single_stock_return(ticker_symbol, start_date, end_date)
                if returns is not None:
                    returns_data[symbol] = returns
                    print(f"  ✅ {symbol}: {returns:+.2f}%")
                else:
                    failed_symbols.append(symbol)
                    print(f"  ⚠️ {symbol}: No data available")
                
                # Rate limiting - be nice to Yahoo Finance
                time.sleep(0.5)
                
            except Exception as e:
                failed_symbols.append(symbol)
                print(f"  ❌ {symbol}: Error - {str(e)}")
        
        print(f"\n✅ Successfully fetched: {len(returns_data)}/{len(symbols)}")
        if failed_symbols:
            print(f"⚠️ Failed symbols: {', '.join(failed_symbols)}")
        
        return returns_data
    
    def _get_single_stock_return(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime
    ) -> Optional[float]:
        """
        Get return for a single stock
        
        Returns:
            Percentage return or None if data unavailable
        """
        # Try NSE first
        ticker_nse = f"{symbol}{self.nse_suffix}"
        stock = yf.Ticker(ticker_nse)
        
        try:
            # Get historical data
            hist = stock.history(start=start_date, end=end_date)
            
            if hist.empty:
                # Try BSE as fallback
                ticker_bse = f"{symbol}{self.bse_suffix}"
                stock = yf.Ticker(ticker_bse)
                hist = stock.history(start=start_date, end=end_date)
            
            if hist.empty or len(hist) < 2:
                return None
            
            # Calculate return
            start_price = hist['Close'].iloc[0]
            end_price = hist['Close'].iloc[-1]
            
            if start_price == 0:
                return None
            
            returns = ((end_price - start_price) / start_price) * 100
            
            return round(returns, 2)
            
        except Exception as e:
            print(f"    Error fetching {symbol}: {str(e)}")
            return None
    
    def get_benchmark_return(
        self,
        benchmark: str,
        start_date: datetime,
        end_date: Optional[datetime] = None,
        period_months: Optional[int] = None
    ) -> float:
        """
        Get benchmark index return
        
        Args:
            benchmark: Index symbol (e.g., '^NSEI' for Nifty 50)
            start_date: Start date
            end_date: End date (default: today)
            period_months: Alternative to end_date
            
        Returns:
            Percentage return
        """
        if end_date is None:
            if period_months:
                end_date = start_date + timedelta(days=period_months * 30)
            else:
                end_date = datetime.now()
        
        try:
            index = yf.Ticker(benchmark)
            hist = index.history(start=start_date, end=end_date)
            
            if hist.empty or len(hist) < 2:
                print(f"⚠️ No benchmark data for {benchmark}")
                return 0.0
            
            start_price = hist['Close'].iloc[0]
            end_price = hist['Close'].iloc[-1]
            
            returns = ((end_price - start_price) / start_price) * 100
            
            print(f"📈 {benchmark} return: {returns:+.2f}%")
            return round(returns, 2)
            
        except Exception as e:
            print(f"❌ Error fetching benchmark {benchmark}: {str(e)}")
            return 0.0
    
    def validate_snapshot_with_actual_returns(
        self,
        snapshot_id: str,
        period_months: int = 6,
        benchmark: str = '^NSEI'
    ) -> Dict:
        """
        Automatically fetch returns and validate a snapshot
        
        Args:
            snapshot_id: ID of the snapshot to validate
            period_months: Period for return calculation (3, 6, or 12 months)
            benchmark: Benchmark index (default: Nifty 50)
            
        Returns:
            Validation results
        """
        from performance_tracking import tracker
        
        # Load snapshot
        snapshots = tracker._load_snapshots()
        snapshot = None
        
        for s in snapshots:
            if s['snapshot_id'] == snapshot_id:
                snapshot = s
                break
        
        if not snapshot:
            raise ValueError(f"Snapshot {snapshot_id} not found")
        
        # Get snapshot date
        snapshot_date = datetime.fromisoformat(snapshot['timestamp'])
        
        # Extract symbols from rankings
        symbols = [r['symbol'] for r in snapshot['rankings'][:50]]
        
        print(f"\n🔄 Validating snapshot {snapshot_id}")
        print(f"   Date: {snapshot_date.date()}")
        print(f"   Period: {period_months} months")
        print(f"   Companies: {len(symbols)}")
        
        # Fetch actual returns
        returns_data = self.get_stock_returns(
            symbols=symbols,
            start_date=snapshot_date,
            period_months=period_months
        )
        
        # Fetch benchmark return
        benchmark_return = self.get_benchmark_return(
            benchmark=benchmark,
            start_date=snapshot_date,
            period_months=period_months
        )
        
        # Add returns to snapshot
        validation = tracker.add_actual_returns(
            snapshot_id=snapshot_id,
            returns_data=returns_data,
            period_months=period_months
        )
        
        # Add benchmark info
        validation['benchmark'] = benchmark
        validation['benchmark_return'] = benchmark_return
        
        return validation
    
    def get_current_prices(self, symbols: List[str]) -> Dict[str, float]:
        """
        Get current market prices for symbols
        
        Args:
            symbols: List of stock symbols
            
        Returns:
            Dict mapping symbols to current prices
        """
        prices = {}
        
        for symbol in symbols:
            try:
                ticker = f"{symbol}{self.nse_suffix}"
                stock = yf.Ticker(ticker)
                
                # Get current price
                info = stock.info
                current_price = info.get('currentPrice') or info.get('regularMarketPrice')
                
                if current_price:
                    prices[symbol] = round(current_price, 2)
                
                time.sleep(0.3)  # Rate limiting
                
            except Exception as e:
                print(f"⚠️ Could not fetch price for {symbol}: {str(e)}")
        
        return prices
    
    def get_market_cap(self, symbols: List[str]) -> Dict[str, float]:
        """
        Get market capitalization for symbols
        
        Args:
            symbols: List of stock symbols
            
        Returns:
            Dict mapping symbols to market cap in crores
        """
        market_caps = {}
        
        for symbol in symbols:
            try:
                ticker = f"{symbol}{self.nse_suffix}"
                stock = yf.Ticker(ticker)
                
                info = stock.info
                market_cap = info.get('marketCap')
                
                if market_cap:
                    # Convert to crores (1 crore = 10 million)
                    market_cap_cr = market_cap / 10_000_000
                    market_caps[symbol] = round(market_cap_cr, 2)
                
                time.sleep(0.3)
                
            except Exception as e:
                print(f"⚠️ Could not fetch market cap for {symbol}: {str(e)}")
        
        return market_caps
    
    def get_fundamental_data(self, symbol: str) -> Dict:
        """
        Get fundamental data for a symbol
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Dict with fundamental metrics
        """
        try:
            ticker = f"{symbol}{self.nse_suffix}"
            stock = yf.Ticker(ticker)
            info = stock.info
            
            fundamentals = {
                'symbol': symbol,
                'current_price': info.get('currentPrice'),
                'market_cap': info.get('marketCap'),
                'pe_ratio': info.get('trailingPE'),
                'forward_pe': info.get('forwardPE'),
                'peg_ratio': info.get('pegRatio'),
                'dividend_yield': info.get('dividendYield', 0) * 100 if info.get('dividendYield') else 0,
                'beta': info.get('beta'),
                'profit_margin': info.get('profitMargins', 0) * 100 if info.get('profitMargins') else None,
                'roe': info.get('returnOnEquity', 0) * 100 if info.get('returnOnEquity') else None,
                'debt_to_equity': info.get('debtToEquity'),
                '52_week_high': info.get('fiftyTwoWeekHigh'),
                '52_week_low': info.get('fiftyTwoWeekLow'),
                'volume': info.get('volume'),
                'avg_volume': info.get('averageVolume')
            }
            
            return fundamentals
            
        except Exception as e:
            print(f"❌ Error fetching fundamentals for {symbol}: {str(e)}")
            return {}


# Singleton instance
fetcher = MarketDataFetcher()


# Convenience functions
def fetch_returns_for_snapshot(snapshot_id: str, months: int = 6) -> Dict:
    """Fetch and validate returns for a snapshot"""
    return fetcher.validate_snapshot_with_actual_returns(snapshot_id, months)


def get_nifty_return(start_date: datetime, months: int) -> float:
    """Get Nifty 50 return"""
    return fetcher.get_benchmark_return('^NSEI', start_date, period_months=months)


def get_stock_prices(symbols: List[str]) -> Dict[str, float]:
    """Get current prices"""
    return fetcher.get_current_prices(symbols)


# Benchmark indices for India
INDIAN_BENCHMARKS = {
    'nifty50': '^NSEI',
    'nifty_next50': '^NSMIDCP',
    'nifty_midcap100': '^NSEMDCP100',
    'nifty_smallcap100': '^NSEMDCP50',
    'nifty_it': '^CNXIT',
    'nifty_bank': '^NSEBANK',
    'nifty_pharma': '^CNXPHARMA',
    'nifty_auto': '^CNXAUTO',
    'nifty_fmcg': '^CNXFMCG',
    'sensex': '^BSESN'
}


def get_sector_benchmark_return(
    sector: str,
    start_date: datetime,
    period_months: int
) -> float:
    """
    Get sector-specific benchmark return
    
    Args:
        sector: Sector name (IT, Banking, Pharma, etc.)
        start_date: Start date
        period_months: Period in months
        
    Returns:
        Sector benchmark return
    """
    sector_map = {
        'IT': 'nifty_it',
        'Banking': 'nifty_bank',
        'Pharma': 'nifty_pharma',
        'Auto': 'nifty_auto',
        'FMCG': 'nifty_fmcg'
    }
    
    benchmark_key = sector_map.get(sector, 'nifty50')
    benchmark_symbol = INDIAN_BENCHMARKS[benchmark_key]
    
    return fetcher.get_benchmark_return(
        benchmark=benchmark_symbol,
        start_date=start_date,
        period_months=period_months
    )
