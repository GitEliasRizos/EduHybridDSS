"""
Main Window for PyMOO GUI Application
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
    """Main application window"""
    
    # Signals
    optimization_started = pyqtSignal()
    optimization_finished = pyqtSignal(object)
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyMOO GUI - Multi-Objective Optimization")
        self.setGeometry(100, 100, 1200, 800)
        
        # Initialize UI components
        self._init_ui()
        self._init_menubar()
        self._init_toolbar()
        self._init_statusbar()
        
        # Connect signals
        self._connect_signals()
        
    def _init_ui(self):
        """Initialize the main UI components"""
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        
        # Create splitter for resizable panes
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)
        
        # Left side - Configuration tabs
        self.tab_widget = QTabWidget()
        
        # Create tabs
        self.problem_tab = ProblemTab()
        self.algorithm_tab = AlgorithmTab()
        
        # Add tabs
        self.tab_widget.addTab(self.problem_tab, "Problem Definition")
        self.tab_widget.addTab(self.algorithm_tab, "Algorithm & Settings")
        
        splitter.addWidget(self.tab_widget)
        
        # Right side - Results
        self.results_tab = ResultsTab()
        splitter.addWidget(self.results_tab)
        
        # Set splitter proportions (70% left, 30% right)
        splitter.setSizes([840, 360])
        
    def _init_menubar(self):
        """Initialize the menu bar"""
        menubar = self.menuBar()
        
        # File menu
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
            <h3>PyMOO GUI v1.0.0</h3>
            <p>A comprehensive graphical user interface for PyMOO 
            (Multi-objective Optimization in Python).</p>
            
            <p><b>Features:</b></p>
            <ul>
            <li>Problem definition with variables, objectives, and constraints</li>
            <li>Algorithm selection and configuration</li>
            <li>Results visualization and analysis</li>
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
