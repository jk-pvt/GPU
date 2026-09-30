# SolverX — Sovereign Adaptive Optimization Engine (SAOE)
from __future__ import annotations

import os
import sys
from pathlib import Path

# Bring in native PRAMANA kernel bindings
from pramana import (
    Model as PramanaModel,
    Result as PramanaResult,
    Var as PramanaVar,
    solve_file,
    parametric,
    family,
    gpu_info,
    load_library,
    version,
)

from .ir.model import Model, Var, Constraint
from .ai.strategy import StrategyEngine, OptimizationStrategy
from .ai.intelligence import ProblemIntelligence, ProblemAutopsy
from .quantum.qubo import QuantumInspiredSubproblemOptimizer, IsingSolver
from .decomposition.engine import DecompositionEngine
from .learning.memory import LearningMemory, ExperienceStore
from .orchestrator import SolverOrchestrator

__version__ = "2.0.0-saoe"
__all__ = [
    "Model",
    "Var",
    "Constraint",
    "SolverOrchestrator",
    "StrategyEngine",
    "ProblemIntelligence",
    "ProblemAutopsy",
    "QuantumInspiredSubproblemOptimizer",
    "IsingSolver",
    "DecompositionEngine",
    "LearningMemory",
    "ExperienceStore",
    "solve",
    "autopsy",
]


def solve(model_or_path, **kwargs):
    """Sovereign Autopilot Solve: Analyze -> Plan -> Solve -> Measure -> Adapt -> Learn."""
    orchestrator = SolverOrchestrator()
    return orchestrator.solve(model_or_path, **kwargs)


def autopsy(model_or_path):
    """Perform mathematical autopsy and structural intelligence inspection."""
    intelligence = ProblemIntelligence()
    return intelligence.analyze(model_or_path)
