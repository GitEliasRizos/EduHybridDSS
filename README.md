# PyMOO GUI - Multi-Objective Optimization Interface

A comprehensive graphical user interface for PyMOO (Multi-objective Optimization in Python) built with PyQt6. This application provides an intuitive, feature-rich environment for defining, configuring, and solving multi-objective optimization problems with professional-grade visualization and analysis capabilities.

## 🌟 Key Features

### 📋 **Problem Definition**
- **Mixed Variable Types**: Support for Real, Integer, and Binary variables with proper constraint enforcement
- **Custom Objective Functions**: Define mathematical expressions with full numpy function support
- **Flexible Constraints**: Linear and nonlinear equality/inequality constraints
- **Expression Validation**: Real-time syntax checking and error reporting
- **Problem Templates**: Built-in examples and the ability to save/load custom configurations

### 🧬 **Algorithm Configuration**  
- **Multiple Algorithms**: NSGA-II, NSGA-III, SPEA2, MOEA/D, RVEA with intelligent parameter suggestions
- **Operator Customization**: Configure crossover (SBX, PCX, UX) and mutation (Polynomial, Gaussian) operators
- **Reference Directions**: Automatic setup for many-objective algorithms with customizable generation methods
- **Parameter Validation**: Real-time validation with algorithm-specific parameter recommendations
- **Advanced Options**: Population sizing, termination criteria, random seeding control

### 🎯 **Optimization Execution**
- **Multi-threaded Processing**: Non-blocking optimization with responsive GUI during execution
- **Real-time Progress**: Detailed progress monitoring with generation tracking and convergence metrics
- **Constraint Enforcement**: Automatic repair operators for integer/binary variables during optimization
- **Error Handling**: Comprehensive error reporting with suggested solutions
- **Cancellation Support**: Safe optimization termination at any point

### 📊 **Results Visualization**
- **Professional Plots**: Publication-ready visualizations with matplotlib integration
- **Multiple Views**: Objective space, decision space, convergence plots, solution tables
- **Interactive Analysis**: Sortable tables, solution filtering, detailed inspection tools
- **Export Options**: Save results as JSON, CSV, or high-resolution images
- **Statistical Analysis**: Built-in metrics and performance indicators

## � Advanced Features

### 🔧 **Mixed-Variable Optimization**
- **Intelligent Constraint Handling**: Automatic repair operators ensure integer/binary variables maintain discrete values
- **Type-Aware Sampling**: Specialized initialization for mixed-variable problems
- **Seamless Integration**: All algorithms work transparently with mixed variable types
- **Validation & Feedback**: Real-time validation of variable definitions and bounds

### 📈 **Performance & Scalability**
- **Efficient Implementation**: Optimized for both small-scale and large-scale optimization problems
- **Memory Management**: Smart resource handling for long-running optimizations
- **Progress Tracking**: Detailed metrics collection without performance overhead
- **Parallel Processing**: Worker thread architecture prevents GUI freezing

### 🎨 **User Experience**
- **Intuitive Interface**: Logical workflow with tab-based organization
- **Responsive Design**: Resizable panels and scrollable content for any screen size
- **Keyboard Shortcuts**: Full menu system with keyboard navigation support
- **Context Help**: Tooltips, status messages, and detailed error explanations

## 💡 **Use Cases**

### **Engineering Design**
- **Multi-disciplinary Optimization**: Balance competing objectives like cost, performance, weight
- **Parameter Tuning**: Optimize control parameters with multiple quality criteria
- **Robustness Analysis**: Find solutions robust to parameter variations

### **Scientific Research**
- **Algorithm Development**: Test new optimization approaches with comprehensive metrics
- **Benchmark Studies**: Compare algorithm performance across multiple problems
- **Publication Support**: Generate publication-ready plots and statistical analyses

### **Educational Applications**
- **Teaching Tool**: Demonstrate multi-objective optimization concepts interactively
- **Student Projects**: Provide accessible interface for optimization coursework
- **Research Training**: Learn optimization techniques through hands-on experimentation

## 🛠 **Supported Algorithms**

### **Pareto-based Approaches**
- **NSGA-II**: Fast Non-dominated Sorting Genetic Algorithm II
  - *Best for*: 2-3 objectives, fast convergence, well-established
  - *Features*: Non-dominated sorting, crowding distance diversity preservation
  
- **SPEA2**: Strength Pareto Evolutionary Algorithm 2  
  - *Best for*: Alternative to NSGA-II, external archive maintenance
  - *Features*: Fitness assignment based on dominance strength, archive-based selection

### **Reference-based Approaches**
- **NSGA-III**: NSGA-II extension for many objectives
  - *Best for*: 4+ objectives, structured Pareto front approximation
  - *Features*: Reference point guided selection, Das-Dennis reference directions
  
- **RVEA**: Reference Vector Guided Evolutionary Algorithm
  - *Best for*: Many objectives, adaptive reference vectors
  - *Features*: Angle-penalized distance, reference vector adaptation

### **Decomposition-based Approaches**  
- **MOEA/D**: Multi-Objective Evolutionary Algorithm based on Decomposition
  - *Best for*: Problems with known preference structure, scalable to many objectives
  - *Features*: Scalar function decomposition, neighborhood-based evolution

## 📦 **Installation**

1. Clone or download this project
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Basic Usage
Run the main application:
```bash
python main.py
```

### Advanced Workflow
1. **Problem Setup**: Define your optimization problem
2. **Real-time Testing**: Use real-time visualization to understand algorithm behavior  
3. **Algorithm Comparison**: Compare multiple algorithms to find the best one
4. **Performance Analysis**: Generate comprehensive metrics and reports
5. **Export Results**: Save everything for documentation or publication

### Example Configurations
The `examples/` directory contains ready-to-use problem configurations:
- `simple_biobjective.json` - Basic bi-objective optimization
- `zdt1.json` - ZDT1 benchmark problem
- `dtlz2_nsga3.json` - Many-objective DTLZ2 with NSGA-III
- `pressure_vessel_spea2.json` - Engineering design optimization
- `knapsack_moead.json` - Combinatorial optimization

## Quick Start

1. **Load Example**: File → Open Problem → `simple_biobjective.json`
2. **Run Basic Optimization**: F5 or Run → Start Optimization  
3. **Try Real-time**: Advanced → Real-time Visualization
4. **Compare Algorithms**: Advanced → Multi-Algorithm Comparison
5. **Analyze Performance**: Advanced → Performance Metrics

## New Feature Demo

Run the interactive demo to learn about new features:
```bash  
python demo_new_features.py
```

## Dependencies

- **Python 3.9+**: Runtime environment
- **PyQt6**: GUI framework
- **PyMOO 0.6+**: Multi-objective optimization library
- **NumPy**: Numerical computing
- **Matplotlib**: Plotting and visualization
- **SciPy**: Scientific computing (for metrics)
- **Pandas**: Data analysis (for export)
- **scikit-learn**: Machine learning (for clustering analysis)
- **OpenPyXL**: Excel export functionality

## Architecture

```
PyMOO GUI/
├── main.py                 # Application entry point
├── ui/                     # User interface modules
│   ├── main_window.py     # Main application window
│   ├── problem_tab.py     # Problem definition interface
│   ├── algorithm_tab.py   # Algorithm configuration
│   ├── results_tab.py     # Basic results display
│   ├── realtime_viz.py    # 🆕 Real-time visualization
│   ├── multi_algorithm.py # 🆕 Algorithm comparison
│   └── performance_metrics.py # 🆕 Metrics dashboard
├── core/                  # Core optimization logic
│   ├── problem_manager.py # Problem evaluation
│   ├── algorithm_manager.py # Algorithm instantiation  
│   └── optimizer.py       # Optimization execution
├── utils/                 # Utility functions
│   ├── helpers.py         # Configuration I/O
│   └── validators.py      # Input validation
└── examples/              # Example configurations
    ├── simple_biobjective.json
    ├── zdt1.json
    └── ...
```

## What's New in v2.0.0

### Enhanced User Experience
- **4 Tab Interface**: Results, Real-time, Comparison, Metrics
- **Advanced Menu**: Quick access to new features
- **Integrated Workflow**: Seamless feature interaction

### Scientific Rigor  
- **Professional Metrics**: Publication-quality performance indicators
- **Statistical Analysis**: Comprehensive algorithm comparison
- **Export Capabilities**: Results in multiple formats

### Real-time Capabilities
- **Live Monitoring**: Watch optimization as it happens
- **Interactive Controls**: Adjust visualization in real-time
- **Performance Feedback**: Immediate algorithm assessment

## Contributing

Contributions are welcome! Areas for enhancement:
- Additional optimization algorithms
- New performance metrics  
- Enhanced visualization options
- Export format support

## License

This project is open source. Please check the license file for details.

## Citation

If you use PyMOO GUI in your research, please cite:
- The PyMOO library: Blank, J. & Deb, K. (2020). Pymoo: Multi-objective optimization in python. IEEE Access.
- This GUI tool: [Your citation information]

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
