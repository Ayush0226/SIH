@echo off
echo ========================================================
echo Starting ComplyScan 2.0 (React PWA + Supabase Backend)
echo ========================================================

:: Set UTF-8 encoding so the AI progress bars don't crash Windows CMD
set PYTHONIOENCODING=utf-8

:: Start Backend in a new window
start "ComplyScan API (Backend)" cmd /k "cd backend && ..\venv\Scripts\uvicorn main:app --port 8000"

:: Start Frontend in a new window
start "ComplyScan UI (Frontend)" cmd /k "cd frontend && npm run dev"

echo Servers launched! 
echo Frontend is likely running at: http://localhost:5173 (Check the new UI window!)
echo Backend API is at: http://127.0.0.1:8000
pause
