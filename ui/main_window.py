"""
Main Window for PyMOO GUI Application

This module contains the MainWindow class which serves as the primary interface
for the multi-objective optimization GUI. It coordinates between different tabs
(Problem Definition, Algorithm Configuration, and Results Visualization) and 
manages the overall application workflow.

Key Features:
- Tab-based interface for different optimization phases
- Menu system for file operations and settings
- Toolbar for quick actions
- Status bar for user feedback
- Signal-slot architecture for component communication
- Automatic optimization workflow management

Author: Elias Rizos [it21490]
Version: 1.3.2
"""

from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                            QTabWidget, QMenuBar, QStatusBar, QToolBar,
                            QMessageBox, QFileDialog, QSplitter)

from PyQt6.QtCore import Qt, pyqtSignal

from PyQt6.QtGui import QAction, QIcon, QKeySequence

from .problem_tab import ProblemTab
from .algorithm_tab import AlgorithmTab
from .results_tab import ResultsTab


class MainWindow(QMainWindow):
    """
    Main application window for the PyMOO GUI
    
    This class creates and manages the primary user interface, including:
    - Tab widget with Problem, Algorithm, and Results tabs
    - Menu bar with File, Edit, View, and Help menus
    - Toolbar with common actions
    - Status bar for displaying application state
    
    The MainWindow coordinates optimization workflow by:
    1. Collecting problem definition from ProblemTab
    2. Getting algorithm configuration from AlgorithmTab
    3. Running optimization in ResultsTab
    4. Managing UI state during optimization process
    
    Signals:
        optimization_started: Emitted when optimization begins
        optimization_finished: Emitted when optimization completes with results
    """
    
    # Custom signals for coordinating optimization workflow
    optimization_started = pyqtSignal()
    optimization_finished = pyqtSignal(object)  # object = optimization results
    
    def __init__(self):
        """
        Initialize the main window
        
        Sets up the complete user interface including tabs, menus, toolbar,
        and status bar. Also connects all necessary signals for component
        communication.
        """
        super().__init__()
        self.setWindowTitle("PyMOO GUI - Multi-Objective Optimization")
        self.setGeometry(100, 100, 1200, 800)  # x, y, width, height
        
        # Initialize UI components in order
        self._init_ui()          # Main layout and tabs
        self._init_menubar()     # File, Edit, View, Help menus
        self._init_toolbar()     # Quick action buttons
        self._init_statusbar()   # Status information display
        
        # Connect inter-component communication signals
        self._connect_signals()
        
    def _init_ui(self):
        """
        Initialize the main user interface components
        
        Creates the central widget with tab interface:
        - ProblemTab: Define optimization problem (variables, objectives, constraints)
        - AlgorithmTab: Configure optimization algorithm (NSGA-II, NSGA-III, etc.)
        - ResultsTab: Run optimization and view results (plots, tables, export)
        
        Uses a splitter layout to allow user-resizable sections.
        """
        # Central widget serves as the main container
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout organizes components vertically
        main_layout = QVBoxLayout(central_widget)
        
        # Create horizontal splitter for resizable panes
        # This allows users to adjust space between sections
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)
        
        # Left side - Configuration tabs (70% of window width)
        # Contains problem definition and algorithm configuration
        self.tab_widget = QTabWidget()
        
        # Create individual tabs for different optimization phases
        self.problem_tab = ProblemTab()      # Variables, objectives, constraints
        self.algorithm_tab = AlgorithmTab()  # Algorithm selection and parameters
        
        # Add tabs to the tab widget with descriptive labels
        self.tab_widget.addTab(self.problem_tab, "Problem Definition")
        self.tab_widget.addTab(self.algorithm_tab, "Algorithm & Settings")
        
        # Add tab widget to left side of splitter
        splitter.addWidget(self.tab_widget)
        
        # Right side - Results tab (30% of window width)
        # Contains optimization execution, progress, and result visualization
        self.results_tab = ResultsTab()
        
        # Add results tab to right side of splitter
        splitter.addWidget(self.results_tab)
        
        # Set initial splitter proportions (70% left configuration, 30% right results)
        # Users can adjust these proportions by dragging the splitter
        splitter.setSizes([840, 360])  # Based on 1200px total width
        
    def _init_menubar(self):
        """
        Initialize the application menu bar
        
        Creates a comprehensive menu system with:
        - File menu: New, Open, Save, Export operations
        - Edit menu: Cut, Copy, Paste, Undo, Redo
        - View menu: UI customization and display options
        - Help menu: Documentation and about information
        
        Each menu item is configured with appropriate shortcuts,
        icons, and status tips for enhanced usability.
        """
        menubar = self.menuBar()
        
        # File menu - handles project and data operations
        file_menu = menubar.addMenu("&File")
        
        # New problem
        new_action = QAction("&New Problem", self)
        new_action.setShortcut(QKeySequence.StandardKey.New)
        new_action.triggered.connect(self.new_problem)
        file_menu.addAction(new_action)
        
        # Open problem
        open_action = QAction("&Open Problem", self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.triggered.connect(self.open_problem)
        file_menu.addAction(open_action)
        
        # Save problem
        save_action = QAction("&Save Problem", self)
        save_action.setShortcut(QKeySequence.StandardKey.Save)
        save_action.triggered.connect(self.save_problem)
        file_menu.addAction(save_action)
        
        file_menu.addSeparator()
        
        # Export results
        export_action = QAction("&Export Results", self)
        export_action.triggered.connect(self.export_results)
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        # Exit
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit menu
        edit_menu = menubar.addMenu("&Edit")
        
        # Clear all
        clear_action = QAction("&Clear All", self)
        clear_action.triggered.connect(self.clear_all)
        edit_menu.addAction(clear_action)
        
        # Run menu
        run_menu = menubar.addMenu("&Run")
        
        # Start optimization
        self.run_action = QAction("&Start Optimization", self)
        self.run_action.setShortcut("F5")
        self.run_action.triggered.connect(self.start_optimization)
        run_menu.addAction(self.run_action)
        
        # Stop optimization
        self.stop_action = QAction("&Stop Optimization", self)
        self.stop_action.setShortcut("Shift+F5")
        self.stop_action.setEnabled(False)
        self.stop_action.triggered.connect(self.stop_optimization)
        run_menu.addAction(self.stop_action)
        
        # Help menu
        help_menu = menubar.addMenu("&Help")
        
        # About
        about_action = QAction("&About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
    def _init_toolbar(self):
        """Initialize the toolbar"""
        toolbar = self.addToolBar("Main")
        toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        
        # Run optimization button
        self.run_button = toolbar.addAction("▶ Run Optimization")
        self.run_button.triggered.connect(self.start_optimization)
        
        # Stop optimization button
        self.stop_button = toolbar.addAction("⏹ Stop")
        self.stop_button.setEnabled(False)
        self.stop_button.triggered.connect(self.stop_optimization)
        
        toolbar.addSeparator()
        
        # Clear button
        clear_button = toolbar.addAction("🗑 Clear All")
        clear_button.triggered.connect(self.clear_all)
        
    def _init_statusbar(self):
        """Initialize the status bar"""
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("Ready")
        
    def _connect_signals(self):
        """Connect internal signals"""
        self.problem_tab.problem_changed.connect(self.on_problem_changed)
        self.algorithm_tab.algorithm_changed.connect(self.on_algorithm_changed)
        
        # Connect results tab signals to handle optimization completion
        self.results_tab.optimization_completed.connect(self._on_optimization_finished)
        self.results_tab.optimization_error.connect(lambda error: self._on_optimization_finished(None))
        
    def new_problem(self):
        """Create a new problem"""
        reply = QMessageBox.question(
            self, "New Problem",
            "This will clear all current settings. Continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.clear_all()
            
    def open_problem(self):
        """Open a problem from file"""
        filename, _ = QFileDialog.getOpenFileName(
            self, "Open Problem", "",
            "JSON Files (*.json);;All Files (*)"
        )
        if filename:
            try:
                from utils.helpers import load_complete_config, load_problem_config
                
                # Try to load as complete config first (new format)
                complete_config = load_complete_config(filename)
                if complete_config:
                    # New format with both problem and algorithm
                    if "problem" in complete_config:
                        self.problem_tab.set_configuration(complete_config["problem"])
                    if "algorithm" in complete_config:
                        self.algorithm_tab.set_configuration(complete_config["algorithm"])
                    self.status_bar.showMessage(f"Complete configuration loaded from {filename}")
                else:
                    # Try old format (problem only)
                    config = load_problem_config(filename)
                    if config:
                        self.problem_tab.set_configuration(config)
                        self.status_bar.showMessage(f"Problem loaded from {filename} (algorithm settings not included)")
                    else:
                        QMessageBox.warning(
                            self, "Load Error",
                            "Failed to load configuration from file."
                        )
            except Exception as e:
                QMessageBox.critical(
                    self, "Load Error",
                    f"Error loading configuration: {str(e)}"
                )
            
    def save_problem(self):
        """Save current problem to file"""
        filename, _ = QFileDialog.getSaveFileName(
            self, "Save Problem", "",
            "JSON Files (*.json);;All Files (*)"
        )
        if filename:
            try:
                from utils.helpers import save_complete_config
                
                # Create complete configuration including problem and algorithm
                complete_config = {
                    "problem": self.problem_tab.get_configuration(),
                    "algorithm": self.algorithm_tab.get_configuration(),
                    "metadata": {
                        "created_by": "PyMOO GUI",
                        "version": "1.0.0",
                        "created_date": self._get_current_timestamp()
                    }
                }
                
                if save_complete_config(complete_config, filename):
                    self.status_bar.showMessage(f"Complete configuration saved to {filename}")
                else:
                    QMessageBox.warning(
                        self, "Save Error",
                        "Failed to save configuration to file."
                    )
            except Exception as e:
                QMessageBox.critical(
                    self, "Save Error",
                    f"Error saving configuration: {str(e)}"
                )
            
    def export_results(self):
        """Export optimization results"""
        if not self.results_tab.has_results():
            QMessageBox.information(
                self, "Export Results",
                "No results available to export."
            )
            return
            
        filename, _ = QFileDialog.getSaveFileName(
            self, "Export Results", "",
            "CSV Files (*.csv);;JSON Files (*.json);;Excel Files (*.xlsx);;All Files (*)"
        )
        if filename:
            try:
                from utils.helpers import export_results_csv, export_results_json, export_results_excel
                results = self.results_tab.results
                
                if filename.lower().endswith('.csv'):
                    success = export_results_csv(results, filename)
                elif filename.lower().endswith('.json'):
                    success = export_results_json(results, filename)
                elif filename.lower().endswith('.xlsx'):
                    success = export_results_excel(results, filename)
                else:
                    # Default to CSV
                    success = export_results_csv(results, filename)
                    
                if success:
                    self.status_bar.showMessage(f"Results exported to {filename}")
                else:
                    QMessageBox.warning(
                        self, "Export Error",
                        "Failed to export results to file."
                    )
            except Exception as e:
                QMessageBox.critical(
                    self, "Export Error",
                    f"Error exporting results: {str(e)}"
                )
            
    def clear_all(self):
        """Clear all settings and results"""
        self.problem_tab.clear()
        self.algorithm_tab.clear()
        self.results_tab.clear()
        self.status_bar.showMessage("All settings cleared")
        
    def start_optimization(self):
        """Start the optimization process"""
        # Validate problem and algorithm settings
        if not self.problem_tab.is_valid():
            QMessageBox.warning(
                self, "Invalid Problem",
                "Please define a valid problem before starting optimization."
            )
            return
            
        if not self.algorithm_tab.is_valid():
            QMessageBox.warning(
                self, "Invalid Algorithm",
                "Please select and configure an algorithm."
            )
            return
            
        # Update UI state
        self.run_action.setEnabled(False)
        self.run_button.setEnabled(False)
        self.stop_action.setEnabled(True)
        self.stop_button.setEnabled(True)
        
        self.status_bar.showMessage("Optimization running...")
        
        # Get problem and algorithm configurations
        problem_config = self.problem_tab.get_configuration()
        algorithm_config = self.algorithm_tab.get_configuration()
        
        # Start optimization (this will be handled by the results tab)
        self.results_tab.start_optimization(problem_config, algorithm_config)
        
        # Emit signal
        self.optimization_started.emit()
        
    def stop_optimization(self):
        """Stop the optimization process"""
        self.results_tab.stop_optimization()
        self._on_optimization_finished(None)
        
    def _on_optimization_finished(self, results):
        """Handle optimization completion"""
        # Update UI state
        self.run_action.setEnabled(True)
        self.run_button.setEnabled(True)
        self.stop_action.setEnabled(False)
        self.stop_button.setEnabled(False)
        
        if results is not None:
            self.status_bar.showMessage("Optimization completed successfully")
        else:
            self.status_bar.showMessage("Optimization stopped")
            
        # Emit signal
        self.optimization_finished.emit(results)
        
    def on_problem_changed(self):
        """Handle problem configuration changes"""
        self.status_bar.showMessage("Problem configuration updated")
        
    def on_algorithm_changed(self):
        """Handle algorithm configuration changes"""
        self.status_bar.showMessage("Algorithm configuration updated")
        
    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(
            self, "About PyMOO GUI",
            """
            <h3>PyMOO GUI v2.0.0</h3>
            <p>A comprehensive graphical user interface for PyMOO 
            (Multi-objective Optimization in Python).</p>
            
            <p><b>Features:</b></p>
            <ul>
            <li>Problem definition with variables, objectives, and constraints</li>
            <li>Algorithm selection and configuration</li>
            <li>Results visualization and analysis</li>
            <li>Real-time optimization visualization</li>
            <li>Multi-algorithm comparison</li>
            <li>Performance metrics dashboard</li>
            <li>Export capabilities</li>
            </ul>
            
            <p>Built with PyQt6 and PyMOO</p>
            """
        )
    
    def closeEvent(self, event):
        """Handle application close event"""
        if self.results_tab.is_running():
            reply = QMessageBox.question(
                self, "Optimization Running",
                "An optimization is currently running. Do you want to stop it and exit?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.results_tab.stop_optimization()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()
            
    def _get_current_timestamp(self):
        """Get current timestamp for metadata"""
        from datetime import datetime
        return datetime.now().isoformat()
