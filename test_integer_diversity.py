#!/usr/bin/env python3
"""
Test script to verify integer variables can take different values
Using an objective that doesn't clearly prefer one integer value
"""

import numpy as np
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.optimize import minimize
from core.problem_manager import ProblemManager
from core.algorithm_manager import AlgorithmManager

# Test configuration with integer variable that can be 1, 2, or 3
# Using an objective that creates trade-offs to encourage different x2 values
problem_config = {
    'variables': [
        {'name': 'x1', 'type': 'Real', 'lower_bound': 0.0, 'upper_bound': 5.0},
        {'name': 'x2', 'type': 'Integer', 'lower_bound': 1, 'upper_bound': 3},  # Can be 1, 2, or 3
        {'name': 'x3', 'type': 'Binary', 'lower_bound': 0, 'upper_bound': 1}
    ],
    'objectives': [
        # This objective creates different trade-offs for different x2 values
        {'name': 'f1', 'function': '(x2 - 2)**2 + x1 + x3', 'direction': 'Minimize', 'weight': 1.0}
    ],
    'constraints': []
}

algorithm_config = {
    'name': 'NSGA-II',
    'parameters': {'population_size': 50, 'n_generations': 100},
    'crossover': {'operator': 'SBX', 'probability': 0.9, 'eta': 15},
    'mutation': {'operator': 'Polynomial Mutation', 'probability': 0.3, 'eta': 20}
}

print("=== Testing Integer Variable Range ===")
print("x2 should be able to take values 1, 2, or 3")
print("Objective: (x2-2)^2 + x1 + x3 encourages x2=2")

# Create problem and algorithm
problem_manager = ProblemManager()
problem = problem_manager.create_problem_from_config(problem_config)

algorithm_manager = AlgorithmManager()
algorithm = algorithm_manager.create_algorithm_from_config(
    algorithm_config, 
    n_objectives=1,
    problem_config=problem_config
)

# Run optimization with more generations and higher mutation rate
from pymoo.termination import get_termination
termination = get_termination("n_gen", 100)

result = minimize(problem, algorithm, termination, verbose=False)

print(f"\nOptimization results:")
print(f"result.X type: {type(result.X)}")
print(f"result.X shape: {result.X.shape if hasattr(result.X, 'shape') else 'No shape'}")

# Check if we have multiple solutions in population
if hasattr(algorithm, 'pop') and algorithm.pop is not None:
    population_X = algorithm.pop.get("X")
    print(f"\nFinal population size: {len(population_X)}")
    
    # Check x2 values in the population
    x2_values = population_X[:, 1]
    unique_x2 = np.unique(x2_values)
    print(f"Unique x2 values in population: {unique_x2}")
    
    # Show distribution
    from collections import Counter
    x2_counts = Counter(x2_values)
    print("x2 value distribution in population:")
    for val, count in sorted(x2_counts.items()):
        print(f"  x2 = {val}: {count} individuals")
    
    # Check if all are integers
    all_integers = all(val in [1, 2, 3] for val in unique_x2)
    print(f"\nInteger constraints working: {all_integers}")
    
else:
    print(f"\nBest solution: x2 = {result.X[1]}")
    print(f"x2 is integer: {result.X[1] in [1, 2, 3]}")

print(f"\nObjective value: {result.F}")
