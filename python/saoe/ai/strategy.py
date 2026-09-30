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
    branching_strategy: str         # "reliability", "pseudocost", "gnn_guided", "strong", "mostfrac"
    cut_selection: str              # "all", "mir_learned", "sparse_only", "none"
    precision: str                  # "FP32", "FP64", "Adaptive"
    use_gpu: bool                   # True / False
    use_quantum_heuristics: bool    # True / False
    decomposition: Optional[str]    # "Benders", "Dantzig-Wolfe", None
    threads: int = 0                # 0 = auto
    tolerance: float = 1e-7
    time_limit: float = 0.0
    mip_gap: float = 1e-4

    def to_solver_options(self) -> Dict[str, Any]:
        """Maps Strategy to high-performance PRAMANA C++ kernel options."""
        # Map gnn_guided or custom branching rules to kernel-supported branching
        branch_rule = self.branching_strategy
        if branch_rule in ("gnn_guided", "hybrid_ai"):
            branch_rule = "reliability"
        elif branch_rule not in ("reliability", "pseudocost", "mostfrac", "strong"):
            branch_rule = "reliability"

        opts: Dict[str, Any] = {
            "algorithm": self.algorithm,
            "presolve": self.presolve_level != "none",
            "scale": self.scaling_enabled,
            "branching": branch_rule,
            "cuts": self.cut_selection != "none",
            "heuristics": True,
            "allow_gpu": self.use_gpu,
            "tolerance": self.tolerance,
            "threads": self.threads,
        }
        if self.time_limit > 0:
            opts["time_limit"] = self.time_limit
        if self.mip_gap > 0:
            opts["mip_gap"] = self.mip_gap

        return opts


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

        # Rule & Heuristic AI Synthesis based on Mathematical Autopsy
        algo = "auto"
        use_gpu = gpu_available and (autopsy.nnz >= 30000)
        presolve = "aggressive" if autopsy.sparsity_ratio > 0.95 else "standard"
        branching = "gnn_guided" if autopsy.num_binaries > 50 else "reliability"
        cuts = "mir_learned" if autopsy.num_integers > 0 else "none"
        use_quantum = autopsy.num_binaries > 15 and autopsy.integer_ratio > 0.25
        prec = "FP64" if autopsy.ill_conditioned else "Adaptive"

        if autopsy.is_qp:
            algo = "ipm"
        elif autopsy.num_integers > 0:
            algo = "bnb"
        elif use_gpu and autopsy.nnz > 80000:
            algo = "pdhg-gpu"
        elif autopsy.num_constraints > 5000 and autopsy.sparsity_ratio > 0.98:
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
