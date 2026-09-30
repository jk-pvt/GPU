"""Optimization Strategy Engine.

Synthesizes structural problem autopsy + historical memory + hardware capabilities
into an executable optimization strategy configuration.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from .intelligence import ProblemAutopsy
from ..learning.memory import LearningMemory


@dataclass
class OptimizationStrategy:
    algorithm: str                  # "auto", "dual", "ipm", "pdhg-gpu", "pdhg-cpu", "bnb", "race"
    presolve_level: str             # "aggressive", "standard", "none"
    scaling_enabled: bool           # True / False
    branching_strategy: str         # "reliability", "pseudocost", "gnn_guided", "strong"
    cut_selection: str              # "all", "mir_learned", "sparse_only", "none"
    precision: str                  # "FP32", "FP64", "Adaptive"
    use_gpu: bool                   # True / False
    use_quantum_heuristics: bool    # True / False
    decomposition: Optional[str]    # "Benders", "Dantzig-Wolfe", None
    threads: int = 0                # 0 = auto
    tolerance: float = 1e-7

    def to_solver_options(self) -> Dict[str, Any]:
        """Maps Strategy to PRAMANA kernel options."""
        return {
            "algorithm": self.algorithm,
            "presolve": self.presolve_level != "none",
            "scale": self.scaling_enabled,
            "branching": "reliability" if self.branching_strategy == "gnn_guided" else self.branching_strategy,
            "cuts": self.cut_selection != "none",
            "heuristics": True,
            "allow_gpu": self.use_gpu,
            "tolerance": self.tolerance,
        }


class StrategyEngine:
    """Strategy synthesis & meta-learning engine."""

    def __init__(self, memory: Optional[LearningMemory] = None):
        self.memory = memory or LearningMemory()

    def generate_strategy(
        self,
        autopsy: ProblemAutopsy,
        gpu_available: bool = False,
        user_overrides: Optional[Dict[str, Any]] = None,
    ) -> OptimizationStrategy:
        # Check if experience store has matching fingerprint
        historical_strategy = self.memory.query_strategy(autopsy)
        if historical_strategy and not user_overrides:
            return historical_strategy

        # Rule & Heuristic AI Synthesis
        algo = "auto"
        use_gpu = gpu_available and (autopsy.nnz > 30000)
        presolve = "aggressive" if autopsy.sparsity_ratio > 0.95 else "standard"
        branching = "gnn_guided" if autopsy.num_binaries > 50 else "reliability"
        cuts = "mir_learned" if autopsy.num_integers > 0 else "none"
        use_quantum = autopsy.num_binaries > 20 and autopsy.integer_ratio > 0.3
        prec = "FP64" if autopsy.ill_conditioned else "Adaptive"

        if autopsy.is_qp:
            algo = "ipm"
        elif autopsy.num_integers > 0:
            algo = "bnb"
        elif use_gpu and autopsy.nnz > 100000:
            algo = "pdhg-gpu"
        elif autopsy.sparsity_ratio > 0.99:
            algo = "dual"
        else:
            algo = "auto"

        strat = OptimizationStrategy(
            algorithm=algo,
            presolve_level=presolve,
            scaling_enabled=True,
            branching_strategy=branching,
            cut_selection=cuts,
            precision=prec,
            use_gpu=use_gpu,
            use_quantum_heuristics=use_quantum,
            decomposition=autopsy.recommended_decomposition,
            threads=0,
            tolerance=1e-7 if not autopsy.ill_conditioned else 1e-9,
        )

        if user_overrides:
            for k, v in user_overrides.items():
                if hasattr(strat, k):
                    setattr(strat, k, v)

        return strat
