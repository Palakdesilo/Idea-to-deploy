@echo off
echo --- FIXING PYTHON ENVIRONMENT ---

echo 1. Cleaning up pycache...
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"

echo 2. Installing Hypercorn/Dependencies...
python -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo.
    echo ERROR: Could not install dependencies. Your Python installation might be corrupted.
    echo Try running: pip install --upgrade pip
    pause
    exit /b
)

echo 3. Starting Server...
python -m hypercorn main:app --bind 0.0.0.0:4000 --reload
pause
