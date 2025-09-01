"""
MCDA Tab - Multi-Criteria Decision Analysis Interface

This module provides a GUI interface for applying AHP (Analytic Hierarchy Process)
and TOPSIS (Technique for Order of Preference by Similarity to Ideal Solution) 
methods to analyze PyMOO optimization results.

Key Features:
- Method selection (AHP vs TOPSIS)
- Interactive pairwise comparison matrix for AHP
- Weight configuration for TOPSIS
- Results visualization and ranking tables
- Export functionality for analysis results
- Integration with PyMOO optimization results

The tab is activated after optimization is complete and provides comprehensive
multi-criteria decision analysis capabilities.

Author: Elias Rizos [it21490]
Version: 1.0.0
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, 
                            QRadioButton, QButtonGroup, QPushButton, QTableWidget,
                            QTableWidgetItem, QLabel, QSpinBox, QDoubleSpinBox,
                            QTabWidget, QTextEdit, QHeaderView, QMessageBox,
                            QFileDialog, QProgressBar, QComboBox, QCheckBox,
                            QScrollArea, QGridLayout, QFrame, QSplitter)

from PyQt6.QtCore import Qt, pyqtSignal, QThread, pyqtSlot
from PyQt6.QtGui import QFont, QPixmap, QPainter, QColor

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
import json

try:
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.figure import Figure
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

from core.mcda import MCDAManager, AHPAnalyzer, TOPSISAnalyzer


class PairwiseComparisonWidget(QWidget):
    """Widget for creating AHP pairwise comparison matrices"""
    
    def __init__(self, criteria_names: List[str], parent=None):
        super().__init__(parent)
        self.criteria_names = criteria_names
        self.comparison_widgets = {}
        self.init_ui()
        
    def init_ui(self):
        """Initialize the pairwise comparison interface"""
        layout = QVBoxLayout()
        
        # Instructions
        instructions = QLabel(
            "Compare criteria pairwise using the 1-9 scale:\n"
            "1 = Equal importance, 3 = Moderate importance, 5 = Strong importance\n"
            "7 = Very strong importance, 9 = Extreme importance\n"
            "Use decimals (e.g., 0.5, 0.33) to indicate the second criterion is more important"
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet("QLabel { background-color: #303030; padding: 10px; border-radius: 5px; }")
        layout.addWidget(instructions)
        
        # Comparison matrix
        scroll_area = QScrollArea()
        comparison_widget = QWidget()
        comparison_layout = QGridLayout(comparison_widget)
        
        # Create comparison inputs
        row = 0
        for i, crit1 in enumerate(self.criteria_names):
            for j, crit2 in enumerate(self.criteria_names):
                if i < j:  # Only upper triangle
                    label = QLabel(f"{crit1} vs {crit2}:")
                    comparison_layout.addWidget(label, row, 0)
                    
                    spinbox = QDoubleSpinBox()
                    spinbox.setRange(0.11, 9.0)
                    spinbox.setValue(1.0)
                    spinbox.setDecimals(2)
                    spinbox.setSingleStep(0.1)
                    comparison_layout.addWidget(spinbox, row, 1)
                    
                    explanation = QLabel("Equal importance")
                    explanation.setStyleSheet("QLabel { color: #666; font-style: italic; }")
                    comparison_layout.addWidget(explanation, row, 2)
                    
                    # Update explanation when value changes
                    spinbox.valueChanged.connect(lambda v, lbl=explanation: self._update_explanation(v, lbl))
                    
                    self.comparison_widgets[(crit1, crit2)] = spinbox
                    row += 1
                    
        scroll_area.setWidget(comparison_widget)
        layout.addWidget(scroll_area)
        self.setLayout(layout)
        
    def _update_explanation(self, value: float, label: QLabel):
        """Update explanation text based on comparison value"""
        if value == 1.0:
            explanation = "Equal importance"
        elif 1.0 < value <= 2.0:
            explanation = "Slight to moderate importance"
        elif 2.0 < value <= 4.0:
            explanation = "Moderate to strong importance"  
        elif 4.0 < value <= 6.0:
            explanation = "Strong to very strong importance"
        elif 6.0 < value <= 8.0:
            explanation = "Very strong to extreme importance"
        elif value > 8.0:
            explanation = "Extreme importance"
        elif 0.5 <= value < 1.0:
            explanation = "Second criterion more important"
        else:
            explanation = "Second criterion much more important"
            
        label.setText(explanation)
        
    def get_comparisons(self) -> Dict[Tuple[str, str], float]:
        """Get current pairwise comparison values"""
        comparisons = {}
        for (crit1, crit2), widget in self.comparison_widgets.items():
            comparisons[(crit1, crit2)] = widget.value()
        return comparisons


class WeightConfigurationWidget(QWidget):
    """Widget for configuring TOPSIS criteria weights"""
    
    def __init__(self, criteria_names: List[str], parent=None):
        super().__init__(parent)
        self.criteria_names = criteria_names
        self.weight_widgets = {}
        self.init_ui()
        
    def init_ui(self):
        """Initialize weight configuration interface"""
        layout = QVBoxLayout()
        
        # Instructions
        instructions = QLabel(
            "Set the importance weights for each criterion (0-1 scale).\n"
            "Weights will be automatically normalized to sum to 1."
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet("QLabel { background-color: #f0f8ff; padding: 10px; border-radius: 5px; }")
        layout.addWidget(instructions)
        
        # Weight inputs
        weights_layout = QGridLayout()
        
        for i, criterion in enumerate(self.criteria_names):
            label = QLabel(f"{criterion}:")
            weights_layout.addWidget(label, i, 0)
            
            spinbox = QDoubleSpinBox()
            spinbox.setRange(0.0, 1.0)
            spinbox.setValue(1.0 / len(self.criteria_names))  # Equal weights initially
            spinbox.setDecimals(3)
            spinbox.setSingleStep(0.01)
            weights_layout.addWidget(spinbox, i, 1)
            
            # Connect to auto-normalization
            spinbox.valueChanged.connect(self._normalize_weights)
            
            self.weight_widgets[criterion] = spinbox
            
        # Equal weights button
        equal_weights_btn = QPushButton("Set Equal Weights")
        equal_weights_btn.clicked.connect(self._set_equal_weights)
        
        layout.addLayout(weights_layout)
        layout.addWidget(equal_weights_btn)
        self.setLayout(layout)
        
    def _normalize_weights(self):
        """Normalize weights to sum to 1 (optional, can be disabled)"""
        # This is called when any weight changes
        # You can implement auto-normalization here if desired
        pass
        
    def _set_equal_weights(self):
        """Set all weights to equal values"""
        equal_weight = 1.0 / len(self.criteria_names)
        for widget in self.weight_widgets.values():
            widget.setValue(equal_weight)
            
    def get_weights(self) -> np.ndarray:
        """Get current weights as normalized array"""
        weights = np.array([widget.value() for widget in self.weight_widgets.values()])
        
        # Normalize to sum to 1
        weight_sum = np.sum(weights)
        if weight_sum > 0:
            weights = weights / weight_sum
        else:
            weights = np.ones(len(weights)) / len(weights)  # Equal weights if all are 0
            
        return weights


class MCDAResultsWidget(QWidget):
    """Widget for displaying MCDA analysis results"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_results = None
        self.init_ui()
        
    def init_ui(self):
        """Initialize results display interface"""
        layout = QVBoxLayout()
        
        # Results tabs
        self.results_tabs = QTabWidget()
        
        # Rankings tab
        self.rankings_tab = self._create_rankings_tab()
        self.results_tabs.addTab(self.rankings_tab, "Rankings")
        
        # Details tab
        self.details_tab = self._create_details_tab()
        self.results_tabs.addTab(self.details_tab, "Analysis Details")
        
        # Visualization tab
        if MATPLOTLIB_AVAILABLE:
            self.visualization_tab = self._create_visualization_tab()
            self.results_tabs.addTab(self.visualization_tab, "Visualization")
            
        layout.addWidget(self.results_tabs)
        
        # Export buttons
        export_layout = QHBoxLayout()
        
        export_csv_btn = QPushButton("Export Rankings (CSV)")
        export_csv_btn.clicked.connect(self._export_csv)
        
        export_json_btn = QPushButton("Export Full Results (JSON)")
        export_json_btn.clicked.connect(self._export_json)
        
        export_layout.addWidget(export_csv_btn)
        export_layout.addWidget(export_json_btn)
        export_layout.addStretch()
        
        layout.addLayout(export_layout)
        self.setLayout(layout)
        
    def _create_rankings_tab(self):
        """Create rankings display tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Summary statistics
        self.summary_label = QLabel("No analysis performed yet")
        self.summary_label.setStyleSheet("QLabel { font-weight: bold; padding: 5px; }")
        layout.addWidget(self.summary_label)
        
        # Rankings table
        self.rankings_table = QTableWidget()
        self.rankings_table.setSortingEnabled(True)
        layout.addWidget(self.rankings_table)
        
        widget.setLayout(layout)
        return widget
        
    def _create_details_tab(self):
        """Create analysis details tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Details text area
        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        self.details_text.setFont(QFont("Consolas", 10))
        layout.addWidget(self.details_text)
        
        widget.setLayout(layout)
        return widget
        
    def _create_visualization_tab(self):
        """Create visualization tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Matplotlib canvas
        self.figure = Figure(figsize=(12, 8))
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
        
        widget.setLayout(layout)
        return widget
        
    def update_results(self, results: Dict):
        """Update display with new analysis results"""
        self.current_results = results
        self._update_rankings_table()
        self._update_details_text()
        if MATPLOTLIB_AVAILABLE:
            self._update_visualization()
            
    def _update_rankings_table(self):
        """Update the rankings table"""
        if not self.current_results:
            return
            
        # Create ranking summary
        method = self.current_results.get('method', 'Unknown')
        scores = self.current_results['scores']
        rankings = self.current_results['rankings']
        
        # Get alternatives matrix and criteria names
        alternatives_matrix = self.current_results.get('alternatives_matrix', np.array([]))
        criteria_names = self.current_results.get('criteria_names', 
                                                  [f'Criterion_{i+1}' for i in range(alternatives_matrix.shape[1])])
        
        print(f"📊 Results Widget Debug:")
        print(f"   - Results keys: {list(self.current_results.keys())}")
        print(f"   - Criteria names from results: {self.current_results.get('criteria_names', 'NOT FOUND')}")
        print(f"   - Using criteria names: {criteria_names}")
        
        # Update summary
        n_alternatives = len(scores)
        self.summary_label.setText(
            f"{method} Analysis - {n_alternatives} alternatives, "
            f"{len(criteria_names)} criteria"
        )
        
        # Setup table
        n_cols = 3 + len(criteria_names)  # Rank, Alternative, Score, + criteria values
        self.rankings_table.setRowCount(n_alternatives)
        self.rankings_table.setColumnCount(n_cols)
        
        # Headers
        headers = ['Rank', 'Alternative', 'Score'] + criteria_names
        self.rankings_table.setHorizontalHeaderLabels(headers)
        
        # Fill table data
        sorted_indices = np.argsort(-scores)  # Sort by score descending
        
        for row, idx in enumerate(sorted_indices):
            # Rank
            rank_item = QTableWidgetItem(str(row + 1))
            self.rankings_table.setItem(row, 0, rank_item)
            
            # Alternative
            alt_item = QTableWidgetItem(f"Solution_{idx + 1}")
            self.rankings_table.setItem(row, 1, alt_item)
            
            # Score
            score_item = QTableWidgetItem(f"{scores[idx]:.6f}")
            self.rankings_table.setItem(row, 2, score_item)
            
            # Criteria values
            if alternatives_matrix.size > 0:
                for col, criterion in enumerate(criteria_names):
                    value_item = QTableWidgetItem(f"{alternatives_matrix[idx, col]:.4f}")
                    self.rankings_table.setItem(row, 3 + col, value_item)
                    
        # Resize columns
        self.rankings_table.resizeColumnsToContents()
        
    def _update_details_text(self):
        """Update analysis details text"""
        if not self.current_results:
            return
            
        method = self.current_results.get('method', 'Unknown')
        details = [f"=== {method} Analysis Details ===\n"]
        
        if method == 'AHP':
            # AHP specific details
            weights = self.current_results.get('weights', np.array([]))
            criteria_names = self.current_results.get('criteria_names', [])
            consistency_ratio = self.current_results.get('consistency_ratio', 0)
            
            details.append("Criteria Weights:")
            for i, (name, weight) in enumerate(zip(criteria_names, weights)):
                details.append(f"  {name}: {weight:.4f}")
                
            details.append(f"\nConsistency Ratio: {consistency_ratio:.4f}")
            details.append(f"Consistency Check: {'PASS' if consistency_ratio < 0.1 else 'FAIL'}")
            
            if 'pairwise_matrix' in self.current_results:
                details.append("\nPairwise Comparison Matrix:")
                matrix = self.current_results['pairwise_matrix']
                for i, row in enumerate(matrix):
                    row_str = "  " + "  ".join([f"{val:6.3f}" for val in row])
                    details.append(row_str)
                    
        elif method == 'TOPSIS':
            # TOPSIS specific details
            weights = self.current_results.get('weights', np.array([]))
            criteria_names = self.current_results.get('criteria_names', [])
            ideal_solution = self.current_results.get('ideal_solution', np.array([]))
            anti_ideal_solution = self.current_results.get('anti_ideal_solution', np.array([]))
            
            details.append("Criteria Weights:")
            for name, weight in zip(criteria_names, weights):
                details.append(f"  {name}: {weight:.4f}")
                
            details.append("\nIdeal Solution:")
            for name, value in zip(criteria_names, ideal_solution):
                details.append(f"  {name}: {value:.4f}")
                
            details.append("\nAnti-Ideal Solution:")
            for name, value in zip(criteria_names, anti_ideal_solution):
                details.append(f"  {name}: {value:.4f}")
                
        # General statistics
        scores = self.current_results.get('scores', np.array([]))
        if len(scores) > 0:
            details.append(f"\nScore Statistics:")
            details.append(f"  Mean: {np.mean(scores):.6f}")
            details.append(f"  Std Dev: {np.std(scores):.6f}")
            details.append(f"  Min: {np.min(scores):.6f}")
            details.append(f"  Max: {np.max(scores):.6f}")
            
        self.details_text.setText("\n".join(details))
        
    def _update_visualization(self):
        """Update visualization plots"""
        if not self.current_results or not MATPLOTLIB_AVAILABLE:
            return
            
        self.figure.clear()
        
        scores = self.current_results.get('scores', np.array([]))
        method = self.current_results.get('method', 'Unknown')
        
        if len(scores) == 0:
            return
            
        # Create subplots
        if len(scores) > 1:
            ax1 = self.figure.add_subplot(2, 2, 1)
            ax2 = self.figure.add_subplot(2, 2, 2)
            ax3 = self.figure.add_subplot(2, 2, (3, 4))
        else:
            ax3 = self.figure.add_subplot(1, 1, 1)
            
        if len(scores) > 1:
            # Score distribution histogram
            ax1.hist(scores, bins=min(20, len(scores)//2 + 1), alpha=0.7, color='skyblue', edgecolor='black')
            ax1.set_title(f'{method} Score Distribution')
            ax1.set_xlabel('Score')
            ax1.set_ylabel('Frequency')
            
            # Box plot
            ax2.boxplot(scores)
            ax2.set_title(f'{method} Score Box Plot')
            ax2.set_ylabel('Score')
            
        # Ranking visualization
        sorted_indices = np.argsort(-scores)
        top_n = min(20, len(scores))  # Show top 20
        top_indices = sorted_indices[:top_n]
        top_scores = scores[top_indices]
        
        bars = ax3.bar(range(top_n), top_scores, color='lightgreen', alpha=0.7, edgecolor='black')
        ax3.set_title(f'Top {top_n} {method} Scores')
        ax3.set_xlabel('Rank')
        ax3.set_ylabel('Score')
        
        # Add value labels on bars
        for i, (bar, score) in enumerate(zip(bars, top_scores)):
            height = bar.get_height()
            ax3.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                    f'{score:.4f}', ha='center', va='bottom', fontsize=8)
                    
        self.figure.tight_layout()
        self.canvas.draw()
        
    def _export_csv(self):
        """Export rankings to CSV"""
        if not self.current_results:
            QMessageBox.warning(self, "No Results", "No analysis results to export.")
            return
            
        filename, _ = QFileDialog.getSaveFileName(
            self, "Export Rankings CSV", 
            f"mcda_rankings_{self.current_results.get('method', 'unknown').lower()}.csv",
            "CSV Files (*.csv)"
        )
        
        if filename:
            try:
                # Create DataFrame from rankings table
                rows = self.rankings_table.rowCount()
                cols = self.rankings_table.columnCount()
                
                data = []
                headers = []
                
                # Get headers
                for col in range(cols):
                    header_item = self.rankings_table.horizontalHeaderItem(col)
                    headers.append(header_item.text() if header_item else f"Column_{col}")
                    
                # Get data
                for row in range(rows):
                    row_data = []
                    for col in range(cols):
                        item = self.rankings_table.item(row, col)
                        row_data.append(item.text() if item else "")
                    data.append(row_data)
                    
                df = pd.DataFrame(data, columns=headers)
                df.to_csv(filename, index=False)
                
                QMessageBox.information(self, "Export Successful", f"Rankings exported to {filename}")
                
            except Exception as e:
                QMessageBox.critical(self, "Export Error", f"Failed to export CSV: {str(e)}")
                
    def _export_json(self):
        """Export full results to JSON"""
        if not self.current_results:
            QMessageBox.warning(self, "No Results", "No analysis results to export.")
            return
            
        filename, _ = QFileDialog.getSaveFileName(
            self, "Export Full Results JSON",
            f"mcda_results_{self.current_results.get('method', 'unknown').lower()}.json",
            "JSON Files (*.json)"
        )
        
        if filename:
            try:
                # Prepare results for JSON serialization
                export_data = {}
                for key, value in self.current_results.items():
                    if isinstance(value, np.ndarray):
                        export_data[key] = value.tolist()
                    else:
                        export_data[key] = value
                        
                with open(filename, 'w') as f:
                    json.dump(export_data, f, indent=2)
                    
                QMessageBox.information(self, "Export Successful", f"Full results exported to {filename}")
                
            except Exception as e:
                QMessageBox.critical(self, "Export Error", f"Failed to export JSON: {str(e)}")


class MCDATab(QWidget):
    """
    Main MCDA analysis tab
    
    Provides interface for performing multi-criteria decision analysis on
    PyMOO optimization results using AHP or TOPSIS methods.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.mcda_manager = MCDAManager()
        self.current_pymoo_result = None
        self.current_objectives_info = None
        self.init_ui()
        
    def init_ui(self):
        """Initialize the MCDA tab interface"""
        layout = QVBoxLayout()
        
        # Title and description
        title = QLabel("Multi-Criteria Decision Analysis (MCDA)")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        description = QLabel(
            "Analyze PyMOO optimization results using AHP (Analytic Hierarchy Process) "
            "or TOPSIS (Technique for Order of Preference by Similarity to Ideal Solution) methods."
        )
        description.setWordWrap(True)
        description.setStyleSheet("QLabel { color: #666; margin-bottom: 10px; }")
        
        layout.addWidget(title)
        layout.addWidget(description)
        
        # Main content splitter
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left side - Configuration
        config_widget = self._create_configuration_widget()
        main_splitter.addWidget(config_widget)
        
        # Right side - Results
        self.results_widget = MCDAResultsWidget()
        main_splitter.addWidget(self.results_widget)
        
        # Set initial splitter sizes (30% config, 70% results)
        main_splitter.setSizes([300, 700])
        
        layout.addWidget(main_splitter)
        self.setLayout(layout)
        
        # Note: Tab will be enabled/disabled by main window based on optimization status
        
    def _create_configuration_widget(self):
        """Create the configuration panel"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Status
        self.status_label = QLabel("No optimization results loaded")
        self.status_label.setStyleSheet("QLabel { background-color: #8a3030; padding: 8px; border-radius: 4px; }")
        layout.addWidget(self.status_label)
        
        # Method selection
        method_group = QGroupBox("Analysis Method")
        method_layout = QVBoxLayout()
        
        self.method_group = QButtonGroup()
        
        self.ahp_radio = QRadioButton("AHP (Analytic Hierarchy Process)")
        self.ahp_radio.setChecked(True)
        self.ahp_radio.toggled.connect(self._on_method_changed)
        
        self.topsis_radio = QRadioButton("TOPSIS (Ideal Solution Technique)")
        self.topsis_radio.toggled.connect(self._on_method_changed)
        
        self.method_group.addButton(self.ahp_radio, 0)
        self.method_group.addButton(self.topsis_radio, 1)
        
        method_layout.addWidget(self.ahp_radio)
        method_layout.addWidget(self.topsis_radio)
        method_group.setLayout(method_layout)
        
        # Method-specific configuration
        self.config_tabs = QTabWidget()
        
        # AHP configuration tab
        self.ahp_config_widget = QWidget()
        self.config_tabs.addTab(self.ahp_config_widget, "AHP Configuration")
        
        # TOPSIS configuration tab  
        self.topsis_config_widget = QWidget()
        self.config_tabs.addTab(self.topsis_config_widget, "TOPSIS Configuration")
        
        # Analysis button
        self.analyze_button = QPushButton("Perform Analysis")
        self.analyze_button.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QPushButton:disabled {
                background-color: #ccc;
                color: #666;
            }
        """)
        self.analyze_button.clicked.connect(self._perform_analysis)
        self.analyze_button.setEnabled(False)
        
        # Test button for demo purposes
        self.test_button = QPushButton("Test with Demo Data")
        self.test_button.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                padding: 8px;
                font-size: 12px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        self.test_button.clicked.connect(self._test_with_demo_data)
        
        layout.addWidget(method_group)
        layout.addWidget(self.config_tabs)
        layout.addWidget(self.analyze_button)
        layout.addWidget(self.test_button)
        layout.addStretch()
        
        widget.setLayout(layout)
        return widget
        
    def _on_method_changed(self):
        """Handle method selection change"""
        if self.ahp_radio.isChecked():
            self.config_tabs.setCurrentIndex(0)
        else:
            self.config_tabs.setCurrentIndex(1)
            
    def set_optimization_results(self, pymoo_result, objectives_info: List[Dict]):
        """
        Set PyMOO optimization results for MCDA analysis
        
        Args:
            pymoo_result: PyMOO optimization result object or dict containing results
            objectives_info: List of objective information dictionaries
        """
        print(f"🔄 MCDA Tab: Received optimization results!")
        print(f"   - Result type: {type(pymoo_result)}")
        print(f"   - Objectives info: {len(objectives_info)} objectives")
        print(f"   - Objective names: {[obj.get('name', 'unnamed') for obj in objectives_info]}")
        
        # Handle different result formats
        if isinstance(pymoo_result, dict):
            print(f"   - Result keys: {list(pymoo_result.keys())}")
            # Convert dict to object-like structure for compatibility
            class ResultWrapper:
                def __init__(self, result_dict):
                    # Try common keys for objective values
                    if 'F' in result_dict:
                        self.F = result_dict['F']
                    elif 'objectives' in result_dict:
                        self.F = result_dict['objectives']
                    elif 'objective_values' in result_dict:
                        self.F = result_dict['objective_values']
                    else:
                        # Look for any array-like data
                        for key, value in result_dict.items():
                            if hasattr(value, 'shape') and len(value.shape) >= 2:
                                self.F = value
                                break
                        else:
                            raise ValueError(f"Could not find objective values in result dict. Keys: {list(result_dict.keys())}")
                    
                    # Try common keys for decision variables
                    if 'X' in result_dict:
                        self.X = result_dict['X']
                    elif 'variables' in result_dict:
                        self.X = result_dict['variables']
                    elif 'decision_variables' in result_dict:
                        self.X = result_dict['decision_variables']
                    else:
                        # Create dummy variables if not found
                        import numpy as np
                        self.X = np.zeros((self.F.shape[0], 1))
            
            pymoo_result = ResultWrapper(pymoo_result)
            print(f"   - Wrapped result: F shape = {pymoo_result.F.shape}, X shape = {pymoo_result.X.shape}")
        
        self.current_pymoo_result = pymoo_result
        self.current_objectives_info = objectives_info
        
        # Update status
        n_solutions = pymoo_result.F.shape[0] if pymoo_result.F.ndim > 1 else 1
        n_objectives = len(objectives_info)
        
        self.status_label.setText(f"Ready: {n_solutions} solutions, {n_objectives} objectives")
        self.status_label.setStyleSheet("QLabel { background-color: #20af20; padding: 8px; border-radius: 4px; }")
        
        # Create configuration widgets
        criteria_names = [obj.get('name', f'Objective_{i+1}') for i, obj in enumerate(objectives_info)]
        
        # AHP configuration
        ahp_layout = QVBoxLayout()
        self.ahp_comparisons_widget = PairwiseComparisonWidget(criteria_names)
        ahp_layout.addWidget(self.ahp_comparisons_widget)
        self.ahp_config_widget.setLayout(ahp_layout)
        
        # TOPSIS configuration
        topsis_layout = QVBoxLayout()
        self.topsis_weights_widget = WeightConfigurationWidget(criteria_names)
        topsis_layout.addWidget(self.topsis_weights_widget)
        self.topsis_config_widget.setLayout(topsis_layout)
        
        # Enable interface
        self.setEnabled(True)
        self.analyze_button.setEnabled(True)
        
    def _perform_analysis(self):
        """Perform the selected MCDA analysis"""
        if not self.current_pymoo_result or not self.current_objectives_info:
            QMessageBox.warning(self, "No Data", "No optimization results available for analysis.")
            return
            
        try:
            if self.ahp_radio.isChecked():
                # Perform AHP analysis
                comparisons = self.ahp_comparisons_widget.get_comparisons()
                results = self.mcda_manager.analyze_with_ahp(
                    self.current_pymoo_result, 
                    self.current_objectives_info, 
                    comparisons
                )
                
                # Check consistency
                if not results['is_consistent']:
                    QMessageBox.warning(
                        self, "Consistency Warning",
                        f"The pairwise comparisons have a consistency ratio of {results['consistency_ratio']:.4f}, "
                        f"which exceeds the recommended threshold of 0.1. "
                        f"Consider reviewing your comparisons for consistency."
                    )
                    
            else:
                # Perform TOPSIS analysis
                weights = self.topsis_weights_widget.get_weights()
                results = self.mcda_manager.analyze_with_topsis(
                    self.current_pymoo_result,
                    self.current_objectives_info,
                    weights
                )
                
            # Display results
            self.results_widget.update_results(results)
            
            QMessageBox.information(
                self, "Analysis Complete", 
                f"{results['method']} analysis completed successfully!"
            )
            
        except Exception as e:
            QMessageBox.critical(self, "Analysis Error", f"Failed to perform analysis: {str(e)}")
    
    def _test_with_demo_data(self):
        """Test the MCDA functionality with demo data"""
        try:
            import numpy as np
            
            # Create synthetic optimization results (similar to PyMOO output)
            n_solutions = 10
            n_objectives = 3
            
            # Generate synthetic Pareto front solutions
            np.random.seed(42)
            objectives = np.random.rand(n_solutions, n_objectives)
            
            # Create variable values (synthetic design variables)
            variables = np.random.rand(n_solutions, 5)
            
            # Create a mock result object similar to PyMOO's Result
            class MockResult:
                def __init__(self, X, F):
                    self.X = X  # Decision variables
                    self.F = F  # Objective values
            
            mock_result = MockResult(variables, objectives)
            
            # Create mock objectives info
            objectives_info = [
                {"name": "Cost", "minimize": True},
                {"name": "Weight", "minimize": True}, 
                {"name": "Performance", "minimize": False}
            ]
            
            # Set this as our optimization results using the existing method
            self.set_optimization_results(mock_result, objectives_info)
            
            # Show success message
            QMessageBox.information(
                self, "Demo Data Loaded", 
                f"Demo data loaded successfully!\n"
                f"- Solutions: {n_solutions}\n"
                f"- Objectives: {n_objectives}\n"
                f"- Current method: {self.method_combo.currentText()}\n\n"
                f"You can now click 'Analyze' to see the results."
            )
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create demo data: {str(e)}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    # Demo/testing code
    from PyQt6.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)
    
    # Create demo widget
    widget = MCDATab()
    widget.resize(1200, 800)
    widget.show()
    
    sys.exit(app.exec())
