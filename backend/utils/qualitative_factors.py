"""
Qualitative Factors Framework for Stock Analysis
This module provides a structure for incorporating qualitative factors into rankings
"""
from typing import Dict, List, Optional
from enum import Enum
import pandas as pd


class MoatStrength(Enum):
    """Economic moat strength categories"""
    NONE = 0
    NARROW = 1
    WIDE = 2


class IndustryTrend(Enum):
    """Industry trend categories"""
    DECLINING = -1
    STABLE = 0
    GROWING = 1
    BOOMING = 2


class ManagementQuality(Enum):
    """Management quality assessment"""
    POOR = 0
    AVERAGE = 1
    GOOD = 2
    EXCELLENT = 3


class QualitativeFactors:
    """
    Framework for qualitative assessment of companies
    
    Future implementation will include:
    - Economic moat analysis (brand, network effects, cost advantages, switching costs)
    - Industry trends and positioning
    - Management quality and track record
    - Competitive landscape analysis
    - Regulatory environment
    - ESG factors
    """
    
    def __init__(self):
        self.moat_indicators = {
            'brand_strength': ['market_share', 'brand_recognition', 'pricing_power'],
            'network_effects': ['user_base_growth', 'platform_stickiness'],
            'cost_advantages': ['scale_economies', 'proprietary_tech', 'location'],
            'switching_costs': ['customer_retention', 'integration_depth']
        }
        
        self.industry_indicators = {
            'growth_trends': ['market_size_growth', 'adoption_rate', 'innovation_pace'],
            'competitive_intensity': ['market_concentration', 'entry_barriers', 'price_competition'],
            'regulatory_environment': ['compliance_burden', 'policy_support', 'regulatory_risk']
        }
        
        self.management_indicators = {
            'track_record': ['historical_performance', 'strategic_decisions', 'capital_allocation'],
            'transparency': ['disclosure_quality', 'communication', 'governance'],
            'alignment': ['insider_ownership', 'compensation_structure', 'shareholder_focus']
        }
    
    def assess_economic_moat(self, company_data: Dict) -> Dict:
        """
        Assess economic moat strength based on available data
        
        Args:
            company_data: Dictionary with company metrics and qualitative info
            
        Returns:
            Dict with moat assessment and contributing factors
        """
        moat_score = 0.0
        factors = []
        
        # Brand strength indicators (from financial metrics)
        if 'opm' in company_data and company_data['opm'] > 20:
            moat_score += 0.3
            factors.append('High operating margins suggest pricing power')
        
        # Customer retention (from consistent revenue growth)
        if 'sales_growth_5yr' in company_data and company_data['sales_growth_5yr'] > 15:
            moat_score += 0.2
            factors.append('Consistent revenue growth indicates customer loyalty')
        
        # Scale advantages (from asset turnover and market cap)
        if 'asset_turnover' in company_data and company_data['asset_turnover'] > 1.5:
            moat_score += 0.2
            factors.append('High asset efficiency suggests operational advantages')
        
        # Return on capital consistency
        if 'roce' in company_data and company_data['roce'] > 20:
            moat_score += 0.3
            factors.append('High ROCE indicates sustainable competitive advantage')
        
        # Determine moat strength
        if moat_score >= 0.7:
            strength = MoatStrength.WIDE
        elif moat_score >= 0.4:
            strength = MoatStrength.NARROW
        else:
            strength = MoatStrength.NONE
        
        return {
            'strength': strength.name,
            'score': moat_score,
            'factors': factors,
            'description': self._get_moat_description(strength)
        }
    
    def assess_industry_position(self, company_data: Dict, sector: Optional[str] = None) -> Dict:
        """
        Assess company's position within its industry
        
        Args:
            company_data: Dictionary with company metrics
            sector: Industry/sector classification
            
        Returns:
            Dict with industry position assessment
        """
        position_score = 0.0
        insights = []
        
        # Growth trajectory
        if 'profit_growth_5yr' in company_data:
            growth = company_data['profit_growth_5yr']
            if growth > 25:
                position_score += 0.4
                insights.append('Strong profit growth indicates market share gains')
                trend = IndustryTrend.BOOMING
            elif growth > 15:
                position_score += 0.3
                insights.append('Solid growth trajectory')
                trend = IndustryTrend.GROWING
            elif growth > 5:
                position_score += 0.1
                trend = IndustryTrend.STABLE
            else:
                trend = IndustryTrend.DECLINING
        else:
            trend = IndustryTrend.STABLE
        
        # Market position (from market cap and returns)
        if 'market_cap' in company_data and company_data['market_cap'] > 10000:
            position_score += 0.3
            insights.append('Large market cap indicates market leadership')
        
        # Competitive resilience (from margins and returns)
        if 'return_3yr' in company_data and company_data['return_3yr'] > 20:
            position_score += 0.3
            insights.append('Strong returns suggest competitive resilience')
        
        return {
            'trend': trend.name,
            'position_score': position_score,
            'insights': insights,
            'sector': sector or 'Unknown'
        }
    
    def assess_management_quality(self, company_data: Dict) -> Dict:
        """
        Assess management quality based on financial performance and capital allocation
        
        Args:
            company_data: Dictionary with company metrics
            
        Returns:
            Dict with management quality assessment
        """
        quality_score = 0.0
        indicators = []
        
        # Capital allocation efficiency (ROE and ROCE)
        if 'roe' in company_data and 'roce' in company_data:
            avg_return = (company_data['roe'] + company_data['roce']) / 2
            if avg_return > 25:
                quality_score += 0.4
                indicators.append('Excellent capital allocation (high ROE/ROCE)')
            elif avg_return > 15:
                quality_score += 0.3
                indicators.append('Good capital allocation')
        
        # Cash flow generation (FCF conversion)
        if 'fcf' in company_data and 'pat' in company_data:
            if company_data['pat'] > 0:
                fcf_conversion = company_data['fcf'] / company_data['pat']
                if fcf_conversion > 0.8:
                    quality_score += 0.3
                    indicators.append('Strong cash flow generation')
        
        # Debt management
        if 'debt_equity' in company_data:
            if company_data['debt_equity'] < 0.5:
                quality_score += 0.3
                indicators.append('Conservative debt management')
        
        # Determine quality level
        if quality_score >= 0.8:
            quality = ManagementQuality.EXCELLENT
        elif quality_score >= 0.6:
            quality = ManagementQuality.GOOD
        elif quality_score >= 0.3:
            quality = ManagementQuality.AVERAGE
        else:
            quality = ManagementQuality.POOR
        
        return {
            'quality': quality.name,
            'score': quality_score,
            'indicators': indicators
        }
    
    def _get_moat_description(self, strength: MoatStrength) -> str:
        """Get description for moat strength"""
        descriptions = {
            MoatStrength.WIDE: "Strong competitive advantages that protect market position",
            MoatStrength.NARROW: "Some competitive advantages but vulnerable to disruption",
            MoatStrength.NONE: "Limited competitive advantages, commodity-like business"
        }
        return descriptions.get(strength, "Unknown")
    
    def generate_qualitative_report(self, company_data: Dict, sector: Optional[str] = None) -> Dict:
        """
        Generate comprehensive qualitative assessment report
        
        Args:
            company_data: Dictionary with company metrics
            sector: Industry/sector classification
            
        Returns:
            Complete qualitative assessment
        """
        moat = self.assess_economic_moat(company_data)
        industry = self.assess_industry_position(company_data, sector)
        management = self.assess_management_quality(company_data)
        
        # Calculate overall qualitative score
        overall_score = (moat['score'] * 0.4 + 
                        industry['position_score'] * 0.3 + 
                        management['score'] * 0.3)
        
        return {
            'overall_score': overall_score,
            'moat_assessment': moat,
            'industry_position': industry,
            'management_quality': management,
            'recommendation': self._generate_recommendation(overall_score, moat, industry, management)
        }
    
    def _generate_recommendation(self, score: float, moat: Dict, industry: Dict, management: Dict) -> str:
        """Generate investment recommendation based on qualitative factors"""
        if score >= 0.7:
            return f"Strong qualitative profile with {moat['strength'].lower()} moat and {management['quality'].lower()} management"
        elif score >= 0.5:
            return f"Decent qualitative profile but monitor {industry['trend'].lower()} industry trends"
        else:
            return "Weak qualitative profile - requires deeper due diligence"


# Singleton instance
qualitative_analyzer = QualitativeFactors()
