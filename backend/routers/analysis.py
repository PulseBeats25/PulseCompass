"""
Analysis Router - Handles company analysis and semantic queries
"""
from fastapi import APIRouter, HTTPException
from typing import Optional, Dict, Any, List
from datetime import datetime

from models.schemas import (
    CompanyAnalysis,
    TranscriptSummary,
    FinancialMetrics,
    InvestorViews,
    InvestorView,
    Recommendation
)
from services.ollama_service import OllamaService
from services.recommendation_engine import RecommendationEngine
from database.supabase_client import SupabaseClient
from core.state import get_files_by_company, get_processed_files

router = APIRouter(prefix="/company", tags=["analysis"])

# Initialize services
ollama_service = OllamaService()
recommendation_engine = RecommendationEngine()


def _generate_ratings_summary(traffic_lights: Dict[str, Dict[str, Dict[str, Any]]]) -> Dict[str, str]:
    """Generate overall ratings for each category"""
    ratings = {}
    
    for category, metrics in traffic_lights.items():
        if not metrics:
            continue
            
        # Count status types
        status_counts = {'green': 0, 'yellow': 0, 'red': 0}
        for metric_data in metrics.values():
            status = metric_data.get('status', 'yellow')
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Determine overall rating
        total = sum(status_counts.values())
        if total == 0:
            ratings[category] = 'Unknown'
        elif status_counts['green'] / total >= 0.6:
            ratings[category] = ' Excellent'
        elif status_counts['red'] / total >= 0.6:
            ratings[category] = ' Poor'
        else:
            ratings[category] = ' Average'
    
    return ratings


def _analyze_temporal_transcripts(transcript_files: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Analyze multiple transcripts over time to track:
    - Promises vs. Delivery
    - Guidance accuracy
    - Management credibility
    - Trend analysis
    """
    promises_tracked = []
    credibility_score = 5.0  # Start neutral
    trends = []
    
    # Keywords for identifying promises/guidance
    promise_keywords = [
        'expect', 'guidance', 'target', 'plan', 'will', 'aim', 'goal',
        'forecast', 'project', 'anticipate', 'outlook', 'commit'
    ]
    
    delivery_keywords = [
        'achieved', 'delivered', 'met', 'exceeded', 'beat', 'reached',
        'accomplished', 'completed', 'fulfilled'
    ]
    
    miss_keywords = [
        'missed', 'below', 'short', 'disappointed', 'failed', 'lower than',
        'did not meet', 'fell short', 'underperformed'
    ]
    
    # Analyze each transcript pair (previous -> current)
    for i in range(len(transcript_files) - 1):
        prev_transcript = transcript_files[i]
        curr_transcript = transcript_files[i + 1]
        
        prev_text = prev_transcript.get('raw_text', '').lower()
        curr_text = curr_transcript.get('raw_text', '').lower()
        
        prev_analysis = prev_transcript.get('analysis', {})
        curr_analysis = curr_transcript.get('analysis', {})
        
        # Extract promises from previous transcript
        prev_guidance = prev_analysis.get('guidance', {})
        
        # Check if promises were delivered in current transcript
        for guidance_type, guidance_items in prev_guidance.items():
            if isinstance(guidance_items, list):
                for item in guidance_items:
                    item_lower = str(item).lower()
                    
                    # Check if this promise was mentioned in current transcript
                    delivered = any(keyword in curr_text and any(word in item_lower for word in item_lower.split()) 
                                  for keyword in delivery_keywords)
                    missed = any(keyword in curr_text and any(word in item_lower for word in item_lower.split()) 
                               for keyword in miss_keywords)
                    
                    status = 'delivered' if delivered else ('missed' if missed else 'unclear')
                    
                    promises_tracked.append({
                        'quarter': prev_transcript.get('filename', 'Unknown'),
                        'promise': item,
                        'category': guidance_type,
                        'status': status,
                        'next_quarter': curr_transcript.get('filename', 'Unknown')
                    })
                    
                    # Adjust credibility score
                    if status == 'delivered':
                        credibility_score += 0.5
                    elif status == 'missed':
                        credibility_score -= 1.0
        
        # Track trends
        prev_tone = prev_analysis.get('management_tone', 'neutral')
        curr_tone = curr_analysis.get('management_tone', 'neutral')
        
        if prev_tone != curr_tone:
            trends.append({
                'type': 'tone_change',
                'from': prev_tone,
                'to': curr_tone,
                'quarter': curr_transcript.get('filename', 'Unknown')
            })
    
    # Cap credibility score between 0-10
    credibility_score = max(0, min(10, credibility_score))
    
    # Generate summary
    delivered_count = sum(1 for p in promises_tracked if p['status'] == 'delivered')
    missed_count = sum(1 for p in promises_tracked if p['status'] == 'missed')
    
    summary = f"Tracked {len(promises_tracked)} promises across {len(transcript_files)} quarters. "
    if delivered_count > 0:
        summary += f"Delivered on {delivered_count} promises. "
    if missed_count > 0:
        summary += f"Missed {missed_count} targets. "
    
    delivery_rate = (delivered_count / len(promises_tracked) * 100) if promises_tracked else 0
    
    return {
        'promises_tracked': promises_tracked,
        'credibility_score': credibility_score,
        'delivery_rate': delivery_rate,
        'trends': trends,
        'summary': summary,
        'quarters_analyzed': len(transcript_files),
        'delivered_count': delivered_count,
        'missed_count': missed_count
    }


@router.get("/{company_id}/analysis", response_model=CompanyAnalysis)
async def get_company_analysis(company_id: str):
    """Get comprehensive analysis for a company based on uploaded files"""
    try:
        print(f"\n=== Starting analysis for company: {company_id} ===")
        
        # Get processed files
        all_files = get_processed_files()
        print(f"Found {len(all_files)} total processed files")
        
        if not all_files:
            error_msg = "No files have been processed yet. Please upload files first."
            print(error_msg)
            raise HTTPException(status_code=404, detail=error_msg)
        
        # Find files for this company
        company_files = {}
        for file_id, file_data in all_files.items():
            print(f"Checking file {file_id}: {file_data.get('filename')} for company {company_id}")
            if (file_data.get('company_id') == company_id or 
                company_id in ['latest', 'default-company'] or 
                not company_files):  # If no files found, use any file
                company_files[file_id] = file_data
                
        print(f"Found {len(company_files)} files for analysis")
        
        if not company_files:
            error_msg = f"No files found for company {company_id}"
            print(error_msg)
            raise HTTPException(status_code=404, detail=error_msg)
        
        if not company_files:
            # Use most recent files
            company_files = dict(list(all_files.items())[-2:]) if len(all_files) >= 2 else all_files
        
        # Separate transcript and financial data - collect ALL transcripts for temporal analysis
        transcript_files = []
        financial_data = None
        
        for file_data in company_files.values():
            if file_data['type'] == 'transcript':
                transcript_files.append(file_data)
                print(f"Found transcript: {file_data.get('filename')}")
            elif file_data['type'] == 'financial':
                financial_data = file_data
                print(f"Found financial data: {file_data.get('filename')}")
        
        # Sort transcripts by filename (assuming chronological naming)
        transcript_files.sort(key=lambda x: x.get('filename', ''))
        
        print(f"Analysis will use: {len(transcript_files)} transcript(s), Financial={'Yes' if financial_data else 'No (using defaults)'}")
        
        # Analyze multiple transcripts for temporal insights
        temporal_analysis = None
        if len(transcript_files) > 1:
            temporal_analysis = _analyze_temporal_transcripts(transcript_files)
            print(f"✨ Temporal analysis completed: {len(temporal_analysis.get('promises_tracked', []))} promises tracked")
        
        # Create transcript summary (use most recent for primary data, but include temporal insights)
        if transcript_files:
            latest_transcript = transcript_files[-1]  # Most recent
            
            # Enhance summary with temporal analysis if available
            enhanced_summary = latest_transcript['analysis'].copy()
            key_quotes = latest_transcript['analysis'].get('key_quotes', [])
            
            if temporal_analysis:
                enhanced_summary['temporal_insights'] = temporal_analysis
                enhanced_summary['management_credibility'] = temporal_analysis.get('credibility_score', 5)
                
                # Add temporal insights to key quotes for visibility
                temporal_summary = temporal_analysis.get('summary', '')
                if temporal_summary:
                    key_quotes.insert(0, f"📊 MULTI-QUARTER INSIGHT: {temporal_summary}")
                
                # Add specific promise tracking
                delivered = temporal_analysis.get('delivered_count', 0)
                missed = temporal_analysis.get('missed_count', 0)
                if delivered > 0 or missed > 0:
                    key_quotes.insert(1, f"✅ Delivered: {delivered} promises | ❌ Missed: {missed} targets")
            
            transcript_summary = TranscriptSummary(
                id=f"transcript_{company_id}",
                company_id=company_id,
                quarter="Q3",
                year=2024,
                raw_text=latest_transcript['raw_text'][:500] + "...",
                summary=enhanced_summary,
                integrity_score=latest_transcript['integrity_score'],
                key_quotes=key_quotes,
                management_tone=latest_transcript['analysis'].get('management_tone', 'neutral'),
                created_at=datetime.utcnow()
            )
        else:
            transcript_summary = TranscriptSummary(
                id=f"transcript_{company_id}",
                company_id=company_id,
                quarter="Q3",
                year=2024,
                raw_text="No transcript data available",
                summary={"key_points": "No transcript uploaded"},
                integrity_score=5,
                key_quotes=[],
                management_tone="neutral",
                created_at=datetime.utcnow()
            )
        
        # Create financial metrics with comprehensive analysis
        if financial_data:
            metrics = financial_data['metrics']
            traffic_lights = financial_data.get('traffic_lights', {})
            
            print(f"📊 Financial metrics from Excel: {list(metrics.keys())}")
            print(f"📊 Sample values: revenue={metrics.get('revenue')}, roe={metrics.get('roe')}, eps={metrics.get('eps')}")
            
            # Generate comprehensive ratings
            ratings_summary = _generate_ratings_summary(traffic_lights)
            print(f"📊 Ratings Summary: {ratings_summary}")
            
            financial_metrics = FinancialMetrics(
                id=f"financial_{company_id}",
                company_id=company_id,
                period=datetime.utcnow(),
                revenue=metrics.get('revenue', 0),
                net_profit=metrics.get('net_profit', 0),
                eps=metrics.get('eps', 0),
                roe=metrics.get('roe', 12.0),
                roce=metrics.get('roce', 14.0),
                pe_ratio=metrics.get('pe_ratio', 15.0),
                pb_ratio=metrics.get('pb_ratio', 2.5),
                debt_equity=metrics.get('debt_equity', 0.8),
                ev_ebitda=metrics.get('ev_ebitda', 10.0),
                traffic_lights=metrics.get('traffic_lights', {
                    'revenue': {'status': 'green', 'value': metrics.get('revenue', 0)},
                    'profitability': {'status': 'green', 'value': metrics.get('net_profit', 0)},
                    'debt': {'status': 'yellow' if metrics.get('debt_equity', 0.8) > 1.0 else 'green', 'value': metrics.get('debt_equity', 0.8)}
                }),
                created_at=datetime.utcnow()
            )
        else:
            ratings_summary = {}
            financial_metrics = FinancialMetrics(
                id=f"financial_{company_id}",
                company_id=company_id,
                period=datetime.utcnow(),
                revenue=1000000000,
                net_profit=100000000,
                eps=5.0,
                roe=12.0,
                roce=14.0,
                pe_ratio=15.0,
                pb_ratio=2.5,
                debt_equity=0.8,
                ev_ebitda=10.0,
                traffic_lights={
                    'revenue': {'status': 'green', 'value': 1000000000},
                    'profitability': {'status': 'green', 'value': 100000000},
                    'debt': {'status': 'green', 'value': 0.8}
                },
                created_at=datetime.utcnow()
            )
        
        # Generate recommendation
        recommendation_data = recommendation_engine.calculate_recommendation(
            transcript_data=transcript_summary.dict() if transcript_files else {},
            financial_data=financial_metrics.dict(),
            investor_views={}
        )
        
        # Enhance reasoning with temporal insights
        base_reasoning = recommendation_data.get('reasoning', 'Insufficient data for detailed analysis')
        if temporal_analysis:
            temporal_summary = temporal_analysis.get('summary', '')
            delivery_rate = temporal_analysis.get('delivery_rate', 0)
            credibility = temporal_analysis.get('credibility_score', 5)
            
            temporal_reasoning = f"\n\n📊 Multi-Quarter Analysis: {temporal_summary}"
            if delivery_rate > 70:
                temporal_reasoning += f" Management has a strong track record with {delivery_rate:.0f}% delivery rate."
            elif delivery_rate < 40:
                temporal_reasoning += f" Caution: Management has only delivered on {delivery_rate:.0f}% of promises."
            
            base_reasoning += temporal_reasoning
        
        recommendation = Recommendation(
            rating=recommendation_data.get('rating', 'HOLD'),
            confidence_score=recommendation_data.get('confidence_score', 5.0) / 10.0,  # Convert to 0-1 scale
            target_price=recommendation_data.get('target_price', 100.0),
            current_price=recommendation_data.get('current_price', 90.0),
            margin_of_safety=recommendation_data.get('margin_of_safety', 10.0),
            reasoning=base_reasoning,
            risk_factors=recommendation_data.get('risk_factors', ['Market volatility', 'Competition']),
            catalysts=recommendation_data.get('catalysts', ['Market expansion', 'Innovation'])
        )
        
        # Generate investor views
        component_scores = recommendation_data.get('component_scores', {})
        investor_views_data = recommendation_data.get('investor_views', {})
        
        # Extract metrics for investor analysis
        roe = getattr(financial_metrics, 'roe', 12.0)
        debt_equity = getattr(financial_metrics, 'debt_equity', 0.8)
        pe_ratio = getattr(financial_metrics, 'pe_ratio', 15.0)
        pb_ratio = getattr(financial_metrics, 'pb_ratio', 2.5)
        revenue_growth = financial_data.get('metrics', {}).get('revenue_growth', 0) if financial_data else 0
        
        # Create investor views
        investor_views = InvestorViews(
            warren_buffett=InvestorView(
                investor_name='Warren Buffett',
                score=float(investor_views_data.get('warren_buffett', {}).get('score', component_scores.get('financial_health', 5))),
                strengths=[f"ROE: {roe:.1f}%"] + (["Debt control"] if debt_equity <= 1.0 else []),
                concerns=["High debt levels"] if debt_equity > 1.0 else ["Market competition"],
                assessment=f"Focus on moat, ROE ({roe:.1f}%), debt control ({debt_equity:.2f})",
                key_factors={"moat": f"ROE {roe:.1f}%", "debt_control": f"{debt_equity:.2f}"},
                reasoning="Focuses on companies with durable competitive advantages and high ROE"
            ),
            benjamin_graham=InvestorView(
                investor_name='Benjamin Graham',
                score=float(investor_views_data.get('benjamin_graham', {}).get('score', component_scores.get('valuation', 5))),
                strengths=([f"P/E ratio: {pe_ratio:.1f}x"] if pe_ratio > 0 else []) + ["Balance sheet strength"],
                concerns=["Market volatility"] + (["Valuation premium"] if pe_ratio > 25 else []),
                assessment=f"Intrinsic value analysis - P/E: {pe_ratio:.1f}x, P/B: {pb_ratio:.1f}x",
                key_factors={"pe_ratio": f"{pe_ratio:.1f}x", "pb_ratio": f"{pb_ratio:.1f}x"},
                reasoning="Looks for stocks trading below intrinsic value with margin of safety"
            ),
            peter_lynch=InvestorView(
                investor_name='Peter Lynch',
                score=float(investor_views_data.get('peter_lynch', {}).get('score', component_scores.get('growth_prospects', 5))),
                strengths=([f"Revenue growth: {revenue_growth:.1f}%"] if revenue_growth > 0 else []) + ["Growth prospects"],
                concerns=["Growth sustainability"] if revenue_growth > 30 else ["Market conditions"],
                assessment=f"PEG analysis - Growth: {revenue_growth:.1f}%, P/E: {pe_ratio:.1f}x",
                key_factors={"growth": f"{revenue_growth:.1f}%", "pe_ratio": f"{pe_ratio:.1f}x"},
                reasoning="Seeks companies with strong growth potential at reasonable prices"
            ),
            charlie_munger=InvestorView(
                investor_name='Charlie Munger',
                score=float(investor_views_data.get('charlie_munger', {}).get('score', component_scores.get('management_integrity', 5))),
                strengths=[f"Management integrity: {transcript_summary.integrity_score}/10"],
                concerns=["Management execution"] if transcript_summary.integrity_score < 7 else ["Market dynamics"],
                assessment=f"Quality business analysis - Integrity: {transcript_summary.integrity_score}/10",
                key_factors={"integrity": f"{transcript_summary.integrity_score}/10"},
                reasoning="Focuses on high-quality businesses with strong management"
            ),
            consensus={
                'overall_score': float(recommendation_data.get('confidence_score', 0.5)) * 10,
                'recommendation': recommendation_data.get('rating', 'HOLD')
            }
        )
        
        # Determine company name
        company_name = "Sample Company"
        if transcript_files:
            latest_transcript = transcript_files[-1]
            company_name = latest_transcript['filename'].split(' - ')[0] if ' - ' in latest_transcript['filename'] else latest_transcript['filename'].split('.')[0]
        elif financial_data:
            company_name = financial_data['filename'].split('(')[0] if '(' in financial_data['filename'] else financial_data['filename'].split('.')[0]
        
        return CompanyAnalysis(
            company_id=company_id,
            company_name=company_name,
            transcript_summary=transcript_summary,
            financial_metrics=financial_metrics,
            investor_views=investor_views,
            recommendation=recommendation,
            ratings_summary=ratings_summary if financial_data else {},
            last_updated=datetime.utcnow()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/query")
async def semantic_query(
    query: str,
    company_id: Optional[str] = None
):
    """Perform semantic search on transcripts"""
    try:
        # Generate query embedding
        query_embedding = await ollama_service.generate_embedding(query)
        
        # Search similar transcripts
        db_client = SupabaseClient()
        results = await db_client.semantic_search(
            query_embedding=query_embedding,
            company_id=company_id,
            limit=5
        )
        
        # Generate answer using Ollama
        answer = await ollama_service.generate_answer(query, results)
        
        return {
            "query": query,
            "answer": answer,
            "sources": results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
