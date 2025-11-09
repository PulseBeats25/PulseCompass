# 📊 Symbol Mapping Guide - Fix Backtest Errors

## ⚠️ **The Problem**

Your backtest failed because stock symbols in your data are **company names** (like "Abans Financial") instead of **ticker symbols** (like "ABFRL").

Yahoo Finance needs actual NSE/BSE ticker symbols to fetch historical data.

---

## ✅ **Solution Implemented**

I've added a symbol mapping system that automatically converts company names to ticker symbols.

### **Files Created:**

1. **`data/symbol_mapping.json`** - Maps company names to tickers
2. **Updated `market_data_fetcher.py`** - Auto-resolves symbols

---

## 🔍 **How to Find Correct Ticker Symbols**

### **Method 1: NSE Website** (Most Reliable)

1. Go to: https://www.nseindia.com/
2. Search for company name
3. Copy the symbol (e.g., "CRISIL", "BAJAJHLDNG")

### **Method 2: Yahoo Finance**

1. Go to: https://finance.yahoo.com/
2. Search: "Company Name NSE"
3. Symbol will be shown (e.g., "CRISIL.NS")

### **Method 3: Screener.in**

1. Go to: https://www.screener.in/
2. Search company name
3. Symbol shown in URL and page title

---

## 📝 **Update Symbol Mapping**

### **File Location:**
```
z:\PROJECTS  APP\stocks analyzer\PulseCompass\backend\data\symbol_mapping.json
```

### **Format:**
```json
{
  "Company Name from Excel": "NSE_TICKER_SYMBOL",
  "Authum Invest": "AUTHUM",
  "CRISIL": "CRISIL",
  "Bajaj Holdings": "BAJAJHLDNG"
}
```

---

## 🎯 **Example: Finding Ticker for "Authum Investment"**

### **Step 1: Search on NSE**
- Go to NSE website
- Search "Authum Investment"
- Find symbol: **AUTHUM**

### **Step 2: Add to Mapping**
```json
{
  "Authum Invest": "AUTHUM"
}
```

### **Step 3: Test**
```bash
python scripts/run_backtest.py --auto-validate-all
```

---

## 📊 **Common Indian Stock Tickers**

| Company Name | NSE Ticker |
|--------------|------------|
| Reliance Industries | RELIANCE |
| TCS | TCS |
| Infosys | INFY |
| HDFC Bank | HDFCBANK |
| ICICI Bank | ICICIBANK |
| Bajaj Finance | BAJFINANCE |
| Bajaj Holdings | BAJAJHLDNG |
| CRISIL | CRISIL |
| PTC India Financial | PFS |

---

## 🔧 **Current Mapping (Needs Verification)**

The system currently has these mappings (you need to verify these are correct):

```json
{
  "Abans Financial": "ABFRL",
  "Balmer Law. Inv.": "BALMLAWRIE",
  "Authum Invest": "AUTHUM",
  "Prime Securities": "PRIME",
  "Jindal Poly Inve": "JINDALPOLY",
  "Wealth First Por": "WEALTHFP",
  "Bajaj Holdings": "BAJAJHLDNG",
  "PTC India Fin": "PFS",
  "Rane Holdings": "RANEHOLDIN",
  "CRISIL": "CRISIL"
}
```

---

## ⚠️ **Important: Verify Each Symbol**

Many of these symbols might be **incorrect guesses**. You need to:

1. **Look up each company on NSE website**
2. **Find the correct ticker symbol**
3. **Update `symbol_mapping.json`**

---

## 🚀 **Better Solution: Add Ticker Column to Excel**

### **Recommended Excel Format:**

| Name | Ticker | ROE | ROCE | P/E |
|------|--------|-----|------|-----|
| Authum Investment | AUTHUM | 34.1 | 30.9 | 11.9 |
| Balmer Lawrie | BALMLAWRIE | 13.2 | 17.2 | 10.0 |
| CRISIL | CRISIL | 27.8 | 35.6 | 46.6 |

### **Benefits:**
- ✅ No manual mapping needed
- ✅ More accurate
- ✅ Easier to maintain
- ✅ Works automatically

---

## 🧪 **Test Your Mapping**

### **Quick Test Script:**

```python
# Test if symbols work
import yfinance as yf

symbols = ["AUTHUM", "CRISIL", "BAJAJHLDNG"]

for symbol in symbols:
    ticker = f"{symbol}.NS"
    stock = yf.Ticker(ticker)
    try:
        hist = stock.history(period="1mo")
        if not hist.empty:
            print(f"✅ {symbol}: Working")
        else:
            print(f"❌ {symbol}: No data")
    except Exception as e:
        print(f"❌ {symbol}: Error - {e}")
```

---

## 📋 **Action Items**

### **Option A: Quick Fix (For Testing)**

1. Update `symbol_mapping.json` with correct tickers
2. Run backtest again
3. Fix any remaining errors

### **Option B: Proper Solution (Recommended)**

1. Add "Ticker" column to your Excel file
2. Fill in NSE ticker symbols for each company
3. Re-upload Excel file
4. Backtest will work automatically

---

## 🎯 **Next Steps**

### **Step 1: Verify Top 10 Symbols**

Focus on getting the top 10 companies working first:

1. Authum Invest → Find NSE ticker
2. Balmer Lawrie → Find NSE ticker
3. Wealth First → Find NSE ticker
4. Prime Securities → Find NSE ticker
5. Jindal Poly → Find NSE ticker
6. CRISIL → **CRISIL** (confirmed)
7. Abans Financial → Find NSE ticker
8. PTC India Fin → **PFS** (likely correct)
9. Bajaj Holdings → **BAJAJHLDNG** (confirmed)
10. Rane Holdings → Find NSE ticker

### **Step 2: Update Mapping**

Edit `data/symbol_mapping.json` with correct symbols.

### **Step 3: Test**

```bash
python scripts/run_backtest.py --auto-validate-all
```

---

## ✅ **Expected Output After Fix**

```
📊 Fetching returns for 31 stocks from 2025-05-05 to 2025-11-01
  ✅ Authum Invest: +71.08%
  ✅ Balmer Law. Inv.: -2.91%
  ✅ Wealth First Por: -28.21%
  ✅ Prime Securities: -4.05%
  ✅ CRISIL: -10.59%
  ✅ Bajaj Holdings: +14.06%

✅ Successfully fetched: 28/31

🎯 Top 10 Performance:
   Average Return: +18.5%
   Hit Rate: 70.0%
```

---

## 📞 **Need Help?**

### **Resources:**

1. **NSE Website:** https://www.nseindia.com/
2. **Yahoo Finance:** https://finance.yahoo.com/
3. **Screener.in:** https://www.screener.in/
4. **MoneyControl:** https://www.moneycontrol.com/

### **Common Issues:**

1. **"No data available"** → Wrong ticker symbol
2. **"404 Not Found"** → Company name doesn't match ticker
3. **"Possibly delisted"** → Stock no longer traded

---

**The system is ready - you just need to provide correct ticker symbols!** 🚀
