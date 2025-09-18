"""
Results Tab - Display and analyze optimization results

This module provides the ResultsTab class which handles optimization execution,
progress monitoring, and result visualization. It serves as the final stage
of the optimization workflow where users run their configured problems and
analyze the obtained results.

Key Features:
- Multi-threaded optimization execution to prevent GUI freezing  
- Real-time progress monitoring with detailed status updates
- Comprehensive result visualization (Pareto front, objective space plots)
- Solution table with sortable columns and filtering capabilities
- Export functionality for results and plots
- Integration with matplotlib for high-quality visualizations
- Error handling and user feedback mechanisms

The ResultsTab coordinates with the ProblemManager and AlgorithmManager to
execute optimizations and processes the returned results for user consumption.
It uses Qt's signal-slot mechanism to provide responsive user interaction
during potentially long-running optimizations.

Classes:
    OptimizationWorker: Background thread for optimization execution
    ResultsTab: Main UI component for results display and management

Workflow:
    1. User clicks "Run Optimization"
    2. OptimizationWorker thread is created and started
    3. Progress updates are emitted and displayed to user
    4. Upon completion, results are processed and visualized
    5. User can explore results, export data, or run new optimizations

Author: Elias Rizos [it21490]
Version: 1.3.2
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
                            QTableWidget, QTableWidgetItem, QHeaderView,
                            QPushButton, QLabel, QProgressBar, QTextEdit,
                            QTabWidget, QSplitter, QComboBox, QCheckBox,
                            QSpinBox, QFileDialog, QMessageBox)
from PyQt6.QtCore import Qt, pyqtSignal, QThread, QTimer
from PyQt6.QtGui import QFont
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
import pandas as pd
import json
import csv
import os
from datetime import datetime


class OptimizationWorker(QThread):
    """
    Worker thread for running optimization in the background
    
    This class handles the actual optimization execution in a separate thread
    to prevent the GUI from freezing during potentially long-running optimizations.
    It communicates with the main thread through Qt signals to provide progress
    updates and deliver results.
    
    Key Features:
    - Runs optimization in separate thread (non-blocking)
    - Provides real-time progress updates with descriptive messages
    - Handles errors gracefully and reports them to the main thread
    - Can be safely cancelled by the user
    - Integrates with ProblemManager, AlgorithmManager, and Optimizer
    
    Signals:
        progress_update(int, str): Progress percentage (0-100) and status message
        results_ready(object): Emitted when optimization completes successfully
        error_occurred(str): Emitted when an error occurs during optimization
    
    Thread Safety:
        All optimization work is done in this thread, while GUI updates
        are handled in the main thread through signal connections.
    """
    
    # Qt signals for thread-safe communication with main GUI thread
    progress_update = pyqtSignal(int, str)  # (percentage, status_message)
    results_ready = pyqtSignal(object)      # (optimization_results)
    error_occurred = pyqtSignal(str)        # (error_message)
    
    def __init__(self, problem_config, algorithm_config):
        """
        Initialize the optimization worker thread
        
        Args:
            problem_config (dict): Complete problem configuration from GUI
            algorithm_config (dict): Complete algorithm configuration from GUI
        """
        super().__init__()
        self.problem_config = problem_config      # Problem definition from GUI
        self.algorithm_config = algorithm_config  # Algorithm settings from GUI  
        self._is_running = True                   # Flag for cancellation support
        
    def run(self):
        """
        Execute the optimization process
        
        This method runs in the worker thread and performs the complete
        optimization workflow:
        1. Initialize problem and algorithm managers
        2. Create PyMOO problem and algorithm instances
        3. Set up optimization parameters and termination
        4. Run optimization with progress callbacks
        5. Process and emit results
        
        Progress is reported at key stages to keep users informed.
        Any exceptions are caught and reported through the error_occurred signal.
        """
        try:
            # Phase 1: Initialize optimization components (10% progress)
            self.progress_update.emit(10, "Initializing problem...")
            
            # Import required core modules (done here to avoid circular imports)
            from core.problem_manager import ProblemManager
            from core.algorithm_manager import AlgorithmManager
            from core.optimizer import Optimizer
            
            # Initialize management objects
            problem_manager = ProblemManager()
            algorithm_manager = AlgorithmManager()
            optimizer = Optimizer()
            
            # Phase 2: Problem setup (20% progress)
            self.progress_update.emit(20, "Setting up problem...")
            
            # Convert GUI configuration to PyMOO problem instance
            problem = problem_manager.create_problem_from_config(self.problem_config)
            
            self.progress_update.emit(30, "Setting up algorithm...")
            
            # Create PyMOO algorithm from configuration
            n_objectives = len(self.problem_config.get("objectives", []))
            algorithm = algorithm_manager.create_algorithm_from_config(
                self.algorithm_config, 
                n_objectives, 
                self.problem_config
            )
            
            self.progress_update.emit(40, "Starting optimization...")
            
            # Set up termination properly using PyMOO's get_termination
            from pymoo.termination import get_termination
            n_generations = self.algorithm_config.get("parameters", {}).get("n_generations", 50)
            termination = get_termination("n_gen", n_generations)
            
            # Setup optimizer
            optimizer.setup(problem, algorithm, termination)
            
            # Progress callback for real-time updates
            def progress_callback(callback):
                if not self._is_running:
                    return
                if hasattr(callback, 'history') and callback.history['n_gen']:
                    current_gen = callback.history['n_gen'][-1]
                    progress = 40 + int((current_gen / n_generations) * 50)
                    self.progress_update.emit(progress, f"Generation {current_gen}/{n_generations}")
                else:
                    # Fallback if no history available
                    self.progress_update.emit(50, "Optimization in progress...")
            
            # Run the actual optimization
            optimizer.run(progress_callback)
            
            self.progress_update.emit(95, "Processing results...")
            
            # Extract results in GUI format
            results = optimizer.extract_results(self.problem_config, self.algorithm_config)
            
            self.progress_update.emit(100, "Optimization completed")
            self.results_ready.emit(results)
            
        except Exception as e:
            self.error_occurred.emit(f"Optimization failed: {str(e)}")
            import traceback
            print(f"Optimization error: {traceback.format_exc()}")
            
    def stop(self):
        """Stop the optimization"""
        self._is_running = False


class PlotCanvas(FigureCanvas):
    """Canvas for matplotlib plots"""
    
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        super().__init__(self.fig)
        self.setParent(parent)
        
    def plot_objectives(self, results):
        """Plot objective space"""
        self.fig.clear()
        objectives = results["objectives"]
        n_objectives = objectives.shape[1]
        
        # Debug: Check what's in results
        print(f"🎯 Plot Objectives Debug:")
        print(f"   - Results keys: {list(results.keys())}")
        print(f"   - Has problem_config: {'problem_config' in results}")
        if 'problem_config' in results:
            print(f"   - Problem config keys: {list(results['problem_config'].keys())}")
            if 'objectives' in results['problem_config']:
                obj_names_debug = [obj['name'] for obj in results['problem_config']['objectives']]
                print(f"   - Objective names found: {obj_names_debug}")
        
        # Get objective names from problem configuration
        if 'problem_config' in results and 'objectives' in results['problem_config']:
            obj_names = [obj['name'] for obj in results['problem_config']['objectives']]
            print(f"   - Using objective names: {obj_names}")
        else:
            # Fallback to generic names
            obj_names = [f"Objective {i+1}" for i in range(n_objectives)]
            print(f"   - Using fallback names: {obj_names}")
        
        if n_objectives == 2:
            ax = self.fig.add_subplot(111)
            ax.scatter(objectives[:, 0], objectives[:, 1], alpha=0.7, s=30)
            ax.set_xlabel(obj_names[0])
            ax.set_ylabel(obj_names[1])
            ax.set_title("Pareto Front")
            ax.grid(True, alpha=0.3)
        elif n_objectives == 3:
            ax = self.fig.add_subplot(111, projection='3d')
            ax.scatter(objectives[:, 0], objectives[:, 1], objectives[:, 2], alpha=0.7, s=30)
            ax.set_xlabel(obj_names[0])
            ax.set_ylabel(obj_names[1])
            ax.set_zlabel(obj_names[2])
            ax.set_title("3D Pareto Front")
        else:
            # Parallel coordinates plot for many objectives
            ax = self.fig.add_subplot(111)
            for i in range(objectives.shape[0]):
                ax.plot(range(n_objectives), objectives[i, :], alpha=0.5)
            ax.set_xlabel("Objective Index")
            ax.set_ylabel("Objective Value")
            ax.set_title("Parallel Coordinates Plot")
            ax.set_xticks(range(n_objectives))
            ax.set_xticklabels(obj_names, rotation=45)
            ax.grid(True, alpha=0.3)
            
        self.fig.tight_layout()
        self.draw()
        
    def plot_convergence(self, results):
        """Plot convergence history"""
        self.fig.clear()
        ax = self.fig.add_subplot(111)
        
        convergence = results.get("convergence", [])
        if len(convergence) > 0:
            ax.plot(convergence)
            ax.set_xlabel("Generation")
            ax.set_ylabel("Convergence Metric")
            ax.set_title("Convergence History")
            ax.grid(True, alpha=0.3)
        else:
            ax.text(0.5, 0.5, "No convergence data available", 
                   ha='center', va='center', transform=ax.transAxes)
            
        self.fig.tight_layout()
        self.draw()
        
    def plot_variables(self, results):
        """Plot decision variables"""
        self.fig.clear()
        variables = results["variables"]
        n_variables = variables.shape[1]
        
        # Get variable names from problem configuration
        if 'problem_config' in results and 'variables' in results['problem_config']:
            var_names = [var['name'] for var in results['problem_config']['variables']]
        else:
            # Fallback to generic names
            var_names = [f"Variable {i+1}" for i in range(n_variables)]
        
        if n_variables <= 2:
            ax = self.fig.add_subplot(111)
            if n_variables == 1:
                ax.hist(variables[:, 0], bins=20, alpha=0.7)
                ax.set_xlabel(var_names[0])
                ax.set_ylabel("Frequency")
            else:
                ax.scatter(variables[:, 0], variables[:, 1], alpha=0.7, s=30)
                ax.set_xlabel(var_names[0])
                ax.set_ylabel(var_names[1])
            ax.set_title("Decision Variables")
            ax.grid(True, alpha=0.3)
        else:
            # Parallel coordinates for many variables
            ax = self.fig.add_subplot(111)
            for i in range(min(variables.shape[0], 100)):  # Limit for visibility
                ax.plot(range(n_variables), variables[i, :], alpha=0.3)
            ax.set_xlabel("Variable Index")
            ax.set_ylabel("Variable Value")
            ax.set_title("Decision Variables (Parallel Coordinates)")
            ax.set_xticks(range(n_variables))
            ax.set_xticklabels(var_names, rotation=45)
            ax.grid(True, alpha=0.3)
            
        self.fig.tight_layout()
        self.draw()


class ResultsTab(QWidget):
    """Widget for displaying optimization results"""
    
    # Signals to communicate with main window
    optimization_completed = pyqtSignal(object)  # Emitted when optimization finishes successfully
    optimization_error = pyqtSignal(str)         # Emitted when optimization fails
    
    def __init__(self):
        super().__init__()
        self.results = None
        self.current_result = None  # Store current optimization result
        self.worker = None
        self._init_ui()
        
    def _init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout(self)
        
        # Progress section
        self._init_progress_section(layout)
        
        # Results section
        self._init_results_section(layout)
        
    def _init_progress_section(self, parent_layout):
        """Initialize progress tracking section"""
        progress_group = QGroupBox("Optimization Progress")
        layout = QVBoxLayout(progress_group)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Status label
        self.status_label = QLabel("Ready to start optimization")
        layout.addWidget(self.status_label)
        
        # Log text area
        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(100)
        self.log_text.setFont(QFont("Courier", 9))
        layout.addWidget(self.log_text)
        
        parent_layout.addWidget(progress_group)
        
    def _init_results_section(self, parent_layout):
        """Initialize results display section"""
        results_group = QGroupBox("Optimization Results")
        layout = QVBoxLayout(results_group)
        
        # Create tabs for different result views
        self.results_tabs = QTabWidget()
        
        # Summary tab
        self.summary_tab = self._create_summary_tab()
        self.results_tabs.addTab(self.summary_tab, "Summary")
        
        # Plots tab
        self.plots_tab = self._create_plots_tab()
        self.results_tabs.addTab(self.plots_tab, "Plots")
        
        # Solutions table tab
        self.table_tab = self._create_table_tab()
        self.results_tabs.addTab(self.table_tab, "Solutions Table")
        
        # Export tab
        self.export_tab = self._create_export_tab()
        self.results_tabs.addTab(self.export_tab, "Export")
        
        layout.addWidget(self.results_tabs)
        parent_layout.addWidget(results_group)
        
        # Initially disable results tabs
        self.results_tabs.setEnabled(False)
        
    def _create_summary_tab(self):
        """Create the summary tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        self.summary_text = QTextEdit()
        self.summary_text.setReadOnly(True)
        self.summary_text.setPlainText("No results available yet. Run an optimization to see the summary.")
        layout.addWidget(self.summary_text)
        
        return tab
        
    def _create_plots_tab(self):
        """Create the plots tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Plot controls
        controls_layout = QHBoxLayout()
        
        self.plot_type = QComboBox()
        self.plot_type.addItems(["Objective Space", "Convergence", "Decision Variables"])
        self.plot_type.currentTextChanged.connect(self._update_plot)
        controls_layout.addWidget(QLabel("Plot Type:"))
        controls_layout.addWidget(self.plot_type)
        
        self.refresh_plot_btn = QPushButton("Refresh Plot")
        self.refresh_plot_btn.clicked.connect(self._update_plot)
        controls_layout.addWidget(self.refresh_plot_btn)
        controls_layout.addStretch()
        
        layout.addLayout(controls_layout)
        
        # Plot canvas
        self.plot_canvas = PlotCanvas()
        layout.addWidget(self.plot_canvas)
        
        return tab
        
    def _create_table_tab(self):
        """Create the solutions table tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Table controls
        controls_layout = QHBoxLayout()
        
        self.show_objectives = QCheckBox("Show Objectives")
        self.show_objectives.setChecked(True)
        self.show_objectives.toggled.connect(self._update_table)
        controls_layout.addWidget(self.show_objectives)
        
        self.show_variables = QCheckBox("Show Variables")
        self.show_variables.setChecked(True)
        self.show_variables.toggled.connect(self._update_table)
        controls_layout.addWidget(self.show_variables)
        
        controls_layout.addWidget(QLabel("Max Rows:"))
        self.max_rows = QSpinBox()
        self.max_rows.setRange(10, 1000)
        self.max_rows.setValue(100)
        self.max_rows.valueChanged.connect(self._update_table)
        controls_layout.addWidget(self.max_rows)
        
        controls_layout.addStretch()
        
        layout.addLayout(controls_layout)
        
        # Results table
        self.results_table = QTableWidget()
        layout.addWidget(self.results_table)
        
        return tab
        
    def _create_export_tab(self):
        """Create the export tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Export options
        options_group = QGroupBox("Export Options")
        options_layout = QVBoxLayout(options_group)
        
        self.export_objectives = QCheckBox("Export Objectives")
        self.export_objectives.setChecked(True)
        options_layout.addWidget(self.export_objectives)
        
        self.export_variables = QCheckBox("Export Variables")
        self.export_variables.setChecked(True)
        options_layout.addWidget(self.export_variables)
        
        self.export_metadata = QCheckBox("Export Metadata")
        self.export_metadata.setChecked(True)
        options_layout.addWidget(self.export_metadata)
        
        layout.addWidget(options_group)
        
        # Export buttons
        buttons_layout = QHBoxLayout()
        
        self.export_csv_btn = QPushButton("Export to CSV")
        self.export_csv_btn.clicked.connect(lambda: self._export_results("csv"))
        buttons_layout.addWidget(self.export_csv_btn)
        
        self.export_json_btn = QPushButton("Export to JSON")
        self.export_json_btn.clicked.connect(lambda: self._export_results("json"))
        buttons_layout.addWidget(self.export_json_btn)
        
        self.export_excel_btn = QPushButton("Export to Excel")
        self.export_excel_btn.clicked.connect(lambda: self._export_results("excel"))
        buttons_layout.addWidget(self.export_excel_btn)
        
        buttons_layout.addStretch()
        layout.addLayout(buttons_layout)
        
        layout.addStretch()
        
        return tab
        
    def start_optimization(self, problem_config, algorithm_config):
        """
        Start the optimization process in a background thread
        
        Initializes and starts the optimization worker thread with the provided
        problem and algorithm configurations. Handles cleanup of any previous
        optimization and sets up the UI for progress monitoring.
        
        Args:
            problem_config: Dict containing problem definition (variables, objectives, constraints)
            algorithm_config: Dict containing algorithm settings and parameters
            
        Note:
            This method is thread-safe and can be called multiple times.
            Any running optimization will be stopped before starting a new one.
        """
        # Stop any currently running optimization gracefully
        if self.worker and self.worker.isRunning():
            self.worker.stop()           # Signal worker to stop
            self.worker.wait()           # Wait for clean shutdown
            
        # Reset UI to initial state for new optimization
        self.progress_bar.setValue(0)               # Reset progress to 0%
        self.progress_bar.setVisible(True)          # Show progress bar
        self.log_text.clear()                       # Clear previous log messages
        self.results_tabs.setEnabled(False)         # Disable results until completion
        
        # Create new worker thread with current configurations
        self.worker = OptimizationWorker(problem_config, algorithm_config)
        
        # Connect worker signals to UI update methods for real-time feedback
        self.worker.progress_update.connect(self._on_progress_update)  # Progress updates
        self.worker.results_ready.connect(self._on_results_ready)      # Completion notification
        self.worker.error_occurred.connect(self._on_error_occurred)    # Error handling
        
        # Start the optimization in background thread (non-blocking)
        self.worker.start()
        
    def stop_optimization(self):
        """
        Stop the currently running optimization process
        
        Gracefully terminates the optimization worker thread and updates
        the UI to reflect the stopped state. Safe to call even if no
        optimization is running.
        """
        if self.worker and self.worker.isRunning():
            self.worker.stop()                              # Request graceful shutdown
            self.worker.wait()                              # Wait for thread to finish
            self.progress_bar.setVisible(False)             # Hide progress bar
            self.status_label.setText("Optimization stopped by user")  # Update status
            
    def is_running(self):
        """
        Check if an optimization is currently running
        
        Returns:
            bool: True if optimization worker is active, False otherwise
        """
        return self.worker and self.worker.isRunning()
        
    def has_results(self):
        """
        Check if optimization results are available for display
        
        Returns:
            bool: True if results are loaded and ready for visualization, False otherwise
        """
        return self.results is not None
        
    def _on_progress_update(self, progress, message):
        """
        Handle progress updates from the optimization worker thread
        
        Updates the progress bar and status displays with real-time information
        about the optimization progress. Thread-safe slot for worker signals.
        
        Args:
            progress: Integer progress percentage (0-100)
            message: String describing current optimization status
        """
        self.progress_bar.setValue(progress)                    # Update progress bar
        self.status_label.setText(message)                      # Update status text
        self.log_text.append(f"[{progress:3d}%] {message}")     # Add to progress log
        
    def _on_results_ready(self, results):
        """Handle optimization results"""
        self.results = results
        self.current_result = results  # Store for performance metrics
        self.progress_bar.setVisible(False)
        self.status_label.setText("Optimization completed successfully")
        self.results_tabs.setEnabled(True)
        
        # Update all result views
        self._update_summary()
        self._update_plot()
        self._update_table()
        
        # Emit signal to main window that optimization completed successfully
        self.optimization_completed.emit(results)
        
    def _on_error_occurred(self, error_message):
        """Handle optimization errors"""
        self.progress_bar.setVisible(False)
        self.status_label.setText(f"Error: {error_message}")
        self.log_text.append(f"[ERROR] {error_message}")
        
        # Emit signal to main window that optimization failed
        self.optimization_error.emit(error_message)
        
    def _update_summary(self):
        """Update the summary tab"""
        if not self.results:
            return
            
        summary = f"""
                        Optimization Results Summary
                        ============================

                        Algorithm: {self.results['algorithm']}
                        Number of Solutions: {self.results['n_solutions']}
                        Number of Generations: {self.results['n_generations']}

                        Problem Configuration:
                        - Variables: {len(self.results['problem_config']['variables'])}
                        - Objectives: {len(self.results['problem_config']['objectives'])}
                        - Constraints: {len(self.results['problem_config']['constraints'])}

                        Objective Statistics:
                    """
        
        objectives = self.results['objectives']
        for i in range(objectives.shape[1]):
            obj_name = self.results['problem_config']['objectives'][i]['name']
            obj_min = objectives[:, i].min()
            obj_max = objectives[:, i].max()
            obj_mean = objectives[:, i].mean()
            obj_std = objectives[:, i].std()
            
            summary += f"""
                            {obj_name}:
                            Min: {obj_min:.6f}
                            Max: {obj_max:.6f}
                            Mean: {obj_mean:.6f}
                            Std: {obj_std:.6f}
                        """
        
        self.summary_text.setPlainText(summary)
        
    def _update_plot(self):
        """Update the current plot"""
        if not self.results:
            return
            
        plot_type = self.plot_type.currentText()
        
        if plot_type == "Objective Space":
            self.plot_canvas.plot_objectives(self.results)
        elif plot_type == "Convergence":
            self.plot_canvas.plot_convergence(self.results)
        elif plot_type == "Decision Variables":
            self.plot_canvas.plot_variables(self.results)
            
    def _update_table(self):
        """Update the solutions table"""
        if not self.results:
            return
            
        objectives = self.results['objectives']
        variables = self.results['variables']
        max_rows = min(self.max_rows.value(), objectives.shape[0])
        
        # Determine columns
        columns = []
        if self.show_objectives.isChecked():
            obj_names = [obj['name'] for obj in self.results['problem_config']['objectives']]
            columns.extend(obj_names)
        if self.show_variables.isChecked():
            var_names = [var['name'] for var in self.results['problem_config']['variables']]
            columns.extend(var_names)
            
        # Setup table
        self.results_table.setRowCount(max_rows)
        self.results_table.setColumnCount(len(columns))
        self.results_table.setHorizontalHeaderLabels(columns)
        
        # Fill table
        col_idx = 0
        
        # Objectives
        if self.show_objectives.isChecked():
            for obj_idx in range(objectives.shape[1]):
                for row in range(max_rows):
                    item = QTableWidgetItem(f"{objectives[row, obj_idx]:.6f}")
                    self.results_table.setItem(row, col_idx, item)
                col_idx += 1
                
        # Variables
        if self.show_variables.isChecked():
            for var_idx in range(variables.shape[1]):
                for row in range(max_rows):
                    item = QTableWidgetItem(f"{variables[row, var_idx]:.6f}")
                    self.results_table.setItem(row, col_idx, item)
                col_idx += 1
                
        # Auto-resize columns
        self.results_table.resizeColumnsToContents()
        
    def _export_results(self, format_type):
        """Export results to file"""
        if not self.results:
            QMessageBox.warning(self, "No Results", "No optimization results available to export.")
            return
            
        try:
            # Generate default filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            problem_name = self.results.get('problem_config', {}).get('name', 'optimization')
            algorithm = self.results.get('algorithm', 'unknown')
            
            # Clean names for filename
            safe_problem_name = "".join(c for c in problem_name if c.isalnum() or c in (' ', '-', '_')).strip()
            safe_algorithm = "".join(c for c in algorithm if c.isalnum() or c in (' ', '-', '_')).strip()
            
            if format_type.lower() == 'csv':
                default_filename = f"{safe_problem_name}_{safe_algorithm}_{timestamp}.csv"
                filename, _ = QFileDialog.getSaveFileName(
                    self, 
                    "Export Results as CSV",
                    default_filename,
                    "CSV Files (*.csv);;All Files (*)"
                )
                if filename:
                    self._export_to_csv(filename)
                    
            elif format_type.lower() == 'excel':
                default_filename = f"{safe_problem_name}_{safe_algorithm}_{timestamp}.xlsx"
                filename, _ = QFileDialog.getSaveFileName(
                    self, 
                    "Export Results as Excel",
                    default_filename,
                    "Excel Files (*.xlsx);;All Files (*)"
                )
                if filename:
                    self._export_to_excel(filename)
                    
            elif format_type.lower() == 'json':
                default_filename = f"{safe_problem_name}_{safe_algorithm}_{timestamp}.json"
                filename, _ = QFileDialog.getSaveFileName(
                    self, 
                    "Export Results as JSON",
                    default_filename,
                    "JSON Files (*.json);;All Files (*)"
                )
                if filename:
                    self._export_to_json(filename)
                    
            elif format_type.lower() == 'plot':
                default_filename = f"{safe_problem_name}_{safe_algorithm}_{timestamp}.png"
                filename, _ = QFileDialog.getSaveFileName(
                    self, 
                    "Export Plot as Image",
                    default_filename,
                    "PNG Files (*.png);;PDF Files (*.pdf);;SVG Files (*.svg);;All Files (*)"
                )
                if filename:
                    self._export_plot(filename)
                    
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export results:\n{str(e)}")
            
    def _export_to_csv(self, filename):
        """Export results to CSV format"""
        try:
            # Prepare data for CSV export
            variables = self.results['variables']
            objectives = self.results['objectives']
            
            # Create column names
            var_names = [f"Var_{i+1}" for i in range(variables.shape[1])]
            if 'problem_config' in self.results and 'variables' in self.results['problem_config']:
                var_names = [var['name'] for var in self.results['problem_config']['variables']]
            
            obj_names = [f"Obj_{i+1}" for i in range(objectives.shape[1])]
            if 'problem_config' in self.results and 'objectives' in self.results['problem_config']:
                obj_names = [obj['name'] for obj in self.results['problem_config']['objectives']]
            
            # Combine data
            all_data = np.column_stack([variables, objectives])
            all_column_names = var_names + obj_names
            
            # Create DataFrame and save to CSV
            df = pd.DataFrame(all_data, columns=all_column_names)
            df.to_csv(filename, index=False)
            
            self.log_text.append(f"[INFO] Results exported to CSV: {filename}")
            QMessageBox.information(self, "Export Successful", f"Results successfully exported to:\n{filename}")
            
        except Exception as e:
            raise Exception(f"CSV export failed: {str(e)}")
            
    def _export_to_excel(self, filename):
        """Export results to Excel format with multiple sheets"""
        try:
            variables = self.results['variables']
            objectives = self.results['objectives']
            
            # Prepare variable names
            var_names = [f"Var_{i+1}" for i in range(variables.shape[1])]
            if 'problem_config' in self.results and 'variables' in self.results['problem_config']:
                var_names = [var['name'] for var in self.results['problem_config']['variables']]
            
            obj_names = [f"Obj_{i+1}" for i in range(objectives.shape[1])]
            if 'problem_config' in self.results and 'objectives' in self.results['problem_config']:
                obj_names = [obj['name'] for obj in self.results['problem_config']['objectives']]
            
            # Create Excel writer
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                # Solutions sheet
                all_data = np.column_stack([variables, objectives])
                all_column_names = var_names + obj_names
                solutions_df = pd.DataFrame(all_data, columns=all_column_names)
                solutions_df.to_excel(writer, sheet_name='Solutions', index=False)
                
                # Variables sheet
                variables_df = pd.DataFrame(variables, columns=var_names)
                variables_df.to_excel(writer, sheet_name='Variables', index=False)
                
                # Objectives sheet
                objectives_df = pd.DataFrame(objectives, columns=obj_names)
                objectives_df.to_excel(writer, sheet_name='Objectives', index=False)
                
                # Statistics sheet
                stats_data = []
                for i, obj_name in enumerate(obj_names):
                    obj_data = objectives[:, i]
                    stats_data.append({
                        'Objective': obj_name,
                        'Min': obj_data.min(),
                        'Max': obj_data.max(),
                        'Mean': obj_data.mean(),
                        'Std': obj_data.std(),
                        'Median': np.median(obj_data)
                    })
                
                stats_df = pd.DataFrame(stats_data)
                stats_df.to_excel(writer, sheet_name='Statistics', index=False)
                
                # Configuration sheet
                config_data = {
                    'Algorithm': [self.results.get('algorithm', 'Unknown')],
                    'Number of Solutions': [self.results.get('n_solutions', 0)],
                    'Number of Generations': [self.results.get('n_generations', 0)],
                    'Export Date': [datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
                }
                config_df = pd.DataFrame(config_data)
                config_df.to_excel(writer, sheet_name='Configuration', index=False)
            
            self.log_text.append(f"[INFO] Results exported to Excel: {filename}")
            QMessageBox.information(self, "Export Successful", f"Results successfully exported to Excel with multiple sheets:\n{filename}")
            
        except Exception as e:
            raise Exception(f"Excel export failed: {str(e)}")
            
    def _export_to_json(self, filename):
        """Export results to JSON format"""
        try:
            # Prepare exportable data (convert numpy arrays to lists)
            export_data = {
                'export_info': {
                    'timestamp': datetime.now().isoformat(),
                    'version': '1.0',
                    'software': 'NewDSS Multi-Objective Optimization'
                },
                'algorithm': self.results.get('algorithm', 'Unknown'),
                'n_solutions': int(self.results.get('n_solutions', 0)),
                'n_generations': int(self.results.get('n_generations', 0)),
                'variables': self.results['variables'].tolist(),
                'objectives': self.results['objectives'].tolist(),
                'problem_config': self.results.get('problem_config', {}),
                'algorithm_config': self.results.get('algorithm_config', {}),
            }
            
            # Add constraints if available
            if 'constraints' in self.results and self.results['constraints'] is not None:
                export_data['constraints'] = self.results['constraints'].tolist()
            
            # Add statistics
            objectives = self.results['objectives']
            obj_names = [f"Obj_{i+1}" for i in range(objectives.shape[1])]
            if 'problem_config' in self.results and 'objectives' in self.results['problem_config']:
                obj_names = [obj['name'] for obj in self.results['problem_config']['objectives']]
            
            export_data['statistics'] = {}
            for i, obj_name in enumerate(obj_names):
                obj_data = objectives[:, i]
                export_data['statistics'][obj_name] = {
                    'min': float(obj_data.min()),
                    'max': float(obj_data.max()),
                    'mean': float(obj_data.mean()),
                    'std': float(obj_data.std()),
                    'median': float(np.median(obj_data))
                }
            
            # Save to JSON
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            self.log_text.append(f"[INFO] Results exported to JSON: {filename}")
            QMessageBox.information(self, "Export Successful", f"Results successfully exported to JSON:\n{filename}")
            
        except Exception as e:
            raise Exception(f"JSON export failed: {str(e)}")
            
    def _export_plot(self, filename):
        """Export current plot to image file"""
        try:
            if not hasattr(self, 'plot_canvas') or not self.plot_canvas.fig:
                raise Exception("No plot available to export")
            
            # Determine DPI based on file extension
            file_ext = os.path.splitext(filename)[1].lower()
            if file_ext == '.pdf':
                dpi = None  # PDF uses vector format
            elif file_ext == '.svg':
                dpi = None  # SVG uses vector format
            else:
                dpi = 300  # High DPI for raster formats
            
            # Save the plot
            self.plot_canvas.fig.savefig(
                filename,
                dpi=dpi,
                bbox_inches='tight',
                facecolor='white',
                edgecolor='none',
                format=file_ext[1:] if file_ext else 'png'
            )
            
            self.log_text.append(f"[INFO] Plot exported to: {filename}")
            QMessageBox.information(self, "Export Successful", f"Plot successfully exported to:\n{filename}")
            
        except Exception as e:
            raise Exception(f"Plot export failed: {str(e)}")
        
    def clear(self):
        """Clear all results and reset the UI"""
        self.results = None
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)
        self.status_label.setText("Ready to start optimization")
        self.log_text.clear()
        self.summary_text.setPlainText("No results available yet. Run an optimization to see the summary.")
        self.results_table.setRowCount(0)
        self.results_tabs.setEnabled(False)
        
        # Clear plot
        self.plot_canvas.fig.clear()
        self.plot_canvas.draw()
