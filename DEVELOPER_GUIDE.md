"""
PyMOO GUI - Developer Guide

This guide provides comprehensive information for developers working on the
PyMOO GUI project, including coding standards, development workflows, and
contribution guidelines.

## 📋 Table of Contents

1. [Development Setup](#development-setup)
2. [Coding Standards](#coding-standards)  
3. [Project Structure](#project-structure)
4. [Development Workflow](#development-workflow)
5. [Testing Guidelines](#testing-guidelines)
6. [Contributing](#contributing)

## 🛠 Development Setup

### Prerequisites
```bash
# Python 3.8+ required
python --version

# Install dependencies
pip install -r requirements.txt

# Development dependencies
pip install pytest pytest-qt black flake8 mypy
```

### Development Environment
```bash
# Clone repository
git clone https://github.com/your-username/pymoo-gui.git
cd pymoo-gui

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate

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
├── ARCHITECTURE.md        # Architecture overview
├── DEVELOPER_GUIDE.md     # This file
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

## 🧪 Testing Guidelines

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
