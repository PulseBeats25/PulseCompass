"""
AI-Powered Analysis Service
Uses LLM for intelligent transcript analysis with real insights
"""
import os
import re
from typing import Dict, List
import json

# Check if Ollama is available
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False


class AIAnalyzer:
    """AI-powered transcript analyzer with intelligent insights using Ollama"""
    
    def __init__(self):
        self.ollama_url = os.getenv('OLLAMA_URL', 'http://localhost:11434')
        self.ollama_model = os.getenv('OLLAMA_MODEL', 'llama3.1:8b')
        
        # Check if Ollama is running
        if REQUESTS_AVAILABLE:
            try:
                response = requests.get(f"{self.ollama_url}/api/tags", timeout=2)
                self.use_ai = response.status_code == 200
                if self.use_ai:
                    print(f"✓ Ollama connected - Using model: {self.ollama_model}")
            except Exception as e:
                print(f"✗ Ollama not available: {e}")
                self.use_ai = False
        else:
            print("✗ Requests library not available")
            self.use_ai = False
    
    def analyze_quarter_with_ai(self, text: str, quarter: str, company: str, model: str = None, temperature: float = None, max_chars: int = 0) -> Dict:
        """
        Analyze quarter transcript with AI for intelligent insights.
        Optional overrides: model, temperature, max_chars (prompt truncation).
        """
        if self.use_ai and len(text) > 500:
            return self._analyze_with_ollama(text, quarter, company, model=model, temperature=temperature, max_chars=max_chars)
        else:
            return self._analyze_with_advanced_heuristics(text, quarter, company)
    
    def _analyze_with_ollama(self, text: str, quarter: str, company: str, model: str = None, temperature: float = None, max_chars: int = 0) -> Dict:
        """Use Ollama for deep analysis"""
        
        active_model = (model or self.ollama_model)
        print(f"🤖 Analyzing {quarter} for {company} with Ollama ({active_model})...")
        
        # Truncate text to fit context window (default first 4500 chars for faster analysis)
        limit = max_chars if max_chars and max_chars > 0 else 4500
        analysis_text = text[:limit]
        
        prompt = f"""Analyze this earnings transcript and return ONLY valid JSON (no explanations):

COMPANY: {company}
QUARTER: {quarter}

TRANSCRIPT:
{analysis_text}

Return this JSON structure filled with data from the transcript above:
{{
  "financial_performance": {{
    "revenue_growth": "specific % or description",
    "margin_trend": "expanding/stable/contracting with %",
    "profitability": "detailed analysis",
    "key_metrics": ["metric 1", "metric 2"]
  }},
  "strategic_initiatives": [
    "initiative 1 with details",
    "initiative 2 with details"
  ],
  "market_position": {{
    "competitive_advantage": "description",
    "market_share": "trend and data",
    "customer_dynamics": "wins, losses, trends"
  }},
  "management_quality": {{
    "credibility_score": 85,
    "transparency": "high/medium/low with reasoning",
    "execution": "track record assessment"
  }},
  "risks_concerns": [
    "risk 1 with impact",
    "risk 2 with impact"
  ],
  "forward_guidance": [
    "specific target 1",
    "specific target 2"
  ],
  "key_insights": [
    "actionable insight 1",
    "actionable insight 2",
    "actionable insight 3"
  ],
  "investment_thesis": "2-3 sentence summary"
}}

IMPORTANT: Return ONLY the JSON object above, nothing else. No explanations, no markdown, just the JSON."""

        try:
            # Call Ollama API using chat endpoint for better structured output
            response = requests.post(
                f"{self.ollama_url}/api/chat",
                json={
                    "model": active_model,
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a financial analyst. You ONLY respond with valid JSON. Never include explanations or markdown formatting."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "stream": False,
                    "format": "json",
                    "options": {
                        "temperature": 0.1 if temperature is None else float(temperature),
                        "num_predict": 2000
                    }
                },
                timeout=180  # 3 minutes timeout for analysis
            )
            
            if response.status_code == 200:
                response_data = response.json()
                # Chat API returns message in different format
                result_text = response_data.get('message', {}).get('content', '') or response_data.get('response', '')
                print(f"✓ Ollama response received ({len(result_text)} chars)")
                
                # Extract JSON from response
                json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
                if json_match:
                    try:
                        analysis = json.loads(json_match.group())
                        print(f"✓ JSON parsed successfully")
                        
                        # Normalize all array fields that might contain objects
                        def normalize_array(arr):
                            """Convert array of objects to array of strings"""
                            normalized = []
                            for item in arr:
                                if isinstance(item, dict):
                                    # Try common patterns
                                    if 'initiative' in item and 'details' in item:
                                        normalized.append(f"{item['initiative']} - {item['details']}")
                                    elif 'initiative' in item:
                                        normalized.append(item['initiative'])
                                    elif 'insight' in item:
                                        normalized.append(item['insight'])
                                    elif 'risk' in item:
                                        normalized.append(item['risk'])
                                    elif 'guidance' in item:
                                        normalized.append(item['guidance'])
                                    else:
                                        # Fallback: join all values
                                        normalized.append(' - '.join(str(v) for v in item.values() if v))
                                else:
                                    normalized.append(str(item))
                            return normalized
                        
                        # Normalize all list fields
                        for field in ['strategic_initiatives', 'key_insights', 'risks_concerns', 'forward_guidance']:
                            if field in analysis and isinstance(analysis[field], list):
                                analysis[field] = normalize_array(analysis[field])
                        
                        return analysis
                    except json.JSONDecodeError as je:
                        print(f"✗ JSON parse error: {je}")
                        print(f"Response preview: {result_text[:500]}")
                        return self._analyze_with_advanced_heuristics(text, quarter, company)
                else:
                    print(f"✗ No JSON found in response")
                    print(f"Response preview: {result_text[:500]}")
                    return self._analyze_with_advanced_heuristics(text, quarter, company)
            else:
                print(f"✗ Ollama returned status {response.status_code}")
                return self._analyze_with_advanced_heuristics(text, quarter, company)
                
        except Exception as e:
            print(f"✗ Ollama analysis failed: {e}, falling back to heuristics")
            return self._analyze_with_advanced_heuristics(text, quarter, company)
    
    def _analyze_with_advanced_heuristics(self, text: str, quarter: str, company: str) -> Dict:
        """
        Advanced heuristic analysis with intelligent pattern matching
        """
        text_lower = text.lower()
        
        # Extract financial metrics with context
        financial_performance = self._extract_financial_metrics(text, text_lower)
        
        # Extract strategic initiatives
        strategic_initiatives = self._extract_strategic_initiatives(text, text_lower)
        
        # Analyze market position
        market_position = self._analyze_market_position(text, text_lower)
        
        # Assess management quality
        management_quality = self._assess_management_quality(text, text_lower)
        
        # Identify risks
        risks_concerns = self._identify_risks(text, text_lower)
        
        # Extract guidance
        forward_guidance = self._extract_forward_guidance(text, text_lower)
        
        # Generate insights
        key_insights = self._generate_insights(
            financial_performance, 
            strategic_initiatives, 
            market_position,
            management_quality
        )
        
        # Create investment thesis
        investment_thesis = self._create_investment_thesis(
            financial_performance,
            strategic_initiatives,
            management_quality
        )
        
        return {
            "financial_performance": financial_performance,
            "strategic_initiatives": strategic_initiatives,
            "market_position": market_position,
            "management_quality": management_quality,
            "risks_concerns": risks_concerns,
            "forward_guidance": forward_guidance,
            "key_insights": key_insights,
            "investment_thesis": investment_thesis
        }
    
    def _extract_financial_metrics(self, text: str, text_lower: str) -> Dict:
        """Extract specific financial metrics with context"""
        
        # Revenue growth patterns
        revenue_patterns = [
            r'revenue.*?(?:grew|increased|grew by|up).*?(\d+(?:\.\d+)?)\s*(?:%|percent)',
            r'(?:top|top-line|topline).*?growth.*?(\d+(?:\.\d+)?)\s*(?:%|percent)',
            r'sales.*?(?:grew|increased).*?(\d+(?:\.\d+)?)\s*(?:%|percent)'
        ]
        
        revenue_growth = "Not specified"
        for pattern in revenue_patterns:
            match = re.search(pattern, text_lower)
            if match:
                revenue_growth = f"{match.group(1)}% growth"
                break
        
        # Margin trends
        margin_patterns = [
            r'(?:ebitda|operating|net)\s+margin.*?(?:expanded|improved|increased).*?(\d+(?:\.\d+)?)\s*(?:%|percent|basis points|bps)',
            r'margin.*?(?:expanded|improved).*?(\d+(?:\.\d+)?)\s*(?:basis points|bps)',
            r'margin.*?(?:at|of|was).*?(\d+(?:\.\d+)?)\s*%'
        ]
        
        margin_trend = "Stable"
        for pattern in margin_patterns:
            match = re.search(pattern, text_lower)
            if match:
                if 'expanded' in text_lower or 'improved' in text_lower:
                    margin_trend = f"Expanding (improved by {match.group(1)} bps)"
                else:
                    margin_trend = f"At {match.group(1)}%"
                break
        
        # Profitability context
        profit_words = ['profitable', 'profitability', 'earnings', 'net income']
        profit_mentions = sum(text_lower.count(word) for word in profit_words)
        
        if profit_mentions > 10:
            profitability = "Strong focus on profitability with multiple mentions of earnings growth and margin expansion"
        elif profit_mentions > 5:
            profitability = "Moderate profitability discussion with focus on operational efficiency"
        else:
            profitability = "Limited profitability discussion in this quarter"
        
        # Key metrics mentioned
        key_metrics = []
        if 'roce' in text_lower or 'return on capital' in text_lower:
            key_metrics.append("ROCE - Return on Capital Employed")
        if 'roe' in text_lower or 'return on equity' in text_lower:
            key_metrics.append("ROE - Return on Equity")
        if 'free cash flow' in text_lower or 'fcf' in text_lower:
            key_metrics.append("Free Cash Flow generation")
        if 'working capital' in text_lower:
            key_metrics.append("Working Capital management")
        
        return {
            "revenue_growth": revenue_growth,
            "margin_trend": margin_trend,
            "profitability": profitability,
            "key_metrics": key_metrics if key_metrics else ["Standard financial metrics discussed"]
        }
    
    def _extract_strategic_initiatives(self, text: str, text_lower: str) -> List[str]:
        """Extract strategic initiatives with context"""
        initiatives = []
        
        # Digital transformation
        if text_lower.count('digital') > 5 or text_lower.count('transformation') > 3:
            digital_count = text_lower.count('digital') + text_lower.count('transformation')
            initiatives.append(f"Digital transformation initiative emphasized ({digital_count} mentions) - modernizing operations and customer experience")
        
        # AI/Technology
        ai_words = ['artificial intelligence', 'ai', 'machine learning', 'ml', 'automation']
        ai_count = sum(text_lower.count(word) for word in ai_words)
        if ai_count > 5:
            initiatives.append(f"AI and automation investments ({ai_count} mentions) - leveraging technology for competitive advantage")
        
        # New products/services
        if 'new product' in text_lower or 'product launch' in text_lower or 'new service' in text_lower:
            initiatives.append("New product/service launches mentioned - expanding portfolio and market reach")
        
        # Geographic expansion
        expansion_words = ['expansion', 'new market', 'international', 'global']
        expansion_count = sum(text_lower.count(word) for word in expansion_words)
        if expansion_count > 3:
            initiatives.append(f"Geographic/market expansion ({expansion_count} mentions) - entering new markets and regions")
        
        # M&A
        if 'acquisition' in text_lower or 'merger' in text_lower or 'acquired' in text_lower:
            initiatives.append("Inorganic growth through acquisitions - strategic M&A activity")
        
        return initiatives if initiatives else ["Standard operational initiatives discussed"]
    
    def _analyze_market_position(self, text: str, text_lower: str) -> Dict:
        """Analyze competitive position and market dynamics"""
        
        # Competitive advantage
        advantage_words = ['market leader', 'leading', 'competitive advantage', 'differentiation', 'unique']
        advantage_count = sum(text_lower.count(word) for word in advantage_words)
        
        if advantage_count > 5:
            competitive_advantage = "Strong competitive positioning with multiple references to market leadership and differentiation"
        elif advantage_count > 2:
            competitive_advantage = "Solid market position with some competitive advantages highlighted"
        else:
            competitive_advantage = "Standard competitive positioning discussed"
        
        # Market share
        if 'market share' in text_lower:
            if 'gain' in text_lower or 'increase' in text_lower or 'grew' in text_lower:
                market_share = "Gaining market share - positive competitive dynamics"
            elif 'maintain' in text_lower or 'stable' in text_lower:
                market_share = "Maintaining market share - stable competitive position"
            else:
                market_share = "Market share dynamics discussed"
        else:
            market_share = "Market share not explicitly discussed"
        
        # Customer dynamics
        customer_count = text_lower.count('customer') + text_lower.count('client')
        win_count = text_lower.count('win') + text_lower.count('won') + text_lower.count('new customer')
        
        if customer_count > 20 and win_count > 3:
            customer_dynamics = f"Strong customer focus ({customer_count} mentions) with multiple new customer wins - expanding customer base"
        elif customer_count > 10:
            customer_dynamics = f"Moderate customer focus ({customer_count} mentions) - maintaining relationships"
        else:
            customer_dynamics = "Standard customer relationship discussion"
        
        return {
            "competitive_advantage": competitive_advantage,
            "market_share": market_share,
            "customer_dynamics": customer_dynamics
        }
    
    def _assess_management_quality(self, text: str, text_lower: str) -> Dict:
        """Assess management credibility and quality"""
        
        # Positive indicators
        positive_words = ['delivered', 'achieved', 'exceeded', 'outperformed', 'successful', 'accomplished']
        positive_count = sum(text_lower.count(word) for word in positive_words)
        
        # Negative indicators
        negative_words = ['missed', 'failed', 'disappointed', 'below', 'shortfall']
        negative_count = sum(text_lower.count(word) for word in negative_words)
        
        # Calculate credibility score
        base_score = 75
        score_adjustment = (positive_count * 3) - (negative_count * 5)
        credibility_score = max(0, min(100, base_score + score_adjustment))
        
        # Transparency assessment
        risk_words = ['risk', 'challenge', 'headwind', 'uncertainty']
        risk_count = sum(text_lower.count(word) for word in risk_words)
        
        if risk_count > 8:
            transparency = "High - management openly discusses risks and challenges"
        elif risk_count > 4:
            transparency = "Medium - some risk discussion present"
        else:
            transparency = "Low - limited risk acknowledgment"
        
        # Execution assessment
        execution_words = ['execute', 'deliver', 'implement', 'achieve']
        execution_count = sum(text_lower.count(word) for word in execution_words)
        
        if execution_count > 10 and positive_count > 5:
            execution = "Strong execution track record - consistently delivering on commitments"
        elif execution_count > 5:
            execution = "Solid execution capabilities - meeting most objectives"
        else:
            execution = "Standard execution discussion"
        
        return {
            "credibility_score": credibility_score,
            "transparency": transparency,
            "execution": execution
        }
    
    def _identify_risks(self, text: str, text_lower: str) -> List[str]:
        """Identify specific risks and concerns"""
        risks = []
        
        # Macro risks
        if 'macro' in text_lower or 'economic' in text_lower or 'recession' in text_lower:
            risks.append("Macroeconomic headwinds - economic uncertainty impacting business environment")
        
        # Competition
        if 'competitive pressure' in text_lower or 'competition' in text_lower:
            risks.append("Competitive pressures - intensifying competition in key markets")
        
        # Cost inflation
        if 'cost inflation' in text_lower or 'rising costs' in text_lower or 'input costs' in text_lower:
            risks.append("Cost inflation - rising input costs pressuring margins")
        
        # Supply chain
        if 'supply chain' in text_lower and ('challenge' in text_lower or 'issue' in text_lower):
            risks.append("Supply chain challenges - disruptions impacting operations")
        
        # Regulatory
        if 'regulatory' in text_lower or 'compliance' in text_lower:
            risks.append("Regulatory considerations - compliance and regulatory changes")
        
        return risks if risks else ["Standard business risks acknowledged"]
    
    def _extract_forward_guidance(self, text: str, text_lower: str) -> List[str]:
        """Extract specific forward guidance"""
        guidance = []
        
        # Revenue guidance
        revenue_guidance = re.findall(
            r'(?:revenue|sales).*?(?:guidance|target|expect|forecast).*?(\d+(?:\.\d+)?)\s*(?:%|percent|crore|million|billion)',
            text_lower
        )
        if revenue_guidance:
            guidance.append(f"Revenue target: {revenue_guidance[0]}% growth expected")
        
        # Margin guidance
        margin_guidance = re.findall(
            r'(?:margin|ebitda).*?(?:guidance|target|expect).*?(\d+(?:\.\d+)?)\s*%',
            text_lower
        )
        if margin_guidance:
            guidance.append(f"Margin target: {margin_guidance[0]}% expected")
        
        # Capex guidance
        capex_guidance = re.findall(
            r'capex.*?(?:guidance|plan|expect).*?(\d+(?:,\d+)?)\s*(?:crore|million|billion)',
            text_lower
        )
        if capex_guidance:
            guidance.append(f"Capex plan: {capex_guidance[0]} for investments")
        
        # General outlook
        if 'optimistic' in text_lower or 'confident' in text_lower:
            guidance.append("Management expresses confidence in future performance")
        elif 'cautious' in text_lower or 'uncertain' in text_lower:
            guidance.append("Management takes cautious stance on near-term outlook")
        
        return guidance if guidance else ["General positive outlook provided"]
    
    def _generate_insights(self, financial, strategic, market, management) -> List[str]:
        """Generate actionable investment insights"""
        insights = []
        
        # Financial insight
        if "growth" in financial["revenue_growth"].lower():
            insights.append(f"Strong topline momentum: {financial['revenue_growth']} indicates robust demand environment")
        
        # Strategic insight
        if len(strategic) > 2:
            insights.append(f"Active strategic positioning: {len(strategic)} major initiatives underway to drive long-term growth")
        
        # Market insight
        if "strong" in market["competitive_advantage"].lower():
            insights.append("Competitive moat strengthening: Market leadership position provides pricing power and customer stickiness")
        
        # Management insight
        if management["credibility_score"] > 80:
            insights.append(f"High management credibility (score: {management['credibility_score']}): Track record of delivering on commitments")
        
        # Execution insight
        if "strong" in management["execution"].lower():
            insights.append("Execution excellence: Management demonstrates consistent ability to implement strategic initiatives")
        
        return insights if insights else ["Standard quarter performance with no major red flags"]
    
    def _create_investment_thesis(self, financial, strategic, management) -> str:
        """Create concise investment thesis"""
        
        # Determine overall sentiment
        positive_indicators = 0
        
        if "growth" in financial["revenue_growth"].lower():
            positive_indicators += 1
        if "expanding" in financial["margin_trend"].lower():
            positive_indicators += 1
        if len(strategic) > 2:
            positive_indicators += 1
        if management["credibility_score"] > 75:
            positive_indicators += 1
        
        if positive_indicators >= 3:
            thesis = f"Strong quarter with {financial['revenue_growth']}, expanding margins, and multiple strategic initiatives. Management demonstrates high credibility and execution capability. Positive outlook for continued performance."
        elif positive_indicators >= 2:
            thesis = f"Solid quarter with {financial['revenue_growth']} and stable operations. Strategic initiatives progressing as planned. Management maintaining steady execution."
        else:
            thesis = f"Mixed quarter with {financial['revenue_growth']}. Some operational challenges but management taking corrective actions. Monitor execution in coming quarters."
        
        return thesis
