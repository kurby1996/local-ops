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

echo Starting console...
if defined PYARGS (
  "%PYEXE%" %PYARGS% server.py
) else (
  "%PYEXE%" server.py
)
set "ERR=%ERRORLEVEL%"
if not "%ERR%"=="0" (
  echo.
  echo server.py exited with code %ERR%
  pause
)
exit /b %ERR%
