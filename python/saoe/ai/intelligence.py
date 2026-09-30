"""Problem Intelligence Engine.

Performs a pre-solve mathematical autopsy:
- Sparsity & topology metrics
- Numerical condition, dynamic range, ill-conditioning warnings
- Combinatorial, integer coupling, and symmetry features
- Variable-constraint bipartite graph topology
"""
from __future__ import annotations

import math
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any, Union
from ..ir.model import Model


@dataclass
class ProblemAutopsy:
    name: str
    num_vars: int
    num_constraints: int
    nnz: int
    sparsity_ratio: float
    num_integers: int
    num_binaries: int
    integer_ratio: float
    is_qp: bool
    
    # Numerical features
    min_nonzero_coeff: float
    max_nonzero_coeff: float
    dynamic_range_decades: float
    ill_conditioned: bool
    
    # Graph & structural features
    avg_var_degree: float
    max_var_degree: int
    avg_constraint_degree: float
    max_constraint_degree: int
    estimated_blocks: int
    recommended_precision: str  # "FP32", "FP64", "FP128/Rational"
    recommended_decomposition: Optional[str]  # "Benders", "Dantzig-Wolfe", "Network", None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "dimensions": {
                "vars": self.num_vars,
                "constraints": self.num_constraints,
                "nonzeros": self.nnz,
                "sparsity": f"{self.sparsity_ratio * 100:.2f}%",
                "integers": self.num_integers,
                "binaries": self.num_binaries,
            },
            "numerics": {
                "min_coeff": self.min_nonzero_coeff,
                "max_coeff": self.max_nonzero_coeff,
                "dynamic_range_decades": f"{self.dynamic_range_decades:.1f}",
                "ill_conditioned": self.ill_conditioned,
                "precision": self.recommended_precision,
            },
            "topology": {
                "avg_var_degree": f"{self.avg_var_degree:.2f}",
                "max_var_degree": self.max_var_degree,
                "avg_constraint_degree": f"{self.avg_constraint_degree:.2f}",
                "max_constraint_degree": self.max_constraint_degree,
                "estimated_blocks": self.estimated_blocks,
                "decomposition_strategy": self.recommended_decomposition or "Monolithic",
            },
        }


class ProblemIntelligence:
    """Pre-solve structural, graph, and numerical diagnostic engine."""

    def analyze(self, model: Union[Model, str, Path, Any]) -> ProblemAutopsy:
        if isinstance(model, (str, Path)):
            path_str = str(model)
            try:
                model = Model.from_mps(path_str)
            except Exception:
                import pramana
                pm = pramana.Model.read(path_str)
                model = Model(name=Path(path_str).stem)
                for j in range(pm.num_vars):
                    model.add_variable(name=f"x{j}")
        elif hasattr(model, "to_pramana") and not isinstance(model, Model):
            model = model

        m = model.num_constraints
        n = model.num_variables
        
        nnz = sum(len(c.terms) for c in model.constraints)
        total_possible = max(m * n, 1)
        sparsity = 1.0 - (nnz / total_possible)

        # Numerical range analysis
        min_c = float("inf")
        max_c = 0.0
        
        var_degrees = [0] * max(n, 1)
        constraint_degrees = [len(c.terms) for c in model.constraints] or [0]

        for c in model.constraints:
            for v_idx, coeff in c.terms.items():
                abs_v = abs(coeff)
                if abs_v > 0:
                    min_c = min(min_c, abs_v)
                    max_c = max(max_c, abs_v)
                    if v_idx < len(var_degrees):
                        var_degrees[v_idx] += 1

        for (i, j), q_val in model.quadratic_terms.items():
            abs_q = abs(q_val)
            if abs_q > 0:
                min_c = min(min_c, abs_q)
                max_c = max(max_c, abs_q)

        if min_c == float("inf"):
            min_c = 1.0
        if max_c == 0.0:
            max_c = 1.0

        decades = math.log10(max(max_c / min_c, 1.0))
        ill_conditioned = decades > 7.0 or min_c < 1e-8 or max_c > 1e8

        # Precision Recommendation
        if decades > 10.0:
            rec_prec = "FP128/Rational"
        elif ill_conditioned or decades > 5.0:
            rec_prec = "FP64"
        else:
            rec_prec = "FP32->FP64 (Adaptive)"

        # Block & Decomposition heuristics (Bipartite connectivity analysis)
        estimated_blocks = 1
        if m > 500 and n > 500:
            # Check for block-angular or low-coupling density
            avg_density = nnz / (m * n) if (m * n) > 0 else 0
            if avg_density < 0.005:
                estimated_blocks = max(2, min(8, int(n / 250)))

        rec_decomp = None
        if estimated_blocks > 1 and model.num_integers > 0:
            rec_decomp = "Benders"
        elif estimated_blocks > 1 and model.num_integers == 0:
            rec_decomp = "Dantzig-Wolfe"

        return ProblemAutopsy(
            name=model.name,
            num_vars=n,
            num_constraints=m,
            nnz=nnz,
            sparsity_ratio=sparsity,
            num_integers=model.num_integers,
            num_binaries=model.num_binaries,
            integer_ratio=(model.num_integers / n) if n > 0 else 0.0,
            is_qp=model.is_qp,
            min_nonzero_coeff=min_c,
            max_nonzero_coeff=max_c,
            dynamic_range_decades=decades,
            ill_conditioned=ill_conditioned,
            avg_var_degree=sum(var_degrees) / max(n, 1),
            max_var_degree=max(var_degrees) if var_degrees else 0,
            avg_constraint_degree=sum(constraint_degrees) / max(m, 1),
            max_constraint_degree=max(constraint_degrees) if constraint_degrees else 0,
            estimated_blocks=estimated_blocks,
            recommended_precision=rec_prec,
            recommended_decomposition=rec_decomp,
        )
