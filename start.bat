@echo off
setlocal EnableExtensions EnableDelayedExpansion
cd /d "%~dp0"

echo.
echo ========================================
echo   AnimAI - start everything
echo ========================================
echo.

set "BACKEND_PORT=8000"
call :port_listening 8000
if not errorlevel 1 (
  echo Port 8000 is already in use. Trying 8001 for the backend ...
  set "BACKEND_PORT=8001"
  call :port_listening 8001
  if not errorlevel 1 (
    echo ERROR: Ports 8000 and 8001 are both in use.
    echo Free a port or run start-backend.bat with another port.
    echo Another project may already be using 8000 - this script will not kill it.
    pause
    exit /b 1
  )
)

set "API_BASE=http://localhost:!BACKEND_PORT!"

echo Launching backend in a new window ^(port !BACKEND_PORT!^) ...
start "AnimAI Backend" cmd /k ""%~dp0start-backend.bat" !BACKEND_PORT!"

echo Launching frontend in a new window ...
start "AnimAI Frontend" cmd /k ""%~dp0start-frontend.bat" !API_BASE!"

echo.
echo ----------------------------------------
echo   Frontend:  http://localhost:5173
echo   API docs:  http://localhost:!BACKEND_PORT!/docs
echo ----------------------------------------
echo.
echo Two new console windows were opened ^(backend + frontend^).
echo Close those windows to stop the servers.
echo.
if not "!BACKEND_PORT!"=="8000" (
  echo NOTE: Backend is on !BACKEND_PORT! because 8000 was busy.
  echo       Frontend was pointed at !API_BASE! for this session.
  echo.
)
pause
exit /b 0

:port_listening
REM Returns errorlevel 0 if something is LISTENING on the port, 1 if free.
netstat -ano 2>nul | findstr /C:":%~1 " | findstr /I "LISTENING" >nul
if errorlevel 1 (
  exit /b 1
) else (
  exit /b 0
)
