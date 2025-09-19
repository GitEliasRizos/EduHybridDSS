"""
Main Window - Primary Application Interface Controller

This module implements the central user interface controller for the PyMOO GUI 
application. It provides a tabbed interface architecture that coordinates between 
different functional components for multi-objective optimization workflow management.

Core Architecture:
The main window serves as the primary container and coordinator for all application
functionality, organizing the user interface into specialized tabs:

Interface Components:
- Problem Definition Tab: Multi-objective problem specification and configuration
- Algorithm Configuration Tab: Optimization algorithm selection and parameter tuning  
- Results Visualization Tab: Solution analysis, plotting, and export capabilities
- MCDA Integration Tab: Multi-criteria decision analysis for solution ranking

System Architecture:
This module serves as the central interface controller, managing tab coordination,
inter-component communication through signals, and overall application workflow.

Author: Elias Rizos [it21490]
Version: 1.3.2
"""

# Import PyQt6 framework components for GUI construction
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                            QTabWidget, QMenuBar, QStatusBar, QToolBar,
                            QMessageBox, QFileDialog, QSplitter, QTableWidgetItem)

from PyQt6.QtCore import Qt, pyqtSignal

from PyQt6.QtGui import QAction, QKeySequence, QFont

# Import application-specific tab components
from .problem_tab import ProblemTab
from .algorithm_tab import AlgorithmTab    # Algorithm selection department  
from .results_tab import ResultsTab        # Results visualization department
from .mcda_tab import MCDATab              # Decision analysis department

# Import database manager for group sessions
from core.user_manager import UserDatabaseManager


class MainWindow(QMainWindow):
    """
    Main Application Window - Central Interface Controller
    
    This class implements the primary application window that serves as the central
    hub for multi-objective optimization workflow management. It coordinates between
    different functional components through a tabbed interface architecture.
    
    Interface Organization:
    The main window organizes functionality into specialized tabs:
    - Problem Definition Tab: Problem specification and configuration management
    - Algorithm Configuration Tab: Optimization algorithm selection and tuning
    - Results Analysis Tab: Solution visualization, analysis, and export
    - MCDA Integration Tab: Multi-criteria decision analysis and ranking
    
    Workflow Coordination:
    The window manages the complete optimization workflow:
    1. Problem Definition: Specify variables, objectives, and constraints
    2. Algorithm Configuration: Select and configure optimization algorithms
    3. Execution Management: Monitor and control optimization processes
    4. Results Processing: Analyze, visualize, and export optimization results
    
    Inter-Component Communication:
    Custom signals coordinate workflow between components:
    - optimization_started: Signals the beginning of optimization execution
    - optimization_finished: Signals completion with results for analysis
    """
    
    # Custom signals for optimization workflow coordination
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
        
        # Initialize database manager for group sessions
        self.db_manager = UserDatabaseManager()
        
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
        self.mcda_tab = MCDATab()            # Multi-criteria decision analysis
        
        # Add tabs to the tab widget with descriptive labels
        self.tab_widget.addTab(self.problem_tab, "Problem Definition")
        self.tab_widget.addTab(self.algorithm_tab, "Algorithm & Settings")
        self.tab_widget.addTab(self.mcda_tab, "MCDA Analysis")
        
        # Initially disable MCDA tab until optimization is completed
        # For testing: comment next line to enable MCDA tab immediately  
        # self.tab_widget.setTabEnabled(2, False)
        
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
        
        # Group Decision menu
        group_menu = menubar.addMenu("&Group Decision")
        
        # View Sessions
        view_sessions_action = QAction("&View Active Sessions", self)
        view_sessions_action.triggered.connect(self.view_group_sessions)
        group_menu.addAction(view_sessions_action)
        
        # Check Ready Sessions  
        check_ready_action = QAction("&Check Ready Sessions", self)
        check_ready_action.triggered.connect(self.check_ready_sessions)
        group_menu.addAction(check_ready_action)
        
        group_menu.addSeparator()
        
        # Run Complete Group Analysis
        run_complete_action = QAction("Run &Complete Group Analysis", self)
        run_complete_action.triggered.connect(self.run_complete_group_analysis)
        group_menu.addAction(run_complete_action)
        
        group_menu.addSeparator()
        
        # Run Group AHP
        run_group_ahp_action = QAction("Run Group &AHP Analysis", self)
        run_group_ahp_action.triggered.connect(self.run_group_ahp)
        group_menu.addAction(run_group_ahp_action)
        
        # Run Group TOPSIS
        run_group_topsis_action = QAction("Run Group &TOPSIS Analysis", self)
        run_group_topsis_action.triggered.connect(self.run_group_topsis)
        group_menu.addAction(run_group_topsis_action)
        
        group_menu.addSeparator()
        
        # View Results
        view_results_action = QAction("View &Group Analysis Results", self)
        view_results_action.triggered.connect(self.view_group_results)
        group_menu.addAction(view_results_action)
        
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
        self.mcda_tab.clear()  # Clear MCDA tab as well
        
        # Disable MCDA tab at the tab level until new optimization results are loaded
        self.tab_widget.setTabEnabled(2, False)  # MCDA tab is at index 2
        
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
        print(f"🏁 Main Window: Optimization finished!")
        print(f"   - Results: {results is not None}")
        
        # Update UI state
        self.run_action.setEnabled(True)
        self.run_button.setEnabled(True)
        self.stop_action.setEnabled(False)
        self.stop_button.setEnabled(False)

        if results is not None:
            self.status_bar.showMessage("Optimization completed successfully")
            
            # Pass results to MCDA tab for analysis
            try:
                # Get objectives information from problem tab
                problem_config = self.problem_tab.get_configuration()
                objectives_info = problem_config.get('objectives', [])
                
                print(f"   - Problem config objectives: {len(objectives_info)}")
                print(f"   - Objective details: {objectives_info}")
                
                # Set optimization results in MCDA tab
                self.mcda_tab.set_optimization_results(results, objectives_info)
                
                # Switch to MCDA tab to show analysis is available
                self.tab_widget.setTabEnabled(2, True)  # Enable MCDA tab
                print(f"   - MCDA tab enabled!")
                
                # Ask admin if they want to create a group decision session
                self._offer_group_session_creation(results, problem_config, objectives_info)
                
            except Exception as e:
                print(f"Warning: Could not initialize MCDA analysis: {e}")
                import traceback
                traceback.print_exc()
        else:
            self.status_bar.showMessage("Optimization stopped")
            
        # Emit signal
        self.optimization_finished.emit(results)
    
    def _offer_group_session_creation(self, results, problem_config, objectives_info):
        """Ask admin if they want to create a group decision session from optimization results"""
        from PyQt6.QtWidgets import QInputDialog, QMessageBox
        
        # Ask if they want to create a group session
        reply = QMessageBox.question(
            self, 
            "Create Group Decision Session?",
            "Would you like to create a group decision session so other users can provide their preferences on these optimization results?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Get session name from user
            session_name, ok = QInputDialog.getText(
                self, 
                "Group Session Name", 
                "Enter a name for this group decision session:",
                text=f"Optimization Session {len(self.db_manager.get_active_sessions()) + 1}"
            )
            
            if ok and session_name.strip():
                try:
                    # Extract criteria names from objectives
                    criteria_names = [obj['name'] for obj in objectives_info]
                    
                    # Prepare alternatives data (optimization solutions)
                    alternatives_data = []
                    
                    # Handle PyMOO Result objects
                    if hasattr(results, 'F') and results.F is not None:
                        # PyMOO Result object - use F attribute for objective values
                        objective_values = results.F
                    elif isinstance(results, dict) and 'objective_values' in results:
                        # Dictionary format
                        objective_values = results['objective_values']
                    else:
                        objective_values = None
                    
                    if objective_values is not None:
                        for i, solution in enumerate(objective_values):
                            alt_data = {
                                'id': i + 1,
                                'name': f"Solution {i + 1}",
                                'values': solution.tolist() if hasattr(solution, 'tolist') else list(solution)
                            }
                            alternatives_data.append(alt_data)
                    
                    # Convert optimization results to JSON-serializable format
                    json_serializable_results = self._make_json_serializable(results)
                    
                    # Create the session (assuming admin user ID is 1 for now)
                    admin_user_id = 1  # TODO: Get from authentication system
                    session_id = self.db_manager.create_session(
                        session_name=session_name.strip(),
                        problem_name=problem_config.get('problem_name', 'Unnamed Problem'),
                        criteria_names=criteria_names,
                        objectives_info=objectives_info,
                        created_by_user_id=admin_user_id,
                        optimization_results=json_serializable_results,
                        alternatives_data=alternatives_data
                    )
                    
                    QMessageBox.information(
                        self,
                        "Session Created",
                        f"Group decision session '{session_name}' has been created successfully.\n\n"
                        f"Session ID: {session_id}\n"
                        f"Users can now log in and provide their preferences for the {len(alternatives_data)} optimization solutions."
                    )
                    
                    print(f"✅ Created group decision session: {session_name} (ID: {session_id})")
                    
                except Exception as e:
                    QMessageBox.warning(
                        self,
                        "Session Creation Failed",
                        f"Failed to create group decision session:\n{str(e)}"
                    )
                    print(f"❌ Failed to create session: {e}")
                    import traceback
                    traceback.print_exc()
    
    def _make_json_serializable(self, obj):
        """Convert numpy arrays and other non-serializable objects to JSON-compatible format"""
        import numpy as np
        from pymoo.core.result import Result
        
        if isinstance(obj, Result):
            # Handle PyMOO Result objects by extracting key attributes
            result_dict = {}
            
            # Extract main optimization results
            if hasattr(obj, 'X') and obj.X is not None:
                result_dict['X'] = self._make_json_serializable(obj.X)  # Decision variables
            if hasattr(obj, 'F') and obj.F is not None:
                result_dict['F'] = self._make_json_serializable(obj.F)  # Objective values
            if hasattr(obj, 'G') and obj.G is not None:
                result_dict['G'] = self._make_json_serializable(obj.G)  # Constraint values
            if hasattr(obj, 'CV') and obj.CV is not None:
                result_dict['CV'] = self._make_json_serializable(obj.CV)  # Constraint violations
            
            # Extract algorithm information
            if hasattr(obj, 'algorithm') and obj.algorithm is not None:
                # Only store basic algorithm info to avoid circular references
                result_dict['algorithm_name'] = str(type(obj.algorithm).__name__)
            
            # Extract problem information
            if hasattr(obj, 'problem') and obj.problem is not None:
                result_dict['problem_name'] = str(type(obj.problem).__name__)
                if hasattr(obj.problem, 'n_var'):
                    result_dict['n_var'] = obj.problem.n_var
                if hasattr(obj.problem, 'n_obj'):
                    result_dict['n_obj'] = obj.problem.n_obj
                if hasattr(obj.problem, 'n_constr'):
                    result_dict['n_constr'] = obj.problem.n_constr
            
            # Extract execution info
            if hasattr(obj, 'exec_time') and obj.exec_time is not None:
                result_dict['exec_time'] = float(obj.exec_time)
            if hasattr(obj, 'n_evals') and obj.n_evals is not None:
                result_dict['n_evals'] = int(obj.n_evals)
            
            return result_dict
            
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, dict):
            return {key: self._make_json_serializable(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._make_json_serializable(item) for item in obj]
        elif isinstance(obj, tuple):
            return list(self._make_json_serializable(list(obj)))
        elif isinstance(obj, (np.int64, np.int32)):
            return int(obj)
        elif isinstance(obj, (np.float64, np.float32)):
            return float(obj)
        elif hasattr(obj, 'item'):  # numpy scalars
            return obj.item()
        else:
            # For any other object types that might not be JSON serializable
            try:
                # Try to convert to string as fallback
                return str(obj)
            except:
                return None
        
    def on_problem_changed(self):
        """Handle problem configuration changes"""
        self.status_bar.showMessage("Problem configuration updated")
        
    def on_algorithm_changed(self):
        """Handle algorithm configuration changes"""
        self.status_bar.showMessage("Algorithm configuration updated")
    
    def view_group_sessions(self):
        """View and manage active group decision sessions"""
        try:
            from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QLabel
            
            dialog = QDialog(self)
            dialog.setWindowTitle("Group Decision Sessions")
            dialog.setMinimumSize(800, 500)
            
            layout = QVBoxLayout(dialog)
            
            # Instructions
            instructions = QLabel("""
            <b>Active Group Decision Sessions</b><br>
            Below are the sessions where users can provide their preferences. 
            Click on a session to see participation status and run group analysis when ready.
            """)
            instructions.setWordWrap(True)
            layout.addWidget(instructions)
            
            # Sessions table
            sessions_table = QTableWidget()
            sessions = self.db_manager.get_active_sessions()
            
            sessions_table.setRowCount(len(sessions))
            sessions_table.setColumnCount(6)
            sessions_table.setHorizontalHeaderLabels([
                "Session Name", "Problem", "Criteria Count", "Alternatives", "Created", "Status"
            ])
            
            for i, session in enumerate(sessions):
                sessions_table.setItem(i, 0, QTableWidgetItem(session['session_name']))
                sessions_table.setItem(i, 1, QTableWidgetItem(session['problem_name']))
                sessions_table.setItem(i, 2, QTableWidgetItem(str(len(session['criteria_names']))))
                
                alt_count = len(session['alternatives_data']) if session['alternatives_data'] else 0
                sessions_table.setItem(i, 3, QTableWidgetItem(str(alt_count)))
                sessions_table.setItem(i, 4, QTableWidgetItem(session['created_at']))
                
                # Check participation status
                status = self._get_session_participation_status(session['id'])
                sessions_table.setItem(i, 5, QTableWidgetItem(status))
            
            sessions_table.resizeColumnsToContents()
            layout.addWidget(sessions_table)
            
            # Buttons
            button_layout = QHBoxLayout()
            
            refresh_btn = QPushButton("Refresh")
            refresh_btn.clicked.connect(lambda: self._refresh_sessions_table(sessions_table))
            button_layout.addWidget(refresh_btn)
            
            button_layout.addStretch()
            
            close_btn = QPushButton("Close")
            close_btn.clicked.connect(dialog.close)
            button_layout.addWidget(close_btn)
            
            layout.addLayout(button_layout)
            
            dialog.exec()
            
        except Exception as e:
            QMessageBox.critical(
                self, 
                "Error Loading Sessions",
                f"Failed to load group decision sessions:\n\n{str(e)}\n\n"
                "This might be due to a database issue. Please check if the database is properly initialized."
            )
            print(f"Error in view_group_sessions: {e}")
            import traceback
            traceback.print_exc()
    
    def run_group_ahp(self):
        """Run group AHP analysis on selected session"""
        self._run_group_analysis('ahp')
    
    def run_group_topsis(self):
        """Run group TOPSIS analysis on selected session"""
        self._run_group_analysis('topsis')
    
    def run_complete_group_analysis(self):
        """Run complete group analysis (AHP + TOPSIS + Consensus)"""
        self._run_group_analysis('complete')
    
    def _run_group_analysis(self, method):
        """Run group decision analysis using specified method"""
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QComboBox, QLabel, QPushButton, QTextEdit
        
        # Get sessions with submitted comparisons
        sessions = self.db_manager.get_active_sessions()
        available_sessions = []
        
        for session in sessions:
            # Check if session has user submissions
            has_submissions = self._session_has_submissions(session['id'], method)
            if has_submissions:
                available_sessions.append(session)
        
        if not available_sessions:
            QMessageBox.information(
                self, 
                "No Sessions Available",
                f"No sessions have user submissions for {method.upper()} analysis yet.\n\n"
                "Users must submit their comparisons before group analysis can be performed."
            )
            return
        
        # Session selection dialog
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Run Group {method.upper()} Analysis")
        dialog.setMinimumSize(600, 400)
        
        layout = QVBoxLayout(dialog)
        
        # Instructions
        instructions = QLabel(f"""
        <b>Group {method.upper()} Analysis</b><br><br>
        Select a session to run group decision analysis. This will aggregate all user 
        comparisons and compute final rankings for the optimization alternatives.
        """)
        instructions.setWordWrap(True)
        layout.addWidget(instructions)
        
        # Session selection
        session_label = QLabel("Select Session:")
        layout.addWidget(session_label)
        
        session_combo = QComboBox()
        for session in available_sessions:
            session_combo.addItem(
                f"{session['session_name']} ({len(session['alternatives_data'] or [])} alternatives)",
                session['id']
            )
        layout.addWidget(session_combo)
        
        # Results area
        results_text = QTextEdit()
        results_text.setReadOnly(True)
        layout.addWidget(results_text)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        run_btn = QPushButton(f"Run {method.upper()} Analysis")
        run_btn.clicked.connect(lambda: self._execute_group_analysis(
            session_combo.currentData(), method, results_text
        ))
        button_layout.addWidget(run_btn)
        
        button_layout.addStretch()
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.close)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        
        dialog.exec()
    
    def _get_session_participation_status(self, session_id):
        """Get participation status for a session"""
        try:
            status = self.db_manager.get_session_status(session_id)
            
            if 'error' in status:
                return status['error']
            
            # Create a concise status string
            ahp_ready = "✅" if status['ready_for_ahp_analysis'] else "❌"
            topsis_ready = "✅" if status['ready_for_topsis_analysis'] else "❌"
            
            status_text = f"AHP: {status['ahp_submissions']}/{status['total_users']} {ahp_ready} | "
            status_text += f"TOPSIS: {status['topsis_submissions']}/{status['total_users']} {topsis_ready}"
            
            return status_text
            
        except Exception as e:
            return f"Error: {str(e)}"
    
    def _session_has_submissions(self, session_id, method):
        """Check if session has enough user submissions for the given method"""
        try:
            status = self.db_manager.get_session_status(session_id)
            
            if 'error' in status:
                return False
            
            if method == 'ahp':
                return status['ready_for_ahp_analysis']
            elif method == 'topsis':
                return status['ready_for_topsis_analysis']
            elif method == 'complete':
                # For complete analysis, we need both AHP and TOPSIS submissions
                return status['ready_for_ahp_analysis'] and status['ready_for_topsis_analysis']
            else:
                return False
                
        except Exception as e:
            print(f"Error checking session submissions: {e}")
            return False
    
    def _execute_group_analysis(self, session_id, method, results_text):
        """Execute the group decision analysis"""
        try:
            results_text.append(f"Starting {method.upper()} group analysis for session {session_id}...")
            results_text.append("Collecting user submissions...")
            
            # Get admin user ID (should be passed from authentication in future)
            admin_user_id = 1  # TODO: Get from authentication system
            
            if method == 'complete':
                # Run complete group decision analysis (AHP + TOPSIS + Consensus)
                results = self.db_manager.compute_group_decision(session_id, admin_user_id)
                self._display_complete_results(results, results_text)
                
            elif method == 'ahp':
                # Get AHP matrices only
                ahp_matrices = self.db_manager.get_session_ahp_comparisons(session_id)
                if not ahp_matrices:
                    results_text.append("❌ No AHP comparisons found for this session.")
                    return
                    
                # Get session data for alternatives
                sessions = self.db_manager.get_active_sessions()
                session = next((s for s in sessions if s['id'] == session_id), None)
                alternatives_data = session.get('alternatives_data', [])
                
                # Compute AHP group decision
                ahp_result = self.db_manager._compute_ahp_group_decision(ahp_matrices, alternatives_data)
                
                # Save results
                self.db_manager.save_group_result(
                    session_id=session_id,
                    method='AHP',
                    aggregated_data=ahp_result['aggregated_matrix'].tolist(),
                    final_scores=ahp_result['final_scores'],
                    final_rankings=ahp_result['rankings'],
                    computed_by_user_id=admin_user_id
                )
                
                self._display_ahp_results(ahp_result, results_text)
                
            elif method == 'topsis':
                # Get TOPSIS weights only
                topsis_weights = self.db_manager.get_session_topsis_weights(session_id)
                if not topsis_weights:
                    results_text.append("❌ No TOPSIS weights found for this session.")
                    return
                    
                # Get session data
                sessions = self.db_manager.get_active_sessions()
                session = next((s for s in sessions if s['id'] == session_id), None)
                alternatives_data = session.get('alternatives_data', [])
                
                # Compute TOPSIS group decision
                topsis_result = self.db_manager._compute_topsis_group_decision(topsis_weights, alternatives_data, session)
                
                # Save results
                self.db_manager.save_group_result(
                    session_id=session_id,
                    method='TOPSIS',
                    aggregated_data=topsis_result['aggregated_weights'],
                    final_scores=topsis_result['final_scores'],
                    final_rankings=topsis_result['rankings'],
                    computed_by_user_id=admin_user_id
                )
                
                self._display_topsis_results(topsis_result, results_text)
            
            results_text.append(f"\n✅ {method.upper()} group analysis completed successfully!")
            results_text.append(f"Results have been saved to the database.")
            
            QMessageBox.information(
                self,
                "Analysis Complete",
                f"Group {method.upper()} analysis completed!\n\n"
                f"The results have been saved to the database and displayed above."
            )
            
        except Exception as e:
            results_text.append(f"\n❌ Error during analysis: {str(e)}")
            import traceback
            traceback.print_exc()
            QMessageBox.warning(
                self,
                "Analysis Error", 
                f"Error during {method.upper()} analysis:\n{str(e)}"
            )
    
    def _display_complete_results(self, results, results_text):
        """Display complete group decision results"""
        results_text.append(f"\n{'='*60}")
        results_text.append(f"COMPLETE GROUP DECISION ANALYSIS RESULTS")
        results_text.append(f"{'='*60}")
        results_text.append(f"Session: {results['session_name']}")
        results_text.append(f"Alternatives: {results['alternatives_count']}")
        results_text.append(f"AHP Participants: {results['ahp_participants']}")
        results_text.append(f"TOPSIS Participants: {results['topsis_participants']}")
        results_text.append(f"Computed: {results['computed_at']}")
        
        if 'ahp_results' in results:
            results_text.append(f"\n{'='*40}")
            results_text.append("AHP GROUP RESULTS:")
            results_text.append(f"{'='*40}")
            self._display_ahp_results(results['ahp_results'], results_text, show_header=False)
        
        if 'topsis_results' in results:
            results_text.append(f"\n{'='*40}")
            results_text.append("TOPSIS GROUP RESULTS:")
            results_text.append(f"{'='*40}")
            self._display_topsis_results(results['topsis_results'], results_text, show_header=False)
        
        if 'consensus_results' in results:
            results_text.append(f"\n{'='*40}")
            results_text.append("CONSENSUS RESULTS:")
            results_text.append(f"{'='*40}")
            consensus = results['consensus_results']
            results_text.append(f"Method Correlation: {consensus['correlation_coefficient']:.3f}")
            results_text.append(f"Agreement Level: {consensus['agreement_level']}")
            results_text.append("\nFinal Rankings:")
            
            for i, (score, rank) in enumerate(zip(consensus['combined_scores'], consensus['final_rankings'])):
                results_text.append(f"  Alternative {i+1}: Score={score:.3f}, Rank={rank}")
    
    def _display_ahp_results(self, results, results_text, show_header=True):
        """Display AHP group decision results"""
        if show_header:
            results_text.append(f"\n{'='*40}")
            results_text.append("AHP GROUP ANALYSIS RESULTS")
            results_text.append(f"{'='*40}")
        
        results_text.append(f"Participants: {results['participants']}")
        results_text.append(f"Consistency Ratio: {results['consistency_ratio']:.3f}")
        results_text.append(f"Is Consistent: {'✅ Yes' if results['is_consistent'] else '❌ No'}")
        
        results_text.append("\nAggregated Criteria Weights:")
        for i, weight in enumerate(results['criteria_weights']):
            results_text.append(f"  Criterion {i+1}: {weight:.3f}")
        
        results_text.append("\nFinal Alternative Rankings:")
        for i, (score, rank) in enumerate(zip(results['final_scores'], results['rankings'])):
            results_text.append(f"  Alternative {i+1}: Score={score:.3f}, Rank={rank}")
    
    def _display_topsis_results(self, results, results_text, show_header=True):
        """Display TOPSIS group decision results"""
        if show_header:
            results_text.append(f"\n{'='*40}")
            results_text.append("TOPSIS GROUP ANALYSIS RESULTS")
            results_text.append(f"{'='*40}")
        
        results_text.append(f"Participants: {results['participants']}")
        
        results_text.append("\nAggregated Criteria Weights:")
        for i, weight in enumerate(results['aggregated_weights']):
            results_text.append(f"  Criterion {i+1}: {weight:.3f}")
        
        results_text.append("\nFinal Alternative Rankings:")
        for i, (score, rank) in enumerate(zip(results['final_scores'], results['rankings'])):
            results_text.append(f"  Alternative {i+1}: Closeness={score:.3f}, Rank={rank}")
    
    def view_group_results(self):
        """View previous group analysis results"""
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QComboBox, QLabel, QPushButton, QTextEdit
        
        # Get sessions that have results
        sessions = self.db_manager.get_active_sessions()
        sessions_with_results = []
        
        for session in sessions:
            results = self.db_manager.get_group_results(session['id'])
            if results:
                session['group_results'] = results
                sessions_with_results.append(session)
        
        if not sessions_with_results:
            QMessageBox.information(
                self,
                "No Results Available",
                "No group analysis results have been computed yet.\n\n"
                "Run group analysis on sessions with user submissions to generate results."
            )
            return
        
        # Results viewer dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Group Analysis Results")
        dialog.setMinimumSize(800, 600)
        
        layout = QVBoxLayout(dialog)
        
        # Instructions
        instructions = QLabel("""
        <b>Group Analysis Results Viewer</b><br><br>
        Select a session to view its group decision analysis results. Results include
        AHP rankings, TOPSIS rankings, and consensus rankings when available.
        """)
        instructions.setWordWrap(True)
        layout.addWidget(instructions)
        
        # Session selection
        session_label = QLabel("Select Session:")
        layout.addWidget(session_label)
        
        session_combo = QComboBox()
        for session in sessions_with_results:
            methods = list(session['group_results'].keys())
            session_combo.addItem(
                f"{session['session_name']} ({', '.join(methods)})",
                session
            )
        layout.addWidget(session_combo)
        
        # Results display
        results_text = QTextEdit()
        results_text.setReadOnly(True)
        results_text.setFont(QFont("Consolas", 10))
        layout.addWidget(results_text)
        
        # Load results button
        def load_results():
            session = session_combo.currentData()
            if session:
                self._display_saved_results(session, results_text)
        
        load_btn = QPushButton("Load Results")
        load_btn.clicked.connect(load_results)
        layout.addWidget(load_btn)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.close)
        layout.addWidget(close_btn)
        
        # Load first session by default
        if sessions_with_results:
            load_results()
        
        dialog.exec()
    
    def _display_saved_results(self, session, results_text):
        """Display saved group analysis results"""
        results_text.clear()
        
        results_text.append(f"{'='*80}")
        results_text.append(f"GROUP ANALYSIS RESULTS")
        results_text.append(f"{'='*80}")
        results_text.append(f"Session: {session['session_name']}")
        results_text.append(f"Problem: {session['problem_name']}")
        results_text.append(f"Alternatives: {len(session.get('alternatives_data', []))}")
        
        group_results = session['group_results']
        
        # Display each method's results
        for method, result in group_results.items():
            results_text.append(f"\n{'='*50}")
            results_text.append(f"{method} ANALYSIS RESULTS")
            results_text.append(f"{'='*50}")
            results_text.append(f"Computed: {result['computed_at']}")
            results_text.append(f"Computed by user ID: {result['computed_by']}")
            
            if result['final_scores'] and result['final_rankings']:
                results_text.append("\nFinal Rankings:")
                for i, (score, rank) in enumerate(zip(result['final_scores'], result['final_rankings'])):
                    results_text.append(f"  Alternative {i+1}: Score={score:.3f}, Rank={rank}")
            
            # Display method-specific data
            if method == 'CONSENSUS' and result['aggregated_data']:
                consensus_data = result['aggregated_data']
                if 'correlation_coefficient' in consensus_data:
                    results_text.append(f"\nCorrelation between methods: {consensus_data['correlation_coefficient']:.3f}")
                    results_text.append(f"Agreement level: {consensus_data.get('agreement_level', 'Unknown')}")
        
        results_text.append(f"\n{'='*80}")
        results_text.append("END OF RESULTS")
        results_text.append(f"{'='*80}")
    
    def _refresh_sessions_table(self, table):
        """Refresh the sessions table"""
        # Reload sessions and update table
        sessions = self.db_manager.get_active_sessions()
        table.setRowCount(len(sessions))
        
        for i, session in enumerate(sessions):
            table.setItem(i, 0, QTableWidgetItem(session['session_name']))
            table.setItem(i, 1, QTableWidgetItem(session['problem_name']))
            table.setItem(i, 2, QTableWidgetItem(str(len(session['criteria_names']))))
            
            alt_count = len(session['alternatives_data']) if session['alternatives_data'] else 0
            table.setItem(i, 3, QTableWidgetItem(str(alt_count)))
            table.setItem(i, 4, QTableWidgetItem(session['created_at']))
            
            status = self._get_session_participation_status(session['id'])
            table.setItem(i, 5, QTableWidgetItem(status))
        
        table.resizeColumnsToContents()
    
    def check_ready_sessions(self):
        """Check for sessions ready for group analysis and notify admin"""
        try:
            pending_sessions = self.db_manager.get_pending_sessions()
            
            if pending_sessions:
                session_names = [s['session_name'] for s in pending_sessions]
                
                QMessageBox.information(
                    self,
                    "Sessions Ready for Analysis",
                    f"The following sessions have enough participants for group decision analysis:\n\n"
                    f"• {chr(10).join(session_names)}\n\n"
                    f"You can run group AHP or TOPSIS analysis from the Group Decision menu."
                )
            else:
                QMessageBox.information(
                    self,
                    "No Ready Sessions",
                    "No sessions currently have enough participants for group analysis.\n\n"
                    "Sessions need at least 2 user submissions to run group decision analysis."
                )
        except Exception as e:
            QMessageBox.warning(
                self,
                "Check Failed",
                f"Failed to check session status: {str(e)}"
            )
        
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
