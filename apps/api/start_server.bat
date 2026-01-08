@echo off
cd /d d:\Palak\Idea-to-deploy\apps\api
echo Starting API Server...
python -m uvicorn main:app --reload --port 4000 --host 0.0.0.0 > server.log 2>&1
pause
