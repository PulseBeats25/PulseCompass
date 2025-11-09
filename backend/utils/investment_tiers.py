"""
Investment Tier Classification System
Based on deep analysis feedback - Quality over Quantity
"""
import pandas as pd
from typing import Dict, List, Tuple


def classify_investment_tier(row: pd.Series) -> Tuple[int, str, str]:
    """
    Classify company into investment tiers based on fundamental quality
    
    Returns:
        (tier_number, tier_name, tier_action)
    
    Tier 1: CORE PORTFOLIO (5-8 stocks) - BUY/HOLD 5+ years
    Tier 2: QUALITY ADDITIONS (10-15 stocks) - HOLD/BUY on dips
    Tier 3: SPECIALIZED PLAYS (15-20 stocks) - HOLD/RESEARCH
    Tier 4: AVOID (Remaining) - EXCLUDE from portfolio
    """
    
    roe = row.get('roe', 0)
    roce = row.get('roce', 0)
    pe_ratio = row.get('pe_ratio', 999)
    fcf = row.get('fcf', 0)
    debt_equity = row.get('debt_equity', 999)
    profit_growth = row.get('profit_growth_3yr', 0)
    
    # TIER 1: CORE PORTFOLIO - Exceptional Quality
    # Criteria: ROE > 20% + ROCE > 20% + P/E < 25 + FCF > ₹500 Cr + D/E < 0.5
    if (roe > 20 and roce > 20 and pe_ratio < 25 and 
        fcf > 500 and debt_equity < 0.5):
        return 1, "CORE PORTFOLIO", "BUY / HOLD 5+ years"
    
    # TIER 2: QUALITY ADDITIONS - Good Quality
    # Criteria: ROE > 15% + ROCE > 15% + P/E < 35 + FCF > ₹100 Cr + D/E < 1.0
    if (roe > 15 and roce > 15 and pe_ratio < 35 and 
        fcf > 100 and debt_equity < 1.0):
        return 2, "QUALITY ADDITIONS", "HOLD / BUY on dips"
    
    # TIER 3: SPECIALIZED PLAYS - Mixed Quality
    # Criteria: Either ROE > 12% OR FCF > ₹1,000 Cr + Positive Growth + D/E < 1.5
    if ((roe > 12 or (fcf > 1000 and profit_growth > 0)) and 
        debt_equity < 1.5):
        return 3, "SPECIALIZED PLAYS", "HOLD / RESEARCH"
    
    # TIER 4: AVOID - Poor Quality
    # Everything else
    return 4, "AVOID", "EXCLUDE from portfolio"


def get_tier_summary(df: pd.DataFrame) -> Dict:
    """
    Get summary statistics for each investment tier
    
    Args:
        df: DataFrame with classified companies
        
    Returns:
        Dict with tier statistics
    """
    tier_stats = {}
    
    for tier in [1, 2, 3, 4]:
        tier_df = df[df['investment_tier'] == tier]
        
        if len(tier_df) > 0:
            tier_stats[tier] = {
                'count': len(tier_df),
                'avg_roe': tier_df['roe'].mean(),
                'avg_roce': tier_df['roce'].mean(),
                'avg_pe': tier_df['pe_ratio'].mean(),
                'avg_fcf': tier_df['fcf'].mean(),
                'avg_debt_equity': tier_df['debt_equity'].mean(),
                'avg_score': tier_df['composite_score'].mean(),
                'companies': tier_df['name'].tolist()[:10]  # Top 10
            }
        else:
            tier_stats[tier] = {
                'count': 0,
                'companies': []
            }
    
    return tier_stats


def add_tier_insights(row: pd.Series) -> str:
    """
    Generate tier-specific insights for a company
    
    Args:
        row: Company data
        
    Returns:
        Insight string explaining tier placement
    """
    tier = row.get('investment_tier', 4)
    tier_name = row.get('investment_tier_name', 'AVOID')
    
    roe = row.get('roe', 0)
    roce = row.get('roce', 0)
    pe_ratio = row.get('pe_ratio', 999)
    fcf = row.get('fcf', 0)
    debt_equity = row.get('debt_equity', 999)
    
    insights = []
    
    if tier == 1:
        insights.append(f"✅ Exceptional quality: ROE {roe:.1f}%, ROCE {roce:.1f}%")
        insights.append(f"✅ Strong cash generation: FCF ₹{fcf:.0f} Cr")
        insights.append(f"✅ Reasonable valuation: P/E {pe_ratio:.1f}x")
        insights.append(f"✅ Low debt: D/E {debt_equity:.2f}")
        return " | ".join(insights)
    
    elif tier == 2:
        insights.append(f"✅ Good quality: ROE {roe:.1f}%, ROCE {roce:.1f}%")
        
        if pe_ratio > 30:
            insights.append(f"⚠️ High valuation: P/E {pe_ratio:.1f}x (wait for dip)")
        else:
            insights.append(f"✅ Fair valuation: P/E {pe_ratio:.1f}x")
        
        if fcf > 500:
            insights.append(f"✅ Strong FCF: ₹{fcf:.0f} Cr")
        else:
            insights.append(f"⚠️ Moderate FCF: ₹{fcf:.0f} Cr")
        
        return " | ".join(insights)
    
    elif tier == 3:
        if roe < 12:
            insights.append(f"⚠️ Low ROE: {roe:.1f}% (below quality threshold)")
        else:
            insights.append(f"✅ Decent ROE: {roe:.1f}%")
        
        if fcf > 1000:
            insights.append(f"✅ Massive FCF: ₹{fcf:.0f} Cr (fortress balance sheet)")
        
        if debt_equity > 1.0:
            insights.append(f"⚠️ High debt: D/E {debt_equity:.2f}")
        
        insights.append("⚠️ Requires further research")
        return " | ".join(insights)
    
    else:  # Tier 4
        reasons = []
        
        if roe < 8:
            reasons.append(f"❌ Very low ROE: {roe:.1f}%")
        
        if pe_ratio > 40:
            reasons.append(f"❌ Expensive: P/E {pe_ratio:.1f}x")
        
        if fcf < 0:
            reasons.append(f"❌ Negative FCF: ₹{fcf:.0f} Cr")
        
        if debt_equity > 1.5:
            reasons.append(f"❌ High debt: D/E {debt_equity:.2f}")
        
        if not reasons:
            reasons.append("❌ Does not meet quality criteria")
        
        return " | ".join(reasons)


def get_tier_color(tier: int) -> str:
    """Get color code for tier"""
    colors = {
        1: "#10b981",  # Green - Excellent
        2: "#3b82f6",  # Blue - Good
        3: "#f59e0b",  # Orange - Caution
        4: "#ef4444"   # Red - Avoid
    }
    return colors.get(tier, "#6b7280")


def get_portfolio_recommendation(tier_stats: Dict) -> str:
    """
    Generate portfolio construction recommendation
    
    Args:
        tier_stats: Statistics for each tier
        
    Returns:
        Recommendation string
    """
    tier1_count = tier_stats.get(1, {}).get('count', 0)
    tier2_count = tier_stats.get(2, {}).get('count', 0)
    tier3_count = tier_stats.get(3, {}).get('count', 0)
    tier4_count = tier_stats.get(4, {}).get('count', 0)
    
    total = tier1_count + tier2_count + tier3_count + tier4_count
    
    recommendation = []
    
    # Tier 1 Analysis
    if tier1_count >= 5:
        recommendation.append(f"✅ Excellent: {tier1_count} CORE stocks available")
        recommendation.append(f"   → Allocate 60-70% of portfolio to these {tier1_count} stocks")
    elif tier1_count > 0:
        recommendation.append(f"⚠️ Limited: Only {tier1_count} CORE stocks found")
        recommendation.append(f"   → Allocate 40-50% to these, supplement with Tier 2")
    else:
        recommendation.append(f"❌ No CORE stocks meet criteria")
        recommendation.append(f"   → Focus on Tier 2 stocks or wait for better opportunities")
    
    # Tier 2 Analysis
    if tier2_count >= 10:
        recommendation.append(f"✅ Good: {tier2_count} QUALITY stocks available")
        recommendation.append(f"   → Allocate 20-30% to top {min(10, tier2_count)} from this tier")
    elif tier2_count > 0:
        recommendation.append(f"⚠️ Limited: {tier2_count} QUALITY stocks found")
        recommendation.append(f"   → Allocate 15-20% to these stocks")
    
    # Tier 3 Analysis
    if tier3_count > 0:
        recommendation.append(f"⚠️ Caution: {tier3_count} SPECIALIZED stocks")
        recommendation.append(f"   → Maximum 10% allocation, only after deep research")
    
    # Tier 4 Analysis
    if tier4_count > 0:
        recommendation.append(f"❌ Avoid: {tier4_count} stocks do not meet quality standards")
        recommendation.append(f"   → EXCLUDE from portfolio")
    
    # Overall Portfolio Construction
    investable = tier1_count + tier2_count
    recommendation.append(f"\n📊 Portfolio Construction:")
    recommendation.append(f"   Total Analyzed: {total} stocks")
    recommendation.append(f"   Investable (Tier 1+2): {investable} stocks ({investable/total*100:.1f}%)")
    recommendation.append(f"   Recommended Portfolio Size: {min(investable, 20)} stocks")
    
    if investable < 10:
        recommendation.append(f"\n⚠️ WARNING: Only {investable} quality stocks found")
        recommendation.append(f"   Consider expanding universe or waiting for better valuations")
    
    return "\n".join(recommendation)


def classify_all_companies(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add tier classification to all companies in DataFrame
    
    Args:
        df: DataFrame with company data
        
    Returns:
        DataFrame with tier columns added
    """
    # Apply tier classification
    tier_data = df.apply(classify_investment_tier, axis=1, result_type='expand')
    df['investment_tier'] = tier_data[0]
    df['investment_tier_name'] = tier_data[1]
    df['investment_tier_action'] = tier_data[2]
    
    # Add tier insights
    df['tier_insights'] = df.apply(add_tier_insights, axis=1)
    
    return df
