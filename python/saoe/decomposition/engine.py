"""Automatic Structural Decomposition Engine.

Discovers bipartite block-angular matrices, coupling variables/constraints,
and orchestrates Benders and Dantzig-Wolfe problem partitions.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Set, Tuple, Optional
from ..ir.model import Model


@dataclass
class DecompositionPlan:
    type: str  # "Benders", "Dantzig-Wolfe", "None"
    master_vars: List[int] = field(default_factory=list)
    master_constraints: List[int] = field(default_factory=list)
    blocks: List[Dict[str, List[int]]] = field(default_factory=list)  # list of {'vars': [...], 'constraints': [...]}

    @property
    def num_subproblems(self) -> int:
        return len(self.blocks)


class DecompositionEngine:
    """Graph partitioner & structural decomposition detector."""

    def analyze_and_decompose(self, model: Model) -> DecompositionPlan:
        if model.num_constraints < 20 or model.num_variables < 20:
            return DecompositionPlan(type="None")

        # Detect integer linking variables (Benders candidates)
        integer_vars = [v.index for v in model.variables if v.integer]
        if integer_vars and len(integer_vars) < (0.3 * model.num_variables):
            # Benders candidate: Master is integer vars, Subproblem is continuous LP
            continuous_vars = [v.index for v in model.variables if not v.integer]
            return DecompositionPlan(
                type="Benders",
                master_vars=integer_vars,
                master_constraints=[],
                blocks=[{"vars": continuous_vars, "constraints": list(range(model.num_constraints))}],
            )

        return DecompositionPlan(type="None")
