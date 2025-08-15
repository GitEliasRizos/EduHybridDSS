"""
Problem Definition Tab - Define optimization problems
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
                            QGroupBox, QLineEdit, QTextEdit, QSpinBox,
                            QDoubleSpinBox, QComboBox, QPushButton, QTableWidget,
                            QTableWidgetItem, QHeaderView, QMessageBox, QSplitter,
                            QTabWidget, QScrollArea, QLabel)
from PyQt6.QtCore import Qt, pyqtSignal
import json


class ProblemTab(QWidget):
    """Widget for defining optimization problems"""
    
    # Signal emitted when problem configuration changes
    problem_changed = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self._init_ui()
        self._connect_signals()
        
    def _init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout(self)
        
        # Create scroll area for the content
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        
        # Problem Information Group
        self._init_problem_info_group(scroll_layout)
        
        # Variables Group
        self._init_variables_group(scroll_layout)
        
        # Objectives Group
        self._init_objectives_group(scroll_layout)
        
        # Constraints Group
        self._init_constraints_group(scroll_layout)
        
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        layout.addWidget(scroll_area)
        
    def _init_problem_info_group(self, parent_layout):
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
        """Get the current problem configuration"""
        config = {
            "name": self.problem_name.text(),
            "description": self.problem_description.toPlainText(),
            "type": self.problem_type.currentText(),
            "variables": [],
            "objectives": [],
            "constraints": []
        }
        
        # Get variables
        for row in range(self.variables_table.rowCount()):
            var_config = {
                "name": self.variables_table.item(row, 0).text(),
                "type": self.variables_table.cellWidget(row, 1).currentText(),
                "lower_bound": self.variables_table.cellWidget(row, 2).value(),
                "upper_bound": self.variables_table.cellWidget(row, 3).value(),
                "initial_value": self.variables_table.cellWidget(row, 4).value()
            }
            config["variables"].append(var_config)
            
        # Get objectives
        for row in range(self.objectives_table.rowCount()):
            obj_config = {
                "name": self.objectives_table.item(row, 0).text(),
                "direction": self.objectives_table.cellWidget(row, 1).currentText(),
                "weight": self.objectives_table.cellWidget(row, 2).value(),
                "function": self.objectives_table.item(row, 3).text()
            }
            config["objectives"].append(obj_config)
            
        # Get constraints
        for row in range(self.constraints_table.rowCount()):
            const_config = {
                "name": self.constraints_table.item(row, 0).text(),
                "type": self.constraints_table.cellWidget(row, 1).currentText(),
                "function": self.constraints_table.item(row, 2).text(),
                "value": self.constraints_table.cellWidget(row, 3).value()
            }
            config["constraints"].append(const_config)
            
        return config
        
    def set_configuration(self, config):
        """Set the problem configuration"""
        if "name" in config:
            self.problem_name.setText(config["name"])
        if "description" in config:
            self.problem_description.setPlainText(config["description"])
        if "type" in config:
            index = self.problem_type.findText(config["type"])
            if index >= 0:
                self.problem_type.setCurrentIndex(index)
                
        # Set variables
        if "variables" in config:
            variables = config["variables"]
            self.n_variables.setValue(len(variables))
            
            # Wait for table to be updated, then set values
            from PyQt6.QtCore import QTimer
            QTimer.singleShot(100, lambda: self._set_variable_values(variables))
            
        # Set objectives
        if "objectives" in config:
            objectives = config["objectives"]
            self.n_objectives.setValue(len(objectives))
            
            # Wait for table to be updated, then set values
            from PyQt6.QtCore import QTimer
            QTimer.singleShot(150, lambda: self._set_objective_values(objectives))
            
        # Set constraints
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
