"""
PyMOO GUI - Architecture Documentation

This document provides a comprehensive overview of the PyMOO GUI architecture,
design patterns, and component interactions. It serves as a guide for developers
who want to understand, maintain, or extend the application.

## 📋 Table of Contents

1. [Architectural Overview](#architectural-overview)
2. [Design Patterns](#design-patterns)
3. [Component Architecture](#component-architecture)
4. [Data Flow](#data-flow)
5. [Threading Model](#threading-model)
6. [Extension Points](#extension-points)

## 🏗 Architectural Overview

The PyMOO GUI follows a **Model-View-Controller (MVC)** pattern with additional
separation of concerns for optimization-specific functionality and **multi-user group decision making**. The architecture is designed for:

- **Modularity**: Each component has clear responsibilities
- **Extensibility**: Easy addition of new algorithms, problems, or UI features  
- **Maintainability**: Clear separation between GUI and optimization logic
- **Testability**: Components can be tested independently
- **Performance**: Multi-threaded execution for responsive user experience
- **🆕 Scalability**: Multi-user group decision system with database persistence
- **🆕 Security**: Role-based authentication and session management

### High-Level Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Presentation  │    │    Business     │    
│   Decision      │    │      Data       │
│     Layer       │    │     Logic       │    
│    Layer        │    │     Layer       │
├─────────────────┤    ├─────────────────┤    ├─────────────────┤    ├─────────────────┤
│ • MainWindow    │◄──►│ • ProblemMgr    │◄──►
│ • AHPAnalyzer   │◄──►│ • Configuration │
│ • ProblemTab    │    │ • AlgorithmMgr  │    
│ • TOPSISAnalyzer│    │ • Results       │
│ • AlgorithmTab  │    │ • Optimizer     │    
│ • GroupDecision │    │ • User Database │
│ • ResultsTab    │    │ • Validators    │    
│ • SessionMgr    │    │ • Templates     │
│ • 🆕 MCDATab    │    │ • 🆕 UserMgr   │    
│ • 🆕 AuthSystem │    │ • 🆕 Sessions  │
│ • 🆕 UserUI     │    │                 │    │                 │    │ • Export Data   │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🎯 Design Patterns

### 1. Model-View-Controller (MVC)
- **Model**: Core logic classes (ProblemManager, AlgorithmManager, Optimizer)
- **View**: PyQt6 widgets (MainWindow, tabs, dialogs)  
- **Controller**: Signal-slot connections coordinating model and view updates

### 2. Observer Pattern
- Qt's signal-slot mechanism implements observer pattern
- Configuration changes trigger updates across components
- Real-time optimization progress updates

### 3. Strategy Pattern
- Algorithm selection and configuration
- Different optimization strategies (NSGA-II, NSGA-III, etc.)
- Operator selection (crossover, mutation)

### 4. Factory Pattern
- ProblemManager creates appropriate Problem instances
- AlgorithmManager creates configured algorithms
- Dynamic object creation based on configuration

### 5. Command Pattern
- Menu actions and toolbar commands
- Undo/redo functionality (future enhancement)
- Batch operations

## 🧩 Component Architecture

### Presentation Layer (`ui/`)

#### MainWindow
- **Purpose**: Application coordinator and main interface
- **Responsibilities**: 
  - Window management and layout
  - Menu and toolbar handling
  - Tab coordination
  - Signal routing between components
- **Key Features**:
  - Splitter-based resizable layout
  - Comprehensive menu system
  - Status bar with progress indication

#### ProblemTab  
- **Purpose**: Problem definition interface
- **Responsibilities**:
  - Variable specification (type, bounds, names)
  - Objective function definition with expression validation
  - Constraint specification and validation
  - Problem metadata management
- **Key Features**:
  - Table-based editing with real-time validation
  - Expression syntax highlighting
  - Import/export problem configurations

#### AlgorithmTab
- **Purpose**: Algorithm configuration interface  
- **Responsibilities**:
  - Algorithm selection and parameterization
  - Operator configuration (crossover, mutation)
  - Reference direction setup
  - Termination criteria specification
- **Key Features**:
  - Dynamic UI adaptation based on algorithm
  - Parameter validation and suggestions
  - Advanced options for expert users

### 6. MCDA Integration

#### MCDATab
- **Purpose**: Individual multi-criteria decision analysis interface for optimization results
- **Responsibilities**:
  - Criteria definition and weight configuration
  - AHP (Analytic Hierarchy Process) pairwise comparison interface with consistency checking
  - TOPSIS analysis configuration and execution
  - Results visualization and ranking display

#### 🆕 GroupDecisionTab
- **Purpose**: Administrative interface for group decision making sessions
- **Responsibilities**:
  - Session creation and management
  - User coordination and monitoring
  - Group analysis execution (AHP/TOPSIS aggregation)
  - Consensus results visualization and export

#### 🆕 UserInterface  
- **Purpose**: Simplified interface for regular users to provide decision input
- **Responsibilities**:
  - Session selection and context display
  - AHP pairwise comparison input with consistency validation
  - TOPSIS weight specification
  - Submission tracking and status updates
  - MCDA results visualization and interpretation
- **Key Features**:
  - Dropdown-based Saaty scale for AHP comparisons
  - Real-time consistency ratio monitoring
  - Multiple normalization methods for TOPSIS
  - Interactive results tables with sorting and ranking

#### MCDAManager (in `core/mcda.py`)
- **Purpose**: Individual and group multi-criteria decision analysis coordinator
- **Responsibilities**:
  - Integrate optimization results with MCDA methods
  - Coordinate individual AHP and TOPSIS analysis workflows
  - 🆕 Manage group decision aggregation processes
  - Process PyMOO results into MCDA-compatible format
- **Key Features**:
  - Seamless PyMOO integration for result processing
  - Support for both individual and group MCDA methodologies
  - Mathematical rigor with comprehensive academic documentation
  - 🆕 Group aggregation using geometric and arithmetic means

#### AHPAnalyzer
- **Purpose**: Individual and group Analytic Hierarchy Process implementation
- **Responsibilities**:
  - Process individual pairwise comparison matrices using Saaty's 1-9 scale
  - Calculate criteria weights using eigenvalue decomposition
  - 🆕 Validate consistency with real-time feedback before submission
  - 🆕 Aggregate multiple user matrices using geometric mean
- **Mathematical Foundation**:
  - Principal eigenvalue-based weight calculation following Saaty (1980)
  - Consistency ratio validation using Random Index methodology
  - 🆕 Pre-submission consistency checking prevents invalid data entry
  - Robust handling of complex eigenvalues with educational user feedback

#### TOPSISAnalyzer  
- **Purpose**: Individual and group TOPSIS implementation
- **Responsibilities**:
  - Implement vector and linear normalization methods for individual analysis
  - Calculate positive and negative ideal solutions
  - 🆕 Aggregate multiple user weight vectors using arithmetic mean
  - Handle both minimization and maximization criteria in group context
- **Mathematical Foundation**:
  - Multiple normalization approaches (Hwang & Yoon, 1981)
  - Euclidean distance-based similarity measurements
  - 🆕 Group weight aggregation maintaining normalization properties

#### 🆕 UserDatabaseManager (in `core/user_manager.py`)
- **Purpose**: Multi-user system database management and authentication
- **Responsibilities**:
  - User registration, authentication, and role management
  - Session creation and management for group decisions
  - AHP/TOPSIS submission storage and retrieval
  - Group analysis execution and result persistence
- **Key Features**:
  - SQLite database with automated schema migration
  - Secure password hashing and session management
  - Role-based access control (admin/user)
  - Comprehensive group decision data model
  - Robust handling of mixed objective directions
  - Professional implementation with comprehensive documentation

#### PairwiseComparisonWidget
- **Purpose**: Specialized UI component for AHP pairwise comparisons
- **Responsibilities**:
  - Provide intuitive dropdown interface for Saaty scale values
  - Maintain reciprocal consistency in comparison matrices
  - Real-time validation of comparison inputs
  - User-friendly presentation of pairwise comparison workflow
- **Key Features**:
  - QComboBox-based Saaty scale selection (1/9 to 9)
  - Automatic reciprocal value handling
  - Clear labeling with criteria names
  - Responsive layout for multiple criteria scenarios

### Business Logic Layer (`core/`)

#### ProblemManager
- **Purpose**: Problem definition and PyMOO integration
- **Responsibilities**:
  - Convert GUI configuration to PyMOO problems
  - Handle mixed variable types (Real, Integer, Binary)
  - Evaluate custom objective functions
  - Apply constraint functions
  - Variable type constraint enforcement
- **Key Features**:
  - Expression evaluation with numpy support
  - Security-conscious expression parsing
  - Repair mechanisms for discrete variables
  - Comprehensive error handling

#### AlgorithmManager  
- **Purpose**: Algorithm instantiation and configuration
- **Responsibilities**:
  - Create PyMOO algorithm instances from GUI config
  - Configure operators (crossover, mutation, selection)
  - Set up repair operators for mixed variables
  - Generate reference directions for many-objective algorithms
- **Key Features**:
  - Support for all major MOO algorithms
  - Automatic parameter validation
  - Intelligent default parameter selection
  - Repair operator integration

#### Optimizer
- **Purpose**: Optimization execution coordinator
- **Responsibilities**:
  - Coordinate problem, algorithm, and termination
  - Execute optimization with progress monitoring
  - Collect optimization metrics and history
  - Process results for GUI consumption
- **Key Features**:
  - Thread-safe optimization execution
  - Real-time progress callbacks
  - Comprehensive metrics collection
  - Graceful error handling and recovery

### Utility Layer (`utils/`)

#### Validators
- **Purpose**: Input validation and error checking
- **Responsibilities**:
  - Problem configuration validation
  - Algorithm parameter validation  
  - Expression syntax validation
  - Security validation for user expressions
- **Key Features**:
  - Comprehensive validation coverage
  - Clear, actionable error messages
  - Security-first approach
  - Integration with GUI for real-time feedback

#### Helpers
- **Purpose**: Utility functions and common operations
- **Responsibilities**:
  - File I/O operations
  - Data format conversions
  - Common mathematical operations
  - UI utility functions

## 🔄 Data Flow

### 1. Problem Definition Flow
```
User Input → ProblemTab → ValidationConfig → ProblemManager → PyMOO Problem
     ↑                                                             ↓
GUI Updates ← ValidationErrors ← Validators ← ConfigurationDict ←──┘
```

### 2. Algorithm Configuration Flow  
```
User Selection → AlgorithmTab → ValidationConfig → AlgorithmManager → PyMOO Algorithm
       ↑                                                                 ↓
Parameter Updates ← DynamicUI ← AlgorithmRequirements ← AlgorithmMeta ←──┘
```

### 3. Optimization Execution Flow
```
Run Command → ResultsTab → OptimizationWorker → Optimizer → PyMOO.minimize
     ↑                           ↓                  ↓            ↓
GUI Updates ← ProgressSignals ← ProgressCallback ← OptimizationResults
```

### 4. Result Processing Flow
```
PyMOO Results → Optimizer → ProcessedResults → ResultsTab → Visualizations
                    ↓              ↓              ↓             ↓
                Metrics → Statistics → Tables → ExportData
```

## 🧵 Threading Model

The application uses Qt's threading model to ensure responsive user experience:

### Main Thread (GUI Thread)
- **Purpose**: Handle all GUI operations and user interactions
- **Components**: All UI widgets, event handling, signal processing
- **Constraints**: Must not perform blocking operations

### Worker Thread (OptimizationWorker)
- **Purpose**: Execute potentially long-running optimizations
- **Components**: OptimizationWorker, PyMOO integration, result processing
- **Communication**: Qt signals for thread-safe communication with GUI
- **Features**: 
  - Cancellation support through threading.Event
  - Progress reporting via signals
  - Error handling and recovery

### Thread Safety Measures
- **Signal-Slot Communication**: All cross-thread communication uses Qt signals
- **Atomic Operations**: Critical data updates are atomic
- **Resource Management**: Proper cleanup on thread termination
- **Error Isolation**: Worker thread errors don't crash main application

## 🎯 MCDA Integration

The PyMOO GUI includes a comprehensive Multi-Criteria Decision Analysis (MCDA) module that enables sophisticated post-optimization analysis of Pareto-optimal solutions. This integration provides professional-grade decision support capabilities.

### MCDA Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   PyMOO Results │    │   MCDA Module   │    │  Decision       │
│                 │    │                 │    │  Support        │
├─────────────────┤    ├─────────────────┤    ├─────────────────┤
│ • Pareto Front  │───►│ • AHP Analyzer  │───►│ • Ranked Solns  │
│ • Decision Vars │    │ • TOPSIS Engine │    │ • Weight Vector │
│ • Objective Vals│    │ • MCDA Manager  │    │ • Consistency   │
│ • Constraint Vals│    │ • UI Controller │    │ • Preferences  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Mathematical Foundations

#### Analytic Hierarchy Process (AHP)
- **Theoretical Basis**: Saaty's eigenvalue method for deriving criteria weights
- **Implementation**: Principal eigenvalue decomposition with consistency validation
- **Key Equation**: $A \cdot w = \lambda_{max} \cdot w$ where $w$ represents criteria weights
- **Consistency Measure**: $CR = \frac{CI}{RI} = \frac{\lambda_{max} - n}{(n-1) \cdot RI}$
- **Reference**: Saaty, T. L. (1980). The Analytic Hierarchy Process. McGraw-Hill.

#### TOPSIS Method  
- **Theoretical Basis**: Distance-based ranking relative to ideal solutions
- **Normalization**: Vector normalization $r_{ij} = \frac{x_{ij}}{\sqrt{\sum_{k=1}^{m} x_{kj}^2}}$
- **Ideal Solutions**: $A^+ = \{v_1^+, v_2^+, ..., v_n^+\}$ and $A^- = \{v_1^-, v_2^-, ..., v_n^-\}$
- **Closeness Coefficient**: $C_i = \frac{S_i^-}{S_i^+ + S_i^-}$ where $S_i^+$ and $S_i^-$ are distances to ideal solutions
- **Reference**: Hwang, C. L., & Yoon, K. (1981). Multiple Attribute Decision Making. Springer.

### Data Flow in MCDA Module

```
PyMOO Results → prepare_pymoo_results() → Decision Matrix
       ↓
Criteria Definition → AHP Pairwise Comparisons → Weight Vector
       ↓                      ↓                      ↓  
TOPSIS Analysis ← Normalized Matrix ← apply_weights() ← Weight Integration
       ↓
Ranked Solutions → UI Display → Export Capabilities
```

### Integration Points

1. **Results Tab Integration**: Seamless transition from optimization results to MCDA analysis
2. **Criteria Mapping**: Automatic mapping of optimization objectives to MCDA criteria
3. **Weight Persistence**: Save and load weight configurations for consistent analysis
4. **Export Integration**: Include MCDA rankings in result export functionality

## 🔌 Extension Points

The architecture provides several extension points for future enhancements:

### 1. Algorithm Extensions
- **Interface**: Implement PyMOO Algorithm interface
- **Integration**: Add to AlgorithmManager._create_algorithm_from_config()
- **UI**: Add algorithm-specific parameters to AlgorithmTab

### 2. Problem Type Extensions
- **Interface**: Extend ProblemManager with new problem types
- **Integration**: Add problem-specific validation and creation
- **UI**: Extend ProblemTab with type-specific controls

### 3. Visualization Extensions
- **Interface**: Create new matplotlib-based plot classes
- **Integration**: Add to ResultsTab plot selection
- **Features**: Custom metrics, specialized visualizations

### 4. Export Format Extensions  
- **Interface**: Implement export strategy pattern
- **Integration**: Add to export dialog and processing
- **Formats**: New file formats, cloud integration, database storage

### 6. MCDA Method Extensions
- **Interface**: Implement new MCDA methods in core/mcda.py
- **Integration**: Add to MCDAManager method selection
- **UI**: Extend MCDATab with method-specific parameters
- **Examples**: ELECTRE, PROMETHEE, SAW, VIKOR methods

### 7. Criteria Definition Extensions
- **Interface**: Extend criteria input mechanisms  
- **Integration**: Add advanced criteria types and relationships
- **Features**: Hierarchical criteria, group decision making, fuzzy criteria

### 8. Mathematical Extensions
- **Interface**: Add advanced mathematical operators and validations
- **Integration**: Extend eigenvalue handling, add sensitivity analysis

---

## 📊 Current System Status

### ✅ Production-Ready Components

#### Core Optimization System
- **Complete Implementation**: All 5 algorithms (NSGA-II, NSGA-III, SPEA2, MOEA/D, RVEA)
- **Full Parameter Control**: Crossover, mutation, selection operators
- **Mixed Variable Support**: Real, Integer, Binary variables with constraints
- **Results System**: Comprehensive visualization and export capabilities

#### Individual MCDA System
- **AHP Implementation**: Complete eigenvalue-based weight calculation
- **TOPSIS Implementation**: Full distance-based ranking system
- **Professional UI**: Dropdown-based Saaty scale, real-time validation
- **Mathematical Rigor**: Academic-quality implementation with proper references

#### 🆕 Group Decision System
- **Multi-User Authentication**: Secure role-based access (admin/user)
- **Session Management**: Custom dialog with rich problem descriptions
- **Consistency Validation**: Pre-submission AHP consistency checking
- **Group Aggregation**: Geometric mean (AHP) and arithmetic mean (TOPSIS)
- **Database Integration**: SQLite with automated schema migration

### 🔄 Enhanced Features (Recently Updated)

#### Consistency Validation System
- **Pre-submission Checking**: Prevents inconsistent AHP data from database entry
- **Educational Feedback**: Real-time guidance helps users improve comparisons
- **Mathematical Validation**: Uses Saaty's CR < 0.1 threshold with Random Index
- **User Experience**: Clear error messages with specific improvement suggestions

#### Session Creation Enhancement
- **Rich Problem Context**: Multi-line description replaces simple name input
- **Administrative Tools**: Comprehensive dialog for session setup
- **Validation System**: Input validation ensures meaningful session information
- **Database Migration**: Seamless upgrade from problem_name to problem_description

### 🚧 Areas for Future Enhancement

#### Advanced Group Features
- **Fuzzy MCDA Methods**: Theoretical framework documented, implementation needed
- **Advanced Aggregation**: Alternative methods beyond geometric/arithmetic means
- **Real-time Collaboration**: Live updates when users submit comparisons
- **Sensitivity Analysis**: Mathematical framework exists, UI integration needed

#### System Infrastructure
- **Cloud Deployment**: Currently local SQLite, could expand to cloud databases
- **REST API**: No external API currently, potential for system integration
- **Advanced Security**: Basic password hashing, could implement stronger methods
- **Comprehensive Audit Trail**: Basic logging, could expand for full user action tracking

#### Performance & Scalability
- **Large Group Handling**: Current system works well for typical group sizes
- **Parallel Processing**: Framework documented for large-scale analysis
- **Memory Optimization**: Current implementation efficient, could optimize for very large problems
- **Real-time Updates**: Session management exists, could add live collaboration features
- **Features**: Uncertainty analysis, robustness testing, what-if scenarios

## 📊 Performance Considerations

### Memory Management
- **Lazy Loading**: Components loaded only when needed
- **Data Cleanup**: Proper cleanup of optimization results and history
- **Resource Monitoring**: Track memory usage during long optimizations

### Optimization Performance
- **Native Implementation**: PyMOO provides C-optimized algorithms
- **Parallel Processing**: Multi-threaded optimization execution
- **Progress Batching**: Efficient progress update batching

### UI Responsiveness
- **Non-blocking Operations**: All long operations in worker threads
- **Progressive Updates**: Incremental UI updates during optimization
- **Efficient Rendering**: Optimized matplotlib integration

## 🔧 Configuration Management

### Configuration Storage
- **Format**: JSON-based configuration files
- **Structure**: Hierarchical organization matching UI structure
- **Validation**: Schema-based validation on load/save
- **Versioning**: Configuration version tracking for compatibility

### Default Management
- **Intelligent Defaults**: Context-aware default parameter selection
- **User Preferences**: Persistent user preference storage
- **Template System**: Built-in problem and algorithm templates

## 🧪 Testing Strategy

### Unit Testing
- **Core Logic**: ProblemManager, AlgorithmManager, Optimizer
- **Validation**: Comprehensive validator testing
- **Utilities**: Helper function testing

### Integration Testing
- **Component Integration**: Cross-component interaction testing
- **PyMOO Integration**: Algorithm and problem integration testing
- **File I/O**: Configuration save/load testing

### UI Testing
- **Widget Testing**: Individual widget functionality
- **Workflow Testing**: Complete user workflow validation
- **Error Handling**: Error scenario and recovery testing

This architecture provides a solid foundation for a maintainable, extensible,
and performant multi-objective optimization GUI application.
"""
