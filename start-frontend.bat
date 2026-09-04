@echo off
setlocal EnableExtensions EnableDelayedExpansion
cd /d "%~dp0"

set "FRONTEND_DIR=%~dp0frontend"
set "API_BASE=%~1"
if "%API_BASE%"=="" set "API_BASE=http://localhost:8000"

echo.
echo ========================================
echo   AnimAI Frontend
echo ========================================
echo.

where npm >nul 2>&1
if errorlevel 1 (
  echo ERROR: npm not found. Install Node.js 18+ ^(or 20+^) and ensure it is on PATH.
  pause
  exit /b 1
)

if not exist "%FRONTEND_DIR%\.env" (
  if exist "%FRONTEND_DIR%\.env.example" (
    echo Copying frontend\.env.example to frontend\.env ...
    copy /Y "%FRONTEND_DIR%\.env.example" "%FRONTEND_DIR%\.env" >nul
  )
)

if not exist "%FRONTEND_DIR%\node_modules\" (
  echo Running npm install in frontend ...
  pushd "%FRONTEND_DIR%"
  call npm install
  if errorlevel 1 (
    echo ERROR: npm install failed.
    popd
    pause
    exit /b 1
  )
  popd
)

REM Session override so a non-default backend port works without editing .env
set "VITE_API_BASE_URL=%API_BASE%"

echo.
echo Starting Vite dev server ...
echo Frontend: http://localhost:5173
echo API base: %VITE_API_BASE_URL%
echo.
echo Close this window to stop the frontend.
echo.

pushd "%FRONTEND_DIR%"
call npm run dev
set "EXITCODE=!errorlevel!"
popd
if not "!EXITCODE!"=="0" pause
exit /b !EXITCODE!
