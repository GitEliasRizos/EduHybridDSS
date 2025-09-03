"""
Algorithm Configuration Tab - Configure optimization algorithms

This module provides the AlgorithmTab class which serves as the interface for
configuring multi-objective optimization algorithms. It allows users to select
algorithms, configure parameters, and customize genetic operators for their
specific optimization problems.

Key Features:
- Algorithm selection (NSGA-II, NSGA-III, SPEA2, MOEA/D, RVEA)
- Population and generation parameter configuration
- Genetic operator customization (crossover, mutation)
- Reference direction setup for many-objective algorithms
- Termination criteria specification
- Real-time parameter validation and suggestions
- Algorithm-specific parameter adaptation
- Import/export of algorithm configurations

The AlgorithmTab dynamically adjusts available options based on the selected
algorithm and number of objectives in the problem. It provides intelligent
defaults while allowing advanced users to fine-tune all parameters.

Supported Algorithms:
    - NSGA-II: Best for 2-3 objectives, fast convergence
    - NSGA-III: Excellent for many objectives (4+), reference-based
    - SPEA2: Alternative multi-objective approach with archive
    - MOEA/D: Decomposition-based, good for complex Pareto fronts
    - RVEA: Reference vector guided, efficient for many objectives

Algorithm Components:
    - Population sampling strategies
    - Crossover operators (SBX, PCX, UX)
    - Mutation operators (Polynomial, Gaussian)  
    - Selection mechanisms
    - Reference direction generation
    - Termination criteria (generations, evaluations, time)

Classes:
    AlgorithmTab: Main widget for algorithm configuration

Author: Elias Rizos [it21490]
Version: 1.3.2
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
                            QGroupBox, QComboBox, QSpinBox, QDoubleSpinBox,
                            QCheckBox, QLineEdit, QTextEdit, QTableWidget,
                            QTableWidgetItem, QHeaderView, QPushButton,
                            QLabel, QScrollArea, QTabWidget)
from PyQt6.QtCore import Qt, pyqtSignal


class AlgorithmTab(QWidget):
    """
    Widget for configuring optimization algorithms
    
    This class provides a comprehensive interface for selecting and configuring
    multi-objective optimization algorithms. It dynamically adapts its interface
    based on the chosen algorithm and provides intelligent parameter suggestions.
    
    Key Responsibilities:
    - Present available algorithms with descriptions and recommendations
    - Configure algorithm-specific parameters (population size, generations)
    - Set up genetic operators (crossover, mutation) with appropriate parameters
    - Handle reference directions for many-objective algorithms
    - Configure termination criteria and stopping conditions
    - Validate parameter combinations and provide warnings/suggestions
    - Enable advanced users to fine-tune all algorithm aspects
    
    The interface is organized into logical groups that appear/disappear based
    on algorithm requirements. For example, reference directions are only shown
    for algorithms that use them (NSGA-III, RVEA, etc.).
    
    UI Organization:
    - Algorithm Selection: Choose primary algorithm
    - Parameters: Population size, generations, seed
    - Genetic Operators: Crossover and mutation configuration
    - Reference Directions: For many-objective algorithms
    - Termination: Stopping criteria and limits
    
    Dynamic Behavior:
    - Options change based on selected algorithm
    - Parameter ranges adapt to problem characteristics
    - Intelligent defaults are provided for all settings
    - Advanced options can be revealed for expert users
    
    Attributes:
        algorithm_changed (pyqtSignal): Emitted when configuration changes
    """
    
    # Signal emitted when any aspect of algorithm configuration changes
    # Allows other components to react to algorithm updates
    algorithm_changed = pyqtSignal()
    
    def __init__(self):
        """
        Initialize the AlgorithmTab widget
        
        Sets up the complete interface for algorithm configuration including
        all parameter groups, connects signals, and establishes default
        algorithm settings.
        """
        super().__init__()
        self._init_ui()                    # Create UI components
        self._connect_signals()            # Connect change notifications
        self._update_algorithm_options()   # Set up algorithm-specific options
        
    def _init_ui(self):
        """
        Initialize the user interface layout and components
        
        Creates a scrollable interface with five main configuration groups:
        1. Algorithm Selection - choose the optimization algorithm
        2. Algorithm Parameters - population size, generations, random seed
        3. Genetic Operators - crossover and mutation operator configuration
        4. Reference Directions - for many-objective algorithms (NSGA-III, RVEA)
        5. Termination Criteria - stopping conditions and limits
        
        Uses QScrollArea to accommodate all configuration options comfortably.
        """
        layout = QVBoxLayout(self)
        
        # Create scroll area for algorithm configuration options
        # This ensures all options are accessible even on smaller screens
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        
        # Initialize configuration sections in logical workflow order
        self._init_algorithm_selection_group(scroll_layout)     # Choose algorithm
        self._init_algorithm_parameters_group(scroll_layout)    # Basic parameters
        self._init_genetic_operators_group(scroll_layout)       # Crossover/mutation
        self._init_reference_directions_group(scroll_layout)    # Many-objective setup
        self._init_termination_group(scroll_layout)             # Stopping criteria
        
        # Add stretch to prevent UI components from being cramped together
        scroll_layout.addStretch()
        
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        layout.addWidget(scroll_area)
        
    def _init_algorithm_selection_group(self, parent_layout):
        """Initialize algorithm selection group"""
        group = QGroupBox("Algorithm Selection")
        layout = QFormLayout(group)
        
        # Algorithm category
        self.algorithm_category = QComboBox()
        self.algorithm_category.addItems([
            "Evolutionary Algorithms",
            "Decomposition-based",
            "Indicator-based",
            "Reference Point-based",
            "Other Algorithms"
        ])
        layout.addRow("Category:", self.algorithm_category)
        
        # Algorithm name
        self.algorithm_name = QComboBox()
        layout.addRow("Algorithm:", self.algorithm_name)
        
        # Algorithm description
        self.algorithm_description = QTextEdit()
        self.algorithm_description.setMaximumHeight(80)  # Increased from 60 for better visibility
        self.algorithm_description.setReadOnly(True)
        self.algorithm_description.setStyleSheet("QTextEdit { background-color: #303030; }")  # Light background
        layout.addRow("Description:", self.algorithm_description)
        
        parent_layout.addWidget(group)
        
    def _init_algorithm_parameters_group(self, parent_layout):
        """Initialize algorithm parameters group"""
        group = QGroupBox("Algorithm Parameters")
        layout = QFormLayout(group)
        
        # Population size
        self.population_size = QSpinBox()
        self.population_size.setRange(10, 10000)
        self.population_size.setValue(100)
        layout.addRow("Population Size:", self.population_size)
        
        # Number of generations
        self.n_generations = QSpinBox()
        self.n_generations.setRange(1, 100000)
        self.n_generations.setValue(250)
        layout.addRow("Generations:", self.n_generations)
        
        # Seed for reproducibility
        self.seed = QSpinBox()
        self.seed.setRange(0, 2**31 - 1)
        self.seed.setValue(42)
        layout.addRow("Random Seed:", self.seed)
        
        # Algorithm-specific parameters
        self.specific_params_layout = QVBoxLayout()
        layout.addRow("Specific Parameters:", self.specific_params_layout)
        
        parent_layout.addWidget(group)
        
    def _init_genetic_operators_group(self, parent_layout):
        """Initialize genetic operators group"""
        group = QGroupBox("Genetic Operators")
        layout = QVBoxLayout(group)
        
        # Create tabs for crossover and mutation
        tabs = QTabWidget()
        
        # Crossover tab
        crossover_tab = QWidget()
        crossover_layout = QFormLayout(crossover_tab)
        
        self.crossover_operator = QComboBox()
        self.crossover_operator.addItems([
            "SBX (Simulated Binary Crossover)",
            "PCX (Parent-Centric Crossover)",
            "BLX (Blend Crossover)",
            "UX (Uniform Crossover)",
            "OX (Order Crossover)",
            "PMX (Partially Matched Crossover)"
        ])
        crossover_layout.addRow("Crossover Operator:", self.crossover_operator)
        
        self.crossover_prob = QDoubleSpinBox()
        self.crossover_prob.setRange(0.0, 1.0)
        self.crossover_prob.setSingleStep(0.01)
        self.crossover_prob.setValue(0.9)
        crossover_layout.addRow("Crossover Probability:", self.crossover_prob)
        
        self.crossover_eta = QDoubleSpinBox()
        self.crossover_eta.setRange(0.1, 50.0)
        self.crossover_eta.setValue(15.0)
        crossover_layout.addRow("Distribution Index (η):", self.crossover_eta)
        
        tabs.addTab(crossover_tab, "Crossover")
        
        # Mutation tab
        mutation_tab = QWidget()
        mutation_layout = QFormLayout(mutation_tab)
        
        self.mutation_operator = QComboBox()
        self.mutation_operator.addItems([
            "Polynomial Mutation",
            "Gaussian Mutation",
            "Uniform Mutation",
            "Bit-flip Mutation",
            "Scramble Mutation",
            "Swap Mutation"
        ])
        mutation_layout.addRow("Mutation Operator:", self.mutation_operator)
        
        self.mutation_prob = QDoubleSpinBox()
        self.mutation_prob.setRange(0.0, 1.0)
        self.mutation_prob.setSingleStep(0.01)
        self.mutation_prob.setValue(0.1)
        mutation_layout.addRow("Mutation Probability:", self.mutation_prob)
        
        self.mutation_eta = QDoubleSpinBox()
        self.mutation_eta.setRange(0.1, 50.0)
        self.mutation_eta.setValue(20.0)
        mutation_layout.addRow("Distribution Index (η):", self.mutation_eta)
        
        tabs.addTab(mutation_tab, "Mutation")
        
        layout.addWidget(tabs)
        parent_layout.addWidget(group)
        
    def _init_reference_directions_group(self, parent_layout):
        """Initialize reference directions group"""
        self.reference_directions_group = QGroupBox("Reference Directions")
        self.reference_directions_group.setVisible(False)  # Hidden by default
        layout = QFormLayout(self.reference_directions_group)
        
        # Reference direction method
        self.ref_dir_method = QComboBox()
        self.ref_dir_method.addItems([
            "Das-Dennis",
            "Multi-layer Das-Dennis",
            "Uniform Random",
            "Custom Directions"
        ])
        layout.addRow("Method:", self.ref_dir_method)
        
        # Number of reference directions
        self.n_ref_dirs = QSpinBox()
        self.n_ref_dirs.setRange(1, 1000)
        self.n_ref_dirs.setValue(91)
        layout.addRow("Number of Directions:", self.n_ref_dirs)
        
        # Partitions (for Das-Dennis)
        self.n_partitions = QSpinBox()
        self.n_partitions.setRange(1, 50)
        self.n_partitions.setValue(12)
        layout.addRow("Partitions:", self.n_partitions)
        
        # Scaling factor
        self.ref_dir_scaling = QDoubleSpinBox()
        self.ref_dir_scaling.setRange(0.1, 10.0)
        self.ref_dir_scaling.setValue(1.0)
        layout.addRow("Scaling Factor:", self.ref_dir_scaling)
        
        parent_layout.addWidget(self.reference_directions_group)
        
    def _init_termination_group(self, parent_layout):
        """Initialize termination criteria group"""
        group = QGroupBox("Termination Criteria")
        layout = QFormLayout(group)
        
        # Maximum function evaluations
        self.max_evaluations = QSpinBox()
        self.max_evaluations.setRange(100, 1000000)
        self.max_evaluations.setValue(25000)
        layout.addRow("Max Function Evaluations:", self.max_evaluations)
        
        # Convergence tolerance
        self.convergence_tol = QDoubleSpinBox()
        self.convergence_tol.setRange(1e-12, 1e-1)
        self.convergence_tol.setValue(1e-6)
        self.convergence_tol.setDecimals(10)
        layout.addRow("Convergence Tolerance:", self.convergence_tol)
        
        # Enable convergence check
        self.enable_convergence = QCheckBox("Enable convergence check")
        self.enable_convergence.setChecked(True)
        layout.addRow(self.enable_convergence)
        
        # Verbose output
        self.verbose = QCheckBox("Verbose output")
        self.verbose.setChecked(True)
        layout.addRow(self.verbose)
        
        parent_layout.addWidget(group)
        
    def _connect_signals(self):
        """Connect signals to slots"""
        self.algorithm_category.currentTextChanged.connect(self._update_algorithm_options)
        self.algorithm_name.currentTextChanged.connect(self._update_algorithm_description)
        self.algorithm_name.currentTextChanged.connect(self._update_specific_parameters)
        self.algorithm_name.currentTextChanged.connect(self._on_algorithm_changed)
        
        # Connect parameter changes
        self.population_size.valueChanged.connect(self._on_algorithm_changed)
        self.n_generations.valueChanged.connect(self._on_algorithm_changed)
        self.seed.valueChanged.connect(self._on_algorithm_changed)
        
        # Connect genetic operators
        self.crossover_operator.currentTextChanged.connect(self._on_algorithm_changed)
        self.crossover_prob.valueChanged.connect(self._on_algorithm_changed)
        self.crossover_eta.valueChanged.connect(self._on_algorithm_changed)
        self.mutation_operator.currentTextChanged.connect(self._on_algorithm_changed)
        self.mutation_prob.valueChanged.connect(self._on_algorithm_changed)
        self.mutation_eta.valueChanged.connect(self._on_algorithm_changed)
        
        # Connect reference directions
        self.ref_dir_method.currentTextChanged.connect(self._on_algorithm_changed)
        self.n_ref_dirs.valueChanged.connect(self._on_algorithm_changed)
        self.n_partitions.valueChanged.connect(self._on_algorithm_changed)
        self.ref_dir_scaling.valueChanged.connect(self._on_algorithm_changed)
        
        # Connect termination criteria
        self.max_evaluations.valueChanged.connect(self._on_algorithm_changed)
        self.convergence_tol.valueChanged.connect(self._on_algorithm_changed)
        self.enable_convergence.toggled.connect(self._on_algorithm_changed)
        self.verbose.toggled.connect(self._on_algorithm_changed)
        
    def _update_algorithm_options(self):
        """Update available algorithms based on category"""
        category = self.algorithm_category.currentText()
        self.algorithm_name.clear()
        
        algorithms = {
            "Evolutionary Algorithms": [
                ("NSGA-II", "Non-dominated Sorting Genetic Algorithm II"),
                ("NSGA-III", "Non-dominated Sorting Genetic Algorithm III"),
                ("SPEA2", "Strength Pareto Evolutionary Algorithm 2"),
                ("MOEA/D", "Multi-Objective Evolutionary Algorithm based on Decomposition")
            ],
            "Decomposition-based": [
                ("MOEA/D", "Multi-Objective Evolutionary Algorithm based on Decomposition"),
                ("MOEA/D-DE", "MOEA/D with Differential Evolution"),
                ("RVEA", "Reference Vector Guided Evolutionary Algorithm")
            ],
            "Indicator-based": [
                ("IBEA", "Indicator-Based Evolutionary Algorithm"),
                ("SMS-EMOA", "S-Metric Selection Evolutionary Multi-Objective Algorithm"),
                ("HypE", "Hypervolume-based Evolutionary Algorithm")
            ],
            "Reference Point-based": [
                ("NSGA-III", "Non-dominated Sorting Genetic Algorithm III"),
                ("RVEA", "Reference Vector Guided Evolutionary Algorithm"),
                ("A-NSGA-III", "Adaptive NSGA-III")
            ],
            "Other Algorithms": [
                ("GDE3", "Generalized Differential Evolution 3"),
                ("CTAEA", "Constrained Two-Archive Evolutionary Algorithm"),
                ("BiGE", "Bi-objective Genetic Algorithm")
            ]
        }
        
        if category in algorithms:
            for name, description in algorithms[category]:
                self.algorithm_name.addItem(name)
                
        self._update_algorithm_description()
        self._update_specific_parameters()
        
    def _update_algorithm_description(self):
        """Update algorithm description"""
        algorithm = self.algorithm_name.currentText()
        
        descriptions = {
            "NSGA-II": "Fast and elitist multi-objective genetic algorithm with non-dominated sorting and crowding distance.",
            "NSGA-III": "Extension of NSGA-II for many-objective optimization using reference directions.",
            "SPEA2": "Strength Pareto Evolutionary Algorithm with improved fitness assignment and density estimation.",
            "MOEA/D": "Decomposes multi-objective problem into scalar subproblems using weight vectors.",
            "MOEA/D-DE": "MOEA/D variant using Differential Evolution operators.",
            "RVEA": "Uses reference vectors to guide the search in many-objective optimization.",
            "IBEA": "Uses indicator functions to compare solutions directly.",
            "SMS-EMOA": "Steady-state algorithm using hypervolume indicator for selection.",
            "HypE": "Hypervolume-based algorithm with Monte Carlo sampling for high dimensions.",
            "GDE3": "Generalized Differential Evolution for multi-objective optimization.",
            "CTAEA": "Handles constraints using a two-archive approach.",
            "BiGE": "Specialized for bi-objective optimization problems.",
            "A-NSGA-III": "Adaptive version of NSGA-III with reference point adaptation."
        }
        
        description = descriptions.get(algorithm, "No description available.")
        self.algorithm_description.setPlainText(description)
        
        # Show/hide reference directions group based on algorithm
        ref_dir_algorithms = ["NSGA-III", "RVEA", "A-NSGA-III", "MOEA/D", "MOEA/D-DE"]
        self.reference_directions_group.setVisible(algorithm in ref_dir_algorithms)
        
    def _update_specific_parameters(self):
        """Update algorithm-specific parameters"""
        # Clear existing specific parameters safely
        while self.specific_params_layout.count():
            child = self.specific_params_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
                
        algorithm = self.algorithm_name.currentText()
        
        # Add algorithm-specific parameters
        if algorithm == "SPEA2":
            self._add_specific_param("Archive Size", QSpinBox, 10, 1000, 100)
        elif algorithm == "SMS-EMOA":
            self._add_specific_param("Offspring Size", QSpinBox, 1, 100, 1)
        elif algorithm == "IBEA":
            kappa_spinbox = QDoubleSpinBox()
            kappa_spinbox.setRange(0.001, 10.0)
            kappa_spinbox.setValue(0.05)
            self._add_specific_param_widget("Kappa", kappa_spinbox)
        elif algorithm in ["MOEA/D", "MOEA/D-DE"]:
            self._add_specific_param("Neighborhood Size", QSpinBox, 5, 50, 20)
            prob_spinbox = QDoubleSpinBox()
            prob_spinbox.setRange(0.0, 1.0)
            prob_spinbox.setValue(0.9)
            self._add_specific_param_widget("Neighbor Probability", prob_spinbox)
            
    def _add_specific_param(self, label, widget_type, min_val, max_val, default_val):
        """Add a specific parameter widget"""
        widget = widget_type()
        widget.setRange(min_val, max_val)
        widget.setValue(default_val)
        widget.valueChanged.connect(self._on_algorithm_changed)
        self._add_specific_param_widget(label, widget)
        
    def _add_specific_param_widget(self, label, widget):
        """Add a specific parameter widget"""
        layout = QHBoxLayout()
        label_widget = QLabel(label + ":")
        label_widget.setMinimumWidth(150)  # Set minimum width for consistent alignment
        layout.addWidget(label_widget)
        layout.addWidget(widget)
        layout.addStretch()
        
        # Create a container widget for better layout control
        container = QWidget()
        container.setLayout(layout)
        self.specific_params_layout.addWidget(container)
        
    def _on_algorithm_changed(self):
        """Handle algorithm configuration changes"""
        self.algorithm_changed.emit()
        
    def is_valid(self):
        """Check if the current algorithm configuration is valid"""
        return self.algorithm_name.currentText() != ""
        
    def get_configuration(self):
        """Get the current algorithm configuration"""
        config = {
            "category": self.algorithm_category.currentText(),
            "name": self.algorithm_name.currentText(),
            "parameters": {
                "population_size": self.population_size.value(),
                "n_generations": self.n_generations.value(),
                "seed": self.seed.value()
            },
            "crossover": {
                "operator": self.crossover_operator.currentText(),
                "probability": self.crossover_prob.value(),
                "eta": self.crossover_eta.value()
            },
            "mutation": {
                "operator": self.mutation_operator.currentText(),
                "probability": self.mutation_prob.value(),
                "eta": self.mutation_eta.value()
            },
            "termination": {
                "max_evaluations": self.max_evaluations.value(),
                "convergence_tolerance": self.convergence_tol.value(),
                "enable_convergence": self.enable_convergence.isChecked(),
                "verbose": self.verbose.isChecked()
            }
        }
        
        # Add reference directions if visible
        if self.reference_directions_group.isVisible():
            config["reference_directions"] = {
                "method": self.ref_dir_method.currentText(),
                "n_directions": self.n_ref_dirs.value(),
                "n_partitions": self.n_partitions.value(),
                "scaling": self.ref_dir_scaling.value()
            }
            
        # TODO: Add specific parameters
        
        return config
        
    def set_configuration(self, config):
        """Set the algorithm configuration"""
        if "category" in config:
            index = self.algorithm_category.findText(config["category"])
            if index >= 0:
                self.algorithm_category.setCurrentIndex(index)
                self._update_algorithm_options()  # Update options after category change
                
        if "name" in config:
            index = self.algorithm_name.findText(config["name"])
            if index >= 0:
                self.algorithm_name.setCurrentIndex(index)
                # Force update of algorithm description and visibility
                self._update_algorithm_description()
                self._update_specific_parameters()
                
        # Set reference directions configuration (after algorithm is set and visibility updated)
        if "reference_directions" in config:
            ref_dirs = config["reference_directions"]
            if "type" in ref_dirs:
                index = self.ref_dir_method.findText(ref_dirs["type"])
                if index >= 0:
                    self.ref_dir_method.setCurrentIndex(index)
            if "n_partitions" in ref_dirs:
                self.n_partitions.setValue(ref_dirs["n_partitions"])
            # Handle both n_ref_dirs and n_dim (number of objectives/dimensions)
            if "n_ref_dirs" in ref_dirs:
                self.n_ref_dirs.setValue(ref_dirs["n_ref_dirs"])
            elif "n_dim" in ref_dirs and "n_partitions" in ref_dirs:
                # Calculate number of reference directions for Das-Dennis method
                # Formula: C(n_dim + n_partitions - 1, n_partitions)
                import math
                n_dim = ref_dirs["n_dim"]
                n_partitions = ref_dirs["n_partitions"]
                try:
                    n_ref_dirs = math.comb(n_dim + n_partitions - 1, n_partitions)
                    self.n_ref_dirs.setValue(n_ref_dirs)
                except:
                    # Fallback to using n_dim if calculation fails
                    self.n_ref_dirs.setValue(n_dim * 10)  # Approximate
            elif "n_dim" in ref_dirs:
                # Fallback: use a reasonable multiple of n_dim
                self.n_ref_dirs.setValue(ref_dirs["n_dim"] * 15)
            if "scaling" in ref_dirs:
                self.ref_dir_scaling.setValue(ref_dirs["scaling"])
                
        # Set parameters
        if "parameters" in config:
            params = config["parameters"]
            if "population_size" in params:
                self.population_size.setValue(params["population_size"])
            if "n_generations" in params:
                self.n_generations.setValue(params["n_generations"])
            if "seed" in params:
                self.seed.setValue(params["seed"])
                
        # Set crossover configuration
        if "crossover" in config:
            crossover = config["crossover"]
            if "operator" in crossover:
                index = self.crossover_operator.findText(crossover["operator"])
                if index >= 0:
                    self.crossover_operator.setCurrentIndex(index)
            if "probability" in crossover:
                self.crossover_prob.setValue(crossover["probability"])
            if "eta" in crossover:
                self.crossover_eta.setValue(crossover["eta"])
                
        # Set mutation configuration
        if "mutation" in config:
            mutation = config["mutation"]
            if "operator" in mutation:
                index = self.mutation_operator.findText(mutation["operator"])
                if index >= 0:
                    self.mutation_operator.setCurrentIndex(index)
            if "probability" in mutation:
                self.mutation_prob.setValue(mutation["probability"])
            if "eta" in mutation:
                self.mutation_eta.setValue(mutation["eta"])
                
        # Set termination configuration
        if "termination" in config:
            term = config["termination"]
            if "max_evaluations" in term:
                self.max_evaluations.setValue(term["max_evaluations"])
            if "convergence_tolerance" in term:
                self.convergence_tol.setValue(term["convergence_tolerance"])
            if "enable_convergence" in term:
                self.enable_convergence.setChecked(term["enable_convergence"])
            if "verbose" in term:
                self.verbose.setChecked(term["verbose"])
        
    def clear(self):
        """Clear all algorithm settings"""
        self.algorithm_category.setCurrentIndex(0)
        self.population_size.setValue(100)
        self.n_generations.setValue(250)
        self.seed.setValue(42)
        self.crossover_prob.setValue(0.9)
        self.crossover_eta.setValue(15.0)
        self.mutation_prob.setValue(0.1)
        self.mutation_eta.setValue(20.0)
        self.max_evaluations.setValue(25000)
        self.convergence_tol.setValue(1e-6)
        self.enable_convergence.setChecked(True)
        self.verbose.setChecked(True)
