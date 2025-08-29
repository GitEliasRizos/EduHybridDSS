#!/usr/bin/env python3
"""
Simple diagnostic test for variable handling
"""

import numpy as np
from core.problem_manager import ProblemManager
from core.algorithm_manager import AlgorithmManager
from core.optimizer import Optimizer
from pymoo.termination import get_termination

def diagnostic_test():
    """Simple diagnostic to understand the variable handling issue"""
    
    print("=== Diagnostic Test for Variable Handling ===\n")
    
    # Simple test problem
    test_problem = {
        "name": "Simple Diagnostic",
        "variables": [
            {"name": "x1", "type": "Real", "lower_bound": 0.0, "upper_bound": 5.0},
            {"name": "x2", "type": "Integer", "lower_bound": 1, "upper_bound": 3},
            {"name": "x3", "type": "Binary", "lower_bound": 0, "upper_bound": 1}
        ],
        "objectives": [
            {"name": "f1", "function": "x1 + x2 + x3", "direction": "minimize", "weight": 1.0}
        ],
        "constraints": []
    }
    
    algorithm_config = {
        "name": "NSGA-II",
        "parameters": {
            "population_size": 10,
            "n_generations": 3
        }
    }
    
    try:
        # Create components
        pm = ProblemManager()
        am = AlgorithmManager()
        optimizer = Optimizer()
        
        # Create problem
        problem = pm.create_problem_from_config(test_problem)
        print(f"Problem variables: {problem.n_var}")
        print(f"Problem objectives: {problem.n_obj}")
        print(f"Problem bounds: xl={problem.xl}, xu={problem.xu}")
        print(f"Variable types: {getattr(problem, 'vtype', 'Not specified')}")
        
        # Test direct evaluation
        test_point = np.array([[2.5, 2.0, 1.0]])  # 3 variables
        print(f"\nDirect evaluation test:")
        print(f"Input: {test_point}")
        
        if hasattr(problem, '_evaluate'):
            out = {}
            problem._evaluate(test_point, out)
            print(f"Output F: {out.get('F', 'No F')}")
        
        # Run short optimization
        algorithm = am.create_algorithm_from_config(algorithm_config, problem.n_obj, test_problem)
        termination = get_termination("n_gen", 3)
        optimizer.setup(problem, algorithm, termination)
        
        result = optimizer.run()
        
        print(f"\nRaw PyMOO results:")
        print(f"result.X type: {type(result.X)}")
        print(f"result.X shape: {result.X.shape if hasattr(result.X, 'shape') else 'No shape'}")
        print(f"result.F type: {type(result.F)}")
        print(f"result.F shape: {result.F.shape if hasattr(result.F, 'shape') else 'No shape'}")
        
        if hasattr(result.X, 'shape') and len(result.X.shape) > 1:
            print(f"result.X[0]: {result.X[0]}")
            
            # Check if repair is working
            x1, x2, x3 = result.X[0]
            print(f"Variable analysis:")
            print(f"  x1 (Real): {x1:.6f} - OK")
            print(f"  x2 (Integer): {x2:.6f} - Should be integer: {x2:.6f} != {round(x2)}")
            print(f"  x3 (Binary): {x3:.6f} - Should be 0 or 1: {x3:.6f} != {round(x3)}")
            
            # Test if repair method exists and works
            if hasattr(problem, '_repair'):
                print(f"\nTesting repair method:")
                repaired = problem._repair(result.X)
                print(f"Before repair: {result.X[0]}")
                print(f"After repair:  {repaired[0]}")
            else:
                print(f"\n❌ No repair method found on problem!")
        else:
            print(f"result.X: {result.X}")
            
        print(f"result.F: {result.F}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    diagnostic_test()
