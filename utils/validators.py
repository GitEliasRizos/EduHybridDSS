"""
Validators - Input validation utilities

This module provides comprehensive validation utilities for the PyMOO GUI
application. It includes validators for problem configurations, algorithm
settings, and mathematical expressions to ensure data integrity and provide
helpful error messages to users.

Key Features:
- Problem configuration validation (variables, objectives, constraints)
- Algorithm parameter validation and range checking
- Mathematical expression syntax validation with security checks
- Variable name and identifier validation
- Bounds checking and consistency validation
- Detailed error reporting with specific issue descriptions
- Safe evaluation of mathematical expressions
- Integration with GUI for real-time validation feedback

The validation system is designed to catch errors early and provide clear,
actionable feedback to help users create valid optimization configurations.
It includes both structural validation (required fields, data types) and
semantic validation (logical consistency, mathematical validity).

Validation Categories:
    - Structural: Required fields, data types, array dimensions
    - Semantic: Logical consistency, mathematical validity
    - Security: Safe expression evaluation, injection prevention
    - Range: Parameter bounds, reasonable value checking
    - Syntax: Mathematical expression parsing and validation

Classes:
    ValidationError: Custom exception for validation errors
    ProblemValidator: Validates problem configurations
    AlgorithmValidator: Validates algorithm configurations  
    ExpressionValidator: Validates mathematical expressions
    
Design Philosophy:
    - Fail fast with clear error messages
    - Provide suggestions for fixing common issues
    - Security-first approach for user expressions
    - Comprehensive coverage of edge cases
    
Author: Elias Rizos [it21490]
Version: 1.3.2
"""

import re
import numpy as np
from typing import List, Dict, Any, Tuple, Optional


class ValidationError(Exception):
    """
    Custom exception for validation errors
    
    This exception is raised when validation fails and provides
    detailed information about what went wrong and how to fix it.
    
    Attributes:
        message (str): Detailed error description
        field (str): The field that caused the validation error
        suggestions (list): Possible solutions or fixes
    """
    pass


class ProblemValidator:
    """
    Validator for optimization problem configurations
    
    This class provides comprehensive validation for problem definitions
    including variables, objectives, and constraints. It ensures that
    problem configurations are complete, consistent, and mathematically
    valid before they are passed to the optimization engine.
    
    Key Validation Areas:
    - Structural integrity (required fields, correct data types)
    - Variable definitions (names, bounds, types)
    - Objective functions (syntax, variable references, directions)
    - Constraint specifications (expressions, operators, bounds)
    - Cross-references between components (variable names consistency)
    - Mathematical expression validity and security
    
    The validator provides detailed error messages that help users
    identify and fix configuration issues quickly.
    """
    
    @staticmethod
    def validate_problem_config(config: Dict[str, Any]) -> List[str]:
        """
        Validate complete problem configuration
        
        This is the main validation entry point that performs comprehensive
        checking of all problem configuration aspects. It validates structure,
        variables, objectives, and constraints in the correct order.
        
        Args:
            config (Dict[str, Any]): Complete problem configuration dictionary
                Expected to contain:
                - name: Problem name (string)
                - variables: List of variable definitions
                - objectives: List of objective function definitions
                - constraints: List of constraint definitions (optional)
                
        Returns:
            List[str]: List of validation error messages. Empty list indicates
                      successful validation.
                      
        The validation is performed in dependency order:
        1. Basic structure validation
        2. Variable validation (foundation for other components)
        3. Objective validation (references variables)
        4. Constraint validation (references variables)
        """
        errors = []
        
        # Phase 1: Validate basic configuration structure and required fields
        errors.extend(ProblemValidator._validate_basic_structure(config))
        
        # Phase 2: Validate variable definitions (foundation for other validations)
        if 'variables' in config:
            errors.extend(ProblemValidator._validate_variables(config['variables']))
            
        # Phase 3: Validate objective function definitions
        if 'objectives' in config:
            errors.extend(ProblemValidator._validate_objectives(
                config['objectives'], 
                config.get('variables', [])
            ))
            
        # Phase 4: Validate constraint definitions (optional)
        if 'constraints' in config:
            errors.extend(ProblemValidator._validate_constraints(
                config['constraints'], 
                config.get('variables', [])
            ))
            
        return errors
        
    @staticmethod
    def _validate_basic_structure(config: Dict[str, Any]) -> List[str]:
        """
        Validate basic configuration structure and required fields
        
        Checks that the configuration has the minimum required structure
        and that required fields are present with appropriate data types.
        
        Args:
            config (Dict[str, Any]): Configuration dictionary to validate
            
        Returns:
            List[str]: List of structural validation errors
            
        Validates:
        - Required fields presence (name, variables, objectives)
        - Correct data types for each field
        - Non-empty collections where required
        - Basic naming conventions
        """
        errors = []
        
        # Check for required top-level fields
        required_fields = ['name', 'variables', 'objectives']
        for field in required_fields:
            if field not in config:
                errors.append(f"Missing required field: {field}")
            elif field == 'name' and not isinstance(config[field], str):
                errors.append("Problem name must be a string")
            elif field in ['variables', 'objectives'] and not isinstance(config[field], list):
                errors.append(f"{field} must be a list")
                
        # Check optional fields
        if 'constraints' in config and not isinstance(config['constraints'], list):
            errors.append("Constraints must be a list")
            
        if 'description' in config and not isinstance(config['description'], str):
            errors.append("Description must be a string")
            
        return errors
        
    @staticmethod
    def _validate_variables(variables: List[Dict[str, Any]]) -> List[str]:
        """Validate variables configuration"""
        errors = []
        
        if len(variables) == 0:
            errors.append("At least one variable must be defined")
            return errors
            
        variable_names = set()
        
        for i, var in enumerate(variables):
            var_prefix = f"Variable {i+1}"
            
            # Check required fields
            required_fields = ['name', 'type', 'lower_bound', 'upper_bound']
            for field in required_fields:
                if field not in var:
                    errors.append(f"{var_prefix}: Missing required field '{field}'")
                    continue
                    
            # Validate name
            if 'name' in var:
                name = var['name']
                if not isinstance(name, str) or not name.strip():
                    errors.append(f"{var_prefix}: Name must be a non-empty string")
                elif name in variable_names:
                    errors.append(f"{var_prefix}: Duplicate variable name '{name}'")
                elif not ProblemValidator._is_valid_identifier(name):
                    errors.append(f"{var_prefix}: Name '{name}' is not a valid identifier")
                else:
                    variable_names.add(name)
                    
            # Validate type
            if 'type' in var:
                valid_types = ['Real', 'Integer', 'Binary']
                if var['type'] not in valid_types:
                    errors.append(f"{var_prefix}: Type must be one of {valid_types}")
                    
            # Validate bounds
            if 'lower_bound' in var and 'upper_bound' in var:
                try:
                    lower = float(var['lower_bound'])
                    upper = float(var['upper_bound'])
                    
                    if lower >= upper:
                        errors.append(f"{var_prefix}: Lower bound must be less than upper bound")
                        
                    # Additional validation for specific types
                    if var.get('type') == 'Binary':
                        if lower != 0 or upper != 1:
                            errors.append(f"{var_prefix}: Binary variables must have bounds [0, 1]")
                            
                except (ValueError, TypeError):
                    errors.append(f"{var_prefix}: Bounds must be numeric values")
                    
            # Validate initial value if provided
            if 'initial_value' in var:
                try:
                    initial = float(var['initial_value'])
                    if 'lower_bound' in var and 'upper_bound' in var:
                        lower = float(var['lower_bound'])
                        upper = float(var['upper_bound'])
                        if not (lower <= initial <= upper):
                            errors.append(f"{var_prefix}: Initial value must be within bounds")
                except (ValueError, TypeError):
                    errors.append(f"{var_prefix}: Initial value must be numeric")
                    
        return errors
        
    @staticmethod
    def _validate_objectives(objectives: List[Dict[str, Any]], variables: List[Dict[str, Any]]) -> List[str]:
        """Validate objectives configuration"""
        errors = []
        
        if len(objectives) == 0:
            errors.append("At least one objective must be defined")
            return errors
            
        objective_names = set()
        variable_names = [var.get('name', f'x{i+1}') for i, var in enumerate(variables)]
        
        for i, obj in enumerate(objectives):
            obj_prefix = f"Objective {i+1}"
            
            # Check required fields
            required_fields = ['name', 'direction', 'function']
            for field in required_fields:
                if field not in obj:
                    errors.append(f"{obj_prefix}: Missing required field '{field}'")
                    continue
                    
            # Validate name
            if 'name' in obj:
                name = obj['name']
                if not isinstance(name, str) or not name.strip():
                    errors.append(f"{obj_prefix}: Name must be a non-empty string")
                elif name in objective_names:
                    errors.append(f"{obj_prefix}: Duplicate objective name '{name}'")
                elif not ProblemValidator._is_valid_identifier(name):
                    errors.append(f"{obj_prefix}: Name '{name}' is not a valid identifier")
                else:
                    objective_names.add(name)
                    
            # Validate direction
            if 'direction' in obj:
                valid_directions = ['Minimize', 'Maximize']
                if obj['direction'] not in valid_directions:
                    errors.append(f"{obj_prefix}: Direction must be one of {valid_directions}")
                    
            # Validate weight
            if 'weight' in obj:
                try:
                    weight = float(obj['weight'])
                    if weight <= 0:
                        errors.append(f"{obj_prefix}: Weight must be positive")
                except (ValueError, TypeError):
                    errors.append(f"{obj_prefix}: Weight must be numeric")
                    
            # Validate function
            if 'function' in obj:
                function = obj['function']
                if not isinstance(function, str) or not function.strip():
                    errors.append(f"{obj_prefix}: Function must be a non-empty string")
                else:
                    # Validate function syntax
                    func_errors = ProblemValidator._validate_function_syntax(function, variable_names)
                    for error in func_errors:
                        errors.append(f"{obj_prefix}: {error}")
                        
        return errors
        
    @staticmethod
    def _validate_constraints(constraints: List[Dict[str, Any]], variables: List[Dict[str, Any]]) -> List[str]:
        """Validate constraints configuration"""
        errors = []
        
        constraint_names = set()
        variable_names = [var.get('name', f'x{i+1}') for i, var in enumerate(variables)]
        
        for i, const in enumerate(constraints):
            const_prefix = f"Constraint {i+1}"
            
            # Check required fields
            required_fields = ['name', 'type', 'function', 'value']
            for field in required_fields:
                if field not in const:
                    errors.append(f"{const_prefix}: Missing required field '{field}'")
                    continue
                    
            # Validate name
            if 'name' in const:
                name = const['name']
                if not isinstance(name, str) or not name.strip():
                    errors.append(f"{const_prefix}: Name must be a non-empty string")
                elif name in constraint_names:
                    errors.append(f"{const_prefix}: Duplicate constraint name '{name}'")
                elif not ProblemValidator._is_valid_identifier(name):
                    errors.append(f"{const_prefix}: Name '{name}' is not a valid identifier")
                else:
                    constraint_names.add(name)
                    
            # Validate type
            if 'type' in const:
                valid_types = ['≤ (Less than or equal)', '≥ (Greater than or equal)', '= (Equal to)']
                if const['type'] not in valid_types:
                    errors.append(f"{const_prefix}: Type must be one of {valid_types}")
                    
            # Validate value
            if 'value' in const:
                try:
                    float(const['value'])
                except (ValueError, TypeError):
                    errors.append(f"{const_prefix}: Value must be numeric")
                    
            # Validate function
            if 'function' in const:
                function = const['function']
                if not isinstance(function, str) or not function.strip():
                    errors.append(f"{const_prefix}: Function must be a non-empty string")
                else:
                    # Validate function syntax
                    func_errors = ProblemValidator._validate_function_syntax(function, variable_names)
                    for error in func_errors:
                        errors.append(f"{const_prefix}: {error}")
                        
        return errors
        
    @staticmethod
    def _validate_function_syntax(function: str, variable_names: List[str]) -> List[str]:
        """Validate mathematical function syntax"""
        errors = []
        
        # Check for empty function
        if not function.strip():
            errors.append("Function cannot be empty")
            return errors
            
        # Check for dangerous constructs
        dangerous_patterns = [
            r'__.*__',  # Dunder methods
            r'import\s+',  # Import statements
            r'exec\s*\(',  # Exec function
            r'eval\s*\(',  # Eval function (we'll use it safely)
            r'open\s*\(',  # File operations
            r'subprocess',  # Subprocess module
            r'os\.',  # OS module
            r'sys\.',  # Sys module
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, function, re.IGNORECASE):
                errors.append(f"Function contains potentially dangerous construct: {pattern}")
                
        # Check for valid mathematical syntax
        try:
            # Create test context
            test_context = {}
            
            # Add variables
            for name in variable_names:
                test_context[name] = 1.0
                
            # Add x1, x2, etc. for convenience
            for i in range(len(variable_names)):
                test_context[f'x{i+1}'] = 1.0
                
            # Add mathematical functions
            test_context.update({
                'sin': np.sin, 'cos': np.cos, 'tan': np.tan,
                'asin': np.arcsin, 'acos': np.arccos, 'atan': np.arctan,
                'sinh': np.sinh, 'cosh': np.cosh, 'tanh': np.tanh,
                'exp': np.exp, 'log': np.log, 'log10': np.log10,
                'sqrt': np.sqrt, 'pow': np.power,
                'abs': np.abs, 'floor': np.floor, 'ceil': np.ceil,
                'min': min, 'max': max, 'sum': sum,
                'pi': np.pi, 'e': np.e
            })
            
            # Try to compile and evaluate
            compiled = compile(function, '<string>', 'eval')
            result = eval(compiled, {"__builtins__": {}}, test_context)
            
            # Check if result is numeric
            if not isinstance(result, (int, float, np.number)):
                try:
                    float(result)
                except (ValueError, TypeError):
                    errors.append("Function must return a numeric value")
                        
        except SyntaxError as e:
            errors.append(f"Syntax error in function: {e}")
        except Exception as e:
            errors.append(f"Error evaluating function: {e}")
            
        return errors
        
    @staticmethod
    def _is_valid_identifier(name: str) -> bool:
        """Check if a name is a valid Python identifier"""
        return name.isidentifier() and not name.startswith('__')


class AlgorithmValidator:
    """Validator for algorithm configurations"""
    
    @staticmethod
    def validate_algorithm_config(config: Dict[str, Any]) -> List[str]:
        """Validate complete algorithm configuration"""
        errors = []
        
        # Check required fields
        if 'name' not in config:
            errors.append("Algorithm name is required")
            
        # Validate parameters
        if 'parameters' in config:
            errors.extend(AlgorithmValidator._validate_parameters(config['parameters']))
            
        # Validate genetic operators
        if 'crossover' in config:
            errors.extend(AlgorithmValidator._validate_crossover(config['crossover']))
            
        if 'mutation' in config:
            errors.extend(AlgorithmValidator._validate_mutation(config['mutation']))
            
        # Validate termination
        if 'termination' in config:
            errors.extend(AlgorithmValidator._validate_termination(config['termination']))
            
        return errors
        
    @staticmethod
    def _validate_parameters(params: Dict[str, Any]) -> List[str]:
        """Validate algorithm parameters"""
        errors = []
        
        # Population size
        if 'population_size' in params:
            try:
                pop_size = int(params['population_size'])
                if pop_size < 4:
                    errors.append("Population size must be at least 4")
                elif pop_size > 10000:
                    errors.append("Population size should not exceed 10,000")
            except (ValueError, TypeError):
                errors.append("Population size must be an integer")
                
        # Number of generations
        if 'n_generations' in params:
            try:
                n_gen = int(params['n_generations'])
                if n_gen < 1:
                    errors.append("Number of generations must be at least 1")
            except (ValueError, TypeError):
                errors.append("Number of generations must be an integer")
                
        # Seed
        if 'seed' in params:
            try:
                seed = int(params['seed'])
                if seed < 0 or seed >= 2**32:
                    errors.append("Seed must be between 0 and 2^32-1")
            except (ValueError, TypeError):
                errors.append("Seed must be an integer")
                
        return errors
        
    @staticmethod
    def _validate_crossover(crossover: Dict[str, Any]) -> List[str]:
        """Validate crossover configuration"""
        errors = []
        
        # Probability
        if 'probability' in crossover:
            try:
                prob = float(crossover['probability'])
                if not (0.0 <= prob <= 1.0):
                    errors.append("Crossover probability must be between 0 and 1")
            except (ValueError, TypeError):
                errors.append("Crossover probability must be numeric")
                
        # Eta (for SBX)
        if 'eta' in crossover:
            try:
                eta = float(crossover['eta'])
                if eta < 0:
                    errors.append("Crossover eta must be non-negative")
            except (ValueError, TypeError):
                errors.append("Crossover eta must be numeric")
                
        return errors
        
    @staticmethod
    def _validate_mutation(mutation: Dict[str, Any]) -> List[str]:
        """Validate mutation configuration"""
        errors = []
        
        # Probability
        if 'probability' in mutation:
            try:
                prob = float(mutation['probability'])
                if not (0.0 <= prob <= 1.0):
                    errors.append("Mutation probability must be between 0 and 1")
            except (ValueError, TypeError):
                errors.append("Mutation probability must be numeric")
                
        # Eta (for Polynomial Mutation)
        if 'eta' in mutation:
            try:
                eta = float(mutation['eta'])
                if eta < 0:
                    errors.append("Mutation eta must be non-negative")
            except (ValueError, TypeError):
                errors.append("Mutation eta must be numeric")
                
        return errors
        
    @staticmethod
    def _validate_termination(termination: Dict[str, Any]) -> List[str]:
        """Validate termination configuration"""
        errors = []
        
        # Maximum evaluations
        if 'max_evaluations' in termination:
            try:
                max_eval = int(termination['max_evaluations'])
                if max_eval < 1:
                    errors.append("Maximum evaluations must be at least 1")
            except (ValueError, TypeError):
                errors.append("Maximum evaluations must be an integer")
                
        # Convergence tolerance
        if 'convergence_tolerance' in termination:
            try:
                tol = float(termination['convergence_tolerance'])
                if tol <= 0:
                    errors.append("Convergence tolerance must be positive")
            except (ValueError, TypeError):
                errors.append("Convergence tolerance must be numeric")
                
        return errors


def validate_numeric_input(value: str, min_val: float = None, max_val: float = None) -> Tuple[bool, Optional[float], str]:
    """Validate numeric input from user interface"""
    try:
        num_val = float(value)
        
        if min_val is not None and num_val < min_val:
            return False, None, f"Value must be at least {min_val}"
        if max_val is not None and num_val > max_val:
            return False, None, f"Value must be at most {max_val}"
            
        return True, num_val, ""
    except ValueError:
        return False, None, "Invalid numeric value"


def validate_integer_input(value: str, min_val: int = None, max_val: int = None) -> Tuple[bool, Optional[int], str]:
    """Validate integer input from user interface"""
    try:
        int_val = int(value)
        
        if min_val is not None and int_val < min_val:
            return False, None, f"Value must be at least {min_val}"
        if max_val is not None and int_val > max_val:
            return False, None, f"Value must be at most {max_val}"
            
        return True, int_val, ""
    except ValueError:
        return False, None, "Invalid integer value"
