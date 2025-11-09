from fastapi import FastAPI, UploadFile, File, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from typing import List, Optional
import os
import tempfile
import shutil
from datetime import datetime
from dotenv import load_dotenv

from models.schemas import (
    UploadResponse,
    CompanyAnalysis,
    TranscriptSummary,
    FinancialMetrics,
    InvestorViews,
    InvestorView,
    Recommendation
)
from services.pdf_parser import PDFParser
from services.excel_parser import ExcelParser
from services.ollama_service import OllamaService
from services.recommendation_engine import RecommendationEngine
from database.supabase_client import SupabaseClient

# Load environment variables
load_dotenv()

app = FastAPI(
    title="PulseCompass API",
    description="Advanced Stock Market Analysis Backend",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
pdf_parser = PDFParser()
excel_parser = ExcelParser()
ollama_service = OllamaService()
recommendation_engine = RecommendationEngine()
db_client = SupabaseClient()

@app.get("/")
async def root():
    return {"message": "PulseCompass API is running"}

@app.post("/test-upload")
async def test_upload(file: UploadFile = File(...)):
    """Simple test endpoint to verify upload functionality"""
    try:
        content = await file.read()
        return {
            "success": True,
            "filename": file.filename,
            "size": len(content),
            "content_type": file.content_type,
            "message": "Upload test successful"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Upload test failed"
        }

@app.post("/upload/pdf", response_model=UploadResponse)
async def upload_pdf(
    files: List[UploadFile] = File(...),
    company_id: Optional[str] = None
):
    """Upload and process PDF transcript files"""
    try:
        results = []
        
        for file in files:
            if not file.filename.endswith('.pdf'):
                raise HTTPException(status_code=400, detail=f"File {file.filename} is not a PDF")
            
            # Read file content
            content = await file.read()
            
            # Actually process the PDF
            try:
                raw_text = pdf_parser.extract_text(content)
                analysis = pdf_parser.analyze_transcript(raw_text)
                integrity_score = pdf_parser.calculate_integrity_score(raw_text, analysis)
                
                file_id = f"pdf_{len(results) + 1}"
                
                # Store processed data in session/memory for analysis endpoint
                if not hasattr(app.state, 'processed_files'):
                    app.state.processed_files = {}
                
                app.state.processed_files[file_id] = {
                    'type': 'transcript',
                    'filename': file.filename,
                    'raw_text': raw_text,
                    'analysis': analysis,
                    'integrity_score': integrity_score,
                    'company_id': company_id
                }
                
                results.append({
                    "file_id": file_id,
                    "filename": file.filename,
                    "status": "processed",
                    "integrity_score": integrity_score
                })
                
            except Exception as parse_error:
                # Still create a basic entry even if processing fails
                file_id = f"pdf_{len(results) + 1}"
                
                if not hasattr(app.state, 'processed_files'):
                    app.state.processed_files = {}
                
                app.state.processed_files[file_id] = {
                    'type': 'transcript',
                    'filename': file.filename,
                    'raw_text': 'PDF processing failed',
                    'analysis': {'key_quotes': [], 'management_tone': 'neutral'},
                    'integrity_score': 5,
                    'company_id': company_id,
                    'error': str(parse_error)
                }
                
                results.append({
                    "file_id": file_id,
                    "filename": file.filename,
                    "status": "processed_with_errors",
                    "integrity_score": 5,
                    "error": str(parse_error)
                })
        
        return UploadResponse(
            success=True,
            message=f"Successfully processed {len(files)} PDF files",
            files=results
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload/excel", response_model=UploadResponse)
async def upload_excel(
    files: List[UploadFile] = File(...),
    company_id: Optional[str] = None
):
    """Upload and process Excel/CSV financial data files"""
    try:
        results = []
        
        for file in files:
            if not any(file.filename.endswith(ext) for ext in ['.xlsx', '.xls', '.csv']):
                raise HTTPException(status_code=400, detail=f"File {file.filename} is not supported")
            
            # Read file content
            content = await file.read()
            
            # Actually process the Excel file
            try:
                financial_data = excel_parser.parse_financial_data(content, file.filename)
                metrics = excel_parser.calculate_metrics(financial_data)
                traffic_lights = excel_parser.generate_traffic_lights(metrics)
                
                file_id = f"excel_{len(results) + 1}"
                
                # Store processed data in session/memory for analysis endpoint
                if not hasattr(app.state, 'processed_files'):
                    app.state.processed_files = {}
                
                app.state.processed_files[file_id] = {
                    'type': 'financial',
                    'filename': file.filename,
                    'financial_data': financial_data,
                    'metrics': metrics,
                    'traffic_lights': traffic_lights,
                    'company_id': company_id
                }
                
                results.append({
                    "file_id": file_id,
                    "filename": file.filename,
                    "status": "processed",
                    "metrics_count": len(metrics)
                })
                
            except Exception as parse_error:
                # Still create a basic entry even if processing fails
                file_id = f"excel_{len(results) + 1}"
                
                if not hasattr(app.state, 'processed_files'):
                    app.state.processed_files = {}
                
                default_metrics = excel_parser._get_default_metrics()
                default_traffic_lights = excel_parser.generate_traffic_lights(default_metrics)
                
                app.state.processed_files[file_id] = {
                    'type': 'financial',
                    'filename': file.filename,
                    'financial_data': {'raw_dataframe': [], 'columns': []},
                    'metrics': default_metrics,
                    'traffic_lights': default_traffic_lights,
                    'company_id': company_id,
                    'error': str(parse_error)
                }
                
                results.append({
                    "file_id": file_id,
                    "filename": file.filename,
                    "status": "processed_with_errors",
                    "metrics_count": len(default_metrics),
                    "error": str(parse_error)
                })
        
        return UploadResponse(
            success=True,
            message=f"Successfully processed {len(files)} financial files",
            files=results
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/company/{company_id}/analysis", response_model=CompanyAnalysis)
async def get_company_analysis(company_id: str):
    """Get comprehensive analysis for a company based on uploaded files"""
    try:
        # Get processed files from app state
        if not hasattr(app.state, 'processed_files') or not app.state.processed_files:
            raise HTTPException(status_code=404, detail="No files have been processed yet. Please upload files first.")
        
        # Find files for this company
        company_files = {k: v for k, v in app.state.processed_files.items() 
                        if v.get('company_id') == company_id or company_id == 'latest' or company_id == 'default-company'}
        
        if not company_files:
            # If no specific company files, use the most recent files
            company_files = dict(list(app.state.processed_files.items())[-2:]) if len(app.state.processed_files) >= 2 else app.state.processed_files
        
        # Separate transcript and financial data
        transcript_data = None
        financial_data = None
        
        for file_data in company_files.values():
            if file_data['type'] == 'transcript':
                transcript_data = file_data
            elif file_data['type'] == 'financial':
                financial_data = file_data
        
        # Create transcript summary from actual data or default
        if transcript_data:
            transcript_summary = TranscriptSummary(
                id=f"transcript_{company_id}",
                company_id=company_id,
                quarter="Q3",
                year=2024,
                raw_text=transcript_data['raw_text'][:500] + "...",  # Truncate for response
                summary=transcript_data['analysis'],
                integrity_score=transcript_data['integrity_score'],
                key_quotes=transcript_data['analysis'].get('key_quotes', []),
                management_tone=transcript_data['analysis'].get('management_tone', 'neutral'),
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
        
        # Create financial metrics from actual data or default
        if financial_data:
            metrics = financial_data['metrics']
            financial_metrics = FinancialMetrics(
                id=f"financial_{company_id}",
                company_id=company_id,
                period=datetime.utcnow(),
                revenue=metrics.get('revenue', 0),
                net_profit=metrics.get('net_profit', 0),
                eps=metrics.get('eps', 0),
                roe=metrics.get('roe', 12.0),
                roce=metrics.get('roce', 14.0),
                debt_equity=metrics.get('debt_equity', 0.4),
                pe_ratio=metrics.get('pe_ratio', 20.0),
                ev_ebitda=metrics.get('ev_ebitda', 12.0),
                pb_ratio=metrics.get('pb_ratio', 2.5),
                traffic_lights=financial_data['traffic_lights'],
                created_at=datetime.utcnow()
            )
        else:
            financial_metrics = FinancialMetrics(
                id=f"financial_{company_id}",
                company_id=company_id,
                period=datetime.utcnow(),
                revenue=0,
                net_profit=0,
                eps=0,
                roe=12.0,
                roce=14.0,
                debt_equity=0.4,
                pe_ratio=20.0,
                ev_ebitda=12.0,
                pb_ratio=2.5,
                traffic_lights={},
                created_at=datetime.utcnow()
            )
        
        # Generate recommendation based on actual data
        transcript_dict = {
            'integrity_score': transcript_summary.integrity_score,
            'summary': transcript_summary.summary
        }
        
        financial_dict = {
            'metrics': {
                'roe': financial_metrics.roe,
                'roce': financial_metrics.roce,
                'debt_equity': financial_metrics.debt_equity,
                'pe_ratio': financial_metrics.pe_ratio,
                'ev_ebitda': financial_metrics.ev_ebitda,
                'eps': financial_metrics.eps,
                'revenue_growth': financial_data['metrics'].get('revenue_growth', 0) if financial_data else 0,
                'profit_growth': financial_data['metrics'].get('profit_growth', 0) if financial_data else 0,
                'net_margin': financial_data['metrics'].get('net_margin', 0) if financial_data else 0,
                'current_ratio': financial_data['metrics'].get('current_ratio', 1.5) if financial_data else 1.5
            },
            'traffic_lights': financial_metrics.traffic_lights
        }
        
        # Generate actual recommendation using the recommendation engine
        try:
            recommendation_data = recommendation_engine.calculate_recommendation(
                transcript_dict, financial_dict, {}
            )
            
            # Ensure confidence_score is a valid number between 0 and 1
            confidence_score = 0.5  # Default value
            try:
                confidence_score = float(recommendation_data.get('confidence_score', 5)) / 10.0
                confidence_score = max(0.0, min(1.0, confidence_score))  # Clamp between 0 and 1
            except (TypeError, ValueError):
                pass
                
        except Exception as e:
            print(f"Error in recommendation engine: {str(e)}")
            # Fallback to default recommendation if there's an error
            recommendation_data = {
                'rating': 'HOLD',
                'target_price': float(financial_dict.get('metrics', {}).get('current_price', 0)) * 1.1 if financial_data else 0,
                'current_price': float(financial_dict.get('metrics', {}).get('current_price', 0)) if financial_data else 0,
                'margin_of_safety': 0.2,
                'confidence_score': 0.5,
                'reasoning': 'Analysis could not be completed. ' + str(e),
                'risk_factors': ['Analysis error occurred'],
                'catalysts': ['None identified']
            }
            confidence_score = 0.5
            
        recommendation = Recommendation(
            rating=recommendation_data.get('rating', 'HOLD'),
            target_price=float(recommendation_data.get('target_price', 0)),
            current_price=float(recommendation_data.get('current_price', 0)),
            margin_of_safety=float(recommendation_data.get('margin_of_safety', 0)) / 100.0,  # Convert to decimal
            confidence_score=confidence_score,  # Already in 0-1 scale
            reasoning=recommendation_data.get('reasoning', 'No analysis available'),
            risk_factors=recommendation_data.get('risk_factors', []),
            catalysts=recommendation_data.get('catalysts', [])
        )
        
        # Get component scores with fallbacks
        component_scores = recommendation_data.get('component_scores', {
            'financial_health': 5.0,
            'management_integrity': 5.0,
            'valuation': 5.0,
            'growth_prospects': 5.0,
            'risk_assessment': 5.0
        })
        
        # Get financial metrics with fallbacks
        roe = getattr(financial_metrics, 'roe', 0)
        debt_equity = getattr(financial_metrics, 'debt_equity', 0)
        pe_ratio = getattr(financial_metrics, 'pe_ratio', 0)
        pb_ratio = getattr(financial_metrics, 'pb_ratio', 0)
        revenue_growth = financial_dict.get('metrics', {}).get('revenue_growth', 0) if financial_data else 0
        
        # Generate investor views using the actual analysis results
        investor_views_data = recommendation_data.get('investor_views', {})
        
        # Get the actual analysis from the recommendation data or use the component scores as fallback
        buffett_analysis = investor_views_data.get('warren_buffett', {
            'score': min(10, max(1, component_scores.get('financial_health', 5))),
            'reasoning': "Focuses on companies with durable competitive advantages, high return on equity, and manageable debt levels."
        })
        
        graham_analysis = investor_views_data.get('benjamin_graham', {
            'score': min(10, max(1, component_scores.get('valuation', 5))),
            'reasoning': "Looks for stocks trading below their intrinsic value with a margin of safety."
        })
        
        lynch_analysis = investor_views_data.get('peter_lynch', {
            'score': min(10, max(1, component_scores.get('growth_prospects', 5))),
            'reasoning': "Seeks companies with strong growth potential at reasonable prices (PEG ratio)."
        })
        
        munger_analysis = investor_views_data.get('charlie_munger', {
            'score': min(10, max(1, component_scores.get('management_integrity', 5))),
            'reasoning': "Focuses on high-quality businesses with strong management and durable competitive advantages."
        })
        
        # Create investor view models with actual analysis data
        investor_views = InvestorViews(
            warren_buffett=InvestorView(
                investor_name='Warren Buffett',
                score=float(buffett_analysis.get('score', 5)),
                strengths=buffett_analysis.get('strengths', [f"ROE: {roe:.1f}%"] + (["Debt control"] if debt_equity <= 1.0 else [])),
                concerns=buffett_analysis.get('concerns', ["High debt levels"] if debt_equity > 1.0 else ["Market competition"]),
                assessment=buffett_analysis.get('assessment', f"Focus on moat, ROE ({roe:.1f}%), debt control ({debt_equity:.2f})" if financial_data else "Insufficient financial data"),
                key_factors=buffett_analysis.get('key_factors', {"moat": f"ROE {roe:.1f}%", "debt_control": f"{debt_equity:.2f}", "score": f"{float(buffett_analysis.get('score', 5)):.1f}/10"}),
                reasoning=buffett_analysis.get('reasoning', "Focuses on companies with durable competitive advantages, high return on equity, and manageable debt levels.")
            ),
            benjamin_graham=InvestorView(
                investor_name='Benjamin Graham',
                score=float(graham_analysis.get('score', 5)),
                strengths=graham_analysis.get('strengths', ([f"P/E ratio: {pe_ratio:.1f}x"] if pe_ratio > 0 else []) + ["Balance sheet strength"]),
                concerns=graham_analysis.get('concerns', ["Market volatility"] + (["Valuation premium"] if pe_ratio > 25 else [])),
                assessment=graham_analysis.get('assessment', f"Intrinsic value analysis - P/E: {pe_ratio:.1f}x, P/B: {pb_ratio:.1f}x" if financial_data else "Valuation data not available"),
                key_factors=graham_analysis.get('key_factors', {"pe_ratio": f"{pe_ratio:.1f}x", "pb_ratio": f"{pb_ratio:.1f}x", "score": f"{float(graham_analysis.get('score', 5)):.1f}/10"}),
                reasoning=graham_analysis.get('reasoning', "Looks for stocks trading below their intrinsic value with a margin of safety.")
            ),
            peter_lynch=InvestorView(
                investor_name='Peter Lynch',
                score=float(lynch_analysis.get('score', 5)),
                strengths=lynch_analysis.get('strengths', ([f"Revenue growth: {revenue_growth:.1f}%"] if revenue_growth > 0 else []) + ["Growth prospects"]),
                concerns=lynch_analysis.get('concerns', ["Growth sustainability"] if revenue_growth > 30 else ["Market conditions"]),
                assessment=lynch_analysis.get('assessment', f"PEG analysis - Growth: {revenue_growth:.1f}%, P/E: {pe_ratio:.1f}x" if financial_data else "Growth data not available"),
                key_factors=lynch_analysis.get('key_factors', {"growth": f"{revenue_growth:.1f}%", "pe_ratio": f"{pe_ratio:.1f}x", "score": f"{float(lynch_analysis.get('score', 5)):.1f}/10"}),
                reasoning=lynch_analysis.get('reasoning', "Seeks companies with strong growth potential at reasonable prices (PEG ratio).")
            ),
            charlie_munger=InvestorView(
                investor_name='Charlie Munger',
                score=float(munger_analysis.get('score', 5)),
                strengths=munger_analysis.get('strengths', [f"Management integrity: {transcript_summary.integrity_score}/10"] + (["Business quality"] if transcript_data else [])),
                concerns=munger_analysis.get('concerns', ["Management execution"] if transcript_summary.integrity_score < 7 else ["Market dynamics"]),
                assessment=munger_analysis.get('assessment', 
                    f"Quality business analysis - Integrity: {transcript_summary.integrity_score}/10" + 
                    (f", Tone: {transcript_summary.management_tone}" if hasattr(transcript_summary, 'management_tone') else "") 
                    if transcript_data else "Transcript data not analyzed"
                ),
                key_factors=munger_analysis.get('key_factors', {
                    "integrity": f"{transcript_summary.integrity_score}/10", 
                    "tone": getattr(transcript_summary, 'management_tone', 'neutral'),
                    "score": f"{float(munger_analysis.get('score', 5)):.1f}/10"
                }),
                reasoning=munger_analysis.get('reasoning', "Focuses on high-quality businesses with strong management and durable competitive advantages.")
            ),
            consensus={
                'overall_score': float(recommendation_data.get('confidence_score', 0.5)) * 10,  # Convert to 0-100 scale
                'recommendation': recommendation_data.get('rating', 'HOLD')
            }
        )
        
        # Determine company name from filename or use default
        company_name = "Sample Company"
        if transcript_data:
            company_name = transcript_data['filename'].split(' - ')[0] if ' - ' in transcript_data['filename'] else transcript_data['filename'].split('.')[0]
        elif financial_data:
            company_name = financial_data['filename'].split('(')[0] if '(' in financial_data['filename'] else financial_data['filename'].split('.')[0]
        
        return CompanyAnalysis(
            company_id=company_id,
            company_name=company_name,
            transcript_summary=transcript_summary,
            financial_metrics=financial_metrics,
            investor_views=investor_views,
            recommendation=recommendation,
            last_updated=datetime.utcnow()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query")
async def semantic_query(
    query: str,
    company_id: Optional[str] = None
):
    """Perform semantic search on transcripts"""
    try:
        # Generate query embedding
        query_embedding = await ollama_service.generate_embedding(query)
        
        # Search similar transcripts
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

@app.get("/portfolio")
async def get_default_portfolio():
    """Get default portfolio (no user authentication)"""
    try:
        # Return mock portfolio data for now
        return {
            "totalValue": 125000,
            "dayChange": 1250,
            "dayChangePercent": 1.01,
            "positions": 5,
            "alerts": 2
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/portfolio/{user_id}")
async def get_portfolio(user_id: str):
    """Get user's portfolio"""
    try:
        portfolio = await db_client.get_user_portfolio(user_id)
        return portfolio
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/watchlist/{user_id}")
async def get_watchlist(user_id: str):
    """Get user's watchlist"""
    try:
        watchlist = await db_client.get_user_watchlist(user_id)
        return watchlist
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/companies/watchlist")
async def get_default_watchlist():
    """Get default watchlist (no user authentication)"""
    try:
        # Return mock watchlist data for now
        return []
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/companies")
async def create_company(name: str, ticker: str, sector: Optional[str] = None):
    """Create a new company"""
    try:
        company_id = await db_client.create_company(name, ticker, sector)
        return {"company_id": company_id, "message": "Company created successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "services": {
            "ollama": await ollama_service.health_check(),
            "database": await db_client.health_check()
        }
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
