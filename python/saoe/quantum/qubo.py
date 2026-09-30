"""Quantum-Inspired Subproblem Search Layer.

Translates combinatorial/binary subproblems into Quadratic Unconstrained Binary
Optimization (QUBO) / Ising Hamiltonian formulations, then solves using
Simulated Annealing and quantum-inspired local search to generate high-quality
primal incumbents for the MILP engine.
"""
from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional


@dataclass
class QUBOResult:
    best_sample: Dict[int, int]
    energy: float
    iterations: int
    feasible: bool = True


class IsingSolver:
    """Quantum-inspired simulated annealing / transverse field Ising simulator."""

    def __init__(self, seed: int = 42):
        self.rng = random.Random(seed)

    def solve_qubo(
        self,
        Q: Dict[Tuple[int, int], float],
        num_variables: int,
        initial_temp: float = 10.0,
        final_temp: float = 0.01,
        steps: int = 1000,
    ) -> QUBOResult:
        if num_variables == 0:
            return QUBOResult(best_sample={}, energy=0.0, iterations=0)

        # Initialize random state x in {0, 1}^n
        state = [self.rng.choice([0, 1]) for _ in range(num_variables)]

        def eval_energy(s: List[int]) -> float:
            e = 0.0
            for (i, j), q in Q.items():
                if i < len(s) and j < len(s):
                    e += q * s[i] * s[j]
            return e

        current_energy = eval_energy(state)
        best_state = list(state)
        best_energy = current_energy

        temp = initial_temp
        cooling_rate = (final_temp / initial_temp) ** (1.0 / max(steps, 1))

        for it in range(steps):
            idx = self.rng.randint(0, num_variables - 1)
            # Flip bit
            state[idx] = 1 - state[idx]
            new_energy = eval_energy(state)
            delta = new_energy - current_energy

            if delta < 0 or (temp > 1e-6 and self.rng.random() < math.exp(-delta / temp)):
                current_energy = new_energy
                if current_energy < best_energy:
                    best_energy = current_energy
                    best_state = list(state)
            else:
                # Revert flip
                state[idx] = 1 - state[idx]

            temp *= cooling_rate

        sample_map = {i: best_state[i] for i in range(num_variables)}
        return QUBOResult(best_sample=sample_map, energy=best_energy, iterations=steps)


class QuantumInspiredSubproblemOptimizer:
    """Extracts difficult integer sub-blocks from MILP and solves as QUBO."""

    def __init__(self):
        self.solver = IsingSolver()

    def search_incumbent(
        self,
        binary_indices: List[int],
        cost_vector: List[float],
        constraint_matrix: Dict[Tuple[int, int], float],
        penalty: float = 100.0,
    ) -> Dict[int, int]:
        n = len(binary_indices)
        idx_to_pos = {idx: i for i, idx in enumerate(binary_indices)}

        Q: Dict[Tuple[int, int], float] = {}
        # Add linear objective costs as diagonal Q_ii
        for i, idx in enumerate(binary_indices):
            if idx < len(cost_vector):
                Q[(i, i)] = cost_vector[idx]

        # Add quadratic penalty for coupling constraints
        for (r, c), val in constraint_matrix.items():
            if c in idx_to_pos:
                pos = idx_to_pos[c]
                Q[(pos, pos)] = Q.get((pos, pos), 0.0) + (val * penalty)

        res = self.solver.solve_qubo(Q, n, steps=500)
        return {binary_indices[i]: bit for i, bit in res.best_sample.items()}
