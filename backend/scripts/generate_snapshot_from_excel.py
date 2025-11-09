"""
Generate a new ranking snapshot from an Excel/CSV file and append it to
backend/data/performance_tracking/ranking_snapshots.json

Minimal snapshot compatible with backtest:
- snapshot_id
- timestamp
- philosophy
- rankings: list of {rank, company, symbol}

Usage:
  python scripts/generate_snapshot_from_excel.py --excel "Z:\\screener.in data\\FINANCE SCRRNER.xlsx" \
      --philosophy buffett --backdate-months 6
"""
import argparse
import json
import os
from datetime import datetime, timedelta
from typing import List, Tuple
import pandas as pd

SNAPSHOTS_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    'data', 'performance_tracking', 'ranking_snapshots.json'
)


def load_names_and_symbols(excel_path: str) -> Tuple[List[str], List[str]]:
    df = pd.read_excel(excel_path)
    # Normalize columns
    cols = {c.strip().lower(): c for c in df.columns if isinstance(c, str)}

    # Candidate columns for company name and ticker
    name_candidates = [
        'name', 'company', 'company name', 'security name', 'namense', 'namense code'
    ]
    ticker_candidates = [
        'nse code', 'nse', 'ticker', 'symbol', 'code', 'nsecode'
    ]

    def pick(col_list):
        for key in col_list:
            if key in cols:
                return cols[key]
        # fuzzy contains
        for k, v in cols.items():
            for key in col_list:
                if key in k:
                    return v
        return None

    name_col = pick(name_candidates) or (df.columns[0] if len(df.columns) else None)
    tick_col = pick(ticker_candidates)

    if name_col is None:
        raise ValueError("Could not find a company name column in the Excel file")

    names = []
    symbols = []

    for _, row in df.iterrows():
        name = str(row.get(name_col, '')).strip()
        if not name or name.lower() == 'nan':
            continue
        names.append(name)
        if tick_col:
            sym = str(row.get(tick_col, '')).strip()
            symbols.append(sym if sym and sym.lower() != 'nan' else name)
        else:
            # Use company name as symbol; market_data_fetcher will map via symbol_mapping
            symbols.append(name)

    # De-duplicate while preserving order
    seen = set()
    names_out, symbols_out = [], []
    for n, s in zip(names, symbols):
        if n not in seen:
            seen.add(n)
            names_out.append(n)
            symbols_out.append(s)

    return names_out, symbols_out


def ensure_snapshots_file():
    os.makedirs(os.path.dirname(SNAPSHOTS_PATH), exist_ok=True)
    if not os.path.exists(SNAPSHOTS_PATH):
        with open(SNAPSHOTS_PATH, 'w') as f:
            json.dump([], f)


def append_snapshot(philosophy: str, companies: List[str], symbols: List[str], backdate_months: int = 0):
    ensure_snapshots_file()

    with open(SNAPSHOTS_PATH, 'r') as f:
        try:
            snapshots = json.load(f)
            if not isinstance(snapshots, list):
                snapshots = []
        except Exception:
            snapshots = []

    # Compute timestamp
    ts = datetime.now()
    if backdate_months and backdate_months > 0:
        ts = ts - timedelta(days=30 * backdate_months)

    snapshot_id = ts.strftime('%Y%m%d_%H%M%S')

    rankings = []
    for i, (c, s) in enumerate(zip(companies, symbols), start=1):
        rankings.append({
            'rank': i,
            'company': c,
            'symbol': s
        })

    snapshot = {
        'snapshot_id': snapshot_id,
        'timestamp': ts.isoformat(),
        'philosophy': philosophy,
        'rankings': rankings
    }

    # Prepend so it's the latest
    snapshots.insert(0, snapshot)

    with open(SNAPSHOTS_PATH, 'w') as f:
        json.dump(snapshots, f, indent=2)

    print("✅ Snapshot created:")
    print(f"  ID:        {snapshot_id}")
    print(f"  Timestamp: {snapshot['timestamp']}")
    print(f"  Philosophy:{philosophy}")
    print(f"  Companies: {len(rankings)}")


def main():
    parser = argparse.ArgumentParser(description='Generate a ranking snapshot from Excel')
    parser.add_argument('--excel', required=True, help='Path to the Excel/CSV file')
    parser.add_argument('--philosophy', default='buffett', help='Philosophy label to store')
    parser.add_argument('--backdate-months', type=int, default=6, help='Backdate months for immediate 6-month backtest')
    args = parser.parse_args()

    companies, symbols = load_names_and_symbols(args.excel)
    append_snapshot(args.philosophy, companies, symbols, args.backdate_months)

    print('\nNext step:')
    print('  python scripts/run_backtest.py --auto-validate-all')


if __name__ == '__main__':
    main()
