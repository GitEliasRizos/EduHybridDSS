# Multi-Objective Optimization Benchmarks

This directory contains a comprehensive collection of benchmark problems for testing multi-objective optimization algorithms. These problems demonstrate different types of Pareto front behaviors and help validate algorithm performance.

## Problem Categories

### 🔵 Continuous Pareto Fronts
These problems have smooth, continuous Pareto fronts where many solutions can be optimal. **Expected: 50-200 solutions (ratio ≈ 1.0)**

- **ZDT1** (`examples/zdt1.json`) - Convex Pareto front
- **ZDT2** (`zdt2_concave.json`) - Concave Pareto front  
- **DTLZ1** (`dtlz1_3obj.json`) - 3-objective linear front (triangular)
- **DTLZ2** (`dtlz2_3obj_sphere.json`) - 3-objective spherical front

### 🟡 Discontinuous Pareto Fronts
Problems with gaps or multiple disconnected regions in the Pareto front. **Expected: 50-150 solutions in separate regions**

- **ZDT3** (`zdt3_discontinuous.json`) - Multiple disconnected regions
- **Kursawe** (`kursawe_multimodal.json`) - Multi-modal with local fronts

### 🟢 Constrained Problems (Discrete Fronts)
Problems with constraints that eliminate many solutions, creating sparse Pareto fronts. **Expected: 5-30 solutions (ratio < 0.5)**

- **Constrained ZDT1** (`constrained_zdt1_discrete.json`) - ZDT1 with constraining geometry
- **Fonseca-Fleming** (`fonseca_fleming.json`) - Concave front with spherical constraint

### 🔷 Simple Problems
Easy problems for beginners and algorithm validation. **Expected: 20-100 solutions**

- **Schaffer F1** (`schaffer_f1_simple.json`) - Single-variable bi-objective

## Problem Characteristics

| Problem | Variables | Objectives | Constraints | Pareto Front Type | Difficulty |
|---------|-----------|------------|-------------|-------------------|------------|
|   ZDT1  |     3     |     2      |      0      | Convex continuous |    Easy    |
|   ZDT2  |     3     |     2      | 0 | Concave continuous | Easy |
| ZDT3 | 3 | 2 | 0 | Discontinuous | Medium |
| DTLZ1 | 5 | 3 | 0 | Linear continuous | Hard |
| DTLZ2 | 4 | 3 | 0 | Spherical continuous | Medium |
| Constrained ZDT1 | 3 | 2 | 3 | Discrete | Medium |
| Fonseca-Fleming | 3 | 2 | 1 | Constrained concave | Medium |
| Schaffer F1 | 1 | 2 | 0 | Simple convex | Easy |
| Kursawe | 3 | 2 | 0 | Multi-modal | Hard |

## Understanding Results

### ✅ Normal Behavior
- **ZDT1, ZDT2, DTLZ**: Finding population_size solutions is **CORRECT**
- **Constrained problems**: Finding 5-30 solutions is **EXPECTED**
- **Multi-modal problems**: Finding solutions in separate regions is **GOOD**

### ❌ Problematic Behavior  
- **Constrained problems finding 100+ solutions**: Constraints too weak
- **Simple problems finding 0 solutions**: Over-constrained or buggy
- **All problems failing**: Algorithm or implementation issues

## Usage

### Running Individual Benchmarks
```python
# Load and test a specific benchmark
with open('examples/benchmarks/zdt1.json', 'r') as f:
    problem_config = json.load(f)

pm = ProblemManager()
problem = pm.create_problem_from_config(problem_config)
# ... run optimization
```

### Running All Benchmarks
```bash
python test_benchmarks.py
```

This will test all benchmark problems and provide a comprehensive analysis of algorithm performance across different problem types.

## Algorithm Testing Recommendations

### For Algorithm Development
1. **Start with Schaffer F1** - simplest problem
2. **Test ZDT1** - verify basic Pareto front finding
3. **Test ZDT3** - check discontinuous front handling  
4. **Test Constrained ZDT1** - verify constraint handling
5. **Test DTLZ2** - validate 3-objective capabilities

### For Algorithm Comparison
- Use consistent population sizes (50-100)
- Run multiple seeds for statistical significance
- Compare convergence speed and final spread
- Check constraint violation handling

### Expected Performance Metrics
- **IGD (Inverted Generational Distance)**: < 0.01 for ZDT problems
- **Hypervolume**: > 0.6 for 2-objective problems
- **Pareto Front Coverage**: > 90% for continuous fronts
- **Constraint Satisfaction**: 100% feasible solutions

## References

These benchmarks are based on well-established test problems from the multi-objective optimization literature:

- **ZDT Series**: Zitzler, E., Deb, K., & Thiele, L. (2000)
- **DTLZ Series**: Deb, K., Thiele, L., Laumanns, M., & Zitzler, E. (2005)  
- **Fonseca-Fleming**: Fonseca, C. M., & Fleming, P. J. (1995)
- **Kursawe**: Kursawe, F. (1991)
- **Schaffer**: Schaffer, J. D. (1985)

Use these benchmarks to validate your optimization algorithms and compare performance with published results.
