from typing import Dict, Any, List, Optional
import numpy as np
from datetime import datetime

class RecommendationEngine:
    """Generate investment recommendations based on comprehensive analysis"""
    
    def __init__(self):
        self.scoring_weights = {
            'financial_health': 0.3,
            'management_integrity': 0.2,
            'valuation': 0.25,
            'growth_prospects': 0.15,
            'risk_factors': 0.1
        }
        
        self.recommendation_thresholds = {
            'strong_buy': 8.0,
            'buy': 6.5,
            'hold': 4.5,
            'weak_hold': 3.0,
            'avoid': 0.0
        }
    
    def calculate_recommendation(
        self,
        transcript_data: Dict[str, Any],
        financial_data: Dict[str, Any],
        investor_views: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate comprehensive investment recommendation with robust error handling"""
        
        # Initialize with default values
        default_scores = {
            'financial_score': 5.0,
            'integrity_score': 5.0,
            'valuation_score': 5.0,
            'growth_score': 5.0,
            'risk_score': 5.0
        }
        
        try:
            # Safely calculate component scores with fallbacks
            financial_score = self._calculate_financial_score(financial_data) if financial_data else default_scores['financial_score']
            integrity_score = float(transcript_data.get('integrity_score', 5)) * 1.0  # Scale 1-10 to 1-10 (no change)
            valuation_score = self._calculate_valuation_score(financial_data) if financial_data else default_scores['valuation_score']
            growth_score = self._calculate_growth_score(financial_data or {}, transcript_data or {}) if financial_data or transcript_data else default_scores['growth_score']
            risk_score = self._calculate_risk_score(financial_data or {}, transcript_data or {}) if financial_data or transcript_data else default_scores['risk_score']
            
            # Ensure scores are within valid range (1-10)
            financial_score = max(1, min(10, float(financial_score or default_scores['financial_score'])))
            integrity_score = max(1, min(10, float(integrity_score or default_scores['integrity_score'])))
            valuation_score = max(1, min(10, float(valuation_score or default_scores['valuation_score'])))
            growth_score = max(1, min(10, float(growth_score or default_scores['growth_score'])))
            risk_score = max(1, min(10, float(risk_score or default_scores['risk_score'])))
            
            # Calculate weighted overall score (0-10 scale)
            overall_score = (
                financial_score * self.scoring_weights['financial_health'] +
                integrity_score * self.scoring_weights['management_integrity'] +
                valuation_score * self.scoring_weights['valuation'] +
                growth_score * self.scoring_weights['growth_prospects'] +
                (10 - risk_score) * self.scoring_weights['risk_factors']  # Invert risk score (higher risk = lower score)
            )
            
            # Ensure overall score is within valid range
            overall_score = max(1, min(10, overall_score))
            
            # Generate recommendation
            recommendation = self._get_recommendation_from_score(overall_score)
            
            # Calculate confidence score (0-10 scale, then converted to 0-1 in main.py)
            confidence_score = 7.0  # Default confidence
            
            # Adjust confidence based on data quality
            data_quality_factors = [
                len(transcript_data or {}) > 0,  # Has transcript data
                len(financial_data or {}) > 0,    # Has financial data
                financial_score != default_scores['financial_score'],  # Custom financial score
                integrity_score != default_scores['integrity_score']   # Custom integrity score
            ]
            
            # Increase confidence based on available data
            confidence_adjustment = sum(1 for factor in data_quality_factors if factor) * 0.75
            confidence_score = min(10, confidence_score + confidence_adjustment)
            
            return {
                'rating': recommendation,
                'target_price': float(financial_data.get('metrics', {}).get('target_price', 0)) if financial_data else 0,
                'current_price': float(financial_data.get('metrics', {}).get('current_price', 0)) if financial_data else 0,
                'margin_of_safety': float(financial_data.get('metrics', {}).get('margin_of_safety', 15)) if financial_data else 15,
                'confidence_score': confidence_score,  # Will be divided by 10 in main.py
                'reasoning': self._generate_reasoning(
                    overall_score=overall_score,
                    financial_score=financial_score,
                    integrity_score=integrity_score,
                    valuation_score=valuation_score,
                    growth_score=growth_score,
                    risk_score=risk_score
                ),
                'risk_factors': self._identify_risk_factors(financial_data, transcript_data),
                'catalysts': self._identify_catalysts(financial_data, transcript_data),
                'component_scores': {
                    'financial_health': financial_score,
                    'management_integrity': integrity_score,
                    'valuation': valuation_score,
                    'growth_prospects': growth_score,
                    'risk_assessment': risk_score
                }
            }
            
        except Exception as e:
            # Fallback to default recommendation if any error occurs
            print(f"Error in calculate_recommendation: {str(e)}")
            return {
                'rating': 'HOLD',
                'target_price': 0,
                'current_price': 0,
                'margin_of_safety': 15,
                'confidence_score': 5.0,  # Mid-range confidence
                'reasoning': 'Limited data available for analysis. Please ensure both financial and transcript data are provided for a complete assessment.',
                'risk_factors': ['Insufficient data for complete risk assessment'],
                'catalysts': ['N/A - Limited data'],
                'component_scores': {
                    'financial_health': default_scores['financial_score'],
                    'management_integrity': default_scores['integrity_score'],
                    'valuation': default_scores['valuation_score'],
                    'growth_prospects': default_scores['growth_score'],
                    'risk_assessment': default_scores['risk_score']
                }
            }
        
        # Calculate target price and margin of safety
        target_price = self._calculate_target_price(financial_data, overall_score)
        current_price = self._estimate_current_price(financial_data)
        margin_of_safety = ((target_price - current_price) / current_price * 100) if current_price > 0 else 0
        
        # Identify key catalysts and risks
        catalysts = self._identify_catalysts(transcript_data, financial_data)
        risk_factors = self._identify_risk_factors(transcript_data, financial_data)
        
        return {
            'rating': recommendation,
            'target_price': target_price,
            'current_price': current_price,
            'margin_of_safety': margin_of_safety,
            'confidence_score': overall_score,
            'reasoning': self._generate_reasoning(
                overall_score, financial_score, integrity_score, 
                valuation_score, growth_score, risk_score
            ),
            'risk_factors': risk_factors,
            'catalysts': catalysts,
            'component_scores': {
                'financial_health': financial_score,
                'management_integrity': integrity_score,
                'valuation': valuation_score,
                'growth_prospects': growth_score,
                'risk_assessment': risk_score,
                'overall': overall_score
            }
        }
    
    def _calculate_financial_score(self, financial_data: Dict[str, Any]) -> float:
        """Calculate financial health score from 0-10"""
        metrics = financial_data.get('metrics', financial_data.get('key_metrics', {}))
        traffic_lights = financial_data.get('traffic_lights', {})
        
        score = 5.0  # Base score
        
        # ROE scoring
        roe = metrics.get('roe', 0)
        if roe > 20:
            score += 2
        elif roe > 15:
            score += 1
        elif roe < 10:
            score -= 1
        
        # Debt scoring
        debt_equity = metrics.get('debt_equity', 1)
        if debt_equity < 0.3:
            score += 1.5
        elif debt_equity < 0.5:
            score += 0.5
        elif debt_equity > 1.5:
            score -= 2
        
        # Profitability scoring
        net_margin = metrics.get('net_margin', 0)
        if net_margin > 15:
            score += 1
        elif net_margin < 5:
            score -= 1
        
        # Current ratio scoring
        current_ratio = metrics.get('current_ratio', 1.5)
        if current_ratio > 2:
            score += 0.5
        elif current_ratio < 1.2:
            score -= 1
        
        return max(0, min(10, score))
    
    def _calculate_valuation_score(self, financial_data: Dict[str, Any]) -> float:
        """Calculate valuation attractiveness score from 0-10"""
        metrics = financial_data.get('metrics', financial_data.get('key_metrics', {}))
        
        score = 5.0  # Base score
        
        # P/E ratio scoring (lower is better for value)
        pe_ratio = metrics.get('pe_ratio', 20)
        if pe_ratio < 12:
            score += 2
        elif pe_ratio < 18:
            score += 1
        elif pe_ratio > 30:
            score -= 2
        elif pe_ratio > 25:
            score -= 1
        
        # P/B ratio scoring
        pb_ratio = metrics.get('pb_ratio', 2)
        if pb_ratio < 1.5:
            score += 1
        elif pb_ratio > 4:
            score -= 1
        
        # EV/EBITDA scoring
        ev_ebitda = metrics.get('ev_ebitda', 15)
        if ev_ebitda < 10:
            score += 1
        elif ev_ebitda > 20:
            score -= 1
        
        # PEG ratio scoring
        peg_ratio = metrics.get('peg_ratio', 1.5)
        if peg_ratio < 1:
            score += 1.5
        elif peg_ratio > 2:
            score -= 1
        
        return max(0, min(10, score))
    
    def _calculate_growth_score(self, financial_data: Dict[str, Any], transcript_data: Dict[str, Any]) -> float:
        """Calculate growth prospects score from 0-10"""
        metrics = financial_data.get('metrics', financial_data.get('key_metrics', {}))
        guidance = transcript_data.get('summary', {}).get('guidance', {})
        
        score = 5.0  # Base score
        
        # Revenue growth scoring
        revenue_growth = metrics.get('revenue_growth', 0)
        if revenue_growth > 25:
            score += 2
        elif revenue_growth > 15:
            score += 1
        elif revenue_growth < 5:
            score -= 1
        elif revenue_growth < 0:
            score -= 2
        
        # Profit growth scoring
        profit_growth = metrics.get('profit_growth', 0)
        if profit_growth > 30:
            score += 1.5
        elif profit_growth > 20:
            score += 1
        elif profit_growth < 0:
            score -= 2
        
        # Strategic initiatives from transcripts
        strategic_initiatives = guidance.get('strategic_initiatives', [])
        if len(strategic_initiatives) > 3:
            score += 1
        elif len(strategic_initiatives) > 1:
            score += 0.5
        
        # Sales projections confidence
        sales_projections = guidance.get('sales_projections', [])
        if len(sales_projections) > 2:
            score += 0.5
        
        return max(0, min(10, score))
    
    def _calculate_risk_score(self, financial_data: Dict[str, Any], transcript_data: Dict[str, Any]) -> float:
        """Calculate risk score from 0-10 (higher is less risky)"""
        metrics = financial_data.get('metrics', financial_data.get('key_metrics', {}))
        
        score = 5.0  # Base score
        
        # Debt risk
        debt_equity = metrics.get('debt_equity', 1)
        if debt_equity < 0.3:
            score += 2
        elif debt_equity < 0.5:
            score += 1
        elif debt_equity > 1.5:
            score -= 2
        elif debt_equity > 1.0:
            score -= 1
        
        # Liquidity risk
        current_ratio = metrics.get('current_ratio', 1.5)
        if current_ratio > 2:
            score += 1
        elif current_ratio < 1.2:
            score -= 2
        
        # Interest coverage risk
        interest_coverage = metrics.get('interest_coverage', 5)
        if interest_coverage > 8:
            score += 1
        elif interest_coverage < 3:
            score -= 2
        
        # Management integrity risk
        integrity_score = transcript_data.get('integrity_score', 5)
        if integrity_score >= 8:
            score += 1
        elif integrity_score < 5:
            score -= 2
        
        return max(0, min(10, score))
    
    def _get_recommendation_from_score(self, score: float) -> str:
        """Convert numerical score to recommendation"""
        if score >= self.recommendation_thresholds['strong_buy']:
            return 'Strong Buy'
        elif score >= self.recommendation_thresholds['buy']:
            return 'Buy'
        elif score >= self.recommendation_thresholds['hold']:
            return 'Hold'
        elif score >= self.recommendation_thresholds['weak_hold']:
            return 'Weak Hold'
        else:
            return 'Avoid'
    
    def _calculate_target_price(self, financial_data: Dict[str, Any], overall_score: float) -> float:
        """Calculate target price based on valuation methods"""
        metrics = financial_data.get('metrics', financial_data.get('key_metrics', {}))
        
        # Simple target price calculation
        pe_ratio = metrics.get('pe_ratio', 15)
        eps = metrics.get('eps', 10)
        
        # Adjust P/E based on quality score
        quality_multiplier = 1 + (overall_score - 5) * 0.1  # ±50% adjustment based on score
        fair_pe = pe_ratio * quality_multiplier
        
        target_price = eps * fair_pe
        
        return max(target_price, 10)  # Minimum target price
    
    def _estimate_current_price(self, financial_data: Dict[str, Any]) -> float:
        """Estimate current stock price"""
        metrics = financial_data.get('metrics', financial_data.get('key_metrics', {}))
        
        pe_ratio = metrics.get('pe_ratio', 15)
        eps = metrics.get('eps', 10)
        
        estimated_price = pe_ratio * eps
        return max(estimated_price, 10)  # Minimum price assumption
    
    def _identify_catalysts(self, transcript_data: Dict[str, Any], financial_data: Dict[str, Any]) -> List[str]:
        """Identify potential positive catalysts"""
        catalysts = []
        
        guidance = transcript_data.get('summary', {}).get('guidance', {})
        metrics = financial_data.get('metrics', financial_data.get('key_metrics', {}))
        
        # Strategic initiatives as catalysts
        strategic_initiatives = guidance.get('strategic_initiatives', [])
        for initiative in strategic_initiatives[:3]:
            catalysts.append(f"Strategic initiative: {initiative}")
        
        # Strong growth as catalyst
        revenue_growth = metrics.get('revenue_growth', 0)
        if revenue_growth > 20:
            catalysts.append(f"Strong revenue growth momentum ({revenue_growth:.1f}%)")
        
        # Margin expansion
        margin_guidance = guidance.get('margin_expectations', [])
        if margin_guidance:
            catalysts.append("Management guidance on margin expansion")
        
        # Capex investments
        capex_guidance = guidance.get('capex_investments', [])
        if capex_guidance:
            catalysts.append("Planned capacity expansion and investments")
        
        # Low debt as catalyst for growth
        debt_equity = metrics.get('debt_equity', 1)
        if debt_equity < 0.3:
            catalysts.append("Low debt provides flexibility for growth investments")
        
        return catalysts[:5]  # Top 5 catalysts
    
    def _identify_risk_factors(self, transcript_data: Dict[str, Any], financial_data: Dict[str, Any]) -> List[str]:
        """Identify key risk factors"""
        risks = []
        
        metrics = financial_data.get('metrics', financial_data.get('key_metrics', {}))
        
        # High debt risk
        debt_equity = metrics.get('debt_equity', 0)
        if debt_equity > 1.5:
            risks.append(f"High debt levels (D/E: {debt_equity:.2f}) increase financial risk")
        
        # Valuation risk
        pe_ratio = metrics.get('pe_ratio', 15)
        if pe_ratio > 35:
            risks.append(f"High P/E ratio ({pe_ratio:.1f}) suggests overvaluation risk")
        
        # Low profitability risk
        roe = metrics.get('roe', 0)
        if roe < 10:
            risks.append(f"Low ROE ({roe:.1f}%) indicates weak profitability")
        
        # Liquidity risk
        current_ratio = metrics.get('current_ratio', 1.5)
        if current_ratio < 1.2:
            risks.append(f"Low current ratio ({current_ratio:.2f}) suggests liquidity concerns")
        
        # Management integrity risk
        integrity_score = transcript_data.get('integrity_score', 5)
        if integrity_score < 6:
            risks.append(f"Management integrity concerns (score: {integrity_score}/10)")
        
        # Growth sustainability risk
        revenue_growth = metrics.get('revenue_growth', 0)
        if revenue_growth > 40:
            risks.append("Very high growth rate may not be sustainable")
        
        return risks[:5]  # Top 5 risks
    
    def _generate_reasoning(
        self,
        overall_score: float,
        financial_score: float,
        integrity_score: float,
        valuation_score: float,
        growth_score: float,
        risk_score: float
    ) -> str:
        """Generate reasoning for the recommendation"""
        
        reasoning_parts = []
        
        # Overall assessment
        if overall_score >= 8:
            reasoning_parts.append("This is a high-quality investment opportunity with strong fundamentals.")
        elif overall_score >= 6.5:
            reasoning_parts.append("This represents a solid investment with good risk-reward characteristics.")
        elif overall_score >= 4.5:
            reasoning_parts.append("This is a fair investment with balanced pros and cons.")
        else:
            reasoning_parts.append("This investment has significant concerns that outweigh the positives.")
        
        # Financial health
        if financial_score >= 7:
            reasoning_parts.append("The company demonstrates excellent financial health with strong profitability and conservative debt levels.")
        elif financial_score < 4:
            reasoning_parts.append("Financial health concerns include weak profitability or high debt levels.")
        
        # Management integrity
        if integrity_score >= 8:
            reasoning_parts.append("Management has demonstrated high integrity and reliable guidance.")
        elif integrity_score < 5:
            reasoning_parts.append("Management integrity concerns may affect future performance.")
        
        # Valuation
        if valuation_score >= 7:
            reasoning_parts.append("The stock appears undervalued based on multiple valuation metrics.")
        elif valuation_score < 4:
            reasoning_parts.append("Valuation appears stretched relative to fundamentals.")
        
        # Growth prospects
        if growth_score >= 7:
            reasoning_parts.append("Strong growth prospects supported by strategic initiatives.")
        elif growth_score < 4:
            reasoning_parts.append("Limited growth visibility raises concerns about future performance.")
        
        # Risk assessment
        if risk_score >= 7:
            reasoning_parts.append("Risk profile is manageable with strong balance sheet fundamentals.")
        elif risk_score < 4:
            reasoning_parts.append("Elevated risk factors require careful monitoring.")
        
        return " ".join(reasoning_parts)