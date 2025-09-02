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
separation of concerns for optimization-specific functionality. The architecture
is designed for:

- **Modularity**: Each component has clear responsibilities
- **Extensibility**: Easy addition of new algorithms, problems, or UI features
- **Maintainability**: Clear separation between GUI and optimization logic
- **Testability**: Components can be tested independently
- **Performance**: Multi-threaded execution for responsive user experience

### High-Level Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Presentation  │    │    Business     │    │      Data       │
│     Layer       │    │     Logic       │    │     Layer       │
├─────────────────┤    ├─────────────────┤    ├─────────────────┤
│ • MainWindow    │◄──►│ • ProblemMgr    │◄──►│ • Configuration │
│ • ProblemTab    │    │ • AlgorithmMgr  │    │ • Results       │
│ • AlgorithmTab  │    │ • Optimizer     │    │ • Templates     │
│ • ResultsTab    │    │ • Validators    │    │ • Export Data   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
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

#### ResultsTab
- **Purpose**: Optimization execution and result visualization
- **Responsibilities**:
  - Optimization execution coordination
  - Progress monitoring and display
  - Result visualization and analysis
  - Export functionality
- **Key Features**:
  - Multi-threaded optimization execution
  - Real-time progress updates
  - Professional visualization with matplotlib
  - Comprehensive result export options

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

### 5. Validation Extensions
- **Interface**: Extend Validators with new validation rules
- **Integration**: Add to real-time validation pipeline
- **Features**: Custom business rules, external validation services

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
