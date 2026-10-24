@echo off
echo ============================================================
echo   SauceDemo Automation - Varshith Vasamsetti
echo   Website : https://www.saucedemo.com/
echo   Total   : 8 Test Cases
echo ============================================================
echo.

echo [Step 1] Activating virtual environment...
call .venv\Scripts\activate.bat
echo.

echo [Step 2] Running all 8 test cases with HTML report...
pytest test_saucedemo.py -v -s --tb=short ^
  --html=reports/saucedemo_report.html ^
  --self-contained-html
echo.

echo ============================================================
echo   Done!
echo   HTML Report : reports\saucedemo_report.html
echo   Screenshots : screenshots\
echo ============================================================
pause
