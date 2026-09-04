@echo off
setlocal EnableExtensions EnableDelayedExpansion
cd /d "%~dp0"

set "BACKEND_DIR=%~dp0backend"
set "PORT=%~1"
if "%PORT%"=="" set "PORT=8000"

echo.
echo ========================================
echo   AnimAI Backend
echo ========================================
echo.

where python >nul 2>&1
if errorlevel 1 (
  where py >nul 2>&1
  if errorlevel 1 (
    echo ERROR: Python not found. Install Python 3.11+ and ensure it is on PATH.
    pause
    exit /b 1
  )
  set "PY=py -3"
) else (
  set "PY=python"
)

set "NEED_INSTALL=0"
if not exist "%BACKEND_DIR%\.venv\Scripts\python.exe" (
  echo Creating virtual environment in backend\.venv ...
  pushd "%BACKEND_DIR%"
  %PY% -m venv .venv
  if errorlevel 1 (
    echo ERROR: Failed to create virtual environment.
    popd
    pause
    exit /b 1
  )
  popd
  set "NEED_INSTALL=1"
)

set "VENV_PY=%BACKEND_DIR%\.venv\Scripts\python.exe"
set "VENV_PIP=%BACKEND_DIR%\.venv\Scripts\pip.exe"

if "!NEED_INSTALL!"=="0" (
  "%VENV_PY%" -c "import uvicorn, fastapi" >nul 2>&1
  if errorlevel 1 set "NEED_INSTALL=1"
)

if "!NEED_INSTALL!"=="1" (
  echo Installing backend dependencies ^(pip install -e ".[dev]"^) ...
  pushd "%BACKEND_DIR%"
  "%VENV_PIP%" install -e ".[dev]"
  if errorlevel 1 (
    echo ERROR: pip install failed.
    popd
    pause
    exit /b 1
  )
  popd
) else (
  echo Backend dependencies already present.
)

if not exist "%BACKEND_DIR%\.env" (
  if exist "%BACKEND_DIR%\.env.example" (
    echo Copying backend\.env.example to backend\.env ...
    copy /Y "%BACKEND_DIR%\.env.example" "%BACKEND_DIR%\.env" >nul
  )
)

REM If launched alone with default 8000 and it is busy, try 8001.
if "%~1"=="" (
  call :port_listening %PORT%
  if not errorlevel 1 (
    echo Port %PORT% is already in use. Trying 8001 ...
    set "PORT=8001"
    call :port_listening !PORT!
    if not errorlevel 1 (
      echo ERROR: Ports 8000 and 8001 are both in use.
      echo Stop the other process or pass a free port: start-backend.bat 8002
      pause
      exit /b 1
    )
  )
) else (
  call :port_listening %PORT%
  if not errorlevel 1 (
    echo ERROR: Port %PORT% is already in use.
    echo Choose another port, e.g. start-backend.bat 8001
    pause
    exit /b 1
  )
)

echo.
echo Starting uvicorn on http://localhost:!PORT!
echo API docs: http://localhost:!PORT!/docs
echo.
echo Close this window to stop the backend.
echo.

pushd "%BACKEND_DIR%"
"%VENV_PY%" -m uvicorn app.main:app --reload --host 0.0.0.0 --port !PORT!
set "EXITCODE=!errorlevel!"
popd
if not "!EXITCODE!"=="0" pause
exit /b !EXITCODE!

:port_listening
REM Returns errorlevel 0 if something is LISTENING on the port, 1 if free.
netstat -ano 2>nul | findstr /C:":%~1 " | findstr /I "LISTENING" >nul
if errorlevel 1 (
  exit /b 1
) else (
  exit /b 0
)
