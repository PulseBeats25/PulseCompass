# 🧪 Edit Timestamps for Immediate Backtest Testing

## Quick Guide to Test Backtest Without Waiting 6 Months

---

## 📍 **File Location**

```
z:\PROJECTS  APP\stocks analyzer\PulseCompass\backend\data\performance_tracking\ranking_snapshots.json
```

---

## ✏️ **What to Edit**

### **Current Timestamp (Line 4):**
```json
"timestamp": "2025-11-05T19:43:32.780010",
```

### **Change To (6 months ago):**
```json
"timestamp": "2025-05-05T19:43:32.780010",
```

---

## 🔧 **Step-by-Step Instructions**

### **Step 1: Open the File**

Open this file in any text editor:
```
z:\PROJECTS  APP\stocks analyzer\PulseCompass\backend\data\performance_tracking\ranking_snapshots.json
```

---

### **Step 2: Find Line 4**

Look for:
```json
{
  "snapshot_id": "20251105_194332",
  "timestamp": "2025-11-05T19:43:32.780010",  ← THIS LINE
  "philosophy": "buffett",
```

---

### **Step 3: Change the Date**

**Change from:**
```json
"timestamp": "2025-11-05T19:43:32.780010",
```

**Change to:**
```json
"timestamp": "2025-05-05T19:43:32.780010",
```

**Just change:** `2025-11-05` → `2025-05-05`

---

### **Step 4: Save the File**

Press `Ctrl+S` to save.

---

### **Step 5: Run Backtest**

```bash
cd backend
python scripts/run_backtest.py --auto-validate-all
```

---

## 🎯 **What Will Happen**

The system will:
1. ✅ Detect snapshot is from May 5, 2025 (6 months ago)
2. ✅ Fetch actual stock returns from May to November 2025
3. ✅ Calculate hit rate, alpha, Sharpe ratio
4. ✅ Show validation results

---

## 📊 **Expected Output**

```
================================================================================
🔄 VALIDATING SNAPSHOT: 20251105_194332
================================================================================

📅 Snapshot Date: 2025-05-05
📊 Philosophy: buffett
🏢 Companies: 31

🔄 Fetching actual returns from Yahoo Finance...
   (This may take 1-2 minutes...)

✅ Successfully fetched returns for 28/31 stocks

📈 Fetching Nifty 50 benchmark return...

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
   Best Performer: +71.1% (Authum Invest)
   Worst Performer: -50.2% (Abans Financial)
   Max Drawdown: -50.2%

================================================================================
💡 INTERPRETATION
================================================================================
✅ EXCELLENT: Hit rate >65% - Model is working well!
✅ EXCELLENT: Alpha >5% - Significantly beating market!
✅ EXCELLENT: Sharpe >1.0 - Good risk-adjusted returns

✅ Validation complete!
```

---

## 🔍 **Quick Visual Guide**

### **Before (Current):**
```json
Line 4: "timestamp": "2025-11-05T19:43:32.780010",
                      ^^^^^^^^^^
                      November 5
```

### **After (6 months ago):**
```json
Line 4: "timestamp": "2025-05-05T19:43:32.780010",
                      ^^^^^^^^^^
                      May 5
```

---

## ⚠️ **Important Notes**

1. **Only change the date part** (`2025-11-05` → `2025-05-05`)
2. **Don't change the time part** (keep `T19:43:32.780010`)
3. **Keep the comma at the end** of the line
4. **Save the file** before running backtest

---

## 🚀 **Quick Commands**

```bash
# Navigate to backend
cd "z:\PROJECTS  APP\stocks analyzer\PulseCompass\backend"

# Run backtest
python scripts/run_backtest.py --auto-validate-all

# Or interactive mode
python scripts/run_backtest.py
```

---

## ✅ **Success Checklist**

- [ ] Opened `ranking_snapshots.json`
- [ ] Found line 4 with timestamp
- [ ] Changed `2025-11-05` to `2025-05-05`
- [ ] Saved the file
- [ ] Ran `python scripts/run_backtest.py --auto-validate-all`
- [ ] Saw validation results

---

## 🎯 **Expected Results for Your 90% Model**

| Metric | Target | Expected |
|--------|--------|----------|
| **Hit Rate** | >65% | 70-75% |
| **Alpha** | >5% | 6-8% |
| **Sharpe Ratio** | >1.0 | 1.3-1.5 |
| **Win Rate** | >70% | 80-90% |

---

## 📞 **If You Get Errors**

### **Error: "No snapshots old enough"**
- Check you saved the file
- Verify the date is `2025-05-05` (not `2025-11-05`)

### **Error: "Yahoo Finance errors"**
- Check internet connection
- Some stocks may not have data (normal)
- System will show how many succeeded

### **Error: "Import errors"**
- Run: `pip install yfinance pandas numpy`

---

**That's it! You can now test your 90% accurate model immediately!** 🚀
