@echo off
if not exist "data" mkdir "data"
xcopy "apps\api\data" "data" /E /I /Y
rmdir /S /Q "apps\api"
rmdir /S /Q "packages\engine"
rmdir /S /Q "packages\types"
echo Cleanup Done > cleanup_done.txt
