"""
PyMOO GUI - Developer Guide

This guide provides comprehensive information for developers working on the
PyMOO GUI project, including coding standards, development workflows, and
contribution guidelines. Special attention is given to MCDA module development
and mathematical implementation patterns.

## 📋 Table of Contents

1. [Development Setup](#development-setup)
2. [Coding Standards](#coding-standards)  
3. [Project Structure](#project-structure)
4. [Development Workflow](#development-workflow)
5. [MCDA Development](#mcda-development)
6. [Testing Guidelines](#testing-guidelines)
7. [Contributing](#contributing)

## 🛠 Development Setup

### Prerequisites
```bash
# Python 3.8+ required
python --version

# Install dependencies
pip install -r requirements.txt

# Development dependencies (optional but recommended)
pip install pytest pytest-qt black flake8 mypy
```

### Development Environment
```bash
# Clone repository
git clone https://github.com/your-username/pymoo-gui.git
cd pymoo-gui

# Create virtual environment
python -m venv venv
# On Windows: venv\\Scripts\\activate
# On Unix/MacOS: source venv/bin/activate

# Install in development mode
pip install -e .

# Run application
python main.py
```

### IDE Configuration

#### VS Code
```json
{
  "python.defaultInterpreter": "./venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": true,
  "python.formatting.provider": "black",
  "python.testing.pytestEnabled": true,
  "files.associations": {
    "*.py": "python"
  }
}
```

#### PyCharm
- Set Python interpreter to virtual environment
- Enable type checking with mypy
- Configure code style to Black
- Set up pytest as test runner

## 📝 Coding Standards

### Python Style Guide
We follow **PEP 8** with some project-specific adaptations:

#### Code Formatting
```python
# Use Black for automatic formatting
black --line-length 100 .

# Configuration in pyproject.toml
[tool.black]
line-length = 100
target-version = ['py38']
```

#### Import Organization
```python
"""Module docstring describing purpose and key features."""

# Standard library imports
import sys
import os
from typing import Dict, List, Optional, Any

# Third-party imports
import numpy as np
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from pymoo.algorithms.moo.nsga2 import NSGA2

# Local imports
from core.problem_manager import ProblemManager
from utils.validators import ProblemValidator
```

#### Type Hints
```python
def create_problem_from_config(self, config: Dict[str, Any]) -> Problem:
    """
    Create PyMOO problem from configuration.
    
    Args:
        config: Problem configuration dictionary containing variables,
                objectives, and constraints definitions.
    
    Returns:
        Problem: Configured PyMOO problem instance ready for optimization.
        
    Raises:
        ValidationError: If configuration is invalid or incomplete.
        ValueError: If variable bounds or types are inconsistent.
    """
    pass
```

#### Documentation Standards
```python
class ProblemManager:
    """
    Manages optimization problem definitions and configurations.
    
    This class serves as the bridge between GUI problem configurations
    and PyMOO problem instances. It handles variable type conversion,
    objective function evaluation, and constraint enforcement.
    
    Key Features:
    - Support for mixed variable types (Real, Integer, Binary)
    - Custom objective function evaluation with numpy support
    - Expression validation and security checks
    - Repair mechanisms for discrete variables
    
    Attributes:
        current_problem: Active PyMOO problem instance
        problem_config: Current problem configuration dictionary
        
    Example:
        >>> manager = ProblemManager()
        >>> config = {
        ...     'variables': [{'name': 'x1', 'type': 'Real', ...}],
        ...     'objectives': [{'name': 'f1', 'function': 'x1**2', ...}]
        ... }
        >>> problem = manager.create_problem_from_config(config)
    """
```

### Qt/PyQt Guidelines

#### Signal-Slot Connections
```python
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self._init_ui()
        self._connect_signals()
    
    def _connect_signals(self):
        """Connect all signal-slot pairs for component communication."""
        # Use descriptive connection comments
        self.problem_tab.problem_changed.connect(self._on_problem_changed)
        self.results_tab.optimization_completed.connect(self._on_optimization_completed)
        
        # Connect with lambda for parameters
        self.algorithm_tab.algorithm_changed.connect(
            lambda: self._validate_problem_algorithm_compatibility()
        )
```

#### Widget Organization
```python
def _init_ui(self):
    """Initialize user interface with logical component grouping."""
    # Main layout
    layout = QVBoxLayout(self)
    
    # Create component groups
    self._create_problem_section(layout)
    self._create_algorithm_section(layout)
    self._create_results_section(layout)
    
    # Apply consistent styling
    self._apply_styling()
```

#### Threading Best Practices
```python
class OptimizationWorker(QThread):
    """Worker thread for non-blocking optimization execution."""
    
    # Define signals at class level
    progress_update = pyqtSignal(int, str)
    results_ready = pyqtSignal(object)
    error_occurred = pyqtSignal(str)
    
    def run(self):
        """Execute optimization with proper error handling."""
        try:
            # Emit progress updates
            self.progress_update.emit(10, "Initializing...")
            
            # Actual work here
            result = self._run_optimization()
            
            # Emit results
            self.results_ready.emit(result)
            
        except Exception as e:
            # Always handle exceptions in worker threads
            self.error_occurred.emit(str(e))
```

## 🏗 Project Structure

### Directory Organization
```
pymoo-gui/
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
├── README.md              # Project documentation
│
├── docs/                  # Documentation files
│   ├── ARCHITECTURE.md    # Architecture overview
│   ├── DEVELOPER_GUIDE.md # This file
│   ├── PASSWORD_MANAGEMENT.md # Password management guide
│   └── PROJECT_STATUS.md  # Project status and roadmap
│
├── databases/             # Database files
│   └── pymoo.db          # Main application database
│
├── ui/                    # User interface components
│   ├── __init__.py
│   ├── main_window.py     # Main application window
│   ├── problem_tab.py     # Problem definition interface
│   ├── algorithm_tab.py   # Algorithm configuration interface
│   └── results_tab.py     # Results and visualization
│
├── core/                  # Business logic
│   ├── __init__.py
│   ├── problem_manager.py # Problem definition and creation
│   ├── algorithm_manager.py # Algorithm configuration
│   └── optimizer.py       # Optimization execution
│
├── utils/                 # Utility functions
│   ├── __init__.py
│   ├── validators.py      # Input validation
│   └── helpers.py         # Common utilities
│
├── examples/              # Example problems
│   ├── __init__.py
│   ├── basic_problems.json
│   └── advanced_problems.json
│
├── tests/                 # Test suite
│   ├── __init__.py
│   ├── test_problem_manager.py
│   ├── test_algorithm_manager.py
│   ├── test_validators.py
│   └── test_ui/           # UI-specific tests
│
└── docs/                  # Additional documentation
    ├── user_guide.md
    ├── api_reference.md
    └── deployment.md
```

### Module Responsibilities

#### `ui/` - User Interface Layer
- **Purpose**: PyQt6-based graphical interface
- **Dependencies**: Can depend on `core/` and `utils/`
- **Restrictions**: No direct PyMOO imports (use core layer)

#### `core/` - Business Logic Layer  
- **Purpose**: Optimization logic and PyMOO integration
- **Dependencies**: Can depend on `utils/`, PyMOO
- **Restrictions**: No PyQt6 imports (except for threading)

#### `utils/` - Utility Layer
- **Purpose**: Common functionality and helpers
- **Dependencies**: Minimal external dependencies
- **Restrictions**: No application-specific logic

## 🔄 Development Workflow

### Git Workflow
We use **Git Flow** with the following branch structure:

```bash
# Main branches
main        # Production-ready code
develop     # Integration branch for development

# Supporting branches
feature/*   # New features
bugfix/*    # Bug fixes
hotfix/*    # Critical production fixes
release/*   # Release preparation
```

### Feature Development
```bash
# Start new feature
git checkout develop
git pull origin develop
git checkout -b feature/new-algorithm-support

# Make changes with good commit messages
git add .
git commit -m "feat: add MOEA/D algorithm support

- Implement MOEA/D algorithm configuration
- Add reference direction generation for decomposition
- Update algorithm selection UI
- Add comprehensive tests for new algorithm

Closes #123"

# Push and create pull request
git push origin feature/new-algorithm-support
```

### Commit Message Format
```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types**: feat, fix, docs, style, refactor, test, chore
**Scopes**: ui, core, utils, tests, docs
**Examples**:
- `feat(core): add integer variable constraint enforcement`
- `fix(ui): resolve table sorting issue in results tab`
- `docs(readme): update installation instructions`

### Code Review Process
1. **Self Review**: Review your own code before submitting
2. **Automated Checks**: Ensure all CI checks pass
3. **Peer Review**: At least one approval required
4. **Testing**: All tests must pass
5. **Documentation**: Update docs for user-facing changes

## � MCDA Development

The Multi-Criteria Decision Analysis (MCDA) module is a critical component requiring careful attention to mathematical rigor, numerical stability, and user experience. This section provides comprehensive guidance for MCDA development.

### Mathematical Implementation Standards

#### Eigenvalue Decomposition (AHP)
```python
def calculate_weights(self, comparison_matrix: np.ndarray) -> Tuple[np.ndarray, float]:
    """
    Calculate criteria weights using principal eigenvalue method.
    
    Implementation follows Saaty (1980) methodology with robust handling
    of numerical precision issues and complex eigenvalues.
    
    Mathematical Foundation:
    - Principal eigenvalue: A * w = λ_max * w
    - Consistency Ratio: CR = (λ_max - n) / ((n-1) * RI)
    
    Args:
        comparison_matrix: n×n pairwise comparison matrix following Saaty scale
        
    Returns:
        tuple: (normalized_weights, consistency_ratio)
        
    Raises:
        ValueError: If matrix is not square or contains invalid values
        
    References:
        Saaty, T. L. (1980). The Analytic Hierarchy Process. McGraw-Hill.
    """
    # Validate input matrix
    if not self._validate_comparison_matrix(comparison_matrix):
        raise ValueError("Invalid comparison matrix format")
    
    # Calculate eigenvalues and eigenvectors
    eigenvalues, eigenvectors = np.linalg.eig(comparison_matrix)
    
    # Find principal eigenvalue (largest real eigenvalue)
    max_eigenvalue_idx = np.argmax(np.real(eigenvalues))
    principal_eigenvalue = np.real(eigenvalues[max_eigenvalue_idx])
    principal_eigenvector = np.real(eigenvectors[:, max_eigenvalue_idx])
    
    # Handle potential negative weights from numerical precision
    principal_eigenvector = np.abs(principal_eigenvector)
    
    # Normalize weights to sum to 1
    weights = principal_eigenvector / np.sum(principal_eigenvector)
    
    # Calculate consistency ratio
    n = len(comparison_matrix)
    consistency_index = (principal_eigenvalue - n) / (n - 1)
    random_index = self._get_random_index(n)
    consistency_ratio = consistency_index / random_index if random_index > 0 else 0
    
    return weights, consistency_ratio
```

#### TOPSIS Implementation Pattern
```python
def analyze_with_topsis(
    self, 
    decision_matrix: np.ndarray, 
    weights: np.ndarray,
    objectives: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Perform TOPSIS analysis with comprehensive error handling.
    
    Implements vector normalization method following Hwang & Yoon (1981)
    with support for mixed objective directions (minimize/maximize).
    
    Mathematical Steps:
    1. Vector normalization: r_ij = x_ij / √(Σ x_kj²)
    2. Weighted normalized matrix: v_ij = w_j * r_ij  
    3. Ideal solutions: A⁺ = {max(v_ij)} for benefit, {min(v_ij)} for cost
    4. Distance calculations: D⁺ and D⁻ using Euclidean distance
    5. Closeness coefficient: C_i = D⁻ / (D⁺ + D⁻)
    
    Args:
        decision_matrix: m×n matrix of alternatives vs criteria
        weights: n-element weight vector from AHP or direct input
        objectives: List of objective configurations with directions
        
    Returns:
        Dict containing rankings, scores, and analysis details
    """
    # Input validation and preprocessing
    validated_matrix = self._validate_and_preprocess_matrix(decision_matrix)
    normalized_matrix = self._normalize_matrix(validated_matrix, method='vector')
    weighted_matrix = self._apply_weights(normalized_matrix, weights)
    
    # Calculate ideal solutions based on objective directions
    ideal_positive, ideal_negative = self._calculate_ideal_solutions(
        weighted_matrix, objectives
    )
    
    # Distance calculations with numerical stability checks
    distances_positive = self._calculate_distances(weighted_matrix, ideal_positive)
    distances_negative = self._calculate_distances(weighted_matrix, ideal_negative)
    
    # Closeness coefficients with division by zero protection
    closeness_coefficients = self._calculate_closeness_coefficients(
        distances_positive, distances_negative
    )
    
    return self._format_topsis_results(closeness_coefficients, decision_matrix)
```

### UI Component Development Patterns

#### Custom Widget Development (PairwiseComparisonWidget)
```python
class PairwiseComparisonWidget(QWidget):
    """
    Custom widget for AHP pairwise comparisons using Saaty scale.
    
    This widget demonstrates proper PyQt6 development patterns including:
    - Signal-slot communication
    - Custom layout management  
    - Data validation and consistency
    - User experience optimization
    """
    
    # Define signals at class level for proper Qt integration
    comparison_changed = pyqtSignal(int, int, float)  # row, col, value
    matrix_completed = pyqtSignal(np.ndarray)
    
    def __init__(self, criteria_names: List[str], parent=None):
        super().__init__(parent)
        self.criteria_names = criteria_names
        self.comparison_widgets = {}
        self._init_ui()
        self._connect_signals()
    
    def _init_ui(self):
        """Initialize UI with proper layout and styling."""
        layout = QGridLayout(self)
        
        # Create header labels
        for i, name in enumerate(self.criteria_names):
            label = QLabel(name)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(label, 0, i + 1)
            layout.addWidget(QLabel(name), i + 1, 0)
        
        # Create comparison dropdowns for upper triangle
        for i in range(len(self.criteria_names)):
            for j in range(i + 1, len(self.criteria_names)):
                combo = self._create_saaty_combo()
                layout.addWidget(combo, i + 1, j + 1)
                self.comparison_widgets[(i, j)] = combo
                
    def _create_saaty_combo(self) -> QComboBox:
        """Create standardized Saaty scale dropdown."""
        combo = QComboBox()
        
        # Saaty scale values with descriptive labels
        saaty_scale = [
            (1/9, "1/9 - Extremely Less Important"),
            (1/7, "1/7 - Very Strongly Less Important"), 
            (1/5, "1/5 - Strongly Less Important"),
            (1/3, "1/3 - Moderately Less Important"),
            (1, "1 - Equal Importance"),
            (3, "3 - Moderately More Important"),
            (5, "5 - Strongly More Important"),
            (7, "7 - Very Strongly More Important"),
            (9, "9 - Extremely More Important")
        ]
        
        for value, label in saaty_scale:
            combo.addItem(label, value)
            
        # Set default to equal importance
        combo.setCurrentIndex(4)  # Index for value 1
        
        # Connect to update handler
        combo.currentIndexChanged.connect(self._on_comparison_changed)
        
        return combo
```

### Debugging and Testing Patterns

#### MCDA-Specific Testing
```python
import pytest
import numpy as np
from core.mcda import AHPAnalyzer, TOPSISAnalyzer

class TestAHPAnalyzer:
    """Comprehensive test suite for AHP implementation."""
    
    @pytest.fixture
    def perfect_consistency_matrix(self):
        """3x3 matrix with perfect consistency for testing."""
        return np.array([
            [1.0, 3.0, 5.0],
            [1/3, 1.0, 5/3],
            [1/5, 3/5, 1.0]
        ])
    
    @pytest.fixture  
    def inconsistent_matrix(self):
        """Matrix with known inconsistency for testing tolerance."""
        return np.array([
            [1.0, 2.0, 8.0],
            [0.5, 1.0, 6.0], 
            [0.125, 1/6, 1.0]
        ])
    
    def test_weight_calculation_perfect_consistency(self, perfect_consistency_matrix):
        """Test weight calculation with perfectly consistent matrix."""
        analyzer = AHPAnalyzer()
        weights, cr = analyzer.calculate_weights(perfect_consistency_matrix)
        
        # Weights should sum to 1
        assert np.isclose(np.sum(weights), 1.0, atol=1e-10)
        
        # Consistency ratio should be very small for perfect consistency
        assert cr < 0.01, f"CR should be near zero, got {cr}"
        
        # Weights should be positive
        assert np.all(weights > 0), "All weights should be positive"
    
    def test_consistency_ratio_calculation(self, inconsistent_matrix):
        """Test consistency ratio calculation with inconsistent matrix."""
        analyzer = AHPAnalyzer()
        weights, cr = analyzer.calculate_weights(inconsistent_matrix)
        
        # CR should be above acceptable threshold (0.1)
        assert cr > 0.1, f"Expected high CR for inconsistent matrix, got {cr}"
        
    def test_eigenvalue_edge_cases(self):
        """Test handling of edge cases in eigenvalue computation."""
        analyzer = AHPAnalyzer()
        
        # Test with matrix having complex eigenvalues
        complex_matrix = np.array([
            [1.0, 2.0, 0.1],
            [0.5, 1.0, 0.2],
            [10.0, 5.0, 1.0]
        ])
        
        # Should not raise exception and return real weights
        weights, cr = analyzer.calculate_weights(complex_matrix)
        assert np.all(np.isreal(weights)), "Weights should be real numbers"
        assert np.isreal(cr), "Consistency ratio should be real"
```

#### Debugging Workflow for MCDA Issues

1. **Matrix Validation Issues**:
```python
def debug_comparison_matrix(self, matrix: np.ndarray):
    """Debug helper for comparison matrix issues."""
    print(f"Matrix shape: {matrix.shape}")
    print(f"Matrix dtype: {matrix.dtype}")
    print(f"Reciprocal check: {self._check_reciprocity(matrix)}")
    print(f"Eigenvalues: {np.linalg.eigvals(matrix)}")
    print(f"Condition number: {np.linalg.cond(matrix)}")
```

2. **Weight Calculation Debugging**:
```python
def debug_weight_calculation(self, comparison_matrix: np.ndarray):
    """Step-by-step debugging of weight calculation."""
    eigenvals, eigenvecs = np.linalg.eig(comparison_matrix)
    print(f"All eigenvalues: {eigenvals}")
    
    # Check for complex eigenvalues
    complex_mask = np.iscomplex(eigenvals)
    if np.any(complex_mask):
        print(f"Complex eigenvalues found: {eigenvals[complex_mask]}")
        
    # Principal eigenvalue analysis
    max_idx = np.argmax(np.real(eigenvals))
    principal_val = eigenvals[max_idx]
    principal_vec = eigenvecs[:, max_idx]
    
    print(f"Principal eigenvalue: {principal_val}")
    print(f"Principal eigenvector: {principal_vec}")
    print(f"Is principal eigenvector real: {np.all(np.isreal(principal_vec))}")
```

### Performance Optimization

#### Numerical Stability
```python
# Use appropriate tolerances for floating point comparisons
EIGENVALUE_TOLERANCE = 1e-10
WEIGHT_TOLERANCE = 1e-12

def _normalize_weights_stable(self, weights: np.ndarray) -> np.ndarray:
    """Numerically stable weight normalization."""
    # Handle potential negative weights from numerical precision
    weights = np.abs(weights)
    
    # Check for zero weights
    if np.sum(weights) < WEIGHT_TOLERANCE:
        raise ValueError("All weights are effectively zero")
        
    return weights / np.sum(weights)
```

#### Memory Management for Large Matrices
```python
def _process_large_decision_matrix(self, matrix: np.ndarray) -> np.ndarray:
    """Efficient processing of large decision matrices."""
    # Use numpy operations that minimize memory allocation
    if matrix.size > 10000:  # Threshold for large matrices
        # Process in chunks if necessary
        return self._chunked_normalization(matrix)
    else:
        return self._standard_normalization(matrix)
```

## �🧪 Testing Guidelines

### Test Structure
```python
# tests/test_problem_manager.py
import pytest
from unittest.mock import Mock, patch
from core.problem_manager import ProblemManager, ValidationError


class TestProblemManager:
    """Test suite for ProblemManager class."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.manager = ProblemManager()
        self.valid_config = {
            'name': 'Test Problem',
            'variables': [
                {'name': 'x1', 'type': 'Real', 'lower_bound': 0, 'upper_bound': 1}
            ],
            'objectives': [
                {'name': 'f1', 'function': 'x1**2', 'direction': 'Minimize', 'weight': 1.0}
            ],
            'constraints': []
        }
    
    def test_create_problem_valid_config(self):
        """Test problem creation with valid configuration."""
        problem = self.manager.create_problem_from_config(self.valid_config)
        
        assert problem is not None
        assert problem.n_var == 1
        assert problem.n_obj == 1
        assert problem.n_constr == 0
    
    def test_create_problem_invalid_config(self):
        """Test problem creation with invalid configuration."""
        invalid_config = {'name': 'Invalid'}  # Missing required fields
        
        with pytest.raises(ValidationError):
            self.manager.create_problem_from_config(invalid_config)
    
    @pytest.mark.parametrize("var_type,expected_type", [
        ('Real', 'real'),
        ('Integer', 'int'), 
        ('Binary', 'bool')
    ])
    def test_variable_type_mapping(self, var_type, expected_type):
        """Test variable type mapping from GUI to PyMOO."""
        config = self.valid_config.copy()
        config['variables'][0]['type'] = var_type
        
        problem = self.manager.create_problem_from_config(config)
        # Test implementation details as needed
```

### UI Testing
```python
# tests/test_ui/test_problem_tab.py
import pytest
from PyQt6.QtWidgets import QApplication
from PyQt6.QtTest import QTest
from PyQt6.QtCore import Qt
from ui.problem_tab import ProblemTab


@pytest.fixture
def app():
    """Create QApplication instance for testing."""
    return QApplication.instance() or QApplication([])


@pytest.fixture  
def problem_tab(app):
    """Create ProblemTab widget for testing."""
    return ProblemTab()


class TestProblemTab:
    """Test suite for ProblemTab UI component."""
    
    def test_initial_state(self, problem_tab):
        """Test initial widget state."""
        assert problem_tab.variables_table.rowCount() == 0
        assert problem_tab.objectives_table.rowCount() == 0
        assert problem_tab.constraints_table.rowCount() == 0
    
    def test_add_variable(self, problem_tab):
        """Test adding a new variable."""
        initial_count = problem_tab.variables_table.rowCount()
        
        # Simulate button click
        QTest.mouseClick(problem_tab.add_variable_btn, Qt.MouseButton.LeftButton)
        
        assert problem_tab.variables_table.rowCount() == initial_count + 1
    
    def test_problem_validation(self, problem_tab):
        """Test problem configuration validation."""
        # Add invalid configuration
        problem_tab.problem_name_edit.setText("")  # Empty name should be invalid
        
        config = problem_tab.get_problem_config()
        errors = problem_tab.validate_config(config)
        
        assert len(errors) > 0
        assert any("name" in error.lower() for error in errors)
```

### Test Categories

#### Unit Tests
- **Scope**: Individual functions and methods
- **Focus**: Business logic, calculations, data transformations
- **Isolation**: Mock external dependencies
- **Coverage**: Aim for >90% code coverage

#### Integration Tests  
- **Scope**: Component interactions
- **Focus**: Data flow between components
- **Dependencies**: Real implementations where possible
- **Coverage**: Critical user workflows

#### UI Tests
- **Scope**: User interface components
- **Focus**: User interactions and widget behavior
- **Tools**: pytest-qt for Qt testing
- **Coverage**: Key user workflows and error states

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_problem_manager.py

# Run tests with specific marker
pytest -m "not slow"

# Run UI tests (requires display)
pytest tests/test_ui/ --qt-tests
```

## 🤝 Contributing

### Getting Started
1. **Fork** the repository on GitHub
2. **Clone** your fork locally
3. **Create** a feature branch
4. **Make** your changes
5. **Test** your changes thoroughly
6. **Submit** a pull request

### Contribution Types

#### Bug Fixes
- Include clear reproduction steps
- Add regression tests
- Update documentation if needed
- Reference issue number in commit

#### New Features
- Discuss feature in issue before implementation
- Follow existing architecture patterns
- Include comprehensive tests
- Update user documentation
- Add example usage

#### Documentation
- Keep documentation up to date with code changes
- Include examples and use cases
- Follow documentation style guide
- Test documentation accuracy

### Code Quality Checklist
Before submitting a pull request, ensure:

- [ ] Code follows project style guidelines
- [ ] All tests pass locally
- [ ] New code has appropriate test coverage
- [ ] Documentation is updated for user-facing changes
- [ ] Commit messages follow convention
- [ ] No sensitive information in commits
- [ ] Performance impact considered
- [ ] Backwards compatibility maintained (or properly documented)

### Pull Request Process
1. **Describe** your changes clearly
2. **Link** related issues
3. **Include** testing instructions
4. **Request** specific reviewers if needed
5. **Address** review feedback promptly
6. **Squash** commits if requested

### Community Guidelines
- **Be Respectful**: Treat all contributors with respect
- **Be Constructive**: Provide helpful feedback and suggestions
- **Be Patient**: Reviews take time; be understanding
- **Be Collaborative**: Work together toward common goals

This developer guide ensures consistent, high-quality contributions to the
PyMOO GUI project. Following these guidelines helps maintain code quality,
facilitates collaboration, and makes the project more maintainable.
"""
