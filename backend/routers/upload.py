"""
Upload Router - Handles file uploads (PDF transcripts and Excel financial data)
"""
from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List, Optional
from datetime import datetime

from models.schemas import UploadResponse
from services.pdf_parser import PDFParser
from services.excel_parser import ExcelParser
from core.state import get_app_state, set_processed_file

router = APIRouter(prefix="/upload", tags=["upload"])

# Initialize services
pdf_parser = PDFParser()
excel_parser = ExcelParser()


@router.get("/debug/state")
async def debug_state():
    """Debug endpoint to check current processed files state"""
    all_files = get_processed_files()
    
    # Add detailed metrics for financial files
    files_detail = []
    for file_id, data in all_files.items():
        file_info = {
            "file_id": file_id,
            "type": data.get('type'),
            "filename": data.get('filename')
        }
        
        # Add metrics preview for financial files
        if data.get('type') == 'financial' and 'metrics' in data:
            metrics = data['metrics']
            file_info['metrics_preview'] = {
                'revenue': metrics.get('revenue', 'N/A'),
                'net_profit': metrics.get('net_profit', 'N/A'),
                'roe': metrics.get('roe', 'N/A'),
                'eps': metrics.get('eps', 'N/A'),
                'total_metrics': len(metrics)
            }
        
        files_detail.append(file_info)
    
    return {
        "total_files": len(all_files),
        "files": files_detail
    }


@router.post("/test")
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


@router.post("/seed-sample-data")
async def seed_sample_data():
    """Seed sample data for testing when no files are uploaded"""
    try:
        from core.state import set_processed_file
        
        # Create sample transcript data
        transcript_file_id = f"pdf_{datetime.utcnow().timestamp()}"
        transcript_data = {
            'type': 'transcript',
            'filename': 'Sample Company - Q3 2024 Earnings Call.pdf',
            'raw_text': 'Sample earnings call transcript. Management discussed strong revenue growth of 15% year-over-year. The company exceeded guidance and delivered solid margins. Strategic initiatives are on track.',
            'analysis': {
                'key_quotes': [
                    'Revenue growth exceeded expectations at 15%',
                    'Operating margins improved by 200 basis points',
                    'Strategic initiatives on track for completion'
                ],
                'management_tone': 'confident',
                'guidance': {
                    'sales_projections': 'Expecting 12-15% revenue growth next quarter',
                    'margin_expectations': 'Targeting 20% operating margin',
                    'strategic_initiatives': 'New product launch planned for Q4'
                }
            },
            'integrity_score': 8,
            'company_id': 'default-company',
            'uploaded_at': datetime.utcnow().isoformat()
        }
        set_processed_file(transcript_file_id, transcript_data)
        
        # Create sample financial data
        financial_file_id = f"excel_{datetime.utcnow().timestamp()}"
        financial_data = {
            'type': 'financial',
            'filename': 'Sample Company Financial Data.xlsx',
            'financial_data': {'raw_dataframe': [], 'columns': []},
            'metrics': {
                'revenue': 5000000000,
                'net_profit': 500000000,
                'eps': 12.5,
                'roe': 18.5,
                'roce': 22.0,
                'pe_ratio': 18.5,
                'pb_ratio': 3.2,
                'debt_equity': 0.65,
                'ev_ebitda': 12.5,
                'revenue_growth': 15.0
            },
            'traffic_lights': {
                'revenue': {'status': 'green', 'value': 5000000000},
                'profitability': {'status': 'green', 'value': 500000000},
                'debt': {'status': 'green', 'value': 0.65},
                'growth': {'status': 'green', 'value': 15.0}
            },
            'company_id': 'default-company',
            'uploaded_at': datetime.utcnow().isoformat()
        }
        set_processed_file(financial_file_id, financial_data)
        
        return {
            "success": True,
            "message": "Sample data seeded successfully",
            "files": [
                {"file_id": transcript_file_id, "type": "transcript"},
                {"file_id": financial_file_id, "type": "financial"}
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/pdf", response_model=UploadResponse)
async def upload_pdf(
    files: List[UploadFile] = File(...),
    company_id: Optional[str] = None
):
    """Upload and process PDF transcript files"""
    try:
        results = []
        app_state = get_app_state()
        
        for file in files:
            if not file.filename.endswith('.pdf'):
                raise HTTPException(
                    status_code=400, 
                    detail=f"File {file.filename} is not a PDF"
                )
            
            # Read file content
            content = await file.read()
            
            # Process the PDF
            try:
                raw_text = pdf_parser.extract_text(content)
                analysis = pdf_parser.analyze_transcript(raw_text)
                integrity_score = pdf_parser.calculate_integrity_score(raw_text, analysis)
                
                file_id = f"pdf_{datetime.utcnow().timestamp()}"
                
                # Store processed data
                file_data = {
                    'type': 'transcript',
                    'filename': file.filename,
                    'raw_text': raw_text,
                    'analysis': analysis,
                    'integrity_score': integrity_score,
                    'company_id': company_id,
                    'uploaded_at': datetime.utcnow().isoformat()
                }
                
                set_processed_file(file_id, file_data)
                
                results.append({
                    "file_id": file_id,
                    "filename": file.filename,
                    "status": "processed",
                    "integrity_score": integrity_score
                })
                
            except Exception as parse_error:
                # Create entry even if processing fails
                file_id = f"pdf_{datetime.utcnow().timestamp()}_error"
                
                file_data = {
                    'type': 'transcript',
                    'filename': file.filename,
                    'raw_text': 'PDF processing failed',
                    'analysis': {'key_quotes': [], 'management_tone': 'neutral'},
                    'integrity_score': 5,
                    'company_id': company_id,
                    'error': str(parse_error),
                    'uploaded_at': datetime.utcnow().isoformat()
                }
                
                set_processed_file(file_id, file_data)
                
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


@router.post("/excel", response_model=UploadResponse)
async def upload_excel(
    files: List[UploadFile] = File(...),
    company_id: Optional[str] = None
):
    """Upload and process Excel/CSV financial data files"""
    try:
        results = []
        
        for file in files:
            if not any(file.filename.endswith(ext) for ext in ['.xlsx', '.xls', '.csv']):
                raise HTTPException(
                    status_code=400, 
                    detail=f"File {file.filename} is not supported"
                )
            
            # Read file content
            content = await file.read()
            
            # Process the Excel file
            try:
                print(f"\n=== Parsing Excel file: {file.filename} ===")
                parsed_data = excel_parser.parse_financial_data(content, file.filename)
                print(f"Parsed data shape: {parsed_data.get('shape', 'unknown')}")
                print(f"Columns found: {parsed_data.get('columns', [])[:10]}")  # First 10 columns
                
                if 'error' in parsed_data.get('metadata', {}):
                    raise Exception(f"Parsing error: {parsed_data['metadata']['error']}")
                
                metrics = excel_parser.calculate_metrics(parsed_data)
                print(f"Calculated metrics: {list(metrics.keys())}")
                print(f"Revenue: {metrics.get('revenue', 'NOT FOUND')}")
                print(f"Net Profit: {metrics.get('net_profit', 'NOT FOUND')}")
                
                if metrics.get('revenue') is None:
                    print("⚠️ WARNING: Revenue not found in Excel file!")
                
                traffic_lights = excel_parser.generate_traffic_lights(metrics)
                
                file_id = f"excel_{datetime.utcnow().timestamp()}"
                
                # Store processed data
                file_data = {
                    'type': 'financial',
                    'filename': file.filename,
                    'financial_data': parsed_data,
                    'metrics': metrics,
                    'traffic_lights': traffic_lights,
                    'company_id': company_id,
                    'uploaded_at': datetime.utcnow().isoformat()
                }
                
                set_processed_file(file_id, file_data)
                
                results.append({
                    "file_id": file_id,
                    "filename": file.filename,
                    "status": "processed",
                    "metrics_count": len(metrics)
                })
                
            except Exception as parse_error:
                # Create entry even if processing fails
                print(f"❌ ERROR parsing Excel file: {str(parse_error)}")
                import traceback
                traceback.print_exc()
                
                file_id = f"excel_{datetime.utcnow().timestamp()}_error"
                
                default_metrics = excel_parser._get_default_metrics()
                default_traffic_lights = excel_parser.generate_traffic_lights(default_metrics)
                
                file_data = {
                    'type': 'financial',
                    'filename': file.filename,
                    'financial_data': {'raw_dataframe': [], 'columns': []},
                    'metrics': default_metrics,
                    'traffic_lights': default_traffic_lights,
                    'company_id': company_id,
                    'error': str(parse_error),
                    'uploaded_at': datetime.utcnow().isoformat()
                }
                
                set_processed_file(file_id, file_data)
                
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
