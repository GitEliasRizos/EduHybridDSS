"""
Optimizer - Core functionality for running optimizations

This module provides the Optimizer class which serves as the central coordinator
for running multi-objective optimization tasks. It integrates with PyMOO to
execute optimizations while providing progress monitoring, result processing,
and state management capabilities.

Key Features:
- Integration with PyMOO optimization framework
- Real-time progress monitoring and callback system
- Optimization state management (running, stopped, completed)
- Result extraction and formatting for GUI consumption
- Performance metrics tracking and history
- Thread-safe operation for GUI integration
- Comprehensive error handling and recovery

The Optimizer acts as a high-level interface that coordinates between the
problem definition, algorithm configuration, and result visualization
components. It handles the complexity of PyMOO integration while providing
a simple interface for the GUI components.

Core Workflow:
    1. Setup: Configure problem, algorithm, and termination
    2. Execute: Run optimization with progress callbacks
    3. Monitor: Track progress and performance metrics
    4. Extract: Process results for GUI display
    5. Cleanup: Manage resources and state

Classes:
    OptimizationCallback: Progress monitoring and history tracking
    Optimizer: Main optimization coordinator and executor

Thread Safety:
    The Optimizer is designed to work safely in multi-threaded environments,
    particularly with Qt's worker thread pattern used by the GUI.

Author: Elias Rizos [it21490]
Version: 1.3.2
"""

from pymoo.optimize import minimize
from pymoo.core.callback import Callback
import numpy as np
import time
from threading import Event


class OptimizationCallback(Callback):
    """
    Callback class to monitor optimization progress and collect metrics
    
    This class integrates with PyMOO's callback system to provide real-time
    monitoring of optimization progress. It tracks key metrics like generation
    count, function evaluations, and objective value statistics.
    
    Key Features:
    - Real-time progress tracking during optimization
    - History collection for convergence analysis
    - Objective value statistics (min, max, average)
    - Integration with GUI progress reporting
    - Thread-safe operation with stop event handling
    - Performance metrics for algorithm assessment
    
    The callback is called at each generation and collects comprehensive
    data about the optimization state. This information is used both for
    progress reporting and post-optimization analysis.
    
    Attributes:
        history (dict): Collection of optimization metrics over time
        progress_callback (callable): Optional callback for GUI updates
        stop_event (Event): Threading event for graceful termination
    """
    
    def __init__(self):
        """
        Initialize the optimization callback
        
        Sets up data collection structures and prepares for optimization
        monitoring. All history tracking arrays are initialized empty.
        """
        super().__init__()
        
        # History dictionary to track optimization progress over generations
        self.history = {
            'n_gen': [],      # Generation numbers
            'n_eval': [],     # Cumulative function evaluations
            'f_min': [],      # Minimum objective value in population
            'f_avg': [],      # Average objective value in population  
            'f_max': []       # Maximum objective value in population
        }
        
        # Optional callback function for GUI progress updates
        self.progress_callback = None
        
        # Threading event for graceful optimization termination
        self.stop_event = Event()
        
    def notify(self, algorithm):
        """
        Called at each generation to collect optimization metrics
        
        This method is automatically invoked by PyMOO at each generation.
        It extracts relevant information from the algorithm state and
        updates the history tracking structures.
        
        Args:
            algorithm: The PyMOO algorithm instance being executed
            
        The method safely handles various population states and objective
        value formats, ensuring robust operation across different problem types.
        """
        # Record basic generation and evaluation information
        self.history['n_gen'].append(algorithm.n_gen)
        self.history['n_eval'].append(algorithm.evaluator.n_eval)
        
        # Extract and analyze objective values from current population
        if algorithm.pop is not None and len(algorithm.pop) > 0:
            # Get objective values from all individuals in population
            F = np.array([ind.F for ind in algorithm.pop])
            
            if F.ndim == 2 and F.shape[0] > 0:
                # Multi-objective case: use first objective for progress tracking
                # This provides a consistent progress metric across problem types
                f_vals = F[:, 0] if F.shape[1] > 0 else F.flatten()
            else:
                # Single objective or flattened array case
                f_vals = F.flatten()
                
            # Calculate and store population statistics if valid data exists
            if len(f_vals) > 0:
                self.history['f_min'].append(np.min(f_vals))
                self.history['f_avg'].append(np.mean(f_vals))
                self.history['f_max'].append(np.max(f_vals))
            else:
                # Handle edge case of empty or invalid objective values
                self.history['f_min'].append(np.inf)
                self.history['f_avg'].append(np.inf)
                self.history['f_max'].append(np.inf)
        else:
            self.history['f_min'].append(np.inf)
            self.history['f_avg'].append(np.inf)
            self.history['f_max'].append(np.inf)
            
        # Call progress callback if provided
        if self.progress_callback:
            self.progress_callback(self)  # Pass the callback object itself
            
        # Check for stop signal
        if self.stop_event.is_set():
            algorithm.termination.force_termination = True
            
    def stop(self):
        """Signal the optimization to stop"""
        self.stop_event.set()


class Optimizer:
    """Main optimizer class that coordinates problem and algorithm"""
    
    def __init__(self):
        self.problem = None
        self.algorithm = None
        self.termination = None
        self.callback = None
        self.results = None
        self.is_running = False
        
    def setup(self, problem, algorithm, termination):
        """Setup the optimization components"""
        self.problem = problem
        self.algorithm = algorithm
        self.termination = termination
        self.callback = OptimizationCallback()
        
    def run(self, progress_callback=None):
        """Run the optimization"""
        if not all([self.problem, self.algorithm, self.termination]):
            raise ValueError("Problem, algorithm, and termination must be set before running")
            
        self.is_running = True
        
        try:
            # Set up progress callback
            if progress_callback:
                self.callback.progress_callback = progress_callback
                
            # Run optimization
            start_time = time.time()
            
            self.results = minimize(
                problem=self.problem,
                algorithm=self.algorithm,
                termination=self.termination,
                callback=self.callback,
                seed=getattr(self.algorithm, 'seed', None),
                verbose=False
            )
            
            end_time = time.time()
            
            # Add timing information to results
            if hasattr(self.results, 'exec_time'):
                self.results.exec_time = end_time - start_time
            else:
                # Create exec_time attribute
                self.results.__dict__['exec_time'] = end_time - start_time
                
            # Add callback history to results
            if hasattr(self.results, 'history') and isinstance(self.results.history, dict):
                self.results.history.update(self.callback.history)
            else:
                self.results.__dict__['history'] = self.callback.history
                
        except Exception as e:
            raise RuntimeError(f"Optimization failed: {str(e)}")
        finally:
            self.is_running = False
            
        return self.results
        
    def stop(self):
        """Stop the running optimization"""
        if self.callback:
            self.callback.stop()
            
    def get_results_summary(self):
        """Get a summary of optimization results"""
        if self.results is None:
            return "No optimization results available"
            
        summary = {
            'n_evaluations': getattr(self.results, 'n_eval', 'Unknown'),
            'execution_time': getattr(self.results, 'exec_time', 'Unknown'),
            'n_solutions': len(self.results.X) if self.results.X is not None else 0,
            'objectives_shape': self.results.F.shape if self.results.F is not None else 'Unknown',
            'variables_shape': self.results.X.shape if self.results.X is not None else 'Unknown',
            'convergence': getattr(self.results, 'history', {}).get('f_min', [])
        }
        
        return summary
        
    def extract_results(self, problem_config, algorithm_config):
        """Extract and format results for visualization"""
        if self.results is None:
            return None
            
        # Get basic results
        objectives = self.results.F
        variables = self.results.X
        
        # Ensure arrays are 2D
        if objectives.ndim == 1:
            objectives = objectives.reshape(-1, 1)
        if variables.ndim == 1:
            variables = variables.reshape(-1, 1)
            
        # Handle direction (maximize objectives were negated)
        for i, obj_config in enumerate(problem_config.get('objectives', [])):
            if obj_config.get('direction') == 'Maximize':
                objectives[:, i] = -objectives[:, i]
                
        # Create results dictionary
        formatted_results = {
            'objectives': objectives,
            'variables': variables,
            'n_solutions': len(variables),
            'n_generations': getattr(self.results.algorithm, 'n_gen', 0),
            'n_evaluations': getattr(self.results, 'n_eval', 0),
            'execution_time': getattr(self.results, 'exec_time', 0),
            'algorithm': algorithm_config.get('name', 'Unknown'),
            'problem_config': problem_config,
            'algorithm_config': algorithm_config,
            'convergence': getattr(self.results, 'history', {}).get('f_min', []),
            'raw_results': self.results
        }
        
        return formatted_results
        
    def calculate_metrics(self, results):
        """Calculate optimization metrics"""
        if results is None:
            return {}
            
        objectives = results['objectives']
        metrics = {}
        
        # Basic statistics for each objective
        for i in range(objectives.shape[1]):
            obj_values = objectives[:, i]
            metrics[f'obj_{i+1}_min'] = float(np.min(obj_values))
            metrics[f'obj_{i+1}_max'] = float(np.max(obj_values))
            metrics[f'obj_{i+1}_mean'] = float(np.mean(obj_values))
            metrics[f'obj_{i+1}_std'] = float(np.std(obj_values))
            
        # Solution spread (for multi-objective)
        if objectives.shape[1] > 1:
            # Calculate spread in objective space
            ranges = np.max(objectives, axis=0) - np.min(objectives, axis=0)
            metrics['objective_spread'] = float(np.mean(ranges))
            
        # Number of non-dominated solutions
        if objectives.shape[1] > 1:
            # Simple non-domination check
            is_dominated = np.zeros(len(objectives), dtype=bool)
            for i in range(len(objectives)):
                for j in range(len(objectives)):
                    if i != j:
                        if np.all(objectives[j] <= objectives[i]) and np.any(objectives[j] < objectives[i]):
                            is_dominated[i] = True
                            break
            metrics['n_non_dominated'] = int(np.sum(~is_dominated))
        else:
            # For single objective, best solution
            best_idx = np.argmin(objectives[:, 0])
            metrics['best_objective'] = float(objectives[best_idx, 0])
            metrics['best_solution_idx'] = int(best_idx)
            
        # Convergence metrics
        convergence = results.get('convergence', [])
        if len(convergence) > 0:
            metrics['initial_best'] = float(convergence[0]) if len(convergence) > 0 else None
            metrics['final_best'] = float(convergence[-1]) if len(convergence) > 0 else None
            metrics['improvement'] = float(convergence[0] - convergence[-1]) if len(convergence) > 0 else None
            
        return metrics
