# Algorithm-Specific Benchmark Problems

This directory contains benchmark problems specifically designed to showcase the strengths and characteristics of each algorithm available in the PyMOO GUI. Each benchmark is tailored to highlight what makes each algorithm unique and effective.

## 🎯 Algorithm Coverage

### Evolutionary Algorithms
- **NSGA-II**: Fast bi-objective optimization with crowding distance
- **NSGA-III**: Many-objective optimization with reference directions  
- **SPEA2**: Archive-based optimization with clustering

### Decomposition-based Algorithms  
- **MOEA/D**: Weight vector decomposition approach
- **RVEA**: Reference vector guided evolution

### Indicator-based Algorithms
- **IBEA**: Direct indicator-based comparison
- **SMS-EMOA**: Steady-state hypervolume optimization

### Specialized Algorithms
- **GDE3**: Differential evolution for multi-objective problems
- **CTAEA**: Two-archive constraint handling

## 📋 Benchmark Catalog

### NSGA-II Benchmarks
| Problem | Variables | Objectives | Constraints | Focus |
|---------|-----------|------------|-------------|-------|
| `nsga2_biobjective_test.json` | 3 | 2 | 0 | Crowding distance, diversity |
| `nsga2_constrained_engineering.json` | 3 | 2 | 3 | Constraint handling, elitism |

**Best Settings**: Population 50-100, 2-3 objectives
**Expected Performance**: Excellent convergence and diversity for bi-objective problems

### NSGA-III Benchmarks  
| Problem | Variables | Objectives | Constraints | Focus |
|---------|-----------|------------|-------------|-------|
| `nsga3_4obj_dtlz2.json` | 5 | 4 | 0 | 4D reference directions |
| `nsga3_5obj_portfolio.json` | 5 | 5 | 3 | 5D portfolio optimization |

**Best Settings**: Population = reference directions (35-91), 4+ objectives, H1=4-8
**Expected Performance**: Excellent distribution in many-objective space

### SPEA2 Benchmarks
| Problem | Variables | Objectives | Constraints | Focus |
|---------|-----------|------------|-------------|-------|
| `spea2_archive_test.json` | 3 | 2 | 0 | Archive mechanism, non-uniform density |
| `spea2_clustering_challenge.json` | 3 | 2 | 0 | Multi-modal clustering |

**Best Settings**: Population 50, archive size 50, 2-3 objectives
**Expected Performance**: Good handling of irregular Pareto fronts and multi-modal problems

### MOEA/D Benchmarks
| Problem | Variables | Objectives | Constraints | Focus |
|---------|-----------|------------|-------------|-------|
| `moead_decomposition_test.json` | 4 | 2 | 0 | Weight vector distribution |
| `moead_3obj_weights.json` | 5 | 3 | 1 | 3D decomposition |

**Best Settings**: Population 50-100, neighborhood size 10-20
**Expected Performance**: Uniform distribution along Pareto front, good for decomposable problems

### RVEA Benchmarks
| Problem | Variables | Objectives | Constraints | Focus |
|---------|-----------|------------|-------------|-------|
| `rvea_reference_vector_test.json` | 6 | 4 | 0 | Reference vector guidance |

**Best Settings**: Population = reference vectors, 4+ objectives, adaptive penalty
**Expected Performance**: Solutions aligned with reference directions, good convergence

### IBEA Benchmarks
| Problem | Variables | Objectives | Constraints | Focus |
|---------|-----------|------------|-------------|-------|
| `ibea_hypervolume_test.json` | 3 | 2 | 1 | Hypervolume indicator |

**Best Settings**: Population 50-100, hypervolume indicator
**Expected Performance**: High hypervolume values, good knee point finding

### SMS-EMOA Benchmarks
| Problem | Variables | Objectives | Constraints | Focus |
|---------|-----------|------------|-------------|-------|
| `sms_emoa_steady_state.json` | 2 | 2 | 0 | Steady-state hypervolume |

**Best Settings**: Small population 15-25, steady-state replacement
**Expected Performance**: Excellent hypervolume with small populations

### GDE3 Benchmarks
| Problem | Variables | Objectives | Constraints | Focus |
|---------|-----------|------------|-------------|-------|
| `gde3_differential_evolution.json` | 3 | 2 | 0 | DE operators, multi-modal |

**Best Settings**: Population 50, F=0.5, CR=0.9
**Expected Performance**: Good exploration of rugged landscapes

### CTAEA Benchmarks
| Problem | Variables | Objectives | Constraints | Focus |
|---------|-----------|------------|-------------|-------|
| `ctaea_constrained_chemical.json` | 4 | 2 | 5 | Heavy constraints |

**Best Settings**: Population 50, two-archive approach
**Expected Performance**: 100% feasible solutions, excellent constraint handling

## 🚀 Usage Guide

### Running Individual Algorithm Tests
```bash
# Test NSGA-II with its specific benchmarks
python test_algorithm_benchmarks.py NSGA-II

# Test NSGA-III with reference direction problems  
python test_algorithm_benchmarks.py NSGA-III

# Test all algorithms
python test_algorithm_benchmarks.py all
```

### Understanding Results

#### Expected Ratios by Algorithm Type:
- **NSGA-II/SPEA2**: 1.0 for unconstrained, 0.1-0.5 for constrained
- **NSGA-III/RVEA**: 1.0 (distributed across reference directions)
- **MOEA/D**: 1.0 (uniform along weight vectors)
- **CTAEA**: 0.2-0.8 (depends on constraint tightness)
- **SMS-EMOA**: 1.0 (small population, all optimal)

#### Performance Indicators:
- **Convergence**: How close to true Pareto front
- **Diversity**: Spread along the front  
- **Coverage**: Portion of Pareto front found
- **Constraint Satisfaction**: Feasibility rate

## 🔧 Algorithm Selection Guide

### Problem Characteristics → Recommended Algorithm

| Problem Type | Best Algorithm | Why |
|--------------|----------------|-----|
| 2-3 objectives, fast needed | NSGA-II | Proven performance, simple setup |
| 4+ objectives | NSGA-III, RVEA | Reference direction guidance |
| Irregular/multi-modal front | SPEA2 | Archive + clustering |
| Decomposable problems | MOEA/D | Weight vector approach |
| Heavily constrained | CTAEA | Two-archive constraint handling |
| Small population budget | SMS-EMOA | Steady-state efficiency |
| Rugged landscapes | GDE3 | DE exploration |
| Hypervolume focus | IBEA, SMS-EMOA | Direct indicator optimization |

### Recommended Parameter Settings

#### Population Sizing:
- **NSGA-II/SPEA2**: 50-100
- **NSGA-III**: Equal to reference directions (35-455)
- **MOEA/D**: 50-100 (divisible by objective count)
- **RVEA**: Equal to reference vectors
- **SMS-EMOA**: 15-25 (steady-state)
- **CTAEA**: 50-100
- **GDE3**: 50-100

#### Generation Counts:
- **Fast algorithms** (NSGA-II, SPEA2): 100-250
- **Many-objective** (NSGA-III, RVEA): 250-500  
- **Constrained** (CTAEA): 300-600
- **Steady-state** (SMS-EMOA): 500-1000

## 🎯 Validation Checklist

Use these benchmarks to validate your algorithm implementation:

- [ ] **NSGA-II**: Good bi-objective performance, crowding distance working
- [ ] **NSGA-III**: Reference directions properly distributed
- [ ] **SPEA2**: Archive management and clustering effective
- [ ] **MOEA/D**: Weight vectors covering Pareto front uniformly
- [ ] **RVEA**: Solutions aligned with reference vectors
- [ ] **IBEA**: High hypervolume values achieved
- [ ] **SMS-EMOA**: Efficient with small populations
- [ ] **GDE3**: Good exploration of multi-modal problems
- [ ] **CTAEA**: All solutions feasible for constrained problems

## 📚 References

These benchmarks are based on algorithm characteristics from:

- **NSGA-II**: Deb, K., et al. (2002) - Fast and elitist approach
- **NSGA-III**: Deb, K., & Jain, H. (2014) - Reference directions
- **SPEA2**: Zitzler, E., et al. (2001) - Strength and density
- **MOEA/D**: Zhang, Q., & Li, H. (2007) - Decomposition approach  
- **RVEA**: Cheng, R., et al. (2016) - Reference vector guidance
- **IBEA**: Zitzler, E., & Künzli, S. (2004) - Indicator-based
- **SMS-EMOA**: Beume, N., et al. (2007) - Steady-state hypervolume
- **GDE3**: Kukkonen, S., & Lampinen, J. (2005) - Differential evolution
- **CTAEA**: Li, K., et al. (2015) - Constrained two-archive
