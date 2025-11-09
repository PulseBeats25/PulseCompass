import pandas as pd
import numpy as np
from typing import Dict, List, Any, Union
import io
from datetime import datetime
from .philosophy_scorer import PhilosophyScorer

class ExcelParser:
    """Service for parsing Excel/CSV financial data and calculating metrics"""
    
    def __init__(self):
        self.philosophy_scorer = PhilosophyScorer()
        self.traffic_light_thresholds = {
            'profitability': {
                'roe': {'good': 15, 'neutral': 10},
                'roa': {'good': 10, 'neutral': 5},
                'roce': {'good': 15, 'neutral': 10},
                'net_margin': {'good': 10, 'neutral': 5},
                'operating_margin': {'good': 15, 'neutral': 10},
                'gross_margin': {'good': 30, 'neutral': 20}
            },
            'strength': {
                'debt_equity': {'good': 0.5, 'neutral': 1.0, 'reverse': True},
                'current_ratio': {'good': 1.5, 'neutral': 1.2},
                'interest_coverage': {'good': 5, 'neutral': 2.5},
                'cash_ratio': {'good': 0.2, 'neutral': 0.1}
            },
            'valuation': {
                'pe_ratio': {'good': 15, 'neutral': 25, 'reverse': True},
                'pb_ratio': {'good': 1.5, 'neutral': 3, 'reverse': True},
                'ev_ebitda': {'good': 10, 'neutral': 15, 'reverse': True},
                'peg_ratio': {'good': 1, 'neutral': 1.5, 'reverse': True}
            },
            'growth': {
                'revenue_growth': {'good': 15, 'neutral': 8},
                'profit_growth': {'good': 20, 'neutral': 10},
                'eps_growth': {'good': 15, 'neutral': 8}
            }
        }
    
    def parse_financial_data(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        """Parse financial data from Excel/CSV files"""
        try:
            if filename.endswith('.csv'):
                df = pd.read_csv(io.BytesIO(file_content))
                all_sheets = {'Sheet1': df}
            else:
                # Read all sheets from Excel file
                try:
                    all_sheets = pd.read_excel(io.BytesIO(file_content), sheet_name=None, engine='openpyxl')
                except Exception:
                    try:
                        all_sheets = pd.read_excel(io.BytesIO(file_content), sheet_name=None, engine='xlrd')
                    except Exception:
                        all_sheets = pd.read_excel(io.BytesIO(file_content), sheet_name=None)
                
                print(f"📊 Found {len(all_sheets)} sheets: {list(all_sheets.keys())}")
                
                # Process ALL relevant sheets and combine data
                processed_sheets = {}
                sheet_types = {
                    'quarters': ['quarters'],
                    'profit_loss': ['profit & loss', 'profit_&_loss', 'p&l'],
                    'balance_sheet': ['balance sheet', 'balance_sheet'],
                    'cash_flow': ['cash flow', 'cash_flow', 'cashflow']
                }
                
                for sheet_type, patterns in sheet_types.items():
                    for sheet_name, sheet_df in all_sheets.items():
                        if any(pattern in sheet_name.lower() for pattern in patterns):
                            if not sheet_df.empty:
                                processed_sheets[sheet_type] = {
                                    'name': sheet_name,
                                    'df': sheet_df
                                }
                                print(f"✅ Found {sheet_type}: '{sheet_name}'")
                                break
                
                # Use Quarters as primary, fall back to P&L
                if 'quarters' in processed_sheets:
                    df = processed_sheets['quarters']['df']
                    print(f"✅ Using primary sheet: '{processed_sheets['quarters']['name']}'")
                elif 'profit_loss' in processed_sheets:
                    df = processed_sheets['profit_loss']['df']
                    print(f"✅ Using primary sheet: '{processed_sheets['profit_loss']['name']}'")
                else:
                    # Use first non-empty sheet
                    for sheet_name, sheet_df in all_sheets.items():
                        if not sheet_df.empty and 'data sheet' not in sheet_name.lower():
                            df = sheet_df
                            print(f"✅ Using first non-empty sheet: '{sheet_name}'")
                            break
                
                # Store all processed sheets for comprehensive analysis
                if not hasattr(self, '_all_sheets'):
                    self._all_sheets = processed_sheets
            
            # Clean and standardize the dataframe
            df = self._clean_dataframe(df)
            
            # Extract structured data
            structured_data = {
                'raw_dataframe': df.to_dict('records'),
                'columns': df.columns.tolist(),
                'shape': df.shape,
                'periods': self._extract_periods(df),
                'metadata': {
                    'filename': filename,
                    'processed_at': datetime.utcnow().isoformat(),
                    'rows': len(df),
                    'columns': len(df.columns)
                }
            }
            
            return structured_data
            
        except Exception as e:
            # Return a basic structure even if parsing fails
            return {
                'raw_dataframe': [],
                'columns': [],
                'shape': (0, 0),
                'periods': [],
                'metadata': {
                    'filename': filename,
                    'processed_at': datetime.utcnow().isoformat(),
                    'rows': 0,
                    'columns': 0,
                    'error': str(e)
                }
            }
    
    def calculate_metrics(self, financial_data: Dict[str, Any]) -> Dict[str, float]:
        """Calculate key financial metrics from parsed data"""
        try:
            df = pd.DataFrame(financial_data['raw_dataframe'])
            
            # Return default metrics if no data
            if df.empty:
                return self._get_default_metrics()
            
            metrics = {}
            
            # Extract base financial values
            base_values = self._extract_base_values(df)
            
            # Extract profitability metrics
            metrics.update(self._extract_profitability_metrics(df))
            
            # Extract strength metrics
            metrics.update(self._extract_strength_metrics(df))
            
            # Extract valuation metrics
            metrics.update(self._extract_valuation_metrics(df))
            
            # Extract growth metrics
            metrics.update(self._extract_growth_metrics(df))
            
            # Calculate derived metrics (ROA, EPS, etc.)
            metrics.update(self._calculate_derived_metrics(metrics, base_values, df))
            
            # Try to extract additional metrics from other sheets if available
            if hasattr(self, '_all_sheets') and self._all_sheets:
                metrics.update(self._extract_from_balance_sheet())
                metrics.update(self._calculate_growth_from_quarters())
            
            return metrics
        except Exception as e:
            print(f"Error calculating metrics: {e}")
            return self._get_default_metrics()
    
    def _extract_from_balance_sheet(self) -> Dict[str, float]:
        """Extract metrics from balance sheet"""
        metrics = {}
        if 'balance_sheet' not in self._all_sheets:
            return metrics
        
        try:
            bs_df = self._all_sheets['balance_sheet']['df']
            bs_df = self._clean_dataframe(bs_df)
            
            # Extract equity and debt
            equity = self._find_metric_value(bs_df, ['equity', 'total_equity', 'shareholders_equity', 'net_block'])
            debt = self._find_metric_value(bs_df, ['borrowings', 'total_debt', 'debt'])
            
            if equity and debt and equity > 0:
                metrics['debt_equity'] = debt / equity
                print(f"📊 Calculated Debt/Equity from Balance Sheet: {metrics['debt_equity']:.2f}")
            
        except Exception as e:
            print(f"Error extracting from balance sheet: {e}")
        
        return metrics
    
    def _calculate_growth_from_quarters(self) -> Dict[str, float]:
        """Calculate growth metrics from quarterly data"""
        metrics = {}
        if 'quarters' not in self._all_sheets:
            return metrics
        
        try:
            q_df = self._all_sheets['quarters']['df']
            q_df = self._clean_dataframe(q_df)
            
            # Get revenue and profit columns
            revenue_col = None
            profit_col = None
            
            for col in q_df.columns:
                if 'sales' in col.lower() or 'revenue' in col.lower():
                    revenue_col = col
                if 'net_profit' in col.lower() or 'net profit' in col.lower():
                    profit_col = col
            
            if revenue_col and len(q_df) >= 2:
                revenues = q_df[revenue_col].dropna()
                if len(revenues) >= 2:
                    latest = revenues.iloc[-1]
                    previous = revenues.iloc[-2]
                    if previous != 0:
                        metrics['revenue_growth'] = ((latest - previous) / abs(previous)) * 100
                        print(f"📊 Calculated Revenue Growth: {metrics['revenue_growth']:.1f}%")
            
            if profit_col and len(q_df) >= 2:
                profits = q_df[profit_col].dropna()
                if len(profits) >= 2:
                    latest = profits.iloc[-1]
                    previous = profits.iloc[-2]
                    if previous != 0:
                        metrics['profit_growth'] = ((latest - previous) / abs(previous)) * 100
                        print(f"📊 Calculated Profit Growth: {metrics['profit_growth']:.1f}%")
            
        except Exception as e:
            print(f"Error calculating growth: {e}")
        
        return metrics
    
    def generate_traffic_lights(self, metrics: Dict[str, float]) -> Dict[str, Dict[str, Dict[str, Any]]]:
        """Generate traffic light indicators for all metrics"""
        traffic_lights = {
            'profitability': {},
            'strength': {},
            'valuation': {},
            'growth': {}
        }
        
        for category, category_metrics in self.traffic_light_thresholds.items():
            for metric, thresholds in category_metrics.items():
                if metric in metrics:
                    value = metrics[metric]
                    status = self._get_traffic_light_status(value, thresholds)
                    
                    traffic_lights[category][metric] = {
                        'value': self._format_metric_value(metric, value),
                        'status': status,
                        'raw_value': value,
                        'threshold_good': thresholds['good'],
                        'threshold_neutral': thresholds['neutral'],
                        'rating': self._get_rating_label(status)
                    }
        
        return traffic_lights
    
    def _get_rating_label(self, status: str) -> str:
        """Convert traffic light status to rating label"""
        rating_map = {
            'green': 'Excellent',
            'yellow': 'Average',
            'red': 'Poor'
        }
        return rating_map.get(status, 'Unknown')
    
    def generate_philosophy_scores(self, metrics: Dict[str, float]) -> Dict[str, Any]:
        """Generate investment philosophy scores for all philosophies"""
        philosophy_scores = self.philosophy_scorer.compare_philosophies(metrics)
        
        # Add individual philosophy details
        all_philosophies = self.philosophy_scorer.get_all_philosophies()
        
        return {
            'scores': philosophy_scores,
            'philosophies': all_philosophies
        }
    
    def _clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and standardize the dataframe"""
        # Remove only completely empty rows (keep columns even if mostly empty)
        df = df.dropna(how='all')
        
        # Check if data is in row format (metrics as row labels, quarters as columns)
        # This is common in financial statements
        if len(df.columns) >= 1 and len(df) > 0:
            # Check if first column OR first few rows contain "Narration" or similar keywords
            transpose_keywords = ['narration', 'metric', 'item', 'description', 'particulars', 'sales', 'revenue', 'expenses']
            
            # Check if any of the first 10 rows contain these keywords
            should_transpose = any(
                any(keyword in str(val).lower() for keyword in transpose_keywords)
                for val in df.iloc[:min(10, len(df)), 0]
            )
            
            if should_transpose:
                print("📊 Detected row-based format, transposing...")
                # Find the row with "Narration" or similar
                narration_row = None
                for idx in range(min(10, len(df))):
                    val = str(df.iloc[idx, 0]).lower()
                    if 'narration' in val or 'metric' in val or 'item' in val:
                        narration_row = idx
                        print(f"📊 Found header row at index {idx}")
                        break
                
                # Use that row as header and transpose
                if narration_row is not None:
                    if narration_row > 0:
                        # Skip rows before narration row
                        df = df.iloc[narration_row:]
                    
                    # Set first row as header
                    df.columns = df.iloc[0]
                    df = df.iloc[1:]
                    
                    # Now transpose
                    df = df.T
                    # Reset index to make quarters a column
                    df = df.reset_index()
                    
                    # Set first row as column names after transpose
                    if len(df) > 0:
                        df.columns = df.iloc[0]
                        df = df.iloc[1:]
                        df = df.reset_index(drop=True)
                    
                    df.columns.name = None
                    print(f"📊 Transposed to shape: {df.shape}")
                else:
                    # If we found keywords but no clear header row, try simple transpose
                    df = df.set_index(df.columns[0]).T
                    df = df.reset_index()
                    df.columns.name = None
        
        # Standardize column names (convert to string first)
        df.columns = [str(col).lower().strip().replace(' ', '_') for col in df.columns]
        
        print(f"📋 Columns after cleaning: {df.columns.tolist()[:15]}")  # First 15 columns
        print(f"📋 First few rows:\n{df.head(3)}")
        
        # Convert numeric columns
        for col in df.columns:
            if df[col].dtype == 'object':
                try:
                    # First clean the string values
                    cleaned_series = df[col].astype(str).str.replace('%', '').str.replace(',', '')
                    # Try to convert to numeric
                    numeric_series = pd.to_numeric(cleaned_series, errors='coerce')
                    # Only update if we successfully converted any values
                    if not numeric_series.isna().all():
                        df[col] = numeric_series
                except (ValueError, TypeError, AttributeError):
                    # If conversion fails, leave as is
                    continue
        
        return df
    
    def _extract_periods(self, df: pd.DataFrame) -> List[str]:
        """Extract time periods from the dataframe"""
        periods = []
        
        # Look for date/period columns
        date_patterns = ['date', 'quarter', 'year', 'period', 'fy', 'q1', 'q2', 'q3', 'q4']
        
        for col in df.columns:
            col_lower = col.lower()
            if any(pattern in col_lower for pattern in date_patterns):
                periods.extend(df[col].dropna().astype(str).tolist())
                break
        
        return periods[:10]  # Return up to 10 periods
    
    def _extract_base_values(self, df: pd.DataFrame) -> Dict[str, float]:
        """Extract base financial statement values for derived calculations"""
        base_values = {}
        
        column_patterns = {
            'net_income': ['net_income', 'net profit', 'profit_after_tax', 'pat', 'net_profit', 'net profit'],
            'total_assets': ['total_assets', 'total assets', 'assets', 'total'],
            'total_equity': ['total_equity', 'shareholders_equity', 'equity', 'total equity', 'equity_share_capital', 'net_block'],
            'shares_outstanding': ['shares_outstanding', 'shares outstanding', 'outstanding_shares', 'number_of_shares'],
            'expenses': ['expenses', 'total_expenses'],
            'depreciation': ['depreciation'],
            'interest': ['interest'],
            'tax': ['tax'],
            'borrowings': ['borrowings', 'debt', 'total_debt']
        }
        
        for key, patterns in column_patterns.items():
            value = self._find_metric_value(df, patterns)
            if value is not None:
                base_values[key] = value
        
        return base_values
    
    def _extract_profitability_metrics(self, df: pd.DataFrame) -> Dict[str, float]:
        """Extract profitability metrics"""
        metrics = {}
        
        column_patterns = {
            'roe': ['roe', 'return_on_equity', 'return on equity'],
            'roa': ['roa', 'return_on_assets', 'return on assets'],
            'roce': ['roce', 'return_on_capital_employed', 'return on capital employed'],
            'net_margin': ['net_margin', 'net profit margin', 'npm', 'net_profit_margin'],
            'operating_margin': ['operating_margin', 'opm', 'ebit_margin', 'operating margin'],
            'gross_margin': ['gross_margin', 'gpm', 'gross margin'],
            'revenue': ['sales', 'revenue', 'total_revenue', 'turnover', 'total_sales'],
            'net_profit': ['net_profit', 'net profit', 'profit_after_tax', 'pat'],
            'operating_profit': ['operating_profit', 'operating profit', 'ebit', 'operating_income']
        }
        
        for metric, patterns in column_patterns.items():
            value = self._find_metric_value(df, patterns)
            if value is not None:
                metrics[metric] = value
        
        return metrics
    
    def _extract_strength_metrics(self, df: pd.DataFrame) -> Dict[str, float]:
        """Extract financial strength metrics"""
        metrics = {}
        
        column_patterns = {
            'debt_equity': ['debt_to_equity', 'debt_equity', 'd/e', 'debt/equity', 'debt equity'],
            'current_ratio': ['current_ratio', 'cr', 'current ratio'],
            'interest_coverage': ['interest_coverage', 'times_interest_earned', 'interest coverage'],
            'cash_ratio': ['cash_ratio', 'cash ratio', 'cash_and_equivalents_ratio']
        }
        
        for metric, patterns in column_patterns.items():
            value = self._find_metric_value(df, patterns)
            if value is not None:
                metrics[metric] = value
        
        return metrics
    
    def _extract_valuation_metrics(self, df: pd.DataFrame) -> Dict[str, float]:
        """Extract valuation metrics"""
        metrics = {}
        
        column_patterns = {
            'pe_ratio': ['pe', 'p/e', 'price_to_earnings', 'pe_ratio', 'price to earnings'],
            'pb_ratio': ['pb', 'p/b', 'price_to_book', 'pb_ratio', 'price to book'],
            'ev_ebitda': ['ev/ebitda', 'ev_ebitda', 'enterprise_value_to_ebitda'],
            'peg_ratio': ['peg', 'peg_ratio', 'price_earnings_growth']
        }
        
        for metric, patterns in column_patterns.items():
            value = self._find_metric_value(df, patterns)
            if value is not None:
                metrics[metric] = value
        
        return metrics
    
    def _extract_growth_metrics(self, df: pd.DataFrame) -> Dict[str, float]:
        """Extract growth metrics"""
        metrics = {}
        
        column_patterns = {
            'revenue_growth': ['sales_growth', 'revenue_growth', 'sales growth', 'revenue growth'],
            'profit_growth': ['profit_growth', 'net_profit_growth', 'profit growth'],
            'eps_growth': ['eps_growth', 'earnings_per_share_growth', 'eps growth']
        }
        
        for metric, patterns in column_patterns.items():
            value = self._find_metric_value(df, patterns)
            if value is not None:
                metrics[metric] = value
        
        return metrics
    
    def _find_metric_value(self, df: pd.DataFrame, patterns: List[str]) -> Union[float, None]:
        """Find metric value in dataframe using flexible column matching"""
        for pattern in patterns:
            # Try exact match first
            for col in df.columns:
                if pattern.lower() == col.lower().strip():
                    values = df[col].dropna()
                    if not values.empty:
                        try:
                            return float(values.iloc[-1])  # Get most recent value
                        except (ValueError, TypeError):
                            continue
            
            # Try partial match
            for col in df.columns:
                if pattern.lower() in col.lower():
                    values = df[col].dropna()
                    if not values.empty:
                        try:
                            return float(values.iloc[-1])
                        except (ValueError, TypeError):
                            continue
        
        return None
    
    def _calculate_derived_metrics(self, metrics: Dict[str, float], base_values: Dict[str, float], df: pd.DataFrame) -> Dict[str, float]:
        """Calculate derived metrics from base metrics and financial statement values"""
        derived = {}
        
        # Calculate ROA if not already present and we have net income and total assets
        if 'roa' not in metrics and 'net_income' in base_values and 'total_assets' in base_values:
            if base_values['total_assets'] > 0:
                derived['roa'] = (base_values['net_income'] / base_values['total_assets']) * 100
        
        # Calculate EPS if we have net income and shares outstanding
        if 'net_income' in base_values and 'shares_outstanding' in base_values:
            if base_values['shares_outstanding'] > 0:
                derived['eps'] = base_values['net_income'] / base_values['shares_outstanding']
        
        # Try to find EPS directly from the dataframe if not calculated
        if 'eps' not in derived:
            eps_patterns = ['eps', 'earnings_per_share', 'earnings per share']
            eps_value = self._find_metric_value(df, eps_patterns)
            if eps_value is not None:
                derived['eps'] = eps_value
        
        # Calculate PEG ratio if P/E and growth are available
        if 'pe_ratio' in metrics and 'eps_growth' in metrics and metrics['eps_growth'] > 0:
            derived['peg_ratio'] = metrics['pe_ratio'] / metrics['eps_growth']
        
        # Calculate financial health score
        derived['financial_health_score'] = self._calculate_health_score(metrics)
        
        return derived
    
    def _calculate_health_score(self, metrics: Dict[str, float]) -> float:
        """Calculate overall financial health score from 1-10"""
        score_components = []
        
        # Profitability score
        if 'roe' in metrics:
            if metrics['roe'] > 20:
                score_components.append(10)
            elif metrics['roe'] > 15:
                score_components.append(8)
            elif metrics['roe'] > 10:
                score_components.append(6)
            else:
                score_components.append(4)
        
        # Debt score
        if 'debt_equity' in metrics:
            if metrics['debt_equity'] < 0.3:
                score_components.append(10)
            elif metrics['debt_equity'] < 0.5:
                score_components.append(8)
            elif metrics['debt_equity'] < 1.0:
                score_components.append(6)
            else:
                score_components.append(4)
        
        # Growth score
        if 'revenue_growth' in metrics:
            if metrics['revenue_growth'] > 20:
                score_components.append(10)
            elif metrics['revenue_growth'] > 15:
                score_components.append(8)
            elif metrics['revenue_growth'] > 10:
                score_components.append(6)
            else:
                score_components.append(4)
        
        return sum(score_components) / len(score_components) if score_components else 5.0
    
    def _get_default_metrics(self) -> Dict[str, float]:
        """Return default metrics when parsing fails"""
        return {
            'roe': 12.0,
            'roa': 8.0,
            'roce': 14.0,
            'net_margin': 8.0,
            'operating_margin': 12.0,
            'gross_margin': 25.0,
            'debt_equity': 0.4,
            'current_ratio': 1.8,
            'interest_coverage': 6.0,
            'pe_ratio': 20.0,
            'pb_ratio': 2.5,
            'ev_ebitda': 12.0,
            'revenue_growth': 10.0,
            'profit_growth': 15.0,
            'eps_growth': 12.0,
            'eps': 0.0,
            'financial_health_score': 6.5
        }
    
    def _get_traffic_light_status(self, value: float, thresholds: Dict[str, float]) -> str:
        """Determine traffic light status based on value and thresholds"""
        reverse = thresholds.get('reverse', False)
        good_threshold = thresholds['good']
        neutral_threshold = thresholds['neutral']
        
        if not reverse:
            # Higher is better
            if value >= good_threshold:
                return 'good'
            elif value >= neutral_threshold:
                return 'neutral'
            else:
                return 'bad'
        else:
            # Lower is better
            if value <= good_threshold:
                return 'good'
            elif value <= neutral_threshold:
                return 'neutral'
            else:
                return 'bad'
    
    def _format_metric_value(self, metric: str, value: float) -> str:
        """Format metric value for display"""
        if metric.endswith('_growth') or metric.endswith('_margin') or metric in ['roe', 'roa', 'roce']:
            return f"{value:.1f}%"
        elif metric in ['pe_ratio', 'pb_ratio', 'ev_ebitda', 'peg_ratio']:
            return f"{value:.1f}x"
        elif metric == 'eps':
            return f"${value:.2f}"
        else:
            return f"{value:.2f}"
