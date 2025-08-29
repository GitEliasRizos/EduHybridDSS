"""
Real-time Optimization Visualization Widget
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLabel, QProgressBar, QComboBox, QSpinBox, QCheckBox)
from PyQt6.QtCore import QTimer, pyqtSignal, QThread, pyqtSlot
from PyQt6.QtGui import QFont
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
from collections import deque


class OptimizationWorker(QThread):
    """Worker thread for running optimization with real-time updates"""
    
    progress_update = pyqtSignal(int, object, object)  # generation, X, F
    optimization_finished = pyqtSignal(object)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, optimizer, problem, algorithm, termination):
        super().__init__()
        self.optimizer = optimizer  # Can be None, not used in current implementation
        self.problem = problem
        self.algorithm = algorithm
        self.termination = termination
        self.is_running = True
        
    def run(self):
        """Run optimization with callbacks for real-time updates"""
        try:
            from pymoo.optimize import minimize
            from pymoo.core.callback import Callback
            
            class RealtimeCallback(Callback):
                def __init__(self, worker):
                    super().__init__()
                    self.worker = worker
                    
                def notify(self, algorithm):
                    if not self.worker.is_running:
                        # Set termination flag if available
                        if hasattr(algorithm, 'termination') and hasattr(algorithm.termination, 'force_termination'):
                            algorithm.termination.force_termination = True
                        return
                    
                    # Safely get population data
                    try:
                        if hasattr(algorithm, 'pop') and algorithm.pop is not None:
                            X = algorithm.pop.get("X")
                            F = algorithm.pop.get("F")
                            generation = getattr(algorithm, 'n_gen', 0)
                            
                            self.worker.progress_update.emit(generation, X, F)
                    except Exception as e:
                        print(f"Callback error: {e}")
            
            # Create callback
            callback = RealtimeCallback(self)
            
            # Run optimization with safety checks
            if self.problem is None or self.algorithm is None or self.termination is None:
                raise ValueError("Problem, algorithm, or termination not properly configured")
                
            result = minimize(
                self.problem, 
                self.algorithm, 
                self.termination, 
                callback=callback, 
                verbose=False,
                save_history=False  # Reduce memory usage
            )
            
            if self.is_running:
                self.optimization_finished.emit(result)
                
        except Exception as e:
            self.error_occurred.emit(f"Optimization failed: {str(e)}")
    
    def stop(self):
        """Stop the optimization"""
        self.is_running = False
        if self.isRunning():
            self.quit()
            self.wait(5000)  # Wait up to 5 seconds


class RealTimeVisualizationWidget(QWidget):
    """Widget for real-time optimization visualization"""
    
    def __init__(self):
        super().__init__()
        
        # Data storage - initialize first
        self.current_generation = 0
        self.max_generations = 100
        self.current_X = None
        self.current_F = None
        self.history_X = deque(maxlen=1000)  # Store last 1000 generations
        self.history_F = deque(maxlen=1000)
        self.history_metrics = deque(maxlen=1000)
        
        # Worker thread
        self.worker = None
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout()
        
        # Control panel
        control_panel = self.create_control_panel()
        layout.addWidget(control_panel)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Status label
        self.status_label = QLabel("Ready to start real-time optimization")
        font = QFont()
        font.setBold(True)
        self.status_label.setFont(font)
        layout.addWidget(self.status_label)
        
        # Matplotlib canvas
        self.create_plots()
        layout.addWidget(self.canvas)
        
        self.setLayout(layout)
        
    def create_control_panel(self):
        """Create control panel with settings"""
        panel = QWidget()
        layout = QHBoxLayout()
        
        # Update interval
        layout.addWidget(QLabel("Update Interval (ms):"))
        self.update_interval_spin = QSpinBox()
        self.update_interval_spin.setRange(100, 5000)
        self.update_interval_spin.setValue(500)
        layout.addWidget(self.update_interval_spin)
        
        # Plot type selection
        layout.addWidget(QLabel("Plot Type:"))
        self.plot_type_combo = QComboBox()
        self.plot_type_combo.addItems([
            "Objective Space", 
            "Convergence", 
            "Population Spread",
            "Best Solutions"
        ])
        self.plot_type_combo.currentTextChanged.connect(self.on_plot_type_changed)
        layout.addWidget(self.plot_type_combo)
        
        # Show history checkbox
        self.show_history_check = QCheckBox("Show History")
        self.show_history_check.setChecked(True)
        layout.addWidget(self.show_history_check)
        
        # Control buttons
        self.start_button = QPushButton("Start Real-time")
        self.start_button.clicked.connect(self.start_optimization)
        layout.addWidget(self.start_button)
        
        self.stop_button = QPushButton("Stop")
        self.stop_button.clicked.connect(self.stop_optimization)
        self.stop_button.setEnabled(False)
        layout.addWidget(self.stop_button)
        
        layout.addStretch()
        panel.setLayout(layout)
        return panel
        
    def create_plots(self):
        """Create matplotlib plots"""
        self.figure = Figure(figsize=(12, 8))
        self.canvas = FigureCanvas(self.figure)
        
        # Create subplots
        self.ax_main = self.figure.add_subplot(221)
        self.ax_convergence = self.figure.add_subplot(222)
        self.ax_spread = self.figure.add_subplot(223)
        self.ax_metrics = self.figure.add_subplot(224)
        
        self.figure.tight_layout()
        
        # Initialize plots
        self.update_plots()
        
    def setup_optimization(self, problem, algorithm, termination):
        """Setup optimization parameters"""
        try:
            self.problem = problem
            self.algorithm = algorithm
            self.termination = termination
            
            # Estimate max generations more safely
            self.max_generations = 100  # Default
            
            if hasattr(termination, 'n_max_gen'):
                self.max_generations = termination.n_max_gen
            elif hasattr(termination, 'n_max_evals'):
                # Safely get population size
                pop_size = 100  # Default
                if hasattr(algorithm, 'pop_size'):
                    pop_size = algorithm.pop_size
                elif hasattr(algorithm, 'n_offsprings'):
                    pop_size = algorithm.n_offsprings
                    
                self.max_generations = max(1, termination.n_max_evals // pop_size)
            
            self.progress_bar.setMaximum(self.max_generations)
            self.start_button.setEnabled(True)
            
            # Reset any previous state
            self.current_generation = 0
            self.history_X.clear()
            self.history_F.clear()
            self.history_metrics.clear()
            
        except Exception as e:
            print(f"Setup error: {e}")
            self.status_label.setText(f"Setup error: {e}")
            self.start_button.setEnabled(False)
        
    def start_optimization(self):
        """Start real-time optimization"""
        if not hasattr(self, 'problem') or self.problem is None:
            self.status_label.setText("No problem configured for optimization")
            return
            
        try:
            # Reset data
            self.current_generation = 0
            self.history_X.clear()
            self.history_F.clear()
            self.history_metrics.clear()
            
            # Setup UI
            self.start_button.setEnabled(False)
            self.stop_button.setEnabled(True)
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)
            self.status_label.setText("Starting optimization...")
            
            # Create a fresh optimizer instance to avoid conflicts
            self.worker = OptimizationWorker(None, self.problem, self.algorithm, self.termination)
            self.worker.progress_update.connect(self.on_progress_update)
            self.worker.optimization_finished.connect(self.on_optimization_finished)
            self.worker.error_occurred.connect(self.on_error_occurred)
            
            # Start the worker
            self.worker.start()
            
        except Exception as e:
            self.status_label.setText(f"Failed to start optimization: {str(e)}")
            self.start_button.setEnabled(True)
            self.stop_button.setEnabled(False)
            self.progress_bar.setVisible(False)
        
    def stop_optimization(self):
        """Stop the optimization"""
        if self.worker:
            self.worker.stop()
            self.worker = None
            
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.progress_bar.setVisible(False)
        self.status_label.setText("Optimization stopped")
        
    @pyqtSlot(int, object, object)
    def on_progress_update(self, generation, X, F):
        """Handle progress update from optimization"""
        try:
            self.current_generation = generation
            self.current_X = X
            self.current_F = F
            
            # Store in history with safety checks
            if X is not None and F is not None and len(X) > 0 and len(F) > 0:
                self.history_X.append(X.copy())
                self.history_F.append(F.copy())
                
                # Calculate metrics if possible
                try:
                    metrics = self.calculate_metrics(F)
                    self.history_metrics.append(metrics)
                except Exception as e:
                    print(f"Metrics calculation error: {e}")
            
            # Update progress safely
            if self.progress_bar.maximum() > 0:
                progress_value = min(generation, self.progress_bar.maximum())
                self.progress_bar.setValue(progress_value)
            
            # Update status
            solution_count = len(X) if X is not None else 0
            self.status_label.setText(f"Generation {generation}/{self.max_generations} - {solution_count} solutions")
            
            # Update plots with error handling
            try:
                self.update_plots()
            except Exception as e:
                print(f"Plot update error: {e}")
                
        except Exception as e:
            print(f"Progress update error: {e}")
            self.status_label.setText(f"Progress update error: {e}")
        
    @pyqtSlot(object)
    def on_optimization_finished(self, result):
        """Handle optimization completion"""
        self.status_label.setText(f"Optimization completed - Final generation: {self.current_generation}")
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.progress_bar.setVisible(False)
        
    @pyqtSlot(str)
    def on_error_occurred(self, error_msg):
        """Handle optimization error"""
        self.status_label.setText(f"Error: {error_msg}")
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.progress_bar.setVisible(False)
        
    def calculate_metrics(self, F):
        """Calculate optimization metrics"""
        metrics = {}
        
        if F is not None and len(F) > 0:
            # Basic metrics
            metrics['mean'] = np.mean(F, axis=0)
            metrics['std'] = np.std(F, axis=0)
            metrics['min'] = np.min(F, axis=0)
            metrics['max'] = np.max(F, axis=0)
            
            # Hypervolume approximation (simple version)
            if F.shape[1] == 2:  # Only for 2 objectives
                ref_point = np.max(F, axis=0) + 1
                hv = self.approximate_hypervolume_2d(F, ref_point)
                metrics['hypervolume'] = hv
                
        return metrics
        
    def approximate_hypervolume_2d(self, F, ref_point):
        """Approximate hypervolume for 2D objectives"""
        if len(F) == 0:
            return 0
        
        # Sort by first objective
        sorted_F = F[np.argsort(F[:, 0])]
        
        hv = 0
        for i, point in enumerate(sorted_F):
            if i == 0:
                width = ref_point[0] - point[0]
            else:
                width = sorted_F[i-1][0] - point[0]
            height = ref_point[1] - point[1]
            
            if width > 0 and height > 0:
                hv += width * height
                
        return hv
        
    def update_plots(self):
        """Update all plots with current data"""
        try:
            self.figure.clear()
            
            plot_type = self.plot_type_combo.currentText()
            
            if plot_type == "Objective Space":
                self.plot_objective_space()
            elif plot_type == "Convergence":
                self.plot_convergence()
            elif plot_type == "Population Spread":
                self.plot_population_spread()
            elif plot_type == "Best Solutions":
                self.plot_best_solutions()
            
            # Draw with error handling    
            try:
                self.canvas.draw()
            except Exception as e:
                print(f"Canvas draw error: {e}")
                
        except Exception as e:
            print(f"Plot update error: {e}")
            # Create a simple error plot
            try:
                ax = self.figure.add_subplot(111)
                ax.text(0.5, 0.5, f'Plot error: {str(e)}', 
                       ha='center', va='center', transform=ax.transAxes)
                ax.set_title('Plot Error')
                self.canvas.draw()
            except:
                pass  # If even error plotting fails, just continue
        
    def plot_objective_space(self):
        """Plot current population in objective space"""
        try:
            ax = self.figure.add_subplot(111)
            
            if self.current_F is not None:
                F = self.current_F
                
                if F.shape[1] >= 2:
                    # 2D or higher dimensional plot
                    ax.scatter(F[:, 0], F[:, 1], alpha=0.7, s=30, c='blue', label='Current Population')
                    
                    # Show history if enabled
                    if self.show_history_check.isChecked() and len(self.history_F) > 1:
                        for i, hist_F in enumerate(list(self.history_F)[::5]):  # Every 5th generation
                            alpha = 0.1 + 0.3 * (i / len(self.history_F))
                            ax.scatter(hist_F[:, 0], hist_F[:, 1], alpha=alpha, s=10, c='gray')
                    
                    ax.set_xlabel('Objective 1')
                    ax.set_ylabel('Objective 2')
                    ax.set_title(f'Objective Space - Generation {self.current_generation}')
                    ax.grid(True, alpha=0.3)
                    ax.legend()
                else:
                    # Single objective
                    ax.hist(F[:, 0], bins=20, alpha=0.7)
                    ax.set_xlabel('Objective Value')
                    ax.set_ylabel('Frequency')
                    ax.set_title(f'Objective Distribution - Generation {self.current_generation}')
                    ax.grid(True, alpha=0.3)
            else:
                ax.text(0.5, 0.5, 'No data available', ha='center', va='center', transform=ax.transAxes)
                ax.set_title('Objective Space')
                
        except Exception as e:
            print(f"Objective space plot error: {e}")
            try:
                ax = self.figure.add_subplot(111)
                ax.text(0.5, 0.5, f'Plot error: {str(e)}', 
                       ha='center', va='center', transform=ax.transAxes)
                ax.set_title('Objective Space - Error')
            except:
                pass  # If even error plotting fails, continue
            
    def plot_convergence(self):
        """Plot convergence metrics over time"""
        try:
            ax = self.figure.add_subplot(111)
            
            if len(self.history_metrics) > 0:
                generations = list(range(len(self.history_metrics)))
                
                # Plot mean objective values
                means = [m.get('mean', [0, 0]) for m in self.history_metrics]
                if len(means[0]) >= 2:
                    means_array = np.array(means)
                    ax.plot(generations, means_array[:, 0], label='Obj 1 Mean', linewidth=2)
                    ax.plot(generations, means_array[:, 1], label='Obj 2 Mean', linewidth=2)
                
                # Plot hypervolume if available
                hv_values = [m.get('hypervolume', 0) for m in self.history_metrics if 'hypervolume' in m]
                if hv_values:
                    ax2 = ax.twinx()
                    ax2.plot(generations[:len(hv_values)], hv_values, 'r--', label='Hypervolume', linewidth=2)
                    ax2.set_ylabel('Hypervolume', color='red')
                    ax2.legend(loc='upper right')
                
                ax.set_xlabel('Generation')
                ax.set_ylabel('Objective Values')
                ax.set_title('Convergence Progress')
                ax.grid(True, alpha=0.3)
                ax.legend(loc='upper left')
            else:
                ax.text(0.5, 0.5, 'No convergence data available', ha='center', va='center', transform=ax.transAxes)
                ax.set_title('Convergence Progress')
                
        except Exception as e:
            print(f"Convergence plot error: {e}")
            try:
                ax = self.figure.add_subplot(111)
                ax.text(0.5, 0.5, f'Plot error: {str(e)}', 
                       ha='center', va='center', transform=ax.transAxes)
                ax.set_title('Convergence Progress - Error')
            except:
                pass  # If even error plotting fails, continue
            
    def plot_population_spread(self):
        """Plot population spread over time"""
        ax = self.figure.add_subplot(111)
        
        if len(self.history_metrics) > 0:
            generations = list(range(len(self.history_metrics)))
            
            # Plot standard deviation as measure of spread
            stds = [m.get('std', [0, 0]) for m in self.history_metrics]
            if len(stds[0]) >= 2:
                stds_array = np.array(stds)
                ax.plot(generations, stds_array[:, 0], label='Obj 1 Std Dev', linewidth=2)
                ax.plot(generations, stds_array[:, 1], label='Obj 2 Std Dev', linewidth=2)
                
                ax.set_xlabel('Generation')
                ax.set_ylabel('Standard Deviation')
                ax.set_title('Population Spread')
                ax.grid(True, alpha=0.3)
                ax.legend()
        else:
            ax.text(0.5, 0.5, 'No spread data available', ha='center', va='center', transform=ax.transAxes)
            ax.set_title('Population Spread')
            
    def plot_best_solutions(self):
        """Plot evolution of best solutions"""
        ax = self.figure.add_subplot(111)
        
        if len(self.history_F) > 0:
            generations = list(range(len(self.history_F)))
            
            # Extract best solutions per generation
            best_obj1 = []
            best_obj2 = []
            
            for F in self.history_F:
                if F.shape[1] >= 2:
                    best_obj1.append(np.min(F[:, 0]))
                    best_obj2.append(np.min(F[:, 1]))
            
            if best_obj1 and best_obj2:
                ax.plot(generations, best_obj1, label='Best Obj 1', linewidth=2, marker='o', markersize=3)
                ax.plot(generations, best_obj2, label='Best Obj 2', linewidth=2, marker='s', markersize=3)
                
                ax.set_xlabel('Generation')
                ax.set_ylabel('Best Objective Values')
                ax.set_title('Best Solutions Evolution')
                ax.grid(True, alpha=0.3)
                ax.legend()
        else:
            ax.text(0.5, 0.5, 'No best solutions data available', ha='center', va='center', transform=ax.transAxes)
            ax.set_title('Best Solutions Evolution')
            
    def on_plot_type_changed(self, plot_type):
        """Handle plot type change"""
        self.update_plots()
