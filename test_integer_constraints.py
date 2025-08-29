#!/usr/bin/env python3
"""
Test integer variable constraint enforcement
"""

import numpy as np
from core.problem_manager import ProblemManager
from core.algorithm_manager import AlgorithmManager
from core.optimizer import Optimizer
from pymoo.termination import get_termination

def test_integer_variables():
    """Test that integer variables actually stay integer during optimization"""
    
    print("=== Testing Integer Variable Enforcement ===\n")
    
    # Create a problem with mixed variable types
    test_problem = {
        "name": "Integer Variables Test",
        "variables": [
            {"name": "continuous", "type": "Real", "lower_bound": 0.0, "upper_bound": 10.0},
            {"name": "integer_var", "type": "Integer", "lower_bound": 1, "upper_bound": 5},
            {"name": "binary_var", "type": "Binary", "lower_bound": 0, "upper_bound": 1}
        ],
        "objectives": [
            {"name": "f1", "function": "continuous + integer_var + binary_var", "direction": "minimize", "weight": 1.0}
        ],
        "constraints": []
    }
    
    algorithm_config = {
        "name": "NSGA-II",
        "parameters": {
            "population_size": 20,
            "n_generations": 10,
            "crossover_rate": 0.9,
            "mutation_rate": 0.1
        }
    }
    
    print("Problem setup:")
    for var in test_problem['variables']:
        print(f"  • {var['name']}: {var['type']} [{var['lower_bound']}, {var['upper_bound']}]")
    
    try:
        # Create components
        pm = ProblemManager()
        am = AlgorithmManager() 
        optimizer = Optimizer()
        
        print(f"\n🔧 Creating problem...")
        problem = pm.create_problem_from_config(test_problem)
        print(f"   Problem type: {type(problem).__name__}")
        print(f"   Variable types: {getattr(problem, 'vtype', 'Not specified')}")
        
        print(f"\n🔧 Creating algorithm...")
        algorithm = am.create_algorithm_from_config(algorithm_config, problem.n_obj, test_problem)
        
        print(f"\n🚀 Running optimization...")
        termination = get_termination("n_gen", 10)
        optimizer.setup(problem, algorithm, termination)
        
        result = optimizer.run()
        
        if result.X is not None and len(result.X) > 0:
            print(f"\n📊 RESULTS ANALYSIS:")
            print(f"   Solutions found: {len(result.X)}")
            print(f"   Result.X shape: {result.X.shape if hasattr(result.X, 'shape') else 'No shape'}")
            print(f"   Result.X type: {type(result.X)}")
            
            # Debug: print first few raw results
            print(f"   First solution raw: {result.X[0] if len(result.X) > 0 else 'None'}")
            
            print(f"\n🔍 Checking variable types in solutions:")
            for i in range(min(5, len(result.X))):  # Check first 5 solutions
                x = result.X[i]
                
                # Handle different result formats
                if hasattr(x, '__len__') and len(x) >= 3:
                    continuous_val = x[0]
                    integer_val = x[1]
                    binary_val = x[2]
                elif np.isscalar(x):
                    print(f"   Solution {i+1}: Scalar result {x} - cannot analyze variable types")
                    continue
                else:
                    print(f"   Solution {i+1}: Unexpected format {x}")
                    continue
                
                # Check if integer variable is actually integer
                is_integer = abs(integer_val - round(integer_val)) < 1e-10
                # Check if binary variable is 0 or 1
                is_binary = abs(binary_val - round(binary_val)) < 1e-10 and (round(binary_val) in [0, 1])
                
                print(f"   Solution {i+1}: [{continuous_val:.3f}, {integer_val:.6f}, {binary_val:.6f}]")
                print(f"     Integer var is integer: {is_integer} ({'✅' if is_integer else '❌'})")
                print(f"     Binary var is binary: {is_binary} ({'✅' if is_binary else '❌'})")
                
            # Overall statistics
            integer_violations = 0
            binary_violations = 0
            
            for x in result.X:
                if abs(x[1] - round(x[1])) > 1e-10:  # Integer variable not integer
                    integer_violations += 1
                if abs(x[2] - round(x[2])) > 1e-10 or round(x[2]) not in [0, 1]:  # Binary not 0/1
                    binary_violations += 1
            
            print(f"\n📈 CONSTRAINT VIOLATIONS:")
            print(f"   Integer constraint violations: {integer_violations}/{len(result.X)} ({100*integer_violations/len(result.X):.1f}%)")
            print(f"   Binary constraint violations: {binary_violations}/{len(result.X)} ({100*binary_violations/len(result.X):.1f}%)")
            
            if integer_violations > 0 or binary_violations > 0:
                print(f"\n❌ PROBLEM IDENTIFIED:")
                print(f"   The algorithm is not respecting integer/binary variable constraints!")
                print(f"   This is a known limitation of many multi-objective algorithms.")
                return False
            else:
                print(f"\n✅ SUCCESS:")
                print(f"   All variable type constraints are properly enforced!")
                return True
        else:
            print(f"❌ No solutions found!")
            return False
            
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_integer_variables()
    
    if not success:
        print(f"\n🔧 POTENTIAL SOLUTIONS:")
        print(f"   1. Use specialized mixed-integer algorithms")
        print(f"   2. Add repair operators to enforce integer constraints")  
        print(f"   3. Use penalty methods for constraint violations")
        print(f"   4. Round variables to nearest integer in post-processing")
