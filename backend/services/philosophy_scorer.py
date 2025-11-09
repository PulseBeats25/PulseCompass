from typing import Dict, List, Optional

class PhilosophyScorer:
    """Service for investment philosophy-based scoring and analysis"""
    
    def __init__(self):
        self.philosophies = {
            'buffett': {
                'name': 'Warren Buffett Style',
                'description': 'Focus on high ROE, low debt, strong cash flows, and long-term value creation',
                'weights': {
                    'roe': 0.35,           # High emphasis on return on equity
                    'roce': 0.20,          # Capital efficiency
                    'debt_equity': 0.25,   # Low debt preference
                    'profit_growth': 0.10, # Moderate growth focus
                    'net_margin': 0.10     # Profitability
                },
                'key_principles': [
                    'High return on equity (>15%)',
                    'Low debt-to-equity ratio (<0.5)',
                    'Consistent profitability',
                    'Strong competitive moats',
                    'Quality management'
                ],
                'ideal_metrics': {
                    'roe': 20,
                    'roce': 18,
                    'debt_equity': 0.3,
                    'profit_growth': 15,
                    'net_margin': 15
                }
            },
            
            'graham': {
                'name': 'Benjamin Graham Style',
                'description': 'Value investing with margin of safety, strong balance sheet, and reasonable valuation',
                'weights': {
                    'debt_equity': 0.30,   # Strong balance sheet
                    'current_ratio': 0.20, # Liquidity
                    'roe': 0.20,           # Decent returns
                    'pe_ratio': 0.15,      # Reasonable valuation
                    'pb_ratio': 0.15       # Book value focus
                },
                'key_principles': [
                    'Trading below intrinsic value',
                    'Strong balance sheet (D/E < 0.5)',
                    'Current ratio > 1.5',
                    'Consistent earnings history',
                    'Margin of safety (30%+)'
                ],
                'ideal_metrics': {
                    'debt_equity': 0.3,
                    'current_ratio': 2.0,
                    'roe': 15,
                    'pe_ratio': 15,
                    'pb_ratio': 1.5
                }
            },
            
            'lynch': {
                'name': 'Peter Lynch Style',
                'description': 'Growth at reasonable price with focus on earnings growth and PEG ratio',
                'weights': {
                    'profit_growth': 0.40, # High emphasis on growth
                    'roe': 0.20,           # Good returns
                    'roce': 0.15,          # Capital efficiency
                    'peg_ratio': 0.15,     # Growth valuation
                    'debt_equity': 0.10    # Manageable debt
                },
                'key_principles': [
                    'Strong earnings growth (>15%)',
                    'Reasonable valuation (PEG < 1)',
                    'Understandable business model',
                    'Market leadership in niche',
                    'Insider ownership'
                ],
                'ideal_metrics': {
                    'profit_growth': 25,
                    'roe': 18,
                    'roce': 16,
                    'peg_ratio': 0.8,
                    'debt_equity': 0.5
                }
            },
            
            'munger': {
                'name': 'Charlie Munger Style',
                'description': 'Quality businesses with durable competitive advantages and rational management',
                'weights': {
                    'roe': 0.30,           # High returns
                    'roce': 0.30,          # Excellent capital efficiency
                    'debt_equity': 0.20,   # Conservative debt
                    'net_margin': 0.10,    # Profitability
                    'operating_margin': 0.10 # Operating efficiency
                },
                'key_principles': [
                    'High and stable ROE/ROCE',
                    'Strong competitive moats',
                    'Predictable cash flows',
                    'Quality management',
                    'Market leadership'
                ],
                'ideal_metrics': {
                    'roe': 25,
                    'roce': 22,
                    'debt_equity': 0.3,
                    'net_margin': 15,
                    'operating_margin': 18
                }
            },
            
            'growth': {
                'name': 'Growth Investing',
                'description': 'Focus on high growth companies with strong returns on capital',
                'weights': {
                    'profit_growth': 0.35, # Very high growth focus
                    'roce': 0.30,          # High capital efficiency
                    'roe': 0.25,           # Strong returns
                    'revenue_growth': 0.10 # Top-line growth
                },
                'key_principles': [
                    'High profit growth (>20%)',
                    'Excellent return on capital (>20%)',
                    'Scalable business model',
                    'Large addressable market',
                    'Innovation and disruption potential'
                ],
                'ideal_metrics': {
                    'profit_growth': 30,
                    'roce': 25,
                    'roe': 22,
                    'revenue_growth': 25
                }
            },
            
            'value': {
                'name': 'Value Investing',
                'description': 'Focus on undervalued companies with strong fundamentals and margin of safety',
                'weights': {
                    'debt_equity': 0.30,   # Strong balance sheet
                    'roe': 0.25,           # Decent returns
                    'roce': 0.20,          # Capital efficiency
                    'pe_ratio': 0.15,      # Low valuation
                    'pb_ratio': 0.10       # Book value discount
                },
                'key_principles': [
                    'Trading below intrinsic value',
                    'Strong balance sheet',
                    'Consistent cash flows',
                    'Temporary business challenges',
                    'Margin of safety (30%+)'
                ],
                'ideal_metrics': {
                    'debt_equity': 0.4,
                    'roe': 15,
                    'roce': 14,
                    'pe_ratio': 12,
                    'pb_ratio': 1.2
                }
            },
            
            'quality': {
                'name': 'Quality Investing',
                'description': 'Focus on high-quality companies with strong competitive advantages',
                'weights': {
                    'roe': 0.30,           # High returns
                    'roce': 0.30,          # Excellent capital efficiency
                    'debt_equity': 0.20,   # Conservative debt
                    'net_margin': 0.10,    # Profitability
                    'profit_growth': 0.10  # Steady growth
                },
                'key_principles': [
                    'High and stable ROE/ROCE (>20%)',
                    'Strong competitive moats',
                    'Predictable cash flows',
                    'Quality management',
                    'Market leadership'
                ],
                'ideal_metrics': {
                    'roe': 25,
                    'roce': 23,
                    'debt_equity': 0.3,
                    'net_margin': 18,
                    'profit_growth': 15
                }
            }
        }
    
    def get_philosophy_weights(self, philosophy_name: str) -> Dict[str, float]:
        """Get weights for a specific investment philosophy"""
        philosophy = self.philosophies.get(philosophy_name.lower())
        if philosophy:
            return philosophy['weights'].copy()
        return {}
    
    def get_philosophy_details(self, philosophy_name: str) -> Optional[Dict]:
        """Get detailed information about a philosophy"""
        return self.philosophies.get(philosophy_name.lower())
    
    def get_all_philosophies(self) -> Dict:
        """Get all available philosophies"""
        return {name: {
            'name': details['name'],
            'description': details['description'],
            'key_principles': details['key_principles']
        } for name, details in self.philosophies.items()}
    
    def calculate_philosophy_score(self, company_data: Dict, philosophy_name: str) -> Optional[Dict]:
        """Calculate score for a company based on philosophy weights"""
        philosophy = self.philosophies.get(philosophy_name.lower())
        if not philosophy:
            return None
        
        weights = philosophy['weights']
        ideal_metrics = philosophy['ideal_metrics']
        
        total_score = 0
        total_weight = 0
        metric_scores = {}
        
        for metric, weight in weights.items():
            value = company_data.get(metric)
            
            if value is not None and weight > 0:
                # Normalize the metric value (0-1 scale)
                normalized_value = self._normalize_metric_value(metric, value, ideal_metrics.get(metric))
                metric_score = normalized_value * 100
                
                metric_scores[metric] = {
                    'value': value,
                    'score': round(metric_score, 1),
                    'weight': weight,
                    'contribution': round(metric_score * weight, 1)
                }
                
                total_score += normalized_value * weight
                total_weight += weight
        
        if total_weight > 0:
            final_score = round((total_score / total_weight) * 100, 1)
            rank = self._get_score_rank(final_score)
            
            return {
                'score': final_score,
                'rank': rank,
                'metric_scores': metric_scores,
                'strengths': self._identify_strengths(company_data, philosophy),
                'weaknesses': self._identify_weaknesses(company_data, philosophy)
            }
        
        return None
    
    def compare_philosophies(self, company_data: Dict) -> Dict:
        """Compare how a company scores under different philosophies"""
        comparison = {}
        
        for philosophy_name, philosophy in self.philosophies.items():
            score_data = self.calculate_philosophy_score(company_data, philosophy_name)
            
            if score_data:
                comparison[philosophy_name] = {
                    'name': philosophy['name'],
                    'score': score_data['score'],
                    'rank': score_data['rank'],
                    'strengths': score_data['strengths'],
                    'weaknesses': score_data['weaknesses']
                }
        
        # Find best philosophy
        if comparison:
            best_philosophy = max(comparison.items(), key=lambda x: x[1]['score'])
            comparison['best_philosophy'] = {
                'name': best_philosophy[0],
                'score': best_philosophy[1]['score']
            }
        
        return comparison
    
    def _normalize_metric_value(self, metric: str, value: float, ideal_value: Optional[float] = None) -> float:
        """Normalize a metric value to 0-1 scale"""
        
        if metric in ['roe', 'roa', 'roce']:
            # ROE/ROA/ROCE: 0% = 0, ideal% = 1
            target = ideal_value or 20
            return min(1.0, max(0.0, value / target))
        
        elif metric in ['net_margin', 'operating_margin', 'gross_margin']:
            # Margins: 0% = 0, ideal% = 1
            target = ideal_value or 15
            return min(1.0, max(0.0, value / target))
        
        elif metric == 'debt_equity':
            # Debt/Equity: 0 = 1, 2+ = 0 (inverse - lower is better)
            target = ideal_value or 0.5
            if value <= target:
                return 1.0
            else:
                return max(0.0, 1.0 - ((value - target) / (2 - target)))
        
        elif metric in ['profit_growth', 'revenue_growth', 'eps_growth']:
            # Growth: 0% = 0, ideal% = 1
            target = ideal_value or 20
            return min(1.0, max(0.0, value / target))
        
        elif metric in ['pe_ratio', 'pb_ratio', 'ev_ebitda']:
            # Valuation: Lower is better (inverse)
            target = ideal_value or 15
            if value <= target:
                return 1.0
            else:
                return max(0.0, 1.0 - ((value - target) / (target * 2)))
        
        elif metric == 'peg_ratio':
            # PEG: <1 is ideal
            target = ideal_value or 1.0
            if value <= target:
                return 1.0
            else:
                return max(0.0, 1.0 - ((value - target) / 2))
        
        elif metric == 'current_ratio':
            # Current Ratio: 1.5-2.5 is ideal
            target = ideal_value or 2.0
            if 1.5 <= value <= 2.5:
                return 1.0
            elif value < 1.5:
                return max(0.0, value / 1.5)
            else:
                return max(0.0, 1.0 - ((value - 2.5) / 2.5))
        
        else:
            return 0.5  # Default neutral score
    
    def _get_score_rank(self, score: float) -> str:
        """Get rank label based on score"""
        if score >= 85:
            return 'Excellent'
        elif score >= 70:
            return 'Strong'
        elif score >= 55:
            return 'Good'
        elif score >= 40:
            return 'Fair'
        else:
            return 'Poor'
    
    def _identify_strengths(self, company_data: Dict, philosophy: Dict) -> List[str]:
        """Identify strengths based on philosophy weights"""
        strengths = []
        weights = philosophy['weights']
        ideal_metrics = philosophy['ideal_metrics']
        
        for metric, weight in weights.items():
            if weight > 0.15:  # High weight metrics
                value = company_data.get(metric)
                ideal = ideal_metrics.get(metric)
                
                if value is not None and ideal is not None:
                    if metric in ['roe', 'roa', 'roce'] and value >= ideal * 0.9:
                        strengths.append(f"Excellent {metric.upper()} ({value:.1f}%)")
                    elif metric in ['net_margin', 'operating_margin'] and value >= ideal * 0.9:
                        strengths.append(f"Strong {metric.replace('_', ' ').title()} ({value:.1f}%)")
                    elif metric == 'debt_equity' and value <= ideal * 1.2:
                        strengths.append(f"Low Debt/Equity ({value:.2f})")
                    elif metric in ['profit_growth', 'revenue_growth'] and value >= ideal * 0.8:
                        strengths.append(f"Strong {metric.replace('_', ' ').title()} ({value:.1f}%)")
                    elif metric in ['pe_ratio', 'pb_ratio'] and value <= ideal * 1.2:
                        strengths.append(f"Attractive {metric.upper().replace('_', '/')} ({value:.1f}x)")
        
        return strengths[:5]  # Return top 5 strengths
    
    def _identify_weaknesses(self, company_data: Dict, philosophy: Dict) -> List[str]:
        """Identify weaknesses based on philosophy weights"""
        weaknesses = []
        weights = philosophy['weights']
        ideal_metrics = philosophy['ideal_metrics']
        
        for metric, weight in weights.items():
            if weight > 0.15:  # High weight metrics
                value = company_data.get(metric)
                ideal = ideal_metrics.get(metric)
                
                if value is not None and ideal is not None:
                    if metric in ['roe', 'roa', 'roce'] and value < ideal * 0.6:
                        weaknesses.append(f"Low {metric.upper()} ({value:.1f}%)")
                    elif metric in ['net_margin', 'operating_margin'] and value < ideal * 0.6:
                        weaknesses.append(f"Weak {metric.replace('_', ' ').title()} ({value:.1f}%)")
                    elif metric == 'debt_equity' and value > ideal * 2:
                        weaknesses.append(f"High Debt/Equity ({value:.2f})")
                    elif metric in ['profit_growth', 'revenue_growth'] and value < ideal * 0.4:
                        weaknesses.append(f"Slow {metric.replace('_', ' ').title()} ({value:.1f}%)")
                    elif metric in ['pe_ratio', 'pb_ratio'] and value > ideal * 2:
                        weaknesses.append(f"High {metric.upper().replace('_', '/')} ({value:.1f}x)")
        
        return weaknesses[:5]  # Return top 5 weaknesses
