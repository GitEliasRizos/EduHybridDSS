from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QComboBox, QTableWidget, QTableWidgetItem,
                             QTextEdit, QGroupBox, QFrame, QHeaderView, QTabWidget,
                             QMessageBox, QScrollArea, QGridLayout)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont
import sys
import os
import numpy as np

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from auth.user_manager import UserManager
from core.mcda import AHPAnalyzer, TOPSISAnalyzer

class GroupDecisionTab(QWidget):
    """Admin panel for group decision making analysis"""
    
    def __init__(self, user_manager: UserManager = None, current_user: str = "admin"):
        super().__init__()
        self.user_manager = user_manager or UserManager()
        self.current_user = current_user
        self.setup_ui()
        self.refresh_sessions()
        
    def setup_ui(self):
        """Setup the group decision interface"""
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Header
        header = QLabel("Group Decision Making Analysis")
        header.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setStyleSheet("background-color: #303030; padding: 10px; border: 2px solid #000;")
        layout.addWidget(header)
        
        # Session management
        session_frame = self.create_session_management()
        layout.addWidget(session_frame)
        
        # Analysis tabs
        self.analysis_tabs = QTabWidget()
        
        # AHP Group Analysis Tab
        self.ahp_group_tab = AHPGroupAnalysisTab(self.user_manager)
        self.analysis_tabs.addTab(self.ahp_group_tab, "AHP Group Analysis")
        
        # TOPSIS Group Analysis Tab
        self.topsis_group_tab = TOPSISGroupAnalysisTab(self.user_manager)
        self.analysis_tabs.addTab(self.topsis_group_tab, "TOPSIS Group Analysis")
        
        # User Management Tab
        self.user_mgmt_tab = UserManagementTab(self.user_manager)
        self.analysis_tabs.addTab(self.user_mgmt_tab, "User Management")
        
        layout.addWidget(self.analysis_tabs)
        
    def create_session_management(self):
        """Create session management controls"""
        frame = QGroupBox("Session Management")
        layout = QHBoxLayout()
        
        layout.addWidget(QLabel("Active Session:"))
        
        self.session_combo = QComboBox()
        self.session_combo.setEditable(True)
        self.session_combo.currentTextChanged.connect(self.on_session_changed)
        layout.addWidget(self.session_combo)
        
        refresh_button = QPushButton("Refresh")
        refresh_button.clicked.connect(self.refresh_sessions)
        layout.addWidget(refresh_button)
        
        create_button = QPushButton("Create Session")
        create_button.clicked.connect(self.create_session)
        layout.addWidget(create_button)
        
        frame.setLayout(layout)
        return frame
        
    def refresh_sessions(self):
        """Refresh the list of available sessions"""
        # Get existing sessions from database
        sessions = self.user_manager.get_group_sessions()
        
        self.session_combo.clear()
        for session in sessions:
            self.session_combo.addItem(session['session_id'])
            
        # Add some default sessions if none exist
        if not sessions:
            default_sessions = ["session_1", "session_2", "session_3"]
            self.session_combo.addItems(default_sessions)
            
    def create_session(self):
        """Create a new group decision session"""
        # For now, just add a new session to the combo box
        from PyQt6.QtWidgets import QInputDialog
        
        session_id, ok = QInputDialog.getText(self, "Create Session", "Enter session ID:")
        if ok and session_id:
            # Create session in database
            criteria_names = ["Cost", "Quality", "Time"]  # Default criteria
            success = self.user_manager.create_group_session(
                session_id, "Group Decision Problem", criteria_names, self.current_user
            )
            
            if success:
                self.session_combo.addItem(session_id)
                self.session_combo.setCurrentText(session_id)
                QMessageBox.information(self, "Session Created", f"Session '{session_id}' created successfully.")
            else:
                QMessageBox.warning(self, "Creation Failed", "Failed to create session.")
                
    def on_session_changed(self):
        """Handle session change"""
        session_id = self.session_combo.currentText()
        
        # Update all analysis tabs
        self.ahp_group_tab.set_session(session_id)
        self.topsis_group_tab.set_session(session_id)

class AHPGroupAnalysisTab(QWidget):
    """Tab for AHP group analysis"""
    
    def __init__(self, user_manager: UserManager):
        super().__init__()
        self.user_manager = user_manager
        self.current_session = ""
        self.setup_ui()
        
    def setup_ui(self):
        """Setup AHP group analysis interface"""
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Analysis controls
        controls_frame = QFrame()
        controls_layout = QHBoxLayout()
        
        self.analyze_button = QPushButton("Analyze Group AHP")
        self.analyze_button.clicked.connect(self.analyze_group_ahp)
        controls_layout.addWidget(self.analyze_button)
        
        self.export_button = QPushButton("Export Results")
        self.export_button.clicked.connect(self.export_results)
        self.export_button.setEnabled(False)
        controls_layout.addWidget(self.export_button)
        
        controls_frame.setLayout(controls_layout)
        layout.addWidget(controls_frame)
        
        # Results display
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setMaximumHeight(200)
        layout.addWidget(self.results_text)
        
        # Individual contributions table
        self.contributions_table = QTableWidget()
        layout.addWidget(self.contributions_table)
        
    def set_session(self, session_id: str):
        """Set the current session"""
        self.current_session = session_id
        self.refresh_display()
        
    def refresh_display(self):
        """Refresh the display for current session"""
        if not self.current_session:
            return
            
        # Get group data
        group_data = self.user_manager.get_group_ahp_data(self.current_session)
        
        if not group_data.get('users'):
            self.results_text.setText("No AHP comparisons found for this session.")
            self.contributions_table.setRowCount(0)
            return
            
        # Display user contributions
        self.display_user_contributions(group_data)
        
    def display_user_contributions(self, group_data):
        """Display individual user contributions"""
        users = group_data['users']
        criteria_names = group_data.get('criteria_names', [])
        weights = group_data['weights']
        consistency_ratios = group_data['consistency_ratios']
        
        # Setup table
        self.contributions_table.setRowCount(len(users))
        self.contributions_table.setColumnCount(2 + len(criteria_names))
        
        headers = ["User", "Consistency Ratio"] + criteria_names
        self.contributions_table.setHorizontalHeaderLabels(headers)
        
        # Fill table
        for i, (user, weight_vector, cr) in enumerate(zip(users, weights, consistency_ratios)):
            self.contributions_table.setItem(i, 0, QTableWidgetItem(user))
            self.contributions_table.setItem(i, 1, QTableWidgetItem(f"{cr:.3f}"))
            
            for j, weight in enumerate(weight_vector):
                self.contributions_table.setItem(i, 2 + j, QTableWidgetItem(f"{weight:.3f}"))
        
        # Auto-resize columns
        self.contributions_table.resizeColumnsToContents()
        
    def analyze_group_ahp(self):
        """Perform group AHP analysis"""
        if not self.current_session:
            QMessageBox.warning(self, "Analysis Error", "Please select a session.")
            return
            
        # Get group data
        group_data = self.user_manager.get_group_ahp_data(self.current_session)
        
        if not group_data.get('users'):
            QMessageBox.warning(self, "Analysis Error", "No AHP comparisons found for this session.")
            return
            
        try:
            # Aggregate matrices using geometric mean
            matrices = group_data['matrices']
            aggregated_matrix = self.user_manager.aggregate_ahp_matrices(matrices)
            
            # Calculate group weights using AHP
            ahp_analyzer = AHPAnalyzer()
            eigenvalues, eigenvectors = np.linalg.eig(aggregated_matrix)
            max_eigenvalue = np.max(eigenvalues.real)
            principal_eigenvector = eigenvectors[:, np.argmax(eigenvalues.real)].real
            group_weights = principal_eigenvector / np.sum(principal_eigenvector)
            
            # Calculate group consistency
            n = len(group_weights)
            ci = (max_eigenvalue - n) / (n - 1) if n > 1 else 0
            ri_values = {1: 0, 2: 0, 3: 0.52, 4: 0.89, 5: 1.11, 6: 1.25, 7: 1.35, 8: 1.40, 9: 1.45}
            ri = ri_values.get(n, 1.45)
            group_cr = ci / ri if ri > 0 else 0
            
            # Display results
            criteria_names = group_data['criteria_names']
            result_text = f"GROUP AHP ANALYSIS RESULTS\n"
            result_text += f"Session: {self.current_session}\n"
            result_text += f"Participants: {len(group_data['users'])} users\n"
            result_text += f"Group Consistency Ratio: {group_cr:.3f} ({'Good' if group_cr < 0.1 else 'Needs Review'})\n\n"
            
            result_text += "GROUP WEIGHTS:\n"
            for criterion, weight in zip(criteria_names, group_weights):
                result_text += f"  {criterion}: {weight:.3f} ({weight*100:.1f}%)\n"
            
            result_text += f"\nINDIVIDUAL CONSISTENCY RATIOS:\n"
            for user, cr in zip(group_data['users'], group_data['consistency_ratios']):
                result_text += f"  {user}: {cr:.3f}\n"
            
            self.results_text.setText(result_text)
            self.export_button.setEnabled(True)
            
        except Exception as e:
            QMessageBox.critical(self, "Analysis Error", f"Error performing group analysis: {str(e)}")
            
    def export_results(self):
        """Export analysis results"""
        # TODO: Implement export functionality
        QMessageBox.information(self, "Export", "Export functionality will be implemented.")

class TOPSISGroupAnalysisTab(QWidget):
    """Tab for TOPSIS group analysis"""
    
    def __init__(self, user_manager: UserManager):
        super().__init__()
        self.user_manager = user_manager
        self.current_session = ""
        self.setup_ui()
        
    def setup_ui(self):
        """Setup TOPSIS group analysis interface"""
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Analysis controls
        controls_frame = QFrame()
        controls_layout = QHBoxLayout()
        
        self.analyze_button = QPushButton("Analyze Group TOPSIS")
        self.analyze_button.clicked.connect(self.analyze_group_topsis)
        controls_layout.addWidget(self.analyze_button)
        
        self.export_button = QPushButton("Export Results")
        self.export_button.clicked.connect(self.export_results)
        self.export_button.setEnabled(False)
        controls_layout.addWidget(self.export_button)
        
        controls_frame.setLayout(controls_layout)
        layout.addWidget(controls_frame)
        
        # Results display
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setMaximumHeight(200)
        layout.addWidget(self.results_text)
        
        # Individual weights table
        self.weights_table = QTableWidget()
        layout.addWidget(self.weights_table)
        
    def set_session(self, session_id: str):
        """Set the current session"""
        self.current_session = session_id
        self.refresh_display()
        
    def refresh_display(self):
        """Refresh the display for current session"""
        if not self.current_session:
            return
            
        # Get group data
        group_data = self.user_manager.get_group_topsis_data(self.current_session)
        
        if not group_data.get('users'):
            self.results_text.setText("No TOPSIS weights found for this session.")
            self.weights_table.setRowCount(0)
            return
            
        # Display user weights
        self.display_user_weights(group_data)
        
    def display_user_weights(self, group_data):
        """Display individual user weights"""
        users = group_data['users']
        criteria_names = group_data.get('criteria_names', [])
        weights = group_data['weights']
        
        # Setup table
        self.weights_table.setRowCount(len(users))
        self.weights_table.setColumnCount(1 + len(criteria_names))
        
        headers = ["User"] + criteria_names
        self.weights_table.setHorizontalHeaderLabels(headers)
        
        # Fill table
        for i, (user, weight_vector) in enumerate(zip(users, weights)):
            self.weights_table.setItem(i, 0, QTableWidgetItem(user))
            
            for j, weight in enumerate(weight_vector):
                self.weights_table.setItem(i, 1 + j, QTableWidgetItem(f"{weight:.3f}"))
        
        # Auto-resize columns
        self.weights_table.resizeColumnsToContents()
        
    def analyze_group_topsis(self):
        """Perform group TOPSIS analysis"""
        if not self.current_session:
            QMessageBox.warning(self, "Analysis Error", "Please select a session.")
            return
            
        # Get group data
        group_data = self.user_manager.get_group_topsis_data(self.current_session)
        
        if not group_data.get('users'):
            QMessageBox.warning(self, "Analysis Error", "No TOPSIS weights found for this session.")
            return
            
        try:
            # Aggregate weights using arithmetic mean
            weights_list = group_data['weights']
            group_weights = self.user_manager.aggregate_topsis_weights(weights_list)
            
            # Display results
            criteria_names = group_data['criteria_names']
            result_text = f"GROUP TOPSIS ANALYSIS RESULTS\n"
            result_text += f"Session: {self.current_session}\n"
            result_text += f"Participants: {len(group_data['users'])} users\n\n"
            
            result_text += "GROUP WEIGHTS (Normalized):\n"
            for criterion, weight in zip(criteria_names, group_weights):
                result_text += f"  {criterion}: {weight:.3f} ({weight*100:.1f}%)\n"
            
            result_text += f"\nWEIGHT STATISTICS:\n"
            weights_matrix = np.vstack(weights_list)
            for i, criterion in enumerate(criteria_names):
                col_weights = weights_matrix[:, i]
                std_dev = np.std(col_weights)
                result_text += f"  {criterion}: mean={np.mean(col_weights):.3f}, std={std_dev:.3f}\n"
            
            self.results_text.setText(result_text)
            self.export_button.setEnabled(True)
            
        except Exception as e:
            QMessageBox.critical(self, "Analysis Error", f"Error performing group analysis: {str(e)}")
            
    def export_results(self):
        """Export analysis results"""
        # TODO: Implement export functionality
        QMessageBox.information(self, "Export", "Export functionality will be implemented.")

class UserManagementTab(QWidget):
    """Tab for user management"""
    
    def __init__(self, user_manager: UserManager):
        super().__init__()
        self.user_manager = user_manager
        self.setup_ui()
        self.refresh_users()
        
    def setup_ui(self):
        """Setup user management interface"""
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Controls
        controls_frame = QFrame()
        controls_layout = QHBoxLayout()
        
        refresh_button = QPushButton("Refresh Users")
        refresh_button.clicked.connect(self.refresh_users)
        controls_layout.addWidget(refresh_button)
        
        controls_frame.setLayout(controls_layout)
        layout.addWidget(controls_frame)
        
        # Users table
        self.users_table = QTableWidget()
        self.users_table.setColumnCount(3)
        self.users_table.setHorizontalHeaderLabels(["Username", "Role", "Created"])
        layout.addWidget(self.users_table)
        
    def refresh_users(self):
        """Refresh the users list"""
        users = self.user_manager.get_all_users()
        
        self.users_table.setRowCount(len(users))
        
        for i, user in enumerate(users):
            self.users_table.setItem(i, 0, QTableWidgetItem(user['username']))
            self.users_table.setItem(i, 1, QTableWidgetItem(user['role']))
            self.users_table.setItem(i, 2, QTableWidgetItem(user['created_at']))
        
        self.users_table.resizeColumnsToContents()

# Test the group decision tab standalone
if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication, QMainWindow
    import sys
    
    app = QApplication(sys.argv)
    
    window = QMainWindow()
    tab = GroupDecisionTab()
    window.setCentralWidget(tab)
    window.setWindowTitle("Group Decision Making - Test")
    window.resize(1000, 700)
    window.show()
    
    sys.exit(app.exec())