"""
Utils Package - PyMOO GUI Utility Functions and Helpers

This package contains utility functions, validators, and helper classes that
support the PyMOO GUI application. It provides common functionality used
across multiple modules for data processing, validation, file operations,
and configuration management.

Utility Modules:
    helpers: General utility functions for file I/O, data processing, and visualization
    validators: Input validation and error checking utilities
    secure_evaluator: Safe mathematical expression evaluation (security-focused)
    secure_problem_manager: Enhanced problem management with security features

Key Features:
- Configuration save/load functionality with error handling
- Comprehensive input validation for all user inputs
- Safe mathematical expression evaluation with security checks
- File format validation and cross-platform path handling
- Data serialization utilities for complex nested structures
- Visualization helpers for consistent plot styling
- Performance measurement and debugging utilities
- Security-first approach for user-provided expressions

Security Features:
- Sandboxed expression evaluation to prevent code injection
- Input sanitization and validation at multiple levels
- Safe import restrictions for mathematical expressions
- Comprehensive error handling with detailed feedback

The utilities package follows defensive programming principles with
extensive validation, error handling, and security considerations
to ensure robust operation even with invalid or malicious inputs.

Author: Elias Rizos [it21490]
Version: 1.3.2
"""

# Utils package for PyMOO GUI utility functions
# Contains helpers, validators, and security utilities

__version__ = "1.3.2"
__author__ = "Elias Rizos [it21490]"

# Export main utility functions for convenient importing
__all__ = [
    'save_problem_config',
    'load_problem_config', 
    'save_algorithm_config',
    'load_algorithm_config',
    'validate_problem_config',
    'validate_algorithm_config',
    'ValidationError',
    'SecureEvaluator'
]
