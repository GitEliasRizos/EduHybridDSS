"""
UI Package - PyMOO GUI User Interface Components

This package contains all user interface components for the PyMOO GUI application.
It provides a comprehensive Qt6-based interface for multi-objective optimization
problem setup, algorithm configuration, execution monitoring, and result analysis.

UI Modules:
    main_window: Main application window with tab coordination and menu system
    problem_tab: Interface for defining optimization problems (variables, objectives, constraints)
    algorithm_tab: Algorithm selection and parameter configuration interface
    results_tab: Optimization execution, progress monitoring, and result visualization
    mcda_tab: Multi-criteria decision analysis interface for solution ranking

Key Features:
- Intuitive tabbed interface following optimization workflow
- Real-time validation and feedback for user inputs
- Comprehensive parameter configuration with intelligent defaults
- Progress monitoring with cancellation support
- Rich result visualization with matplotlib integration
- Export/import functionality for configurations and results
- Multi-criteria decision analysis with AHP and TOPSIS methods
- Responsive design that adapts to different problem complexities

Design Philosophy:
- User-friendly interface suitable for both beginners and experts
- Clear workflow progression through logical tabs
- Immediate feedback and validation to prevent errors
- Comprehensive help and guidance throughout the application
- Professional appearance with consistent styling

The UI package uses PyQt6 for modern, cross-platform interface capabilities
and integrates seamlessly with the core optimization engine through Qt's
signal/slot mechanism for responsive, non-blocking operation.

Author: Elias Rizos [it21490]
Version: 1.3.2
"""

# UI package for PyMOO GUI application
# Contains all Qt6-based user interface components

__version__ = "1.3.2"
__author__ = "Elias Rizos [it21490]"

# Export main UI classes for convenient importing
__all__ = [
    'MainWindow',
    'ProblemTab',
    'AlgorithmTab',
    'ResultsTab',
    'MCDATab'
]
