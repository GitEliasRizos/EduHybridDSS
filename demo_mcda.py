"""
MCDA Integration Demo

This script demonstrates how to use AHP and TOPSIS with PyMOO optimization results.
It creates a sample optimization problem, runs it with PyMOO, and then applies
both AHP and TOPSIS methods for decision analysis.

Run this script to see the complete workflow in action.
"""

import numpy as np
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.core.problem import Problem
from pymoo.optimize import minimize
from pymoo.termination import get_termination

from core.mcda import MCDAManager


class SampleProblem(Problem):
    """Sample multi-objective optimization problem for testing MCDA"""
    
    def __init__(self):
        super().__init__(n_var=3, n_obj=3, xl=0, xu=1)
        
    def _evaluate(self, X, out, *args, **kwargs):
        # Three conflicting objectives
        f1 = X[:, 0]  # Minimize cost
        f2 = -X[:, 1]  # Maximize performance (negated for minimization)
        f3 = -X[:, 2]  # Maximize reliability (negated for minimization)
        
        out["F"] = np.column_stack([f1, f2, f3])


def demo_mcda_with_pymoo():
    """Demonstrate complete MCDA workflow with PyMOO results"""
    
    print("=== MCDA Integration with PyMOO Demo ===\n")
    
    # Step 1: Define and solve optimization problem
    print("1. Setting up optimization problem...")
    problem = SampleProblem()
    
    algorithm = NSGA2(pop_size=50)
    termination = get_termination("n_gen", 100)
    
    print("2. Running optimization...")
    result = minimize(problem, algorithm, termination, verbose=False)
    
    print(f"   Found {len(result.F)} Pareto optimal solutions")
    
    # Step 2: Prepare objectives information (as would come from GUI)
    objectives_info = [
        {"name": "Cost", "direction": "Minimize"},
        {"name": "Performance", "direction": "Maximize"},  
        {"name": "Reliability", "direction": "Maximize"}
    ]
    
    print("3. Preparing MCDA analysis...")
    mcda = MCDAManager()
    
    # Step 3: AHP Analysis
    print("\n=== AHP Analysis ===")
    
    # Example pairwise comparisons (Performance > Reliability > Cost)
    ahp_comparisons = {
        ("Cost", "Performance"): 0.2,      # Performance 5x more important than cost
        ("Cost", "Reliability"): 0.33,     # Reliability 3x more important than cost
        ("Performance", "Reliability"): 2.0 # Performance 2x more important than reliability
    }
    
    ahp_results = mcda.analyze_with_ahp(result, objectives_info, ahp_comparisons)
    
    print(f"Criteria weights: {ahp_results['criteria_names']}")
    for name, weight in zip(ahp_results['criteria_names'], ahp_results['weights']):
        print(f"  {name}: {weight:.3f}")
    
    print(f"Consistency Ratio: {ahp_results['consistency_ratio']:.4f} ({'PASS' if ahp_results['is_consistent'] else 'FAIL'})")
    
    # Show top 5 solutions
    top_ahp = mcda.get_ranking_summary(ahp_results, 5)
    print("\nTop 5 AHP Solutions:")
    print(top_ahp.to_string(index=False))
    
    # Step 4: TOPSIS Analysis  
    print("\n=== TOPSIS Analysis ===")
    
    # Example weights (same importance distribution as AHP for comparison)
    topsis_weights = np.array([0.15, 0.50, 0.35])  # Cost, Performance, Reliability
    
    topsis_results = mcda.analyze_with_topsis(result, objectives_info, topsis_weights)
    
    print(f"Criteria weights: {topsis_results['criteria_names']}")
    for name, weight in zip(topsis_results['criteria_names'], topsis_results['weights']):
        print(f"  {name}: {weight:.3f}")
        
    # Show top 5 solutions
    top_topsis = mcda.get_ranking_summary(topsis_results, 5)
    print("\nTop 5 TOPSIS Solutions:")
    print(top_topsis.to_string(index=False))
    
    # Step 5: Comparison
    print("\n=== Method Comparison ===")
    
    comparison = mcda.compare_methods(result, objectives_info, ahp_comparisons, topsis_weights)
    correlation = comparison['ranking_correlation']
    
    print(f"Ranking correlation between AHP and TOPSIS: {correlation:.3f}")
    
    if correlation > 0.7:
        print("✅ Strong agreement between methods")
    elif correlation > 0.4:
        print("⚠️  Moderate agreement between methods")
    else:
        print("❌ Low agreement - methods give different rankings")
    
    print("\n=== Summary ===")
    print("The MCDA integration allows users to:")
    print("1. Apply sophisticated decision analysis to PyMOO results")
    print("2. Incorporate subjective preferences through pairwise comparisons (AHP)")
    print("3. Use weighted criteria analysis (TOPSIS)")
    print("4. Compare different decision methods")
    print("5. Export rankings and detailed analysis results")
    print("\nIntegration complete! 🎉")
    
    return ahp_results, topsis_results, comparison


if __name__ == "__main__":
    demo_mcda_with_pymoo()
