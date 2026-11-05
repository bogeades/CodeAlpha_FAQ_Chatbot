@echo off
title CodeAlpha FAQ Chatbot - ResolveAI Assistant
echo ===================================================
echo     CodeAlpha AI Internship - FAQ Chatbot
echo ===================================================
echo.

where python >nul 2>nul
if %errorlevel% neq 0 (
    set "PYTHON_CMD=C:\Users\dessa\AppData\Local\Programs\Python\Python311\python.exe"
) else (
    set "PYTHON_CMD=python"
)

echo Starting FastAPI Server and React UI...
echo.
echo Application will be available at: http://localhost:8000
echo API Documentation available at:   http://localhost:8000/docs
echo.
"%PYTHON_CMD%" run.py --server --port 8000
pause
