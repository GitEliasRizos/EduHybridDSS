# PyMOO GUI Architecture Documentation

## Overview

PyMOO GUI is a comprehensive graphical interface for multi-objective optimization using the PyMOO framework. The application follows a modular, layered architecture with clear separation of concerns between UI components, core functionality, and utilities.

## Architecture Principles

- **Separation of Concerns**: Clear distinction between UI, business logic, and data management
- **Modular Design**: Independent components that can be modified without affecting others
- **Security-First**: AST-based expression evaluation to prevent code injection
- **Extensibility**: Plugin-like architecture for algorithms and problem types
- **Type Safety**: Comprehensive input validation and error handling

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    PyMOO GUI Application                    │
├─────────────────────────────────────────────────────────────┤
│  UI Layer (PyQt6)                                          │
│  ├── MainWindow (main_window.py)                           │
│  ├── ProblemTab (problem_tab.py)                           │
│  ├── AlgorithmTab (algorithm_tab.py)                       │
│  ├── ResultsTab (results_tab.py)                           │
│  └── MCDATab (mcda_tab.py)                                 │
├─────────────────────────────────────────────────────────────┤
│  Core Logic Layer                                          │
│  ├── ProblemManager (problem_manager.py)                   │
│  ├── AlgorithmManager (algorithm_manager.py)               │
│  ├── Optimizer (optimizer.py)                              │
│  └── MCDA (mcda.py)                                        │
├─────────────────────────────────────────────────────────────┤
│  Utilities Layer                                           │
│  ├── Validators (validators.py)                            │
│  └── Helpers (helpers.py)                                  │
├─────────────────────────────────────────────────────────────┤
│  Data Layer                                                │
│  ├── JSON Problem Definitions                              │
│  ├── Algorithm Configurations                              │
│  └── Results Export                                        │
└─────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. Main Application (`main.py`)

**Purpose**: Application entry point and initialization
- Configures PyQt6 application settings
- Sets application metadata (name, version, organization)
- Initializes and displays the main window
- Manages the Qt event loop

### 2. UI Layer (`ui/` directory)

#### MainWindow (`main_window.py`)
- **Role**: Central application coordinator
- **Responsibilities**: 
  - Tab management and navigation
  - Menu bar and toolbar setup
  - File operations (load/save problems)
  - Window state management
- **Key Features**:
  - Tabbed interface for different workflow stages
  - Menu-driven operations
  - Status bar for user feedback

#### ProblemTab (`problem_tab.py`)
- **Role**: Problem definition interface
- **Responsibilities**:
  - Variable configuration (bounds, types, names)
  - Objective function definition
  - Constraint specification
  - Problem validation
- **Key Features**:
  - Dynamic form generation
  - Real-time expression validation
  - Import/export problem definitions

#### AlgorithmTab (`algorithm_tab.py`)
- **Role**: Algorithm selection and configuration
- **Responsibilities**:
  - Algorithm selection (NSGA-II, NSGA-III, SPEA2, etc.)
  - Parameter configuration
  - Crossover/mutation operator setup
  - Reference directions for many-objective problems
- **Supported Algorithms**:
  - NSGA-II (Non-dominated Sorting Genetic Algorithm II)
  - NSGA-III (Non-dominated Sorting Genetic Algorithm III)
  - SPEA2 (Strength Pareto Evolutionary Algorithm 2)
  - MOEA/D (Multi-Objective Evolutionary Algorithm based on Decomposition)
  - RVEA (Reference Vector Guided Evolutionary Algorithm)
  - IBEA (Indicator-Based Evolutionary Algorithm)
  - SMS-EMOA (S-Metric Selection Evolutionary Multi-Objective Algorithm)
  - GDE3 (Generalized Differential Evolution 3)
  - CTAEA (Constrained Two-Archive Evolutionary Algorithm)

#### ResultsTab (`results_tab.py`)
- **Role**: Results visualization and analysis
- **Responsibilities**:
  - Solution visualization (scatter plots, parallel coordinates)
  - Statistical analysis
  - Export functionality
  - Interactive result exploration
- **Key Features**:
  - Multiple visualization types
  - Export to Excel/CSV
  - Pareto front analysis

#### MCDATab (`mcda_tab.py`)
- **Role**: Multi-Criteria Decision Analysis
- **Responsibilities**:
  - Decision maker preference integration
  - Solution ranking and selection
  - Trade-off analysis
  - Final recommendation generation

### 3. Core Logic Layer (`core/` directory)

#### ProblemManager (`problem_manager.py`)
- **Role**: Problem definition and management
- **Key Features**:
  - **SecureMathEvaluator**: AST-based expression evaluation for security
  - **numpy Integration**: Full support for mathematical functions (np.sin, np.log2, etc.)
  - **Validation**: Comprehensive input validation
  - **JSON I/O**: Load/save problem configurations
- **Security Features**:
  - Blocks file system access
  - Prevents system command execution
  - Allows only mathematical operations
  - AST-based parsing instead of eval()

#### AlgorithmManager (`algorithm_manager.py`)
- **Role**: Algorithm configuration and instantiation
- **Responsibilities**:
  - Algorithm parameter validation
  - Factory pattern for algorithm creation
  - Default configuration management
  - Algorithm-specific optimization

#### Optimizer (`optimizer.py`)
- **Role**: Optimization execution and coordination
- **Responsibilities**:
  - Problem-algorithm integration
  - Optimization process management
  - Progress tracking and callbacks
  - Result collection and formatting

#### MCDA (`mcda.py`)
- **Role**: Multi-Criteria Decision Analysis implementation
- **Methods Supported**:
  - TOPSIS (Technique for Order Preference by Similarity to Ideal Solution)
  - Weighted Sum Method
  - ELECTRE (Elimination and Choice Translating Reality)
  - AHP-based approaches

### 4. Utilities Layer (`utils/` directory)

#### Validators (`validators.py`)
- **Purpose**: Input validation and sanitization
- **Functions**:
  - Expression syntax validation
  - Numerical range checking
  - Type conversion and verification
  - Error message generation

#### Helpers (`helpers.py`)
- **Purpose**: Common utility functions
- **Functions**:
  - File I/O operations
  - Data format conversions
  - Mathematical utilities
  - String processing

## Data Flow Architecture

### 1. Problem Definition Flow
```
User Input → ProblemTab → ProblemManager → SecureMathEvaluator → Validation → Storage
```

### 2. Optimization Flow
```
Problem Definition → AlgorithmManager → Optimizer → PyMOO → Results → ResultsTab
```

### 3. Decision Analysis Flow
```
Optimization Results → MCDATab → MCDA → Ranked Solutions → Recommendations
```

## Security Architecture

### AST-Based Expression Evaluation

The application implements a custom `SecureMathEvaluator` class that uses Abstract Syntax Tree (AST) parsing instead of dangerous `eval()` calls:

```python
class SecureMathEvaluator:
    def __init__(self):
        self.allowed_names = {
            # Mathematical functions
            'sin', 'cos', 'tan', 'exp', 'log', 'sqrt', 'abs',
            # Numpy functions
            'np': numpy_module,
            # Mathematical constants
            'pi', 'e'
        }
    
    def evaluate(self, expression, variables):
        # Parse expression into AST
        # Validate only allowed operations
        # Execute safely without eval()
```

### Security Features

1. **Code Injection Prevention**: No `eval()` or `exec()` usage
2. **File System Protection**: No file access from expressions
3. **Command Execution Prevention**: No system command execution
4. **Namespace Isolation**: Controlled variable and function access
5. **Input Sanitization**: Comprehensive validation of all user inputs

## Design Patterns

### 1. Model-View-Controller (MVC)
- **Model**: Core logic (ProblemManager, AlgorithmManager)
- **View**: UI components (all Tab classes)
- **Controller**: MainWindow coordinates between model and view

### 2. Factory Pattern
- **AlgorithmManager** acts as a factory for creating algorithm instances
- **ProblemManager** factory methods for different problem types

### 3. Observer Pattern
- **Progress callbacks** for optimization status updates
- **Event-driven UI updates** for real-time feedback

### 4. Strategy Pattern
- **Algorithm selection** allows runtime strategy switching
- **Visualization strategies** for different plot types

## Extensibility Points

### Adding New Algorithms

1. Extend `AlgorithmManager.get_supported_algorithms()`
2. Add algorithm-specific parameter configuration in `AlgorithmTab`
3. Implement algorithm factory method in `AlgorithmManager.create_algorithm()`

### Adding New Problem Types

1. Create new JSON schema for problem definition
2. Extend `ProblemManager` validation methods
3. Add UI components in `ProblemTab` if needed

### Adding New Visualizations

1. Extend `ResultsTab` with new plot types
2. Add visualization logic to `Optimizer` result processing
3. Implement new chart types using matplotlib

### Adding New MCDA Methods

1. Implement new methods in `mcda.py`
2. Add UI controls in `MCDATab`
3. Integrate with results processing pipeline

## Performance Considerations

### 1. Optimization Performance
- **Vectorized Operations**: Numpy-based calculations for efficiency
- **Memory Management**: Careful handling of large result sets
- **Progress Tracking**: Non-blocking UI updates during optimization

### 2. UI Responsiveness
- **Threading**: Long-running optimizations don't block UI
- **Progressive Loading**: Large datasets loaded incrementally
- **Lazy Evaluation**: UI elements created on-demand

### 3. Memory Usage
- **Result Caching**: Intelligent caching of optimization results
- **Data Structures**: Efficient storage of Pareto solutions
- **Cleanup**: Proper resource disposal and garbage collection

## Configuration Management

### 1. Problem Configurations
- **JSON Format**: Human-readable problem definitions
- **Schema Validation**: Ensures configuration integrity
- **Version Compatibility**: Handles different configuration versions

### 2. Application Settings
- **User Preferences**: Window states, default parameters
- **Algorithm Defaults**: Standard configurations for each algorithm
- **Export Preferences**: Default file formats and locations

## Error Handling Strategy

### 1. Input Validation
- **Pre-validation**: Check inputs before processing
- **User Feedback**: Clear error messages and suggestions
- **Recovery**: Graceful handling of invalid inputs

### 2. Runtime Errors
- **Exception Handling**: Comprehensive try-catch blocks
- **Logging**: Detailed error logging for debugging
- **User Notification**: Informative error dialogs

### 3. Optimization Failures
- **Convergence Issues**: Detect and handle non-convergent problems
- **Resource Limits**: Handle memory and time constraints
- **Algorithm Failures**: Fallback strategies for failed optimizations

## Testing Architecture

### 1. Unit Testing
- **Component Tests**: Individual class testing
- **Mock Objects**: Isolated testing with mocks
- **Edge Cases**: Boundary condition testing

### 2. Integration Testing
- **Workflow Tests**: End-to-end process testing
- **UI Testing**: Automated UI interaction testing
- **Algorithm Tests**: Optimization result validation

### 3. Security Testing
- **Expression Evaluation**: Test AST evaluator security
- **Input Sanitization**: Validate all security measures
- **Penetration Testing**: Attempt code injection attacks

## Future Architecture Enhancements

### 1. Plugin System
- **Algorithm Plugins**: Third-party algorithm integration
- **Visualization Plugins**: Custom chart types
- **Problem Type Plugins**: Domain-specific problems

### 2. Distributed Computing
- **Cluster Integration**: Support for distributed optimization
- **Cloud Computing**: Integration with cloud platforms
- **Parallel Processing**: Multi-core optimization support

### 3. Database Integration
- **Result Storage**: Persistent optimization history
- **Problem Libraries**: Centralized problem repositories
- **Collaboration**: Multi-user problem sharing

---

**Version**: 1.3.2  
**Last Updated**: September 3, 2025  
**Maintainer**: Elias Rizos [it21490]
