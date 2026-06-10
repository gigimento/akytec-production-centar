@echo off
echo ========================================
echo   akYtec TV Dashboard
echo ========================================
echo.
echo Pokretanje na portu 8502...
echo Otvori browser: http://localhost:8502
echo.
cd /d "%~dp0tv"
streamlit run app.py --server.port 8502 --server.address 0.0.0.0
pause
