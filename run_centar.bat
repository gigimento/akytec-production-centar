@echo off
echo ========================================
echo   akYtec SMT Production Centar
echo ========================================
echo.
echo Pokretanje na portu 8501...
echo Otvori browser: http://localhost:8501
echo.
cd /d "%~dp0centar"
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
pause
