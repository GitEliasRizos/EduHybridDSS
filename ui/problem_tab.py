"""
Problem Definition Tab - Multi-Objective Optimization Problem Configuration

This module provides a comprehensive user interface for defining multi-objective 
optimization problems. It enables users to specify decision variables, objective 
functions, and constraints through an intuitive tabular interface with integrated 
validation and export capabilities.

Core Functionality:
- Variable Definition: Configure decision variables with bounds, types, and constraints
- Objective Function Specification: Define mathematical expressions for optimization targets
- Constraint Management: Set equality and inequality constraints with validation
- Problem Validation: Real-time validation of mathematical expressions and configurations
- Configuration Export: Save/load problem definitions in standardized JSON format

Architecture:
The interface is organized into logical groups with tables for efficient
data entry and management:

Components:
- Problem Information: Metadata, description, and documentation
- Decision Variables: Variable definitions with type, bounds, and properties
- Objective Functions: Mathematical expressions with optimization direction
- Constraint Definitions: Equality and inequality constraint specifications
- Problem Validation: Real-time syntax and mathematical validation
- Export Controls: Configuration save/load and problem serialization

Supported Variable Types:
- Continuous: Real-valued variables with floating-point precision
- Integer: Discrete integer variables with specified ranges
- Binary: Boolean decision variables (0/1 or True/False)
- Categorical: Discrete choice variables from predefined sets

Mathematical Expression Support:
- Standard mathematical operators and functions
- NumPy function compatibility for advanced mathematical operations
- Variable referencing with automatic dependency resolution
- Real-time syntax validation and error reporting

Integration:
The tab interfaces with the core problem management system to generate
PyMOO-compatible problem instances for optimization execution.

Author: Elias Rizos [it21490]
Version: 1.3.2
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
                            QGroupBox, QLineEdit, QTextEdit, QSpinBox,
                            QDoubleSpinBox, QComboBox, QPushButton, QTableWidget,
                            QTableWidgetItem, QHeaderView, QMessageBox, QSplitter,
                            QTabWidget, QScrollArea, QLabel)
from PyQt6.QtCore import Qt, pyqtSignal  # Communication system
import json  # For saving/loading problem descriptions


class ProblemTab(QWidget):
    """
    Widget for defining optimization problems
    
    This class provides a comprehensive interface for users to specify their
    optimization problems including variables, objectives, and constraints.
    The interface is organized into logical groups with tables for easy
    manipulation of problem components.
    
    Key Responsibilities:
    - Collect variable definitions (names, types, bounds)
    - Gather objective function expressions and settings
    - Handle constraint specifications  
    - Validate problem configuration completeness
    - Provide real-time feedback on syntax errors
    - Support problem import/export functionality
    
    The tab uses a scrollable layout to accommodate problems with many
    variables or constraints, and provides immediate validation feedback
    to help users create valid problem definitions.
    
    UI Organization:
    - Problem Information: Basic metadata and description
    - Variables Table: Decision variable specifications  
    - Objectives Table: Objective function definitions
    - Constraints Table: Constraint expressions
    
    Attributes:
        problem_changed (pyqtSignal): Emitted when problem configuration changes
    """
    
    # Signal emitted when any aspect of the problem configuration changes
    # This allows other components to react to problem updates in real-time
    problem_changed = pyqtSignal()
    
    def __init__(self):
        """
        Initialize the ProblemTab widget
        
        Sets up the complete user interface including all tables, forms,
        and controls for problem definition. Also connects signals for
        real-time problem validation and change notification.
        """
        super().__init__()
        self._init_ui()          # Create all UI components
        self._connect_signals()  # Wire up signal-slot connections
        
    def _init_ui(self):
        """
        Initialize the user interface layout and components
        
        Creates a scrollable interface with four main sections:
        1. Problem Information - basic metadata
        2. Variables - decision variable specifications
        3. Objectives - objective function definitions  
        4. Constraints - constraint expressions
        
        Uses QScrollArea to handle problems with many components.
        """
        layout = QVBoxLayout(self)
        
        # Create scroll area to handle large problem definitions
        # This ensures the interface remains usable even with many variables/constraints
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        
        # Initialize each problem definition section in logical order
        self._init_problem_info_group(scroll_layout)    # Basic problem info
        self._init_variables_group(scroll_layout)       # Decision variables
        self._init_objectives_group(scroll_layout)      # Objective functions
        self._init_constraints_group(scroll_layout)     # Constraints
        
        # Configure scroll area for proper content display
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)  # Allow content to resize with window
        layout.addWidget(scroll_area)
        
    def _init_problem_info_group(self, parent_layout):
        """
        Initialize the problem information section
        
        Creates form fields for basic problem metadata including:
        - Problem name and description
        - Problem type and category
        - Author and creation date information
        - Notes and documentation fields
        
        Args:
            parent_layout: The parent layout to add this group to
        """
        """Initialize problem information group"""
        group = QGroupBox("Problem Information")
        layout = QFormLayout(group)
        
        # Problem name
        self.problem_name = QLineEdit()
        self.problem_name.setPlaceholderText("Enter problem name")
        layout.addRow("Name:", self.problem_name)
        
        # Problem description
        self.problem_description = QTextEdit()
        self.problem_description.setMaximumHeight(80)
        self.problem_description.setPlaceholderText("Enter problem description (optional)")
        layout.addRow("Description:", self.problem_description)
        
        # Problem type
        self.problem_type = QComboBox()
        self.problem_type.addItems([
            "Custom Problem",
            "Mathematical Function",
            "Engineering Problem",
            "Multi-disciplinary Problem"
        ])
        layout.addRow("Type:", self.problem_type)
        
        parent_layout.addWidget(group)
        
    def _init_variables_group(self, parent_layout):
        """Initialize variables definition group"""
        group = QGroupBox("Decision Variables")
        layout = QVBoxLayout(group)
        
        # Controls
        controls_layout = QHBoxLayout()
        
        self.n_variables = QSpinBox()
        self.n_variables.setRange(1, 100)
        self.n_variables.setValue(2)
        controls_layout.addWidget(QLabel("Number of variables:"))
        controls_layout.addWidget(self.n_variables)
        
        self.add_variable_btn = QPushButton("Add Variable")
        self.remove_variable_btn = QPushButton("Remove Variable")
        controls_layout.addWidget(self.add_variable_btn)
        controls_layout.addWidget(self.remove_variable_btn)
        controls_layout.addStretch()
        
        layout.addLayout(controls_layout)
        
        # Variables table
        self.variables_table = QTableWidget()
        self.variables_table.setColumnCount(5)
        self.variables_table.setHorizontalHeaderLabels([
            "Name", "Type", "Lower Bound", "Upper Bound", "Initial Value"
        ])
        
        # Set column widths
        header = self.variables_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        
        layout.addWidget(self.variables_table)
        
        # Initialize with default variables
        self._update_variables_table()
        
        parent_layout.addWidget(group)
        
    def _init_objectives_group(self, parent_layout):
        """Initialize objectives definition group"""
        group = QGroupBox("Objective Functions")
        layout = QVBoxLayout(group)
        
        # Controls
        controls_layout = QHBoxLayout()
        
        self.n_objectives = QSpinBox()
        self.n_objectives.setRange(1, 10)
        self.n_objectives.setValue(2)
        controls_layout.addWidget(QLabel("Number of objectives:"))
        controls_layout.addWidget(self.n_objectives)
        
        self.add_objective_btn = QPushButton("Add Objective")
        self.remove_objective_btn = QPushButton("Remove Objective")
        controls_layout.addWidget(self.add_objective_btn)
        controls_layout.addWidget(self.remove_objective_btn)
        controls_layout.addStretch()
        
        layout.addLayout(controls_layout)
        
        # Objectives table
        self.objectives_table = QTableWidget()
        self.objectives_table.setColumnCount(4)
        self.objectives_table.setHorizontalHeaderLabels([
            "Name", "Direction", "Weight", "Function"
        ])
        
        # Set column widths
        header = self.objectives_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        
        layout.addWidget(self.objectives_table)
        
        # Initialize with default objectives
        self._update_objectives_table()
        
        parent_layout.addWidget(group)
        
    def _init_constraints_group(self, parent_layout):
        """Initialize constraints definition group"""
        group = QGroupBox("Constraints")
        layout = QVBoxLayout(group)
        
        # Controls
        controls_layout = QHBoxLayout()
        
        self.add_constraint_btn = QPushButton("Add Constraint")
        self.remove_constraint_btn = QPushButton("Remove Constraint")
        controls_layout.addWidget(self.add_constraint_btn)
        controls_layout.addWidget(self.remove_constraint_btn)
        controls_layout.addStretch()
        
        layout.addLayout(controls_layout)
        
        # Constraints table
        self.constraints_table = QTableWidget()
        self.constraints_table.setColumnCount(4)
        self.constraints_table.setHorizontalHeaderLabels([
            "Name", "Type", "Function", "Value"
        ])
        
        # Set column widths
        header = self.constraints_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        
        layout.addWidget(self.constraints_table)
        
        parent_layout.addWidget(group)
        
    def _connect_signals(self):
        """Connect signals to slots"""
        self.problem_name.textChanged.connect(self._on_problem_changed)
        self.problem_description.textChanged.connect(self._on_problem_changed)
        self.problem_type.currentTextChanged.connect(self._on_problem_changed)
        
        self.n_variables.valueChanged.connect(self._update_variables_table)
        self.add_variable_btn.clicked.connect(self._add_variable)
        self.remove_variable_btn.clicked.connect(self._remove_variable)
        
        self.n_objectives.valueChanged.connect(self._update_objectives_table)
        self.add_objective_btn.clicked.connect(self._add_objective)
        self.remove_objective_btn.clicked.connect(self._remove_objective)
        
        self.add_constraint_btn.clicked.connect(self._add_constraint)
        self.remove_constraint_btn.clicked.connect(self._remove_constraint)
        
    def _update_variables_table(self):
        """Update variables table based on number of variables"""
        n_vars = self.n_variables.value()
        current_rows = self.variables_table.rowCount()
        
        # Add or remove rows as needed
        if n_vars > current_rows:
            for i in range(current_rows, n_vars):
                self._add_variable_row(i)
        elif n_vars < current_rows:
            for i in range(current_rows - 1, n_vars - 1, -1):
                self.variables_table.removeRow(i)
                
        self._on_problem_changed()
        
    def _add_variable_row(self, row_index):
        """Add a new variable row"""
        self.variables_table.insertRow(row_index)
        
        # Name
        name_item = QTableWidgetItem(f"x{row_index + 1}")
        self.variables_table.setItem(row_index, 0, name_item)
        
        # Type combo box
        type_combo = QComboBox()
        type_combo.addItems(["Real", "Integer", "Binary"])
        type_combo.currentTextChanged.connect(self._on_problem_changed)
        self.variables_table.setCellWidget(row_index, 1, type_combo)
        
        # Lower bound
        lower_bound = QDoubleSpinBox()
        lower_bound.setRange(-1000000, 1000000)
        lower_bound.setValue(0.0)
        lower_bound.valueChanged.connect(self._on_problem_changed)
        self.variables_table.setCellWidget(row_index, 2, lower_bound)
        
        # Upper bound
        upper_bound = QDoubleSpinBox()
        upper_bound.setRange(-1000000, 1000000)
        upper_bound.setValue(1.0)
        upper_bound.valueChanged.connect(self._on_problem_changed)
        self.variables_table.setCellWidget(row_index, 3, upper_bound)
        
        # Initial value
        initial_value = QDoubleSpinBox()
        initial_value.setRange(-1000000, 1000000)
        initial_value.setValue(0.5)
        initial_value.valueChanged.connect(self._on_problem_changed)
        self.variables_table.setCellWidget(row_index, 4, initial_value)
        
    def _update_objectives_table(self):
        """Update objectives table based on number of objectives"""
        n_objs = self.n_objectives.value()
        current_rows = self.objectives_table.rowCount()
        
        # Add or remove rows as needed
        if n_objs > current_rows:
            for i in range(current_rows, n_objs):
                self._add_objective_row(i)
        elif n_objs < current_rows:
            for i in range(current_rows - 1, n_objs - 1, -1):
                self.objectives_table.removeRow(i)
                
        self._on_problem_changed()
        
    def _add_objective_row(self, row_index):
        """Add a new objective row"""
        self.objectives_table.insertRow(row_index)
        
        # Name
        name_item = QTableWidgetItem(f"f{row_index + 1}")
        self.objectives_table.setItem(row_index, 0, name_item)
        
        # Direction combo box
        direction_combo = QComboBox()
        direction_combo.addItems(["Minimize", "Maximize"])
        direction_combo.currentTextChanged.connect(self._on_problem_changed)
        self.objectives_table.setCellWidget(row_index, 1, direction_combo)
        
        # Weight
        weight_spinbox = QDoubleSpinBox()
        weight_spinbox.setRange(0.0, 10.0)
        weight_spinbox.setValue(1.0)
        weight_spinbox.setSingleStep(0.1)
        weight_spinbox.valueChanged.connect(self._on_problem_changed)
        self.objectives_table.setCellWidget(row_index, 2, weight_spinbox)
        
        # Function
        function_item = QTableWidgetItem("x1**2 + x2**2")  # Default function
        self.objectives_table.setItem(row_index, 3, function_item)
        
    def _add_variable(self):
        """Add a new variable"""
        self.n_variables.setValue(self.n_variables.value() + 1)
        
    def _remove_variable(self):
        """Remove the last variable"""
        if self.n_variables.value() > 1:
            self.n_variables.setValue(self.n_variables.value() - 1)
            
    def _add_objective(self):
        """Add a new objective"""
        self.n_objectives.setValue(self.n_objectives.value() + 1)
        
    def _remove_objective(self):
        """Remove the last objective"""
        if self.n_objectives.value() > 1:
            self.n_objectives.setValue(self.n_objectives.value() - 1)
            
    def _add_constraint(self):
        """Add a new constraint"""
        row = self.constraints_table.rowCount()
        self.constraints_table.insertRow(row)
        
        # Name
        name_item = QTableWidgetItem(f"g{row + 1}")
        self.constraints_table.setItem(row, 0, name_item)
        
        # Type combo box
        type_combo = QComboBox()
        type_combo.addItems(["≤ (Less than or equal)", "≥ (Greater than or equal)", "= (Equal to)"])
        type_combo.currentTextChanged.connect(self._on_problem_changed)
        self.constraints_table.setCellWidget(row, 1, type_combo)
        
        # Function
        function_item = QTableWidgetItem("x1 + x2")  # Default constraint
        self.constraints_table.setItem(row, 2, function_item)
        
        # Value
        value_spinbox = QDoubleSpinBox()
        value_spinbox.setRange(-1000000, 1000000)
        value_spinbox.setValue(0.0)
        value_spinbox.valueChanged.connect(self._on_problem_changed)
        self.constraints_table.setCellWidget(row, 3, value_spinbox)
        
        self._on_problem_changed()
        
    def _remove_constraint(self):
        """Remove the selected constraint"""
        current_row = self.constraints_table.currentRow()
        if current_row >= 0:
            self.constraints_table.removeRow(current_row)
            self._on_problem_changed()
        elif self.constraints_table.rowCount() > 0:
            # Remove last row if none selected
            self.constraints_table.removeRow(self.constraints_table.rowCount() - 1)
            self._on_problem_changed()
            
    def _on_problem_changed(self):
        """Handle problem configuration changes"""
        self.problem_changed.emit()
        
    def is_valid(self):
        """Check if the current problem configuration is valid"""
        # Check if problem name is provided
        if not self.problem_name.text().strip():
            return False
            
        # Check if variables are properly defined
        if self.variables_table.rowCount() == 0:
            return False
            
        # Check if objectives are properly defined
        if self.objectives_table.rowCount() == 0:
            return False
            
        # Check variable bounds
        for row in range(self.variables_table.rowCount()):
            lower_widget = self.variables_table.cellWidget(row, 2)
            upper_widget = self.variables_table.cellWidget(row, 3)
            if lower_widget and upper_widget:
                if lower_widget.value() >= upper_widget.value():
                    return False
                    
        return True
        
    def get_configuration(self):
        """
        Extract the complete problem configuration from all UI components
        
        Traverses all tables and input fields to build a comprehensive
        problem configuration dictionary. This configuration can be saved
        to file, passed to the optimization engine, or used for validation.
        
        Returns:
            dict: Complete problem configuration with structure:
                - name: Problem title/identifier
                - description: Detailed problem description  
                - type: Problem category/classification
                - variables: List of decision variable definitions
                - objectives: List of objective function definitions
                - constraints: List of constraint definitions
                
        Note:
            Each variable/objective/constraint includes all necessary parameters
            for optimization engine consumption (bounds, types, expressions, etc.)
        """
        # Build base configuration structure
        config = {
            "name": self.problem_name.text().strip(),                      # Problem identifier
            "description": self.problem_description.toPlainText().strip(), # Detailed description
            "type": self.problem_type.currentText(),                       # Problem category
            "variables": [],                                               # Decision variables
            "objectives": [],                                              # Objective functions
            "constraints": []                                              # Problem constraints
        }
        
        # Extract variable definitions from table (each row = one variable)
        for row in range(self.variables_table.rowCount()):
            var_config = {
                "name": self.variables_table.item(row, 0).text(),              # Variable name/ID
                "type": self.variables_table.cellWidget(row, 1).currentText(), # Real/Integer/Binary
                "lower_bound": self.variables_table.cellWidget(row, 2).value(),# Minimum value
                "upper_bound": self.variables_table.cellWidget(row, 3).value(),# Maximum value
                "initial_value": self.variables_table.cellWidget(row, 4).value() # Starting guess
            }
            config["variables"].append(var_config)
            
        # Extract objective function definitions from table (each row = one objective)
        for row in range(self.objectives_table.rowCount()):
            obj_config = {
                "name": self.objectives_table.item(row, 0).text(),              # Objective name
                "direction": self.objectives_table.cellWidget(row, 1).currentText(), # Min/Max
                "weight": self.objectives_table.cellWidget(row, 2).value(),     # Importance weight
                "function": self.objectives_table.item(row, 3).text()           # Math expression
            }
            config["objectives"].append(obj_config)
            
        # Extract constraint definitions from table (each row = one constraint)
        for row in range(self.constraints_table.rowCount()):
            const_config = {
                "name": self.constraints_table.item(row, 0).text(),             # Constraint name
                "type": self.constraints_table.cellWidget(row, 1).currentText(),# <=, >=, = type
                "function": self.constraints_table.item(row, 2).text(),         # Math expression
                "value": self.constraints_table.cellWidget(row, 3).value()      # Constraint bound
            }
            config["constraints"].append(const_config)
            
        return config
        
    def set_configuration(self, config):
        """
        Populate the UI with a problem configuration (typically from file load)
        
        Takes a configuration dictionary and populates all UI components
        including tables, text fields, and combo boxes. Uses delayed execution
        to ensure proper table initialization before setting values.
        
        Args:
            config: Problem configuration dict with same structure as get_configuration()
            
        Note:
            Uses QTimer.singleShot for delayed execution to handle Qt table
            initialization timing issues. This ensures tables are properly
            sized before attempting to populate them.
        """
        # Set basic problem information fields
        if "name" in config:
            self.problem_name.setText(config["name"])
        if "description" in config:
            self.problem_description.setPlainText(config["description"])
        if "type" in config:
            # Find and select the problem type in combo box
            index = self.problem_type.findText(config["type"])
            if index >= 0:
                self.problem_type.setCurrentIndex(index)
                
        # Set variables (trigger table resize, then populate with delay)
        if "variables" in config:
            variables = config["variables"]
            self.n_variables.setValue(len(variables))  # This triggers table resize
            
            # Use delayed execution to ensure table is ready before setting values
            from PyQt6.QtCore import QTimer
            QTimer.singleShot(100, lambda: self._set_variable_values(variables))
            
        # Set objectives (similar delayed approach)
        if "objectives" in config:
            objectives = config["objectives"]
            self.n_objectives.setValue(len(objectives))  # Triggers table resize
            
            # Delayed execution with slightly more time to avoid race conditions
            from PyQt6.QtCore import QTimer
            QTimer.singleShot(150, lambda: self._set_objective_values(objectives))
            
        # Set constraints (final step with most delay)
        if "constraints" in config:
            constraints = config["constraints"]
            QTimer.singleShot(200, lambda: self._set_constraint_values(constraints))
            
    def _set_variable_values(self, variables):
        """Set values in the variables table"""
        for row, var in enumerate(variables):
            if row < self.variables_table.rowCount():
                # Set name
                if "name" in var:
                    self.variables_table.item(row, 0).setText(var["name"])
                    
                # Set type
                if "type" in var:
                    type_widget = self.variables_table.cellWidget(row, 1)
                    if type_widget:
                        index = type_widget.findText(var["type"])
                        if index >= 0:
                            type_widget.setCurrentIndex(index)
                            
                # Set bounds and initial value
                if "lower_bound" in var:
                    lower_widget = self.variables_table.cellWidget(row, 2)
                    if lower_widget:
                        lower_widget.setValue(var["lower_bound"])
                        
                if "upper_bound" in var:
                    upper_widget = self.variables_table.cellWidget(row, 3)
                    if upper_widget:
                        upper_widget.setValue(var["upper_bound"])
                        
                if "initial_value" in var:
                    initial_widget = self.variables_table.cellWidget(row, 4)
                    if initial_widget:
                        initial_widget.setValue(var["initial_value"])
                        
    def _set_objective_values(self, objectives):
        """Set values in the objectives table"""
        for row, obj in enumerate(objectives):
            if row < self.objectives_table.rowCount():
                # Set name
                if "name" in obj:
                    self.objectives_table.item(row, 0).setText(obj["name"])
                    
                # Set direction
                if "direction" in obj:
                    direction_widget = self.objectives_table.cellWidget(row, 1)
                    if direction_widget:
                        index = direction_widget.findText(obj["direction"])
                        if index >= 0:
                            direction_widget.setCurrentIndex(index)
                            
                # Set weight
                if "weight" in obj:
                    weight_widget = self.objectives_table.cellWidget(row, 2)
                    if weight_widget:
                        weight_widget.setValue(obj["weight"])
                        
                # Set function
                if "function" in obj:
                    self.objectives_table.item(row, 3).setText(obj["function"])
                    
    def _set_constraint_values(self, constraints):
        """Set values in the constraints table"""
        # Clear existing constraints
        self.constraints_table.setRowCount(0)
        
        # Add constraints
        for const in constraints:
            self._add_constraint()
            row = self.constraints_table.rowCount() - 1
            
            # Set name
            if "name" in const:
                self.constraints_table.item(row, 0).setText(const["name"])
                
            # Set type
            if "type" in const:
                type_widget = self.constraints_table.cellWidget(row, 1)
                if type_widget:
                    index = type_widget.findText(const["type"])
                    if index >= 0:
                        type_widget.setCurrentIndex(index)
                        
            # Set function
            if "function" in const:
                self.constraints_table.item(row, 2).setText(const["function"])
                
            # Set value
            if "value" in const:
                value_widget = self.constraints_table.cellWidget(row, 3)
                if value_widget:
                    value_widget.setValue(const["value"])
        
    def clear(self):
        """Clear all problem settings"""
        self.problem_name.clear()
        self.problem_description.clear()
        self.problem_type.setCurrentIndex(0)
        self.n_variables.setValue(2)
        self.n_objectives.setValue(2)
        self.constraints_table.setRowCount(0)
