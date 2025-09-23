"""
Session Creation Dialog

Custom dialog for creating group decision sessions with description input.
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                            QLineEdit, QTextEdit, QPushButton, QFormLayout,
                            QGroupBox, QMessageBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class SessionCreationDialog(QDialog):
    """
    Dialog for creating new group decision sessions with custom description
    """
    
    def __init__(self, parent=None, suggested_name="", current_session_count=0):
        super().__init__(parent)
        self.session_name = ""
        self.problem_description = ""
        
        self.setWindowTitle("Create Group Decision Session")
        self.setModal(True)
        self.setMinimumSize(600, 600)
        
        self._init_ui(suggested_name, current_session_count)
        
    def _init_ui(self, suggested_name, current_session_count):
        """Initialize the user interface"""
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Create New Group Decision Session")
        title.setFont(QFont("", 14, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Explanation
        explanation = QLabel("""
        Create a group decision session to allow multiple users to provide their preferences
        on optimization results. This will enable collaborative multi-criteria decision analysis.
        """)
        explanation.setWordWrap(True)
        explanation.setStyleSheet("""
            QLabel {
                background-color: #542263;
                border: 1px solid #542263;
                border-radius: 4px;
                padding: 10px;
                margin: 10px 0;
            }
        """)
        layout.addWidget(explanation)
        
        # Session Details Group
        details_group = QGroupBox("Session Details")
        details_layout = QFormLayout(details_group)
        
        # Session Name
        self.session_name_input = QLineEdit()
        self.session_name_input.setPlaceholderText("Enter a unique session name")
        if suggested_name:
            self.session_name_input.setText(suggested_name)
        else:
            self.session_name_input.setText(f"Optimization Session {current_session_count + 1}")
        details_layout.addRow("Session Name:", self.session_name_input)
        
        # Problem Description
        description_label = QLabel("Problem Description:")
        description_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText(
            "Describe the optimization problem and decision context...\n\n"
            "Example:\n"
            "Multi-objective optimization for sustainable energy system design.\n"
            "Criteria include: cost minimization, efficiency maximization, and environmental impact reduction.\n"
            "Users will evaluate different system configurations based on their preferences."
        )
        self.description_input.setMaximumHeight(150)
        details_layout.addRow(description_label, self.description_input)
        
        layout.addWidget(details_group)
        
        # Instructions
        instructions = QLabel("""
        <b>Instructions:</b>
        <ul>
        <li>Choose a descriptive session name that users will recognize</li>
        <li>Write a clear problem description explaining the decision context</li>
        <li>Include information about the criteria and what users will be evaluating</li>
        <li>The description will help users understand the problem before making comparisons</li>
        </ul>
        """)
        instructions.setWordWrap(True)
        instructions.setStyleSheet("""
            QLabel {
                background-color: #542263;
                border: 1px solid #542263;
                border-radius: 4px;
                padding: 10px;
                margin: 10px 0;
            }
        """)
        layout.addWidget(instructions)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        self.create_button = QPushButton("Create Session")
        self.create_button.setDefault(True)
        self.create_button.setStyleSheet("""
            QPushButton {
                background-color: #542263;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #542263;
            }
        """)
        self.create_button.clicked.connect(self._validate_and_accept)
        button_layout.addWidget(self.create_button)
        
        layout.addLayout(button_layout)
        
        # Connect enter key to create button
        self.session_name_input.returnPressed.connect(self._validate_and_accept)
        
    def _validate_and_accept(self):
        """Validate input and accept dialog"""
        session_name = self.session_name_input.text().strip()
        description = self.description_input.toPlainText().strip()
        
        if not session_name:
            QMessageBox.warning(self, "Validation Error", "Session name is required.")
            self.session_name_input.setFocus()
            return
            
        if len(session_name) < 3:
            QMessageBox.warning(self, "Validation Error", "Session name must be at least 3 characters long.")
            self.session_name_input.setFocus()
            return
            
        if not description:
            QMessageBox.warning(self, "Validation Error", "Problem description is required.")
            self.description_input.setFocus()
            return
            
        if len(description) < 10:
            QMessageBox.warning(self, "Validation Error", "Problem description must be at least 10 characters long.")
            self.description_input.setFocus()
            return
        
        # Store values
        self.session_name = session_name
        self.problem_description = description
        
        self.accept()
        
    def get_session_data(self):
        """Get the session creation data"""
        return {
            'session_name': self.session_name,
            'problem_description': self.problem_description
        }