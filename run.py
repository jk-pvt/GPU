#!/usr/bin/env python3
"""PRAMANA 2.0 / SAOE Universal Entrypoint.

Usage:
  python run.py                   # Launches interactive CLI with heading & menu
  python run.py --bench           # Check benchmark results right here
  python run.py --solve <model>   # Solve a model with autopilot or custom engine
  python run.py --autopsy <model> # Mathematical autopsy & problem intelligence
  python run.py --compare <model> # Compare all engines side-by-side
  python run.py --check           # Run full system self-check suite
  python run.py --tui             # Launch fullscreen interactive TUI
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PYTHON_DIR = ROOT / "python"
if str(PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(PYTHON_DIR))

from cli import main

if __name__ == "__main__":
    main()
