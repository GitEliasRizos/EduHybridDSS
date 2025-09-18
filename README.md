# PyMOO GUI - Multi-Objective Optimization & Decision Analysis Interface

A comprehensive graphical user interface for PyMOO (Multi-objective Optimization in Python) built with PyQt6. This application provides an intuitive, feature-rich environment for defining, configuring, and solving multi-objective optimization problems with professional-grade visualization, analysis capabilities, and integrated **Multi-Criteria Decision Analysis (MCDA)** for Pareto-optimal solution ranking.

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

### 🎖️ **Multi-Criteria Decision Analysis (MCDA)**
**NEW**: Advanced decision support for Pareto-optimal solution ranking and selection.

#### **Analytic Hierarchy Process (AHP)**
- **Pairwise Comparisons**: Intuitive dropdown interface using Saaty's 1-9 scale
- **Weight Calculation**: Principal eigenvalue method following Saaty (1980) methodology
- **Consistency Validation**: Real-time consistency ratio monitoring with Random Index
- **Mathematical Rigor**: Robust handling of complex eigenvalues and numerical precision issues
- **Professional Implementation**: Comprehensive documentation with APA-style academic references

#### **TOPSIS Analysis**
- **Ideal Solution Ranking**: Distance-based ranking relative to positive and negative ideal solutions
- **Multiple Normalization**: Vector and linear normalization methods (Hwang & Yoon, 1981)
- **Mixed Objectives**: Seamless handling of minimize/maximize objective directions
- **Closeness Coefficients**: Relative closeness calculations for solution ranking
- **Comprehensive Results**: Detailed analysis with ranking tables and score interpretation

#### **Integration Features**
- **Seamless PyMOO Integration**: Direct analysis of optimization results
- **Criteria Mapping**: Automatic mapping of optimization objectives to MCDA criteria
- **Weight Persistence**: Save and load weight configurations for consistent analysis
- **Export Capabilities**: Include MCDA rankings in comprehensive result exports
- **Mathematical Documentation**: Complete theoretical foundations with academic references

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
- **Design Selection**: Use AHP/TOPSIS to rank design alternatives from Pareto front

### **Scientific Research**
- **Algorithm Development**: Test new optimization approaches with comprehensive metrics
- **Benchmark Studies**: Compare algorithm performance across multiple problems
- **Publication Support**: Generate publication-ready plots and statistical analyses
- **Decision Analysis**: Apply rigorous MCDA methods for solution selection and ranking

### **Educational Applications**
- **Teaching Tool**: Demonstrate multi-objective optimization concepts interactively
- **Student Projects**: Provide accessible interface for optimization coursework
- **Research Training**: Learn optimization techniques through hands-on experimentation
- **MCDA Education**: Understand decision analysis methods with practical implementations

### **Business and Management**
- **Strategic Decision Making**: Apply AHP for criteria weighting in business decisions
- **Supplier Selection**: Use TOPSIS for multi-criteria supplier evaluation
- **Project Portfolio Optimization**: Balance multiple project objectives with decision support
- **Investment Analysis**: Rank investment alternatives using mathematical decision methods

## � **Quick Start with MCDA**

### Complete Optimization + Decision Analysis Workflow

1. **Define Your Problem** (Problem Tab)
   - Set up variables, objectives, and constraints
   - Load from example library or create custom problem

2. **Configure Algorithm** (Algorithm Tab)
   - Select algorithm (NSGA-II recommended for beginners)
   - Set population size and generation limits
   - Choose appropriate operators

3. **Run Optimization** (Results Tab)
   - Execute optimization with real-time progress
   - Visualize Pareto front and convergence
   - Export optimization results

4. **Apply Decision Analysis** (MCDA Tab) ⭐ **NEW**
   - **AHP Method**: Define criteria importance using pairwise comparisons
     - Use intuitive dropdown with Saaty scale (1/9 to 9)
     - Monitor consistency ratio in real-time
     - Generate criteria weights automatically
   - **TOPSIS Analysis**: Rank solutions based on ideal solution similarity
     - Apply calculated weights to optimization results
     - View ranked solutions with closeness coefficients
     - Export comprehensive MCDA results

### Example MCDA Workflow
```python
# After optimization, in MCDA tab:
1. Select criteria (your optimization objectives)
2. Perform pairwise comparisons: 
   - "Cost vs Quality": 1/3 (Quality 3x more important)
   - "Cost vs Performance": 1/5 (Performance 5x more important) 
   - "Quality vs Performance": 1/2 (Performance 2x more important)
3. Check consistency ratio (should be < 0.1)
4. Apply TOPSIS ranking to get best solution from Pareto front
```

## �🛠 **Supported Algorithms**

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
2. **Algorithm Selection**: Choose and configure optimization algorithm
3. **Run Optimization**: Execute optimization and view Pareto front
4. **MCDA Analysis**: Apply AHP or TOPSIS to rank solutions based on preferences
5. **Export Results**: Save optimization results and decision analysis

### Example Configurations
The `examples/` directory contains ready-to-use problem configurations:
- `simple_biobjective.json` - Basic bi-objective optimization
- `zdt1.json` - ZDT1 benchmark problem
- `dtlz2_nsga3.json` - Many-objective DTLZ2 with NSGA-III
- `pressure_vessel_spea2.json` - Engineering design optimization
- `knapsack_nsga2.json` - Binary knapsack optimization with NSGA-II
- `portfolio_moead.json` - Portfolio optimization with MOEA/D
- `constrained_engineering.json` - Engineering design with constraints
- `rosenbrock_mo.json` - Multi-objective Rosenbrock function

## 🎯 **Multi-Criteria Decision Analysis (MCDA)**

**NEW FEATURE**: The application now includes comprehensive MCDA capabilities to help you select the best solution from Pareto optimal results.

### **AHP (Analytic Hierarchy Process)**
- **Interactive pairwise comparisons** using 1-9 scale
- **Automatic consistency checking** (CR < 0.1)
- **Criteria weight calculation** via eigenvalue method
- **Best for**: When you can express preferences as pairwise comparisons

### **TOPSIS (Technique for Order of Preference by Similarity to Ideal Solution)**  
- **Configurable criteria weights** (0-1 scale with normalization)
- **Ideal and anti-ideal solution identification**
- **Distance-based ranking** using Euclidean distance
- **Best for**: When you have specific weight preferences for each criterion

### **MCDA Workflow**
1. **Complete Optimization**: Run any PyMOO algorithm to get Pareto solutions
2. **Access MCDA Tab**: Automatically enabled after optimization completion
3. **Choose Method**: Select AHP (pairwise) or TOPSIS (weights)
4. **Configure Preferences**: Set comparisons (AHP) or weights (TOPSIS)
5. **Analyze Results**: View rankings, scores, and detailed analysis
6. **Export Rankings**: Save to CSV or JSON for documentation

### **MCDA Demo**
Test the MCDA integration:
```bash
python demo_mcda.py

## Quick Start

1. **Load Example**: File → Open Problem → `simple_biobjective.json`
2. **Run Optimization**: F5 or Run → Start Optimization  
3. **Analyze Solutions**: Switch to "MCDA Analysis" tab (enabled after optimization)
4. **Configure MCDA**: Choose AHP or TOPSIS and set your preferences
5. **View Rankings**: See which solutions best match your criteria
6. **Export Results**: Save rankings and analysis to CSV/JSON

## 🧪 **Feature Demos**

**MCDA Integration Demo**: Test the complete workflow with sample data
```bash  
python demo_mcda.py
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
│   ├── results_tab.py     # Optimization results display
│   └── mcda_tab.py        # 🆕 Multi-criteria decision analysis
├── core/                   # Core functionality
│   ├── problem_manager.py # Problem creation and validation
│   ├── algorithm_manager.py # Algorithm configuration
│   ├── optimizer.py       # Optimization execution
│   └── mcda.py            # 🆕 AHP and TOPSIS implementation
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
