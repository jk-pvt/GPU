# SolverX — Sovereign Adaptive Optimization Engine (SAOE 2.0)

> **SolverX is a from-scratch sovereign LP/MILP/QP optimization engine that analyzes the mathematical structure of every problem, automatically generates an execution strategy, dynamically selects algorithms and numerical precision, learns from previous solves, and exploits CPU/GPU/HPC resources to obtain high-quality certified solutions efficiently.**

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

### Single-Command Interactive CLI (Universal for macOS, Windows & Linux)
Runs on any device, automatically installs required dependencies, builds native components if needed, prompts for inputs, and provides direct benchmark checking:

- **macOS / Linux:**
  ```bash
  ./run.sh
  ```
- **Windows:**
  ```cmd
  run.bat
  ```
- **Universal (Python 3.8+):**
  ```bash
  python run.py
  ```

#### Direct CLI Commands & Benchmark Checking
```bash
# Check verified benchmark results directly in CLI
./run.sh --bench          # (or run.bat --bench / python run.py --bench)

# Solve a model with automatic engine routing
./run.sh --solve data/netlib/afiro.mps.gz --algo auto

# Perform mathematical structural autopsy
./run.sh --autopsy data/gen/plan_10x12.mps

# Compare all engines (Simplex, IPM, PDHG) side-by-side
./run.sh --compare data/netlib/afiro.mps.gz

# Run system self-check suite
./run.sh --check
```

### Python API & Architecture Reference (`solverx` / `saoe`)

The `solverx` (also aliased as `saoe`) package provides high-level intermediate representation, automated closed-loop optimization orchestration, structural autopsy, quantum-inspired combinatorial optimization, decomposition algorithms, and memory stores.

```python
import solverx  # or 'import saoe'
```

#### Package Exports (`solverx.__all__`)

| Export Symbol | Module | Description |
|---|---|---|
| [`Model`](file:///Users/jk/Desktop/GPU/python/saoe/ir/model.py) | `saoe.ir.model` | Intermediate representation optimization model (LP / MILP / QP) |
| [`Var`](file:///Users/jk/Desktop/GPU/python/saoe/ir/model.py) | `saoe.ir.model` | Decision variable representation with bounds, types (continuous/integer/binary), costs |
| [`Constraint`](file:///Users/jk/Desktop/GPU/python/saoe/ir/model.py) | `saoe.ir.model` | Linear and quadratic constraint specification with LHS/RHS bounds |
| [`solve()`](file:///Users/jk/Desktop/GPU/python/saoe/__init__.py) | `saoe` | High-level closed loop autopilot: `Analyze -> Plan -> Solve -> Measure -> Adapt -> Learn` |
| [`autopsy()`](file:///Users/jk/Desktop/GPU/python/saoe/__init__.py) | `saoe` | Mathematical structural autopsy inspecting sparsity, rank, condition number, graphs |
| [`SolverOrchestrator`](file:///Users/jk/Desktop/GPU/python/saoe/orchestrator.py) | `saoe.orchestrator` | Central solver orchestration brain coordinating intelligence, strategy, and solve loop |
| [`StrategyEngine`](file:///Users/jk/Desktop/GPU/python/saoe/ai/strategy.py) | `saoe.ai.strategy` | AI-assisted and rule-based strategy selector choosing precision, cuts, and solvers |
| [`OptimizationStrategy`](file:///Users/jk/Desktop/GPU/python/saoe/ai/strategy.py) | `saoe.ai.strategy` | Dataclass describing algorithm choice, hardware device, numerical precision, cuts |
| [`ProblemIntelligence`](file:///Users/jk/Desktop/GPU/python/saoe/ai/intelligence.py) | `saoe.ai.intelligence` | Mathematical autopsy engine calculating graph degrees, dynamic range, conditioning |
| [`ProblemAutopsy`](file:///Users/jk/Desktop/GPU/python/saoe/ai/intelligence.py) | `saoe.ai.intelligence` | Structured diagnostic report of model characteristics and suggested decompositions |
| [`QuantumInspiredSubproblemOptimizer`](file:///Users/jk/Desktop/GPU/python/saoe/quantum/qubo.py) | `saoe.quantum.qubo` | QUBO / Ising annealing solver for combinatorial binary subproblems |
| [`IsingSolver`](file:///Users/jk/Desktop/GPU/python/saoe/quantum/qubo.py) | `saoe.quantum.qubo` | Spin-glass simulated quantum annealing engine |
| [`DecompositionEngine`](file:///Users/jk/Desktop/GPU/python/saoe/decomposition/engine.py) | `saoe.decomposition.engine` | Structural partitioner for automated Benders and Dantzig-Wolfe decomposition |
| [`LearningMemory`](file:///Users/jk/Desktop/GPU/python/saoe/learning/memory.py) | `saoe.learning.memory` | Continuous learning store recording solver telemetry and strategy performance |
| [`ExperienceStore`](file:///Users/jk/Desktop/GPU/python/saoe/learning/memory.py) | `saoe.learning.memory` | Persistent database of solve runs for lifelong strategy tuning |

#### Native Kernel Re-Exports
Also available directly from `saoe`:
- `PramanaModel`, `PramanaVar`, `PramanaResult`: Low-level ctypes bindings to C++20 engine
- `solve_file(path, **kwargs)`: Direct solve of MPS/QPS files via C++ runtime
- `gpu_info()`: CUDA hardware probe and device status
- `load_library()`: Dynamic loader for `libpramana` (`.so` / `.dylib` / `.dll`)
- `version()`: Engine version string

---

#### 1. Building and Solving a Model via Optimization IR
```python
import saoe

# Instantiate optimization model
model = saoe.Model("refinery_production", maximize=True)

# Add decision variables (continuous & integer)
x = model.add_variable("x", lb=0, ub=4, cost=3)
y = model.add_variable("y", lb=0, cost=5, integer=True)

# Add constraints (sum(coeff * var) <= ub)
model.add_constraint({x: 1, y: 2}, ub=8, name="capacity")

# Solve with closed-loop Optimization Autopilot
result = saoe.solve(model)
print(result.summary())
print(f"Status: {result.status}, Objective: {result.objective:.4f}, Certified: {result.certified}")
```

#### 2. Mathematical Structural Autopsy & Problem Intelligence
```python
import saoe

# Inspect any in-memory model or file path (.mps, .mps.gz, .qps)
autopsy = saoe.autopsy("data/netlib/afiro.mps.gz")

print(f"Problem: {autopsy.name}")
print(f"Variables: {autopsy.num_vars}, Constraints: {autopsy.num_constraints}, Nonzeros: {autopsy.nnz}")
print(f"Sparsity: {autopsy.sparsity_ratio * 100:.2f}%")
print(f"Dynamic Range: 10^{autopsy.dynamic_range_decades:.1f} decades")
print(f"Conditioning: {'Ill-Conditioned' if autopsy.ill_conditioned else 'Well-Conditioned'}")
print(f"Recommended Precision: {autopsy.recommended_precision}")
print(f"Decomposition Candidate: {autopsy.recommended_decomposition}")
```

#### 3. Quantum-Inspired Combinatorial Optimization (QUBO)
```python
import saoe

# Formulate binary quadratic assignment / unconstrained binary optimization
qubo_matrix = {
    (0, 0): -2.0,
    (1, 1): -3.0,
    (0, 1): 4.0,  # Coupling penalty
}

optimizer = saoe.QuantumInspiredSubproblemOptimizer()
best_spins, energy = optimizer.solve_qubo(qubo_matrix, num_sweeps=1000)
print(f"Optimal binary configuration: {best_spins}, Energy: {energy}")
```

#### 4. Automatic Structural Decomposition (Benders / Dantzig-Wolfe)
```python
import saoe

engine = saoe.DecompositionEngine()
# Automatically analyzes constraint graph for block-angular or linking structures
partition = engine.detect_structure(model)
print(f"Detected Structure: {partition.structure_type}, Blocks: {len(partition.subproblems)}")
```

---

### Direct Native C++ Engine
```bash
./build/pramana solve data/netlib/afiro.mps.gz
```


