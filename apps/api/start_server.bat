@echo off
cd /d d:\Palak\Idea-to-deploy\apps\api
echo Starting API Server with Hypercorn (Python 3.13 compatible)...
python -m hypercorn main:app --bind 0.0.0.0:4000 --reload > server.log 2>&1
pause
