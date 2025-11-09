"""
Financial Ranking Router
Handles company ranking based on financial metrics
"""
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
import pandas as pd
import io
from typing import Dict
import sys
from pathlib import Path
import json

# Add utils to path
sys.path.append(str(Path(__file__).parent.parent / "utils"))

try:
    from sector_adjustments import get_sector_from_name, adjust_score_for_sector, SECTOR_BENCHMARKS
    from performance_tracking import save_current_rankings
    from investment_tiers import classify_all_companies, get_tier_summary, get_portfolio_recommendation
    SECTOR_ENABLED = True
    TIERS_ENABLED = True
except ImportError as e:
    print(f"⚠️ Advanced features not available: {e}")
    SECTOR_ENABLED = False
    TIERS_ENABLED = False

router = APIRouter(prefix="/ranking", tags=["ranking"])

# Investment philosophy weights - Refined with emphasis on valuation and cash flow quality
PHILOSOPHIES = {
    'buffett': {
        'name': 'Warren Buffett',
        'weights': {
            'fcf': 0.28,  # 🔴 CRITICAL: Increased from 18% to 28% - Cash is king
            'roe': 0.20,  # 🔴 Increased from 16% to 20% - ROE is timeless quality
            'roce': 0.16,  # Increased from 14% to 16%
            'pe_ratio': 0.08,  # 🔴 Reduced from 14% to 8% - Stop P/E worship
            'debt_equity': 0.14, 'opm': 0.10,
            'profit_growth_3yr': 0.03, 'sales_growth_5yr': 0.01  # Reduced growth weights
        },
        'description': 'Focus on quality companies with strong ROE, low debt, excellent cash flow, and reasonable valuations'
    },
    'lynch': {
        'name': 'Peter Lynch',
        'weights': {
            'peg': 0.25,  # Heavily weight PEG for growth at reasonable price
            'profit_growth_3yr': 0.18, 'eps_growth_3yr': 0.15,
            'roe': 0.12, 'fcf': 0.12,  # Added FCF emphasis
            'roce': 0.08, 'debt_equity': 0.08, 'pe_ratio': 0.02
        },
        'description': 'Growth at reasonable price (PEG < 1) with strong earnings momentum and cash generation'
    },
    'growth': {
        'name': 'Growth Investing',
        'weights': {
            'profit_growth_5yr': 0.22, 'sales_growth_5yr': 0.18, 
            'eps_growth_3yr': 0.15, 'roce': 0.15,
            'fcf': 0.12,  # Added FCF requirement for sustainable growth
            'roe': 0.10, 'opm': 0.08
        },
        'description': 'High growth companies with strong revenue expansion and sustainable cash generation'
    },
    'value': {
        'name': 'Value Investing',
        'weights': {
            'pe_ratio': 0.28,  # Highest weight on valuation
            'debt_equity': 0.20, 'fcf': 0.18,  # Strong FCF requirement
            'roe': 0.14, 'roce': 0.12,
            'dividend_yield': 0.05, 'profit_growth_3yr': 0.03
        },
        'description': 'Undervalued companies (low P/E) with strong fundamentals, low debt, and positive cash flow'
    },
    'dividend': {
        'name': 'Dividend Focus',
        'weights': {
            'dividend_yield': 0.28, 'fcf': 0.25,  # FCF critical for dividend sustainability
            'roe': 0.15, 'debt_equity': 0.15,
            'roce': 0.10, 'opm': 0.07
        },
        'description': 'High dividend yield backed by strong cash generation and low debt'
    },
    'quality': {
        'name': 'Quality at Fair Price',
        'weights': {
            'fcf': 0.30,  # 🔴 CRITICAL: Highest weight on cash generation
            'roe': 0.18, 'roce': 0.15,
            'pe_ratio': 0.15,  # Valuation discipline
            'debt_equity': 0.12, 'opm': 0.08,
            'profit_growth_3yr': 0.02  # Minimal growth weight
        },
        'description': 'High-quality businesses (strong FCF, ROE, ROCE) at reasonable valuations with low debt'
    }
}


# Load Banking/NBFC mapping: any entry in this file is treated as financials
FINANCIALS_SYMBOLS: set[str] = set()
FINANCIALS_NAMES: set[str] = set()
try:
    _mapping_path = Path(__file__).parent.parent / "data" / "nbfc_bank.json"
    with open(_mapping_path, "r", encoding="utf-8") as _f:
        _mapping = json.load(_f)
        if isinstance(_mapping, dict):
            FINANCIALS_NAMES = {str(k).strip().lower() for k in _mapping.keys()}
            FINANCIALS_SYMBOLS = {str(v).strip().lower() for v in _mapping.values()}
except Exception:
    # If mapping is not available, fall back to heuristics only
    FINANCIALS_SYMBOLS = set()
    FINANCIALS_NAMES = set()


def is_financials(row: pd.Series) -> bool:
    """Detect if a company is in the financials sector (Banking/NBFC/Insurance/HFC).
    Uses sector utils if available; otherwise falls back to name-based heuristics.
    """
    # Mapping-based detection from symbol_mapping.json
    sym = str(row.get('symbol', '')).strip().lower()
    if sym and sym in FINANCIALS_SYMBOLS:
        return True
    nm = str(row.get('name', '')).strip().lower()
    if nm and nm in FINANCIALS_NAMES:
        return True

    # Prefer sector utils when available
    try:
        if SECTOR_ENABLED and 'name' in row and isinstance(row['name'], str):
            sector = get_sector_from_name(row['name'])
            if isinstance(sector, str) and sector:
                sector_low = sector.lower()
                if any(k in sector_low for k in ['bank', 'nbfc', 'finance', 'financial', 'insurance', 'hfc', 'housing finance', 'brokerage']):
                    return True
    except Exception:
        pass

    # Heuristic by company name
    name_val = str(row.get('name', '')).lower()
    return any(
        kw in name_val
        for kw in [
            ' bank', 'bank ', 'nbfc', 'finance', 'finserv', 'fin. ', 'fintech', 'lending', 'microfinance', 'nbfcs', 'housing finance', 'hfc', 'insurance', 'mfi'
        ]
    )


def normalize_score(value: float, min_val: float, max_val: float, inverse: bool = False) -> float:
    """Normalize a value to 0-100 scale"""
    if pd.isna(value) or max_val == min_val:
        return 50.0
    
    if inverse:
        # For metrics where lower is better (like debt/equity)
        normalized = 100 - ((value - min_val) / (max_val - min_val) * 100)
    else:
        normalized = ((value - min_val) / (max_val - min_val) * 100)
    
    return max(0, min(100, normalized))


def assess_quality_score(row: pd.Series) -> float:
    """
    Assess overall quality of the company
    Returns multiplier between 0.5 and 1.0
    
    🔴 CRITICAL: Added ROE multiplier based on deep analysis feedback
    """
    quality_score = 1.0
    red_flags = 0
    yellow_flags = 0
    
    # Red flags (serious concerns)
    if 'roe' in row and row['roe'] < 5:
        red_flags += 1
    
    if 'debt_equity' in row and row['debt_equity'] > 2:
        red_flags += 1
    
    if 'fcf' in row and row['fcf'] < -100:
        red_flags += 1
    
    # Yellow flags (moderate concerns)
    if 'roe' in row and 5 <= row['roe'] < 12:
        yellow_flags += 1
    
    if 'peg' in row and row['peg'] > 2:
        yellow_flags += 1
    
    if 'debt_equity' in row and 1.0 < row['debt_equity'] <= 1.5:
        yellow_flags += 1
    
    # Calculate quality multiplier
    quality_score -= (red_flags * 0.15)  # -15% per red flag
    quality_score -= (yellow_flags * 0.05)  # -5% per yellow flag
    
    # 🔴 CRITICAL FIX: Add ROE multiplier (Issue #1 & #2 from analysis)
    # Formula: Adjusted_Score = Base_Score × (1 + max(0, (ROE - 10) / 40))
    if 'roe' in row and row['roe'] > 10:
        roe_bonus = (row['roe'] - 10) / 40
        quality_score *= (1 + min(roe_bonus, 0.6))  # Cap bonus at +60%
    
    return max(0.5, min(1.5, quality_score))  # Allow up to 1.5x for exceptional ROE


def calculate_risk_penalties(row: pd.Series, fcf_dq_mode: str = 'financials_only_off') -> Dict[str, float]:
    """
    Calculate specific risk penalties for transparency
    Returns dict of penalty reasons and amounts
    """
    penalties = {}
    
    is_fin = is_financials(row)

    # 🔴 CRITICAL: Negative Free Cash Flow Penalty (increased from -30% to -40%)
    # Finance/NBFCs often show negative accounting FCF; soften/skip for them
    if 'fcf' in row and row['fcf'] < 0:
        if not is_fin:
            penalties['negative_fcf'] = 0.40  # -40%
        else:
            penalties['negative_fcf'] = 0.10  # Softer for financials
    
    # Extreme P/E Penalty
    if 'pe_ratio' in row:
        if row['pe_ratio'] > 100:
            penalties['extreme_pe'] = 0.25  # -25%
        elif row['pe_ratio'] > 50:
            penalties['high_pe'] = 0.15  # -15%
    
    # High Debt Penalty
    if 'debt_equity' in row:
        if not is_fin:
            if row['debt_equity'] > 1.5:
                penalties['high_debt'] = 0.20  # -20%
            elif row['debt_equity'] > 1.0:
                penalties['moderate_debt'] = 0.10  # -10%
        else:
            # Leverage is part of the model for financials; use more lenient thresholds
            if row['debt_equity'] > 5.0:
                penalties['high_debt'] = 0.15
            elif row['debt_equity'] > 3.0:
                penalties['moderate_debt'] = 0.05
    
    # 🔴 CRITICAL: Poor Profitability Penalty (strengthened based on expert feedback)
    if 'roe' in row:
        if row['roe'] < 8:
            penalties['very_low_roe'] = 0.30  # -30% for ROE < 8%
        elif row['roe'] < 10:
            penalties['low_roe'] = 0.20  # -20% for ROE < 10% (increased from -15%)
        elif row['roe'] < 12:
            penalties['moderate_roe'] = 0.10  # -10% for ROE < 12% (NEW)
    
    # 🔴 NEW: ROCE Penalty (Expert Feedback - ranks 8-10 have low ROCE)
    if 'roce' in row:
        if row['roce'] < 12:
            penalties['low_roce'] = 0.10  # -10% for ROCE < 12%
        elif row['roce'] < 15:
            penalties['moderate_roce'] = 0.05  # -5% for ROCE < 15%
    
    # High PEG Penalty (overvalued growth)
    if 'peg' in row and row['peg'] > 2:
        penalties['high_peg'] = 0.10  # -10%
    
    # 🔴 CRITICAL FIX: Low ROE + High FCF Penalty (Issue #2 - PTC India)
    # Don't let massive FCF override poor profitability
    if 'roe' in row and 'fcf' in row and 'profit_growth_3yr' in row:
        if row['roe'] < 8 and row['profit_growth_3yr'] < 0:
            # Exception: Fortress balance sheet (FCF > 1000 Cr AND D/E < 0.3)
            if row['fcf'] > 1000 and row.get('debt_equity', 1.0) < 0.3:
                penalties['low_roe_high_fcf'] = 0.20  # -20% (reduced penalty)
            else:
                penalties['low_roe_negative_growth'] = 0.50  # -50% (severe penalty)
    
    # 🔴 NEW: Low FCF Relative to Market Cap (Manager Feedback)
    # For financials, skip this penalty (FCF less meaningful)
    if 'fcf' in row and 'market_cap' in row:
        if not is_fin and 0 < row['fcf'] < 100 and row['market_cap'] > 1000:
            penalties['low_fcf_relative'] = 0.10  # -10%
    
    # 🔴 NEW: Moderate P/E Warning (Manager Feedback)
    # Flag moderately high P/E without disqualifying
    if 'pe_ratio' in row:
        if 25 < row['pe_ratio'] <= 50:
            penalties['moderate_pe'] = 0.05  # -5%
    
    # 🔴 NEW: Compound Penalty for Multiple Red Flags (Expert Feedback)
    # Companies with multiple issues should be heavily penalized
    red_flags = []
    
    if row.get('roe', 100) < 10:
        red_flags.append('low_roe')
    
    if row.get('profit_growth_3yr', 100) < 0:
        red_flags.append('negative_growth')
    
    if not is_fin and row.get('fcf', 1000) < 100 and row.get('market_cap', 0) > 1000:
        red_flags.append('low_fcf')
    
    if row.get('debt_equity', 0) > 1.0:
        red_flags.append('high_debt')
    
    # Apply compound penalty if 2+ red flags
    if len(red_flags) >= 2:
        penalties['multiple_red_flags'] = 0.10 * len(red_flags)  # -10% per flag
    
    # Extreme Volatility Penalty
    if 'return_1yr' in row and abs(row['return_1yr']) > 1000:
        penalties['extreme_volatility'] = 0.20  # -20%
    elif 'return_1yr' in row and abs(row['return_1yr']) > 500:
        penalties['high_volatility'] = 0.10  # -10%
    
    return penalties


def should_disqualify(row: pd.Series, fcf_dq_mode: str = 'financials_only_off') -> tuple[bool, str]:
    """
    Check if company should be disqualified from rankings
    Returns (should_disqualify, reason)
    
    🔴 CRITICAL DISQUALIFICATION RULES - Based on feedback
    """
    # Sector-aware disqualifications
    is_fin = is_financials(row)
    apply_fcf_dq_for_fin = (fcf_dq_mode == 'global_on')
    apply_fcf_dq_for_nonfin = (fcf_dq_mode in ('financials_only_off', 'global_on'))

    # Massive negative FCF
    if 'fcf' in row and row['fcf'] < -500:
        if (is_fin and apply_fcf_dq_for_fin) or (not is_fin and apply_fcf_dq_for_nonfin):
            return True, f"Massive cash burn: FCF {row['fcf']:.0f} Cr (unsustainable)"
    
    # 🔴 CRITICAL: P/E > 100 for top 20 rankings (speculative)
    if 'pe_ratio' in row and row['pe_ratio'] > 100:
        return True, f"Extreme P/E ratio: {row['pe_ratio']:.1f} (speculative valuation)"
    
    # Disqualify if P/E is absurdly high (likely data error)
    if 'pe_ratio' in row and row['pe_ratio'] > 500:
        return True, f"Absurd P/E ratio: {row['pe_ratio']:.1f} (likely data error)"
    
    # Negative FCF + High debt
    if 'fcf' in row and 'debt_equity' in row:
        if row['fcf'] < -100 and row['debt_equity'] > 2.0:
            if (is_fin and apply_fcf_dq_for_fin) or (not is_fin and apply_fcf_dq_for_nonfin):
                return True, "Negative FCF with very high debt (bankruptcy risk)"
    
    # Disqualify if ROE is negative (losing money)
    if 'roe' in row and row['roe'] < 0:
        return True, f"Negative ROE: {row['roe']:.1f}% (unprofitable)"
    
    # Minimal FCF with high market cap
    if 'fcf' in row and 'market_cap' in row:
        if 0 < row['fcf'] < 10 and row['market_cap'] > 1000:
            fcf_yield = (row['fcf'] / row['market_cap']) * 100
            if fcf_yield < 0.5:
                if (is_fin and apply_fcf_dq_for_fin) or (not is_fin and apply_fcf_dq_for_nonfin):
                    return True, f"Minimal FCF (₹{row['fcf']:.1f} Cr) for ₹{row['market_cap']:.0f} Cr market cap (speculative)"
    
    # Disqualify if extreme volatility with negative fundamentals
    if 'return_1yr' in row and 'fcf' in row and 'roe' in row:
        if abs(row['return_1yr']) > 2000 and row['fcf'] < 0 and row['roe'] < 15:
            return True, "Extreme volatility with poor fundamentals (speculative)"
    
    return False, ""


def assess_cash_flow_quality(row: pd.Series) -> float:
    """
    Assess cash flow quality and sustainability
    Returns a multiplier (0.7 to 1.2) - can boost or penalize score
    """
    quality = 1.0
    
    # Positive FCF is baseline
    if 'fcf' in row and row['fcf'] > 0:
        quality += 0.05
        
        # Strong FCF relative to profit (FCF/PAT ratio)
        if 'pat' in row and row['pat'] > 0:
            fcf_to_profit = row['fcf'] / row['pat']
            if fcf_to_profit > 0.8:  # Converting >80% of profit to cash
                quality += 0.10
            elif fcf_to_profit > 0.5:
                quality += 0.05
        
        # Consistent FCF over time
        if 'fcf_3yr' in row and 'fcf_5yr' in row:
            if row['fcf_3yr'] > 0 and row['fcf_5yr'] > 0:
                quality += 0.05  # Consistent positive FCF
    else:
        # Negative FCF is already penalized in risk penalties
        quality -= 0.10
    
    # Asset efficiency (Asset Turnover)
    if 'asset_turnover' in row and row['asset_turnover'] > 1.0:
        quality += 0.05
    
    return max(0.7, min(1.2, quality))


def assess_valuation_reasonableness(row: pd.Series) -> Dict[str, any]:
    """
    Assess if valuation is reasonable given fundamentals
    Returns dict with reasonableness score and warnings
    """
    score = 1.0
    warnings = []
    
    # P/E vs Growth check (PEG logic)
    if 'pe_ratio' in row and 'profit_growth_3yr' in row:
        if row['profit_growth_3yr'] > 0:
            implied_peg = row['pe_ratio'] / row['profit_growth_3yr']
            
            if implied_peg < 0.5:
                score += 0.15  # Undervalued growth
            elif implied_peg < 1.0:
                score += 0.10  # Fair value growth
            elif implied_peg > 3.0:
                score -= 0.20
                warnings.append('High valuation vs growth (PEG > 3)')
            elif implied_peg > 2.0:
                score -= 0.10
                warnings.append('Elevated valuation vs growth (PEG > 2)')
    
    # P/E vs ROE check (Quality premium justified?)
    if 'pe_ratio' in row and 'roe' in row:
        if row['roe'] > 25 and row['pe_ratio'] < 30:
            score += 0.10  # High quality at reasonable price
        elif row['roe'] < 15 and row['pe_ratio'] > 25:
            score -= 0.15
            warnings.append('High P/E without strong ROE')
    
    # FCF yield check (FCF / Market Cap)
    if 'fcf' in row and 'market_cap' in row and row['market_cap'] > 0:
        fcf_yield = (row['fcf'] / row['market_cap']) * 100
        if fcf_yield > 8:
            score += 0.10  # Strong FCF yield
        elif fcf_yield > 5:
            score += 0.05
        elif fcf_yield < 0:
            score -= 0.15
            warnings.append('Negative FCF yield')
    
    # Price/Sales reasonableness
    if 'cmp_sales' in row and 'opm' in row:
        # High P/S should be justified by high margins
        if row['cmp_sales'] > 10 and row['opm'] < 15:
            score -= 0.10
            warnings.append('High Price/Sales without strong margins')
    
    return {
        'score': max(0.6, min(1.3, score)),
        'warnings': warnings
    }


def calculate_composite_score(row: pd.Series, weights: Dict[str, float], normalized_df: pd.DataFrame, fcf_dq_mode: str = 'financials_only_off') -> float:
    """Calculate weighted composite score with quality adjustments"""
    score = 0.0
    
    for metric, weight in weights.items():
        if metric in normalized_df.columns:
            score += normalized_df.loc[row.name, metric] * weight
    
    # Apply quality multiplier
    quality_multiplier = assess_quality_score(row)
    score *= quality_multiplier
    
    # Apply cash flow quality assessment
    cf_quality = assess_cash_flow_quality(row)
    score *= cf_quality
    
    # Apply valuation reasonableness assessment
    valuation_assessment = assess_valuation_reasonableness(row)
    score *= valuation_assessment['score']
    
    # Apply specific risk penalties
    penalties = calculate_risk_penalties(row, fcf_dq_mode)
    total_penalty = sum(penalties.values())
    score *= (1 - min(total_penalty, 0.6))  # Cap total penalty at 60%
    
    return round(score, 1)


def get_key_drivers(row: pd.Series, top_n: int = 5) -> list:
    """Identify key performance drivers"""
    drivers = []
    
    # Profitability metrics
    if 'roe' in row and row['roe'] > 20:
        drivers.append(f"ROE {row['roe']:.1f}%")
    
    if 'roce' in row and row['roce'] > 20:
        drivers.append(f"ROCE {row['roce']:.1f}%")
    
    if 'opm' in row and row['opm'] > 15:
        drivers.append(f"OPM {row['opm']:.1f}%")
    
    # Growth metrics
    if 'profit_growth_3yr' in row and row['profit_growth_3yr'] > 20:
        drivers.append(f"Profit Growth {row['profit_growth_3yr']:.0f}%")
    
    if 'sales_growth_5yr' in row and row['sales_growth_5yr'] > 15:
        drivers.append(f"Sales Growth {row['sales_growth_5yr']:.0f}%")
    
    if 'eps_growth_3yr' in row and row['eps_growth_3yr'] > 20:
        drivers.append(f"EPS Growth {row['eps_growth_3yr']:.0f}%")
    
    # Financial health
    if 'debt_equity' in row and row['debt_equity'] < 0.5:
        drivers.append(f"Low D/E {row['debt_equity']:.2f}")
    
    if 'fcf' in row and row['fcf'] > 0:
        drivers.append("Positive FCF")
    
    # Valuation
    if 'pe_ratio' in row and 0 < row['pe_ratio'] < 15:
        drivers.append(f"Attractive P/E {row['pe_ratio']:.1f}")
    
    if 'peg' in row and 0 < row['peg'] < 1:
        drivers.append(f"Low PEG {row['peg']:.2f}")
    
    if 'dividend_yield' in row and row['dividend_yield'] > 2:
        drivers.append(f"Div Yield {row['dividend_yield']:.1f}%")
    
    return drivers[:top_n]


def generate_ranking_reason(row: pd.Series, philosophy: str, rank: int) -> str:
    """Generate explanation for why company is ranked at this position"""
    reasons = []
    phil = PHILOSOPHIES[philosophy]
    
    # Get top weighted metrics for this philosophy
    top_metrics = sorted(phil['weights'].items(), key=lambda x: x[1], reverse=True)[:3]
    
    for metric, weight in top_metrics:
        if metric in row and not pd.isna(row[metric]):
            value = row[metric]
            if metric == 'roe':
                if value > 20:
                    reasons.append(f"Excellent ROE of {value:.1f}%")
                elif value > 15:
                    reasons.append(f"Strong ROE of {value:.1f}%")
            elif metric == 'roce':
                if value > 20:
                    reasons.append(f"High ROCE of {value:.1f}%")
            elif metric == 'debt_equity':
                if value < 0.5:
                    reasons.append(f"Low debt-to-equity ratio of {value:.2f}")
            elif 'growth' in metric:
                if value > 20:
                    reasons.append(f"Strong growth of {value:.0f}%")
            elif metric == 'pe_ratio':
                if 0 < value < 15:
                    reasons.append(f"Attractive P/E ratio of {value:.1f}")
            elif metric == 'peg':
                if 0 < value < 1:
                    reasons.append(f"Excellent PEG ratio of {value:.2f}")
            elif metric == 'dividend_yield':
                if value > 2:
                    reasons.append(f"Good dividend yield of {value:.1f}%")
    
    if reasons:
        return f"Ranked #{rank}: " + ". ".join(reasons) + f". Aligns well with {phil['name']} investment criteria."
    else:
        return f"Ranked #{rank} based on {phil['name']} investment philosophy."


@router.post("/analyze")
async def analyze_rankings(
    file: UploadFile = File(...),
    philosophy: str = Form(default='buffett'),
    fcfDQMode: str = Form(default='financials_only_off')
):
    """
    Analyze and rank companies based on financial metrics
    """
    print(f"🔍 Ranking endpoint called with file: {file.filename}, philosophy: {philosophy}")
    
    if philosophy not in PHILOSOPHIES:
        raise HTTPException(status_code=400, detail=f"Invalid philosophy: {philosophy}")
    # Validate DQ mode
    valid_modes = {"financials_only_off", "global_off", "global_on"}
    if fcfDQMode not in valid_modes:
        raise HTTPException(status_code=400, detail=f"Invalid fcfDQMode: {fcfDQMode}. Must be one of {sorted(valid_modes)}")
    
    # Read the uploaded file
    try:
        content = await file.read()
        print(f"📁 File size: {len(content)} bytes")
        
        if file.filename.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(content))
        elif file.filename.endswith(('.xlsx', '.xls')):
            # First attempt - read with header=0
            buffer = io.BytesIO(content)
            df = pd.read_excel(buffer, header=0)
            print(f"📋 First read columns: {list(df.columns[:5])}")
            
            # Check if first row looks like generic headers (A, B, C, etc.)
            # Only re-read if ALL first columns are single letters A-Z
            first_cols = [str(c).strip().upper() for c in df.columns[:5]]
            if all(len(c) == 1 and c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ' for c in first_cols):
                # Re-read with header=1 (second row as header)
                print("🔄 Detected generic single-letter headers, re-reading with header=1")
                buffer = io.BytesIO(content)  # Create new buffer
                df = pd.read_excel(buffer, header=1)
                print(f"📋 Second read columns: {list(df.columns[:5])}")
        else:
            raise HTTPException(status_code=400, detail="File must be CSV or Excel format")
    
    except Exception as e:
        print(f"❌ Error reading file: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=f"Error reading file: {str(e)}")
    
    # Normalize column names (handle common variations)
    df.columns = [str(c).replace('\u00a0', ' ').replace('\xa0',' ').strip().lower() for c in df.columns]
    print(f"📊 Normalized columns: {list(df.columns[:10])}")
    
    # Map common column name variations (Screener.in format)
    # Process in specific order to avoid conflicts
    column_mapping = {
        'name': ['company', 'company_name', 'name'],
        'cmp': ['cmp rs', 'cmp', 'current_price', 'price'],
        'market_cap': ['mar cap rs.cr', 'market_cap', 'mcap', 'market cap'],
        'pe_ratio': ['p/e', 'pe', 'pe_ratio', 'price_to_earnings'],
        'roe': ['roe %', 'roe', 'return_on_equity', 'return on equity'],
        'roce': ['roce %', 'roce', 'return_on_capital', 'return on capital employed'],
        'sales_growth_3yr': ['sales var 3yrs', 'sales var 3yrs %', 'sales_growth_3yr', 'sales growth 3yrs %'],
        'sales_growth_5yr': ['sales var 5yrs', 'sales var 5yrs %', 'sales_growth_5yr', 'sales growth 5yrs %', 'sales growth (5 yrs cagr)'],
        'sales': ['sales rs.cr', 'sales', 'revenue'],
        'pat': ['pat 12m rs.cr', 'pat', 'profit_after_tax', 'net_profit'],
        'profit_growth_3yr': ['profit var 3yrs', 'profit var 3yrs %', 'profit_growth_3yr', 'pat growth 3yrs %'],
        'profit_growth_5yr': ['profit var 5yrs', 'profit var 5yrs %', 'profit_growth_5yr', 'pat growth 5yrs %'],
        'fcf_3yr': ['free cash flow 3yrs', 'fcf_3yr'],
        'fcf_5yr': ['free cash flow 5yrs', 'fcf_5yr'],
        'fcf': ['free cash flow rs.cr', 'free cash / eq', 'free cash eq', 'fcf', 'free_cash_flow'],
        'peg': ['peg', 'peg_ratio'],
        'return_1yr': ['1yr return', '1yr return %', 'return_1yr'],
        'return_3yr': ['3yrs return', '3yrs return %', 'return_3yr'],
        'return_5yr': ['5yrs return', '5yrs return %', 'return_5yr'],
        'asset_turnover': ['asset turnover', 'asset_turnover'],
        'cmp_sales': ['cmp / sales', 'cmp_sales', 'price_to_sales'],
        'eps': ['eps 12m rs', 'eps', 'earnings_per_share'],
        'eps_growth_3yr': ['eps var 3yrs', 'eps var 3yrs %', 'eps_growth_3yr'],
        'eps_growth_5yr': ['eps var 5yrs', 'eps var 5yrs %', 'eps_growth_5yr'],
        'debt_equity': ['debt / eq', 'debt/eq', 'debt_equity', 'debt_to_equity', 'd/e', 'debt/equity', 'debt eq'],
        'opm': ['opm %', 'opm', 'operating_profit_margin', 'operating margin'],
        'dividend_yield': ['div yld', 'div yld %', 'dividend_yield', 'dividend yield'],
        # New format columns
        'npm': ['npm ann %', 'net profit margin', 'npm %'],
        'interest_coverage': ['int coverage', 'interest coverage', 'interest coverage ratio'],
        'current_ratio': ['current ratio', 'current_ratio'],
        'pb_ratio': ['cmp / bv', 'price to book', 'p/b', 'pb ratio', 'p/bv'],
        'ev_ebitda': ['ev / ebitda', 'ev/ebitda', 'ev to ebitda'],
        'dividend_payout': ['dividend payout %', 'payout ratio', 'dividend payout'],
        'fcf_yield_inverse': ['cmp / fcf', 'price to fcf'],
        'pledged_pct': ['pledged %', 'pledged shares %', 'pledged'],
        'promoter_holding': ['prom. hold. %', 'promoter holding %', 'promoter holding']
    }
    
    # Standardize column names (process name first to avoid conflicts)
    mapped_cols = set()
    print(f"🔄 Starting column mapping...")
    for standard_name, variations in column_mapping.items():
        for col in df.columns:
            if col not in mapped_cols and any(var in col for var in variations):
                print(f"  Mapping '{col}' -> '{standard_name}'")
                df.rename(columns={col: standard_name}, inplace=True)
                mapped_cols.add(col)
                break
    
    # Handle symbol separately - use 'name' as fallback only if no dedicated symbol column exists
    symbol_variations = ['symbol', 'ticker', 'code']
    symbol_found = False
    for col in df.columns:
        if col not in mapped_cols and any(var in col for var in symbol_variations):
            print(f"  Mapping '{col}' -> 'symbol'")
            df.rename(columns={col: 'symbol'}, inplace=True)
            symbol_found = True
            break
    
    # If no symbol column found, use name as symbol
    if not symbol_found:
        if 'name' in df.columns:
            print(f"  Creating 'symbol' from 'name' column")
            df['symbol'] = df['name']
        else:
            print(f"  ⚠️ No 'name' column found to create 'symbol'")
    
    print(f"✅ Mapped columns: {list(df.columns[:15])}")
    
    # Ensure required columns exist
    if 'name' not in df.columns:
        raise HTTPException(
            status_code=400,
            detail=f"Missing required 'Name' column. Found columns: {', '.join(df.columns[:10])}"
        )
    
    try:
        print(f"🔢 Processing numeric columns...")
        
        # Define all numeric columns
        numeric_cols = [
            'cmp', 'market_cap', 'pe_ratio', 'roe', 'roce', 
            'sales_growth_3yr', 'sales_growth_5yr', 'sales', 'pat',
            'profit_growth_3yr', 'profit_growth_5yr', 
            'fcf_3yr', 'fcf_5yr', 'fcf', 'peg',
            'return_1yr', 'return_3yr', 'return_5yr',
            'asset_turnover', 'cmp_sales', 'eps',
            'eps_growth_3yr', 'eps_growth_5yr',
            'debt_equity', 'opm', 'dividend_yield',
            # New metrics
            'npm', 'interest_coverage', 'current_ratio', 'pb_ratio', 'ev_ebitda',
            'dividend_payout', 'fcf_yield_inverse', 'pledged_pct', 'promoter_holding'
        ]
        
        # Convert to numeric and fill missing values
        for col in numeric_cols:
            if col in df.columns:
                print(f"  Converting {col} to numeric...")
                df[col] = pd.to_numeric(df[col], errors='coerce')
                # Use median for most columns, 0 for growth/return metrics that might be negative
                fill_value = df[col].median() if not df[col].isna().all() else 0
                df[col].fillna(fill_value, inplace=True)
        
        print(f"✅ Numeric conversion complete")
    except Exception as e:
        print(f"❌ Error during numeric conversion: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=f"Error processing numeric columns: {str(e)}")
    
    # Create normalized dataframe
    print(f"📈 Creating normalized scores...")
    normalized_df = pd.DataFrame(index=df.index)
    
    # Metrics where lower is better (inverse scoring)
    inverse_metrics = ['debt_equity', 'pe_ratio', 'peg', 'cmp_sales', 'pb_ratio', 'ev_ebitda', 'fcf_yield_inverse', 'pledged_pct']
    
    for col in numeric_cols:
        if col in df.columns and df[col].notna().any():
            inverse = col in inverse_metrics
            normalized_df[col] = df[col].apply(
                lambda x: normalize_score(x, df[col].min(), df[col].max(), inverse)
            )
    
    print(f"✅ Normalization complete. Normalized {len(normalized_df.columns)} metrics")
    
    # Calculate scores
    print(f"🎯 Calculating composite scores...")
    weights = PHILOSOPHIES[philosophy]['weights']
    df['composite_score'] = df.apply(
        lambda row: calculate_composite_score(row, weights, normalized_df, fcfDQMode),
        axis=1
    )
    
    # Calculate philosophy-specific scores
    df['buffett_score'] = df.apply(
        lambda row: calculate_composite_score(row, PHILOSOPHIES['buffett']['weights'], normalized_df, fcfDQMode),
        axis=1
    )
    df['lynch_score'] = df.apply(
        lambda row: calculate_composite_score(row, PHILOSOPHIES['lynch']['weights'], normalized_df, fcfDQMode),
        axis=1
    )
    df['growth_score'] = df.apply(
        lambda row: calculate_composite_score(row, PHILOSOPHIES['growth']['weights'], normalized_df, fcfDQMode),
        axis=1
    )
    
    # Apply disqualification rules
    print(f"🚨 Checking for disqualifications...")
    disqualified_companies = []
    df['disqualified'] = False
    df['disqualification_reason'] = ''
    
    for idx, row in df.iterrows():
        should_dq, reason = should_disqualify(row, fcfDQMode)
        if should_dq:
            df.at[idx, 'disqualified'] = True
            df.at[idx, 'disqualification_reason'] = reason
            disqualified_companies.append((row['name'], reason))
            print(f"  ⚠️ Disqualified: {row['name']} - {reason}")
    
    # Filter out disqualified companies
    original_count = len(df)
    df = df[df['disqualified'] == False].copy()
    print(f"✅ {len(disqualified_companies)} companies disqualified, {len(df)} remaining")
    
    # Add risk warnings and quality assessments
    df['risk_warnings'] = df.apply(lambda row: list(calculate_risk_penalties(row, fcfDQMode).keys()), axis=1)
    df['quality_score'] = df.apply(assess_quality_score, axis=1)
    df['cf_quality_score'] = df.apply(assess_cash_flow_quality, axis=1)
    
    # Add valuation warnings
    valuation_data = df.apply(assess_valuation_reasonableness, axis=1)
    df['valuation_score'] = valuation_data.apply(lambda x: x['score'])
    df['valuation_warnings'] = valuation_data.apply(lambda x: x['warnings'])
    
    # Add sector identification and adjustments
    if SECTOR_ENABLED:
        print(f"🏢 Applying sector-specific adjustments...")
        df['sector'] = df['name'].apply(get_sector_from_name)
        df['sector_adjustment'] = 0.0
        df['sector_insights'] = ''
        
        for idx, row in df.iterrows():
            sector = row['sector']
            penalties = calculate_risk_penalties(row, fcfDQMode)
            
            adjustment_result = adjust_score_for_sector(
                base_score=row['composite_score'],
                company_data=row,
                sector=sector,
                penalties=penalties
            )
            
            df.at[idx, 'composite_score'] = adjustment_result['adjusted_score']
            df.at[idx, 'sector_adjustment'] = adjustment_result['sector_adjustment']
            df.at[idx, 'sector_insights'] = '; '.join(adjustment_result['sector_insights'])
        
        print(f"✅ Sector adjustments applied")
    else:
        df['sector'] = 'General'
        df['sector_adjustment'] = 0.0
        df['sector_insights'] = ''
    
    # 🔴 CRITICAL: Add Investment Tier Classification (Quality over Quantity)
    if TIERS_ENABLED:
        print(f"🎯 Classifying companies into investment tiers...")
        df = classify_all_companies(df)
        tier_stats = get_tier_summary(df)
        portfolio_recommendation = get_portfolio_recommendation(tier_stats)
        print(f"✅ Tier 1 (CORE): {tier_stats.get(1, {}).get('count', 0)} companies")
        print(f"✅ Tier 2 (QUALITY): {tier_stats.get(2, {}).get('count', 0)} companies")
        print(f"⚠️ Tier 3 (SPECIALIZED): {tier_stats.get(3, {}).get('count', 0)} companies")
        print(f"❌ Tier 4 (AVOID): {tier_stats.get(4, {}).get('count', 0)} companies")
    else:
        df['investment_tier'] = 3
        df['investment_tier_name'] = 'Not Classified'
        df['investment_tier_action'] = 'Research Required'
        df['tier_insights'] = ''
        tier_stats = {}
        portfolio_recommendation = ''
    
    # V2 Sub-scores
    def _avg_present(vals: list[float]) -> float:
        vv = [v for v in vals if v is not None]
        return float(sum(vv) / len(vv)) if vv else 50.0
    def _nz(col: str, idx) -> float | None:
        return float(normalized_df.at[idx, col]) if col in normalized_df.columns else None
    quality_scores = []
    growth_scores = []
    valuation_scores = []
    cashflow_scores = []
    is_fin_flags = []
    for idx, row in df.iterrows():
        is_fin = is_financials(row)
        is_fin_flags.append(is_fin)
        if is_fin:
            q = _avg_present([_nz('roe', idx), _nz('roce', idx)])
        else:
            q = _avg_present([_nz('roe', idx), _nz('roce', idx), _nz('opm', idx)])
        g = _avg_present([
            _nz('sales_growth_5yr', idx) or _nz('sales_growth_3yr', idx),
            _nz('profit_growth_5yr', idx) or _nz('profit_growth_3yr', idx),
            _nz('eps_growth_5yr', idx) or _nz('eps_growth_3yr', idx)
        ])
        v = _avg_present([
            _nz('pe_ratio', idx),
            _nz('peg', idx),
            _nz('pb_ratio', idx),
            _nz('ev_ebitda', idx),
            _nz('cmp_sales', idx)
        ])
        if is_fin:
            c = 50.0
        else:
            fcf_now = _nz('fcf', idx)
            fcf3 = _nz('fcf_3yr', idx)
            fcf5 = _nz('fcf_5yr', idx)
            if fcf3 is not None and fcf5 is not None:
                diff = (fcf5 - fcf3)
                c = max(0.0, min(100.0, 50.0 + diff / 2.0))
            elif fcf_now is not None:
                c = fcf_now
            else:
                c = 50.0
        quality_scores.append(q)
        growth_scores.append(g)
        valuation_scores.append(v)
        cashflow_scores.append(c)
    df['quality_score_v2'] = quality_scores
    df['growth_score_v2'] = growth_scores
    df['valuation_score_v2'] = valuation_scores
    df['cashflow_score_v2'] = cashflow_scores
    df['is_financials_detected'] = is_fin_flags
    final_scores = []
    for idx, row in df.iterrows():
        if row['is_financials_detected']:
            fs = (
                0.45 * row['quality_score_v2'] +
                0.20 * row['growth_score_v2'] +
                0.25 * row['valuation_score_v2'] +
                0.10 * row['cashflow_score_v2']
            )
        else:
            fs = (
                0.35 * row['quality_score_v2'] +
                0.25 * row['growth_score_v2'] +
                0.20 * row['valuation_score_v2'] +
                0.20 * row['cashflow_score_v2']
            )
        final_scores.append(float(fs))
    df['final_score_v2'] = final_scores
    
    # Sort by composite score (after sector adjustments)
    df = df.sort_values('composite_score', ascending=False)
    df['rank'] = range(1, len(df) + 1)
    
    # Get key drivers and reasoning
    df['key_drivers'] = df.apply(get_key_drivers, axis=1)
    df['ranking_reason'] = df.apply(lambda row: generate_ranking_reason(row, philosophy, row['rank']), axis=1)
    
    # Prepare response
    rankings = []
    # Map snake_case to camelCase for JSON response
    metric_name_map = {
        'cmp': 'currentPrice',
        'market_cap': 'marketCap',
        'pe_ratio': 'peRatio',
        'roe': 'roe',
        'roce': 'roce',
        'sales_growth_3yr': 'salesGrowth3Yr',
        'sales_growth_5yr': 'salesGrowth5Yr',
        'sales': 'sales',
        'pat': 'pat',
        'profit_growth_3yr': 'profitGrowth3Yr',
        'profit_growth_5yr': 'profitGrowth5Yr',
        'fcf_3yr': 'fcf3Yr',
        'fcf_5yr': 'fcf5Yr',
        'fcf': 'fcf',
        'peg': 'peg',
        'return_1yr': 'return1Yr',
        'return_3yr': 'return3Yr',
        'return_5yr': 'return5Yr',
        'asset_turnover': 'assetTurnover',
        'cmp_sales': 'priceToSales',
        'eps': 'eps',
        'eps_growth_3yr': 'epsGrowth3Yr',
        'eps_growth_5yr': 'epsGrowth5Yr',
        'debt_equity': 'debtToEquity',
        'opm': 'opm',
        'dividend_yield': 'dividendYield',
        # New metrics
        'npm': 'npm',
        'interest_coverage': 'interestCoverage',
        'current_ratio': 'currentRatio',
        'pb_ratio': 'priceToBook',
        'ev_ebitda': 'evEbitda',
        'dividend_payout': 'dividendPayout',
        'fcf_yield_inverse': 'priceToFcf',
        'pledged_pct': 'pledgedPct',
        'promoter_holding': 'promoterHolding'
    }
    
    for _, row in df.head(50).iterrows():  # Return top 50
        metrics = {}
        for col in numeric_cols:
            if col in row:
                # Convert to camelCase for frontend
                camel_key = metric_name_map.get(col, col)
                metrics[camel_key] = float(row[col]) if not pd.isna(row[col]) else 0.0
        
        # Format risk warnings for display
        risk_warnings_display = []
        for warning in row['risk_warnings']:
            warning_map = {
                'negative_fcf': '⚠️ Negative Free Cash Flow',
                'extreme_pe': '🚨 Extreme P/E Ratio (>100)',
                'high_pe': '⚠️ High P/E Ratio (>50)',
                'moderate_pe': '⚠️ Moderate P/E (25-50x)',
                'high_debt': '🚨 High Debt/Equity (>1.5)',
                'moderate_debt': '⚠️ Moderate Debt (>1.0)',
                'low_roe': '⚠️ Low ROE (<10%)',
                'moderate_roe': '⚠️ Moderate ROE (<12%)',
                'very_low_roe': '🚨 Very Low ROE (<8%)',
                'low_roce': '⚠️ Low ROCE (<12%)',
                'moderate_roce': '⚠️ Moderate ROCE (<15%)',
                'low_roe_negative_growth': '🚨 Low ROE + Negative Growth',
                'low_roe_high_fcf': '⚠️ Low ROE despite High FCF',
                'low_fcf_relative': '⚠️ Low FCF Relative to Size',
                'multiple_red_flags': '🚨 Multiple Quality Concerns',
                'high_peg': '⚠️ High PEG Ratio (>2)',
                'extreme_volatility': '🚨 Extreme Volatility',
                'high_volatility': '⚠️ High Volatility'
            }
            risk_warnings_display.append(warning_map.get(warning, warning))
        
        rankings.append({
            'rank': int(row['rank']),
            'company': str(row['name']),
            'symbol': str(row['symbol']),
            'compositeScore': float(row['composite_score']),
            'buffettScore': float(row['buffett_score']),
            'lynchScore': float(row['lynch_score']),
            'growthScore': float(row['growth_score']),
            'qualityScoreV2': float(row.get('quality_score_v2', 0.0)),
            'growthScoreV2': float(row.get('growth_score_v2', 0.0)),
            'valuationScoreV2': float(row.get('valuation_score_v2', 0.0)),
            'cashflowScoreV2': float(row.get('cashflow_score_v2', 0.0)),
            'finalScoreV2': float(row.get('final_score_v2', 0.0)),
            'keyDrivers': row['key_drivers'],
            'rankingReason': str(row['ranking_reason']),
            'riskWarnings': risk_warnings_display,
            'qualityScore': float(row['quality_score']),
            'cashFlowQuality': float(row['cf_quality_score']),
            'valuationScore': float(row['valuation_score']),
            'valuationWarnings': row['valuation_warnings'],
            'sector': str(row.get('sector', 'General')),
            'sectorAdjustment': float(row.get('sector_adjustment', 0.0)),
            'sectorInsights': str(row.get('sector_insights', '')),
            'investmentTier': int(row.get('investment_tier', 4)),
            'investmentTierName': str(row.get('investment_tier_name', 'Not Classified')),
            'investmentTierAction': str(row.get('investment_tier_action', 'Research Required')),
            'tierInsights': str(row.get('tier_insights', '')),
            'isFinancialsDetected': bool(row.get('is_financials_detected', False)),
            'metrics': metrics
        })
    
    # Save ranking snapshot for performance tracking
    if SECTOR_ENABLED:
        try:
            snapshot_id = save_current_rankings(
                rankings=rankings,
                philosophy=philosophy,
                metadata={
                    'total_analyzed': len(df),
                    'disqualified': len(disqualified_companies),
                    'sector_enabled': True
                }
            )
            print(f"📊 Saved performance snapshot: {snapshot_id}")
        except Exception as e:
            print(f"⚠️ Could not save snapshot: {e}")
    
    return {
        'rankings': rankings,
        'philosophy': philosophy,
        'philosophyDescription': PHILOSOPHIES[philosophy]['description'],
        'totalCompanies': len(df),
        'disqualifiedCount': len(disqualified_companies),
        'disqualifiedCompanies': [{'name': name, 'reason': reason} for name, reason in disqualified_companies],
        'sectorEnabled': SECTOR_ENABLED,
        'tiersEnabled': TIERS_ENABLED,
        'tierStatistics': tier_stats if TIERS_ENABLED else {},
        'portfolioRecommendation': portfolio_recommendation if TIERS_ENABLED else '',
        'fcfDQMode': fcfDQMode
    }


@router.get("/philosophies")
async def get_philosophies():
    """Get available investment philosophies"""
    return {
        philosophy_id: {
            'name': data['name'],
            'weights': data['weights']
        }
        for philosophy_id, data in PHILOSOPHIES.items()
    }
