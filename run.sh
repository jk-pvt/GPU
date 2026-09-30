#!/usr/bin/env bash
# ==============================================================================
# SolverX — Single-Command Launcher (macOS & Linux)
# Installs required packages, verifies native C++20 solver, and launches CLI.
# Usage:
#   ./run.sh                  (interactive menu with heading & prompts)
#   ./run.sh --bench          (check benchmark results directly)
#   ./run.sh --solve <file>   (solve optimization model)
# ==============================================================================
set -e
cd "$(dirname "$0")"

# 1. Detect Python 3.8+
PY=""
for candidate in python3 python; do
  if command -v "$candidate" >/dev/null 2>&1; then
    if "$candidate" -c "import sys; assert sys.version_info >= (3, 8)" >/dev/null 2>&1; then
      PY="$candidate"
      break
    fi
  fi
done

if [ -z "$PY" ]; then
  echo "Error: Python 3.8+ is required. Please install Python 3.8 or newer."
  exit 1
fi

# 2. Virtual environment setup & dependency check
if [ ! -d ".venv" ]; then
  # Create a clean lightweight virtual environment if in externally managed env
  if ! "$PY" -c "import pytest, scipy, numpy" >/dev/null 2>&1; then
    echo "Creating virtual environment .venv and verifying dependencies..."
    "$PY" -m venv .venv 2>/dev/null || true
  fi
fi

if [ -f ".venv/bin/python" ]; then
  PY=".venv/bin/python"
fi

# Install requirements if pip is available
if [ -f "requirements.txt" ]; then
  "$PY" -m pip install -r requirements.txt >/dev/null 2>&1 || true
fi

# 3. Build native solver if missing
mkdir -p build
if [ ! -f "build/pramana" ] || [ ! -f "build/libpramana.dylib" -a ! -f "build/libpramana.so" ]; then
  echo "Building PRAMANA native solver engine (incremental C++20)..."
  cmake -S . -B build -DCMAKE_BUILD_TYPE=Release >build/start_build.log 2>&1 && cmake --build build -j >>build/start_build.log 2>&1 || true
fi

# 4. Prepare benchmark datasets if missing
if [ ! -f "data/netlib/afiro.mps.gz" ]; then
  "$PY" bench/fetch_data.py netlib netlib-infeas miplib3 maros >/dev/null 2>&1 || true
fi
if [ ! -f "data/gen/plan_10x12.mps" ]; then
  "$PY" gen/refinery.py suite --out data/gen >/dev/null 2>&1 || true
fi
if [ ! -f "data/adversarial/scaled_afiro.mps" ]; then
  "$PY" gen/adversarial.py --out data/adversarial >/dev/null 2>&1 || true
fi

# 5. Launch interactive CLI
export PYTHONPATH="$PWD/python:${PYTHONPATH:-}"
exec "$PY" cli.py "$@"
