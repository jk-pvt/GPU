"""Optimization Intermediate Representation (IR).

Unifies LP, MILP, QP, MIQP mathematical structures across all parsers
and front-ends (Python, C/C++, MPS, JSON).
"""
from __future__ import annotations

import json
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Union
import pramana

INF = float("inf")


@dataclass
class Var:
    name: str
    index: int
    lb: float = 0.0
    ub: float = INF
    cost: float = 0.0
    integer: bool = False
    binary: bool = False

    def __hash__(self):
        return hash(self.index)

    def __repr__(self):
        t = "bin" if self.binary else ("int" if self.integer else "cont")
        return f"Var({self.name}:{t}, [{self.lb}, {self.ub}], cost={self.cost})"


@dataclass
class Constraint:
    name: str
    index: int
    terms: Dict[int, float]  # var_index -> coeff
    lb: float = -INF
    ub: float = INF

    def __repr__(self):
        return f"Constraint({self.name}, terms={len(self.terms)}, [{self.lb}, {self.ub}])"


class Model:
    """Sovereign Optimization Intermediate Representation Model."""

    def __init__(self, name: str = "saoe_model", maximize: bool = False):
        self.name = name
        self.maximize = maximize
        self.offset = 0.0
        self.variables: List[Var] = []
        self.constraints: List[Constraint] = []
        self.quadratic_terms: Dict[Tuple[int, int], float] = {}
        self._var_map: Dict[str, Var] = {}

    def add_variable(
        self,
        name: Optional[str] = None,
        lb: float = 0.0,
        ub: float = INF,
        cost: float = 0.0,
        integer: bool = False,
        binary: bool = False,
    ) -> Var:
        idx = len(self.variables)
        nm = name or f"x_{idx}"
        if binary:
            lb = max(lb, 0.0)
            ub = min(ub, 1.0)
            integer = True
        v = Var(name=nm, index=idx, lb=lb, ub=ub, cost=cost, integer=integer, binary=binary)
        self.variables.append(v)
        self._var_map[nm] = v
        return v

    def add_constraint(
        self,
        terms: Dict[Union[Var, int], float],
        lb: float = -INF,
        ub: float = INF,
        name: Optional[str] = None,
    ) -> Constraint:
        idx = len(self.constraints)
        nm = name or f"c_{idx}"
        term_map: Dict[int, float] = {}
        for k, coeff in terms.items():
            v_idx = k.index if isinstance(k, Var) else int(k)
            if coeff != 0.0:
                term_map[v_idx] = float(coeff)
        c = Constraint(name=nm, index=idx, terms=term_map, lb=lb, ub=ub)
        self.constraints.append(c)
        return c

    def add_quadratic(self, v1: Union[Var, int], v2: Union[Var, int], coeff: float):
        i = v1.index if isinstance(v1, Var) else int(v1)
        j = v2.index if isinstance(v2, Var) else int(v2)
        key = (min(i, j), max(i, j))
        self.quadratic_terms[key] = self.quadratic_terms.get(key, 0.0) + float(coeff)

    @property
    def num_variables(self) -> int:
        return len(self.variables)

    @property
    def num_constraints(self) -> int:
        return len(self.constraints)

    @property
    def num_integers(self) -> int:
        return sum(1 for v in self.variables if v.integer)

    @property
    def num_binaries(self) -> int:
        return sum(1 for v in self.variables if v.binary)

    @property
    def is_qp(self) -> bool:
        return len(self.quadratic_terms) > 0

    @property
    def is_milp(self) -> bool:
        return self.num_integers > 0 and not self.is_qp

    @property
    def is_lp(self) -> bool:
        return self.num_integers == 0 and not self.is_qp

    def to_pramana(self) -> pramana.Model:
        """Convert Optimization IR to native high-performance PRAMANA kernel."""
        pm = pramana.Model(self.name, maximize=self.maximize)
        pm.set_offset(self.offset)
        for v in self.variables:
            pm.add_var(lb=v.lb, ub=v.ub, cost=v.cost, integer=v.integer, name=v.name)
        
        # Build rows in pramana
        for c in self.constraints:
            coef_map = {}
            for v_idx, val in c.terms.items():
                coef_map[pm._vars[v_idx]] = val
            pm.add_constraint(coef_map, lb=c.lb, ub=c.ub, name=c.name)
        
        # Quadratic terms
        for (i, j), q_val in self.quadratic_terms.items():
            pm.add_quadratic(pm._vars[i], pm._vars[j], q_val)
            
        return pm

    @classmethod
    def from_mps(cls, mps_path: str) -> "Model":
        """Read standard MPS/QPS file into Optimization IR with complete structure."""
        from pramana.verify import parse_mps
        parsed = parse_mps(mps_path, exact=False)
        m = cls(name=parsed.name or Path(mps_path).stem, maximize=parsed.maximize)
        m.offset = float(parsed.offset)

        # Build variables
        for j, cname in enumerate(parsed.col_names):
            clo = float(parsed.clo[j]) if parsed.clo[j] is not None else -INF
            cup = float(parsed.cup[j]) if parsed.cup[j] is not None else INF
            cost = float(parsed.cost[j]) if j < len(parsed.cost) else 0.0
            is_int = bool(parsed.integer[j]) if j < len(parsed.integer) else False
            is_bin = is_int and (clo == 0.0) and (cup == 1.0)
            m.add_variable(name=cname, lb=clo, ub=cup, cost=cost, integer=is_int, binary=is_bin)

        # Build constraints
        # parsed.cols is list of dict {row_idx: val}
        row_terms: List[Dict[int, float]] = [{} for _ in range(parsed.m)]
        for j, col_dict in enumerate(parsed.cols):
            for row_idx, val in col_dict.items():
                if val != 0.0:
                    row_terms[row_idx][j] = float(val)

        for i, rname in enumerate(parsed.row_names):
            rlo = float(parsed.rlo[i]) if parsed.rlo[i] is not None else -INF
            rup = float(parsed.rup[i]) if parsed.rup[i] is not None else INF
            m.add_constraint(row_terms[i], lb=rlo, ub=rup, name=rname)

        # Quadratic terms
        if hasattr(parsed, "q") and parsed.q:
            for (i, j), val in parsed.q.items():
                m.add_quadratic(i, j, float(val))

        return m
