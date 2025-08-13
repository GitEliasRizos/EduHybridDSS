# PyMOO GUI - Multi-Objective Optimization Interface

A comprehensive graphical user interface for PyMOO (Multi-objective Optimization in Python) built with PyQt6.

## Features

- **Problem Definition**: Define custom optimization problems with variables, objectives, and constraints
- **Algorithm Selection**: Choose from various multi-objective optimization algorithms
- **Variable Configuration**: Set variable bounds, types, and initial values
- **Objective Function Setup**: Define multiple objectives with weights and directions
- **Constraint Management**: Add equality and inequality constraints
- **Crossover & Mutation**: Configure genetic operators for evolutionary algorithms
- **Reference Directions**: Set up reference directions for algorithms that require them
- **Results Visualization**: View optimization results and convergence plots

## Installation

1. Clone or download this project
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the main application:
```bash
python main.py
```

## Project Structure

```
├── main.py                 # Main application entry point
├── ui/                     # UI components
│   ├── main_window.py      # Main window class
│   ├── problem_tab.py      # Problem definition tab
│   ├── algorithm_tab.py    # Algorithm configuration tab
│   ├── results_tab.py      # Results visualization tab
│   └── dialogs/            # Dialog windows
├── core/                   # Core functionality
│   ├── problem_manager.py  # Problem definition management
│   ├── algorithm_manager.py# Algorithm configuration
│   └── optimizer.py        # Optimization execution
├── utils/                  # Utility functions
│   ├── validators.py       # Input validation
│   └── helpers.py          # Helper functions
└── examples/               # Example problems
```

## Requirements

- Python 3.8+
- PyMOO 0.6.0+
- PyQt6 6.5.0+
- NumPy 1.21.0+
- Matplotlib 3.5.0+
- SciPy 1.7.0+
