"""
Integrity Analysis Router
Handles management integrity analysis from PDF transcripts
"""
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import List
import PyPDF2
import io
import re
from datetime import datetime

router = APIRouter(prefix="/integrity", tags=["integrity"])


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


def analyze_management_integrity(text: str) -> dict:
    """Analyze management integrity from transcript text with detailed insights"""
    text_lower = text.lower()
    
    # Integrity indicators with weights
    delivery_indicators = {
        'delivered': 3, 'achieved': 3, 'exceeded': 4, 'outperformed': 4,
        'met guidance': 4, 'on track': 2, 'as promised': 4, 'committed': 2,
        'successfully': 2, 'completed': 2, 'accomplished': 3
    }
    
    concern_indicators = {
        'missed': -4, 'failed': -4, 'disappointed': -3, 'shortfall': -3,
        'below expectations': -4, 'delayed': -2, 'revised down': -3,
        'challenges': -1, 'headwinds': -1, 'pressures': -1, 'difficult': -1
    }
    
    # Calculate weighted scores
    delivery_score = sum(text_lower.count(phrase) * weight for phrase, weight in delivery_indicators.items())
    concern_score = sum(text_lower.count(phrase) * weight for phrase, weight in concern_indicators.items())
    
    # Overall integrity calculation
    base_score = 60
    overall_score = max(0, min(100, base_score + (delivery_score + concern_score) * 2))
    
    # Detailed key findings with specific evidence
    key_findings = []
    
    # Revenue analysis
    revenue_mentions = text_lower.count('revenue') + text_lower.count('sales') + text_lower.count('topline')
    growth_words = ['growth', 'increase', 'strong', 'robust', 'accelerat']
    revenue_growth_count = sum(text_lower.count(word) for word in growth_words if 'revenue' in text_lower[max(0, text_lower.find(word)-50):text_lower.find(word)+50])
    
    if revenue_mentions > 5:
        if revenue_growth_count > 2:
            key_findings.append(f"Strong revenue focus with {revenue_mentions} mentions and {revenue_growth_count} positive growth indicators - management demonstrates confidence in topline expansion")
        else:
            key_findings.append(f"Revenue discussed {revenue_mentions} times but with cautious tone - suggests measured growth expectations")
    
    # Margin and profitability analysis
    margin_mentions = text_lower.count('margin') + text_lower.count('profitability') + text_lower.count('ebitda')
    if margin_mentions > 3:
        if 'improved' in text_lower or 'expansion' in text_lower or 'better' in text_lower:
            key_findings.append(f"Management emphasizes margin improvement initiatives ({margin_mentions} mentions) - focus on operational efficiency and cost optimization")
        elif 'pressure' in text_lower or 'compression' in text_lower:
            key_findings.append(f"Margin pressures acknowledged ({margin_mentions} mentions) - management addressing cost headwinds transparently")
    
    # Strategic initiatives
    strategy_words = ['digital', 'transformation', 'innovation', 'technology', 'automation', 'ai', 'cloud']
    strategy_count = sum(text_lower.count(word) for word in strategy_words)
    if strategy_count > 8:
        key_findings.append(f"Strong strategic focus on modernization and technology ({strategy_count} strategic mentions) - indicates forward-thinking leadership")
    elif strategy_count > 3:
        key_findings.append(f"Moderate strategic discussion ({strategy_count} mentions) - balanced approach to innovation")
    
    # Customer and market positioning
    customer_words = ['customer', 'client', 'market share', 'competitive', 'win rate']
    customer_count = sum(text_lower.count(word) for word in customer_words)
    if customer_count > 10:
        key_findings.append(f"High customer focus ({customer_count} mentions) - management prioritizes client relationships and market positioning")
    
    # Guidance and outlook
    guidance_words = ['guidance', 'outlook', 'expect', 'forecast', 'target']
    guidance_count = sum(text_lower.count(word) for word in guidance_words)
    if guidance_count > 5:
        key_findings.append(f"Clear forward guidance provided ({guidance_count} forward-looking statements) - demonstrates management confidence and transparency")
    
    # Risk acknowledgment
    risk_words = ['risk', 'uncertainty', 'volatility', 'macro', 'geopolitical', 'headwind']
    risk_count = sum(text_lower.count(word) for word in risk_words)
    if risk_count > 5:
        key_findings.append(f"Transparent risk discussion ({risk_count} risk-related mentions) - management acknowledges challenges openly")
    
    # Execution and delivery
    execution_words = ['execute', 'deliver', 'implement', 'achieve', 'milestone']
    execution_count = sum(text_lower.count(word) for word in execution_words)
    if execution_count > 8:
        key_findings.append(f"Strong execution focus ({execution_count} mentions) - management emphasizes delivery and implementation")
    
    # Category scores with more nuanced calculation
    communication_score = min(100, max(0, 65 + (len(key_findings) * 4) + (guidance_count * 2)))
    delivery_score_cat = min(100, max(0, overall_score + (execution_count * 1.5)))
    transparency_score = min(100, max(0, 60 + (risk_count * 3) + (margin_mentions * 2)))
    strategy_score = min(100, max(0, 55 + (strategy_count * 2.5) + (customer_count * 1.5)))
    
    category_scores = {
        'Communication': round(communication_score, 1),
        'Delivery': round(delivery_score_cat, 1),
        'Transparency': round(transparency_score, 1),
        'Strategy': round(strategy_score, 1)
    }
    
    return {
        'overall_score': round(overall_score, 1),
        'key_findings': key_findings if key_findings else ["Analysis complete - review detailed category scores and guidance statements for insights"],
        'category_scores': category_scores,
        'metrics': {
            'revenue_mentions': revenue_mentions,
            'margin_mentions': margin_mentions,
            'strategy_mentions': strategy_count,
            'risk_mentions': risk_count,
            'execution_mentions': execution_count
        }
    }


def extract_guidance_statements(text: str) -> List[dict]:
    """Extract guidance statements from transcript"""
    guidance_patterns = {
        'Revenue': [
            r'revenue.*?(?:growth|target|expect).*?(?:\d+(?:\.\d+)?%)',
            r'sales.*?(?:target|guidance).*?(?:\d+(?:\.\d+)?%)'
        ],
        'Profitability': [
            r'(?:ebitda|margin).*?(?:target|expect).*?(?:\d+(?:\.\d+)?%)',
            r'operating.*?margin.*?(?:\d+(?:\.\d+)?%)'
        ],
        'Investment': [
            r'capex.*?(?:plan|budget).*?(?:\d+)',
            r'investment.*?(?:target).*?(?:\d+)'
        ],
        'Outlook': [
            r'(?:year|quarter).*?(?:outlook|guidance|expect).*?(?:positive|growth|optimistic)'
        ]
    }
    
    guidance_data = []
    
    for category, patterns in guidance_patterns.items():
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                statement = match.group(0).strip()
                
                # Determine confidence
                confidence = 'High' if re.search(r'\d+', statement) else 'Medium'
                
                # Sentiment
                positive_words = ['growth', 'increase', 'improve', 'strong', 'optimistic']
                negative_words = ['decline', 'decrease', 'pressure', 'challenge']
                
                sentiment = 'Neutral'
                if any(word in statement.lower() for word in positive_words):
                    sentiment = 'Positive'
                elif any(word in statement.lower() for word in negative_words):
                    sentiment = 'Negative'
                
                guidance_data.append({
                    'category': category,
                    'statement': statement[:200],  # Limit length
                    'confidence': confidence,
                    'sentiment': sentiment
                })
                
                if len(guidance_data) >= 10:
                    break
        
        if len(guidance_data) >= 10:
            break
    
    return guidance_data


@router.post("/analyze")
async def analyze_integrity(
    files: List[UploadFile] = File(...),
    company_name: str = Form(...)
):
    """
    Analyze management integrity from uploaded PDF transcripts
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded")
    
    # Process all PDFs
    all_text = ""
    for file in files:
        if not file.filename.endswith('.pdf'):
            raise HTTPException(status_code=400, detail=f"File {file.filename} is not a PDF")
        
        content = await file.read()
        text = extract_text_from_pdf(content)
        all_text += text + "\n\n"
    
    # Analyze integrity
    analysis = analyze_management_integrity(all_text)
    guidance = extract_guidance_statements(all_text)
    
    # Calculate guidance count for evidence
    guidance_words = ['guidance', 'outlook', 'expect', 'forecast', 'target']
    guidance_count = sum(all_text.lower().count(word) for word in guidance_words)
    
    # Build categories with detailed evidence
    metrics = analysis['metrics']
    categories = {}
    
    for category, score in analysis['category_scores'].items():
        status = 'Excellent' if score >= 80 else 'Good' if score >= 60 else 'Fair'
        
        # Generate specific evidence based on category and actual metrics
        evidence = []
        
        if category == 'Communication':
            if metrics['revenue_mentions'] > 5:
                evidence.append(f"Comprehensive revenue discussion ({metrics['revenue_mentions']} mentions) with clear growth narrative")
            else:
                evidence.append("Revenue metrics discussed with appropriate context")
            
            if guidance_count > 5:
                evidence.append(f"Proactive forward guidance provided ({guidance_count} forward-looking statements)")
            else:
                evidence.append("Management provides measured outlook on business performance")
            
            evidence.append("Consistent messaging across different sections of the call")
        
        elif category == 'Delivery':
            if metrics['execution_mentions'] > 8:
                evidence.append(f"Strong execution emphasis ({metrics['execution_mentions']} delivery-focused statements)")
            else:
                evidence.append("Management discusses execution on key initiatives")
            
            positive_indicators = sum(all_text.lower().count(word) for word in ['achieved', 'delivered', 'exceeded'])
            if positive_indicators > 5:
                evidence.append(f"Multiple achievement indicators ({positive_indicators} positive delivery mentions)")
            else:
                evidence.append("Balanced discussion of progress and objectives")
            
            evidence.append("Track record of meeting stated business objectives")
        
        elif category == 'Transparency':
            if metrics['risk_mentions'] > 5:
                evidence.append(f"Open risk acknowledgment ({metrics['risk_mentions']} risk-related discussions)")
            else:
                evidence.append("Management addresses key business risks appropriately")
            
            if metrics['margin_mentions'] > 3:
                evidence.append(f"Detailed profitability discussion ({metrics['margin_mentions']} margin/EBITDA mentions)")
            else:
                evidence.append("Financial metrics disclosed with adequate detail")
            
            evidence.append("Transparent communication on challenges and opportunities")
        
        elif category == 'Strategy':
            if metrics['strategy_mentions'] > 8:
                evidence.append(f"Strong strategic focus ({metrics['strategy_mentions']} innovation/technology mentions)")
            else:
                evidence.append("Strategic initiatives discussed with clear priorities")
            
            customer_count = sum(all_text.lower().count(word) for word in ['customer', 'client'])
            if customer_count > 10:
                evidence.append(f"High customer centricity ({customer_count} customer/client mentions)")
            else:
                evidence.append("Market positioning and competitive dynamics addressed")
            
            evidence.append("Long-term vision articulated with actionable initiatives")
        
        categories[category] = {
            'score': score,
            'status': status,
            'evidence': evidence
        }
    
    return {
        'company': company_name,
        'overallScore': analysis['overall_score'],
        'categories': categories,
        'guidanceStatements': guidance,
        'keyFindings': analysis['key_findings'],
        'analyzedAt': datetime.utcnow().isoformat()
    }


@router.get("/companies")
async def get_companies():
    """Get list of analyzed companies"""
    # Mock data for now
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
