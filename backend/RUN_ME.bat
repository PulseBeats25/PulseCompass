@echo off
echo ================================================================================
echo    AUTOMATIC TICKER SYMBOL FETCHER
echo ================================================================================
echo.
echo This will automatically fetch NSE ticker symbols from Screener.in
echo.
echo Step 1: Installing dependencies...
pip install beautifulsoup4 requests --quiet

echo.
echo Step 2: Fetching ticker symbols...
python scripts\fetch_ticker_symbols.py

echo.
echo Step 3: Running backtest...
python scripts\run_backtest.py --auto-validate-all

echo.
echo ================================================================================
echo    DONE!
echo ================================================================================
pause
