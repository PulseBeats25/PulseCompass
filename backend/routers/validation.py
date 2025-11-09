"""
Validation Router
Handles performance validation and return data fetching
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import sys
from pathlib import Path

# Add utils to path
sys.path.append(str(Path(__file__).parent.parent / "utils"))

try:
    from performance_tracking import tracker, get_performance_summary
    from market_data_fetcher import fetcher, fetch_returns_for_snapshot, INDIAN_BENCHMARKS
    VALIDATION_ENABLED = True
except ImportError as e:
    print(f"⚠️ Validation modules not available: {e}")
    VALIDATION_ENABLED = False

router = APIRouter(prefix="/validation", tags=["validation"])


class ValidateSnapshotRequest(BaseModel):
    snapshot_id: str
    period_months: int = 6
    benchmark: str = '^NSEI'


class ManualReturnsRequest(BaseModel):
    snapshot_id: str
    returns_data: dict
    period_months: int


@router.get("/snapshots")
async def get_snapshots():
    """Get all saved ranking snapshots"""
    if not VALIDATION_ENABLED:
        raise HTTPException(status_code=503, detail="Validation system not available")
    
    try:
        snapshots = tracker._load_snapshots()
        
        # Return summary info
        snapshot_list = []
        for snapshot in snapshots:
            snapshot_list.append({
                'snapshot_id': snapshot['snapshot_id'],
                'timestamp': snapshot['timestamp'],
                'philosophy': snapshot['philosophy'],
                'total_companies': snapshot['summary']['total_companies'],
                'has_validation': 'validation' in snapshot,
                'validated_periods': list(snapshot.get('actual_returns', {}).keys()) if 'actual_returns' in snapshot else []
            })
        
        return {
            'total_snapshots': len(snapshot_list),
            'snapshots': snapshot_list
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/validate-snapshot")
async def validate_snapshot_auto(request: ValidateSnapshotRequest):
    """
    Automatically fetch returns and validate a snapshot
    
    This will:
    1. Fetch actual stock returns from Yahoo Finance
    2. Calculate validation metrics (hit rate, alpha, etc.)
    3. Save results to the snapshot
    """
    if not VALIDATION_ENABLED:
        raise HTTPException(status_code=503, detail="Validation system not available")
    
    try:
        print(f"\n🔄 Starting automatic validation for {request.snapshot_id}")
        
        validation_result = fetch_returns_for_snapshot(
            snapshot_id=request.snapshot_id,
            months=request.period_months
        )
        
        return {
            'success': True,
            'snapshot_id': request.snapshot_id,
            'period_months': request.period_months,
            'validation': validation_result,
            'message': f'Successfully validated snapshot with {request.period_months}m actual returns'
        }
    
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Validation failed: {str(e)}")


@router.post("/add-manual-returns")
async def add_manual_returns(request: ManualReturnsRequest):
    """
    Manually add return data for a snapshot
    
    Use this if you have return data from another source
    """
    if not VALIDATION_ENABLED:
        raise HTTPException(status_code=503, detail="Validation system not available")
    
    try:
        validation = tracker.add_actual_returns(
            snapshot_id=request.snapshot_id,
            returns_data=request.returns_data,
            period_months=request.period_months
        )
        
        return {
            'success': True,
            'snapshot_id': request.snapshot_id,
            'validation': validation
        }
    
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/performance-report")
async def get_performance_report():
    """
    Get comprehensive performance report
    
    Shows overall model performance across all validated snapshots
    """
    if not VALIDATION_ENABLED:
        raise HTTPException(status_code=503, detail="Validation system not available")
    
    try:
        report = get_performance_summary()
        return report
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/historical-performance")
async def get_historical_performance(months_back: int = 12):
    """
    Get historical performance data as time series
    
    Args:
        months_back: How many months of history to retrieve
    """
    if not VALIDATION_ENABLED:
        raise HTTPException(status_code=503, detail="Validation system not available")
    
    try:
        df = tracker.get_historical_performance(months_back=months_back)
        
        if df.empty:
            return {
                'message': 'No historical performance data available yet',
                'data': []
            }
        
        # Convert to dict for JSON response
        data = df.to_dict('records')
        
        # Convert datetime to string
        for record in data:
            if 'date' in record:
                record['date'] = record['date'].isoformat()
        
        return {
            'months_back': months_back,
            'data_points': len(data),
            'data': data
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/benchmarks")
async def get_available_benchmarks():
    """Get list of available benchmark indices"""
    return {
        'benchmarks': INDIAN_BENCHMARKS,
        'default': '^NSEI',
        'description': {
            '^NSEI': 'Nifty 50 - Large cap benchmark',
            '^NSMIDCP': 'Nifty Next 50 - Mid cap',
            '^NSEMDCP100': 'Nifty Midcap 100',
            '^CNXIT': 'Nifty IT - Technology sector',
            '^NSEBANK': 'Nifty Bank - Banking sector',
            '^CNXPHARMA': 'Nifty Pharma - Pharmaceutical sector',
            '^BSESN': 'Sensex - BSE benchmark'
        }
    }


@router.get("/stock-prices")
async def get_stock_prices(symbols: str):
    """
    Get current market prices for stocks
    
    Args:
        symbols: Comma-separated list of stock symbols (e.g., "TCS,INFY,WIPRO")
    """
    if not VALIDATION_ENABLED:
        raise HTTPException(status_code=503, detail="Validation system not available")
    
    try:
        symbol_list = [s.strip() for s in symbols.split(',')]
        prices = fetcher.get_current_prices(symbol_list)
        
        return {
            'timestamp': datetime.now().isoformat(),
            'prices': prices
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/export-backtest-data")
async def export_backtest_data():
    """
    Export all snapshot data in format suitable for backtesting
    
    Returns CSV file path
    """
    if not VALIDATION_ENABLED:
        raise HTTPException(status_code=503, detail="Validation system not available")
    
    try:
        output_file = "data/performance_tracking/backtest_export.csv"
        tracker.export_for_backtesting(output_file)
        
        return {
            'success': True,
            'file_path': output_file,
            'message': 'Backtest data exported successfully'
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/validate-all-snapshots")
async def validate_all_snapshots(period_months: int = 6):
    """
    Validate all snapshots that are old enough
    
    This will automatically fetch returns for all snapshots
    that are at least {period_months} months old
    """
    if not VALIDATION_ENABLED:
        raise HTTPException(status_code=503, detail="Validation system not available")
    
    try:
        snapshots = tracker._load_snapshots()
        cutoff_date = datetime.now() - timedelta(days=period_months * 30)
        
        validated_count = 0
        skipped_count = 0
        errors = []
        
        for snapshot in snapshots:
            snapshot_date = datetime.fromisoformat(snapshot['timestamp'])
            
            # Skip if too recent
            if snapshot_date > cutoff_date:
                skipped_count += 1
                continue
            
            # Skip if already validated for this period
            if 'actual_returns' in snapshot and f'{period_months}m' in snapshot['actual_returns']:
                skipped_count += 1
                continue
            
            try:
                fetch_returns_for_snapshot(snapshot['snapshot_id'], period_months)
                validated_count += 1
            except Exception as e:
                errors.append({
                    'snapshot_id': snapshot['snapshot_id'],
                    'error': str(e)
                })
        
        return {
            'success': True,
            'validated': validated_count,
            'skipped': skipped_count,
            'errors': errors,
            'message': f'Validated {validated_count} snapshots'
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
