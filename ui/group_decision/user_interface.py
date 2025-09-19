from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPushButton, QTabWidget, QMessageBox,
                             QLineEdit, QComboBox, QSpinBox, QTextEdit,
                             QTableWidget, QTableWidgetItem, QHeaderView,
                             QDoubleSpinBox, QFrame, QScrollArea, QGridLayout)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QPalette, QPixmap
import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.user_manager import UserDatabaseManager

class UserInterface(QMainWindow):
    """Simplified interface for regular users to input criteria comparisons"""
    
    def __init__(self, username: str, role: str = "user"):
        super().__init__()
        self.username = username
        self.role = role
        self.user_manager = UserDatabaseManager()
        
        self.setWindowTitle(f"PyMOO GUI - User Panel ({username})")
        self.setGeometry(100, 100, 800, 600)
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the user interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        
        # Welcome header
        header_frame = QFrame()
        header_frame.setFrameStyle(QFrame.Shape.Box)
        header_frame.setStyleSheet("background-color: #303030; padding: 10px;")
        header_layout = QVBoxLayout()
        
        welcome_label = QLabel(f"Welcome, {self.username}!")
        welcome_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        instruction_label = QLabel("Please provide your criteria comparisons for group decision making")
        instruction_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        instruction_label.setStyleSheet("color: #303030; margin-top: 5px;")
        
        header_layout.addWidget(welcome_label)
        header_layout.addWidget(instruction_label)
        header_frame.setLayout(header_layout)
        layout.addWidget(header_frame)
        
        # Create tab widget for different comparison methods
        self.tab_widget = QTabWidget()
        
        # AHP Comparison Tab
        self.ahp_tab = AHPUserTab(self.username, self.user_manager)
        self.tab_widget.addTab(self.ahp_tab, "AHP Comparisons")
        
        # TOPSIS Weights Tab
        self.topsis_tab = TOPSISUserTab(self.username, self.user_manager)
        self.tab_widget.addTab(self.topsis_tab, "TOPSIS Weights")
        
        layout.addWidget(self.tab_widget)
        
        # Status bar
        status_frame = QFrame()
        status_frame.setFrameStyle(QFrame.Shape.Box)
        status_frame.setStyleSheet("background-color: #303030; padding: 5px;")
        status_layout = QHBoxLayout()
        
        self.status_label = QLabel("Ready to input comparisons")
        status_layout.addWidget(self.status_label)
        
        logout_button = QPushButton("Logout")
        logout_button.clicked.connect(self.logout)
        status_layout.addWidget(logout_button)
        
        status_frame.setLayout(status_layout)
        layout.addWidget(status_frame)
        
    def logout(self):
        """Handle user logout"""
        reply = QMessageBox.question(self, "Logout", "Are you sure you want to logout?")
        if reply == QMessageBox.StandardButton.Yes:
            self.close()
            
    def update_status(self, message: str):
        """Update status message"""
        self.status_label.setText(message)

class AHPUserTab(QWidget):
    """Tab for AHP pairwise comparisons"""
    
    def __init__(self, username: str, user_manager: UserDatabaseManager):
        super().__init__()
        self.username = username
        self.user_manager = user_manager
        self.criteria_names = []
        self.comparison_widgets = {}
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup AHP comparison interface"""
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Instructions
        instructions = QLabel(
            "AHP (Analytic Hierarchy Process) Pairwise Comparisons\n"
            "Compare criteria using Saaty's 1-9 scale:\n"
            "1=Equal, 3=Moderate, 5=Strong, 7=Very Strong, 9=Extreme importance"
        )
        instructions.setStyleSheet("background-color: #303030; padding: 10px; border: 1px solid #303030;")
        layout.addWidget(instructions)
        
        # Session selection
        session_frame = QFrame()
        session_layout = QHBoxLayout()
        
        session_layout.addWidget(QLabel("Session ID:"))
        self.session_combo = QComboBox()
        self.session_combo.setEditable(True)
        self.session_combo.addItems(["session_1", "session_2", "session_3"])
        self.session_combo.currentTextChanged.connect(self.load_session_criteria)
        session_layout.addWidget(self.session_combo)
        
        load_button = QPushButton("Load Session")
        load_button.clicked.connect(self.load_session_criteria)
        session_layout.addWidget(load_button)
        
        session_frame.setLayout(session_layout)
        layout.addWidget(session_frame)
        
        # Criteria input
        criteria_frame = QFrame()
        criteria_layout = QHBoxLayout()
        
        criteria_layout.addWidget(QLabel("Enter Criteria (comma-separated):"))
        self.criteria_input = QLineEdit()
        self.criteria_input.setPlaceholderText("e.g., Cost, Quality, Time")
        self.criteria_input.setText("Cost, Quality, Time")
        criteria_layout.addWidget(self.criteria_input)
        
        setup_button = QPushButton("Setup Comparisons")
        setup_button.clicked.connect(self.setup_comparisons)
        criteria_layout.addWidget(setup_button)
        
        criteria_frame.setLayout(criteria_layout)
        layout.addWidget(criteria_frame)
        
        # Comparison matrix area (will be populated dynamically)
        self.comparison_scroll = QScrollArea()
        self.comparison_widget = QWidget()
        self.comparison_layout = QVBoxLayout()
        self.comparison_widget.setLayout(self.comparison_layout)
        self.comparison_scroll.setWidget(self.comparison_widget)
        self.comparison_scroll.setWidgetResizable(True)
        layout.addWidget(self.comparison_scroll)
        
        # Save button
        save_frame = QFrame()
        save_layout = QHBoxLayout()
        
        self.save_button = QPushButton("Save AHP Comparisons")
        self.save_button.clicked.connect(self.save_comparisons)
        self.save_button.setEnabled(False)
        save_layout.addWidget(self.save_button)
        
        self.status_label = QLabel("Enter criteria and click 'Setup Comparisons' to begin")
        save_layout.addWidget(self.status_label)
        
        save_frame.setLayout(save_layout)
        layout.addWidget(save_frame)
        
    def load_session_criteria(self):
        """Load criteria for selected session"""
        session_id = self.session_combo.currentText().strip()
        if not session_id:
            return
            
        # Try to load existing session criteria
        # For now, use default criteria
        self.criteria_input.setText("Cost, Quality, Time")
        
    def setup_comparisons(self):
        """Setup comparison matrix based on criteria"""
        criteria_text = self.criteria_input.text().strip()
        if not criteria_text:
            QMessageBox.warning(self, "Input Error", "Please enter criteria names.")
            return
            
        # Parse criteria
        self.criteria_names = [c.strip() for c in criteria_text.split(',') if c.strip()]
        
        if len(self.criteria_names) < 2:
            QMessageBox.warning(self, "Input Error", "Please enter at least 2 criteria.")
            return
            
        # Clear existing comparison widgets
        for i in reversed(range(self.comparison_layout.count())):
            self.comparison_layout.itemAt(i).widget().setParent(None)
        
        self.comparison_widgets = {}
        
        # Create comparison matrix
        n = len(self.criteria_names)
        
        # Title
        title = QLabel(f"Pairwise Comparisons for {len(self.criteria_names)} Criteria")
        title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.comparison_layout.addWidget(title)
        
        # Create grid for comparisons
        grid_widget = QWidget()
        grid_layout = QGridLayout()
        
        # Header
        grid_layout.addWidget(QLabel(""), 0, 0)
        for j, criterion in enumerate(self.criteria_names):
            label = QLabel(criterion)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
            grid_layout.addWidget(label, 0, j + 1)
        
        # Comparison rows
        for i in range(n):
            # Row header
            label = QLabel(self.criteria_names[i])
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
            grid_layout.addWidget(label, i + 1, 0)
            
            for j in range(n):
                if i == j:
                    # Diagonal - always 1
                    label = QLabel("1")
                    label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    label.setStyleSheet("background-color: #303030;")
                    grid_layout.addWidget(label, i + 1, j + 1)
                elif i < j:
                    # Upper triangle - user input
                    spinbox = QDoubleSpinBox()
                    spinbox.setRange(1.0, 9.0)
                    spinbox.setValue(1.0)
                    spinbox.setSingleStep(0.5)
                    spinbox.setDecimals(1)
                    self.comparison_widgets[(i, j)] = spinbox
                    grid_layout.addWidget(spinbox, i + 1, j + 1)
                else:
                    # Lower triangle - reciprocal (will be calculated automatically)
                    label = QLabel("1/x")
                    label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    label.setStyleSheet("background-color: #303030;")
                    self.comparison_widgets[(i, j)] = label
                    grid_layout.addWidget(label, i + 1, j + 1)
        
        grid_widget.setLayout(grid_layout)
        self.comparison_layout.addWidget(grid_widget)
        
        # Connect value changes to update reciprocals
        for (i, j), widget in self.comparison_widgets.items():
            if isinstance(widget, QDoubleSpinBox):
                widget.valueChanged.connect(self.update_reciprocals)
        
        self.save_button.setEnabled(True)
        self.status_label.setText(f"Ready to input comparisons for {len(self.criteria_names)} criteria")
        
    def update_reciprocals(self):
        """Update reciprocal values when comparisons change"""
        for (i, j), widget in self.comparison_widgets.items():
            if isinstance(widget, QDoubleSpinBox) and i < j:
                value = widget.value()
                reciprocal_widget = self.comparison_widgets.get((j, i))
                if reciprocal_widget:
                    if value != 0:
                        reciprocal_widget.setText(f"1/{value:.1f}")
                    else:
                        reciprocal_widget.setText("∞")
                        
    def save_comparisons(self):
        """Save AHP comparisons to database"""
        if not self.criteria_names:
            QMessageBox.warning(self, "Save Error", "No comparisons to save.")
            return
            
        session_id = self.session_combo.currentText().strip()
        if not session_id:
            QMessageBox.warning(self, "Save Error", "Please enter a session ID.")
            return
        
        try:
            # Build comparison matrix
            n = len(self.criteria_names)
            import numpy as np
            matrix = np.ones((n, n))
            
            for (i, j), widget in self.comparison_widgets.items():
                if isinstance(widget, QDoubleSpinBox) and i < j:
                    value = widget.value()
                    matrix[i, j] = value
                    matrix[j, i] = 1.0 / value if value != 0 else 1.0
            
            # Calculate weights using eigenvalue method
            eigenvalues, eigenvectors = np.linalg.eig(matrix)
            max_eigenvalue = np.max(eigenvalues.real)
            principal_eigenvector = eigenvectors[:, np.argmax(eigenvalues.real)].real
            weights = principal_eigenvector / np.sum(principal_eigenvector)
            
            # Calculate consistency ratio
            ci = (max_eigenvalue - n) / (n - 1) if n > 1 else 0
            ri_values = {1: 0, 2: 0, 3: 0.52, 4: 0.89, 5: 1.11, 6: 1.25, 7: 1.35, 8: 1.40, 9: 1.45}
            ri = ri_values.get(n, 1.45)
            cr = ci / ri if ri > 0 else 0
            
            # Save to database
            success = self.user_manager.save_ahp_comparison(
                self.username, session_id, self.criteria_names, matrix, weights, cr
            )
            
            if success:
                QMessageBox.information(self, "Save Successful", 
                                      f"AHP comparisons saved successfully!\n"
                                      f"Consistency Ratio: {cr:.3f}\n"
                                      f"{'Good consistency' if cr < 0.1 else 'Consider revising comparisons'}")
                self.status_label.setText(f"Saved at {session_id} - CR: {cr:.3f}")
            else:
                QMessageBox.warning(self, "Save Error", "Failed to save comparisons.")
                
        except Exception as e:
            QMessageBox.critical(self, "Save Error", f"Error saving comparisons: {str(e)}")

class TOPSISUserTab(QWidget):
    """Tab for TOPSIS weight input"""
    
    def __init__(self, username: str, user_manager: UserDatabaseManager):
        super().__init__()
        self.username = username
        self.user_manager = user_manager
        self.criteria_names = []
        self.weight_widgets = {}
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup TOPSIS weight interface"""
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Instructions
        instructions = QLabel(
            "TOPSIS Weight Assignment\n"
            "Assign weights to each criterion (will be automatically normalized to sum to 1.0)\n"
            "Higher weights indicate more important criteria"
        )
        instructions.setStyleSheet("background-color: #303030; padding: 10px; border: 1px solid #303030;")
        layout.addWidget(instructions)
        
        # Session selection
        session_frame = QFrame()
        session_layout = QHBoxLayout()
        
        session_layout.addWidget(QLabel("Session ID:"))
        self.session_combo = QComboBox()
        self.session_combo.setEditable(True)
        self.session_combo.addItems(["session_1", "session_2", "session_3"])
        session_layout.addWidget(self.session_combo)
        
        session_frame.setLayout(session_layout)
        layout.addWidget(session_frame)
        
        # Criteria input
        criteria_frame = QFrame()
        criteria_layout = QHBoxLayout()
        
        criteria_layout.addWidget(QLabel("Enter Criteria (comma-separated):"))
        self.criteria_input = QLineEdit()
        self.criteria_input.setPlaceholderText("e.g., Cost, Quality, Time")
        self.criteria_input.setText("Cost, Quality, Time")
        criteria_layout.addWidget(self.criteria_input)
        
        setup_button = QPushButton("Setup Weights")
        setup_button.clicked.connect(self.setup_weights)
        criteria_layout.addWidget(setup_button)
        
        criteria_frame.setLayout(criteria_layout)
        layout.addWidget(criteria_frame)
        
        # Weight input area
        self.weight_scroll = QScrollArea()
        self.weight_widget = QWidget()
        self.weight_layout = QVBoxLayout()
        self.weight_widget.setLayout(self.weight_layout)
        self.weight_scroll.setWidget(self.weight_widget)
        self.weight_scroll.setWidgetResizable(True)
        layout.addWidget(self.weight_scroll)
        
        # Save button
        save_frame = QFrame()
        save_layout = QHBoxLayout()
        
        self.save_button = QPushButton("Save TOPSIS Weights")
        self.save_button.clicked.connect(self.save_weights)
        self.save_button.setEnabled(False)
        save_layout.addWidget(self.save_button)
        
        self.status_label = QLabel("Enter criteria and click 'Setup Weights' to begin")
        save_layout.addWidget(self.status_label)
        
        save_frame.setLayout(save_layout)
        layout.addWidget(save_frame)
        
    def setup_weights(self):
        """Setup weight input fields"""
        criteria_text = self.criteria_input.text().strip()
        if not criteria_text:
            QMessageBox.warning(self, "Input Error", "Please enter criteria names.")
            return
            
        # Parse criteria
        self.criteria_names = [c.strip() for c in criteria_text.split(',') if c.strip()]
        
        if len(self.criteria_names) < 2:
            QMessageBox.warning(self, "Input Error", "Please enter at least 2 criteria.")
            return
            
        # Clear existing weight widgets
        for i in reversed(range(self.weight_layout.count())):
            self.weight_layout.itemAt(i).widget().setParent(None)
        
        self.weight_widgets = {}
        
        # Title
        title = QLabel(f"Weight Assignment for {len(self.criteria_names)} Criteria")
        title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.weight_layout.addWidget(title)
        
        # Create weight inputs
        for criterion in self.criteria_names:
            weight_frame = QFrame()
            weight_frame.setFrameStyle(QFrame.Shape.Box)
            weight_layout = QHBoxLayout()
            
            label = QLabel(f"{criterion}:")
            label.setMinimumWidth(100)
            weight_layout.addWidget(label)
            
            spinbox = QDoubleSpinBox()
            spinbox.setRange(0.0, 10.0)
            spinbox.setValue(1.0)
            spinbox.setSingleStep(0.1)
            spinbox.setDecimals(2)
            spinbox.setSuffix(" (will be normalized)")
            self.weight_widgets[criterion] = spinbox
            weight_layout.addWidget(spinbox)
            
            weight_frame.setLayout(weight_layout)
            self.weight_layout.addWidget(weight_frame)
        
        # Equal weights button
        equal_button = QPushButton("Set Equal Weights")
        equal_button.clicked.connect(self.set_equal_weights)
        self.weight_layout.addWidget(equal_button)
        
        self.save_button.setEnabled(True)
        self.status_label.setText(f"Ready to input weights for {len(self.criteria_names)} criteria")
        
    def set_equal_weights(self):
        """Set equal weights for all criteria"""
        for widget in self.weight_widgets.values():
            widget.setValue(1.0)
            
    def save_weights(self):
        """Save TOPSIS weights to database"""
        if not self.criteria_names:
            QMessageBox.warning(self, "Save Error", "No weights to save.")
            return
            
        session_id = self.session_combo.currentText().strip()
        if not session_id:
            QMessageBox.warning(self, "Save Error", "Please enter a session ID.")
            return
        
        try:
            # Get weights
            import numpy as np
            weights = np.array([self.weight_widgets[criterion].value() 
                              for criterion in self.criteria_names])
            
            # Normalize weights
            weights = weights / np.sum(weights)
            
            # Save to database
            success = self.user_manager.save_topsis_weights(
                self.username, session_id, self.criteria_names, weights
            )
            
            if success:
                weight_str = ", ".join([f"{name}: {weight:.3f}" 
                                      for name, weight in zip(self.criteria_names, weights)])
                QMessageBox.information(self, "Save Successful", 
                                      f"TOPSIS weights saved successfully!\n"
                                      f"Normalized weights: {weight_str}")
                self.status_label.setText(f"Saved at {session_id}")
            else:
                QMessageBox.warning(self, "Save Error", "Failed to save weights.")
                
        except Exception as e:
            QMessageBox.critical(self, "Save Error", f"Error saving weights: {str(e)}")

# Test the user interface standalone
if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)
    
    window = UserInterface("testuser", "user")
    window.show()
    
    sys.exit(app.exec())