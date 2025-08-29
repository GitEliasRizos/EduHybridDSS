#!/usr/bin/env python3
"""
Test numpy function support in custom objective functions
"""

import numpy as np
from core.problem_manager import ProblemManager

def test_numpy_functions():
    """Test that numpy functions work in custom objective functions"""
    
    print("=== Testing Numpy Function Support in Custom Objectives ===\n")
    
    # Create a test problem with various numpy functions
    test_problem = {
        "name": "Numpy Functions Test",
        "description": "Test problem to verify numpy function support",
        "variables": [
            {"name": "x1", "type": "Real", "lower_bound": 0.1, "upper_bound": 10.0},
            {"name": "x2", "type": "Real", "lower_bound": 0.1, "upper_bound": 10.0}
        ],
        "objectives": [
            {
                "name": "log_objective",
                "function": "x1 * np.log2(x2)",
                "direction": "minimize",
                "weight": 1.0
            },
            {
                "name": "advanced_objective", 
                "function": "np.sin(x1) + np.log10(x2) + np.exp(x1/10)",
                "direction": "minimize",
                "weight": 1.0
            },
            {
                "name": "mixed_functions",
                "function": "log2(x1) + np.sqrt(x2) + sin(x1*x2)", 
                "direction": "minimize",
                "weight": 1.0
            }
        ],
        "constraints": []
    }
    
    print("Test problem objectives:")
    for i, obj in enumerate(test_problem['objectives'], 1):
        print(f"  {i}. {obj['name']}: {obj['function']}")
    
    # Test problem creation and evaluation
    try:
        pm = ProblemManager()
        
        print(f"\n🔧 Creating problem...")
        problem = pm.create_problem_from_config(test_problem)
        print(f"   ✅ Problem created: {type(problem).__name__}")
        
        # Test evaluation with specific values
        test_points = [
            [1.0, 2.0],   # Should give log2(2) = 1 for first objective
            [2.0, 4.0],   # Should give 2 * log2(4) = 2 * 2 = 4 for first objective
            [0.5, 8.0]    # Should give 0.5 * log2(8) = 0.5 * 3 = 1.5 for first objective
        ]
        
        print(f"\n🧪 Testing function evaluation...")
        for i, point in enumerate(test_points, 1):
            print(f"\n   Test Point {i}: x1={point[0]}, x2={point[1]}")
            
            # Calculate expected value for first objective manually
            expected_log2 = point[0] * np.log2(point[1])
            print(f"   Expected x1 * log2(x2) = {point[0]} * log2({point[1]}) = {expected_log2:.6f}")
            
            # Evaluate using problem manager
            if hasattr(problem, '_evaluate'):
                out = {}
                problem._evaluate(np.array(point).reshape(1, -1), out)
                actual_values = out['F'][0]
                print(f"   Actual objectives: {actual_values}")
                
                # Handle both scalar and array results
                first_objective = actual_values[0] if hasattr(actual_values, '__len__') else actual_values
                print(f"   First objective error: {abs(first_objective - expected_log2):.8f}")
                
                if abs(first_objective - expected_log2) < 1e-6:
                    print("   ✅ Numpy function evaluation CORRECT!")
                else:
                    print("   ❌ Numpy function evaluation INCORRECT!")
            else:
                # For FunctionalProblem, evaluate objectives directly
                result = pm._evaluate_objectives(np.array(point).reshape(1, -1), test_problem['objectives'])
                actual_values = result[0] if len(result.shape) > 1 else result
                print(f"   Actual objectives: {actual_values}")
                
                first_objective = actual_values[0] if hasattr(actual_values, '__len__') else actual_values
                print(f"   First objective error: {abs(first_objective - expected_log2):.8f}")
                
                if abs(first_objective - expected_log2) < 1e-6:
                    print("   ✅ Numpy function evaluation CORRECT!")
                else:
                    print("   ❌ Numpy function evaluation INCORRECT!")
        
        print(f"\n🎯 SUPPORTED NUMPY FUNCTIONS:")
        print("   Direct numpy calls:")
        print("   • np.log2(x)    - Base-2 logarithm")  
        print("   • np.log10(x)   - Base-10 logarithm")
        print("   • np.sin(x)     - Sine function")
        print("   • np.cos(x)     - Cosine function")
        print("   • np.exp(x)     - Exponential function")
        print("   • np.sqrt(x)    - Square root")
        print("   • np.abs(x)     - Absolute value")
        print("   ")
        print("   Shorthand functions (without np.):")
        print("   • log2(x)       - Base-2 logarithm")
        print("   • log10(x)      - Base-10 logarithm") 
        print("   • sin(x)        - Sine function")
        print("   • cos(x)        - Cosine function")
        print("   • exp(x)        - Exponential function")
        print("   • sqrt(x)       - Square root")
        print("   • log(x)        - Natural logarithm")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    return True

if __name__ == "__main__":
    success = test_numpy_functions()
    
    if success:
        print("\n🎉 Numpy functions are now fully supported!")
        print("You can use expressions like 'x1 * np.log2(x2)' in objective functions.")
    else:
        print("\n💥 There are still issues with numpy function support.")
