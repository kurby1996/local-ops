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

REM --detach returns immediately; the console window can then close.
if defined PYARGS (
  "%PYEXE%" %PYARGS% server.py --detach --no-browser
) else (
  "%PYEXE%" server.py --detach --no-browser
)
set "ERR=%ERRORLEVEL%"
if not "%ERR%"=="0" (
  echo.
  echo server.py exited with code %ERR%
  pause
)
exit /b %ERR%
