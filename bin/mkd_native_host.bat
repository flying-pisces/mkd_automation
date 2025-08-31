@echo off
setlocal
cd /d "C:\project\mkd_automation"

:: Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python not found in PATH
    echo Please ensure Python 3.8+ is installed and accessible
    exit /b 1
)

:: Check if project directory exists
if not exist "C:\project\mkd_automation" (
    echo Error: Project directory not found: C:\project\mkd_automation
    exit /b 1
)

:: Set PYTHONPATH to include src directory
set PYTHONPATH=C:\project\mkd_automation\src;%PYTHONPATH%

:: Launch the native host with logging
python -m mkd_v2.native_host.host %*

:: Exit with the same code as Python
exit /b %errorlevel%
