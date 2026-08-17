@echo off
cd /d "%~dp0"
set "PYTHONIOENCODING=utf-8"

if not exist ".venv\Scripts\python.exe" (
  echo [1/2] Creating the local Python environment...
  py -3 -m venv .venv >nul 2>nul
  if errorlevel 1 python -m venv .venv
  if errorlevel 1 goto :setup_error

  echo [2/2] Installing required packages...
  ".venv\Scripts\python.exe" -m pip install -r requirements.txt
  if errorlevel 1 goto :setup_error
)

start "" http://127.0.0.1:4173/
".venv\Scripts\python.exe" server.py
pause
exit /b 0

:setup_error
echo.
echo Setup failed. Please install Python 3.10 or later and try again.
pause
exit /b 1
