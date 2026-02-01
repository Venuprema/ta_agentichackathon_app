@echo off
cd /d "%~dp0"

REM Prefer venv if it exists
if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" -m streamlit run streamlit_app.py %*
    goto :eof
)

REM Otherwise use py launcher (Windows)
py -m streamlit run streamlit_app.py %*
if %ERRORLEVEL% equ 0 goto :eof

REM Fallback: python from PATH
python -m streamlit run streamlit_app.py %*
