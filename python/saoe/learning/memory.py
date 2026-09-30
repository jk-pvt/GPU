"""Learning Memory & Experience Store.

Captures solve telemetry, problem fingerprints, and performance outcomes,
enabling continuous strategy refinement and transfer learning across solves.
"""
from __future__ import annotations

import json
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any


@dataclass
class SolveExperience:
    fingerprint: str
    dimensions: Dict[str, Any]
    strategy_used: Dict[str, Any]
    runtime_seconds: float
    status: str
    gap: float
    iterations: int


class ExperienceStore:
    """Persistent experience and feature store for lifelong solver learning."""

    def __init__(self, store_path: Optional[str] = None):
        self.store_path = Path(store_path) if store_path else Path.home() / ".pramana" / "experience_store.json"
        self.experiences: List[SolveExperience] = []
        self._load()

    def _load(self):
        if self.store_path.exists():
            try:
                with open(self.store_path, "r") as f:
                    data = json.load(f)
                    for item in data:
                        self.experiences.append(SolveExperience(**item))
            except Exception:
                pass

    def record(self, exp: SolveExperience):
        self.experiences.append(exp)
        self._save()

    def _save(self):
        try:
            self.store_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.store_path, "w") as f:
                json.dump([asdict(e) for e in self.experiences[-500:]], f, indent=2)
        except Exception:
            pass


class LearningMemory:
    """Experience-based solver query interface."""

    def __init__(self, store: Optional[ExperienceStore] = None):
        self.store = store or ExperienceStore()

    def query_strategy(self, autopsy) -> Optional[Any]:
        # Return historical strategy if identical structure solved previously
        for exp in reversed(self.store.experiences):
            if (
                exp.dimensions.get("vars") == autopsy.num_vars
                and exp.dimensions.get("constraints") == autopsy.num_constraints
                and exp.dimensions.get("integers") == autopsy.num_integers
                and exp.status == "OPTIMAL"
            ):
                from ..ai.strategy import OptimizationStrategy
                return OptimizationStrategy(
                    algorithm=exp.strategy_used.get("algorithm", "auto"),
                    presolve_level=exp.strategy_used.get("presolve_level", "standard"),
                    scaling_enabled=exp.strategy_used.get("scaling_enabled", True),
                    branching_strategy=exp.strategy_used.get("branching_strategy", "reliability"),
                    cut_selection=exp.strategy_used.get("cut_selection", "all"),
                    precision=exp.strategy_used.get("precision", "Adaptive"),
                    use_gpu=exp.strategy_used.get("use_gpu", False),
                    use_quantum_heuristics=exp.strategy_used.get("use_quantum_heuristics", False),
                    decomposition=exp.strategy_used.get("decomposition"),
                    tolerance=exp.strategy_used.get("tolerance", 1e-7),
                )
        return None
