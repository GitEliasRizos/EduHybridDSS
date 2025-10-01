"""
Helper Functions and Utilities for PyMOO GUI Application

This module provides utility functions for common operations throughout the
PyMOO GUI application, including file I/O, data processing, visualization
helpers, and configuration management.

🔍 LOOKING FOR GROUP WEIGHT AGGREGATION?
========================================
Group decision weight aggregation functions are located in:
📁 core/group_aggregation.py

That module contains:
- aggregate_ahp_matrices() - AHP geometric mean aggregation
- aggregate_topsis_weights() - TOPSIS arithmetic mean aggregation  
- Complete validation and consistency checking
- Full documentation and examples

See docs/GROUP_AGGREGATION_REFERENCE.md for quick reference.

Key Features (This Module):
- Configuration save/load for problems and algorithms
- Data serialization and validation utilities  
- Visualization helpers for plots and charts
- File format validation and error handling
- Cross-platform path handling
- Performance measurement utilities

Functions are organized by category:
- Configuration Management: save/load problem and algorithm configs
- Data Processing: format conversion, validation, cleaning
- Visualization: plot styling, color schemes, layout helpers
- File Operations: safe I/O with error handling
- Validation: input checking and constraint verification

Author: Elias Rizos [it21490]
Version: 1.3.3
"""

import json
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap


def save_problem_config(config: Dict[str, Any], filepath: Union[str, Path]) -> bool:
    """
    Save problem configuration to JSON file with error handling
    
    Safely serializes and saves a problem configuration dictionary to a JSON file.
    Handles numpy arrays, complex nested structures, and provides robust error
    recovery. Creates parent directories if they don't exist.
    
    Args:
        config: Problem configuration dictionary from ProblemTab
        filepath: Target file path (string or Path object)
        
    Returns:
        bool: True if saved successfully, False if error occurred
        
    Example:
        config = {"variables": [...], "objectives": [...]}
        success = save_problem_config(config, "my_problem.json")
    """
    try:
        filepath = Path(filepath)
        
        # Ensure parent directory exists
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        # Create a serializable copy of the config
        serializable_config = make_serializable(config)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(serializable_config, f, indent=2, ensure_ascii=False)
            
        return True
    except Exception as e:
        print(f"Error saving problem config: {e}")
        return False


def load_problem_config(filepath: Union[str, Path]) -> Optional[Dict[str, Any]]:
    """
    Load problem configuration from JSON file with validation
    
    Safely loads and validates a problem configuration from a JSON file.
    Performs basic structure validation and handles missing files gracefully.
    
    Args:
        filepath: Path to JSON configuration file
        
    Returns:
        Dict containing configuration if successful, None if error occurred
        
    Example:
        config = load_problem_config("saved_problem.json")
        if config:
            print(f"Loaded problem: {config['name']}")
    """
    try:
        filepath = Path(filepath)
        
        if not filepath.exists():
            print(f"Configuration file not found: {filepath}")
            return None
            
        with open(filepath, 'r', encoding='utf-8') as f:
            config = json.load(f)
            
        # Basic validation - ensure required keys exist
        required_keys = ['variables', 'objectives']
        if not all(key in config for key in required_keys):
            print(f"Invalid configuration format - missing required keys")
            return None
            
        return config
    except Exception as e:
        print(f"Error loading problem config: {e}")
        return None


def save_algorithm_config(config: Dict[str, Any], filepath: Union[str, Path]) -> bool:
    """
    Save algorithm configuration to JSON file with error handling
    
    Safely serializes and saves an algorithm configuration dictionary to a JSON file.
    Handles algorithm-specific parameters and provides robust error recovery.
    
    Args:
        config: Algorithm configuration dictionary from AlgorithmTab
        filepath: Target file path (string or Path object)
        
    Returns:
        bool: True if saved successfully, False if error occurred
    """
    try:
        filepath = Path(filepath)
        
        # Create a serializable copy of the config
        serializable_config = make_serializable(config)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(serializable_config, f, indent=2, ensure_ascii=False)
            
        return True
    except Exception as e:
        print(f"Error saving algorithm config: {e}")
        return False


def load_algorithm_config(filepath: Union[str, Path]) -> Optional[Dict[str, Any]]:
    """Load algorithm configuration from JSON file"""
    try:
        filepath = Path(filepath)
        
        if not filepath.exists():
            return None
            
        with open(filepath, 'r', encoding='utf-8') as f:
            config = json.load(f)
            
        return config
    except Exception as e:
        print(f"Error loading algorithm config: {e}")
        return None


def save_complete_config(config: Dict[str, Any], filepath: Union[str, Path]) -> bool:
    """Save complete configuration (problem + algorithm) to JSON file"""
    try:
        filepath = Path(filepath)
        
        # Create a serializable copy of the config
        serializable_config = make_serializable(config)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(serializable_config, f, indent=2, ensure_ascii=False)
            
        return True
    except Exception as e:
        print(f"Error saving complete config: {e}")
        return False


def load_complete_config(filepath: Union[str, Path]) -> Optional[Dict[str, Any]]:
    """Load complete configuration (problem + algorithm) from JSON file"""
    try:
        filepath = Path(filepath)
        
        if not filepath.exists():
            return None
            
        with open(filepath, 'r', encoding='utf-8') as f:
            config = json.load(f)
            
        # Check if this is a complete config (has problem and/or algorithm sections)
        if "problem" in config or "algorithm" in config:
            return config
        else:
            # This might be an old-format problem-only config
            return None
            
    except Exception as e:
        print(f"Error loading complete config: {e}")
        return None


def export_results_csv(results: Dict[str, Any], filepath: Union[str, Path], 
                      include_objectives: bool = True, include_variables: bool = True) -> bool:
    """Export optimization results to CSV file"""
    try:
        filepath = Path(filepath)
        
        # Prepare data
        data = {}
        
        if include_objectives and 'objectives' in results:
            objectives = results['objectives']
            obj_names = [f"objective_{i+1}" for i in range(objectives.shape[1])]
            
            # Add objective names from config if available
            if 'problem_config' in results:
                obj_configs = results['problem_config'].get('objectives', [])
                for i, obj_config in enumerate(obj_configs):
                    if i < len(obj_names):
                        obj_names[i] = obj_config.get('name', obj_names[i])
                        
            for i, name in enumerate(obj_names):
                data[name] = objectives[:, i]
                
        if include_variables and 'variables' in results:
            variables = results['variables']
            var_names = [f"variable_{i+1}" for i in range(variables.shape[1])]
            
            # Add variable names from config if available
            if 'problem_config' in results:
                var_configs = results['problem_config'].get('variables', [])
                for i, var_config in enumerate(var_configs):
                    if i < len(var_names):
                        var_names[i] = var_config.get('name', var_names[i])
                        
            for i, name in enumerate(var_names):
                data[name] = variables[:, i]
                
        # Create DataFrame and save
        df = pd.DataFrame(data)
        df.to_csv(filepath, index=False)
        
        return True
    except Exception as e:
        print(f"Error exporting results to CSV: {e}")
        return False


def export_results_json(results: Dict[str, Any], filepath: Union[str, Path]) -> bool:
    """Export optimization results to JSON file"""
    try:
        filepath = Path(filepath)
        
        # Create a serializable copy of the results
        export_data = {}
        
        # Basic information
        export_data['algorithm'] = results.get('algorithm', 'Unknown')
        export_data['n_solutions'] = results.get('n_solutions', 0)
        export_data['n_evaluations'] = results.get('n_evaluations', 0)
        export_data['execution_time'] = results.get('execution_time', 0)
        
        # Objectives
        if 'objectives' in results:
            export_data['objectives'] = results['objectives'].tolist()
            
        # Variables
        if 'variables' in results:
            export_data['variables'] = results['variables'].tolist()
            
        # Convergence history
        if 'convergence' in results:
            export_data['convergence'] = results['convergence']
            
        # Configuration
        if 'problem_config' in results:
            export_data['problem_config'] = make_serializable(results['problem_config'])
        if 'algorithm_config' in results:
            export_data['algorithm_config'] = make_serializable(results['algorithm_config'])
            
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
            
        return True
    except Exception as e:
        print(f"Error exporting results to JSON: {e}")
        return False


def export_results_excel(results: Dict[str, Any], filepath: Union[str, Path]) -> bool:
    """Export optimization results to Excel file"""
    try:
        filepath = Path(filepath)
        
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            # Summary sheet
            summary_data = {
                'Metric': ['Algorithm', 'Solutions', 'Evaluations', 'Execution Time (s)'],
                'Value': [
                    results.get('algorithm', 'Unknown'),
                    results.get('n_solutions', 0),
                    results.get('n_evaluations', 0),
                    results.get('execution_time', 0)
                ]
            }
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
            
            # Objectives sheet
            if 'objectives' in results:
                objectives = results['objectives']
                obj_names = [f"Objective_{i+1}" for i in range(objectives.shape[1])]
                
                # Use names from config if available
                if 'problem_config' in results:
                    obj_configs = results['problem_config'].get('objectives', [])
                    for i, obj_config in enumerate(obj_configs):
                        if i < len(obj_names):
                            obj_names[i] = obj_config.get('name', obj_names[i])
                            
                obj_df = pd.DataFrame(objectives, columns=obj_names)
                obj_df.to_excel(writer, sheet_name='Objectives', index=False)
                
            # Variables sheet
            if 'variables' in results:
                variables = results['variables']
                var_names = [f"Variable_{i+1}" for i in range(variables.shape[1])]
                
                # Use names from config if available
                if 'problem_config' in results:
                    var_configs = results['problem_config'].get('variables', [])
                    for i, var_config in enumerate(var_configs):
                        if i < len(var_names):
                            var_names[i] = var_config.get('name', var_names[i])
                            
                var_df = pd.DataFrame(variables, columns=var_names)
                var_df.to_excel(writer, sheet_name='Variables', index=False)
                
            # Convergence sheet
            if 'convergence' in results and results['convergence']:
                conv_df = pd.DataFrame({
                    'Generation': range(len(results['convergence'])),
                    'Best_Objective': results['convergence']
                })
                conv_df.to_excel(writer, sheet_name='Convergence', index=False)
                
        return True
    except Exception as e:
        print(f"Error exporting results to Excel: {e}")
        return False


def make_serializable(obj: Any) -> Any:
    """
    Convert numpy arrays and other non-serializable objects to JSON-serializable format
    
    Recursively processes complex data structures to convert numpy types and arrays
    into standard Python types that can be serialized to JSON. Essential for
    saving configurations and results that contain numpy data.
    
    Args:
        obj: Any object that may contain non-serializable types
        
    Returns:
        Same object structure with all non-serializable types converted
        
    Supported Conversions:
        - numpy.ndarray -> list
        - numpy.integer -> int  
        - numpy.floating -> float
        - Recursively processes dict, list, tuple containers
        
    Example:
        config = {"results": np.array([1.2, 3.4]), "count": np.int64(5)}
        serializable = make_serializable(config)
        # Result: {"results": [1.2, 3.4], "count": 5}
    """
    # Handle numpy arrays - convert to standard Python lists
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    # Handle numpy integer types - convert to standard Python int
    elif isinstance(obj, np.integer):
        return int(obj)
    # Handle numpy floating point types - convert to standard Python float
    elif isinstance(obj, np.floating):
        return float(obj)
    # Handle numpy boolean types - convert to standard Python bool
    elif isinstance(obj, np.bool_):
        return bool(obj)
    # Recursively process dictionary values
    elif isinstance(obj, dict):
        return {key: make_serializable(value) for key, value in obj.items()}
    # Recursively process list elements
    elif isinstance(obj, list):
        return [make_serializable(item) for item in obj]
    # Recursively process tuple elements (keeping tuple structure)
    elif isinstance(obj, tuple):
        return tuple(make_serializable(item) for item in obj)
    # Return unchanged if already serializable (str, int, float, bool, None)
    else:
        return obj


def calculate_pareto_front_metrics(objectives: np.ndarray) -> Dict[str, float]:
    """Calculate various metrics for Pareto front analysis"""
    metrics = {}
    
    if objectives.shape[0] == 0:
        return metrics
        
    # Basic statistics
    metrics['n_solutions'] = objectives.shape[0]
    metrics['n_objectives'] = objectives.shape[1]
    
    # Range for each objective
    for i in range(objectives.shape[1]):
        obj_values = objectives[:, i]
        metrics[f'obj_{i+1}_range'] = float(np.max(obj_values) - np.min(obj_values))
        
    # Overall spread (sum of ranges)
    ranges = [np.max(objectives[:, i]) - np.min(objectives[:, i]) 
              for i in range(objectives.shape[1])]
    metrics['total_spread'] = float(np.sum(ranges))
    
    # For 2-objective problems, calculate additional metrics
    if objectives.shape[1] == 2:
        # Spacing metric (diversity measure)
        if objectives.shape[0] > 1:
            distances = []
            for i in range(objectives.shape[0]):
                min_dist = float('inf')
                for j in range(objectives.shape[0]):
                    if i != j:
                        dist = np.linalg.norm(objectives[i] - objectives[j])
                        min_dist = min(min_dist, dist)
                distances.append(min_dist)
            
            distances = np.array(distances)
            mean_distance = np.mean(distances)
            spacing = np.sqrt(np.mean((distances - mean_distance) ** 2))
            metrics['spacing'] = float(spacing)
            
        # Extent (diagonal of bounding box)
        min_vals = np.min(objectives, axis=0)
        max_vals = np.max(objectives, axis=0)
        extent = np.linalg.norm(max_vals - min_vals)
        metrics['extent'] = float(extent)
        
    return metrics


def detect_outliers(data: np.ndarray, method: str = 'iqr') -> np.ndarray:
    """Detect outliers in data using specified method"""
    if method == 'iqr':
        Q1 = np.percentile(data, 25)
        Q3 = np.percentile(data, 75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        return (data < lower_bound) | (data > upper_bound)
    elif method == 'zscore':
        z_scores = np.abs((data - np.mean(data)) / np.std(data))
        return z_scores > 3
    else:
        raise ValueError("Method must be 'iqr' or 'zscore'")


def normalize_objectives(objectives: np.ndarray, method: str = 'minmax') -> np.ndarray:
    """Normalize objectives using specified method"""
    if method == 'minmax':
        min_vals = np.min(objectives, axis=0)
        max_vals = np.max(objectives, axis=0)
        ranges = max_vals - min_vals
        # Avoid division by zero
        ranges[ranges == 0] = 1
        return (objectives - min_vals) / ranges
    elif method == 'zscore':
        means = np.mean(objectives, axis=0)
        stds = np.std(objectives, axis=0)
        # Avoid division by zero
        stds[stds == 0] = 1
        return (objectives - means) / stds
    else:
        raise ValueError("Method must be 'minmax' or 'zscore'")


def create_custom_colormap(colors: List[str], name: str = 'custom') -> LinearSegmentedColormap:
    """Create a custom colormap from a list of colors"""
    return LinearSegmentedColormap.from_list(name, colors)


def format_number(value: float, precision: int = 6) -> str:
    """Format a number for display with appropriate precision"""
    if abs(value) >= 1e6 or (abs(value) < 1e-3 and value != 0):
        return f"{value:.{precision-1}e}"
    else:
        return f"{value:.{precision}f}".rstrip('0').rstrip('.')


def generate_latin_hypercube_sample(n_samples: int, n_dims: int, 
                                  bounds: List[tuple]) -> np.ndarray:
    """Generate Latin Hypercube samples within specified bounds"""
    # Simple Latin Hypercube sampling implementation
    samples = np.zeros((n_samples, n_dims))
    
    for dim in range(n_dims):
        lower, upper = bounds[dim]
        
        # Generate uniformly spaced intervals
        intervals = np.linspace(0, 1, n_samples + 1)
        
        # Sample uniformly within each interval
        uniform_samples = np.random.uniform(intervals[:-1], intervals[1:])
        
        # Shuffle to break correlation between dimensions
        np.random.shuffle(uniform_samples)
        
        # Scale to bounds
        samples[:, dim] = lower + uniform_samples * (upper - lower)
        
    return samples


def calculate_dominated_solutions(objectives: np.ndarray) -> np.ndarray:
    """Calculate which solutions are dominated by others"""
    n_solutions = objectives.shape[0]
    is_dominated = np.zeros(n_solutions, dtype=bool)
    
    for i in range(n_solutions):
        for j in range(n_solutions):
            if i != j:
                # Check if j dominates i (all objectives better or equal, at least one strictly better)
                if (np.all(objectives[j] <= objectives[i]) and 
                    np.any(objectives[j] < objectives[i])):
                    is_dominated[i] = True
                    break
                    
    return is_dominated


def find_knee_points(objectives: np.ndarray) -> List[int]:
    """Find knee points (solutions with good trade-offs) in 2D Pareto front"""
    if objectives.shape[1] != 2:
        return []
        
    # Sort solutions by first objective
    sorted_indices = np.argsort(objectives[:, 0])
    sorted_objectives = objectives[sorted_indices]
    
    knee_points = []
    
    # Calculate angles for each point
    for i in range(1, len(sorted_objectives) - 1):
        p1 = sorted_objectives[i-1]
        p2 = sorted_objectives[i]
        p3 = sorted_objectives[i+1]
        
        # Calculate vectors
        v1 = p2 - p1
        v2 = p3 - p2
        
        # Calculate angle
        if np.linalg.norm(v1) > 0 and np.linalg.norm(v2) > 0:
            cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
            cos_angle = np.clip(cos_angle, -1, 1)  # Ensure valid range
            angle = np.arccos(cos_angle)
            
            # Points with sharp angles (small cos_angle) are potential knee points
            if angle > np.pi / 3:  # 60 degrees
                knee_points.append(sorted_indices[i])
                
    return knee_points
