# 🚀 6-Month Backtest - Quick Start

## 📦 Install (One-Time)

```bash
cd backend
pip install yfinance pandas numpy
```

---

## 🎯 Run Backtest (3 Steps)

### **Step 1: Check Snapshots**

```bash
python scripts/run_backtest.py
```

**Output:**
```
✅ Found 5 snapshots
📅 Snapshots older than 6 months: 3
```

---

### **Step 2: Validate**

**Option A - Interactive:**
```bash
python scripts/run_backtest.py
# Choose option 1 or 2
```

**Option B - Auto:**
```bash
python scripts/run_backtest.py --auto-validate-all
```

---

### **Step 3: View Results**

```bash
python scripts/run_backtest.py --report
```

---

## 📊 Success Criteria

| Metric | Target | Status |
|--------|--------|--------|
| Hit Rate | >65% | ? |
| Alpha | >5% | ? |
| Sharpe | >1.0 | ? |

**All green?** ✅ Model validated!

---

## 🧪 Test Without Waiting 6 Months

### **1. Edit Timestamp**

File: `data/performance_tracking/ranking_snapshots.json`

```json
{
  "timestamp": "2025-05-05T19:30:00"  // Change to 6 months ago
}
```

### **2. Run Backtest**

```bash
python scripts/run_backtest.py
```

---

## 🔧 Troubleshooting

**No snapshots?**
→ Run analysis via frontend first

**No old snapshots?**
→ Edit timestamps OR wait 6 months

**Import errors?**
→ `pip install yfinance pandas`

**Yahoo Finance errors?**
→ Check internet connection

---

## 📞 Quick Commands

```bash
# Interactive
python scripts/run_backtest.py

# Specific snapshot
python scripts/run_backtest.py --snapshot-id 20250505_143000

# All snapshots
python scripts/run_backtest.py --auto-validate-all

# Report only
python scripts/run_backtest.py --report

# Export CSV
python scripts/run_backtest.py --export
```

---

## ✅ Done!

Your model is validated if:
- ✅ Hit Rate >65%
- ✅ Alpha >5%
- ✅ Sharpe >1.0

**Next:** Deploy to production! 🚀
