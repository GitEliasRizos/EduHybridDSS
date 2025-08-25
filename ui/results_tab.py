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
                            QSpinBox)
from PyQt6.QtCore import Qt, pyqtSignal, QThread, QTimer
from PyQt6.QtGui import QFont
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np


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
        
    def _generate_mock_results(self):
        """Generate mock optimization results for demonstration
        
        NOTE: This method is deprecated and should not be used.
        The optimization now uses real PyMOO algorithms.
        """
        # This method is kept for compatibility but should not be called
        raise NotImplementedError("Mock results are deprecated. Use real PyMOO optimization instead.")


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
        
        if n_objectives == 2:
            ax = self.fig.add_subplot(111)
            ax.scatter(objectives[:, 0], objectives[:, 1], alpha=0.7, s=30)
            ax.set_xlabel(f"Objective 1")
            ax.set_ylabel(f"Objective 2")
            ax.set_title("Pareto Front")
            ax.grid(True, alpha=0.3)
        elif n_objectives == 3:
            ax = self.fig.add_subplot(111, projection='3d')
            ax.scatter(objectives[:, 0], objectives[:, 1], objectives[:, 2], alpha=0.7, s=30)
            ax.set_xlabel("Objective 1")
            ax.set_ylabel("Objective 2")
            ax.set_zlabel("Objective 3")
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
        
        if n_variables <= 2:
            ax = self.fig.add_subplot(111)
            if n_variables == 1:
                ax.hist(variables[:, 0], bins=20, alpha=0.7)
                ax.set_xlabel("Variable 1")
                ax.set_ylabel("Frequency")
            else:
                ax.scatter(variables[:, 0], variables[:, 1], alpha=0.7, s=30)
                ax.set_xlabel("Variable 1")
                ax.set_ylabel("Variable 2")
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
        """Start the optimization process"""
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.worker.wait()
            
        # Reset UI
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(True)
        self.log_text.clear()
        self.results_tabs.setEnabled(False)
        
        # Create and start worker
        self.worker = OptimizationWorker(problem_config, algorithm_config)
        self.worker.progress_update.connect(self._on_progress_update)
        self.worker.results_ready.connect(self._on_results_ready)
        self.worker.error_occurred.connect(self._on_error_occurred)
        self.worker.start()
        
    def stop_optimization(self):
        """Stop the optimization process"""
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.worker.wait()
            self.progress_bar.setVisible(False)
            self.status_label.setText("Optimization stopped by user")
            
    def is_running(self):
        """Check if optimization is running"""
        return self.worker and self.worker.isRunning()
        
    def has_results(self):
        """Check if results are available"""
        return self.results is not None
        
    def _on_progress_update(self, progress, message):
        """Handle progress updates"""
        self.progress_bar.setValue(progress)
        self.status_label.setText(message)
        self.log_text.append(f"[{progress:3d}%] {message}")
        
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
            return
            
        # TODO: Implement actual export functionality
        self.log_text.append(f"[INFO] Exporting results to {format_type.upper()} format...")
        
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
