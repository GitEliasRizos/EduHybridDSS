"""
Group Decision Making Tab for Admin Interface
=============================================

This module provides group decision making functionality for admin users,
allowing them to create sessions, view user inputs, and run group analysis.
"""

import json
import numpy as np
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QTableWidget, QTableWidgetItem,
                            QTabWidget, QGroupBox, QFormLayout, QLineEdit,
                            QComboBox, QTextEdit, QMessageBox, QProgressBar,
                            QScrollArea, QFrame, QSplitter, QHeaderView,
                            QListWidget, QListWidgetItem, QDialog,
                            QDialogButtonBox, QSpinBox)
from PyQt6.QtCore import Qt, pyqtSignal, QThread
from PyQt6.QtGui import QFont, QPixmap, QIcon
from core.user_manager import UserDatabaseManager
from core.mcda import AHPAnalyzer, TOPSISAnalyzer


class SessionCreationDialog(QDialog):
    """Dialog for creating new decision making sessions"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create New Session")
        self.setFixedSize(400, 350)
        self.setModal(True)
        
        self.session_data = None
        self._init_ui()
        
    def _init_ui(self):
        """Initialize dialog UI"""
        layout = QVBoxLayout(self)
        
        # Form
        form_group = QGroupBox("Session Information")
        form_layout = QFormLayout(form_group)
        
        # Session name
        self.session_name_edit = QLineEdit()
        self.session_name_edit.setPlaceholderText("Enter session name")
        form_layout.addRow("Session Name:", self.session_name_edit)
        
        # Problem name
        self.problem_name_edit = QLineEdit()
        self.problem_name_edit.setPlaceholderText("Enter problem name")
        form_layout.addRow("Problem Name:", self.problem_name_edit)
        
        # Number of criteria
        self.num_criteria_spin = QSpinBox()
        self.num_criteria_spin.setRange(2, 10)
        self.num_criteria_spin.setValue(3)
        self.num_criteria_spin.valueChanged.connect(self._update_criteria_fields)
        form_layout.addRow("Number of Criteria:", self.num_criteria_spin)
        
        layout.addWidget(form_group)
        
        # Criteria details
        self.criteria_group = QGroupBox("Criteria Details")
        self.criteria_layout = QVBoxLayout(self.criteria_group)
        layout.addWidget(self.criteria_group)
        
        # Initial criteria fields
        self._update_criteria_fields()
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self._validate_and_accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
    def _update_criteria_fields(self):
        """Update criteria input fields based on number"""
        # Clear existing fields
        for i in reversed(range(self.criteria_layout.count())):
            child = self.criteria_layout.itemAt(i).widget()
            if child:
                child.setParent(None)
                
        # Create new fields
        self.criteria_inputs = []
        self.direction_combos = []
        
        for i in range(self.num_criteria_spin.value()):
            # Criteria row
            criteria_widget = QWidget()
            criteria_row_layout = QHBoxLayout(criteria_widget)
            criteria_row_layout.setContentsMargins(0, 0, 0, 0)
            
            # Name input
            name_edit = QLineEdit()
            name_edit.setPlaceholderText(f"Criterion {i+1} name")
            criteria_row_layout.addWidget(QLabel(f"Criterion {i+1}:"))
            criteria_row_layout.addWidget(name_edit)
            
            # Direction combo
            direction_combo = QComboBox()
            direction_combo.addItems(["Minimize", "Maximize"])
            criteria_row_layout.addWidget(direction_combo)
            
            self.criteria_inputs.append(name_edit)
            self.direction_combos.append(direction_combo)
            self.criteria_layout.addWidget(criteria_widget)
            
    def _validate_and_accept(self):
        """Validate input and accept dialog"""
        session_name = self.session_name_edit.text().strip()
        problem_name = self.problem_name_edit.text().strip()
        
        if not session_name:
            QMessageBox.warning(self, "Error", "Please enter a session name.")
            return
            
        if not problem_name:
            QMessageBox.warning(self, "Error", "Please enter a problem name.")
            return
            
        # Get criteria data
        criteria_names = []
        objectives_info = []
        
        for i, (name_edit, direction_combo) in enumerate(zip(self.criteria_inputs, self.direction_combos)):
            name = name_edit.text().strip()
            if not name:
                QMessageBox.warning(self, "Error", f"Please enter a name for criterion {i+1}.")
                return
                
            criteria_names.append(name)
            objectives_info.append({
                'name': name,
                'direction': direction_combo.currentText()
            })
            
        self.session_data = {
            'session_name': session_name,
            'problem_name': problem_name,
            'criteria_names': criteria_names,
            'objectives_info': objectives_info
        }
        
        self.accept()
        
    def get_session_data(self):
        """Get the session data"""
        return self.session_data


class GroupDecisionTab(QWidget):
    """
    Tab widget for group decision making functionality
    
    Features:
    - Session management (create, view, activate)
    - User participation monitoring
    - Input aggregation and group analysis
    - Results visualization and export
    """
    
    def __init__(self, db_manager: UserDatabaseManager, user_data: dict):
        super().__init__()
        self.db_manager = db_manager
        self.user_data = user_data
        self.current_session = None
        
        self._init_ui()
        self._refresh_sessions()
        
    def _init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Header
        header_label = QLabel("Group Decision Making Administration")
        header_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #2c3e50;")
        layout.addWidget(header_label)
        
        # Main splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(splitter)
        
        # Left panel - Session management
        self._create_session_panel(splitter)
        
        # Right panel - Session details and analysis
        self._create_analysis_panel(splitter)
        
        # Set splitter proportions
        splitter.setSizes([300, 500])
        
    def _create_session_panel(self, parent):
        """Create session management panel"""
        session_widget = QWidget()
        session_layout = QVBoxLayout(session_widget)
        
        # Session controls
        control_group = QGroupBox("Session Management")
        control_layout = QVBoxLayout(control_group)
        
        # Create session button
        create_button = QPushButton("Create New Session")
        create_button.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        create_button.clicked.connect(self._create_new_session)
        control_layout.addWidget(create_button)
        
        # Refresh button
        refresh_button = QPushButton("Refresh Sessions")
        refresh_button.clicked.connect(self._refresh_sessions)
        control_layout.addWidget(refresh_button)
        
        session_layout.addWidget(control_group)
        
        # Sessions list
        sessions_group = QGroupBox("Active Sessions")
        sessions_layout = QVBoxLayout(sessions_group)
        
        self.sessions_list = QListWidget()
        self.sessions_list.itemClicked.connect(self._on_session_selected)
        sessions_layout.addWidget(self.sessions_list)
        
        session_layout.addWidget(sessions_group)
        
        parent.addWidget(session_widget)
        
    def _create_analysis_panel(self, parent):
        """Create analysis and results panel"""
        analysis_widget = QWidget()
        analysis_layout = QVBoxLayout(analysis_widget)
        
        # Session info
        self.session_info_group = QGroupBox("Session Information")
        self.session_info_layout = QVBoxLayout(self.session_info_group)
        
        self.session_info_label = QLabel("Select a session to view details.")
        self.session_info_label.setStyleSheet("""
            QLabel {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 4px;
                padding: 15px;
            }
        """)
        self.session_info_layout.addWidget(self.session_info_label)
        
        analysis_layout.addWidget(self.session_info_group)
        
        # Participation status
        self.participation_group = QGroupBox("User Participation")
        self.participation_layout = QVBoxLayout(self.participation_group)
        
        self.participation_label = QLabel("No session selected.")
        self.participation_layout.addWidget(self.participation_label)
        
        analysis_layout.addWidget(self.participation_group)
        
        # Analysis controls
        self.analysis_controls_group = QGroupBox("Group Analysis")
        analysis_controls_layout = QHBoxLayout(self.analysis_controls_group)
        
        self.run_ahp_button = QPushButton("Run AHP Group Analysis")
        self.run_ahp_button.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                padding: 10px 15px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)
        self.run_ahp_button.clicked.connect(self._run_ahp_analysis)
        self.run_ahp_button.setEnabled(False)
        analysis_controls_layout.addWidget(self.run_ahp_button)
        
        self.run_topsis_button = QPushButton("Run TOPSIS Group Analysis")
        self.run_topsis_button.setStyleSheet("""
            QPushButton {
                background-color: #17a2b8;
                color: white;
                border: none;
                padding: 10px 15px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #138496;
            }
        """)
        self.run_topsis_button.clicked.connect(self._run_topsis_analysis)
        self.run_topsis_button.setEnabled(False)
        analysis_controls_layout.addWidget(self.run_topsis_button)
        
        analysis_layout.addWidget(self.analysis_controls_group)
        
        # Results display
        self.results_tabs = QTabWidget()
        self.results_tabs.setEnabled(False)
        
        # AHP results tab
        self.ahp_results_widget = QTextEdit()
        self.ahp_results_widget.setReadOnly(True)
        self.results_tabs.addTab(self.ahp_results_widget, "AHP Results")
        
        # TOPSIS results tab
        self.topsis_results_widget = QTextEdit()
        self.topsis_results_widget.setReadOnly(True)
        self.results_tabs.addTab(self.topsis_results_widget, "TOPSIS Results")
        
        analysis_layout.addWidget(self.results_tabs)
        
        parent.addWidget(analysis_widget)
        
    def _create_new_session(self):
        """Create a new decision making session"""
        dialog = SessionCreationDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            session_data = dialog.get_session_data()
            try:
                session_id = self.db_manager.create_session(
                    session_data['session_name'],
                    session_data['problem_name'],
                    session_data['criteria_names'],
                    session_data['objectives_info'],
                    self.user_data['id']
                )
                QMessageBox.information(self, "Success", f"Session created successfully! (ID: {session_id})")
                self._refresh_sessions()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to create session: {str(e)}")
                
    def _refresh_sessions(self):
        """Refresh sessions list"""
        self.sessions_list.clear()
        
        try:
            sessions = self.db_manager.get_active_sessions()
            for session in sessions:
                item_text = f"{session['session_name']}\n{session['problem_name']}"
                item = QListWidgetItem(item_text)
                item.setData(Qt.ItemDataRole.UserRole, session)
                self.sessions_list.addItem(item)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to refresh sessions: {str(e)}")
            
    def _on_session_selected(self, item):
        """Handle session selection"""
        session_data = item.data(Qt.ItemDataRole.UserRole)
        self.current_session = session_data
        self._update_session_display()
        
    def _update_session_display(self):
        """Update session information display"""
        if not self.current_session:
            return
            
        session = self.current_session
        
        # Update session info
        criteria_text = ", ".join(session['criteria_names'])
        objectives_text = "<br>".join([
            f"• {obj['name']}: {obj['direction']}" 
            for obj in session['objectives_info']
        ])
        
        self.session_info_label.setText(f"""
        <b>Session:</b> {session['session_name']}<br>
        <b>Problem:</b> {session['problem_name']}<br>
        <b>Created:</b> {session['created_at']}<br>
        <b>Created by:</b> {session['created_by_name']}<br>
        <b>Criteria:</b> {criteria_text}<br><br>
        <b>Objectives:</b><br>
        {objectives_text}
        """)
        
        # Update participation info
        self._update_participation_status()
        
        # Enable analysis controls
        self.run_ahp_button.setEnabled(True)
        self.run_topsis_button.setEnabled(True)
        self.results_tabs.setEnabled(True)
        
        # Load existing results if any
        self._load_existing_results()
        
    def _update_participation_status(self):
        """Update user participation status"""
        if not self.current_session:
            return
            
        try:
            participation = self.db_manager.get_session_participation(self.current_session['id'])
            
            self.participation_label.setText(f"""
            <b>Total Users:</b> {participation['total_users']}<br>
            <b>AHP Participants:</b> {participation['ahp_participants']} 
            ({participation['ahp_participation_rate']:.1f}%)<br>
            <b>TOPSIS Participants:</b> {participation['topsis_participants']} 
            ({participation['topsis_participation_rate']:.1f}%)
            """)
        except Exception as e:
            self.participation_label.setText(f"Error loading participation: {str(e)}")
            
    def _run_ahp_analysis(self):
        """Run AHP group analysis"""
        if not self.current_session:
            return
            
        try:
            # Get all AHP comparisons for this session
            comparisons = self.db_manager.get_session_ahp_comparisons(self.current_session['id'])
            
            if not comparisons:
                QMessageBox.warning(self, "Warning", "No AHP comparisons found for this session.")
                return
                
            # Aggregate matrices using geometric mean
            aggregated_matrix = self.db_manager.aggregate_ahp_matrices(comparisons)
            
            # Run AHP analysis
            ahp_analyzer = AHPAnalyzer()
            
            # Convert aggregated matrix to pairwise comparisons format
            criteria_names = self.current_session['criteria_names']
            criteria_comparisons = {}
            
            for i in range(len(criteria_names)):
                for j in range(i + 1, len(criteria_names)):
                    key = (criteria_names[i], criteria_names[j])
                    criteria_comparisons[key] = aggregated_matrix[i, j]
                    
            # Perform analysis (without alternatives - just get weights)
            weights, consistency_ratio = ahp_analyzer.calculate_weights(criteria_comparisons, criteria_names)
            
            # Format results
            results_text = f"""
<h3>AHP Group Analysis Results</h3>
<p><b>Session:</b> {self.current_session['session_name']}</p>
<p><b>Participants:</b> {len(comparisons)} users</p>
<p><b>Consistency Ratio:</b> {consistency_ratio:.4f} 
{'✅ Acceptable' if consistency_ratio < 0.1 else '❌ Poor consistency'}</p>

<h4>Aggregated Pairwise Comparison Matrix:</h4>
<table border="1" style="border-collapse: collapse;">
<tr><th></th>"""
            
            for name in criteria_names:
                results_text += f"<th>{name}</th>"
            results_text += "</tr>"
            
            for i, name in enumerate(criteria_names):
                results_text += f"<tr><th>{name}</th>"
                for j in range(len(criteria_names)):
                    results_text += f"<td>{aggregated_matrix[i, j]:.4f}</td>"
                results_text += "</tr>"
            results_text += "</table>"
            
            results_text += "<h4>Criteria Weights:</h4><ul>"
            for name, weight in zip(criteria_names, weights):
                results_text += f"<li><b>{name}:</b> {weight:.4f} ({weight*100:.1f}%)</li>"
            results_text += "</ul>"
            
            results_text += f"""
<h4>Individual User Matrices:</h4>
"""
            for username, matrix in comparisons.items():
                results_text += f"<p><b>{username}:</b></p>"
                results_text += "<table border='1' style='border-collapse: collapse; font-size: 10px;'>"
                for i, row in enumerate(matrix):
                    results_text += "<tr>"
                    for val in row:
                        results_text += f"<td>{val:.3f}</td>"
                    results_text += "</tr>"
                results_text += "</table><br>"
            
            self.ahp_results_widget.setHtml(results_text)
            
            # Save results to database
            self.db_manager.save_group_result(
                self.current_session['id'],
                'ahp',
                {
                    'aggregated_matrix': aggregated_matrix.tolist(),
                    'weights': weights.tolist(),
                    'consistency_ratio': consistency_ratio,
                    'participants': list(comparisons.keys())
                },
                weights.tolist(),
                list(range(len(weights))),  # Rankings not applicable for weights
                self.user_data['id']
            )
            
            QMessageBox.information(self, "Success", "AHP group analysis completed successfully!")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"AHP analysis failed: {str(e)}")
            
    def _run_topsis_analysis(self):
        """Run TOPSIS group analysis"""
        if not self.current_session:
            return
            
        try:
            # Get all TOPSIS weights for this session
            weights_dict = self.db_manager.get_session_topsis_weights(self.current_session['id'])
            
            if not weights_dict:
                QMessageBox.warning(self, "Warning", "No TOPSIS weights found for this session.")
                return
                
            # Aggregate weights using arithmetic mean
            aggregated_weights = self.db_manager.aggregate_topsis_weights(weights_dict)
            
            # Format results
            criteria_names = self.current_session['criteria_names']
            
            results_text = f"""
<h3>TOPSIS Group Analysis Results</h3>
<p><b>Session:</b> {self.current_session['session_name']}</p>
<p><b>Participants:</b> {len(weights_dict)} users</p>

<h4>Aggregated Criteria Weights:</h4>
<ul>"""
            
            for name, weight in zip(criteria_names, aggregated_weights):
                results_text += f"<li><b>{name}:</b> {weight:.4f} ({weight*100:.1f}%)</li>"
            results_text += "</ul>"
            
            results_text += """
<h4>Individual User Weights:</h4>
<table border="1" style="border-collapse: collapse;">
<tr><th>User</th>"""
            
            for name in criteria_names:
                results_text += f"<th>{name}</th>"
            results_text += "</tr>"
            
            for username, weights in weights_dict.items():
                results_text += f"<tr><th>{username}</th>"
                for weight in weights:
                    results_text += f"<td>{weight:.4f}</td>"
                results_text += "</tr>"
            results_text += "</table>"
            
            results_text += f"<p><i>Note: These weights can be used with the alternatives in the main MCDA analysis.</i></p>"
            
            self.topsis_results_widget.setHtml(results_text)
            
            # Save results to database
            self.db_manager.save_group_result(
                self.current_session['id'],
                'topsis',
                {
                    'aggregated_weights': aggregated_weights,
                    'individual_weights': weights_dict,
                    'participants': list(weights_dict.keys())
                },
                aggregated_weights,
                list(range(len(aggregated_weights))),  # Rankings not applicable for weights
                self.user_data['id']
            )
            
            QMessageBox.information(self, "Success", "TOPSIS group analysis completed successfully!")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"TOPSIS analysis failed: {str(e)}")
            
    def _load_existing_results(self):
        """Load existing analysis results if available"""
        if not self.current_session:
            return
            
        try:
            # Load AHP results
            ahp_results = self.db_manager.get_group_results(self.current_session['id'], 'ahp')
            if ahp_results:
                # Display existing AHP results
                self.ahp_results_widget.setPlainText(f"Previous AHP analysis found (computed {ahp_results['computed_at']} by {ahp_results['computed_by']})")
                
            # Load TOPSIS results
            topsis_results = self.db_manager.get_group_results(self.current_session['id'], 'topsis')
            if topsis_results:
                # Display existing TOPSIS results
                self.topsis_results_widget.setPlainText(f"Previous TOPSIS analysis found (computed {topsis_results['computed_at']} by {topsis_results['computed_by']})")
                
        except Exception as e:
            print(f"Error loading existing results: {e}")


if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)
    
    # Test data
    user_data = {
        'id': 1,
        'username': 'admin',
        'full_name': 'Administrator',
        'role': 'admin'
    }
    
    db_manager = UserDatabaseManager()
    
    widget = GroupDecisionTab(db_manager, user_data)
    widget.show()
    
    sys.exit(app.exec())