@echo off
rem ==============================================================================
rem SolverX — Single-Command Launcher (Windows)
rem Installs required packages, verifies native C++20 solver, and launches CLI.
rem Usage:
rem   run.bat                  (interactive menu with heading & prompts)
rem   run.bat --bench          (check benchmark results directly)
rem   run.bat --solve <file>   (solve optimization model)
rem ==============================================================================
setlocal EnableDelayedExpansion
cd /d "%~dp0"
chcp 65001 >nul
title SolverX

rem ---- 1. Locate Python --------------------------------------------------------
set PYEXE=
set PYARGS=
if defined PYTHON (
  "%PYTHON%" -c "import sys" >nul 2>nul && set "PYEXE=%PYTHON%"
)
if not defined PYEXE (
  python -c "import sys; assert sys.version_info >= (3, 8)" >nul 2>nul && set PYEXE=python
)
if not defined PYEXE (
  for %%v in (3.14 3.13 3.12 3.11 3.10 3.9 3) do (
    if not defined PYEXE (
      py -%%v -c "import sys" >nul 2>nul && (set PYEXE=py& set PYARGS=-%%v)
    )
  )
)
if not defined PYEXE (
  echo [!] Python 3.8+ not found. Please install Python from python.org or Microsoft Store.
  exit /b 1
)

rem ---- 2. Virtual Environment & Dependencies -----------------------------------
if exist ".venv\Scripts\python.exe" (
  set "PYEXE=.venv\Scripts\python.exe"
  set PYARGS=
) else (
  "!PYEXE!" !PYARGS! -c "import pytest, scipy, numpy" >nul 2>nul
  if errorlevel 1 (
    echo [*] Creating virtual environment .venv and installing required packages...
    "!PYEXE!" !PYARGS! -m venv .venv >nul 2>nul
    if exist ".venv\Scripts\python.exe" (
      set "PYEXE=.venv\Scripts\python.exe"
      set PYARGS=
    )
  )
)

if exist "requirements.txt" (
  "!PYEXE!" !PYARGS! -m pip install -r requirements.txt >nul 2>nul
)

rem ---- 3. Incremental Build of Native C++20 Solver -----------------------------
if not exist "build\pramana.exe" (
  echo [*] Building native PRAMANA kernel...
  call "%~dp0build.bat" > build\start_build.log 2>&1
  if errorlevel 1 (
    if not exist "build\pramana.exe" (
      echo [!] Warning: Could not compile native kernel (requires MSVC / Visual Studio).
    )
  )
)

rem ---- 4. Check Benchmark Datasets ---------------------------------------------
if not exist "data\netlib\afiro.mps.gz" (
  "!PYEXE!" !PYARGS! bench\fetch_data.py netlib netlib-infeas miplib3 maros >nul 2>nul
)
if not exist "data\gen\plan_10x12.mps" (
  "!PYEXE!" !PYARGS! gen\refinery.py suite --out data\gen >nul 2>nul
)
if not exist "data\adversarial\scaled_afiro.mps" (
  "!PYEXE!" !PYARGS! gen\adversarial.py --out data\adversarial >nul 2>nul
)

rem ---- 5. Launch CLI -----------------------------------------------------------
set "PYTHONPATH=%~dp0python;%PYTHONPATH%"
"!PYEXE!" !PYARGS! cli.py %*
exit /b %ERRORLEVEL%
