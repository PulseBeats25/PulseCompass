"""
Automatic Ticker Symbol Fetcher
Scrapes Screener.in to find correct NSE ticker symbols for company names,
OR reads them directly from an Excel file if provided.
"""
import requests
from bs4 import BeautifulSoup
import json
import time
import re
from typing import Dict, Optional, Tuple, List
import argparse
import os
import pandas as pd

class TickerSymbolFetcher:
    """Fetch NSE ticker symbols from Screener.in"""
    
    def __init__(self):
        self.base_url = "https://www.screener.in"
        self.search_url = f"{self.base_url}/api/company/search/"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def _expand_abbreviations(self, s: str) -> str:
        """Expand common finance abbreviations to improve hits"""
        repls = {
            ' fin serv ': ' finance services ',
            ' fin. serv. ': ' finance services ',
            ' fin ': ' finance ',
            ' inv ': ' investment ',
            ' inv. ': ' investment ',
            ' serv ': ' services ',
            ' serv. ': ' services ',
            ' ind ': ' industries ',
            ' ind. ': ' industries ',
            ' m  m ': ' mahindra  mahindra ',
            ' m & m ': ' mahindra & mahindra ',
            'cholaman': 'cholamandalam',
            'cholamandlam': 'cholamandalam'
        }
        x = f" {s.lower()} "
        for k, v in repls.items():
            x = x.replace(k, v)
        return ' '.join(x.split())

    def _query_variants(self, company_name: str) -> List[str]:
        base = company_name.strip()
        variants = [base]

        # Normalizations
        v = base.replace('&', ' and ')
        v = v.replace('.', ' ')
        v = re.sub(r'[^\w\s&]', ' ', v)
        v = ' '.join(v.split())
        variants.append(v)

        # Abbreviation expansion
        variants.append(self._expand_abbreviations(v))

        # Shorten multiple spaces
        variants = list(dict.fromkeys([x for x in variants if x]))
        return variants

    def _extract_code_from_page(self, url_path: str) -> Optional[str]:
        try:
            page = requests.get(self.base_url + url_path, headers=self.headers, timeout=10)
            if page.status_code != 200:
                return None
            html = page.text
            m = re.search(r'NSE\s*:\s*([A-Z0-9&\.\-]+)', html)
            if m:
                return m.group(1)
        except Exception:
            return None
        return None

    def search_company(self, company_name: str) -> Optional[str]:
        """
        Search for company and return NSE ticker symbol
        
        Args:
            company_name: Company name to search
            
        Returns:
            NSE ticker symbol or None
        """
        try:
            manual = {
                'cholaman.inv.&fn': 'CHOLAFIN',
                'cholamandalam investment & finance': 'CHOLAFIN',
                'm & m fin. serv.': 'M&MFIN',
                'm m fin serv': 'M&MFIN',
                'mahindra & mahindra financial services': 'M&MFIN'
            }
            key = company_name.strip().lower()
            if key in manual:
                return manual[key]

            # Try multiple query variants
            for q in self._query_variants(company_name):
                params = {'q': q}
                response = requests.get(
                    self.search_url,
                    params=params,
                    headers=self.headers,
                    timeout=10
                )
                if response.status_code != 200:
                    continue
                data = response.json()
                if not data:
                    continue
                first = data[0]
                # Prefer nse_code if available
                code = first.get('nse_code') or first.get('nseSymbol')
                if code:
                    print(f"  ✅ {company_name} → {code}")
                    return code
                # Else try URL
                url = first.get('url') or ''
                m = re.search(r'/company/([A-Z0-9&\.\-]+)/', url)
                if m:
                    code = m.group(1)
                    print(f"  ✅ {company_name} → {code}")
                    return code
                # As last resort, open page and parse NSE code
                if url:
                    code = self._extract_code_from_page(url)
                    if code:
                        print(f"  ✅ {company_name} → {code}")
                        return code
            
            print(f"  ⚠️ {company_name}: No ticker found")
            return None
            
        except Exception as e:
            print(f"  ❌ {company_name}: Error - {str(e)}")
            return None
    
    def _clean_company_name(self, name: str) -> str:
        """Clean company name for better search results"""
        # Remove common suffixes
        name = re.sub(r'\s+(Ltd\.?|Limited|Pvt\.?|Private|Inc\.?|Corp\.?|Co\.?|Company\s+Ltd\.?)+$', '', name, flags=re.IGNORECASE)
        # Normalize
        name = name.replace('&', ' and ')
        name = name.replace('.', ' ')
        name = re.sub(r'[^\w\s&]', ' ', name)
        name = ' '.join(name.split())
        
        return name
    
    def fetch_all_tickers(self, company_names: list) -> Dict[str, str]:
        """
        Fetch tickers for multiple companies
        
        Args:
            company_names: List of company names
            
        Returns:
            Dict mapping company names to ticker symbols
        """
        print(f"\n🔍 Fetching ticker symbols for {len(company_names)} companies...")
        print("=" * 80)
        
        mapping = {}
        
        for i, company_name in enumerate(company_names, 1):
            print(f"\n[{i}/{len(company_names)}] Searching: {company_name}")
            
            ticker = self.search_company(company_name)
            
            if ticker:
                mapping[company_name] = ticker
            
            # Rate limiting - be nice to the server
            time.sleep(1)
        
        print("\n" + "=" * 80)
        print(f"✅ Successfully found {len(mapping)}/{len(company_names)} ticker symbols")
        
        return mapping
    
    def save_mapping(self, mapping: Dict[str, str], filepath: str):
        """Save mapping to JSON file"""
        with open(filepath, 'w') as f:
            json.dump(mapping, f, indent=2)
        print(f"\n💾 Saved mapping to: {filepath}")


def load_companies_from_snapshot():
    """Load company names from the latest snapshot"""
    
    snapshot_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        'data',
        'performance_tracking',
        'ranking_snapshots.json'
    )
    
    try:
        with open(snapshot_path, 'r') as f:
            snapshots = json.load(f)
        
        if snapshots and len(snapshots) > 0:
            # Get latest snapshot
            latest = snapshots[0]
            companies = [r['company'] for r in latest['rankings']]
            print(f"📊 Loaded {len(companies)} companies from snapshot")
            return companies
    except Exception as e:
        print(f"⚠️ Could not load from snapshot: {e}")
    
    # Fallback to manual list
    return [
        "Abans Financial",
        "Balmer Law. Inv.",
        "Authum Invest",
        "Prime Securities",
        "Jindal Poly Inve",
        "Wealth First Por",
        "Bajaj Holdings",
        "PTC India Fin",
        "Rane Holdings",
        "CRISIL",
        "Kama Holdings",
        "Indl.& Prud.Inv.",
        "Summit Securitie",
        "Tsf Investments",
        "Elcid Investment",
        "Bengal & Assam",
        "Pilani Invest.",
        "Saraswati Commer",
        "Nalwa Sons Invst",
        "Edelweiss.Fin.",
        "JM Financial"
    ]


def load_from_excel(excel_path: str) -> Tuple[List[str], Dict[str, str]]:
    """
    Load company names and optional NSE codes from an Excel file.
    Returns (companies, direct_mapping). If a ticker column exists, direct_mapping
    will contain company->ticker entries; otherwise it will be empty and
    companies will be used with scraping.
    """
    print(f"📄 Reading Excel: {excel_path}")
    df = pd.read_excel(excel_path)

    # Normalize columns
    cols = {c.strip().lower(): c for c in df.columns if isinstance(c, str)}

    name_cols = [
        c for key, c in cols.items()
        if key in [
            'name', 'company', 'company name', 'nse name', 'security name',
            'namense code', 'namense', 'namense', 'namensecode'
        ] or 'name' in key
    ]

    ticker_cols = [
        c for key, c in cols.items()
        if key in ['nse code', 'ticker', 'symbol', 'nse', 'nsecode', 'code']
        or 'ticker' in key or 'symbol' in key
    ]

    companies: List[str] = []
    direct_mapping: Dict[str, str] = {}

    # Heuristic: if both name and ticker columns exist, map directly
    if name_cols and ticker_cols:
        name_col = name_cols[0]
        tick_col = ticker_cols[0]
        sub = df[[name_col, tick_col]].dropna()
        for _, row in sub.iterrows():
            name = str(row[name_col]).strip()
            tick = str(row[tick_col]).strip()
            if name and tick and tick.lower() != 'nan':
                direct_mapping[name] = tick
        companies = list(direct_mapping.keys())
        print(f"📊 Loaded {len(companies)} companies with tickers from Excel")
        return companies, direct_mapping

    # Else, try to get a single column of company names
    candidate_cols = ticker_cols or name_cols or list(df.columns)
    series = df[candidate_cols[0]].dropna()
    for v in series:
        s = str(v).strip()
        if s and s.lower() != 'nan':
            companies.append(s)
    companies = list(dict.fromkeys(companies))  # de-duplicate preserve order
    print(f"📊 Loaded {len(companies)} companies from Excel (no ticker column found)")
    return companies, {}


def main():
    """Main function to fetch and save ticker symbols"""
    parser = argparse.ArgumentParser(description="Fetch NSE tickers for companies")
    parser.add_argument("--excel", type=str, default=None, help="Path to Excel/CSV with companies (and optional NSE codes)")
    args = parser.parse_args()

    # Prefer Excel input if provided
    companies: List[str]
    direct_mapping: Dict[str, str] = {}

    if args.excel:
        if not os.path.exists(args.excel):
            raise FileNotFoundError(f"Excel file not found: {args.excel}")
        companies, direct_mapping = load_from_excel(args.excel)
    else:
        # Load companies from snapshot as fallback
        companies = load_companies_from_snapshot()
    
    # Initialize fetcher
    fetcher = TickerSymbolFetcher()
    
    # If Excel provided tickers directly, use them; otherwise scrape
    if direct_mapping:
        mapping = direct_mapping
    else:
        mapping = fetcher.fetch_all_tickers(companies)
    
    # Save to file
    output_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        'data',
        'symbol_mapping.json'
    )
    
    fetcher.save_mapping(mapping, output_path)
    
    # Print summary
    print("\n" + "=" * 80)
    print("📊 TICKER MAPPING SUMMARY")
    print("=" * 80)
    
    for company, ticker in sorted(mapping.items()):
        print(f"  {company:<30} → {ticker}")
    
    print("\n✅ Done! You can now run the backtest.")
    print("\nNext step:")
    print("  python scripts/run_backtest.py --auto-validate-all")


if __name__ == "__main__":
    main()
