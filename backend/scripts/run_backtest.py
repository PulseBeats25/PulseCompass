"""
6-Month Backtesting Script
Validates ranking model performance against actual returns
"""
import sys
from pathlib import Path
import pandas as pd
from datetime import datetime, timedelta
import json
from typing import Optional

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

try:
    from utils.performance_tracking import tracker
    from utils.market_data_fetcher import fetcher, INDIAN_BENCHMARKS
except ImportError as e:
    print(f"❌ Error importing modules: {e}")
    print("Make sure you've installed: pip install yfinance pandas")
    sys.exit(1)


def run_6month_backtest(snapshot_id: str = None, auto_validate_all: bool = False, snapshots_path: Optional[str] = None):
    """
    Run 6-month backtest on ranking snapshots
    
    Args:
        snapshot_id: Specific snapshot to validate (optional)
        auto_validate_all: Validate all snapshots older than 6 months
    """
    print("=" * 80)
    print("📊 6-MONTH BACKTESTING SYSTEM")
    print("=" * 80)
    
    # If a snapshots path is provided (or default exists), align tracker storage to that file
    try:
        base_path = Path(__file__).parents[1]  # backend/
        default_path = base_path / 'data' / 'performance_tracking' / 'ranking_snapshots.json'
        selected_path = Path(snapshots_path) if snapshots_path else default_path
        if selected_path.exists():
            tracker.storage_path = selected_path.parent
            tracker.snapshots_file = selected_path
            tracker.validation_file = tracker.storage_path / 'validation_results.json'
            print(f"🗂️  Using snapshots file: {tracker.snapshots_file}")
    except Exception as _e:
        pass

    # Load all snapshots
    snapshots = tracker._load_snapshots()
    loader_info = "tracker._load_snapshots()"

    # If no snapshots found, try explicit path (CLI or default JSON)
    if not snapshots:
        try:
            base_path = Path(__file__).parents[1]  # backend/
            default_path = base_path / 'data' / 'performance_tracking' / 'ranking_snapshots.json'
            path_to_read = Path(snapshots_path) if snapshots_path else default_path
            print(f"\n⚙️  Fallback: loading snapshots directly from: {path_to_read}")
            if path_to_read.exists():
                with path_to_read.open('r', encoding='utf-8') as f:
                    snapshots = json.load(f)
                loader_info = f"json.load({path_to_read})"
            else:
                print(f"\n⚠️ Path does not exist: {path_to_read}")
        except Exception as e:
            print(f"\n⚠️ Fallback load failed: {e}")
    
    if not snapshots:
        print("\n❌ No snapshots found!")
        print(f"   Loader used: {loader_info}")
        print("\nTo create snapshots:")
        print("1. Start backend: python -m uvicorn main:app --reload")
        print("2. Upload Excel file and run analysis")
        print("3. System automatically saves snapshots")
        return
    
    print(f"\n✅ Found {len(snapshots)} snapshots (via {loader_info})")
    
    # Calculate cutoff date (6 months ago)
    cutoff_date = datetime.now() - timedelta(days=180)
    
    # Filter snapshots older than 6 months
    old_snapshots = []
    for snapshot in snapshots:
        snapshot_date = datetime.fromisoformat(snapshot['timestamp'])
        if snapshot_date < cutoff_date:
            old_snapshots.append(snapshot)
    
    print(f"📅 Snapshots older than 6 months: {len(old_snapshots)}")
    
    if not old_snapshots:
        print("\n⚠️ No snapshots old enough for 6-month validation")
        print(f"   Oldest snapshot: {snapshots[0]['timestamp']}")
        print(f"   Need snapshots before: {cutoff_date.date()}")
        print("\n💡 For testing purposes, you can:")
        print("   1. Manually edit snapshot timestamps in data/performance_tracking/ranking_snapshots.json")
        print("   2. Or wait 6 months for real validation")
        return
    
    # Display available snapshots
    print("\n📋 Available Snapshots for Validation:")
    print("-" * 80)
    for i, snapshot in enumerate(old_snapshots, 1):
        snapshot_date = datetime.fromisoformat(snapshot['timestamp'])
        has_validation = 'validation' in snapshot
        status = "✅ Validated" if has_validation else "⏳ Pending"
        
        print(f"{i}. {snapshot['snapshot_id']}")
        print(f"   Date: {snapshot_date.date()}")
        print(f"   Philosophy: {snapshot['philosophy']}")
        companies_count = (
            snapshot.get('summary', {}).get('total_companies')
            or len(snapshot.get('rankings', []))
        )
        print(f"   Companies: {companies_count}")
        print(f"   Status: {status}")
        print()
    
    # Validate specific snapshot or all
    if snapshot_id:
        validate_single_snapshot(snapshot_id)
    elif auto_validate_all:
        validate_all_snapshots(old_snapshots)
    else:
        # Interactive mode
        print("\n🎯 What would you like to do?")
        print("1. Validate a specific snapshot")
        print("2. Validate all old snapshots")
        print("3. View performance report")
        print("4. Exit")
        
        choice = input("\nEnter choice (1-4): ").strip()
        
        if choice == "1":
            snapshot_id = input("Enter snapshot ID: ").strip()
            validate_single_snapshot(snapshot_id)
        elif choice == "2":
            validate_all_snapshots(old_snapshots)
        elif choice == "3":
            show_performance_report()
        else:
            print("Exiting...")


def validate_single_snapshot(snapshot_id: str, snapshots: Optional[list] = None, snapshots_path: Optional[str] = None):
    """Validate a single snapshot
    If snapshots is None, try tracker loader; if empty, try loading from snapshots_path.
    """
    print("\n" + "=" * 80)
    print(f"🔄 VALIDATING SNAPSHOT: {snapshot_id}")
    print("=" * 80)
    
    try:
        # Load snapshots if not provided
        loaded = snapshots
        if loaded is None:
            loaded = tracker._load_snapshots()
            if not loaded:
                # Fallback to explicit path
                base_path = Path(__file__).parents[1]
                default_path = base_path / 'data' / 'performance_tracking' / 'ranking_snapshots.json'
                path_to_read = Path(snapshots_path) if snapshots_path else default_path
                if path_to_read.exists():
                    with path_to_read.open('r', encoding='utf-8') as f:
                        loaded = json.load(f)

        snapshot = None
        
        for s in loaded or []:
            if s['snapshot_id'] == snapshot_id:
                snapshot = s
                break
        
        if not snapshot:
            print(f"❌ Snapshot {snapshot_id} not found")
            return
        
        # Get snapshot details
        snapshot_date = datetime.fromisoformat(snapshot['timestamp'])
        raw_symbols = [r['symbol'] for r in snapshot['rankings'][:50]]
        # Resolve to tickers ahead of time to avoid malformed Yahoo symbols with spaces
        symbols = []
        for s in raw_symbols:
            try:
                # Prefer explicit mapping, fallback to resolver
                mapped = fetcher.symbol_mapping.get(s) or fetcher._resolve_symbol(s)
                symbols.append(mapped)
            except Exception:
                symbols.append(s)
        
        print(f"\n📅 Snapshot Date: {snapshot_date.date()}")
        print(f"📊 Philosophy: {snapshot['philosophy']}")
        print(f"🏢 Companies: {len(symbols)}")
        print(f"\n🔄 Fetching actual returns from Yahoo Finance...")
        print("   (This may take 1-2 minutes...)")
        
        # Fetch actual returns
        returns_data = fetcher.get_stock_returns(
            symbols=symbols,
            start_date=snapshot_date,
            period_months=6
        )
        
        print(f"\n✅ Successfully fetched returns for {len(returns_data)}/{len(symbols)} stocks")
        
        # Fetch benchmark return
        print(f"\n📈 Fetching Nifty 50 benchmark return...")
        benchmark_return = fetcher.get_benchmark_return(
            benchmark='^NSEI',
            start_date=snapshot_date,
            period_months=6
        )
        
        # Add returns to snapshot
        validation = tracker.add_actual_returns(
            snapshot_id=snapshot_id,
            returns_data=returns_data,
            period_months=6
        )
        
        # Display results
        print("\n" + "=" * 80)
        print("📊 VALIDATION RESULTS")
        print("=" * 80)
        
        print(f"\n🎯 Top 10 Performance:")
        print(f"   Average Return: {validation['top_10_avg_return']:+.2f}%")
        print(f"   Benchmark (Nifty 50): {benchmark_return:+.2f}%")
        print(f"   Alpha: {validation['alpha']:+.2f}%")
        
        print(f"\n📈 Success Metrics:")
        print(f"   Hit Rate: {validation['hit_rate']:.1%} (% beating benchmark)")
        print(f"   Win Rate: {validation['win_rate']:.1%} (% positive returns)")
        print(f"   Sharpe Ratio: {validation['sharpe_ratio']:.2f}")
        
        print(f"\n🎲 Range:")
        print(f"   Best Performer: {validation['best_performer']:+.2f}%")
        print(f"   Worst Performer: {validation['worst_performer']:+.2f}%")
        print(f"   Max Drawdown: {validation['max_drawdown']:+.2f}%")
        
        # Interpretation
        print("\n" + "=" * 80)
        print("💡 INTERPRETATION")
        print("=" * 80)
        
        if validation['hit_rate'] >= 0.65:
            print("✅ EXCELLENT: Hit rate >65% - Model is working well!")
        elif validation['hit_rate'] >= 0.55:
            print("⚠️ GOOD: Hit rate 55-65% - Model is decent but can improve")
        else:
            print("❌ POOR: Hit rate <55% - Model needs recalibration")
        
        if validation['alpha'] >= 5:
            print("✅ EXCELLENT: Alpha >5% - Significantly beating market!")
        elif validation['alpha'] >= 0:
            print("⚠️ GOOD: Positive alpha - Beating market slightly")
        else:
            print("❌ POOR: Negative alpha - Underperforming market")
        
        if validation['sharpe_ratio'] >= 1.0:
            print("✅ EXCELLENT: Sharpe >1.0 - Good risk-adjusted returns")
        elif validation['sharpe_ratio'] >= 0.5:
            print("⚠️ GOOD: Sharpe 0.5-1.0 - Acceptable risk-adjusted returns")
        else:
            print("❌ POOR: Sharpe <0.5 - Poor risk-adjusted returns")
        
        print("\n✅ Validation complete!")
        
    except Exception as e:
        print(f"\n❌ Error during validation: {str(e)}")
        import traceback
        traceback.print_exc()


def validate_all_snapshots(old_snapshots: list):
    """Validate all old snapshots"""
    print("\n" + "=" * 80)
    print(f"🔄 BATCH VALIDATION: {len(old_snapshots)} snapshots")
    print("=" * 80)
    
    results = []
    
    for i, snapshot in enumerate(old_snapshots, 1):
        snapshot_id = snapshot['snapshot_id']
        
        # Skip if already validated
        if 'validation' in snapshot and '6m' in snapshot.get('actual_returns', {}):
            print(f"\n⏭️ [{i}/{len(old_snapshots)}] {snapshot_id} - Already validated")
            continue
        
        print(f"\n🔄 [{i}/{len(old_snapshots)}] Validating {snapshot_id}...")
        
        try:
            validate_single_snapshot(snapshot_id)
            results.append({'snapshot_id': snapshot_id, 'status': 'success'})
        except Exception as e:
            print(f"❌ Failed: {str(e)}")
            results.append({'snapshot_id': snapshot_id, 'status': 'failed', 'error': str(e)})
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 BATCH VALIDATION SUMMARY")
    print("=" * 80)
    
    success_count = sum(1 for r in results if r['status'] == 'success')
    failed_count = len(results) - success_count
    
    print(f"\n✅ Successful: {success_count}")
    print(f"❌ Failed: {failed_count}")
    
    if failed_count > 0:
        print("\n❌ Failed Snapshots:")
        for r in results:
            if r['status'] == 'failed':
                print(f"   - {r['snapshot_id']}: {r.get('error', 'Unknown error')}")


def show_performance_report():
    """Show overall performance report"""
    print("\n" + "=" * 80)
    print("📊 OVERALL PERFORMANCE REPORT")
    print("=" * 80)
    
    report = tracker.generate_performance_report()
    
    if report.get('status') == 'No validated data available':
        print("\n⚠️ No validated data available yet")
        print("   Run validation first using option 1 or 2")
        return
    
    print(f"\n📈 Overall Statistics:")
    print(f"   Total Snapshots: {report['total_snapshots']}")
    print(f"   Validated Snapshots: {report['validated_snapshots']}")
    
    if 'date_range' in report:
        print(f"\n📅 Date Range:")
        print(f"   First: {report['date_range']['first']}")
        print(f"   Last: {report['date_range']['last']}")
    
    if 'overall_metrics' in report:
        metrics = report['overall_metrics']
        print(f"\n🎯 Overall Metrics:")
        print(f"   Average Alpha: {metrics['avg_alpha']:+.2f}%")
        print(f"   Average Hit Rate: {metrics['avg_hit_rate']:.1%}")
        print(f"   Average Sharpe: {metrics['avg_sharpe']:.2f}")
        print(f"   Average Win Rate: {metrics['avg_win_rate']:.1%}")
        print(f"   Consistency (StdDev): {metrics['consistency']:.2f}")
    
    if 'by_philosophy' in report:
        print(f"\n📊 Performance by Philosophy:")
        for philosophy, stats in report['by_philosophy'].items():
            print(f"\n   {philosophy.upper()}:")
            print(f"      Count: {stats['count']}")
            print(f"      Avg Alpha: {stats['avg_alpha']:+.2f}%")
            print(f"      Avg Hit Rate: {stats['avg_hit_rate']:.1%}")
            print(f"      Avg Sharpe: {stats['avg_sharpe']:.2f}")
    
    # Best and worst
    if 'best_snapshot' in report:
        best = report['best_snapshot']
        print(f"\n🏆 Best Snapshot:")
        print(f"   ID: {best['snapshot_id']}")
        print(f"   Date: {best['timestamp']}")
        print(f"   Alpha: {best['validation']['alpha']:+.2f}%")
        print(f"   Hit Rate: {best['validation']['hit_rate']:.1%}")
    
    if 'worst_snapshot' in report:
        worst = report['worst_snapshot']
        print(f"\n⚠️ Worst Snapshot:")
        print(f"   ID: {worst['snapshot_id']}")
        print(f"   Date: {worst['timestamp']}")
        print(f"   Alpha: {worst['validation']['alpha']:+.2f}%")
        print(f"   Hit Rate: {worst['validation']['hit_rate']:.1%}")


def export_backtest_results():
    """Export backtest results to CSV"""
    output_file = "data/performance_tracking/backtest_results.csv"
    tracker.export_for_backtesting(output_file)
    print(f"\n✅ Backtest results exported to: {output_file}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Run 6-month backtest on ranking model')
    parser.add_argument('--snapshot-id', help='Specific snapshot ID to validate')
    parser.add_argument('--auto-validate-all', action='store_true', help='Automatically validate all old snapshots')
    parser.add_argument('--report', action='store_true', help='Show performance report only')
    parser.add_argument('--export', action='store_true', help='Export backtest results to CSV')
    parser.add_argument('--snapshots', type=str, default=None, help='Path to ranking_snapshots.json (override)')
    
    args = parser.parse_args()
    
    if args.report:
        show_performance_report()
    elif args.export:
        export_backtest_results()
    else:
        run_6month_backtest(
            snapshot_id=args.snapshot_id,
            auto_validate_all=args.auto_validate_all,
            snapshots_path=args.snapshots
        )
