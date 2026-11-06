@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo Creating virtual environment...
    python -m venv .venv
    if errorlevel 1 goto :error
)

echo Installing dependencies...
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto :error

echo Starting Agent Learning from Zero...
".venv\Scripts\python.exe" run.py
goto :eof

:error
echo.
echo Setup failed. Please check Python 3.10+ installation and network access.
pause
