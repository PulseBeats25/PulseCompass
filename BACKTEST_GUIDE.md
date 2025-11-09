# 📊 6-Month Backtesting Guide

Complete guide to validate your ranking model's performance against actual market returns.

---

## 🎯 What is Backtesting?

Backtesting validates your model by:
1. Taking historical rankings (6 months ago)
2. Fetching actual stock returns from Yahoo Finance
3. Calculating hit rate, alpha, and Sharpe ratio
4. Comparing top 10 picks vs Nifty 50 benchmark

**Goal:** Achieve 65%+ hit rate and 5%+ alpha

---

## 📋 Prerequisites

### 1. Install Required Packages

```bash
cd backend
pip install yfinance pandas numpy
```

### 2. Have Historical Snapshots

Snapshots are automatically created when you run analysis. Location:
```
data/performance_tracking/ranking_snapshots.json
```

---

## 🚀 Quick Start

### **Option 1: Interactive Mode** (Recommended)

```bash
cd backend
python scripts/run_backtest.py
```

**Interactive Menu:**
```
📊 6-MONTH BACKTESTING SYSTEM
================================================================================

✅ Found 5 snapshots
📅 Snapshots older than 6 months: 3

📋 Available Snapshots for Validation:
--------------------------------------------------------------------------------
1. 20250505_143000
   Date: 2025-05-05
   Philosophy: buffett
   Companies: 71
   Status: ⏳ Pending

🎯 What would you like to do?
1. Validate a specific snapshot
2. Validate all old snapshots
3. View performance report
4. Exit

Enter choice (1-4):
```

---

### **Option 2: Validate Specific Snapshot**

```bash
python scripts/run_backtest.py --snapshot-id 20250505_143000
```

---

### **Option 3: Validate All Old Snapshots**

```bash
python scripts/run_backtest.py --auto-validate-all
```

---

### **Option 4: View Performance Report**

```bash
python scripts/run_backtest.py --report
```

---

### **Option 5: Export Results to CSV**

```bash
python scripts/run_backtest.py --export
```

---

## 📊 Understanding Results

### **Sample Output:**

```
================================================================================
📊 VALIDATION RESULTS
================================================================================

🎯 Top 10 Performance:
   Average Return: +18.5%
   Benchmark (Nifty 50): +12.3%
   Alpha: +6.2%

📈 Success Metrics:
   Hit Rate: 70.0% (% beating benchmark)
   Win Rate: 90.0% (% positive returns)
   Sharpe Ratio: 1.45

🎲 Range:
   Best Performer: +45.8%
   Worst Performer: -5.2%
   Max Drawdown: -5.2%

================================================================================
💡 INTERPRETATION
================================================================================
✅ EXCELLENT: Hit rate >65% - Model is working well!
✅ EXCELLENT: Alpha >5% - Significantly beating market!
✅ EXCELLENT: Sharpe >1.0 - Good risk-adjusted returns

✅ Validation complete!
```

---

## 📈 Key Metrics Explained

### **1. Hit Rate**

**Definition:** % of top 10 stocks that beat the benchmark

**Formula:**
```python
hit_rate = (stocks_beating_nifty / 10) * 100
```

**Targets:**
- ✅ Excellent: >65%
- ⚠️ Good: 55-65%
- ❌ Poor: <55%

**Example:**
- Top 10 stocks: 7 beat Nifty 50, 3 underperformed
- Hit Rate: 70%

---

### **2. Alpha**

**Definition:** Excess return over benchmark

**Formula:**
```python
alpha = avg_return_top_10 - nifty_50_return
```

**Targets:**
- ✅ Excellent: >5%
- ⚠️ Good: 0-5%
- ❌ Poor: <0%

**Example:**
- Top 10 avg: +18.5%
- Nifty 50: +12.3%
- Alpha: +6.2% ✅

---

### **3. Sharpe Ratio**

**Definition:** Risk-adjusted returns

**Formula:**
```python
sharpe = (avg_return - risk_free_rate) / std_deviation
```

**Targets:**
- ✅ Excellent: >1.0
- ⚠️ Good: 0.5-1.0
- ❌ Poor: <0.5

**Example:**
- Avg return: 18.5%
- Risk-free: 6%
- StdDev: 8.6%
- Sharpe: (18.5 - 6) / 8.6 = 1.45 ✅

---

### **4. Win Rate**

**Definition:** % of stocks with positive returns

**Formula:**
```python
win_rate = (positive_returns / 10) * 100
```

**Targets:**
- ✅ Excellent: >70%
- ⚠️ Good: 50-70%
- ❌ Poor: <50%

---

## 🔄 Complete Workflow

### **Step 1: Create Snapshots** (Automatic)

```bash
# Start backend
python -m uvicorn main:app --reload

# Upload Excel file via frontend
# System automatically saves snapshot
```

**Snapshot Created:**
```json
{
  "snapshot_id": "20251105_193000",
  "timestamp": "2025-11-05T19:30:00",
  "philosophy": "buffett",
  "rankings": [...top 50 companies...],
  "summary": {
    "total_companies": 71,
    "avg_score": 45.2
  }
}
```

---

### **Step 2: Wait 6 Months** ⏰

Let time pass so we can measure actual returns...

---

### **Step 3: Run Backtest**

```bash
cd backend
python scripts/run_backtest.py
```

**What Happens:**
1. ✅ Loads snapshot from 6 months ago
2. ✅ Extracts top 50 stock symbols
3. ✅ Fetches actual returns from Yahoo Finance
4. ✅ Fetches Nifty 50 benchmark return
5. ✅ Calculates hit rate, alpha, Sharpe
6. ✅ Saves validation results
7. ✅ Displays performance report

---

### **Step 4: Analyze Results**

```bash
python scripts/run_backtest.py --report
```

**Output:**
```
📊 OVERALL PERFORMANCE REPORT
================================================================================

📈 Overall Statistics:
   Total Snapshots: 12
   Validated Snapshots: 8

🎯 Overall Metrics:
   Average Alpha: +7.2%
   Average Hit Rate: 68.5%
   Average Sharpe: 1.32
   Average Win Rate: 75.0%
   Consistency (StdDev): 3.5

📊 Performance by Philosophy:
   BUFFETT:
      Count: 5
      Avg Alpha: +8.5%
      Avg Hit Rate: 72.0%
      Avg Sharpe: 1.45

   LYNCH:
      Count: 3
      Avg Alpha: +5.2%
      Avg Hit Rate: 63.3%
      Avg Sharpe: 1.15

🏆 Best Snapshot:
   ID: 20250505_143000
   Date: 2025-05-05T14:30:00
   Alpha: +12.5%
   Hit Rate: 80.0%
```

---

## 🧪 Testing Without Waiting 6 Months

For immediate testing, you can manually edit snapshot timestamps:

### **1. Locate Snapshots File**

```
data/performance_tracking/ranking_snapshots.json
```

### **2. Edit Timestamp**

```json
{
  "snapshot_id": "20251105_193000",
  "timestamp": "2025-05-05T19:30:00",  // Changed to 6 months ago
  "philosophy": "buffett",
  ...
}
```

### **3. Run Backtest**

```bash
python scripts/run_backtest.py --snapshot-id 20251105_193000
```

**Note:** This fetches actual returns from May 2025 to Nov 2025

---

## 📊 Sample Backtest Results

### **Scenario 1: Excellent Model** ✅

```
🎯 Top 10 Performance:
   Average Return: +22.3%
   Benchmark (Nifty 50): +12.3%
   Alpha: +10.0%

📈 Success Metrics:
   Hit Rate: 80.0%
   Win Rate: 90.0%
   Sharpe Ratio: 1.65

💡 INTERPRETATION:
✅ EXCELLENT: Hit rate >65% - Model is working well!
✅ EXCELLENT: Alpha >5% - Significantly beating market!
✅ EXCELLENT: Sharpe >1.0 - Good risk-adjusted returns
```

**Action:** Model is validated! Use in production.

---

### **Scenario 2: Good Model** ⚠️

```
🎯 Top 10 Performance:
   Average Return: +15.8%
   Benchmark (Nifty 50): +12.3%
   Alpha: +3.5%

📈 Success Metrics:
   Hit Rate: 60.0%
   Win Rate: 70.0%
   Sharpe Ratio: 0.85

💡 INTERPRETATION:
⚠️ GOOD: Hit rate 55-65% - Model is decent but can improve
⚠️ GOOD: Positive alpha - Beating market slightly
⚠️ GOOD: Sharpe 0.5-1.0 - Acceptable risk-adjusted returns
```

**Action:** Model works but needs refinement. Adjust weights.

---

### **Scenario 3: Poor Model** ❌

```
🎯 Top 10 Performance:
   Average Return: +8.5%
   Benchmark (Nifty 50): +12.3%
   Alpha: -3.8%

📈 Success Metrics:
   Hit Rate: 40.0%
   Win Rate: 60.0%
   Sharpe Ratio: 0.35

💡 INTERPRETATION:
❌ POOR: Hit rate <55% - Model needs recalibration
❌ POOR: Negative alpha - Underperforming market
❌ POOR: Sharpe <0.5 - Poor risk-adjusted returns
```

**Action:** Model needs major recalibration. Review weights and penalties.

---

## 🔧 Troubleshooting

### **Issue 1: No Snapshots Found**

```
❌ No snapshots found!
```

**Solution:**
1. Run analysis via frontend to create snapshots
2. Check `data/performance_tracking/ranking_snapshots.json` exists

---

### **Issue 2: No Old Snapshots**

```
⚠️ No snapshots old enough for 6-month validation
```

**Solution:**
- Wait 6 months, OR
- Manually edit timestamps for testing

---

### **Issue 3: Yahoo Finance Errors**

```
❌ Error fetching TCS: No data available
```

**Solution:**
- Check internet connection
- Verify stock symbols are correct (NSE format)
- Some small-cap stocks may not have data
- System automatically retries with BSE

---

### **Issue 4: Import Errors**

```
❌ Error importing modules: No module named 'yfinance'
```

**Solution:**
```bash
pip install yfinance pandas numpy
```

---

## 📁 File Structure

```
backend/
├── scripts/
│   └── run_backtest.py          # Main backtesting script
├── utils/
│   ├── performance_tracking.py   # Snapshot management
│   └── market_data_fetcher.py    # Yahoo Finance integration
└── data/
    └── performance_tracking/
        ├── ranking_snapshots.json    # All snapshots
        └── backtest_results.csv      # Exported results
```

---

## 🎯 Success Criteria

Your model is **validated** if:

| Metric | Target | Your Result |
|--------|--------|-------------|
| **Hit Rate** | >65% | ? |
| **Alpha** | >5% | ? |
| **Sharpe Ratio** | >1.0 | ? |
| **Win Rate** | >70% | ? |
| **Consistency** | <5% StdDev | ? |

**If all targets met:** ✅ Model is production-ready!

---

## 📊 API Endpoints (Alternative)

You can also use API endpoints:

### **1. List Snapshots**

```bash
curl http://localhost:8000/api/v1/validation/snapshots
```

### **2. Validate Snapshot**

```bash
curl -X POST http://localhost:8000/api/v1/validation/validate-snapshot \
  -H "Content-Type: application/json" \
  -d '{
    "snapshot_id": "20250505_143000",
    "period_months": 6,
    "benchmark": "^NSEI"
  }'
```

### **3. Get Performance Report**

```bash
curl http://localhost:8000/api/v1/validation/performance-report
```

---

## 🚀 Next Steps After Validation

### **If Model Passes (>65% hit rate):**

1. ✅ Deploy to production
2. ✅ Set up quarterly re-validation
3. ✅ Monitor performance monthly
4. ✅ Create alerts for deteriorating stocks

### **If Model Needs Improvement (<65% hit rate):**

1. ⚠️ Analyze false positives (high-ranked but underperformed)
2. ⚠️ Analyze false negatives (low-ranked but outperformed)
3. ⚠️ Adjust philosophy weights
4. ⚠️ Strengthen disqualification rules
5. ⚠️ Re-run backtest

---

## 📞 Support

**Common Commands:**

```bash
# Interactive mode
python scripts/run_backtest.py

# Validate specific snapshot
python scripts/run_backtest.py --snapshot-id 20250505_143000

# Validate all
python scripts/run_backtest.py --auto-validate-all

# View report
python scripts/run_backtest.py --report

# Export to CSV
python scripts/run_backtest.py --export
```

**Need Help?**
- Check console output for detailed error messages
- Verify yfinance is installed
- Ensure internet connection for Yahoo Finance API
- Check snapshot file exists and is valid JSON

---

## ✅ Checklist

- [ ] Install yfinance: `pip install yfinance pandas`
- [ ] Have snapshots (run analysis to create)
- [ ] Wait 6 months OR edit timestamps for testing
- [ ] Run backtest: `python scripts/run_backtest.py`
- [ ] Check hit rate >65%
- [ ] Check alpha >5%
- [ ] Check Sharpe >1.0
- [ ] View performance report
- [ ] Export results to CSV
- [ ] Deploy if validated!

---

**Version:** 1.0  
**Last Updated:** November 5, 2025  
**Status:** Ready for Use ✅
