"""
Sector-Specific Adjustments for Financial Ranking
Different sectors have different financial norms and expectations
"""
from typing import Dict, Optional
import pandas as pd


# Sector-specific benchmarks for Indian markets
SECTOR_BENCHMARKS = {
    'IT': {
        'name': 'Information Technology',
        'roe_threshold': 20.0,
        'roce_threshold': 25.0,
        'debt_equity_norm': 0.5,
        'opm_norm': 20.0,
        'fcf_importance': 'high',
        'debt_penalty_multiplier': 1.5,  # Stricter on debt
        'fcf_weight_multiplier': 1.3,    # Higher weight on FCF
    },
    'Banking': {
        'name': 'Banking & Financial Services',
        'roe_threshold': 12.0,
        'roce_threshold': None,  # Not applicable for banks
        'debt_equity_norm': 5.0,  # Banks have high leverage naturally
        'opm_norm': 40.0,
        'fcf_importance': 'medium',
        'debt_penalty_multiplier': 0.1,  # 90% reduction in debt penalty
        'asset_quality_weight': 0.15,    # NPA focus
    },
    'Pharma': {
        'name': 'Pharmaceuticals',
        'roe_threshold': 15.0,
        'roce_threshold': 18.0,
        'debt_equity_norm': 0.8,
        'opm_norm': 20.0,
        'fcf_importance': 'high',
        'rd_intensity': 'high',  # R&D spending is normal
    },
    'Manufacturing': {
        'name': 'Manufacturing',
        'roe_threshold': 12.0,
        'roce_threshold': 15.0,
        'debt_equity_norm': 1.5,
        'opm_norm': 10.0,
        'fcf_importance': 'medium',
        'asset_turnover_weight': 0.15,  # Asset efficiency matters
        'working_capital_focus': True,
    },
    'Telecom': {
        'name': 'Telecommunications',
        'roe_threshold': 8.0,
        'roce_threshold': 10.0,
        'debt_equity_norm': 2.5,  # Capital intensive
        'opm_norm': 30.0,
        'fcf_importance': 'critical',
        'capex_intensity': 'very_high',
    },
    'RealEstate': {
        'name': 'Real Estate',
        'roe_threshold': 8.0,
        'roce_threshold': 10.0,
        'debt_equity_norm': 2.0,
        'opm_norm': 25.0,
        'fcf_importance': 'medium',
        'inventory_turnover_focus': True,
    },
    'FMCG': {
        'name': 'Fast Moving Consumer Goods',
        'roe_threshold': 18.0,
        'roce_threshold': 25.0,
        'debt_equity_norm': 0.5,
        'opm_norm': 15.0,
        'fcf_importance': 'high',
        'brand_value_importance': 'high',
    },
    'Auto': {
        'name': 'Automobile',
        'roe_threshold': 12.0,
        'roce_threshold': 15.0,
        'debt_equity_norm': 1.2,
        'opm_norm': 8.0,
        'fcf_importance': 'medium',
        'inventory_management': 'critical',
    },
    'Energy': {
        'name': 'Energy & Power',
        'roe_threshold': 10.0,
        'roce_threshold': 12.0,
        'debt_equity_norm': 2.0,
        'opm_norm': 12.0,
        'fcf_importance': 'high',
        'capex_intensity': 'very_high',
    },
    'Healthcare': {
        'name': 'Healthcare Services',
        'roe_threshold': 15.0,
        'roce_threshold': 18.0,
        'debt_equity_norm': 1.0,
        'opm_norm': 18.0,
        'fcf_importance': 'high',
        'quality_metrics_focus': True,
    }
}


def get_sector_from_name(company_name: str, industry_keywords: Optional[Dict] = None) -> str:
    """
    Attempt to identify sector from company name or industry keywords
    
    Args:
        company_name: Name of the company
        industry_keywords: Optional dict mapping sectors to keywords
        
    Returns:
        Sector identifier or 'General' if unknown
    """
    if industry_keywords is None:
        industry_keywords = {
            'IT': ['tech', 'software', 'infotech', 'systems', 'solutions', 'technologies'],
            'Banking': ['bank', 'finance', 'nbfc', 'financial', 'capital', 'securities'],
            'Pharma': ['pharma', 'drug', 'biotech', 'healthcare', 'medical', 'lab'],
            'Manufacturing': ['industries', 'manufacturing', 'steel', 'cement', 'chemicals'],
            'Telecom': ['telecom', 'communications', 'wireless', 'broadband'],
            'RealEstate': ['realty', 'properties', 'construction', 'builders'],
            'FMCG': ['consumer', 'foods', 'beverages', 'fmcg'],
            'Auto': ['auto', 'motors', 'vehicles', 'automotive'],
            'Energy': ['power', 'energy', 'oil', 'gas', 'petroleum'],
        }
    
    company_lower = company_name.lower()
    
    for sector, keywords in industry_keywords.items():
        if any(keyword in company_lower for keyword in keywords):
            return sector
    
    return 'General'


def adjust_score_for_sector(
    base_score: float,
    company_data: pd.Series,
    sector: str,
    penalties: Dict[str, float]
) -> Dict:
    """
    Apply sector-specific adjustments to scoring
    
    Args:
        base_score: Base composite score before sector adjustment
        company_data: Company financial metrics
        sector: Identified sector
        penalties: Current penalty dict
        
    Returns:
        Dict with adjusted score and sector insights
    """
    if sector not in SECTOR_BENCHMARKS:
        return {
            'adjusted_score': base_score,
            'sector_adjustment': 0.0,
            'sector_insights': []
        }
    
    benchmarks = SECTOR_BENCHMARKS[sector]
    adjustment_multiplier = 1.0
    insights = []
    
    # Adjust debt penalty based on sector norms
    if 'debt_equity' in company_data and 'debt_penalty_multiplier' in benchmarks:
        debt_ratio = company_data['debt_equity']
        sector_norm = benchmarks['debt_equity_norm']
        
        if debt_ratio <= sector_norm:
            # Within sector norms - reduce or remove penalty
            if 'high_debt' in penalties:
                original_penalty = penalties['high_debt']
                penalties['high_debt'] *= benchmarks['debt_penalty_multiplier']
                insights.append(f"Debt within {benchmarks['name']} norms ({debt_ratio:.2f} vs {sector_norm:.2f})")
        else:
            # Above sector norms - flag it
            excess = ((debt_ratio - sector_norm) / sector_norm) * 100
            insights.append(f"⚠️ Debt {excess:.0f}% above {benchmarks['name']} norm")
    
    # Adjust FCF importance
    if 'fcf' in company_data and 'fcf_weight_multiplier' in benchmarks:
        if company_data['fcf'] > 0:
            fcf_bonus = (benchmarks['fcf_weight_multiplier'] - 1.0) * 0.05
            adjustment_multiplier += fcf_bonus
            insights.append(f"Strong FCF valued highly in {benchmarks['name']}")
    
    # ROE threshold adjustment
    if 'roe' in company_data:
        roe_threshold = benchmarks['roe_threshold']
        if company_data['roe'] > roe_threshold:
            roe_premium = min((company_data['roe'] - roe_threshold) / roe_threshold * 0.1, 0.15)
            adjustment_multiplier += roe_premium
            insights.append(f"ROE exceeds {benchmarks['name']} threshold ({company_data['roe']:.1f}% > {roe_threshold}%)")
        elif company_data['roe'] < roe_threshold * 0.7:
            insights.append(f"⚠️ ROE below {benchmarks['name']} expectations")
    
    # ROCE threshold (if applicable)
    if 'roce' in company_data and benchmarks['roce_threshold'] is not None:
        roce_threshold = benchmarks['roce_threshold']
        if company_data['roce'] > roce_threshold:
            insights.append(f"ROCE exceeds {benchmarks['name']} threshold")
    
    # OPM assessment
    if 'opm' in company_data:
        opm_norm = benchmarks['opm_norm']
        if company_data['opm'] > opm_norm * 1.2:
            adjustment_multiplier += 0.05
            insights.append(f"Exceptional margins for {benchmarks['name']} sector")
        elif company_data['opm'] < opm_norm * 0.6:
            insights.append(f"⚠️ Margins below {benchmarks['name']} average")
    
    # Banking-specific: Remove ROCE penalty
    if sector == 'Banking' and benchmarks['roce_threshold'] is None:
        # Banks don't use ROCE - remove any ROCE-related penalties
        insights.append("ROCE not applicable for banking sector")
    
    # Calculate final adjusted score
    adjusted_score = base_score * adjustment_multiplier
    sector_adjustment = (adjustment_multiplier - 1.0) * 100  # As percentage
    
    return {
        'adjusted_score': round(adjusted_score, 1),
        'sector_adjustment': round(sector_adjustment, 1),
        'sector_insights': insights,
        'sector_name': benchmarks['name']
    }


def get_sector_comparison_metrics(sector: str) -> Dict:
    """
    Get sector-specific metrics for comparison and display
    
    Args:
        sector: Sector identifier
        
    Returns:
        Dict with sector benchmarks and expectations
    """
    if sector not in SECTOR_BENCHMARKS:
        return {}
    
    benchmarks = SECTOR_BENCHMARKS[sector]
    
    return {
        'sector': benchmarks['name'],
        'expected_roe': benchmarks['roe_threshold'],
        'expected_roce': benchmarks.get('roce_threshold'),
        'typical_debt': benchmarks['debt_equity_norm'],
        'typical_opm': benchmarks['opm_norm'],
        'fcf_importance': benchmarks['fcf_importance'],
        'special_considerations': get_sector_special_considerations(sector)
    }


def get_sector_special_considerations(sector: str) -> list:
    """Get special considerations for each sector"""
    considerations = {
        'IT': [
            'High FCF generation expected',
            'Low debt tolerance',
            'Margin stability important',
            'Client concentration risk'
        ],
        'Banking': [
            'High leverage is normal',
            'Asset quality (NPA) critical',
            'Net Interest Margin focus',
            'Capital adequacy requirements'
        ],
        'Pharma': [
            'R&D spending reduces short-term profits',
            'Patent cliff risks',
            'Regulatory approval timelines',
            'Product pipeline quality'
        ],
        'Manufacturing': [
            'Working capital management critical',
            'Capacity utilization matters',
            'Commodity price sensitivity',
            'Asset turnover efficiency'
        ],
        'Telecom': [
            'Very high capex requirements',
            'Spectrum costs',
            'ARPU trends important',
            'Subscriber growth vs churn'
        ]
    }
    
    return considerations.get(sector, ['General sector considerations apply'])


def apply_sector_adjustments_to_dataframe(df: pd.DataFrame, sector_column: str = 'sector') -> pd.DataFrame:
    """
    Apply sector adjustments to entire dataframe
    
    Args:
        df: DataFrame with company data
        sector_column: Name of column containing sector information
        
    Returns:
        DataFrame with sector-adjusted scores
    """
    df = df.copy()
    
    # If no sector column, try to infer from company name
    if sector_column not in df.columns and 'name' in df.columns:
        df['sector'] = df['name'].apply(get_sector_from_name)
    
    # Apply adjustments
    df['sector_adjustment'] = 0.0
    df['sector_insights'] = ''
    
    for idx, row in df.iterrows():
        sector = row.get(sector_column, 'General')
        
        # Get current penalties (would need to be calculated)
        penalties = {}  # Placeholder
        
        adjustment_result = adjust_score_for_sector(
            base_score=row.get('composite_score', 0),
            company_data=row,
            sector=sector,
            penalties=penalties
        )
        
        df.at[idx, 'sector_adjusted_score'] = adjustment_result['adjusted_score']
        df.at[idx, 'sector_adjustment'] = adjustment_result['sector_adjustment']
        df.at[idx, 'sector_insights'] = '; '.join(adjustment_result['sector_insights'])
    
    return df
