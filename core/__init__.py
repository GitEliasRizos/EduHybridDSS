"""
Core Package - PyMOO GUI Optimization Engine

This package contains the core optimization functionality for the PyMOO GUI application.
It provides the essential components for defining, configuring, and executing
multi-objective optimization problems using the PyMOO framework.

Core Modules:
    problem_manager: Handles optimization problem definition and conversion to PyMOO format
    algorithm_manager: Manages algorithm selection, configuration, and instantiation  
    optimizer: Coordinates optimization execution with progress monitoring
    mcda: Multi-criteria decision analysis for result ranking and selection

Key Features:
- Problem definition with mixed variable types (Real, Integer, Binary)
- Support for multiple multi-objective algorithms (NSGA-II, NSGA-III, MOEA/D)
- Custom objective function evaluation with mathematical expression parsing
- Constraint handling and validation
- Reference direction generation for many-objective problems
- Real-time optimization progress monitoring
- Comprehensive result processing and analysis
- MCDA integration for decision support

The core package is designed to be independent of the GUI components, allowing
for potential command-line or API usage in the future. All GUI interactions
are handled through well-defined interfaces and signal/slot mechanisms.

Author: Elias Rizos [it21490]
Version: 1.3.2
"""

# Core package for PyMOO GUI optimization engine
# Main components are imported on-demand to avoid circular dependencies

__version__ = "1.3.2"
__author__ = "Elias Rizos [it21490]"

# Export main classes for convenient importing
__all__ = [
    'ProblemManager',
    'AlgorithmManager', 
    'Optimizer',
    'MCDAManager',
    'AHPAnalyzer',
    'TOPSISAnalyzer'
]