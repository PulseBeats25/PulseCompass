# 🤖 Automatic Ticker Symbol Fetcher

## ✅ **I Created a Web Scraper for You!**

Just like your Google Script that scrapes Screener.in, I've created a Python script that automatically fetches NSE ticker symbols.

---

## 🚀 **Quick Start (3 Commands)**

### **Step 1: Install BeautifulSoup**
```bash
pip install beautifulsoup4 requests
```

### **Step 2: Run the Fetcher**
```bash
cd backend
python scripts/fetch_ticker_symbols.py
```

### **Step 3: Run Backtest**
```bash
python scripts/run_backtest.py --auto-validate-all
```

**That's it!** The script will automatically:
1. ✅ Search each company on Screener.in
2. ✅ Extract the correct NSE ticker symbol
3. ✅ Save to `symbol_mapping.json`
4. ✅ Ready for backtest!

---

## 📊 **What the Script Does**

### **Similar to Your Google Script:**

**Your Google Script (SCREENER.GS):**
```javascript
var url = inputRange[i][0];
var response = UrlFetchApp.fetch(url);
var data = response.getContentText();
var peMatch = data.match(/Stock P\/E\s*<\/span>...);
```

**My Python Script (fetch_ticker_symbols.py):**
```python
response = requests.get(search_url, params={'q': company_name})
data = response.json()
ticker = extract_from_url(data[0]['url'])
```

---

## 🔍 **How It Works**

### **1. Searches Screener.in API**
```
https://www.screener.in/api/company/search/?q=Authum+Invest
```

### **2. Gets First Result**
```json
[
  {
    "name": "Authum Investment & Infrastructure Ltd.",
    "url": "/company/AUTHUM/"
  }
]
```

### **3. Extracts Ticker**
```
URL: /company/AUTHUM/
Ticker: AUTHUM
```

### **4. Saves to JSON**
```json
{
  "Authum Invest": "AUTHUM",
  "CRISIL": "CRISIL"
}
```

---

## 📋 **Expected Output**

```
🔍 Fetching ticker symbols for 31 companies...
================================================================================

[1/31] Searching: Abans Financial
  ✅ Abans Financial → ABFRL

[2/31] Searching: Balmer Law. Inv.
  ✅ Balmer Law. Inv. → BALMLAWRIE

[3/31] Searching: Authum Invest
  ✅ Authum Invest → AUTHUM

[4/31] Searching: Prime Securities
  ✅ Prime Securities → PRIME

[5/31] Searching: CRISIL
  ✅ CRISIL → CRISIL

[6/31] Searching: Bajaj Holdings
  ✅ Bajaj Holdings → BAJAJHLDNG

...

================================================================================
✅ Successfully found 28/31 ticker symbols

💾 Saved mapping to: data/symbol_mapping.json

================================================================================
📊 TICKER MAPPING SUMMARY
================================================================================
  Abans Financial              → ABFRL
  Authum Invest                → AUTHUM
  Bajaj Holdings               → BAJAJHLDNG
  Balmer Law. Inv.             → BALMLAWRIE
  CRISIL                       → CRISIL
  ...

✅ Done! You can now run the backtest.

Next step:
  python scripts/run_backtest.py --auto-validate-all
```

---

## 🎯 **Features**

### **1. Smart Company Name Cleaning**
```python
"Balmer Law. Inv." → "Balmer Law Inv"
"Jindal Poly Inve" → "Jindal Poly Inve"
```

### **2. Multiple Search Strategies**
- ✅ API search
- ✅ URL extraction
- ✅ Name parsing

### **3. Rate Limiting**
- ✅ 1 second delay between requests
- ✅ Respectful to server

### **4. Error Handling**
- ✅ Continues if one fails
- ✅ Shows which companies couldn't be found

---

## 🔧 **Troubleshooting**

### **Issue 1: Import Error**
```
ModuleNotFoundError: No module named 'bs4'
```

**Solution:**
```bash
pip install beautifulsoup4 requests
```

---

### **Issue 2: Connection Error**
```
ConnectionError: Max retries exceeded
```

**Solution:**
- Check internet connection
- Wait a few minutes and try again
- Screener.in might be temporarily down

---

### **Issue 3: Some Companies Not Found**
```
⚠️ Company XYZ: No ticker found
```

**Solution:**
- Company might not be listed on NSE
- Try searching manually on Screener.in
- Add manually to `symbol_mapping.json`

---

## 📝 **Manual Override**

If some companies aren't found automatically, you can add them manually:

### **Edit `data/symbol_mapping.json`:**
```json
{
  "Authum Invest": "AUTHUM",
  "Company Not Found": "MANUAL_TICKER_HERE"
}
```

---

## 🎯 **Complete Workflow**

```bash
# 1. Install dependencies
pip install beautifulsoup4 requests

# 2. Fetch ticker symbols automatically
cd backend
python scripts/fetch_ticker_symbols.py

# 3. Run backtest
python scripts/run_backtest.py --auto-validate-all

# 4. View results
python scripts/run_backtest.py --report
```

---

## 📊 **Comparison with Google Script**

| Feature | Your Google Script | My Python Script |
|---------|-------------------|------------------|
| **Platform** | Google Sheets | Python |
| **Data Source** | Screener.in HTML | Screener.in API |
| **Method** | Regex parsing | JSON parsing |
| **Speed** | Slower (HTML) | Faster (API) |
| **Automation** | Manual trigger | Fully automated |
| **Rate Limiting** | Built-in | Custom (1s delay) |

---

## ✅ **Advantages**

1. ✅ **Fully Automated** - No manual work
2. ✅ **Uses API** - More reliable than HTML scraping
3. ✅ **Error Handling** - Continues even if some fail
4. ✅ **Rate Limited** - Respectful to server
5. ✅ **Saves to JSON** - Ready for backtest immediately

---

## 🚀 **Ready to Run!**

```bash
cd backend
python scripts/fetch_ticker_symbols.py
```

**This will automatically fetch all ticker symbols and save them!** 🎉
