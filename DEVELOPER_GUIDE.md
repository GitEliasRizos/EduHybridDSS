# PyMOO GUI Developer Guide

## Table of Contents

1. [Getting Started](#getting-started)
2. [Development Environment Setup](#development-environment-setup)
3. [Project Structure](#project-structure)
4. [Development Workflow](#development-workflow)
5. [Core Components](#core-components)
6. [Security Guidelines](#security-guidelines)
7. [Testing Framework](#testing-framework)
8. [Code Style and Standards](#code-style-and-standards)
9. [Debugging and Troubleshooting](#debugging-and-troubleshooting)
10. [Contributing Guidelines](#contributing-guidelines)
11. [API Reference](#api-reference)
12. [Advanced Topics](#advanced-topics)

---

## Getting Started

### Prerequisites

- **Python 3.8+** (Recommended: Python 3.11+)
- **Git** for version control
- **VS Code** (recommended IDE with provided configuration)
- **Virtual Environment** support (venv, conda, or virtualenv)

### Quick Start

1. **Clone the Repository**
   ```bash
   git clone https://github.com/GitEliasRizos/NewDSS.git
   cd NewDSS
   ```

2. **Set Up Virtual Environment**
   ```bash
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # Linux/macOS
   source .venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Application**
   ```bash
   python main.py
   ```

---

## Development Environment Setup

### Recommended IDE Configuration

**VS Code Extensions:**
- Python (Microsoft)
- PyQt Integration (optional)
- GitLens (for Git integration)
- Python Docstring Generator
- Pylance (Python language server)

**VS Code Settings (`.vscode/settings.json`)**:
```json
{
    "python.defaultInterpreterPath": "./.venv/Scripts/python.exe",
    "python.analysis.typeCheckingMode": "basic",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.formatting.provider": "black",
    "files.associations": {
        "*.json": "json"
    }
}
```

### Environment Variables

Create a `.env` file in the project root:
```env
PYTHONPATH=.
PYMOO_DEBUG=False
QT_LOGGING_RULES="*=false"
```

### Development Tools

**Required:**
```bash
pip install black          # Code formatting
pip install pylint         # Code linting
pip install pytest         # Testing framework
pip install mypy           # Type checking
```

**Optional:**
```bash
pip install jupyter        # For algorithm experimentation
pip install profilehooks   # Performance profiling
pip install memory_profiler # Memory usage analysis
```

---

## Project Structure

### Directory Layout

```
NewDSS/
├── main.py                 # Application entry point
├── requirements.txt        # Dependencies
├── .gitignore             # Git ignore rules
├── .venv/                 # Virtual environment (not in git)
│
├── core/                  # Core business logic
│   ├── __init__.py
│   ├── problem_manager.py     # Problem definition and validation
│   ├── algorithm_manager.py   # Algorithm configuration
│   ├── optimizer.py           # Optimization execution
│   └── mcda.py               # Multi-criteria decision analysis
│
├── ui/                    # User interface components
│   ├── __init__.py
│   ├── main_window.py        # Main application window
│   ├── problem_tab.py        # Problem definition interface
│   ├── algorithm_tab.py      # Algorithm configuration
│   ├── results_tab.py        # Results visualization
│   └── mcda_tab.py          # MCDA interface
│
├── utils/                 # Utility functions and helpers
│   ├── __init__.py
│   ├── validators.py         # Input validation
│   └── helpers.py           # Common utilities
│
├── examples/              # Example problems and benchmarks
│   ├── benchmarks/          # General benchmarks
│   │   ├── algorithm_specific/  # Algorithm-specific tests
│   │   └── README.md
│   └── *.json              # Problem definition files
│
└── docs/                  # Documentation (this guide)
    ├── ARCHITECTURE.md
    ├── DEVELOPER_GUIDE.md
    └── PROJECT_STATUS.md
```

### File Naming Conventions

- **Python Files**: `snake_case.py`
- **Classes**: `PascalCase`
- **Functions/Methods**: `snake_case()`
- **Constants**: `UPPER_SNAKE_CASE`
- **JSON Files**: `descriptive_name.json`
- **Documentation**: `UPPERCASE.md`

---

## Development Workflow

### Git Workflow

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/algorithm-enhancement
   ```

2. **Make Changes and Commit**
   ```bash
   git add .
   git commit -m "feat: add new algorithm support"
   ```

3. **Push and Create PR**
   ```bash
   git push origin feature/algorithm-enhancement
   # Create pull request on GitHub
   ```

### Code Quality Checks

**Before Committing:**
```bash
# Format code
black .

# Lint code
pylint core/ ui/ utils/

# Type checking
mypy core/ ui/ utils/

# Run tests
pytest
```

### Development Server

For development with auto-reload:
```bash
# Install development dependencies
pip install watchdog

# Run with file watching (custom script needed)
python dev_server.py
```

---

## Core Components

### 1. ProblemManager (`core/problem_manager.py`)

**Purpose**: Handles problem definition, validation, and mathematical expression evaluation.

**Key Features:**
- **SecureMathEvaluator**: AST-based expression parsing
- **Numpy Integration**: Full mathematical function support
- **JSON I/O**: Problem import/export functionality

**Usage Example:**
```python
from core.problem_manager import ProblemManager

# Create problem manager
pm = ProblemManager()

# Define a simple problem
problem_data = {
    "name": "Test Problem",
    "variables": [
        {"name": "x1", "type": "real", "lower_bound": -5, "upper_bound": 5},
        {"name": "x2", "type": "real", "lower_bound": -5, "upper_bound": 5}
    ],
    "objectives": [
        {"name": "f1", "expression": "x1**2 + x2**2", "type": "minimize"},
        {"name": "f2", "expression": "np.sin(x1) + np.cos(x2)", "type": "minimize"}
    ],
    "constraints": []
}

# Create and validate problem
problem = pm.create_problem(problem_data)
is_valid, errors = pm.validate_problem(problem_data)
```

**Security Implementation:**
```python
class SecureMathEvaluator:
    """AST-based secure mathematical expression evaluator"""
    
    def __init__(self):
        self.allowed_names = {
            # Math functions
            'sin', 'cos', 'tan', 'sqrt', 'log', 'exp', 'abs',
            # NumPy module
            'np': np,
            # Constants
            'pi': np.pi, 'e': np.e
        }
        
    def evaluate(self, expression, variables):
        """Safely evaluate mathematical expressions using AST parsing"""
        try:
            tree = ast.parse(expression, mode='eval')
            return self._eval_node(tree.body, variables)
        except Exception as e:
            raise ValueError(f"Expression evaluation failed: {e}")
```

### 2. AlgorithmManager (`core/algorithm_manager.py`)

**Purpose**: Manages algorithm selection, configuration, and instantiation.

**Supported Algorithms:**
- NSGA-II: Multi-objective genetic algorithm
- NSGA-III: Many-objective optimization with reference points
- SPEA2: Strength Pareto evolutionary algorithm
- MOEA/D: Decomposition-based approach
- RVEA: Reference vector guided evolution
- IBEA: Indicator-based optimization
- SMS-EMOA: S-metric selection
- GDE3: Generalized differential evolution
- CTAEA: Constrained two-archive algorithm

**Usage Example:**
```python
from core.algorithm_manager import AlgorithmManager

am = AlgorithmManager()

# Get available algorithms
algorithms = am.get_supported_algorithms()

# Configure NSGA-II
config = {
    "name": "NSGA2",
    "population_size": 100,
    "n_gen": 250,
    "crossover": {"type": "SBX", "prob": 0.9, "eta": 15},
    "mutation": {"type": "PM", "prob": None, "eta": 20}
}

# Create algorithm instance
algorithm = am.create_algorithm(config, problem)
```

### 3. Optimizer (`core/optimizer.py`)

**Purpose**: Executes optimization runs and manages results.

**Features:**
- Progress tracking with callbacks
- Result collection and formatting
- Error handling and recovery
- Performance monitoring

**Usage Example:**
```python
from core.optimizer import Optimizer

optimizer = Optimizer()

# Run optimization
def progress_callback(algorithm):
    print(f"Generation: {algorithm.n_gen}")

result = optimizer.optimize(
    problem=problem,
    algorithm=algorithm,
    callback=progress_callback,
    verbose=True
)

# Access results
pareto_front = result.F
decision_variables = result.X
```

### 4. UI Components (`ui/` directory)

**MainWindow**: Central application coordinator
```python
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.setup_tabs()
        self.setup_menus()
        
    def setup_tabs(self):
        self.problem_tab = ProblemTab()
        self.algorithm_tab = AlgorithmTab()
        self.results_tab = ResultsTab()
        self.mcda_tab = MCDATab()
```

**Tab Architecture**: Each tab is self-contained with:
- UI setup methods
- Event handlers
- Data validation
- Integration points

---

## Security Guidelines

### 🔒 Expression Evaluation Security

**CRITICAL: Never use `eval()` or `exec()`**

❌ **Dangerous (DO NOT DO):**
```python
# NEVER DO THIS - Security vulnerability!
result = eval(user_expression)
```

✅ **Safe (Always Do This):**
```python
# Use the SecureMathEvaluator
evaluator = SecureMathEvaluator()
result = evaluator.evaluate(user_expression, variables)
```

### Security Checklist

- ✅ All user input validated before processing
- ✅ Mathematical expressions parsed with AST only
- ✅ File system access blocked in expression evaluation
- ✅ System commands prevented in user input
- ✅ Namespace isolation for expression variables
- ✅ Error messages don't expose system information

### Input Validation Pattern

```python
def validate_input(user_input, input_type="string"):
    """Standard input validation pattern"""
    if input_type == "expression":
        # Use SecureMathEvaluator for validation
        try:
            evaluator = SecureMathEvaluator()
            evaluator.validate_expression(user_input)
            return True, None
        except ValueError as e:
            return False, str(e)
    
    elif input_type == "numeric":
        try:
            float(user_input)
            return True, None
        except ValueError:
            return False, "Must be a valid number"
    
    return True, None
```

---

## Testing Framework

### Test Structure

```
tests/
├── __init__.py
├── test_problem_manager.py      # Problem definition tests
├── test_algorithm_manager.py    # Algorithm configuration tests
├── test_optimizer.py           # Optimization execution tests
├── test_security.py            # Security validation tests
└── benchmarks/
    ├── test_algorithm_specific.py
    └── test_integration.py
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_problem_manager.py

# Run with coverage
pytest --cov=core --cov=ui --cov=utils

# Run security tests specifically
pytest tests/test_security.py -v
```

### Writing Tests

**Example Test Structure:**
```python
import pytest
from core.problem_manager import ProblemManager, SecureMathEvaluator

class TestSecureMathEvaluator:
    def setup_method(self):
        self.evaluator = SecureMathEvaluator()
    
    def test_basic_arithmetic(self):
        """Test basic mathematical operations"""
        variables = {'x': 2, 'y': 3}
        result = self.evaluator.evaluate('x + y', variables)
        assert result == 5
    
    def test_numpy_functions(self):
        """Test numpy function integration"""
        variables = {'x': 0}
        result = self.evaluator.evaluate('np.sin(x)', variables)
        assert abs(result - 0) < 1e-10
    
    def test_security_blocked_eval(self):
        """Test that dangerous operations are blocked"""
        with pytest.raises(ValueError):
            self.evaluator.evaluate('__import__("os").system("ls")', {})
    
    def test_file_access_blocked(self):
        """Test that file access is prevented"""
        with pytest.raises(ValueError):
            self.evaluator.evaluate('open("test.txt")', {})
```

### Benchmark Testing

```python
# Test algorithm-specific benchmarks
def test_nsga2_benchmark():
    """Test NSGA-II with appropriate benchmark problem"""
    problem_file = "examples/benchmarks/algorithm_specific/nsga2_biobjective_test.json"
    # Load and run optimization
    # Validate results meet expected criteria
```

---

## Code Style and Standards

### Python Style Guide

**Follow PEP 8 with these additions:**

1. **Line Length**: 88 characters (Black formatter default)
2. **Imports**: Grouped and sorted
   ```python
   # Standard library
   import os
   import sys
   
   # Third party
   import numpy as np
   from PyQt6.QtWidgets import QWidget
   
   # Local imports
   from core.problem_manager import ProblemManager
   ```

3. **Docstrings**: Use Google style
   ```python
   def create_problem(self, problem_data: dict) -> Problem:
       """Create a PyMOO problem instance from problem data.
       
       Args:
           problem_data: Dictionary containing problem definition
           
       Returns:
           Configured PyMOO problem instance
           
       Raises:
           ValueError: If problem data is invalid
       """
   ```

### Code Organization

**Class Structure:**
```python
class ExampleClass:
    """Class docstring explaining purpose and usage."""
    
    def __init__(self, param: str):
        """Initialize with parameters."""
        self.param = param
        self._private_attr = None
    
    @property
    def public_property(self) -> str:
        """Public property with type hints."""
        return self._private_attr
    
    def public_method(self, arg: int) -> bool:
        """Public method with clear documentation."""
        return self._private_method(arg)
    
    def _private_method(self, arg: int) -> bool:
        """Private method for internal use."""
        return arg > 0
```

### Error Handling Standards

```python
def robust_operation(data: dict) -> tuple[bool, str]:
    """Standard error handling pattern."""
    try:
        # Main operation logic
        result = process_data(data)
        return True, result
        
    except ValidationError as e:
        # Specific exception handling
        return False, f"Validation failed: {e}"
        
    except Exception as e:
        # General exception handling
        logging.error(f"Unexpected error: {e}")
        return False, "An unexpected error occurred"
```

---

## Debugging and Troubleshooting

### Common Issues and Solutions

#### 1. Expression Evaluation Errors

**Problem**: Mathematical expressions not evaluating correctly
**Solution**: Check SecureMathEvaluator implementation
```python
# Debug expression evaluation
evaluator = SecureMathEvaluator()
try:
    result = evaluator.evaluate("np.log2(x)", {"x": 4})
    print(f"Result: {result}")  # Should be 2.0
except Exception as e:
    print(f"Error: {e}")
```

#### 2. Algorithm Configuration Issues

**Problem**: Algorithm fails to initialize
**Solution**: Validate configuration parameters
```python
# Debug algorithm configuration
config_validator = AlgorithmManager()
is_valid, errors = config_validator.validate_config(algorithm_config)
if not is_valid:
    print(f"Configuration errors: {errors}")
```

#### 3. UI Responsiveness Issues

**Problem**: Interface freezes during optimization
**Solution**: Ensure proper threading
```python
# Use QTimer for UI updates
from PyQt6.QtCore import QTimer

def update_progress(self):
    # Update UI elements
    self.progress_bar.setValue(self.current_progress)
    QTimer.singleShot(100, self.update_progress)  # Non-blocking update
```

### Debugging Tools

**Enable Debug Logging:**
```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# In your code
logger = logging.getLogger(__name__)
logger.debug("Debug information here")
```

**Performance Profiling:**
```python
import cProfile
import pstats

def profile_optimization():
    profiler = cProfile.Profile()
    profiler.enable()
    
    # Your optimization code here
    result = optimizer.optimize(problem, algorithm)
    
    profiler.disable()
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative').print_stats(10)
```

### Development Console

**Interactive Debugging:**
```python
# Add breakpoints in code
import pdb; pdb.set_trace()

# Or use ipdb for better experience
import ipdb; ipdb.set_trace()
```

---

## Contributing Guidelines

### Code Contribution Process

1. **Fork the Repository**
2. **Create Feature Branch**: `git checkout -b feature/your-feature`
3. **Write Tests**: Ensure new code is tested
4. **Follow Style Guide**: Use Black formatter and Pylint
5. **Update Documentation**: Add docstrings and update guides
6. **Submit Pull Request**: Include description and test results

### Contribution Areas

**High Priority:**
- 🔧 Algorithm implementations
- 🔒 Security enhancements
- 📊 Visualization improvements
- 🧪 Test coverage expansion

**Medium Priority:**
- 📚 Documentation improvements
- 🎨 UI/UX enhancements
- ⚡ Performance optimizations
- 🌐 Internationalization

**Low Priority:**
- 🎯 Feature requests
- 🔌 Plugin architecture
- 📱 Mobile responsive design
- ☁️ Cloud integration

### Code Review Checklist

**For Reviewers:**
- [ ] Code follows style guidelines
- [ ] Security best practices followed
- [ ] Tests included and passing
- [ ] Documentation updated
- [ ] No breaking changes (or properly documented)
- [ ] Performance impact considered

**For Contributors:**
- [ ] Self-review completed
- [ ] Tests written and passing
- [ ] Documentation updated
- [ ] Security implications considered
- [ ] Backward compatibility maintained
- [ ] Performance impact minimal

---

## API Reference

### Core Classes

#### ProblemManager

```python
class ProblemManager:
    """Manages optimization problem definitions and validation."""
    
    def create_problem(self, problem_data: dict) -> Problem:
        """Create PyMOO problem from data dictionary."""
        
    def validate_problem(self, problem_data: dict) -> tuple[bool, list[str]]:
        """Validate problem definition."""
        
    def load_problem(self, file_path: str) -> dict:
        """Load problem from JSON file."""
        
    def save_problem(self, problem_data: dict, file_path: str) -> bool:
        """Save problem to JSON file."""
```

#### AlgorithmManager

```python
class AlgorithmManager:
    """Manages algorithm configuration and instantiation."""
    
    def get_supported_algorithms(self) -> list[str]:
        """Get list of supported algorithms."""
        
    def create_algorithm(self, config: dict, problem: Problem) -> Algorithm:
        """Create algorithm instance with configuration."""
        
    def validate_config(self, config: dict) -> tuple[bool, list[str]]:
        """Validate algorithm configuration."""
        
    def get_default_config(self, algorithm_name: str) -> dict:
        """Get default configuration for algorithm."""
```

#### Optimizer

```python
class Optimizer:
    """Executes optimization and manages results."""
    
    def optimize(self, problem: Problem, algorithm: Algorithm, 
                callback: callable = None, verbose: bool = False) -> Result:
        """Run optimization with progress tracking."""
        
    def get_pareto_front(self, result: Result) -> np.ndarray:
        """Extract Pareto front from results."""
        
    def export_results(self, result: Result, file_path: str, 
                      format: str = "excel") -> bool:
        """Export results to file."""
```

### UI Components

#### MainWindow

```python
class MainWindow(QMainWindow):
    """Main application window."""
    
    def load_problem_file(self, file_path: str) -> bool:
        """Load problem from file."""
        
    def save_problem_file(self, file_path: str) -> bool:
        """Save current problem to file."""
        
    def run_optimization(self) -> bool:
        """Execute optimization with current settings."""
```

### Utility Functions

```python
# validators.py
def validate_expression(expression: str) -> tuple[bool, str]:
    """Validate mathematical expression syntax."""

def validate_numeric_input(value: str, min_val: float = None, 
                          max_val: float = None) -> tuple[bool, str]:
    """Validate numeric input with optional bounds."""

# helpers.py
def format_number(value: float, precision: int = 4) -> str:
    """Format number for display."""

def generate_reference_directions(n_obj: int, n_points: int) -> np.ndarray:
    """Generate reference directions for many-objective optimization."""
```

---

## Advanced Topics

### 1. Custom Algorithm Integration

**Adding a New Algorithm:**

1. **Create Algorithm Class:**
```python
from pymoo.algorithms.base.genetic import GeneticAlgorithm

class CustomAlgorithm(GeneticAlgorithm):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Custom initialization
    
    def _next(self):
        # Custom algorithm logic
        pass
```

2. **Register in AlgorithmManager:**
```python
def get_supported_algorithms(self):
    return {
        # ... existing algorithms
        "CUSTOM": {
            "name": "Custom Algorithm",
            "class": CustomAlgorithm,
            "parameters": ["param1", "param2"]
        }
    }
```

3. **Add UI Configuration:**
```python
# In algorithm_tab.py
def setup_custom_config(self):
    """Setup configuration UI for custom algorithm."""
    # Add parameter input widgets
    pass
```

### 2. Custom Problem Types

**Creating Domain-Specific Problems:**

```python
from pymoo.core.problem import ElementwiseProblem

class CustomEngineeringProblem(ElementwiseProblem):
    def __init__(self):
        super().__init__(n_var=3, n_obj=2, n_constr=1,
                         xl=[0, 0, 0], xu=[10, 10, 10])
    
    def _evaluate(self, x, out, *args, **kwargs):
        # Custom evaluation logic
        f1 = x[0]**2 + x[1]**2
        f2 = (x[0] - 1)**2 + x[1]**2
        g1 = x[0] + x[1] - x[2]
        
        out["F"] = [f1, f2]
        out["G"] = [g1]
```

### 3. Advanced Visualization

**Custom Plot Types:**

```python
def create_custom_plot(results):
    """Create domain-specific visualization."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    # Custom plot 1
    ax1.scatter(results.F[:, 0], results.F[:, 1])
    ax1.set_title("Objective Space")
    
    # Custom plot 2 - parallel coordinates
    parallel_coordinates_plot(results.X, ax2)
    ax2.set_title("Decision Space")
    
    return fig
```

### 4. Performance Optimization

**Vectorized Evaluation:**

```python
class VectorizedProblem(Problem):
    def _evaluate(self, X, out, *args, **kwargs):
        # Vectorized operations for better performance
        F = np.column_stack([
            np.sum(X**2, axis=1),  # f1
            np.sum((X - 1)**2, axis=1)  # f2
        ])
        out["F"] = F
```

### 5. Plugin Architecture (Future Enhancement)

**Plugin Interface Design:**

```python
from abc import ABC, abstractmethod

class OptimizationPlugin(ABC):
    @abstractmethod
    def get_name(self) -> str:
        """Return plugin name."""
        
    @abstractmethod
    def get_algorithms(self) -> dict:
        """Return supported algorithms."""
        
    @abstractmethod
    def create_algorithm(self, config: dict) -> Algorithm:
        """Create algorithm instance."""

# Plugin registration
class PluginManager:
    def __init__(self):
        self.plugins = {}
    
    def register_plugin(self, plugin: OptimizationPlugin):
        self.plugins[plugin.get_name()] = plugin
```

---

## Version History and Migration

### Version 1.3.2 (Current) - September 2025
- ✅ Security overhaul with AST-based evaluation
- ✅ Numpy compatibility restoration
- ✅ Comprehensive benchmark suite (37 problems)
- ✅ Workspace cleanup and optimization
- ✅ Production-ready status achieved

### Migration Guidelines

**From Version 1.2.x to 1.3.2:**
1. **Security Changes**: All `eval()` calls replaced with `SecureMathEvaluator`
2. **API Changes**: `ProblemManager.evaluate_expression()` signature updated
3. **Configuration**: New security settings in evaluator
4. **Dependencies**: No new dependencies required

---

## Support and Resources

### Getting Help

1. **GitHub Issues**: Report bugs and feature requests
2. **Documentation**: Comprehensive guides and API reference
3. **Code Examples**: 37 benchmark problems for reference
4. **Developer Community**: Contribute to open-source development

### Additional Resources

- **PyMOO Documentation**: [Official PyMOO Docs](https://pymoo.org/)
- **PyQt6 Guide**: [Qt for Python Documentation](https://doc.qt.io/qtforpython/)
- **Multi-Objective Optimization**: Academic papers and textbooks
- **Python Security**: OWASP Python Security Guidelines

---

**Developer Guide Version**: 1.3.2  
**Last Updated**: September 3, 2025  
**Maintained by**: Elias Rizos [it21490]  
**License**: MIT (Development contributions welcome)

---

*This developer guide is living documentation that evolves with the project. For the most up-to-date information, check the project repository and recent commits.*
