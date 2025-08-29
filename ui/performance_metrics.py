"""
Performance Metrics Dashboard
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QTableWidget, QTableWidgetItem, QTabWidget,
                            QGroupBox, QGridLayout, QComboBox, QPushButton,
                            QProgressBar, QTextEdit, QSplitter, QHeaderView)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QColor, QPalette
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
from scipy.spatial.distance import pdist
from scipy.stats import entropy
import warnings
warnings.filterwarnings('ignore')


class PerformanceMetricsWidget(QWidget):
    """Comprehensive performance metrics dashboard"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        
        # Data storage
        self.current_result = None
        self.metrics_history = []
        self.reference_point = None
        
    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout()
        
        # Title
        title_label = QLabel("Performance Metrics Dashboard")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)
        
        # Create main splitter
        main_splitter = QSplitter(Qt.Orientation.Vertical)
        
        # Top section - Key metrics overview
        overview_section = self.create_overview_section()
        main_splitter.addWidget(overview_section)
        
        # Bottom section - Detailed analysis
        details_section = self.create_details_section()
        main_splitter.addWidget(details_section)
        
        # Set splitter proportions
        main_splitter.setSizes([200, 600])
        
        layout.addWidget(main_splitter)
        
        # Control panel
        control_panel = self.create_control_panel()
        layout.addWidget(control_panel)
        
        self.setLayout(layout)
    
    def create_overview_section(self):
        """Create key metrics overview section"""
        section = QWidget()
        layout = QHBoxLayout()
        
        # Quality metrics
        quality_group = self.create_metric_group("Solution Quality", [
            ("Hypervolume", "hv_value", "Higher is better"),
            ("IGD (Inverted Gen. Distance)", "igd_value", "Lower is better"),
            ("Spacing", "spacing_value", "Lower is better"),
            ("Spread", "spread_value", "Higher is better")
        ])
        layout.addWidget(quality_group)
        
        # Convergence metrics
        convergence_group = self.create_metric_group("Convergence", [
            ("GD (Generational Distance)", "gd_value", "Lower is better"),
            ("Convergence Rate", "conv_rate_value", "Higher is better"),
            ("Stability Index", "stability_value", "Higher is better"),
            ("Progress Rate", "progress_value", "Higher is better")
        ])
        layout.addWidget(convergence_group)
        
        # Efficiency metrics
        efficiency_group = self.create_metric_group("Efficiency", [
            ("Runtime (s)", "runtime_value", "Lower is better"),
            ("Evaluations", "evals_value", "Context dependent"),
            ("Solutions Found", "solutions_value", "Higher is better"),
            ("Success Rate", "success_value", "Higher is better")
        ])
        layout.addWidget(efficiency_group)
        
        section.setLayout(layout)
        return section
    
    def create_metric_group(self, title, metrics):
        """Create a group of metrics"""
        group = QGroupBox(title)
        layout = QGridLayout()
        
        for i, (name, attr_name, description) in enumerate(metrics):
            # Metric name
            name_label = QLabel(name + ":")
            name_label.setAlignment(Qt.AlignmentFlag.AlignRight)
            layout.addWidget(name_label, i, 0)
            
            # Metric value
            value_label = QLabel("N/A")
            value_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
            value_label.setStyleSheet("font-weight: bold; color: #2E86C1;")
            setattr(self, attr_name, value_label)
            layout.addWidget(value_label, i, 1)
            
            # Description tooltip
            value_label.setToolTip(description)
            name_label.setToolTip(description)
        
        group.setLayout(layout)
        return group
    
    def create_details_section(self):
        """Create detailed analysis section"""
        section = QTabWidget()
        
        # Pareto front analysis
        self.create_pareto_analysis_tab(section)
        
        # Distribution analysis
        self.create_distribution_analysis_tab(section)
        
        # Convergence analysis
        self.create_convergence_analysis_tab(section)
        
        # Robustness analysis
        self.create_robustness_analysis_tab(section)
        
        return section
    
    def create_pareto_analysis_tab(self, parent):
        """Create Pareto front analysis tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Controls
        controls = QHBoxLayout()
        controls.addWidget(QLabel("Analysis Type:"))
        
        self.pareto_analysis_combo = QComboBox()
        self.pareto_analysis_combo.addItems([
            "Pareto Front Visualization",
            "Dominance Analysis", 
            "Knee Points Detection",
            "Pareto Optimal Ranking",
            "Reference Point Analysis"
        ])
        self.pareto_analysis_combo.currentTextChanged.connect(self.update_pareto_analysis)
        controls.addWidget(self.pareto_analysis_combo)
        
        controls.addStretch()
        layout.addLayout(controls)
        
        # Plot canvas
        self.pareto_figure = Figure(figsize=(10, 6))
        self.pareto_canvas = FigureCanvas(self.pareto_figure)
        layout.addWidget(self.pareto_canvas)
        
        tab.setLayout(layout)
        parent.addTab(tab, "Pareto Analysis")
    
    def create_distribution_analysis_tab(self, parent):
        """Create solution distribution analysis tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Controls
        controls = QHBoxLayout()
        controls.addWidget(QLabel("Distribution Metric:"))
        
        self.distribution_combo = QComboBox()
        self.distribution_combo.addItems([
            "Objective Space Distribution",
            "Decision Space Distribution",
            "Density Analysis",
            "Clustering Analysis",
            "Diversity Metrics"
        ])
        self.distribution_combo.currentTextChanged.connect(self.update_distribution_analysis)
        controls.addWidget(self.distribution_combo)
        
        controls.addStretch()
        layout.addLayout(controls)
        
        # Plot canvas
        self.distribution_figure = Figure(figsize=(10, 6))
        self.distribution_canvas = FigureCanvas(self.distribution_figure)
        layout.addWidget(self.distribution_canvas)
        
        tab.setLayout(layout)
        parent.addTab(tab, "Distribution")
    
    def create_convergence_analysis_tab(self, parent):
        """Create convergence analysis tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Convergence metrics table
        self.convergence_table = QTableWidget()
        self.convergence_table.setColumnCount(3)
        self.convergence_table.setHorizontalHeaderLabels(["Metric", "Value", "Interpretation"])
        layout.addWidget(self.convergence_table)
        
        # Convergence plot
        self.convergence_figure = Figure(figsize=(10, 4))
        self.convergence_canvas = FigureCanvas(self.convergence_figure)
        layout.addWidget(self.convergence_canvas)
        
        tab.setLayout(layout)
        parent.addTab(tab, "Convergence")
    
    def create_robustness_analysis_tab(self, parent):
        """Create robustness analysis tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Robustness metrics
        robustness_group = QGroupBox("Robustness Metrics")
        robustness_layout = QGridLayout()
        
        metrics = [
            ("Solution Stability", "Solution consistency across runs"),
            ("Parameter Sensitivity", "Sensitivity to parameter changes"), 
            ("Noise Tolerance", "Performance under noisy conditions"),
            ("Constraint Violation", "Degree of constraint satisfaction")
        ]
        
        for i, (name, description) in enumerate(metrics):
            robustness_layout.addWidget(QLabel(name + ":"), i, 0)
            value_label = QLabel("N/A")
            value_label.setToolTip(description)
            robustness_layout.addWidget(value_label, i, 1)
            setattr(self, f"robustness_{i}_value", value_label)
        
        robustness_group.setLayout(robustness_layout)
        layout.addWidget(robustness_group)
        
        # Robustness visualization
        self.robustness_figure = Figure(figsize=(10, 4))
        self.robustness_canvas = FigureCanvas(self.robustness_figure)
        layout.addWidget(self.robustness_canvas)
        
        tab.setLayout(layout)
        parent.addTab(tab, "Robustness")
    
    def create_control_panel(self):
        """Create control panel"""
        panel = QWidget()
        layout = QHBoxLayout()
        
        # Reference point settings
        layout.addWidget(QLabel("Reference Point:"))
        self.ref_point_combo = QComboBox()
        self.ref_point_combo.addItems([
            "Auto (Max values)", 
            "Nadir Point", 
            "Custom", 
            "Ideal Point"
        ])
        self.ref_point_combo.currentTextChanged.connect(self.update_reference_point)
        layout.addWidget(self.ref_point_combo)
        
        # Update button
        self.update_button = QPushButton("Update Metrics")
        self.update_button.clicked.connect(self.calculate_all_metrics)
        layout.addWidget(self.update_button)
        
        # Export button
        self.export_metrics_button = QPushButton("Export Metrics")
        self.export_metrics_button.clicked.connect(self.export_metrics)
        layout.addWidget(self.export_metrics_button)
        
        layout.addStretch()
        
        # Status
        self.metrics_status_label = QLabel("Ready to analyze results")
        layout.addWidget(self.metrics_status_label)
        
        panel.setLayout(layout)
        return panel
    
    def set_result(self, result):
        """Set optimization result for analysis"""
        self.current_result = result
        self.metrics_status_label.setText("Analyzing optimization result...")
        
        # Calculate metrics
        QTimer.singleShot(100, self.calculate_all_metrics)
    
    def calculate_all_metrics(self):
        """Calculate all performance metrics"""
        if not self.current_result or not hasattr(self.current_result, 'F'):
            self.metrics_status_label.setText("No valid result data available")
            return
        
        try:
            F = self.current_result.F
            X = getattr(self.current_result, 'X', None)
            
            if F is None or len(F) == 0:
                self.metrics_status_label.setText("No objective values available")
                return
            
            # Update reference point
            self.update_reference_point()
            
            # Calculate quality metrics
            self.calculate_quality_metrics(F)
            
            # Calculate convergence metrics
            self.calculate_convergence_metrics(F)
            
            # Calculate efficiency metrics
            self.calculate_efficiency_metrics()
            
            # Update visualizations
            self.update_all_visualizations(F, X)
            
            self.metrics_status_label.setText(f"Metrics calculated for {len(F)} solutions")
            
        except Exception as e:
            self.metrics_status_label.setText(f"Error calculating metrics: {str(e)}")
    
    def update_reference_point(self):
        """Update reference point based on selection"""
        if not self.current_result or not hasattr(self.current_result, 'F'):
            return
        
        F = self.current_result.F
        ref_type = self.ref_point_combo.currentText()
        
        if ref_type == "Auto (Max values)":
            self.reference_point = np.max(F, axis=0) * 1.1
        elif ref_type == "Nadir Point":
            self.reference_point = np.max(F, axis=0)
        elif ref_type == "Ideal Point":
            self.reference_point = np.min(F, axis=0) * 0.9
        else:  # Custom
            self.reference_point = np.max(F, axis=0) * 1.1
    
    def calculate_quality_metrics(self, F):
        """Calculate solution quality metrics"""
        try:
            # Hypervolume
            if F.shape[1] == 2 and self.reference_point is not None:
                hv = self.calculate_hypervolume_2d(F, self.reference_point)
                self.hv_value.setText(f"{hv:.4f}")
            else:
                self.hv_value.setText("N/A")
            
            # IGD (simplified - without true Pareto front)
            try:
                # Use ideal point as approximation
                ideal = np.min(F, axis=0)
                distances = np.sqrt(np.sum((F - ideal)**2, axis=1))
                igd = np.mean(distances)
                self.igd_value.setText(f"{igd:.4f}")
            except:
                self.igd_value.setText("N/A")
            
            # Spacing
            try:
                if len(F) > 1:
                    distances = pdist(F)
                    if len(distances) > 0:
                        mean_dist = np.mean(distances)
                        spacing = np.sqrt(np.mean((distances - mean_dist)**2))
                        self.spacing_value.setText(f"{spacing:.4f}")
                    else:
                        self.spacing_value.setText("N/A")
                else:
                    self.spacing_value.setText("N/A")
            except:
                self.spacing_value.setText("N/A")
            
            # Spread
            try:
                if F.shape[1] >= 2:
                    ranges = np.ptp(F, axis=0)  # Peak-to-peak range
                    spread = np.sqrt(np.sum(ranges**2))
                    self.spread_value.setText(f"{spread:.4f}")
                else:
                    self.spread_value.setText("N/A")
            except:
                self.spread_value.setText("N/A")
                
        except Exception as e:
            print(f"Quality metrics error: {e}")
    
    def calculate_convergence_metrics(self, F):
        """Calculate convergence metrics"""
        try:
            # Generational Distance (simplified)
            try:
                ideal = np.min(F, axis=0)
                gd = np.mean(np.sqrt(np.sum((F - ideal)**2, axis=1)))
                self.gd_value.setText(f"{gd:.4f}")
            except:
                self.gd_value.setText("N/A")
            
            # Convergence rate (placeholder)
            self.conv_rate_value.setText("N/A*")
            
            # Stability index (coefficient of variation)
            try:
                cv = np.std(F, axis=0) / (np.mean(F, axis=0) + 1e-10)
                stability = 1.0 / (1.0 + np.mean(cv))
                self.stability_value.setText(f"{stability:.4f}")
            except:
                self.stability_value.setText("N/A")
            
            # Progress rate (placeholder)
            self.progress_value.setText("N/A*")
            
        except Exception as e:
            print(f"Convergence metrics error: {e}")
    
    def calculate_efficiency_metrics(self):
        """Calculate efficiency metrics"""
        try:
            # Runtime
            if hasattr(self.current_result, 'exec_time'):
                self.runtime_value.setText(f"{self.current_result.exec_time:.3f}")
            else:
                self.runtime_value.setText("N/A")
            
            # Evaluations
            if hasattr(self.current_result, 'algorithm') and hasattr(self.current_result.algorithm, 'evaluator'):
                n_evals = self.current_result.algorithm.evaluator.n_eval
                self.evals_value.setText(f"{n_evals}")
            else:
                self.evals_value.setText("N/A")
            
            # Solutions found
            if hasattr(self.current_result, 'F') and self.current_result.F is not None:
                self.solutions_value.setText(f"{len(self.current_result.F)}")
            else:
                self.solutions_value.setText("0")
            
            # Success rate (placeholder)
            self.success_value.setText("N/A*")
            
        except Exception as e:
            print(f"Efficiency metrics error: {e}")
    
    def calculate_hypervolume_2d(self, F, ref_point):
        """Calculate 2D hypervolume"""
        if len(F) == 0:
            return 0.0
        
        # Sort by first objective
        sorted_indices = np.argsort(F[:, 0])
        sorted_F = F[sorted_indices]
        
        hv = 0.0
        prev_x = 0.0
        
        for point in sorted_F:
            if point[0] >= ref_point[0] or point[1] >= ref_point[1]:
                continue
                
            width = ref_point[0] - point[0]
            height = ref_point[1] - point[1]
            
            if width > 0 and height > 0:
                area = width * height
                overlap = max(0, prev_x * height)
                hv += area - overlap
                prev_x = max(prev_x, width)
        
        return hv
    
    def update_all_visualizations(self, F, X):
        """Update all visualization tabs"""
        self.update_pareto_analysis()
        self.update_distribution_analysis()
        self.update_convergence_visualization(F)
        self.update_robustness_analysis(F, X)
    
    def update_pareto_analysis(self):
        """Update Pareto analysis visualization"""
        if not self.current_result or not hasattr(self.current_result, 'F'):
            return
        
        F = self.current_result.F
        analysis_type = self.pareto_analysis_combo.currentText()
        
        self.pareto_figure.clear()
        
        if analysis_type == "Pareto Front Visualization":
            self.plot_pareto_front(F)
        elif analysis_type == "Dominance Analysis":
            self.plot_dominance_analysis(F)
        elif analysis_type == "Knee Points Detection":
            self.plot_knee_points(F)
        elif analysis_type == "Pareto Optimal Ranking":
            self.plot_pareto_ranking(F)
        elif analysis_type == "Reference Point Analysis":
            self.plot_reference_point_analysis(F)
        
        self.pareto_canvas.draw()
    
    def plot_pareto_front(self, F):
        """Plot Pareto front visualization"""
        ax = self.pareto_figure.add_subplot(111)
        
        if F.shape[1] >= 2:
            ax.scatter(F[:, 0], F[:, 1], alpha=0.7, s=50)
            
            # Find Pareto optimal solutions
            is_pareto = self.is_pareto_optimal(F)
            pareto_F = F[is_pareto]
            
            if len(pareto_F) > 0:
                # Sort Pareto solutions for line plot
                sorted_indices = np.argsort(pareto_F[:, 0])
                sorted_pareto = pareto_F[sorted_indices]
                
                ax.scatter(sorted_pareto[:, 0], sorted_pareto[:, 1], 
                          c='red', s=80, alpha=0.8, label='Pareto Optimal')
                ax.plot(sorted_pareto[:, 0], sorted_pareto[:, 1], 
                       'r--', alpha=0.6, linewidth=2)
            
            ax.set_xlabel('Objective 1')
            ax.set_ylabel('Objective 2')
            ax.set_title('Pareto Front Visualization')
            ax.legend()
            ax.grid(True, alpha=0.3)
    
    def plot_dominance_analysis(self, F):
        """Plot dominance relationship analysis"""
        ax = self.pareto_figure.add_subplot(111)
        
        if F.shape[1] >= 2:
            # Calculate dominance count for each solution
            dominance_counts = []
            for i in range(len(F)):
                count = 0
                for j in range(len(F)):
                    if i != j and self.dominates(F[j], F[i]):
                        count += 1
                dominance_counts.append(count)
            
            # Color-code by dominance
            scatter = ax.scatter(F[:, 0], F[:, 1], c=dominance_counts, 
                               cmap='RdYlBu_r', s=60, alpha=0.8)
            
            self.pareto_figure.colorbar(scatter, ax=ax, label='Times Dominated')
            ax.set_xlabel('Objective 1')
            ax.set_ylabel('Objective 2')
            ax.set_title('Dominance Analysis (Blue = Less Dominated)')
            ax.grid(True, alpha=0.3)
    
    def plot_knee_points(self, F):
        """Detect and plot knee points"""
        ax = self.pareto_figure.add_subplot(111)
        
        if F.shape[1] == 2:
            ax.scatter(F[:, 0], F[:, 1], alpha=0.6, s=40, label='All Solutions')
            
            # Simple knee point detection
            pareto_mask = self.is_pareto_optimal(F)
            pareto_F = F[pareto_mask]
            
            if len(pareto_F) > 2:
                # Sort by first objective
                sorted_indices = np.argsort(pareto_F[:, 0])
                sorted_pareto = pareto_F[sorted_indices]
                
                # Calculate curvature (simplified)
                knee_indices = self.find_knee_points(sorted_pareto)
                
                if len(knee_indices) > 0:
                    knee_points = sorted_pareto[knee_indices]
                    ax.scatter(knee_points[:, 0], knee_points[:, 1], 
                              c='red', s=100, marker='*', label='Knee Points')
            
            ax.set_xlabel('Objective 1')
            ax.set_ylabel('Objective 2')
            ax.set_title('Knee Points Detection')
            ax.legend()
            ax.grid(True, alpha=0.3)
    
    def plot_pareto_ranking(self, F):
        """Plot Pareto ranking visualization"""
        ax = self.pareto_figure.add_subplot(111)
        
        if F.shape[1] >= 2:
            # Calculate Pareto ranks
            ranks = self.calculate_pareto_ranks(F)
            
            scatter = ax.scatter(F[:, 0], F[:, 1], c=ranks, 
                               cmap='viridis', s=60, alpha=0.8)
            
            self.pareto_figure.colorbar(scatter, ax=ax, label='Pareto Rank')
            ax.set_xlabel('Objective 1')
            ax.set_ylabel('Objective 2')
            ax.set_title('Pareto Optimal Ranking (Lower Rank = Better)')
            ax.grid(True, alpha=0.3)
    
    def plot_reference_point_analysis(self, F):
        """Plot reference point analysis"""
        ax = self.pareto_figure.add_subplot(111)
        
        if F.shape[1] >= 2 and self.reference_point is not None:
            ax.scatter(F[:, 0], F[:, 1], alpha=0.6, s=40, label='Solutions')
            
            # Plot reference point
            ax.scatter(self.reference_point[0], self.reference_point[1], 
                      c='red', s=200, marker='x', linewidth=3, label='Reference Point')
            
            # Draw hypervolume rectangle for 2D
            if F.shape[1] == 2:
                pareto_mask = self.is_pareto_optimal(F)
                pareto_F = F[pareto_mask]
                
                if len(pareto_F) > 0:
                    # Draw dominated area
                    from matplotlib.patches import Rectangle
                    for point in pareto_F:
                        if (point[0] < self.reference_point[0] and 
                            point[1] < self.reference_point[1]):
                            width = self.reference_point[0] - point[0]
                            height = self.reference_point[1] - point[1]
                            rect = Rectangle(point, width, height, 
                                           alpha=0.1, color='green')
                            ax.add_patch(rect)
            
            ax.set_xlabel('Objective 1')
            ax.set_ylabel('Objective 2')
            ax.set_title('Reference Point Analysis')
            ax.legend()
            ax.grid(True, alpha=0.3)
    
    def update_distribution_analysis(self):
        """Update distribution analysis"""
        if not self.current_result or not hasattr(self.current_result, 'F'):
            return
        
        F = self.current_result.F
        X = getattr(self.current_result, 'X', None)
        metric = self.distribution_combo.currentText()
        
        self.distribution_figure.clear()
        
        if metric == "Objective Space Distribution":
            self.plot_objective_distribution(F)
        elif metric == "Decision Space Distribution" and X is not None:
            self.plot_decision_distribution(X)
        elif metric == "Density Analysis":
            self.plot_density_analysis(F)
        elif metric == "Clustering Analysis":
            self.plot_clustering_analysis(F)
        elif metric == "Diversity Metrics":
            self.plot_diversity_metrics(F)
        
        self.distribution_canvas.draw()
    
    def plot_objective_distribution(self, F):
        """Plot objective space distribution"""
        if F.shape[1] == 1:
            ax = self.distribution_figure.add_subplot(111)
            ax.hist(F[:, 0], bins=20, alpha=0.7, edgecolor='black')
            ax.set_xlabel('Objective Value')
            ax.set_ylabel('Frequency')
            ax.set_title('Objective Distribution')
        elif F.shape[1] >= 2:
            ax1 = self.distribution_figure.add_subplot(221)
            ax1.hist(F[:, 0], bins=15, alpha=0.7, color='blue', edgecolor='black')
            ax1.set_xlabel('Objective 1')
            ax1.set_ylabel('Frequency')
            ax1.set_title('Objective 1 Distribution')
            
            ax2 = self.distribution_figure.add_subplot(222)
            ax2.hist(F[:, 1], bins=15, alpha=0.7, color='orange', edgecolor='black')
            ax2.set_xlabel('Objective 2')
            ax2.set_ylabel('Frequency')
            ax2.set_title('Objective 2 Distribution')
            
            ax3 = self.distribution_figure.add_subplot(223)
            ax3.scatter(F[:, 0], F[:, 1], alpha=0.6)
            ax3.set_xlabel('Objective 1')
            ax3.set_ylabel('Objective 2')
            ax3.set_title('2D Distribution')
            
            if F.shape[1] > 2:
                ax4 = self.distribution_figure.add_subplot(224)
                ax4.hist(F[:, 2], bins=15, alpha=0.7, color='green', edgecolor='black')
                ax4.set_xlabel('Objective 3')
                ax4.set_ylabel('Frequency')
                ax4.set_title('Objective 3 Distribution')
        
        self.distribution_figure.tight_layout()
    
    def plot_decision_distribution(self, X):
        """Plot decision space distribution"""
        if X.shape[1] >= 2:
            n_vars = min(4, X.shape[1])  # Show up to 4 variables
            
            for i in range(n_vars):
                ax = self.distribution_figure.add_subplot(2, 2, i+1)
                ax.hist(X[:, i], bins=15, alpha=0.7, edgecolor='black')
                ax.set_xlabel(f'Variable {i+1}')
                ax.set_ylabel('Frequency')
                ax.set_title(f'Variable {i+1} Distribution')
        
        self.distribution_figure.tight_layout()
    
    def plot_density_analysis(self, F):
        """Plot solution density analysis"""
        if F.shape[1] >= 2:
            ax = self.distribution_figure.add_subplot(111)
            
            # Create hexbin plot for density
            hb = ax.hexbin(F[:, 0], F[:, 1], gridsize=20, cmap='Blues', alpha=0.8)
            self.distribution_figure.colorbar(hb, ax=ax, label='Solution Density')
            
            ax.set_xlabel('Objective 1')
            ax.set_ylabel('Objective 2')
            ax.set_title('Solution Density Analysis')
            ax.grid(True, alpha=0.3)
    
    def plot_clustering_analysis(self, F):
        """Plot clustering analysis"""
        try:
            from sklearn.cluster import KMeans
            
            if F.shape[1] >= 2 and len(F) > 4:
                # Determine optimal number of clusters (simple method)
                max_clusters = min(6, len(F)//2)
                n_clusters = max(2, max_clusters//2)
                
                kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
                clusters = kmeans.fit_predict(F)
                
                ax = self.distribution_figure.add_subplot(111)
                
                # Plot clusters with different colors
                scatter = ax.scatter(F[:, 0], F[:, 1], c=clusters, 
                                   cmap='tab10', alpha=0.7, s=50)
                
                # Plot cluster centers
                centers = kmeans.cluster_centers_
                ax.scatter(centers[:, 0], centers[:, 1], 
                          c='red', marker='x', s=200, linewidth=3,
                          label='Cluster Centers')
                
                ax.set_xlabel('Objective 1')
                ax.set_ylabel('Objective 2')
                ax.set_title(f'Clustering Analysis ({n_clusters} clusters)')
                ax.legend()
                ax.grid(True, alpha=0.3)
        except ImportError:
            ax = self.distribution_figure.add_subplot(111)
            ax.text(0.5, 0.5, 'Clustering requires scikit-learn\npip install scikit-learn', 
                   ha='center', va='center', transform=ax.transAxes, fontsize=12)
            ax.set_title('Clustering Analysis')
    
    def plot_diversity_metrics(self, F):
        """Plot diversity metrics visualization"""
        ax = self.distribution_figure.add_subplot(111)
        
        if F.shape[1] >= 2 and len(F) > 1:
            # Calculate pairwise distances
            distances = pdist(F)
            
            # Plot distance histogram
            ax.hist(distances, bins=20, alpha=0.7, edgecolor='black', color='skyblue')
            ax.axvline(np.mean(distances), color='red', linestyle='--', 
                      linewidth=2, label=f'Mean Distance: {np.mean(distances):.3f}')
            ax.axvline(np.median(distances), color='orange', linestyle='--', 
                      linewidth=2, label=f'Median Distance: {np.median(distances):.3f}')
            
            ax.set_xlabel('Pairwise Distance')
            ax.set_ylabel('Frequency')
            ax.set_title('Solution Diversity Analysis')
            ax.legend()
            ax.grid(True, alpha=0.3)
        else:
            ax.text(0.5, 0.5, 'Insufficient data for diversity analysis', 
                   ha='center', va='center', transform=ax.transAxes)
    
    def update_convergence_visualization(self, F):
        """Update convergence visualization"""
        # Placeholder - would need convergence history
        self.convergence_figure.clear()
        ax = self.convergence_figure.add_subplot(111)
        ax.text(0.5, 0.5, 'Convergence tracking requires\nreal-time optimization data', 
               ha='center', va='center', transform=ax.transAxes, fontsize=12)
        ax.set_title('Convergence Analysis')
        self.convergence_canvas.draw()
        
        # Update convergence table
        self.update_convergence_table(F)
    
    def update_convergence_table(self, F):
        """Update convergence metrics table"""
        metrics = [
            ("Mean Objective 1", np.mean(F[:, 0]) if F.shape[1] > 0 else "N/A", "Lower values generally better"),
            ("Mean Objective 2", np.mean(F[:, 1]) if F.shape[1] > 1 else "N/A", "Lower values generally better"),
            ("Std Objective 1", np.std(F[:, 0]) if F.shape[1] > 0 else "N/A", "Lower values indicate convergence"),
            ("Std Objective 2", np.std(F[:, 1]) if F.shape[1] > 1 else "N/A", "Lower values indicate convergence"),
            ("Range Objective 1", np.ptp(F[:, 0]) if F.shape[1] > 0 else "N/A", "Spread of solutions"),
            ("Range Objective 2", np.ptp(F[:, 1]) if F.shape[1] > 1 else "N/A", "Spread of solutions")
        ]
        
        self.convergence_table.setRowCount(len(metrics))
        
        for i, (metric, value, interpretation) in enumerate(metrics):
            self.convergence_table.setItem(i, 0, QTableWidgetItem(metric))
            if isinstance(value, (int, float)):
                self.convergence_table.setItem(i, 1, QTableWidgetItem(f"{value:.4f}"))
            else:
                self.convergence_table.setItem(i, 1, QTableWidgetItem(str(value)))
            self.convergence_table.setItem(i, 2, QTableWidgetItem(interpretation))
    
    def update_robustness_analysis(self, F, X):
        """Update robustness analysis"""
        # Placeholder implementation
        self.robustness_figure.clear()
        ax = self.robustness_figure.add_subplot(111)
        ax.text(0.5, 0.5, 'Robustness analysis requires\nmultiple optimization runs', 
               ha='center', va='center', transform=ax.transAxes, fontsize=12)
        ax.set_title('Robustness Analysis')
        self.robustness_canvas.draw()
    
    # Utility methods
    def dominates(self, a, b):
        """Check if solution a dominates solution b"""
        return np.all(a <= b) and np.any(a < b)
    
    def is_pareto_optimal(self, F):
        """Find Pareto optimal solutions"""
        is_pareto = np.ones(len(F), dtype=bool)
        
        for i in range(len(F)):
            if is_pareto[i]:
                # Check if current solution is dominated
                for j in range(len(F)):
                    if i != j and self.dominates(F[j], F[i]):
                        is_pareto[i] = False
                        break
        
        return is_pareto
    
    def find_knee_points(self, pareto_F):
        """Find knee points in Pareto front (simplified)"""
        if len(pareto_F) < 3:
            return []
        
        # Calculate curvature using angles
        knee_indices = []
        
        for i in range(1, len(pareto_F) - 1):
            # Vectors to previous and next points
            v1 = pareto_F[i] - pareto_F[i-1]
            v2 = pareto_F[i+1] - pareto_F[i]
            
            # Calculate angle
            try:
                cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
                angle = np.arccos(np.clip(cos_angle, -1, 1))
                
                # If angle is sharp (small), it might be a knee
                if angle < np.pi * 0.7:  # Less than 126 degrees
                    knee_indices.append(i)
            except:
                continue
        
        return knee_indices
    
    def calculate_pareto_ranks(self, F):
        """Calculate Pareto ranks for all solutions"""
        ranks = np.zeros(len(F))
        remaining = np.arange(len(F))
        current_rank = 1
        
        while len(remaining) > 0:
            # Find non-dominated solutions in remaining set
            current_pareto = []
            F_remaining = F[remaining]
            
            for i in range(len(remaining)):
                is_dominated = False
                for j in range(len(remaining)):
                    if i != j and self.dominates(F_remaining[j], F_remaining[i]):
                        is_dominated = True
                        break
                
                if not is_dominated:
                    current_pareto.append(remaining[i])
            
            # Assign current rank
            for idx in current_pareto:
                ranks[idx] = current_rank
            
            # Remove processed solutions
            remaining = np.array([r for r in remaining if r not in current_pareto])
            current_rank += 1
        
        return ranks
    
    def export_metrics(self):
        """Export metrics to file"""
        from PyQt6.QtWidgets import QFileDialog
        from datetime import datetime
        
        filename, _ = QFileDialog.getSaveFileName(
            self, "Export Performance Metrics",
            f"performance_metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            "JSON files (*.json);;Text files (*.txt);;All files (*.*)"
        )
        
        if filename:
            try:
                metrics_data = self.collect_all_metrics()
                
                if filename.endswith('.json'):
                    import json
                    with open(filename, 'w') as f:
                        json.dump(metrics_data, f, indent=2)
                else:
                    with open(filename, 'w') as f:
                        for category, metrics in metrics_data.items():
                            f.write(f"{category}:\n")
                            for key, value in metrics.items():
                                f.write(f"  {key}: {value}\n")
                            f.write("\n")
                
                self.metrics_status_label.setText(f"Metrics exported to {filename}")
            except Exception as e:
                self.metrics_status_label.setText(f"Export failed: {e}")
    
    def collect_all_metrics(self):
        """Collect all calculated metrics"""
        return {
            "Quality Metrics": {
                "Hypervolume": self.hv_value.text(),
                "IGD": self.igd_value.text(),
                "Spacing": self.spacing_value.text(),
                "Spread": self.spread_value.text()
            },
            "Convergence Metrics": {
                "Generational Distance": self.gd_value.text(),
                "Convergence Rate": self.conv_rate_value.text(),
                "Stability Index": self.stability_value.text(),
                "Progress Rate": self.progress_value.text()
            },
            "Efficiency Metrics": {
                "Runtime": self.runtime_value.text(),
                "Evaluations": self.evals_value.text(),
                "Solutions Found": self.solutions_value.text(),
                "Success Rate": self.success_value.text()
            }
        }
