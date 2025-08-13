"""
Optimizer - Core functionality for running optimizations
"""

from pymoo.optimize import minimize
from pymoo.core.callback import Callback
import numpy as np
import time
from threading import Event


class OptimizationCallback(Callback):
    """Callback class to monitor optimization progress"""
    
    def __init__(self):
        super().__init__()
        self.history = {
            'n_gen': [],
            'n_eval': [],
            'f_min': [],
            'f_avg': [],
            'f_max': []
        }
        self.progress_callback = None
        self.stop_event = Event()
        
    def notify(self, algorithm):
        """Called at each generation"""
        # Store generation information
        self.history['n_gen'].append(algorithm.n_gen)
        self.history['n_eval'].append(algorithm.evaluator.n_eval)
        
        # Get objective values from current population
        if algorithm.pop is not None and len(algorithm.pop) > 0:
            F = np.array([ind.F for ind in algorithm.pop])
            if F.ndim == 2 and F.shape[0] > 0:
                # Multi-objective: use first objective for progress tracking
                f_vals = F[:, 0] if F.shape[1] > 0 else F.flatten()
            else:
                f_vals = F.flatten()
                
            if len(f_vals) > 0:
                self.history['f_min'].append(np.min(f_vals))
                self.history['f_avg'].append(np.mean(f_vals))
                self.history['f_max'].append(np.max(f_vals))
            else:
                self.history['f_min'].append(np.inf)
                self.history['f_avg'].append(np.inf)
                self.history['f_max'].append(np.inf)
        else:
            self.history['f_min'].append(np.inf)
            self.history['f_avg'].append(np.inf)
            self.history['f_max'].append(np.inf)
            
        # Call progress callback if provided
        if self.progress_callback:
            progress = int((algorithm.n_gen / algorithm.termination.max_gen) * 100) if hasattr(algorithm.termination, 'max_gen') else 0
            self.progress_callback(progress, f"Generation {algorithm.n_gen}")
            
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
            if hasattr(self.results, 'history'):
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
