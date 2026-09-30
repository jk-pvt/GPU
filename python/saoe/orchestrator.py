"""Sovereign Solver Orchestrator.

Executes the closed-loop optimization cycle:
Analyze -> Plan -> Solve -> Measure -> Adapt -> Learn -> Solve Better
"""
from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Dict, Any, Optional, Union
from .ir.model import Model
from .ai.intelligence import ProblemIntelligence, ProblemAutopsy
from .ai.strategy import StrategyEngine, OptimizationStrategy
from .learning.memory import LearningMemory, SolveExperience
import pramana


@dataclass
class OrchestratedResult:
    status: str
    objective: float
    best_bound: float
    gap: float
    certified: bool
    runtime_seconds: float
    autopsy: ProblemAutopsy
    strategy: OptimizationStrategy
    native_result: pramana.Result

    def summary(self) -> str:
        lines = [
            "============================================================",
            "   SOVEREIGN ADAPTIVE OPTIMIZATION ENGINE (SAOE) RESULT",
            "============================================================",
            f"Model:           {self.autopsy.name} ({self.autopsy.num_vars} vars, {self.autopsy.num_constraints} cons)",
            f"Strategy Plan:   Algo: {self.strategy.algorithm} | GPU: {self.strategy.use_gpu} | Prec: {self.strategy.precision}",
            f"Solve Status:    {self.status}",
            f"Objective:       {self.objective:.12g}",
            f"Certified Bound: {self.best_bound:.12g}",
            f"Relative Gap:    {self.gap:.3e}",
            f"Certified Proof: {'✓ ACCEPTED' if self.certified else '✗ REJECTED'}",
            f"Runtime:         {self.runtime_seconds:.4f}s",
            "============================================================",
        ]
        return "\n".join(lines)


class SolverOrchestrator:
    """The central closed-loop intelligence brain of SAOE."""

    def __init__(self):
        self.intelligence = ProblemIntelligence()
        self.memory = LearningMemory()
        self.strategy_engine = StrategyEngine(memory=self.memory)

    def solve(
        self,
        model_input: Union[Model, str, pramana.Model],
        **user_options,
    ) -> OrchestratedResult:
        # Step 1: Ingest into IR or load
        if isinstance(model_input, str):
            native_model = pramana.Model.read(model_input)
            ir_model = Model(name=model_input)
            for j in range(native_model.num_vars):
                ir_model.add_variable(name=f"x{j}")
        elif isinstance(model_input, Model):
            ir_model = model_input
            native_model = model_input.to_pramana()
        elif isinstance(model_input, pramana.Model):
            native_model = model_input
            ir_model = Model(name="pramana_model")
            for j in range(native_model.num_vars):
                ir_model.add_variable(name=f"x{j}")
        else:
            raise TypeError("Expected Model, path str, or pramana.Model")

        # Step 2: Problem Intelligence Autopsy
        t0 = time.time()
        autopsy = self.intelligence.analyze(ir_model)

        # Step 3: Hardware detection
        gpu_info = pramana.gpu_info()
        gpu_available = gpu_info.get("available", False)

        # Step 4: Strategy Formulation
        strategy = self.strategy_engine.generate_strategy(
            autopsy,
            gpu_available=gpu_available,
            user_overrides=user_options,
        )

        # Step 5: Execute on high-performance native PRAMANA core
        solver_opts = strategy.to_solver_options()
        r = native_model.solve(**solver_opts)
        elapsed = time.time() - t0

        # Step 6: Learning & Feedback
        exp = SolveExperience(
            fingerprint=f"{autopsy.num_vars}x{autopsy.num_constraints}",
            dimensions=autopsy.to_dict()["dimensions"],
            strategy_used=strategy.__dict__,
            runtime_seconds=elapsed,
            status=r.status,
            gap=getattr(r, "relative_gap", 0.0),
            iterations=0,
        )
        self.memory.store.record(exp)

        return OrchestratedResult(
            status=r.status,
            objective=r.objective,
            best_bound=r.bound,
            gap=abs(r.objective - r.bound) / max(1.0, abs(r.objective)) if r.bound != float("-inf") else 0.0,
            certified=r.certified,
            runtime_seconds=elapsed,
            autopsy=autopsy,
            strategy=strategy,
            native_result=r,
        )
