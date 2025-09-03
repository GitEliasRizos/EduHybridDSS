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

import ast
import math
import numpy as np
import sys
import os
import operator
from typing import Dict, Any, Union
from pymoo.core.problem import Problem
from pymoo.problems.functional import FunctionalProblem
from pymoo.core.variable import Real, Integer, Binary


class SecurityError(Exception):
    """Custom exception for security-related evaluation errors."""
    pass


class SecureMathEvaluator:
    """
    Secure mathematical expression evaluator using AST parsing.
    Only allows whitelisted mathematical operations and functions.
    """
    
    # Allowed operators
    SAFE_OPERATORS = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.FloorDiv: operator.floordiv,
        ast.Mod: operator.mod,
        ast.Pow: operator.pow,
        ast.USub: operator.neg,
        ast.UAdd: operator.pos,
    }
    
    # Allowed mathematical functions
    SAFE_FUNCTIONS = {
        # Basic math functions
        'abs': abs,
        'round': round,
        'min': min,
        'max': max,
        'sum': sum,
        
        # Math module functions
        'sin': math.sin,
        'cos': math.cos,
        'tan': math.tan,
        'asin': math.asin,
        'acos': math.acos,
        'atan': math.atan,
        'atan2': math.atan2,
        'sinh': math.sinh,
        'cosh': math.cosh,
        'tanh': math.tanh,
        'exp': math.exp,
        'log': math.log,
        'log2': math.log2,
        'log10': math.log10,
        'sqrt': math.sqrt,
        'pow': pow,
        'ceil': math.ceil,
        'floor': math.floor,
        'fabs': math.fabs,
        
        # Constants
        'pi': math.pi,
        'e': math.e,
        'tau': math.tau,
        
        # Numpy equivalents for compatibility
        'np': type('np', (), {
            'sin': np.sin,
            'cos': np.cos,
            'tan': np.tan,
            'arcsin': np.arcsin,
            'arccos': np.arccos,
            'arctan': np.arctan,
            'arctan2': np.arctan2,
            'sinh': np.sinh,
            'cosh': np.cosh,
            'tanh': np.tanh,
            'exp': np.exp,
            'exp2': np.exp2,
            'log': np.log,
            'log2': np.log2,
            'log10': np.log10,
            'sqrt': np.sqrt,
            'power': np.power,
            'abs': np.abs,
            'ceil': np.ceil,
            'floor': np.floor,
            'round': np.round,
            'min': np.min,
            'max': np.max,
            'sum': np.sum,
            'mean': np.mean,
            'std': np.std,
            'pi': np.pi,
            'e': np.e,
        }),
    }
    
    def __init__(self, max_expression_length: int = 1000, max_recursion_depth: int = 50):
        self.max_expression_length = max_expression_length
        self.max_recursion_depth = max_recursion_depth
        self._recursion_depth = 0
    
    def evaluate(self, expression: str, variables: Dict[str, float]) -> float:
        """Safely evaluate a mathematical expression."""
        if not isinstance(expression, str):
            raise TypeError("Expression must be a string")
            
        if len(expression) > self.max_expression_length:
            raise SecurityError(f"Expression too long (max {self.max_expression_length} chars)")
            
        if not expression.strip():
            raise ValueError("Expression cannot be empty")
        
        try:
            tree = ast.parse(expression.strip(), mode='eval')
        except SyntaxError as e:
            raise ValueError(f"Invalid mathematical syntax: {e}")
        
        self._recursion_depth = 0
        result = self._eval_node(tree.body, variables)
        
        if not isinstance(result, (int, float, np.number)):
            raise TypeError(f"Expression must evaluate to a number, got {type(result)}")
            
        result = float(result)
        if math.isnan(result) or math.isinf(result):
            raise ValueError("Expression produced invalid numerical result (NaN or Inf)")
            
        return result
    
    def _eval_node(self, node: ast.AST, variables: Dict[str, float]) -> Union[float, int]:
        """Recursively evaluate an AST node safely."""
        self._recursion_depth += 1
        if self._recursion_depth > self.max_recursion_depth:
            raise RecursionError("Expression too complex (recursion limit exceeded)")
        
        try:
            # Numbers
            if isinstance(node, ast.Constant):
                if isinstance(node.value, (int, float)):
                    return node.value
                else:
                    raise SecurityError(f"Only numeric constants allowed, found {type(node.value)}")
            
            # For Python < 3.8 compatibility 
            elif isinstance(node, ast.Num):
                return node.n
            
            # Variables
            elif isinstance(node, ast.Name):
                if node.id in variables:
                    return variables[node.id]
                elif node.id in self.SAFE_FUNCTIONS:
                    return self.SAFE_FUNCTIONS[node.id]
                else:
                    raise SecurityError(f"Unknown variable or function: {node.id}")
            
            # Attribute access (np.pi, np.e, etc.)
            elif isinstance(node, ast.Attribute):
                if isinstance(node.value, ast.Name) and node.value.id == 'np':
                    attr_name = node.attr
                    np_module = self.SAFE_FUNCTIONS.get('np')
                    
                    if not hasattr(np_module, attr_name):
                        raise SecurityError(f"numpy attribute {attr_name} not allowed")
                    
                    return getattr(np_module, attr_name)
                else:
                    raise SecurityError("Only np.* attribute access allowed")
            
            # Binary operations
            elif isinstance(node, ast.BinOp):
                if type(node.op) not in self.SAFE_OPERATORS:
                    raise SecurityError(f"Operator {type(node.op).__name__} not allowed")
                
                left = self._eval_node(node.left, variables)
                right = self._eval_node(node.right, variables) 
                
                # Division by zero check
                if isinstance(node.op, ast.Div) and right == 0:
                    raise ValueError("Division by zero")
                
                return self.SAFE_OPERATORS[type(node.op)](left, right)
            
            # Unary operations
            elif isinstance(node, ast.UnaryOp):
                if type(node.op) not in self.SAFE_OPERATORS:
                    raise SecurityError(f"Unary operator {type(node.op).__name__} not allowed")
                
                operand = self._eval_node(node.operand, variables)
                return self.SAFE_OPERATORS[type(node.op)](operand)
            
            # Function calls
            elif isinstance(node, ast.Call):
                # Handle simple function calls (sin, cos, etc.)
                if isinstance(node.func, ast.Name):
                    func_name = node.func.id
                    if func_name not in self.SAFE_FUNCTIONS:
                        raise SecurityError(f"Function {func_name} not allowed")
                    
                    # Evaluate arguments
                    args = [self._eval_node(arg, variables) for arg in node.args]
                    
                    # Check for keyword arguments (not allowed for security)
                    if node.keywords:
                        raise SecurityError("Keyword arguments not allowed in functions")
                    
                    try:
                        return self.SAFE_FUNCTIONS[func_name](*args)
                    except Exception as e:
                        raise ValueError(f"Error calling {func_name}: {e}")
                
                # Handle attribute access (np.log2, np.sin, etc.)
                elif isinstance(node.func, ast.Attribute):
                    if isinstance(node.func.value, ast.Name) and node.func.value.id == 'np':
                        attr_name = node.func.attr
                        np_module = self.SAFE_FUNCTIONS.get('np')
                        
                        if not hasattr(np_module, attr_name):
                            raise SecurityError(f"numpy function {attr_name} not allowed")
                        
                        func = getattr(np_module, attr_name)
                        
                        # Evaluate arguments
                        args = [self._eval_node(arg, variables) for arg in node.args]
                        
                        # Check for keyword arguments (not allowed for security)
                        if node.keywords:
                            raise SecurityError("Keyword arguments not allowed in functions")
                        
                        try:
                            return func(*args)
                        except Exception as e:
                            raise ValueError(f"Error calling np.{attr_name}: {e}")
                    else:
                        raise SecurityError("Only np.* attribute access allowed")
                else:
                    raise SecurityError("Only simple function calls and np.* calls allowed")
            
            # Lists/tuples for multi-argument functions
            elif isinstance(node, (ast.List, ast.Tuple)):
                return [self._eval_node(item, variables) for item in node.elts]
                
            else:
                raise SecurityError(f"AST node type {type(node).__name__} not allowed")
                
        finally:
            self._recursion_depth -= 1


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
        
        Sets up empty problem state and secure evaluator for mathematical expressions.
        Problems are created dynamically when create_problem_from_config is called.
        """
        self.current_problem = None  # Active PyMOO problem instance
        self.problem_config = None   # Current problem configuration dict
        
        # Initialize secure mathematical expression evaluator
        self.secure_evaluator = SecureMathEvaluator(
            max_expression_length=2000,  # Allow complex optimization expressions
            max_recursion_depth=100      # Support nested mathematical operations
        )
        
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
        
        # Check if we have mixed variable types or can use FunctionalProblem
        all_real = all(t == 'real' for t in vtype)
        
        if all_real and n_constr == 0:
            # Use FunctionalProblem for simple continuous problems without constraints
            objective_functions = []
            for i, obj_config in enumerate(config['objectives']):
                def make_obj_func(obj_idx):
                    def objective_func(x):
                        """Evaluate single objective for decision vector x"""
                        result = self._evaluate_objectives(x, [config['objectives'][obj_idx]])
                        return result[0]  # Return single objective value
                    return objective_func
                objective_functions.append(make_obj_func(i))
                
            self.current_problem = FunctionalProblem(
                n_var=n_var,
                objs=objective_functions,
                xl=xl,
                xu=xu
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
        """
        Evaluate objective functions using secure AST-based evaluation
        
        This method safely evaluates user-defined objective functions without
        executing potentially dangerous code. All expressions are parsed and
        evaluated using SecureMathEvaluator which only allows mathematical operations.
        
        Args:
            X: Decision variable matrix (n_solutions x n_variables)
            objective_configs: List of objective function configurations
            
        Returns:
            F: Objective function values (n_solutions x n_objectives)
        """
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
                    # Create variable context for secure evaluation
                    var_context = {}
                    
                    # Add named variables
                    for k, var_config in enumerate(self.problem_config['variables']):
                        var_name = var_config['name']
                        var_context[var_name] = float(X[j, k])
                        
                    # Add x1, x2, etc. convenience variables
                    for k in range(X.shape[1]):
                        var_context[f'x{k+1}'] = float(X[j, k])
                    
                    # SECURE EVALUATION - No eval() or dangerous code execution
                    result = self.secure_evaluator.evaluate(function_str, var_context)
                    
                    # Apply direction (maximize -> minimize by negation)
                    if direction == "Maximize":
                        result = -result
                        
                    # Apply weight
                    result *= weight
                    
                    F[j, i] = result
                    
                except (SecurityError, ValueError, TypeError) as e:
                    print(f"🔒 Secure evaluation failed for objective {i+1}, solution {j+1}: {e}")
                    # Assign penalty value for failed evaluation
                    F[j, i] = 1e6
                    
                except Exception as e:
                    print(f"❌ Unexpected error in objective evaluation: {e}")
                    # If evaluation fails, assign a large penalty value
                    F[j, i] = 1e6
                    
        return F if F.shape[0] > 1 else F[0]
        
    def _evaluate_constraints(self, X, constraint_configs):
        """
        Evaluate constraint functions using secure AST-based evaluation
        
        This method safely evaluates user-defined constraint functions without
        executing potentially dangerous code. All expressions are parsed and
        evaluated using SecureMathEvaluator which only allows mathematical operations.
        
        Args:
            X: Decision variable matrix (n_solutions x n_variables)
            constraint_configs: List of constraint function configurations
            
        Returns:
            G: Constraint violation values (n_solutions x n_constraints)
               G[i] <= 0 means constraint i is satisfied
        """
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
                    # Create variable context for secure evaluation
                    var_context = {}
                    
                    # Add named variables
                    for k, var_config in enumerate(self.problem_config['variables']):
                        var_name = var_config['name']
                        var_context[var_name] = float(X[j, k])
                        
                    # Add x1, x2, etc. convenience variables
                    for k in range(X.shape[1]):
                        var_context[f'x{k+1}'] = float(X[j, k])
                    
                    # SECURE EVALUATION - No eval() or dangerous code execution
                    result = self.secure_evaluator.evaluate(function_str, var_context)
                    
                    # Convert to inequality constraint (g(x) <= 0)
                    if "≤" in constraint_type or "Less than" in constraint_type or "<=" in constraint_type:
                        # g(x) <= value -> g(x) - value <= 0
                        G[j, i] = result - constraint_value
                    elif "≥" in constraint_type or "Greater than" in constraint_type or ">=" in constraint_type:
                        # g(x) >= value -> -(g(x) - value) <= 0
                        G[j, i] = constraint_value - result
                    else:  # Equality constraint
                        # g(x) = value -> |g(x) - value| <= tolerance
                        # For simplicity, convert to inequality with small tolerance
                        G[j, i] = abs(result - constraint_value) - 1e-6
                        
                except (SecurityError, ValueError, TypeError) as e:
                    print(f"🔒 Secure evaluation failed for constraint {i+1}, solution {j+1}: {e}")
                    # Assign constraint violation for failed evaluation
                    G[j, i] = 1e6
                    
                except Exception as e:
                    print(f"❌ Unexpected error in constraint evaluation: {e}")
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
        """
        Validate function syntax using secure AST-based evaluation
        
        This method safely validates mathematical expressions without executing
        potentially dangerous code. It uses SecureMathEvaluator to parse and
        validate expressions using Abstract Syntax Trees.
        
        Args:
            function_str: Mathematical expression to validate
            variables: List of variable definitions
            
        Returns:
            bool: True if expression is valid and safe, False otherwise
        """
        try:
            # Create test context with safe values
            var_context = {}
            for var in variables:
                var_context[var['name']] = 1.0
                
            # Add x1, x2, etc. convenience variables
            for i in range(len(variables)):
                var_context[f'x{i+1}'] = 1.0
            
            # Test with secure evaluator (no actual execution of user code)
            self.secure_evaluator.evaluate(function_str, var_context)
            return True
            
        except (SecurityError, ValueError, TypeError) as e:
            print(f"🔒 Expression validation failed: {e}")
            return False
        except Exception as e:
            print(f"❌ Unexpected validation error: {e}")
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
