import requests
import json
from typing import Dict, List, Any, Optional
import asyncio
import aiohttp
from datetime import datetime

class OllamaService:
    """Service for integrating with Ollama LLM for analysis and embeddings"""
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.model = "mistral"  # Default model
        self.embedding_model = "nomic-embed-text"
        
        # Investor prompt templates
        self.investor_prompts = {
            'buffett': """
            Act as Warren Buffett analyzing this company. Focus on:
            1. Economic moat and competitive advantages
            2. Return on equity and capital efficiency
            3. Debt levels and financial conservatism
            4. Management quality and capital allocation
            5. Long-term business durability
            
            Financial Data: {financial_data}
            Transcript Summary: {transcript_data}
            
            Provide your analysis in this format:
            - Strengths: [list key strengths]
            - Concerns: [list concerns]
            - Assessment: [overall assessment]
            - Score: [1-10 score]
            """,
            
            'graham': """
            Act as Benjamin Graham analyzing this company. Focus on:
            1. Intrinsic value vs market price
            2. Margin of safety
            3. Financial strength and stability
            4. Earnings consistency
            5. Asset backing and book value
            
            Financial Data: {financial_data}
            Transcript Summary: {transcript_data}
            
            Provide your analysis in this format:
            - Value Indicators: [list value factors]
            - Risks: [list risk factors]
            - Graham Score: [1-10 score]
            - Margin of Safety: [percentage]
            """,
            
            'lynch': """
            Act as Peter Lynch analyzing this company. Focus on:
            1. PEG ratio and growth prospects
            2. The "story" of the stock
            3. Management execution capability
            4. Market opportunity and competitive position
            5. Earnings growth sustainability
            
            Financial Data: {financial_data}
            Transcript Summary: {transcript_data}
            
            Provide your analysis in this format:
            - Growth Story: [describe the investment story]
            - PEG Analysis: [PEG ratio assessment]
            - Management Execution: [execution quality]
            - Rating: [Excellent/Good/Fair/Poor]
            """,
            
            'munger': """
            Act as Charlie Munger analyzing this company. Focus on:
            1. Business quality and durability
            2. Long-term competitive advantages
            3. Management rationality and integrity
            4. Industry dynamics and future risks
            5. Circle of competence considerations
            
            Financial Data: {financial_data}
            Transcript Summary: {transcript_data}
            
            Provide your analysis in this format:
            - Business Quality: [assess business model]
            - Long-term Risks: [identify key risks]
            - Management Assessment: [evaluate leadership]
            - Durability Score: [1-10 score]
            """
        }
    
    async def health_check(self) -> bool:
        """Check if Ollama service is available"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/api/tags") as response:
                    return response.status == 200
        except Exception:
            return False
    
    async def generate_embedding(self, text: str) -> List[float]:
        """Generate embeddings for text using Ollama"""
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "model": self.embedding_model,
                    "prompt": text
                }
                
                async with session.post(
                    f"{self.base_url}/api/embeddings",
                    json=payload
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result.get("embedding", [])
                    else:
                        raise Exception(f"Embedding generation failed: {response.status}")
        except Exception as e:
            print(f"Error generating embedding: {e}")
            # Return dummy embedding for development
            return [0.0] * 1536
    
    async def generate_investor_views(
        self, 
        transcript_data: Dict[str, Any], 
        financial_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate analysis from all investor perspectives"""
        
        investor_views = {}
        
        # Prepare data summaries for prompts
        financial_summary = self._summarize_financial_data(financial_data)
        transcript_summary = self._summarize_transcript_data(transcript_data)
        
        # Generate views for each investor
        for investor, prompt_template in self.investor_prompts.items():
            try:
                prompt = prompt_template.format(
                    financial_data=financial_summary,
                    transcript_data=transcript_summary
                )
                
                analysis = await self._generate_completion(prompt)
                investor_views[investor] = self._parse_investor_analysis(investor, analysis)
                
            except Exception as e:
                print(f"Error generating {investor} view: {e}")
                investor_views[investor] = self._get_fallback_analysis(investor)
        
        # Generate consensus view
        investor_views['consensus'] = self._generate_consensus(investor_views)
        
        return investor_views
    
    async def generate_answer(self, query: str, context_documents: List[Dict]) -> str:
        """Generate answer to user query using context from transcripts"""
        
        # Prepare context from documents
        context = "\n\n".join([
            f"Document {i+1}: {doc.get('summary', doc.get('raw_text', ''))[:500]}..."
            for i, doc in enumerate(context_documents)
        ])
        
        prompt = f"""
        Based on the following company documents, answer this question: {query}
        
        Context Documents:
        {context}
        
        Provide a clear, factual answer based only on the information in the documents.
        If the information is not available, say so clearly.
        """
        
        try:
            return await self._generate_completion(prompt)
        except Exception as e:
            return f"I apologize, but I encountered an error while processing your query: {str(e)}"
    
    async def _generate_completion(self, prompt: str) -> str:
        """Generate completion using Ollama"""
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "top_p": 0.9,
                        "max_tokens": 1000
                    }
                }
                
                async with session.post(
                    f"{self.base_url}/api/generate",
                    json=payload
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result.get("response", "")
                    else:
                        raise Exception(f"Completion generation failed: {response.status}")
        except Exception as e:
            print(f"Error generating completion: {e}")
            return "Analysis temporarily unavailable due to technical issues."
    
    def _summarize_financial_data(self, financial_data: Dict[str, Any]) -> str:
        """Create a summary of financial data for LLM prompts"""
        metrics = financial_data.get('metrics', {})
        traffic_lights = financial_data.get('traffic_lights', {})
        
        summary_parts = []
        
        # Key metrics
        if metrics:
            summary_parts.append("Key Financial Metrics:")
            for metric, value in metrics.items():
                summary_parts.append(f"- {metric.replace('_', ' ').title()}: {value}")
        
        # Traffic light status
        if traffic_lights:
            summary_parts.append("\nFinancial Health Indicators:")
            for category, category_metrics in traffic_lights.items():
                summary_parts.append(f"{category.title()}:")
                for metric, data in category_metrics.items():
                    status = data.get('status', 'unknown')
                    value = data.get('value', 'N/A')
                    summary_parts.append(f"- {metric.replace('_', ' ').title()}: {value} ({status})")
        
        return "\n".join(summary_parts)
    
    def _summarize_transcript_data(self, transcript_data: Dict[str, Any]) -> str:
        """Create a summary of transcript data for LLM prompts"""
        summary_parts = []
        
        # Management guidance
        guidance = transcript_data.get('summary', {}).get('guidance', {})
        if guidance:
            summary_parts.append("Management Guidance:")
            for category, items in guidance.items():
                if items:
                    summary_parts.append(f"{category.replace('_', ' ').title()}:")
                    for item in items[:3]:  # Top 3 items per category
                        summary_parts.append(f"- {item}")
        
        # Key quotes
        key_quotes = transcript_data.get('summary', {}).get('key_quotes', [])
        if key_quotes:
            summary_parts.append("\nKey Management Quotes:")
            for quote in key_quotes[:3]:
                summary_parts.append(f"- \"{quote}\"")
        
        # Integrity score
        integrity_score = transcript_data.get('integrity_score', 0)
        summary_parts.append(f"\nManagement Integrity Score: {integrity_score}/10")
        
        # Management tone
        tone = transcript_data.get('summary', {}).get('management_tone', 'neutral')
        summary_parts.append(f"Management Tone: {tone}")
        
        return "\n".join(summary_parts)
    
    def _parse_investor_analysis(self, investor: str, analysis: str) -> Dict[str, Any]:
        """Parse LLM analysis into structured format"""
        # This is a simplified parser - in production, you'd want more robust parsing
        
        parsed = {
            'raw_analysis': analysis,
            'strengths': [],
            'concerns': [],
            'assessment': '',
            'score': 5
        }
        
        lines = analysis.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Detect sections
            if 'strengths:' in line.lower():
                current_section = 'strengths'
                continue
            elif 'concerns:' in line.lower() or 'risks:' in line.lower():
                current_section = 'concerns'
                continue
            elif 'assessment:' in line.lower():
                current_section = 'assessment'
                continue
            elif 'score:' in line.lower():
                # Extract score
                try:
                    score_text = line.lower().replace('score:', '').strip()
                    score = float(score_text.split()[0])
                    parsed['score'] = min(10, max(1, score))
                except:
                    pass
                continue
            
            # Add content to current section
            if current_section == 'strengths' and line.startswith('-'):
                parsed['strengths'].append(line[1:].strip())
            elif current_section == 'concerns' and line.startswith('-'):
                parsed['concerns'].append(line[1:].strip())
            elif current_section == 'assessment':
                parsed['assessment'] += line + ' '
        
        parsed['assessment'] = parsed['assessment'].strip()
        
        return parsed
    
    def _get_fallback_analysis(self, investor: str) -> Dict[str, Any]:
        """Provide fallback analysis when LLM is unavailable"""
        fallback_analyses = {
            'buffett': {
                'strengths': ['Analysis pending - Ollama service unavailable'],
                'concerns': ['Unable to assess without LLM analysis'],
                'assessment': 'Comprehensive analysis requires LLM service to be running',
                'score': 5
            },
            'graham': {
                'value_indicators': ['Analysis pending - Ollama service unavailable'],
                'risks': ['Unable to assess without LLM analysis'],
                'assessment': 'Value analysis requires LLM service to be running',
                'score': 5
            },
            'lynch': {
                'growth_story': 'Analysis pending - Ollama service unavailable',
                'rating': 'Pending',
                'assessment': 'Growth analysis requires LLM service to be running',
                'score': 5
            },
            'munger': {
                'business_quality': ['Analysis pending - Ollama service unavailable'],
                'longterm_risks': ['Unable to assess without LLM analysis'],
                'assessment': 'Quality analysis requires LLM service to be running',
                'score': 5
            }
        }
        
        return fallback_analyses.get(investor, {
            'assessment': 'Analysis unavailable',
            'score': 5
        })
    
    def _generate_consensus(self, investor_views: Dict[str, Any]) -> Dict[str, Any]:
        """Generate consensus view from all investor perspectives"""
        scores = []
        all_strengths = []
        all_concerns = []
        
        for investor, view in investor_views.items():
            if investor == 'consensus':
                continue
                
            score = view.get('score', 5)
            scores.append(score)
            
            strengths = view.get('strengths', [])
            concerns = view.get('concerns', [])
            
            all_strengths.extend(strengths[:2])  # Top 2 from each
            all_concerns.extend(concerns[:2])
        
        avg_score = sum(scores) / len(scores) if scores else 5
        
        # Generate recommendation based on consensus score
        if avg_score >= 8:
            recommendation = 'Strong Buy'
        elif avg_score >= 6.5:
            recommendation = 'Buy'
        elif avg_score >= 4.5:
            recommendation = 'Hold'
        else:
            recommendation = 'Avoid'
        
        return {
            'overall_score': avg_score,
            'recommendation': recommendation,
            'key_strengths': all_strengths[:5],  # Top 5 overall
            'key_concerns': all_concerns[:5],
            'investor_alignment': {
                'Value Investors': 'High' if investor_views.get('graham', {}).get('score', 5) >= 7 else 'Medium',
                'Quality Investors': 'High' if investor_views.get('buffett', {}).get('score', 5) >= 7 else 'Medium',
                'Growth Investors': 'High' if investor_views.get('lynch', {}).get('score', 5) >= 7 else 'Medium',
                'Long-term Investors': 'High' if investor_views.get('munger', {}).get('score', 5) >= 7 else 'Medium'
            }
        }
