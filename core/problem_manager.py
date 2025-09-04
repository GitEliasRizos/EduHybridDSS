"""
Problem Manager - Core functionality for managing optimization problems

This module provides the ProblemManager class which serves as the bridge between
the GUI's problem configuration and PyMOO's problem representation. It handles
the conversion of user-defined problems into proper PyMOO problem instances.

Key Features:
- Support for mixed variable types (Real, Integer, Binary)
- Custom objective function evaluation with numpy support
- Constraint handling and evaluation
- Variable bounds and type enforcement
- Repair mechanisms for integer/binary constraints
- Expression parsing with security considerations

The ProblemManager creates either FunctionalProblem instances for simple cases
or CustomProblem instances for complex mixed-variable optimization problems.

Classes:
    ProblemManager: Main interface for problem creation and management
    CustomProblem: PyMOO Problem subclass for mixed-variable problems

Author: Elias Rizos [it21490]
Version: 1.3.2
"""

import numpy as np
from pymoo.core.problem import Problem
from pymoo.problems.functional import FunctionalProblem
from pymoo.core.variable import Real, Integer, Binary


class ProblemManager:
    """
    Manages optimization problem definitions and configurations
    
    This class serves as the central hub for problem management, converting
    GUI-based problem configurations into PyMOO-compatible problem instances.
    It supports various variable types, custom objective functions, and
    constraint definitions.
    
    Key Responsibilities:
    - Parse problem configuration from GUI
    - Create appropriate PyMOO problem instances
    - Handle mixed variable types (Real, Integer, Binary)
    - Evaluate custom objective functions with numpy support
    - Apply constraint functions
    - Ensure variable type constraints through repair mechanisms
    
    Attributes:
        current_problem: The active PyMOO problem instance
        problem_config: Dictionary containing the current problem configuration
    """
    
    def __init__(self):
        """
        Initialize the ProblemManager
        
        Sets up empty problem state. Problems are created dynamically
        when create_problem_from_config is called.
        """
        self.current_problem = None  # Active PyMOO problem instance
        self.problem_config = None   # Current problem configuration dict
        
    def create_problem_from_config(self, config):
        """
        Create a PyMOO problem instance from GUI configuration
        
        This is the main interface for problem creation. It analyzes the
        configuration to determine the appropriate problem type and creates
        either a FunctionalProblem (for simple cases) or CustomProblem
        (for mixed variables or complex constraints).
        
        Args:
            config (dict): Problem configuration containing:
                - variables: List of variable definitions with bounds and types
                - objectives: List of objective functions with expressions
                - constraints: List of constraint definitions (optional)
        
        Returns:
            Problem: A PyMOO problem instance ready for optimization
            
        Raises:
            ValueError: If configuration is invalid or contains errors
            SyntaxError: If objective/constraint expressions are malformed
        """
        self.problem_config = config
        
        # Extract fundamental problem dimensions
        n_var = len(config['variables'])      # Number of decision variables
        n_obj = len(config['objectives'])     # Number of objectives  
        n_constr = len(config['constraints']) # Number of constraints
        
        # Analyze variable types to determine problem complexity
        var_types = [var.get('type', 'Real') for var in config['variables']]
        has_integer = any(t.lower() in ['integer', 'int'] for t in var_types)
        has_binary = any(t.lower() in ['binary', 'bool'] for t in var_types)
        has_real = any(t.lower() in ['real', 'continuous', 'float'] for t in var_types)
        
        # Extract variable bounds and normalize types for PyMOO
        xl = []  # Lower bounds array
        xu = []  # Upper bounds array  
        vtype = []  # Variable types for PyMOO
        
        for var in config['variables']:
            xl.append(var['lower_bound'])
            xu.append(var['upper_bound'])
            
            # Map GUI variable types to PyMOO internal format
            var_type = var.get('type', 'Real').lower()
            if var_type in ['integer', 'int']:
                vtype.append('int')
            elif var_type in ['binary', 'bool']:
                vtype.append('bool')
            else:  # Default to real/continuous for all other cases
                vtype.append('real')
                
        xl = np.array(xl)
        xu = np.array(xu)
        # Determine if we can use PyMOO's simple FunctionalProblem or need custom Problem
        # FunctionalProblem: Fast, for real variables without constraints
        # CustomProblem: Flexible, for mixed variables and/or constraints
        all_real = all(t == 'real' for t in vtype)
        
        if all_real and n_constr == 0:
            # Use FunctionalProblem for simple continuous problems without constraints
            # This is more efficient and easier to debug than custom Problem class
            objective_functions = []
            for i, obj_config in enumerate(config['objectives']):
                def make_obj_func(obj_idx):
                    def objective_func(x):
                        """
                        Evaluate single objective for decision vector x
                        
                        Args:
                            x: Decision variable vector (numpy array)
                            
                        Returns:
                            float: Objective function value
                        """
                        result = self._evaluate_objectives(x, [config['objectives'][obj_idx]])
                        return result[0]  # Return single objective value
                    return objective_func
                objective_functions.append(make_obj_func(i))
                
            # Create PyMOO FunctionalProblem with our objective functions
            self.current_problem = FunctionalProblem(
                n_var=n_var,      # Number of decision variables
                objs=objective_functions,  # List of objective functions
                xl=xl,            # Lower bounds for variables
                xu=xu             # Upper bounds for variables
            )
        else:
            # Use custom Problem class for mixed variables or constraints
            class CustomProblem(Problem):
                def __init__(self, problem_manager, config, xl, xu, vtype):
                    self.problem_manager = problem_manager
                    self.config = config
                    self.vtype_list = vtype  # Store variable types for repair
                    super().__init__(
                        n_var=len(config['variables']),
                        n_obj=len(config['objectives']),
                        n_ieq_constr=len(config['constraints']),
                        xl=xl,
                        xu=xu,
                        vtype=vtype
                    )
                
                def _repair(self, X, **kwargs):
                    """Repair variables to satisfy integer/binary constraints"""
                    if X.ndim == 1:
                        X = X.reshape(1, -1)
                    
                    X_repaired = X.copy()
                    
                    for i, vtype in enumerate(self.vtype_list):
                        if vtype == 'int':
                            # Round to nearest integer and clip to bounds
                            X_repaired[:, i] = np.round(X_repaired[:, i])
                            X_repaired[:, i] = np.clip(X_repaired[:, i], self.xl[i], self.xu[i])
                        elif vtype == 'bool':
                            # Round to 0 or 1 (binary)
                            X_repaired[:, i] = np.round(X_repaired[:, i])
                            X_repaired[:, i] = np.clip(X_repaired[:, i], 0, 1)
                    
                    return X_repaired
                
                def _evaluate(self, X, out, *args, **kwargs):
                    # Apply repair to ensure integer/binary constraints
                    X_repaired = self._repair(X)
                    
                    # Evaluate objectives with repaired variables
                    F = self.problem_manager._evaluate_objectives(X_repaired, self.config['objectives'])
                    out["F"] = F
                    
                    # Evaluate constraints if any
                    if len(self.config['constraints']) > 0:
                        G = self.problem_manager._evaluate_constraints(X_repaired, self.config['constraints'])
                        out["G"] = G
            
            self.current_problem = CustomProblem(self, config, xl, xu, vtype)
            
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
                        'e': np.e, 'log2': np.log2, 'log10': np.log10,
                        # Full numpy module access for advanced functions
                        'np': np, 'numpy': np
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
                        'e': np.e, 'log2': np.log2, 'log10': np.log10,
                        # Full numpy module access for advanced functions
                        'np': np, 'numpy': np
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
        if len(config['variables']) == 0:
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
                'e': np.e, 'log2': np.log2, 'log10': np.log10,
                # Full numpy module access for advanced functions
                'np': np, 'numpy': np
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
