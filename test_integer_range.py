#!/usr/bin/env python3
"""
Test script to verify integer variables can take different values in their range
"""

import numpy as np
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.optimize import minimize
from pymoo.core.problem import Problem
from core.problem_manager import ProblemManager
from core.algorithm_manager import AlgorithmManager

# Test configuration with integer variable that can be 1, 2, or 3
problem_config = {
    'variables': [
        {'name': 'x1', 'type': 'Real', 'lower_bound': 0.0, 'upper_bound': 5.0},
        {'name': 'x2', 'type': 'Integer', 'lower_bound': 1, 'upper_bound': 3},  # Can be 1, 2, or 3
        {'name': 'x3', 'type': 'Binary', 'lower_bound': 0, 'upper_bound': 1}
    ],
    'objectives': [
        {'name': 'f1', 'function': 'x1 + x2 + x3', 'direction': 'Minimize', 'weight': 1.0}
    ],
    'constraints': []
}

algorithm_config = {
    'name': 'NSGA-II',
    'parameters': {'population_size': 20, 'n_generations': 30},
    'crossover': {'operator': 'SBX', 'probability': 0.9, 'eta': 15},
    'mutation': {'operator': 'Polynomial Mutation', 'probability': 0.1, 'eta': 20}
}

print("=== Testing Integer Variable Range ===")
print("x2 should be able to take values 1, 2, or 3")

# Create problem and algorithm
problem_manager = ProblemManager()
problem = problem_manager.create_problem_from_config(problem_config)

algorithm_manager = AlgorithmManager()
algorithm = algorithm_manager.create_algorithm_from_config(
    algorithm_config, 
    n_objectives=1,
    problem_config=problem_config
)

# Run optimization with more generations to explore the space
from pymoo.termination import get_termination
termination = get_termination("n_gen", 30)

result = minimize(problem, algorithm, termination, verbose=False)

print(f"\nFound solutions")
print(f"result.X type: {type(result.X)}")
print(f"result.X shape: {result.X.shape if hasattr(result.X, 'shape') else 'No shape'}")
print(f"result.X: {result.X}")

# Check if result.X is a single solution or multiple solutions
if result.X.ndim == 1:
    print(f"\nSingle solution found: x2 = {result.X[1]}")
    unique_x2 = [result.X[1]]
else:
    print("\nSample solutions (showing x2 values):")
    for i in range(min(10, len(result.X))):
        x2_value = result.X[i][1]  # x2 is the second variable
        print(f"Solution {i+1}: x2 = {x2_value}")
    
    # Check the range of x2 values
    x2_values = result.X[:, 1]
    unique_x2 = np.unique(x2_values)
    print(f"\nUnique x2 values found: {unique_x2}")
    print("Integer constraints working correctly!" if all(val in [1, 2, 3] for val in unique_x2) else "Issue with integer constraints!")
