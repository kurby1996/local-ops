@echo off
setlocal EnableExtensions
cd /d "%~dp0"

set "PYEXE="
set "PYARGS="

where py >nul 2>nul
if not errorlevel 1 (
  set "PYEXE=py"
  set "PYARGS=-3"
)
if not defined PYEXE (
  where python >nul 2>nul
  if not errorlevel 1 set "PYEXE=python"
)

if not defined PYEXE (
  echo ERROR: Python 3.12+ not found.
  echo Install official Python and check Add python.exe to PATH.
  pause
  exit /b 127
)

echo Stopping this project's console...
if defined PYARGS (
  "%PYEXE%" %PYARGS% server.py --stop
) else (
  "%PYEXE%" server.py --stop
)
set "ERR=%ERRORLEVEL%"
echo.
if not "%ERR%"=="0" (
  echo stop failed with code %ERR%
)
pause
exit /b %ERR%
