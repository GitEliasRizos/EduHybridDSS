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
**ENHANCED**: Professional-grade decision support with group collaboration capabilities.

#### **Individual MCDA Methods**
- **Analytic Hierarchy Process (AHP)**: Pairwise comparisons with Saaty's 1-9 scale and eigenvalue method
- **TOPSIS Analysis**: Distance-based ranking with ideal solutions and mixed objectives
- **Consistency Validation**: Real-time CR checking with educational feedback
- **Mathematical Rigor**: Robust eigenvalue handling and numerical precision

#### **🆕 Group Decision Making System**
- **Multi-User Authentication**: Secure login system with admin/user role management
- **Collaborative Sessions**: Administrators create group decision sessions with rich problem descriptions
- **AHP Consistency Checking**: Pre-submission validation prevents inconsistent data entry
- **Group Aggregation**: Geometric mean for AHP matrices, arithmetic mean for TOPSIS weights
- **Consensus Analysis**: Complete group decision pipeline with ranking aggregation
- **Session Management**: Custom dialog for detailed problem context and user guidance

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

4. **Apply Decision Analysis** (MCDA Tab)
   - **Individual AHP**: Define criteria importance using pairwise comparisons
     - Use intuitive dropdown with Saaty scale (1/9 to 9)
     - Monitor consistency ratio in real-time with validation
     - Generate criteria weights automatically
   - **Individual TOPSIS**: Rank solutions based on ideal solution similarity
     - Apply calculated weights to optimization results
     - View ranked solutions with closeness coefficients

### 🆕 Group Decision Workflow (Admin)

1. **Complete Individual Optimization** (As above)
   - Run optimization to generate Pareto-optimal solutions
   - Review results and validate solution quality

2. **Create Collaborative Session**
   - Accept prompt to create group decision session after optimization
   - Use custom dialog to provide detailed problem description
   - System automatically creates session with optimization results

3. **Coordinate Group Input**
   - Share user credentials with decision participants
   - Users log in with simple interface focused on comparisons
   - Each user provides either AHP pairwise comparisons or TOPSIS weights
   - Built-in consistency checking prevents invalid submissions

4. **Analyze Group Consensus**
   - Access "Group Decisions" menu from main application
   - Select target session and analysis method
   - Run AHP aggregation (geometric mean), TOPSIS aggregation (arithmetic mean), or complete consensus
   - Export comprehensive group decision reports with individual and aggregate results
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

### Individual Usage
Run the main application:
```bash
python main.py
```

**Login**: Use default admin credentials (shown on startup) or create new user account.

### Individual Analysis Workflow
1. **Problem Setup**: Define your optimization problem with variables, objectives, constraints
2. **Algorithm Selection**: Choose and configure optimization algorithm with appropriate operators
3. **Run Optimization**: Execute optimization and view Pareto front with real-time progress
4. **MCDA Analysis**: Apply AHP or TOPSIS to rank solutions based on your preferences
5. **Export Results**: Save optimization results and decision analysis for documentation

### 🆕 Group Decision Workflow
1. **Admin Setup**: Complete individual optimization workflow above
2. **Session Creation**: Accept group session creation prompt with detailed problem description
3. **User Coordination**: Share credentials with decision participants for collaborative input
4. **Group Analysis**: Aggregate user inputs using mathematical methods (geometric/arithmetic means)
5. **Consensus Results**: Export comprehensive group decision reports with rankings and analysis

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

**ENHANCED FEATURE**: Comprehensive individual and group MCDA capabilities for collaborative decision making.

### **Individual MCDA Methods**

#### **AHP (Analytic Hierarchy Process)**
- **Interactive pairwise comparisons** using Saaty's 1-9 scale with dropdown interface
- **Real-time consistency checking** (CR < 0.1) with educational feedback
- **Automatic weight calculation** via eigenvalue method following Saaty (1980)
- **Best for**: When decision makers can express relative importance between criteria pairs

#### **TOPSIS (Technique for Order of Preference by Similarity to Ideal Solution)**  
- **Configurable criteria weights** with normalization and validation
- **Multiple normalization methods** (vector and linear normalization)
- **Distance-based ranking** using positive and negative ideal solutions
- **Best for**: When decision makers have specific weight preferences for each criterion

### **🆕 Group Decision System**

#### **Multi-User Architecture**
- **Secure Authentication**: Role-based access (admin/user) with password protection
- **Session Management**: Administrators create collaborative decision sessions
- **User Interface**: Simplified interface for regular users focused on comparisons
- **Consistency Validation**: Pre-submission checking prevents invalid data entry

#### **Group Aggregation Methods**
- **AHP Aggregation**: Geometric mean of pairwise comparison matrices (Saaty, 1989)
- **TOPSIS Aggregation**: Arithmetic mean of individual weight vectors
- **Consensus Analysis**: Complete group decision pipeline with ranking synthesis
- **Mathematical Rigor**: Maintains reciprocal properties and normalization constraints

### **Complete MCDA Workflow**
1. **Individual Analysis**: Run optimization → apply personal MCDA preferences
2. **Group Session Creation**: Admin creates collaborative session with problem context
3. **Distributed Input**: Multiple users provide AHP comparisons or TOPSIS weights
4. **Group Aggregation**: System combines inputs using appropriate mathematical methods
5. **Consensus Results**: Export comprehensive reports with individual and group rankings

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
