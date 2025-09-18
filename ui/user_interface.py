"""
User Interface for Regular Users - Criteria Comparison Input
===========================================================

This module provides a simplified interface for regular users to input their
criteria comparisons for AHP and TOPSIS in the group decision making system.
"""

import sys
import numpy as np
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QPushButton, QTableWidget, QTableWidgetItem,
                            QTabWidget, QGroupBox, QFormLayout, QDoubleSpinBox,
                            QComboBox, QTextEdit, QMessageBox, QProgressBar,
                            QScrollArea, QFrame, QSplitter, QHeaderView)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QPixmap, QIcon, QPalette
from core.user_manager import UserDatabaseManager


class UserInterface(QMainWindow):
    """
    Simplified interface for regular users to provide criteria comparisons
    
    Features:
    - Session selection
    - AHP pairwise comparison input
    - TOPSIS weight input
    - Submission tracking
    - User-friendly guidance
    """
    
    def __init__(self, user_data: dict, db_manager: UserDatabaseManager):
        super().__init__()
        self.user_data = user_data
        self.db_manager = db_manager
        self.current_session = None
        self.criteria_names = []
        self.objectives_info = []
        
        self.setWindowTitle(f"PyMOO GUI - User Panel ({user_data['full_name']})")
        self.setMinimumSize(800, 600)
        
        self._init_ui()
        self._refresh_sessions()
        
    def _init_ui(self):
        """Initialize the user interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        self._create_header(main_layout)
        
        # Session selection
        self._create_session_section(main_layout)
        
        # Main content area
        self.content_tabs = QTabWidget()
        self.content_tabs.setEnabled(False)  # Disabled until session selected
        main_layout.addWidget(self.content_tabs)
        
        # AHP tab
        self._create_ahp_tab()
        
        # TOPSIS tab
        self._create_topsis_tab()
        
        # Status section
        self._create_status_section(main_layout)
        
        # Footer buttons
        self._create_footer_buttons(main_layout)
        
    def _create_header(self, layout):
        """Create header section"""
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background-color: #34495e;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        header_layout = QHBoxLayout(header_frame)
        
        # Welcome text
        welcome_label = QLabel(f"Welcome, {self.user_data['full_name']}!")
        welcome_label.setStyleSheet("color: white; font-size: 18px; font-weight: bold;")
        header_layout.addWidget(welcome_label)
        
        header_layout.addStretch()
        
        # User info
        info_label = QLabel(f"Role: {self.user_data['role'].title()} | User ID: {self.user_data['username']}")
        info_label.setStyleSheet("color: #bdc3c7; font-size: 12px;")
        header_layout.addWidget(info_label)
        
        layout.addWidget(header_frame)
        
    def _create_session_section(self, layout):
        """Create session selection section"""
        session_group = QGroupBox("Select Decision Making Session")
        session_layout = QVBoxLayout(session_group)
        
        # Session selector
        selector_layout = QHBoxLayout()
        
        self.session_combo = QComboBox()
        self.session_combo.setMinimumHeight(35)
        self.session_combo.currentTextChanged.connect(self._on_session_changed)
        selector_layout.addWidget(QLabel("Session:"))
        selector_layout.addWidget(self.session_combo)
        
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self._refresh_sessions)
        selector_layout.addWidget(self.refresh_button)
        
        session_layout.addLayout(selector_layout)
        
        # Session info
        self.session_info_label = QLabel("Please select a session to begin.")
        self.session_info_label.setStyleSheet("""
            QLabel {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 4px;
                padding: 10px;
                color: #495057;
            }
        """)
        session_layout.addWidget(self.session_info_label)
        
        layout.addWidget(session_group)
        
    def _create_ahp_tab(self):
        """Create AHP comparison tab"""
        ahp_widget = QWidget()
        ahp_layout = QVBoxLayout(ahp_widget)
        
        # Instructions
        instructions = QLabel("""
        <b>AHP Pairwise Comparison Instructions:</b><br><br>
        Compare each pair of criteria using the scale below:<br>
        • <b>1</b> = Equal importance<br>
        • <b>3</b> = Moderate importance of first over second<br>
        • <b>5</b> = Strong importance of first over second<br>
        • <b>7</b> = Very strong importance of first over second<br>
        • <b>9</b> = Extreme importance of first over second<br>
        • <b>2, 4, 6, 8</b> = Intermediate values<br>
        • <b>Fractions (1/3, 1/5, etc.)</b> = Reverse importance
        """)
        instructions.setStyleSheet("""
            QLabel {
                background-color: #e8f4fd;
                border: 1px solid #bee5eb;
                border-radius: 4px;
                padding: 15px;
                font-size: 11px;
            }
        """)
        ahp_layout.addWidget(instructions)
        
        # Comparison matrix
        self.ahp_table = QTableWidget()
        self.ahp_table.setAlternatingRowColors(True)
        ahp_layout.addWidget(self.ahp_table)
        
        # AHP buttons
        ahp_button_layout = QHBoxLayout()
        
        self.ahp_auto_fill_button = QPushButton("Auto-fill Reciprocals")
        self.ahp_auto_fill_button.clicked.connect(self._auto_fill_reciprocals)
        ahp_button_layout.addWidget(self.ahp_auto_fill_button)
        
        self.ahp_reset_button = QPushButton("Reset Matrix")
        self.ahp_reset_button.clicked.connect(self._reset_ahp_matrix)
        ahp_button_layout.addWidget(self.ahp_reset_button)
        
        ahp_button_layout.addStretch()
        
        self.ahp_submit_button = QPushButton("Submit AHP Comparisons")
        self.ahp_submit_button.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        self.ahp_submit_button.clicked.connect(self._submit_ahp_comparisons)
        ahp_button_layout.addWidget(self.ahp_submit_button)
        
        ahp_layout.addLayout(ahp_button_layout)
        
        self.content_tabs.addTab(ahp_widget, "AHP Comparisons")
        
    def _create_topsis_tab(self):
        """Create TOPSIS weights tab"""
        topsis_widget = QWidget()
        topsis_layout = QVBoxLayout(topsis_widget)
        
        # Instructions
        instructions = QLabel("""
        <b>TOPSIS Weight Assignment Instructions:</b><br><br>
        Assign importance weights to each criterion:<br>
        • Weights represent the relative importance of each criterion<br>
        • Higher weights = more important criteria<br>
        • Weights will be automatically normalized to sum to 1.0<br>
        • You can use any positive numbers (e.g., 0.1-1.0 or 1-10 scale)
        """)
        instructions.setStyleSheet("""
            QLabel {
                background-color: #fff3cd;
                border: 1px solid #ffeaa7;
                border-radius: 4px;
                padding: 15px;
                font-size: 11px;
            }
        """)
        topsis_layout.addWidget(instructions)
        
        # Weights form
        self.topsis_form_widget = QWidget()
        self.topsis_form_layout = QFormLayout(self.topsis_form_widget)
        topsis_layout.addWidget(self.topsis_form_widget)
        
        # Quick preset buttons
        preset_layout = QHBoxLayout()
        preset_layout.addWidget(QLabel("Quick presets:"))
        
        equal_button = QPushButton("Equal Weights")
        equal_button.clicked.connect(self._set_equal_topsis_weights)
        preset_layout.addWidget(equal_button)
        
        first_heavy_button = QPushButton("First Criterion Heavy")
        first_heavy_button.clicked.connect(self._set_first_heavy_weights)
        preset_layout.addWidget(first_heavy_button)
        
        preset_layout.addStretch()
        topsis_layout.addLayout(preset_layout)
        
        # TOPSIS buttons
        topsis_button_layout = QHBoxLayout()
        
        self.topsis_normalize_button = QPushButton("Normalize Weights")
        self.topsis_normalize_button.clicked.connect(self._normalize_topsis_weights)
        topsis_button_layout.addWidget(self.topsis_normalize_button)
        
        self.topsis_reset_button = QPushButton("Reset Weights")
        self.topsis_reset_button.clicked.connect(self._reset_topsis_weights)
        topsis_button_layout.addWidget(self.topsis_reset_button)
        
        topsis_button_layout.addStretch()
        
        self.topsis_submit_button = QPushButton("Submit TOPSIS Weights")
        self.topsis_submit_button.setStyleSheet("""
            QPushButton {
                background-color: #17a2b8;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #138496;
            }
        """)
        self.topsis_submit_button.clicked.connect(self._submit_topsis_weights)
        topsis_button_layout.addWidget(self.topsis_submit_button)
        
        topsis_layout.addLayout(topsis_button_layout)
        
        self.content_tabs.addTab(topsis_widget, "TOPSIS Weights")
        
    def _create_status_section(self, layout):
        """Create status and progress section"""
        status_group = QGroupBox("Submission Status")
        status_layout = QVBoxLayout(status_group)
        
        self.status_label = QLabel("No session selected.")
        self.status_label.setStyleSheet("""
            QLabel {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 4px;
                padding: 10px;
                font-size: 12px;
            }
        """)
        status_layout.addWidget(self.status_label)
        
        layout.addWidget(status_group)
        
    def _create_footer_buttons(self, layout):
        """Create footer buttons"""
        footer_layout = QHBoxLayout()
        
        self.logout_button = QPushButton("Logout")
        self.logout_button.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #545b62;
            }
        """)
        self.logout_button.clicked.connect(self.close)
        footer_layout.addWidget(self.logout_button)
        
        footer_layout.addStretch()
        
        self.help_button = QPushButton("Help")
        self.help_button.clicked.connect(self._show_help)
        footer_layout.addWidget(self.help_button)
        
        layout.addLayout(footer_layout)
        
    def _refresh_sessions(self):
        """Refresh available sessions"""
        self.session_combo.clear()
        self.session_combo.addItem("-- Select Session --")
        
        sessions = self.db_manager.get_active_sessions()
        for session in sessions:
            self.session_combo.addItem(
                f"{session['session_name']} - {session['problem_name']}",
                session['id']
            )
            
    def _on_session_changed(self):
        """Handle session selection change"""
        if self.session_combo.currentIndex() == 0:
            self.current_session = None
            self.content_tabs.setEnabled(False)
            self.session_info_label.setText("Please select a session to begin.")
            self.status_label.setText("No session selected.")
            return
            
        session_id = self.session_combo.currentData()
        if session_id:
            self._load_session(session_id)
            
    def _load_session(self, session_id):
        """Load session data and setup UI"""
        sessions = self.db_manager.get_active_sessions()
        session = next((s for s in sessions if s['id'] == session_id), None)
        
        if not session:
            QMessageBox.warning(self, "Error", "Session not found.")
            return
            
        self.current_session = session
        self.criteria_names = session['criteria_names']
        self.objectives_info = session['objectives_info']
        
        # Update session info
        criteria_text = ", ".join(self.criteria_names)
        self.session_info_label.setText(
            f"<b>Session:</b> {session['session_name']}<br>"
            f"<b>Problem:</b> {session['problem_name']}<br>"
            f"<b>Criteria:</b> {criteria_text}<br>"
            f"<b>Created:</b> {session['created_at']}"
        )
        
        # Setup comparison interfaces
        self._setup_ahp_matrix()
        self._setup_topsis_weights()
        
        # Update status
        self._update_submission_status()
        
        # Enable content tabs
        self.content_tabs.setEnabled(True)
        
    def _setup_ahp_matrix(self):
        """Setup AHP comparison matrix"""
        n = len(self.criteria_names)
        self.ahp_table.setRowCount(n)
        self.ahp_table.setColumnCount(n)
        
        # Set headers
        self.ahp_table.setHorizontalHeaderLabels(self.criteria_names)
        self.ahp_table.setVerticalHeaderLabels(self.criteria_names)
        
        # Initialize matrix
        for i in range(n):
            for j in range(n):
                if i == j:
                    # Diagonal elements are always 1
                    item = QTableWidgetItem("1.0")
                    item.setFlags(Qt.ItemFlag.ItemIsEnabled)  # Not editable
                    item.setBackground(QPalette().color(QPalette.ColorRole.Light))
                else:
                    item = QTableWidgetItem("1.0")
                self.ahp_table.setItem(i, j, item)
                
        # Resize columns
        self.ahp_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
    def _setup_topsis_weights(self):
        """Setup TOPSIS weights form"""
        # Clear existing widgets
        for i in reversed(range(self.topsis_form_layout.count())):
            self.topsis_form_layout.itemAt(i).widget().setParent(None)
            
        # Create weight inputs
        self.topsis_weight_inputs = {}
        for criterion in self.criteria_names:
            spinbox = QDoubleSpinBox()
            spinbox.setRange(0.01, 100.0)
            spinbox.setValue(1.0)
            spinbox.setDecimals(3)
            spinbox.setSingleStep(0.1)
            
            self.topsis_weight_inputs[criterion] = spinbox
            self.topsis_form_layout.addRow(f"{criterion}:", spinbox)
            
    def _auto_fill_reciprocals(self):
        """Auto-fill reciprocal values in AHP matrix"""
        n = self.ahp_table.rowCount()
        
        for i in range(n):
            for j in range(i + 1, n):
                try:
                    value = float(self.ahp_table.item(i, j).text())
                    reciprocal = 1.0 / value if value != 0 else 1.0
                    self.ahp_table.item(j, i).setText(f"{reciprocal:.4f}")
                except (ValueError, ZeroDivisionError):
                    pass
                    
    def _reset_ahp_matrix(self):
        """Reset AHP matrix to default values"""
        n = self.ahp_table.rowCount()
        for i in range(n):
            for j in range(n):
                if i != j:
                    self.ahp_table.item(i, j).setText("1.0")
                    
    def _set_equal_topsis_weights(self):
        """Set equal weights for all criteria"""
        equal_weight = 1.0 / len(self.criteria_names)
        for spinbox in self.topsis_weight_inputs.values():
            spinbox.setValue(equal_weight)
            
    def _set_first_heavy_weights(self):
        """Set first criterion with heavy weight"""
        for i, spinbox in enumerate(self.topsis_weight_inputs.values()):
            if i == 0:
                spinbox.setValue(0.5)
            else:
                spinbox.setValue(0.5 / (len(self.criteria_names) - 1))
                
    def _normalize_topsis_weights(self):
        """Normalize TOPSIS weights to sum to 1"""
        weights = [spinbox.value() for spinbox in self.topsis_weight_inputs.values()]
        total = sum(weights)
        
        if total > 0:
            for spinbox, weight in zip(self.topsis_weight_inputs.values(), weights):
                spinbox.setValue(weight / total)
                
    def _reset_topsis_weights(self):
        """Reset TOPSIS weights to default"""
        for spinbox in self.topsis_weight_inputs.values():
            spinbox.setValue(1.0)
            
    def _submit_ahp_comparisons(self):
        """Submit AHP pairwise comparisons"""
        if not self.current_session:
            QMessageBox.warning(self, "Error", "No session selected.")
            return
            
        try:
            # Extract matrix from table
            n = self.ahp_table.rowCount()
            matrix = np.ones((n, n))
            
            for i in range(n):
                for j in range(n):
                    if i != j:
                        value = float(self.ahp_table.item(i, j).text())
                        matrix[i, j] = value
                        
            # Basic validation
            if np.any(matrix <= 0):
                QMessageBox.warning(self, "Error", "All comparison values must be positive.")
                return
                
            # Submit to database
            success = self.db_manager.submit_ahp_comparison(
                self.current_session['id'], 
                self.user_data['id'], 
                matrix
            )
            
            if success:
                QMessageBox.information(self, "Success", "AHP comparisons submitted successfully!")
                self._update_submission_status()
            else:
                QMessageBox.warning(self, "Error", "Failed to submit AHP comparisons.")
                
        except ValueError:
            QMessageBox.warning(self, "Error", "Please enter valid numeric values.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")
            
    def _submit_topsis_weights(self):
        """Submit TOPSIS weights"""
        if not self.current_session:
            QMessageBox.warning(self, "Error", "No session selected.")
            return
            
        try:
            # Extract weights
            weights = [spinbox.value() for spinbox in self.topsis_weight_inputs.values()]
            
            # Normalize weights
            total = sum(weights)
            if total <= 0:
                QMessageBox.warning(self, "Error", "At least one weight must be positive.")
                return
                
            weights = [w / total for w in weights]
            
            # Submit to database
            success = self.db_manager.submit_topsis_weights(
                self.current_session['id'],
                self.user_data['id'],
                weights
            )
            
            if success:
                QMessageBox.information(self, "Success", "TOPSIS weights submitted successfully!")
                self._update_submission_status()
            else:
                QMessageBox.warning(self, "Error", "Failed to submit TOPSIS weights.")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")
            
    def _update_submission_status(self):
        """Update submission status display"""
        if not self.current_session:
            return
            
        submissions = self.db_manager.get_user_submissions(
            self.current_session['id'],
            self.user_data['id']
        )
        
        ahp_status = "✅ Submitted" if submissions['has_ahp_submission'] else "❌ Not submitted"
        topsis_status = "✅ Submitted" if submissions['has_topsis_submission'] else "❌ Not submitted"
        
        ahp_time = f" ({submissions['ahp_submitted_at']})" if submissions['ahp_submitted_at'] else ""
        topsis_time = f" ({submissions['topsis_submitted_at']})" if submissions['topsis_submitted_at'] else ""
        
        self.status_label.setText(
            f"<b>AHP Comparisons:</b> {ahp_status}{ahp_time}<br>"
            f"<b>TOPSIS Weights:</b> {topsis_status}{topsis_time}"
        )
        
    def _show_help(self):
        """Show help dialog"""
        help_text = """
        <h3>PyMOO GUI - User Help</h3>
        
        <h4>Getting Started:</h4>
        <ol>
        <li>Select an active decision making session from the dropdown</li>
        <li>Provide your criteria comparisons using both methods:</li>
        <ul>
        <li><b>AHP:</b> Compare pairs of criteria using the 1-9 scale</li>
        <li><b>TOPSIS:</b> Assign importance weights to each criterion</li>
        </ul>
        <li>Submit your inputs - they will be combined with other users' inputs</li>
        <li>The admin will run the group analysis and share results</li>
        </ol>
        
        <h4>AHP Comparison Scale:</h4>
        <ul>
        <li><b>1:</b> Equal importance</li>
        <li><b>3:</b> Moderate importance</li>
        <li><b>5:</b> Strong importance</li>
        <li><b>7:</b> Very strong importance</li>
        <li><b>9:</b> Extreme importance</li>
        <li><b>2,4,6,8:</b> Intermediate values</li>
        <li><b>1/3, 1/5, etc.:</b> Reverse importance</li>
        </ul>
        
        <h4>Tips:</h4>
        <ul>
        <li>Use "Auto-fill Reciprocals" to maintain consistency in AHP</li>
        <li>TOPSIS weights are automatically normalized</li>
        <li>You can update your submissions until the admin runs the analysis</li>
        </ul>
        """
        
        QMessageBox.information(self, "Help", help_text)


if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    # Test data
    user_data = {
        'id': 1,
        'username': 'testuser',
        'full_name': 'Test User',
        'role': 'user'
    }
    
    db_manager = UserDatabaseManager()
    
    window = UserInterface(user_data, db_manager)
    window.show()
    
    sys.exit(app.exec())