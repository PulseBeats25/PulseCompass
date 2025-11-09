"""
Performance Tracking System for Stock Rankings
Tracks historical rankings and validates model performance over time
"""
import pandas as pd
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pathlib import Path
import numpy as np


class PerformanceTracker:
    """
    Tracks ranking performance over time and validates predictions
    """
    
    def __init__(self, storage_path: str = "data/performance_tracking"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.snapshots_file = self.storage_path / "ranking_snapshots.json"
        self.validation_file = self.storage_path / "validation_results.json"
    
    def save_ranking_snapshot(
        self,
        rankings: List[Dict],
        philosophy: str,
        metadata: Optional[Dict] = None
    ) -> str:
        """
        Save current rankings for future validation
        
        Args:
            rankings: List of ranked companies with scores
            philosophy: Investment philosophy used
            metadata: Additional context (market conditions, etc.)
            
        Returns:
            Snapshot ID for reference
        """
        snapshot_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        snapshot = {
            'snapshot_id': snapshot_id,
            'timestamp': datetime.now().isoformat(),
            'philosophy': philosophy,
            'rankings': rankings[:50],  # Store top 50
            'metadata': metadata or {},
            'summary': {
                'total_companies': len(rankings),
                'avg_score': np.mean([r['compositeScore'] for r in rankings]),
                'top_10_avg_score': np.mean([r['compositeScore'] for r in rankings[:10]]),
                'sector_distribution': self._get_sector_distribution(rankings)
            }
        }
        
        # Load existing snapshots
        snapshots = self._load_snapshots()
        snapshots.append(snapshot)
        
        # Save updated snapshots
        with open(self.snapshots_file, 'w') as f:
            json.dump(snapshots, f, indent=2)
        
        print(f"✅ Saved ranking snapshot: {snapshot_id}")
        return snapshot_id
    
    def add_actual_returns(
        self,
        snapshot_id: str,
        returns_data: Dict[str, float],
        period_months: int
    ):
        """
        Add actual returns data for a historical snapshot
        
        Args:
            snapshot_id: ID of the snapshot to update
            returns_data: Dict mapping company symbols to actual returns
            period_months: Time period for returns (3, 6, or 12 months)
        """
        snapshots = self._load_snapshots()
        
        for snapshot in snapshots:
            if snapshot['snapshot_id'] == snapshot_id:
                if 'actual_returns' not in snapshot:
                    snapshot['actual_returns'] = {}
                
                snapshot['actual_returns'][f'{period_months}m'] = {
                    'returns': returns_data,
                    'recorded_date': datetime.now().isoformat()
                }
                
                # Calculate validation metrics
                validation = self._calculate_validation_metrics(
                    snapshot['rankings'],
                    returns_data,
                    period_months
                )
                
                snapshot['validation'] = validation
                
                # Save updated snapshots
                with open(self.snapshots_file, 'w') as f:
                    json.dump(snapshots, f, indent=2)
                
                print(f"✅ Added {period_months}m returns for snapshot {snapshot_id}")
                print(f"   Hit Rate: {validation['hit_rate']:.1%}")
                print(f"   Alpha: {validation['alpha']:.2f}%")
                
                return validation
        
        raise ValueError(f"Snapshot {snapshot_id} not found")
    
    def _calculate_validation_metrics(
        self,
        rankings: List[Dict],
        returns_data: Dict[str, float],
        period_months: int
    ) -> Dict:
        """
        Calculate validation metrics comparing predictions to actual returns
        """
        top_10 = rankings[:10]
        top_10_symbols = [r['symbol'] for r in top_10]
        
        # Get returns for top 10
        top_10_returns = [returns_data.get(symbol, 0) for symbol in top_10_symbols]
        
        # Benchmark (assume Nifty 50 or average of all stocks)
        all_returns = list(returns_data.values())
        benchmark_return = np.median(all_returns) if all_returns else 0
        
        # Calculate metrics
        avg_return = np.mean(top_10_returns)
        alpha = avg_return - benchmark_return
        hit_rate = sum(1 for r in top_10_returns if r > benchmark_return) / len(top_10_returns)
        
        # Sharpe ratio (simplified - assuming risk-free rate of 6%)
        risk_free_rate = 6.0 * (period_months / 12)  # Annualized
        std_dev = np.std(top_10_returns) if len(top_10_returns) > 1 else 1
        sharpe = (avg_return - risk_free_rate) / std_dev if std_dev > 0 else 0
        
        # Win rate (% positive returns)
        win_rate = sum(1 for r in top_10_returns if r > 0) / len(top_10_returns)
        
        # Max drawdown
        max_drawdown = min(top_10_returns) if top_10_returns else 0
        
        return {
            'period_months': period_months,
            'top_10_avg_return': round(avg_return, 2),
            'benchmark_return': round(benchmark_return, 2),
            'alpha': round(alpha, 2),
            'hit_rate': round(hit_rate, 3),
            'sharpe_ratio': round(sharpe, 2),
            'win_rate': round(win_rate, 3),
            'max_drawdown': round(max_drawdown, 2),
            'best_performer': max(top_10_returns) if top_10_returns else 0,
            'worst_performer': min(top_10_returns) if top_10_returns else 0
        }
    
    def get_historical_performance(self, months_back: int = 12) -> pd.DataFrame:
        """
        Get historical performance summary
        
        Args:
            months_back: How many months of history to retrieve
            
        Returns:
            DataFrame with performance metrics over time
        """
        snapshots = self._load_snapshots()
        cutoff_date = datetime.now() - timedelta(days=months_back * 30)
        
        performance_data = []
        
        for snapshot in snapshots:
            snapshot_date = datetime.fromisoformat(snapshot['timestamp'])
            
            if snapshot_date < cutoff_date:
                continue
            
            if 'validation' in snapshot:
                performance_data.append({
                    'date': snapshot_date,
                    'snapshot_id': snapshot['snapshot_id'],
                    'philosophy': snapshot['philosophy'],
                    **snapshot['validation']
                })
        
        if not performance_data:
            return pd.DataFrame()
        
        df = pd.DataFrame(performance_data)
        df = df.sort_values('date')
        
        return df
    
    def generate_performance_report(self) -> Dict:
        """
        Generate comprehensive performance report
        
        Returns:
            Dict with overall model performance statistics
        """
        snapshots = self._load_snapshots()
        validated_snapshots = [s for s in snapshots if 'validation' in s]
        
        if not validated_snapshots:
            return {
                'status': 'No validated data available',
                'total_snapshots': len(snapshots),
                'validated_snapshots': 0
            }
        
        # Aggregate metrics
        all_validations = [s['validation'] for s in validated_snapshots]
        
        report = {
            'total_snapshots': len(snapshots),
            'validated_snapshots': len(validated_snapshots),
            'date_range': {
                'first': validated_snapshots[0]['timestamp'],
                'last': validated_snapshots[-1]['timestamp']
            },
            'overall_metrics': {
                'avg_alpha': np.mean([v['alpha'] for v in all_validations]),
                'avg_hit_rate': np.mean([v['hit_rate'] for v in all_validations]),
                'avg_sharpe': np.mean([v['sharpe_ratio'] for v in all_validations]),
                'avg_win_rate': np.mean([v['win_rate'] for v in all_validations]),
                'consistency': np.std([v['alpha'] for v in all_validations])
            },
            'by_philosophy': self._aggregate_by_philosophy(validated_snapshots),
            'best_snapshot': max(validated_snapshots, key=lambda s: s['validation']['alpha']),
            'worst_snapshot': min(validated_snapshots, key=lambda s: s['validation']['alpha'])
        }
        
        return report
    
    def _aggregate_by_philosophy(self, snapshots: List[Dict]) -> Dict:
        """Aggregate performance by investment philosophy"""
        by_philosophy = {}
        
        for snapshot in snapshots:
            philosophy = snapshot['philosophy']
            if philosophy not in by_philosophy:
                by_philosophy[philosophy] = []
            by_philosophy[philosophy].append(snapshot['validation'])
        
        result = {}
        for philosophy, validations in by_philosophy.items():
            result[philosophy] = {
                'count': len(validations),
                'avg_alpha': np.mean([v['alpha'] for v in validations]),
                'avg_hit_rate': np.mean([v['hit_rate'] for v in validations]),
                'avg_sharpe': np.mean([v['sharpe_ratio'] for v in validations])
            }
        
        return result
    
    def _get_sector_distribution(self, rankings: List[Dict]) -> Dict:
        """Get sector distribution from rankings"""
        sectors = {}
        for company in rankings[:20]:  # Top 20
            sector = company.get('sector', 'Unknown')
            sectors[sector] = sectors.get(sector, 0) + 1
        return sectors
    
    def _load_snapshots(self) -> List[Dict]:
        """Load existing snapshots from file"""
        if not self.snapshots_file.exists():
            return []
        
        try:
            with open(self.snapshots_file, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []
    
    def export_for_backtesting(self, output_file: str):
        """
        Export data in format suitable for backtesting
        
        Args:
            output_file: Path to output CSV file
        """
        snapshots = self._load_snapshots()
        
        rows = []
        for snapshot in snapshots:
            for rank, company in enumerate(snapshot['rankings'], 1):
                row = {
                    'snapshot_date': snapshot['timestamp'],
                    'philosophy': snapshot['philosophy'],
                    'rank': rank,
                    'company': company['company'],
                    'symbol': company['symbol'],
                    'composite_score': company['compositeScore'],
                    'buffett_score': company['buffettScore'],
                    'lynch_score': company['lynchScore']
                }
                
                # Add actual returns if available
                if 'actual_returns' in snapshot:
                    for period, data in snapshot['actual_returns'].items():
                        returns = data['returns']
                        row[f'return_{period}'] = returns.get(company['symbol'], None)
                
                rows.append(row)
        
        df = pd.DataFrame(rows)
        df.to_csv(output_file, index=False)
        print(f"✅ Exported {len(rows)} records to {output_file}")


# Singleton instance
tracker = PerformanceTracker()


def save_current_rankings(rankings: List[Dict], philosophy: str, metadata: Dict = None) -> str:
    """Convenience function to save rankings"""
    return tracker.save_ranking_snapshot(rankings, philosophy, metadata)


def add_returns_data(snapshot_id: str, returns: Dict[str, float], months: int):
    """Convenience function to add returns"""
    return tracker.add_actual_returns(snapshot_id, returns, months)


def get_performance_summary() -> Dict:
    """Convenience function to get performance report"""
    return tracker.generate_performance_report()
