"""
Problem Manager - Core functionality for managing optimization problems
"""

import numpy as np
from pymoo.core.problem import Problem
from pymoo.problems.functional import FunctionalProblem
import re


class ProblemManager:
    """Manages optimization problem definitions and configurations"""
    
    def __init__(self):
        self.current_problem = None
        self.problem_config = None
        
    def create_problem_from_config(self, config):
        """Create a PyMOO problem from configuration"""
        self.problem_config = config
        
        # Extract problem information
        n_var = len(config['variables'])
        n_obj = len(config['objectives'])
        n_constr = len(config['constraints'])
        
        # Get variable bounds
        xl = []
        xu = []
        for var in config['variables']:
            xl.append(var['lower_bound'])
            xu.append(var['upper_bound'])
            
        xl = np.array(xl)
        xu = np.array(xu)
        
        # Create objective function
        def objective_function(x):
            """Evaluate objectives for decision vector x"""
            return self._evaluate_objectives(x, config['objectives'])
            
        # Create constraint function if constraints exist
        constraint_function = None
        if n_constr > 0:
            def constraint_function(x):
                """Evaluate constraints for decision vector x"""
                return self._evaluate_constraints(x, config['constraints'])
        
        # Create the problem
        if constraint_function is not None:
            self.current_problem = FunctionalProblem(
                n_var=n_var,
                objs=objective_function,
                constr_ieq=constraint_function,
                xl=xl,
                xu=xu
            )
        else:
            self.current_problem = FunctionalProblem(
                n_var=n_var,
                objs=objective_function,
                xl=xl,
                xu=xu
            )
            
        return self.current_problem
        
    def _evaluate_objectives(self, X, objective_configs):
        """Evaluate objective functions"""
        if X.ndim == 1:
            X = X.reshape(1, -1)
            
        n_solutions = X.shape[0]
        n_objectives = len(objective_configs)
        F = np.zeros((n_solutions, n_objectives))
        
        for i, obj_config in enumerate(objective_configs):
            function_str = obj_config['function']
            direction = obj_config['direction']
            weight = obj_config['weight']
            
            # Evaluate the function for each solution
            for j in range(n_solutions):
                try:
                    # Create variable context for evaluation
                    var_context = {}
                    for k, var_config in enumerate(self.problem_config['variables']):
                        var_name = var_config['name']
                        var_context[var_name] = X[j, k]
                        
                    # Also add x1, x2, etc. for convenience
                    for k in range(X.shape[1]):
                        var_context[f'x{k+1}'] = X[j, k]
                        
                    # Add mathematical functions
                    var_context.update({
                        'sin': np.sin, 'cos': np.cos, 'tan': np.tan,
                        'exp': np.exp, 'log': np.log, 'sqrt': np.sqrt,
                        'abs': np.abs, 'pow': np.power, 'pi': np.pi,
                        'e': np.e
                    })
                    
                    # Evaluate the function
                    result = eval(function_str, {"__builtins__": {}}, var_context)
                    
                    # Apply direction (maximize -> minimize by negation)
                    if direction == "Maximize":
                        result = -result
                        
                    # Apply weight
                    result *= weight
                    
                    F[j, i] = result
                    
                except Exception as e:
                    # If evaluation fails, assign a large penalty value
                    F[j, i] = 1e6
                    
        return F if F.shape[0] > 1 else F[0]
        
    def _evaluate_constraints(self, X, constraint_configs):
        """Evaluate constraint functions"""
        if X.ndim == 1:
            X = X.reshape(1, -1)
            
        n_solutions = X.shape[0]
        n_constraints = len(constraint_configs)
        G = np.zeros((n_solutions, n_constraints))
        
        for i, const_config in enumerate(constraint_configs):
            function_str = const_config['function']
            constraint_type = const_config['type']
            constraint_value = const_config['value']
            
            # Evaluate the constraint for each solution
            for j in range(n_solutions):
                try:
                    # Create variable context for evaluation
                    var_context = {}
                    for k, var_config in enumerate(self.problem_config['variables']):
                        var_name = var_config['name']
                        var_context[var_name] = X[j, k]
                        
                    # Also add x1, x2, etc. for convenience
                    for k in range(X.shape[1]):
                        var_context[f'x{k+1}'] = X[j, k]
                        
                    # Add mathematical functions
                    var_context.update({
                        'sin': np.sin, 'cos': np.cos, 'tan': np.tan,
                        'exp': np.exp, 'log': np.log, 'sqrt': np.sqrt,
                        'abs': np.abs, 'pow': np.power, 'pi': np.pi,
                        'e': np.e
                    })
                    
                    # Evaluate the function
                    result = eval(function_str, {"__builtins__": {}}, var_context)
                    
                    # Convert to inequality constraint (g(x) <= 0)
                    if "≤" in constraint_type or "Less than" in constraint_type:
                        # g(x) <= value -> g(x) - value <= 0
                        G[j, i] = result - constraint_value
                    elif "≥" in constraint_type or "Greater than" in constraint_type:
                        # g(x) >= value -> -(g(x) - value) <= 0
                        G[j, i] = constraint_value - result
                    else:  # Equality constraint
                        # g(x) = value -> |g(x) - value| <= tolerance
                        # For simplicity, convert to inequality with small tolerance
                        G[j, i] = abs(result - constraint_value) - 1e-6
                        
                except Exception as e:
                    # If evaluation fails, assign constraint violation
                    G[j, i] = 1e6
                    
        return G if G.shape[0] > 1 else G[0]
        
    def validate_problem_config(self, config):
        """Validate problem configuration"""
        errors = []
        
        # Check required fields
        if 'variables' not in config or len(config['variables']) == 0:
            errors.append("At least one variable must be defined")
            
        if 'objectives' not in config or len(config['objectives']) == 0:
            errors.append("At least one objective must be defined")
            
        # Check variables
        for i, var in enumerate(config.get('variables', [])):
            if 'lower_bound' not in var or 'upper_bound' not in var:
                errors.append(f"Variable {i+1}: bounds must be specified")
            elif var['lower_bound'] >= var['upper_bound']:
                errors.append(f"Variable {i+1}: lower bound must be less than upper bound")
                
        # Check objectives
        for i, obj in enumerate(config.get('objectives', [])):
            if 'function' not in obj or not obj['function'].strip():
                errors.append(f"Objective {i+1}: function must be specified")
            else:
                # Try to validate function syntax
                if not self._validate_function_syntax(obj['function'], config['variables']):
                    errors.append(f"Objective {i+1}: invalid function syntax")
                    
        # Check constraints
        for i, const in enumerate(config.get('constraints', [])):
            if 'function' not in const or not const['function'].strip():
                errors.append(f"Constraint {i+1}: function must be specified")
            else:
                # Try to validate function syntax
                if not self._validate_function_syntax(const['function'], config['variables']):
                    errors.append(f"Constraint {i+1}: invalid function syntax")
                    
        return errors
        
    def _validate_function_syntax(self, function_str, variables):
        """Validate function syntax"""
        try:
            # Create a test context
            var_context = {}
            for var in variables:
                var_context[var['name']] = 1.0
                
            # Add x1, x2, etc.
            for i in range(len(variables)):
                var_context[f'x{i+1}'] = 1.0
                
            # Add mathematical functions
            var_context.update({
                'sin': np.sin, 'cos': np.cos, 'tan': np.tan,
                'exp': np.exp, 'log': np.log, 'sqrt': np.sqrt,
                'abs': np.abs, 'pow': np.power, 'pi': np.pi,
                'e': np.e
            })
            
            # Try to evaluate
            eval(function_str, {"__builtins__": {}}, var_context)
            return True
            
        except Exception:
            return False
            
    def get_problem_summary(self):
        """Get a summary of the current problem"""
        if not self.problem_config:
            return "No problem configured"
            
        config = self.problem_config
        summary = f"""
Problem: {config.get('name', 'Unnamed')}
Variables: {len(config['variables'])}
Objectives: {len(config['objectives'])}
Constraints: {len(config['constraints'])}
Type: {config.get('type', 'Unknown')}
"""
        return summary.strip()
        
    def get_test_point(self):
        """Get a test point for problem evaluation"""
        if not self.problem_config:
            return None
            
        test_point = []
        for var in self.problem_config['variables']:
            # Use initial value if available, otherwise middle of bounds
            if 'initial_value' in var:
                test_point.append(var['initial_value'])
            else:
                lower = var['lower_bound']
                upper = var['upper_bound']
                test_point.append((lower + upper) / 2)
                
        return np.array(test_point)


# Predefined problem templates
PROBLEM_TEMPLATES = {
    "ZDT1": {
        "name": "ZDT1",
        "description": "Zitzler-Deb-Thiele Function 1",
        "type": "Test Function",
        "variables": [
            {"name": f"x{i+1}", "type": "Real", "lower_bound": 0.0, "upper_bound": 1.0, "initial_value": 0.5}
            for i in range(30)
        ],
        "objectives": [
            {"name": "f1", "direction": "Minimize", "weight": 1.0, "function": "x1"},
            {"name": "f2", "direction": "Minimize", "weight": 1.0, 
             "function": "(1 + 9 * sum([x{} for x in range(2, 31)]) / 29) * (1 - sqrt(x1 / (1 + 9 * sum([x{} for x in range(2, 31)]) / 29)))".replace("x{}", "x2")}
        ],
        "constraints": []
    },
    "DTLZ2": {
        "name": "DTLZ2",
        "description": "Deb-Thiele-Laumanns-Zitzler Function 2",
        "type": "Test Function",
        "variables": [
            {"name": f"x{i+1}", "type": "Real", "lower_bound": 0.0, "upper_bound": 1.0, "initial_value": 0.5}
            for i in range(12)
        ],
        "objectives": [
            {"name": "f1", "direction": "Minimize", "weight": 1.0, "function": "(1 + sum([x{} for x in range(3, 13)])) * cos(x1 * pi / 2) * cos(x2 * pi / 2)"},
            {"name": "f2", "direction": "Minimize", "weight": 1.0, "function": "(1 + sum([x{} for x in range(3, 13)])) * cos(x1 * pi / 2) * sin(x2 * pi / 2)"},
            {"name": "f3", "direction": "Minimize", "weight": 1.0, "function": "(1 + sum([x{} for x in range(3, 13)])) * sin(x1 * pi / 2)"}
        ],
        "constraints": []
    }
}
