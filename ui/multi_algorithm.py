"""
Multi-Algorithm Comparison Widget
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                            QLabel, QTableWidget, QTableWidgetItem, QTabWidget,
                            QGroupBox, QCheckBox, QSpinBox, QComboBox, QProgressBar,
                            QTextEdit, QSplitter, QHeaderView)
from PyQt6.QtCore import QTimer, pyqtSignal, QThread, pyqtSlot, Qt
from PyQt6.QtGui import QFont, QColor
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
import pandas as pd
from datetime import datetime
import json


class MultiAlgorithmWorker(QThread):
    """Worker thread for running multiple algorithms simultaneously"""
    
    algorithm_finished = pyqtSignal(str, object, float)  # algorithm_name, result, runtime
    all_finished = pyqtSignal()
    error_occurred = pyqtSignal(str, str)  # algorithm_name, error_msg
    progress_update = pyqtSignal(str, int)  # algorithm_name, progress
    
    def __init__(self, problem, algorithm_configs, termination):
        super().__init__()
        self.problem = problem
        self.algorithm_configs = algorithm_configs
        self.termination = termination
        self.is_running = True
        
    def run(self):
        """Run multiple algorithms and compare results"""
        import time
        from pymoo.optimize import minimize
        from core.optimizer import Optimizer
        from core.algorithm_manager import AlgorithmManager
        
        optimizer = Optimizer()
        alg_manager = AlgorithmManager()
        
        for alg_name, config in self.algorithm_configs.items():
            if not self.is_running:
                break
                
            try:
                start_time = time.time()
                
                # Create algorithm
                algorithm = alg_manager.create_algorithm_from_config(
                    config, 
                    n_objectives=len(self.problem.n_obj) if hasattr(self.problem, 'n_obj') else 2
                )
                
                # Run optimization
                result = minimize(self.problem, algorithm, self.termination, verbose=False)
                
                runtime = time.time() - start_time
                
                if self.is_running:
                    self.algorithm_finished.emit(alg_name, result, runtime)
                    
            except Exception as e:
                if self.is_running:
                    self.error_occurred.emit(alg_name, str(e))
        
        if self.is_running:
            self.all_finished.emit()
    
    def stop(self):
        """Stop all algorithm runs"""
        self.is_running = False
        self.wait()


class MultiAlgorithmComparisonWidget(QWidget):
    """Widget for comparing multiple optimization algorithms"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        
        # Data storage
        self.results = {}
        self.algorithm_configs = {}
        self.problem = None
        self.termination = None
        self.worker = None
        
    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout()
        
        # Title
        title_label = QLabel("Multi-Algorithm Comparison")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)
        
        # Create main splitter
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left panel - Algorithm configuration
        left_panel = self.create_algorithm_panel()
        main_splitter.addWidget(left_panel)
        
        # Right panel - Results
        right_panel = self.create_results_panel()
        main_splitter.addWidget(right_panel)
        
        # Set splitter proportions
        main_splitter.setSizes([400, 800])
        
        layout.addWidget(main_splitter)
        
        # Control buttons
        button_layout = QHBoxLayout()
        
        self.run_comparison_button = QPushButton("Run Comparison")
        self.run_comparison_button.clicked.connect(self.run_comparison)
        button_layout.addWidget(self.run_comparison_button)
        
        self.stop_button = QPushButton("Stop")
        self.stop_button.clicked.connect(self.stop_comparison)
        self.stop_button.setEnabled(False)
        button_layout.addWidget(self.stop_button)
        
        self.export_button = QPushButton("Export Results")
        self.export_button.clicked.connect(self.export_results)
        self.export_button.setEnabled(False)
        button_layout.addWidget(self.export_button)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        # Status bar
        self.status_label = QLabel("Ready to compare algorithms")
        layout.addWidget(self.status_label)
        
        self.setLayout(layout)
        
    def create_algorithm_panel(self):
        """Create algorithm selection and configuration panel"""
        panel = QGroupBox("Algorithm Selection")
        layout = QVBoxLayout()
        
        # Algorithm checkboxes with configurations
        self.algorithm_checks = {}
        
        algorithms = [
            ("NSGA-II", "Pareto-based"),
            ("NSGA-III", "Reference Point-based"),
            ("SPEA2", "Pareto-based"),
            ("MOEA/D", "Decomposition-based"),
            ("RVEA", "Reference Point-based")
        ]
        
        for alg_name, category in algorithms:
            group = QGroupBox(f"{alg_name} ({category})")
            group_layout = QVBoxLayout()
            
            # Enable checkbox
            check = QCheckBox(f"Include {alg_name}")
            check.setChecked(alg_name in ["NSGA-II", "NSGA-III"])  # Default selection
            self.algorithm_checks[alg_name] = check
            group_layout.addWidget(check)
            
            # Population size
            pop_layout = QHBoxLayout()
            pop_layout.addWidget(QLabel("Population:"))
            pop_spin = QSpinBox()
            pop_spin.setRange(20, 500)
            pop_spin.setValue(100)
            pop_spin.setObjectName(f"{alg_name}_population")
            pop_layout.addWidget(pop_spin)
            group_layout.addLayout(pop_layout)
            
            # Generations
            gen_layout = QHBoxLayout()
            gen_layout.addWidget(QLabel("Generations:"))
            gen_spin = QSpinBox()
            gen_spin.setRange(10, 1000)
            gen_spin.setValue(100)
            gen_spin.setObjectName(f"{alg_name}_generations")
            gen_layout.addWidget(gen_spin)
            group_layout.addLayout(gen_layout)
            
            group.setLayout(group_layout)
            layout.addWidget(group)
        
        # Comparison settings
        settings_group = QGroupBox("Comparison Settings")
        settings_layout = QVBoxLayout()
        
        # Number of runs per algorithm
        runs_layout = QHBoxLayout()
        runs_layout.addWidget(QLabel("Runs per algorithm:"))
        self.runs_spin = QSpinBox()
        self.runs_spin.setRange(1, 10)
        self.runs_spin.setValue(1)
        runs_layout.addWidget(self.runs_spin)
        settings_layout.addLayout(runs_layout)
        
        # Seed settings
        seed_layout = QHBoxLayout()
        self.use_different_seeds = QCheckBox("Use different seeds for each run")
        self.use_different_seeds.setChecked(True)
        settings_layout.addWidget(self.use_different_seeds)
        
        settings_group.setLayout(settings_layout)
        layout.addWidget(settings_group)
        
        layout.addStretch()
        panel.setLayout(layout)
        return panel
        
    def create_results_panel(self):
        """Create results display panel"""
        panel = QWidget()
        layout = QVBoxLayout()
        
        # Create tabs for different result views
        self.results_tabs = QTabWidget()
        
        # Summary table tab
        self.create_summary_tab()
        
        # Comparison plots tab
        self.create_plots_tab()
        
        # Statistical analysis tab
        self.create_statistics_tab()
        
        # Detailed results tab
        self.create_details_tab()
        
        layout.addWidget(self.results_tabs)
        panel.setLayout(layout)
        return panel
        
    def create_summary_tab(self):
        """Create summary results table"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        self.summary_table = QTableWidget()
        self.summary_table.setColumnCount(7)
        self.summary_table.setHorizontalHeaderLabels([
            "Algorithm", "Runtime (s)", "Final HV", "Best Obj1", "Best Obj2", 
            "Solutions", "Status"
        ])
        
        # Make table fill available space
        header = self.summary_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        
        layout.addWidget(self.summary_table)
        
        tab.setLayout(layout)
        self.results_tabs.addTab(tab, "Summary")
        
    def create_plots_tab(self):
        """Create comparison plots"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Plot controls
        controls = QHBoxLayout()
        controls.addWidget(QLabel("Plot Type:"))
        
        self.plot_type_combo = QComboBox()
        self.plot_type_combo.addItems([
            "Objective Space Comparison",
            "Convergence Comparison", 
            "Hypervolume Comparison",
            "Runtime Comparison",
            "Solution Distribution"
        ])
        self.plot_type_combo.currentTextChanged.connect(self.update_comparison_plots)
        controls.addWidget(self.plot_type_combo)
        
        controls.addStretch()
        layout.addLayout(controls)
        
        # Matplotlib canvas
        self.comparison_figure = Figure(figsize=(12, 8))
        self.comparison_canvas = FigureCanvas(self.comparison_figure)
        layout.addWidget(self.comparison_canvas)
        
        tab.setLayout(layout)
        self.results_tabs.addTab(tab, "Plots")
        
    def create_statistics_tab(self):
        """Create statistical analysis tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        self.statistics_text = QTextEdit()
        self.statistics_text.setReadOnly(True)
        layout.addWidget(self.statistics_text)
        
        tab.setLayout(layout)
        self.results_tabs.addTab(tab, "Statistics")
        
    def create_details_tab(self):
        """Create detailed results tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        self.details_table = QTableWidget()
        layout.addWidget(self.details_table)
        
        tab.setLayout(layout)
        self.results_tabs.addTab(tab, "Details")
        
    def setup_comparison(self, problem, base_termination):
        """Setup comparison with problem and termination criteria"""
        self.problem = problem
        self.termination = base_termination
        self.run_comparison_button.setEnabled(True)
        
    def run_comparison(self):
        """Start multi-algorithm comparison"""
        if not self.problem:
            self.status_label.setText("No problem configured for comparison")
            return
        
        # Collect selected algorithms and their configurations
        self.algorithm_configs = {}
        
        for alg_name, check in self.algorithm_checks.items():
            if check.isChecked():
                # Find corresponding spin boxes
                pop_spin = self.findChild(QSpinBox, f"{alg_name}_population")
                gen_spin = self.findChild(QSpinBox, f"{alg_name}_generations")
                
                config = {
                    "name": alg_name,
                    "category": self.get_algorithm_category(alg_name),
                    "parameters": {
                        "population_size": pop_spin.value() if pop_spin else 100,
                        "n_generations": gen_spin.value() if gen_spin else 100,
                        "seed": 42
                    },
                    "crossover": {
                        "operator": "SBX (Simulated Binary Crossover)",
                        "probability": 0.9,
                        "eta": 15.0
                    },
                    "mutation": {
                        "operator": "Polynomial Mutation",
                        "probability": 0.1,
                        "eta": 20.0
                    }
                }
                
                # Add reference directions for algorithms that need them
                if alg_name in ["NSGA-III", "RVEA"]:
                    config["reference_directions"] = {
                        "method": "Das-Dennis",
                        "n_directions": 91,
                        "n_partitions": 12,
                        "scaling": 1.0
                    }
                
                self.algorithm_configs[alg_name] = config
        
        if not self.algorithm_configs:
            self.status_label.setText("Please select at least one algorithm")
            return
        
        # Clear previous results
        self.results = {}
        self.update_summary_table()
        
        # Setup UI
        self.run_comparison_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.export_button.setEnabled(False)
        
        self.status_label.setText(f"Running comparison with {len(self.algorithm_configs)} algorithms...")
        
        # Start worker thread
        self.worker = MultiAlgorithmWorker(self.problem, self.algorithm_configs, self.termination)
        self.worker.algorithm_finished.connect(self.on_algorithm_finished)
        self.worker.all_finished.connect(self.on_all_finished)
        self.worker.error_occurred.connect(self.on_algorithm_error)
        self.worker.start()
        
    def stop_comparison(self):
        """Stop the comparison"""
        if self.worker:
            self.worker.stop()
            self.worker = None
        
        self.run_comparison_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.status_label.setText("Comparison stopped")
        
    def get_algorithm_category(self, alg_name):
        """Get algorithm category"""
        categories = {
            "NSGA-II": "Pareto-based",
            "SPEA2": "Pareto-based",
            "NSGA-III": "Reference Point-based",
            "RVEA": "Reference Point-based",
            "MOEA/D": "Decomposition-based"
        }
        return categories.get(alg_name, "Unknown")
        
    @pyqtSlot(str, object, float)
    def on_algorithm_finished(self, alg_name, result, runtime):
        """Handle individual algorithm completion"""
        self.results[alg_name] = {
            'result': result,
            'runtime': runtime,
            'status': 'Completed',
            'X': result.X if hasattr(result, 'X') else None,
            'F': result.F if hasattr(result, 'F') else None,
            'n_evals': result.algorithm.evaluator.n_eval if hasattr(result, 'algorithm') else 0
        }
        
        self.update_summary_table()
        self.update_comparison_plots()
        
        completed = len([r for r in self.results.values() if r['status'] == 'Completed'])
        total = len(self.algorithm_configs)
        self.status_label.setText(f"Progress: {completed}/{total} algorithms completed")
        
    @pyqtSlot()
    def on_all_finished(self):
        """Handle completion of all algorithms"""
        self.run_comparison_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.export_button.setEnabled(True)
        
        self.status_label.setText(f"Comparison completed - {len(self.results)} algorithms finished")
        
        self.update_statistics()
        self.update_details_table()
        
    @pyqtSlot(str, str)
    def on_algorithm_error(self, alg_name, error_msg):
        """Handle algorithm error"""
        self.results[alg_name] = {
            'result': None,
            'runtime': 0,
            'status': f'Error: {error_msg}',
            'X': None,
            'F': None,
            'n_evals': 0
        }
        
        self.update_summary_table()
        
    def update_summary_table(self):
        """Update the summary results table"""
        self.summary_table.setRowCount(len(self.results))
        
        for i, (alg_name, data) in enumerate(self.results.items()):
            self.summary_table.setItem(i, 0, QTableWidgetItem(alg_name))
            self.summary_table.setItem(i, 1, QTableWidgetItem(f"{data['runtime']:.2f}"))
            
            if data['F'] is not None:
                # Calculate hypervolume (simplified)
                try:
                    hv = self.calculate_hypervolume(data['F'])
                    self.summary_table.setItem(i, 2, QTableWidgetItem(f"{hv:.4f}"))
                except:
                    self.summary_table.setItem(i, 2, QTableWidgetItem("N/A"))
                
                # Best objectives
                best_obj1 = np.min(data['F'][:, 0]) if data['F'].shape[1] > 0 else 0
                best_obj2 = np.min(data['F'][:, 1]) if data['F'].shape[1] > 1 else 0
                
                self.summary_table.setItem(i, 3, QTableWidgetItem(f"{best_obj1:.4f}"))
                self.summary_table.setItem(i, 4, QTableWidgetItem(f"{best_obj2:.4f}"))
                self.summary_table.setItem(i, 5, QTableWidgetItem(str(len(data['F']))))
            else:
                for j in range(2, 6):
                    self.summary_table.setItem(i, j, QTableWidgetItem("N/A"))
            
            # Status with color coding
            status_item = QTableWidgetItem(data['status'])
            if data['status'] == 'Completed':
                status_item.setBackground(QColor(144, 238, 144))  # Light green
            elif 'Error' in data['status']:
                status_item.setBackground(QColor(255, 182, 193))  # Light red
            
            self.summary_table.setItem(i, 6, status_item)
    
    def calculate_hypervolume(self, F):
        """Calculate hypervolume (simplified 2D version)"""
        if F is None or len(F) == 0 or F.shape[1] < 2:
            return 0
        
        # Use maximum values as reference point
        ref_point = np.max(F, axis=0) * 1.1
        
        # Sort by first objective
        sorted_indices = np.argsort(F[:, 0])
        sorted_F = F[sorted_indices]
        
        hv = 0
        prev_x = 0
        
        for point in sorted_F:
            width = ref_point[0] - point[0]
            height = ref_point[1] - point[1]
            
            if width > 0 and height > 0:
                hv += width * height - prev_x * height
                prev_x = ref_point[0] - point[0]
        
        return hv
    
    def update_comparison_plots(self):
        """Update comparison plots"""
        if not self.results:
            return
        
        plot_type = self.plot_type_combo.currentText()
        self.comparison_figure.clear()
        
        if plot_type == "Objective Space Comparison":
            self.plot_objective_space_comparison()
        elif plot_type == "Convergence Comparison":
            self.plot_convergence_comparison()
        elif plot_type == "Hypervolume Comparison":
            self.plot_hypervolume_comparison()
        elif plot_type == "Runtime Comparison":
            self.plot_runtime_comparison()
        elif plot_type == "Solution Distribution":
            self.plot_solution_distribution()
        
        self.comparison_canvas.draw()
    
    def plot_objective_space_comparison(self):
        """Plot objective spaces for all algorithms"""
        ax = self.comparison_figure.add_subplot(111)
        
        colors = plt.cm.tab10(np.linspace(0, 1, len(self.results)))
        
        for (alg_name, data), color in zip(self.results.items(), colors):
            if data['F'] is not None and data['status'] == 'Completed':
                F = data['F']
                if F.shape[1] >= 2:
                    ax.scatter(F[:, 0], F[:, 1], alpha=0.6, s=20, 
                              color=color, label=alg_name)
        
        ax.set_xlabel('Objective 1')
        ax.set_ylabel('Objective 2') 
        ax.set_title('Objective Space Comparison')
        ax.legend()
        ax.grid(True, alpha=0.3)
    
    def plot_runtime_comparison(self):
        """Plot runtime comparison"""
        ax = self.comparison_figure.add_subplot(111)
        
        algorithms = []
        runtimes = []
        
        for alg_name, data in self.results.items():
            if data['status'] == 'Completed':
                algorithms.append(alg_name)
                runtimes.append(data['runtime'])
        
        if algorithms:
            bars = ax.bar(algorithms, runtimes, color='skyblue', alpha=0.7)
            ax.set_ylabel('Runtime (seconds)')
            ax.set_title('Runtime Comparison')
            ax.tick_params(axis='x', rotation=45)
            
            # Add value labels on bars
            for bar, runtime in zip(bars, runtimes):
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                       f'{runtime:.2f}s', ha='center', va='bottom')
    
    def plot_hypervolume_comparison(self):
        """Plot hypervolume comparison"""
        ax = self.comparison_figure.add_subplot(111)
        
        algorithms = []
        hypervolumes = []
        
        for alg_name, data in self.results.items():
            if data['F'] is not None and data['status'] == 'Completed':
                try:
                    hv = self.calculate_hypervolume(data['F'])
                    algorithms.append(alg_name)
                    hypervolumes.append(hv)
                except:
                    pass
        
        if algorithms:
            bars = ax.bar(algorithms, hypervolumes, color='lightcoral', alpha=0.7)
            ax.set_ylabel('Hypervolume')
            ax.set_title('Hypervolume Comparison (Higher is Better)')
            ax.tick_params(axis='x', rotation=45)
            
            # Add value labels on bars
            for bar, hv in zip(bars, hypervolumes):
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                       f'{hv:.3f}', ha='center', va='bottom')
    
    def plot_convergence_comparison(self):
        """Plot convergence comparison (placeholder)"""
        ax = self.comparison_figure.add_subplot(111)
        ax.text(0.5, 0.5, 'Convergence comparison\nrequires tracking during optimization', 
                ha='center', va='center', transform=ax.transAxes, fontsize=12)
        ax.set_title('Convergence Comparison')
    
    def plot_solution_distribution(self):
        """Plot solution count distribution"""
        ax = self.comparison_figure.add_subplot(111)
        
        algorithms = []
        solution_counts = []
        
        for alg_name, data in self.results.items():
            if data['F'] is not None and data['status'] == 'Completed':
                algorithms.append(alg_name)
                solution_counts.append(len(data['F']))
        
        if algorithms:
            bars = ax.bar(algorithms, solution_counts, color='lightgreen', alpha=0.7)
            ax.set_ylabel('Number of Solutions')
            ax.set_title('Solution Count Comparison')
            ax.tick_params(axis='x', rotation=45)
            
            # Add value labels on bars
            for bar, count in zip(bars, solution_counts):
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                       str(count), ha='center', va='bottom')
    
    def update_statistics(self):
        """Update statistical analysis"""
        if not self.results:
            return
        
        stats_text = "Statistical Analysis\n" + "="*50 + "\n\n"
        
        completed_results = {k: v for k, v in self.results.items() 
                           if v['status'] == 'Completed' and v['F'] is not None}
        
        if not completed_results:
            stats_text += "No completed results available for analysis.\n"
            self.statistics_text.setPlainText(stats_text)
            return
        
        # Runtime analysis
        runtimes = [data['runtime'] for data in completed_results.values()]
        stats_text += f"Runtime Analysis:\n"
        stats_text += f"  Mean: {np.mean(runtimes):.3f} seconds\n"
        stats_text += f"  Std:  {np.std(runtimes):.3f} seconds\n"
        stats_text += f"  Min:  {np.min(runtimes):.3f} seconds\n"
        stats_text += f"  Max:  {np.max(runtimes):.3f} seconds\n\n"
        
        # Hypervolume analysis
        try:
            hypervolumes = {}
            for alg_name, data in completed_results.items():
                hv = self.calculate_hypervolume(data['F'])
                hypervolumes[alg_name] = hv
            
            if hypervolumes:
                stats_text += f"Hypervolume Analysis:\n"
                sorted_hv = sorted(hypervolumes.items(), key=lambda x: x[1], reverse=True)
                for i, (alg, hv) in enumerate(sorted_hv):
                    stats_text += f"  {i+1}. {alg}: {hv:.4f}\n"
                stats_text += "\n"
        except Exception as e:
            stats_text += f"Hypervolume analysis failed: {e}\n\n"
        
        # Solution count analysis
        solution_counts = {alg: len(data['F']) for alg, data in completed_results.items()}
        stats_text += f"Solution Count Analysis:\n"
        for alg, count in solution_counts.items():
            stats_text += f"  {alg}: {count} solutions\n"
        stats_text += "\n"
        
        # Best objective values
        stats_text += f"Best Objective Values:\n"
        for alg_name, data in completed_results.items():
            F = data['F']
            if F.shape[1] >= 2:
                best_obj1 = np.min(F[:, 0])
                best_obj2 = np.min(F[:, 1])
                stats_text += f"  {alg_name}: Obj1={best_obj1:.4f}, Obj2={best_obj2:.4f}\n"
        
        self.statistics_text.setPlainText(stats_text)
    
    def update_details_table(self):
        """Update detailed results table"""
        if not self.results:
            return
        
        # Collect all solutions from all algorithms
        all_solutions = []
        
        for alg_name, data in self.results.items():
            if data['F'] is not None and data['status'] == 'Completed':
                F = data['F']
                X = data['X']
                
                for i in range(len(F)):
                    solution = [alg_name]
                    
                    # Add decision variables
                    if X is not None:
                        solution.extend(X[i].tolist())
                    
                    # Add objective values
                    solution.extend(F[i].tolist())
                    
                    all_solutions.append(solution)
        
        if all_solutions:
            # Setup table
            n_vars = len(all_solutions[0]) - 1 - (len(all_solutions[0]) - 1 - 2) if all_solutions else 0
            n_objs = 2  # Assume 2 objectives for now
            
            headers = ["Algorithm"] + [f"Var{i+1}" for i in range(n_vars)] + [f"Obj{i+1}" for i in range(n_objs)]
            
            self.details_table.setColumnCount(len(headers))
            self.details_table.setRowCount(len(all_solutions))
            self.details_table.setHorizontalHeaderLabels(headers)
            
            # Fill table
            for i, solution in enumerate(all_solutions):
                for j, value in enumerate(solution):
                    if isinstance(value, float):
                        item = QTableWidgetItem(f"{value:.4f}")
                    else:
                        item = QTableWidgetItem(str(value))
                    self.details_table.setItem(i, j, item)
    
    def export_results(self):
        """Export comparison results"""
        from PyQt6.QtWidgets import QFileDialog
        
        if not self.results:
            return
        
        filename, _ = QFileDialog.getSaveFileName(
            self, "Export Comparison Results", 
            f"comparison_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            "JSON files (*.json);;CSV files (*.csv);;All files (*.*)"
        )
        
        if filename:
            try:
                if filename.endswith('.json'):
                    self.export_to_json(filename)
                elif filename.endswith('.csv'):
                    self.export_to_csv(filename)
                
                self.status_label.setText(f"Results exported to {filename}")
            except Exception as e:
                self.status_label.setText(f"Export failed: {e}")
    
    def export_to_json(self, filename):
        """Export results to JSON"""
        export_data = {
            'timestamp': datetime.now().isoformat(),
            'algorithms': list(self.algorithm_configs.keys()),
            'results': {}
        }
        
        for alg_name, data in self.results.items():
            result_data = {
                'runtime': data['runtime'],
                'status': data['status'],
                'n_solutions': len(data['F']) if data['F'] is not None else 0
            }
            
            if data['F'] is not None:
                result_data['objectives'] = data['F'].tolist()
            if data['X'] is not None:
                result_data['variables'] = data['X'].tolist()
                
            export_data['results'][alg_name] = result_data
        
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2)
    
    def export_to_csv(self, filename):
        """Export summary results to CSV"""
        data = []
        
        for alg_name, result in self.results.items():
            row = {
                'Algorithm': alg_name,
                'Runtime': result['runtime'],
                'Status': result['status']
            }
            
            if result['F'] is not None:
                row['Solutions'] = len(result['F'])
                row['Best_Obj1'] = np.min(result['F'][:, 0]) if result['F'].shape[1] > 0 else None
                row['Best_Obj2'] = np.min(result['F'][:, 1]) if result['F'].shape[1] > 1 else None
                
                try:
                    row['Hypervolume'] = self.calculate_hypervolume(result['F'])
                except:
                    row['Hypervolume'] = None
                    
            data.append(row)
        
        df = pd.DataFrame(data)
        df.to_csv(filename, index=False)
