# Sovereign Adaptive Optimization Engine — SAOE (PRAMANA 2.0)

> **A from-scratch sovereign LP/MILP/QP optimization engine that analyzes the mathematical structure of every problem, automatically generates an execution strategy, dynamically selects algorithms and numerical precision, learns from previous solves, and exploits CPU/GPU/HPC resources to obtain high-quality certified solutions efficiently.**

---

## 🏛️ System Architecture

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│                         APPLICATION / USER LAYER                             │
│                                                                              │
│  Python API     C/C++ API     Rust API     CLI     REST API                 │
│       │             │            │          │          │                     │
└───────┴─────────────┴────────────┴──────────┴──────────┴─────────────────────┘
                                      │
                                      ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                         MODEL INGESTION LAYER                                │
│                                                                              │
│     LP Parser       MILP Parser       QP Parser       MPS / LP / JSON       │
│                                      │                                       │
│                                      ▼                                       │
│                         Model Validation Engine                              │
│                         • variable validation                                │
│                         • constraint validation                              │
│                         • bounds checking                                    │
│                         • coefficient validation                             │
└──────────────────────────────────────┬───────────────────────────────────────┘
                                       │
                                       ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                    MATHEMATICAL INTERMEDIATE REPRESENTATION                  │
│                              (Optimization IR)                               │
│                                                                              │
│       Variables ───── Constraints ───── Objective ───── Bounds              │
│            │                │               │                │               │
│            └────────────────┴───────────────┴────────────────┘               │
│                                      │                                       │
│                          Sparse Matrix Representation                        │
│                         CSR / CSC / Sparse Graph                             │
└──────────────────────────────────────┬───────────────────────────────────────┘
                                       │
                                       ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                         PROBLEM INTELLIGENCE                                │
│                                                                              │
│  ┌─────────────┐ ┌─────────────┐ ┌──────────────┐ ┌─────────────────────┐ │
│  │ Sparsity    │ │ Degeneracy  │ │ Conditioning │ │ Integer Structure   │ │
│  └─────────────┘ └─────────────┘ └──────────────┘ └─────────────────────┘ │
│                                                                              │
│  ┌─────────────┐ ┌─────────────┐ ┌──────────────┐ ┌─────────────────────┐ │
│  │ Symmetry    │ │ Block       │ │ Network      │ │ LP Relaxation       │ │
│  │ Detection   │ │ Detection   │ │ Structure    │ │ Strength             │ │
│  └─────────────┘ └─────────────┘ └──────────────┘ └─────────────────────┘ │
│                                                                              │
│                    Mathematical Graph Analyzer                              │
└──────────────────────────────────────┬───────────────────────────────────────┘
                                       │
                                       ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                    OPTIMIZATION STRATEGY ENGINE                              │
│                                                                              │
│                 ┌────────────────────────────────┐                           │
│                 │ Rule-Based Strategy Engine      │                           │
│                 └────────────────┬───────────────┘                           │
│                                  │                                           │
│                 ┌────────────────▼───────────────┐                           │
│                 │ AI Strategy Prediction Engine   │                           │
│                 │ • GNN                          │                           │
│                 │ • Meta-learning                │                           │
│                 │ • Historical performance       │                           │
│                 └────────────────┬───────────────┘                           │
│                                  │                                           │
│                 ┌────────────────▼───────────────┐                           │
│                 │ Strategy Search / Portfolio     │                           │
│                 │ • simplex                      │                           │
│                 │ • interior point               │                           │
│                 │ • branch & bound               │                           │
│                 │ • branch & cut                 │                           │
│                 │ • Benders                      │                           │
│                 │ • Dantzig-Wolfe                │                           │
│                 │ • heuristics                   │                           │
│                 └────────────────┬───────────────┘                           │
└──────────────────────────────────┼───────────────────────────────────────────┘
                                   │
                                   ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                          SOLVER ORCHESTRATOR                                 │
│                                                                              │
│      Decides dynamically:                                                    │
│                                                                              │
│      Algorithm │ Decomposition │ Cuts │ Branching │ Precision │ Hardware   │
│                                                                              │
│      Continuously monitors solver performance and can change strategy.       │
└─────────────┬──────────────────┬──────────────────┬─────────────────────────┘
              │                  │                  │
              ▼                  ▼                  ▼
┌────────────────────┐ ┌────────────────────┐ ┌────────────────────┐
│      LP ENGINE     │ │     MILP ENGINE    │ │      QP ENGINE     │
│                    │ │                    │ │                    │
│ Revised Simplex   │ │ Branch & Bound     │ │ Interior Point     │
│ Dual Simplex      │ │ Branch & Cut       │ │ Active Set         │
│ Interior Point    │ │ Cutting Planes     │ │ KKT System         │
│ Basis Management  │ │ Presolve           │ │ Convex QP           │
│                   │ │ Heuristics         │ │                    │
└─────────┬──────────┘ └─────────┬──────────┘ └─────────┬──────────┘
          │                      │                      │
          └──────────────────────┼──────────────────────┘
                                 │
                                 ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                        INTELLIGENT MILP LAYER                                │
│                                                                              │
│   AI Branching      AI Cut Selection       Conflict Learning               │
│        │                   │                       │                         │
│        └───────────────────┼───────────────────────┘                         │
│                            │                                                 │
│                    Learned Heuristics                                        │
│                            │                                                 │
│              Quantum-Inspired Subproblem Search                             │
└────────────────────────────────┬─────────────────────────────────────────────┘
                                 │
                                 ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                       DECOMPOSITION ENGINE                                   │
│                                                                              │
│         Automatic Structural Decomposition                                  │
│                                                                              │
│       ┌───────────────┬────────────────┬────────────────┐                    │
│       ▼               ▼                ▼                ▼                    │
│   Benders         Dantzig-Wolfe    Network Flow     Scenario Split          │
│       │               │                │                │                    │
│       └───────────────┴────────────────┴────────────────┘                    │
│                              │                                               │
│                         Parallel Solve                                       │
└────────────────────────────────┬─────────────────────────────────────────────┘
                                 │
                                 ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                       NUMERICAL CORE                                         │
│                                                                              │
│  Sparse BLAS │ Sparse LU │ Cholesky │ QR │ KKT Solver │ Matrix Factorization│
│                                                                              │
│  Scaling │ Pivoting │ Stability Detection │ Residual Monitoring             │
└────────────────────────────────┬─────────────────────────────────────────────┘
                                 │
                                 ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                     ADAPTIVE PRECISION ENGINE                                │
│                                                                              │
│             ┌────────┐       ┌────────┐       ┌──────────────┐              │
│             │ FP32   │ ────► │ FP64   │ ────► │ High Precision│             │
│             └────────┘       └────────┘       └──────────────┘              │
│                                                                              │
│         Precision increases only when numerical instability occurs.         │
└────────────────────────────────┬─────────────────────────────────────────────┘
                                 │
                                 ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                         COMPUTE RUNTIME                                      │
│                                                                              │
│        CPU                 GPU                  HPC Cluster                   │
│        │                   │                       │                         │
│   SIMD / AVX          CUDA / HIP             MPI / Distributed               │
│   Multi-threading     Sparse kernels         Work stealing                   │
│        │                   │                       │                         │
│        └───────────────────┴───────────────────────┘                         │
│                            │                                                 │
│                    Resource Scheduler                                         │
└────────────────────────────────┬─────────────────────────────────────────────┘
                                 │
                                 ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                         SOLUTION MANAGER                                     │
│                                                                              │
│     Primal Solution │ Dual Solution │ Objective │ Gap │ Certificates        │
│                                                                              │
│     Anytime Solution │ Feasibility │ Optimality Bound │ Runtime Statistics  │
└────────────────────────────────┬─────────────────────────────────────────────┘
                                 │
                                 ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                         LEARNING SYSTEM                                      │
│                                                                              │
│  Solver Telemetry → Feature Store → ML Training → Strategy Updates          │
│                                                                              │
│  Previous Solutions │ Branching Data │ Cut Performance │ Numerical Data      │
└──────────────────────────────────────────────────────────────────────────────┘
                                 │
                                 └──────────────► Strategy Engine
```

---

## ⚡ Key Features

1. **Optimization IR**: Unified intermediate representation for LP, MILP, QP, and MIQP models decoupling front-ends from computation.
2. **Mathematical Autopsy (Problem Intelligence)**: Deep pre-solve structural analysis assessing sparsity, condition numbers, integer tightness, and bipartite graph metrics.
3. **Adaptive Strategy Engine & Autopilot**: Real-time closed loop algorithm and precision selection (`Analyze → Plan → Solve → Measure → Adapt → Learn`).
4. **From-Scratch Numerical Kernel**: Certified C++20 engine with bounded simplex, interior-point, and custom CUDA PDHG kernels.
5. **Quantum-Inspired Layer**: QUBO / Ising simulated annealing for combinatorial subproblem acceleration.
6. **Automatic Decomposition Engine**: Automated detection and formulation of Benders and Dantzig-Wolfe partitions.
7. **Experience Store & Lifelong Learning**: Telemetry and strategy performance memory for continuous runtime improvement.

---

## 🚀 Quickstart

### Python API
```python
import saoe

# Build via Optimization IR
model = saoe.Model("refinery_demo", maximize=True)
x = model.add_variable("x", lb=0, ub=4, cost=3)
y = model.add_variable("y", lb=0, cost=5, integer=True)
model.add_constraint({x: 1, y: 2}, ub=8, name="capacity")

# Solve with closed-loop Optimization Autopilot
result = saoe.solve(model)
print(result.summary())
```

### CLI Execution
```bash
./build/pramana solve data/netlib/afiro.mps.gz
```

### Interactive TUI Console
```bash
PYTHONPATH="./python" python3 -m pramana.tui
```
