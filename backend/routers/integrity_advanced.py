"""
Advanced Integrity Analysis Router - Multi-Quarter Analysis
Institutional-grade management integrity tracking with quarter-over-quarter comparison
"""
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import StreamingResponse
from typing import List, Dict, Tuple
import PyPDF2
import io
import re
from datetime import datetime
from collections import defaultdict
import sys
import os
import pandas as pd

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.ai_analyzer import AIAnalyzer

router = APIRouter(prefix="/integrity", tags=["integrity"])

# Initialize AI analyzer
ai_analyzer = AIAnalyzer()


def extract_quarter_from_filename(filename: str) -> Tuple[str, int, int]:
    """Extract quarter and year from filename"""
    patterns = [
        r'(Q|q)(\d)[_\s-]*(FY|fy)?[_\s-]*(\d{4})',  # Q1 FY2024, Q1_2024
        r'(FY|fy)?[_\s-]*(\d{4})[_\s-]*(Q|q)(\d)',  # FY2024 Q1, 2024_Q1
        r'(\d{4})[_\s-]*(Q|q)(\d)',                  # 2024-Q1
    ]
    
    for pattern in patterns:
        match = re.search(pattern, filename, re.IGNORECASE)
        if match:
            groups = match.groups()
            # Extract year and quarter
            year = None
            quarter = None
            
            for g in groups:
                if g and g.isdigit():
                    if len(g) == 4:
                        year = int(g)
                    elif len(g) == 1 and int(g) <= 4:
                        quarter = int(g)
            
            if year and quarter:
                return (f"Q{quarter} FY{year}", quarter, year)
    
    return ("Unknown Quarter", 0, 0)


def extract_quarter_from_text(text: str) -> Tuple[str, int, int]:
    """Fallback: Extract quarter and year from transcript text when filename fails"""
    t = text
    # Normalize fancy apostrophes and whitespace
    t = re.sub(r"[\u2018\u2019\u2032]", "'", t)
    # Common patterns like Q1 FY2025, Q4 FY'25, first quarter FY2026
    patterns = [
        r"(Q|q)([1-4])\s*(FY|fy)?\s*('?)(\d{2,4})",
        r"(FY|fy)\s*('?)(\d{2,4})\s*(Q|q)\s*([1-4])",
        r"(first|1st|second|2nd|third|3rd|fourth|4th)\s+quarter\s+(FY|fy)?\s*('?)(\d{2,4})",
    ]
    quarter_map = {"first": 1, "1st": 1, "second": 2, "2nd": 2, "third": 3, "3rd": 3, "fourth": 4, "4th": 4}
    for p in patterns:
        m = re.search(p, t, re.IGNORECASE)
        if m:
            groups = m.groups()
            qnum = None
            year = None
            # Try to infer positions
            for g in groups:
                if not g:
                    continue
                lg = g.lower()
                if lg in quarter_map:
                    qnum = quarter_map[lg]
                elif lg.isdigit() and (2 <= len(lg) <= 4):
                    y = int(lg)
                    year = 2000 + y if y < 100 else y
                elif lg in ["q", "1", "2", "3", "4"] and len(g) == 1 and g.isdigit():
                    if int(g) <= 4:
                        qnum = int(g)
            if qnum and year:
                return (f"Q{qnum} FY{year}", qnum, year)
    return ("Unknown Quarter", 0, 0)


def extract_text_from_pdf(pdf_file: bytes) -> str:
    """Extract text from PDF file"""
    try:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_file))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading PDF: {str(e)}")


def extract_financial_metrics(text: str) -> Dict:
    """Extract specific financial metrics from transcript"""
    text_lower = text.lower()
    metrics = {}
    
    # Revenue patterns
    revenue_patterns = [
        r'revenue.*?(?:of|was|grew|increased).*?(\d+(?:,\d+)?(?:\.\d+)?)\s*(?:crore|cr|million|billion)',
        r'topline.*?(?:of|was|grew).*?(\d+(?:,\d+)?(?:\.\d+)?)\s*(?:crore|cr|million|billion)',
    ]
    
    for pattern in revenue_patterns:
        matches = re.findall(pattern, text_lower)
        if matches:
            metrics['revenue_mentioned'] = True
            break
    
    # Margin patterns
    margin_patterns = [
        r'(?:ebitda|operating|net)\s+margin.*?(\d+(?:\.\d+)?)\s*%',
        r'margin.*?(?:of|at|was).*?(\d+(?:\.\d+)?)\s*%',
    ]
    
    for pattern in margin_patterns:
        matches = re.findall(pattern, text_lower)
        if matches:
            metrics['margin_mentioned'] = True
            break
    
    return metrics


def analyze_quarter_transcript(text: str, quarter_name: str, company_name: str = "", model: str = None, temperature: float = None) -> Dict:
    """Analyze a single quarter's transcript with AI"""
    text_lower = text.lower()
    
    # Get AI-powered analysis
    ai_analysis = ai_analyzer.analyze_quarter_with_ai(text, quarter_name, company_name, model=model, temperature=temperature, max_chars=4500)
    
    # Key metrics for this quarter (for scoring)
    revenue_mentions = text_lower.count('revenue') + text_lower.count('sales') + text_lower.count('topline')
    margin_mentions = text_lower.count('margin') + text_lower.count('profitability') + text_lower.count('ebitda')
    growth_mentions = sum(text_lower.count(word) for word in ['growth', 'increase', 'expansion', 'accelerat'])
    
    # Positive indicators
    positive_words = ['delivered', 'achieved', 'exceeded', 'outperformed', 'strong', 'robust', 'successful']
    positive_count = sum(text_lower.count(word) for word in positive_words)
    
    # Concern indicators
    concern_words = ['missed', 'below', 'disappointed', 'shortfall', 'challenges', 'headwinds', 'pressure']
    concern_count = sum(text_lower.count(word) for word in concern_words)
    
    # Guidance extraction
    guidance_statements = []
    
    # Revenue guidance
    revenue_guidance = re.findall(
        r'(?:revenue|sales|topline).*?(?:guidance|target|expect|forecast).*?(\d+(?:\.\d+)?)\s*(?:%|percent|crore|million)',
        text_lower
    )
    if revenue_guidance:
        guidance_statements.append({
            'type': 'Revenue',
            'details': f"Revenue guidance mentioned with target of {revenue_guidance[0]}"
        })
    
    # Margin guidance
    margin_guidance = re.findall(
        r'(?:margin|ebitda).*?(?:guidance|target|expect).*?(\d+(?:\.\d+)?)\s*%',
        text_lower
    )
    if margin_guidance:
        guidance_statements.append({
            'type': 'Margin',
            'details': f"Margin target of {margin_guidance[0]}%"
        })
    
    # Extract key highlights
    highlights = []
    
    if positive_count > 5:
        highlights.append(f"Strong performance indicators ({positive_count} positive mentions)")
    
    if revenue_mentions > 8:
        if growth_mentions > 3:
            highlights.append(f"Revenue growth emphasized ({revenue_mentions} revenue mentions, {growth_mentions} growth indicators)")
        else:
            highlights.append(f"Revenue discussed extensively ({revenue_mentions} mentions)")
    
    if margin_mentions > 5:
        if 'expansion' in text_lower or 'improved' in text_lower:
            highlights.append(f"Margin expansion focus ({margin_mentions} margin discussions)")
        else:
            highlights.append(f"Profitability metrics discussed ({margin_mentions} mentions)")
    
    # Strategic initiatives
    strategy_words = ['digital', 'transformation', 'innovation', 'technology', 'automation', 'ai', 'cloud']
    strategy_count = sum(text_lower.count(word) for word in strategy_words)
    if strategy_count > 10:
        highlights.append(f"Strong strategic initiatives focus ({strategy_count} technology/innovation mentions)")
    
    # Customer focus
    customer_count = text_lower.count('customer') + text_lower.count('client')
    if customer_count > 15:
        highlights.append(f"High customer centricity ({customer_count} customer/client mentions)")
    
    # Concerns
    concerns = []
    if concern_count > 5:
        concerns.append(f"Challenges acknowledged ({concern_count} concern indicators)")
    
    # Calculate quarter score
    base_score = 60
    score_adjustment = (positive_count * 2) - (concern_count * 3) + (growth_mentions * 1.5)
    quarter_score = max(0, min(100, base_score + score_adjustment))
    
    return {
        'quarter': quarter_name,
        'score': round(quarter_score, 1),
        'highlights': highlights if highlights else ["Standard quarterly performance discussion"],
        'concerns': concerns if concerns else ["No major concerns highlighted"],
        'guidance': guidance_statements,
        'ai_analysis': ai_analysis,  # Add AI-powered insights
        'metrics': {
            'revenue_mentions': revenue_mentions,
            'margin_mentions': margin_mentions,
            'growth_mentions': growth_mentions,
            'positive_indicators': positive_count,
            'concern_indicators': concern_count,
            'strategy_mentions': strategy_count
        }
    }


def compare_quarters(quarters_data: List[Dict]) -> Dict:
    """Compare multiple quarters and track guidance vs delivery"""
    if len(quarters_data) < 2:
        return {
            'trend': 'Insufficient data for comparison',
            'guidance_tracking': [],
            'performance_summary': 'Single quarter analyzed'
        }
    
    # Sort by year and quarter
    sorted_quarters = sorted(quarters_data, key=lambda x: (x.get('year', 0), x.get('quarter_num', 0)))
    
    # Track trends
    scores = [q['score'] for q in sorted_quarters]
    score_trend = "Improving" if scores[-1] > scores[0] else "Declining" if scores[-1] < scores[0] else "Stable"
    
    # Guidance tracking
    guidance_tracking = []
    
    for i in range(len(sorted_quarters) - 1):
        current_q = sorted_quarters[i]
        next_q = sorted_quarters[i + 1]
        
        # Check if guidance from current quarter was met in next quarter
        current_guidance = current_q.get('guidance', [])
        
        for guidance in current_guidance:
            # Simple heuristic: if next quarter has higher positive indicators, guidance likely met
            current_positive = current_q['metrics']['positive_indicators']
            next_positive = next_q['metrics']['positive_indicators']
            
            delivery_status = "Delivered" if next_positive >= current_positive else "Missed"
            
            guidance_tracking.append({
                'quarter': current_q['quarter'],
                'guidance': guidance['details'],
                'next_quarter': next_q['quarter'],
                'status': delivery_status,
                'evidence': f"Positive indicators: {current_positive} → {next_positive}"
            })
    
    # Performance summary
    avg_score = sum(scores) / len(scores)
    best_quarter = max(sorted_quarters, key=lambda x: x['score'])
    worst_quarter = min(sorted_quarters, key=lambda x: x['score'])
    
    performance_summary = f"Average integrity score: {avg_score:.1f}. Best: {best_quarter['quarter']} ({best_quarter['score']}), Weakest: {worst_quarter['quarter']} ({worst_quarter['score']})"
    
    return {
        'trend': score_trend,
        'guidance_tracking': guidance_tracking,
        'performance_summary': performance_summary,
        'score_progression': [{'quarter': q['quarter'], 'score': q['score']} for q in sorted_quarters]
    }


@router.post("/analyze")
async def analyze_integrity(
    files: List[UploadFile] = File(...),
    company_name: str = Form(...),
    model: str = Form(default=""),
    temperature: float = Form(default=0.1)
):
    """
    Advanced multi-quarter integrity analysis
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded")
    
    # Process each PDF separately
    quarters_analysis = []
    
    for file in files:
        if not file.filename.endswith('.pdf'):
            raise HTTPException(status_code=400, detail=f"File {file.filename} is not a PDF")
        
        # Extract quarter info from filename
        quarter_name, quarter_num, year = extract_quarter_from_filename(file.filename)
        
        # Extract text
        content = await file.read()
        text = extract_text_from_pdf(content)
        # Fallback to extract quarter from transcript content when unknown
        if quarter_num == 0 or year == 0:
            qn, qnum2, year2 = extract_quarter_from_text(text)
            if qnum2 and year2:
                quarter_name, quarter_num, year = qn, qnum2, year2
        
        # Analyze this quarter
        quarter_analysis = analyze_quarter_transcript(text, quarter_name, company_name, model=(model or None), temperature=temperature)
        quarter_analysis['year'] = year
        quarter_analysis['quarter_num'] = quarter_num
        quarter_analysis['filename'] = file.filename
        
        quarters_analysis.append(quarter_analysis)
    
    # Sort quarters chronologically
    quarters_analysis.sort(key=lambda x: (x['year'], x['quarter_num']))
    
    # Compare quarters
    comparison = compare_quarters(quarters_analysis)
    
    # Calculate overall score (weighted average, recent quarters weighted more)
    if len(quarters_analysis) > 0:
        weights = [i + 1 for i in range(len(quarters_analysis))]  # More weight to recent quarters
        total_weight = sum(weights)
        overall_score = sum(q['score'] * w for q, w in zip(quarters_analysis, weights)) / total_weight
    else:
        overall_score = 0
    
    # Build comprehensive response
    return {
        'company': company_name,
        'overallScore': round(overall_score, 1),
        'quartersAnalyzed': len(quarters_analysis),
        'quarters': quarters_analysis,
        'comparison': comparison,
        'summary': {
            'trend': comparison['trend'],
            'averageScore': round(sum(q['score'] for q in quarters_analysis) / len(quarters_analysis), 1) if quarters_analysis else 0,
            'guidanceDelivery': f"{len([g for g in comparison.get('guidance_tracking', []) if g['status'] == 'Delivered'])} out of {len(comparison.get('guidance_tracking', []))} guidance statements delivered" if comparison.get('guidance_tracking') else "No guidance tracking available"
        },
        'analyzedAt': datetime.utcnow().isoformat()
    }


@router.post("/export")
async def export_report(analysis: Dict):
    """Export a concise CSV from the provided analysis JSON"""
    headers = ["Quarter", "Score", "RevenueGrowth", "MarginTrend", "Credibility", "KeyInsights"]
    rows = [",".join(headers)]
    for q in analysis.get('quarters', []):
        fi = q.get('ai_analysis', {}).get('financial_performance', {}) if q.get('ai_analysis') else {}
        mgmt = q.get('ai_analysis', {}).get('management_quality', {}) if q.get('ai_analysis') else {}
        insights = q.get('ai_analysis', {}).get('key_insights', []) if q.get('ai_analysis') else []
        row = [
            q.get('quarter', ''),
            str(q.get('score', '')),
            fi.get('revenue_growth', '') if isinstance(fi, dict) else '',
            fi.get('margin_trend', '') if isinstance(fi, dict) else '',
            str(mgmt.get('credibility_score', '')) if isinstance(mgmt, dict) else '',
            " | ".join(insights[:3]) if isinstance(insights, list) else ''
        ]
        # Escape commas in fields
        row = [f'"{c.replace("\"", "''").replace("\n", " ")}"' if "," in c else c for c in row]
        rows.append(",".join(row))
    csv_data = "\n".join(rows)
    return StreamingResponse(iter([csv_data]), media_type='text/csv', headers={
        'Content-Disposition': 'attachment; filename="management_integrity_report.csv"'
    })


@router.post("/rank_excel")
async def rank_excel(file: UploadFile = File(...)):
    """Rank stocks from uploaded Excel based on fundamental factors.
    Expects a worksheet with headers like user sample.
    Returns top rankings with a composite score.
    """
    if not (file.filename.endswith('.xlsx') or file.filename.endswith('.xls')):
        raise HTTPException(status_code=400, detail="Please upload an Excel file (.xlsx or .xls)")

    content = await file.read()
    try:
        # Read first sheet, try header=0 first, then header=1 if Name not found
        df = pd.read_excel(io.BytesIO(content), sheet_name=0, header=0)
        # Check if first row looks like generic headers (A, B, C, etc.)
        first_cols = [str(c).strip().upper() for c in df.columns[:5]]
        if all(c in ['A', 'B', 'C', 'D', 'E', 'S.NO.', 'UNNAMED: 0'] or c.startswith('UNNAMED') for c in first_cols):
            # Re-read with header=1 (second row as header)
            df = pd.read_excel(io.BytesIO(content), sheet_name=0, header=1)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read Excel: {e}")

    # Normalize column names by stripping spaces and normalizing whitespace
    def norm(c):
        return str(c).replace('\u00a0', ' ').replace('\xa0',' ').strip()
    df.columns = [norm(c) for c in df.columns]
    
    print(f"📊 Excel columns detected: {list(df.columns)}")

    # Expected key columns (best-effort match)
    name_col = next((c for c in df.columns if c.lower().startswith('name')), None)
    pe_col = next((c for c in df.columns if c.lower().startswith('p/e')), None)
    roe_col = next((c for c in df.columns if 'roe' in c.lower()), None)
    roce_col = next((c for c in df.columns if 'roce' in c.lower()), None)
    sales3_col = next((c for c in df.columns if 'sales var 3' in c.lower()), None)
    profit3_col = next((c for c in df.columns if 'profit var 3' in c.lower()), None)
    peg_col = next((c for c in df.columns if c.lower().startswith('peg')), None)
    debt_eq_col = next((c for c in df.columns if 'debt' in c.lower()), None)
    opm_col = next((c for c in df.columns if 'opm' in c.lower()), None)

    if not name_col:
        raise HTTPException(status_code=400, detail=f"Could not locate 'Name' column. Found columns: {', '.join(df.columns[:10])}")

    work = df.copy()

    # Convert percentage-like strings to numeric
    def to_num(series):
        return pd.to_numeric(series.astype(str).str.replace('%','', regex=False).str.replace(',',''), errors='coerce')

    # Build factor scores (rank-based 0..100)
    scores = pd.DataFrame(index=work.index)
    def rank_score(col, ascending=False, weight=1.0):
        if not col:
            return pd.Series(0, index=work.index)
        vals = to_num(work[col])
        r = vals.rank(method='average', ascending=ascending)
        score = (r / r.max()) * 100.0
        return score.fillna(0) * weight

    # Higher is better
    s_roe = rank_score(roe_col, ascending=False, weight=1.5)
    s_roce = rank_score(roce_col, ascending=False, weight=1.2)
    s_sales3 = rank_score(sales3_col, ascending=False, weight=1.0)
    s_profit3 = rank_score(profit3_col, ascending=False, weight=1.2)
    s_opm = rank_score(opm_col, ascending=False, weight=1.0)

    # Lower is better
    s_pe = rank_score(pe_col, ascending=True, weight=1.0)
    s_peg = rank_score(peg_col, ascending=True, weight=1.0)
    s_de = rank_score(debt_eq_col, ascending=True, weight=1.2)

    composite = s_roe + s_roce + s_sales3 + s_profit3 + s_opm + s_pe + s_peg + s_de
    work['rank_score'] = composite.round(2)

    # Select output columns
    out_cols = [name_col, 'rank_score']
    for c in [pe_col, roe_col, roce_col, sales3_col, profit3_col, opm_col, peg_col, debt_eq_col]:
        if c and c not in out_cols:
            out_cols.append(c)
    output = work[out_cols].sort_values('rank_score', ascending=False).reset_index(drop=True)

    # Build JSON response
    results = []
    for _, row in output.iterrows():
        item = { 'name': row.get(name_col, ''), 'rank_score': float(row.get('rank_score', 0)) }
        for c in out_cols:
            if c not in [name_col, 'rank_score']:
                v = row.get(c)
                if pd.notna(v):
                    item[c] = float(v) if isinstance(v, (int, float)) else str(v)
        results.append(item)

    return {
        'mode': 'excel_ranking',
        'count': len(results),
        'columns': out_cols,
        'items': results
    }


@router.get("/companies")
async def get_companies():
    """Get list of analyzed companies"""
    return [
        {
            'id': 1,
            'name': 'Infosys Limited',
            'symbol': 'INFY',
            'sector': 'Information Technology',
            'lastAnalyzed': '2024-01-15'
        }
    ]


@router.post("/companies")
async def create_company(name: str, symbol: str, sector: str):
    """Create a new company entry"""
    return {
        'id': 1,
        'name': name,
        'symbol': symbol,
        'sector': sector,
        'created': datetime.utcnow().isoformat()
    }
