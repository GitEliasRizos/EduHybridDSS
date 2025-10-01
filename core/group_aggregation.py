"""
Group Decision Weight Aggregation Module

This module provides centralized algorithms for aggregating individual decision-maker
preferences into group consensus for multi-criteria decision analysis (MCDA).

KEY AGGREGATION METHODS:
========================

1. AHP Matrix Aggregation (Geometric Mean):
   - Aggregates pairwise comparison matrices using geometric mean
   - Preserves reciprocal property: if A[i,j] = x, then A[j,i] = 1/x
   - Formula: group_matrix[i,j] = (∏ user_matrix[k][i,j])^(1/m)
   
2. TOPSIS Weight Aggregation (Arithmetic Mean):
   - Aggregates individual weight vectors using arithmetic mean
   - Maintains linear interpretation of importance weights
   - Formula: group_weights[i] = (Σ user_weights[k][i]) / m

WHERE TO FIND GROUP AGGREGATION:
===============================
This is THE module for all group aggregation functionality.
All other modules should import and use functions from here.

MATHEMATICAL FOUNDATIONS:
========================
- AHP: Forman, E. & Peniwati, K. (1998). Aggregating individual judgments and priorities
- TOPSIS: Yoon, K. & Hwang, C.L. (1995). Multiple attribute decision making
- Group Theory: Ramanathan, R. & Ganesh, L.S. (1994). Group preference aggregation

Author: Elias Rizos [it21490]
Version: 1.0.0
Date: September 26, 2025
"""

import numpy as np
from typing import Dict, List, Optional, Tuple, Any
import logging
from dataclasses import dataclass


# Configure logging
logger = logging.getLogger(__name__)


@dataclass
class AggregationResult:
    """Result container for aggregation operations"""
    method: str
    aggregated_data: Any
    participants: List[str]
    consistency_info: Optional[Dict] = None
    quality_metrics: Optional[Dict] = None


class GroupAggregationError(Exception):
    """Custom exception for group aggregation errors"""
    pass


def aggregate_ahp_matrices(matrices: Dict[str, np.ndarray]) -> np.ndarray:
    """
    Aggregate multiple AHP pairwise comparison matrices using geometric mean.
    
    This is the standard Aggregation of Individual Judgments (AIJ) method for
    AHP group decision making. It preserves the reciprocal property of AHP matrices
    and provides mathematically sound group consensus.
    
    Mathematical Foundation:
    -----------------------
    For each matrix element (i,j):
    group_matrix[i,j] = (∏_{k=1}^{m} user_matrix_k[i,j])^{1/m}
    
    Where:
    - m = number of participants
    - user_matrix_k = individual comparison matrix from participant k
    - ∏ = product operator (geometric mean)
    
    The geometric mean is preferred because:
    1. Preserves reciprocal property: if group_matrix[i,j] = x, then group_matrix[j,i] = 1/x
    2. Less sensitive to extreme judgments than arithmetic mean
    3. Mathematically consistent with the multiplicative nature of pairwise comparisons
    
    Args:
        matrices: Dictionary mapping participant names to their comparison matrices
                 Each matrix must be square (n×n) and positive with reciprocal structure
                 
    Returns:
        np.ndarray: Aggregated group matrix maintaining reciprocal properties
        
    Raises:
        GroupAggregationError: If matrices are invalid or incompatible
        ValueError: If input validation fails
        
    Example:
        >>> user1_matrix = np.array([[1, 2], [0.5, 1]])
        >>> user2_matrix = np.array([[1, 3], [0.33, 1]])
        >>> matrices = {'user1': user1_matrix, 'user2': user2_matrix}
        >>> group_matrix = aggregate_ahp_matrices(matrices)
        >>> print(group_matrix)
        [[1.0  2.45]
         [0.41 1.0 ]]
    """
    logger.info(f"Starting AHP matrix aggregation for {len(matrices)} participants")
    
    # Input validation
    if not matrices:
        raise ValueError("No matrices provided for aggregation")
    
    if len(matrices) < 2:
        logger.warning("Only one matrix provided - returning original matrix")
        return next(iter(matrices.values())).copy()
    
    # Validate matrix dimensions and properties
    participants = list(matrices.keys())
    first_matrix = matrices[participants[0]]
    n = first_matrix.shape[0]
    
    # Simple check for square matrix (Can't really be raised without injection)
    if first_matrix.shape[0] != first_matrix.shape[1]:
        raise GroupAggregationError("All matrices must be square")
    
    # Validate all matrices have same dimensions
    for participant, matrix in matrices.items():
        if matrix.shape != (n, n):
            raise GroupAggregationError(
                f"Matrix dimension mismatch: {participant} has shape {matrix.shape}, "
                f"expected ({n}, {n})"
            )
        
        # Check for positive values (AHP requirement)
        if np.any(matrix <= 0):
            raise GroupAggregationError(
                f"Matrix from {participant} contains non-positive values"
            )
    
    logger.info(f"Aggregating {n}×{n} matrices from participants: {participants}")
    
    # Initialize result group matrix
    aggregated = np.ones((n, n), dtype=np.float64)
    
    try:
        # Calculate geometric mean for each element
        for i in range(n):
            for j in range(n):
                if i != j:  # Skip diagonal elements (remain 1.0)
                    # Collect all values for position (i,j)
                    elements = [matrix[i, j] for matrix in matrices.values()]
                    
                    # Geometric mean: (a₁ × a₂ × ... × aₘ)^(1/m)
                    geometric_mean = np.power(np.prod(elements), 1.0 / len(elements))
                    aggregated[i, j] = geometric_mean
                    
                    # Maintain reciprocal property
                    aggregated[j, i] = 1.0 / geometric_mean
    
    except Exception as e:
        raise GroupAggregationError(f"Error during geometric mean calculation: {str(e)}")
    
    logger.info("AHP matrix aggregation completed successfully")
    return aggregated


def aggregate_topsis_weights(weights: Dict[str, List[float]]) -> List[float]:
    """
    Aggregate multiple TOPSIS weight vectors using arithmetic mean.
    
    This method combines individual weight preferences into a group consensus
    using arithmetic mean, which is appropriate for TOPSIS because weights
    represent additive importance rather than multiplicative ratios.
    
    Mathematical Foundation:
    -----------------------
    For each criterion i:
    group_weight[i] = (Σ_{k=1}^{m} user_weight_k[i]) / m
    
    Where:
    - m = number of participants  
    - user_weight_k[i] = weight assigned to criterion i by participant k
    - Σ = summation operator (arithmetic mean)
    
    The arithmetic mean is preferred because:
    1. TOPSIS weights represent additive importance, not multiplicative ratios
    2. Final TOPSIS scores are linear combinations of weighted criteria
    3. Preserves intuitive interpretation of average group preference
    4. Mathematically consistent with TOPSIS's linear structure
    
    Args:
        weights: Dictionary mapping participant names to their weight vectors
                Each weight vector must be non-negative and preferably normalized
                
    Returns:
        List[float]: Aggregated and normalized group weights (sum = 1.0)
        
    Raises:
        GroupAggregationError: If weights are invalid or incompatible
        ValueError: If input validation fails
        
    Example:
        >>> user1_weights = [0.5, 0.3, 0.2]
        >>> user2_weights = [0.4, 0.4, 0.2] 
        >>> weights = {'user1': user1_weights, 'user2': user2_weights}
        >>> group_weights = aggregate_topsis_weights(weights)
        >>> print(group_weights)
        [0.45, 0.35, 0.2]
    """
    logger.info(f"Starting TOPSIS weight aggregation for {len(weights)} participants")
    
    # Input validation
    if not weights:
        raise ValueError("No weights provided for aggregation")
    
    if len(weights) < 2:
        logger.warning("Only one weight vector provided - returning normalized original")
        single_weights = list(weights.values())[0]
        normalized = np.array(single_weights) / np.sum(single_weights)
        return normalized.tolist()
    
    # Validate weight vectors
    participants = list(weights.keys())
    first_weights = weights[participants[0]]
    n_criteria = len(first_weights)
    
    # Check all weight vectors have same length
    for participant, weight_vector in weights.items():
        if len(weight_vector) != n_criteria:
            raise GroupAggregationError(
                f"Weight vector length mismatch: {participant} has {len(weight_vector)} "
                f"criteria, expected {n_criteria}"
            )
        
        # Check for non-negative weights
        if any(w < 0 for w in weight_vector):
            raise GroupAggregationError(
                f"Weight vector from {participant} contains negative values"
            )
        
        # Check for non-zero sum
        if sum(weight_vector) == 0:
            raise GroupAggregationError(
                f"Weight vector from {participant} sums to zero"
            )
    
    logger.info(f"Aggregating {n_criteria}-criteria weights from participants: {participants}")
    
    try:
        # Convert to numpy arrays for easier computation
        weight_arrays = [np.array(w) for w in weights.values()]
        weights_matrix = np.stack(weight_arrays)
        
        # Calculate arithmetic mean
        aggregated_weights = np.mean(weights_matrix, axis=0)
        
        # Normalize to sum to 1.0
        # If all weights are zero, avoid division by zero
        # (shouldn't happen due to validation, but just in case)
        if np.sum(aggregated_weights) == 0:
            raise GroupAggregationError("All aggregated weights sum to zero")
        
        normalized_weights = aggregated_weights / np.sum(aggregated_weights)
        
    except Exception as e:
        raise GroupAggregationError(f"Error during arithmetic mean calculation: {str(e)}")
    
    logger.info("TOPSIS weight aggregation completed successfully")
    return normalized_weights.tolist()


def validate_ahp_matrix_consistency(matrix: np.ndarray, threshold: float = 0.1) -> Dict:
    """
    Validate consistency of an AHP matrix using Saaty's Consistency Ratio.
    
    Consistency is crucial for reliable AHP results. This function computes
    the Consistency Ratio (CR) which should be ≤ 0.1 for acceptable consistency.
    
    Mathematical Foundation:
    -----------------------
    CR = CI / RI
    
    Where:
    - CI = (λmax - n) / (n - 1)  [Consistency Index]
    - RI = Random Index (from Saaty's table)
    - λmax = largest eigenvalue of the matrix
    - n = matrix size
    
    Args:
        matrix: Square AHP comparison matrix
        threshold: Consistency threshold (default 0.1 per Saaty)
        
    Returns:
        Dict containing:
        - consistency_ratio: CR value
        - is_consistent: Boolean (CR ≤ threshold)
        - lambda_max: Largest eigenvalue
        - consistency_index: CI value
        - matrix_size: Dimension of matrix
        
    Example:
        >>> matrix = np.array([[1, 2, 3], [0.5, 1, 2], [0.33, 0.5, 1]])
        >>> result = validate_ahp_matrix_consistency(matrix)
        >>> print(f"CR: {result['consistency_ratio']:.3f}")
        CR: 0.037
    """
    n = matrix.shape[0]
    
    if n <= 2:
        return {
            'consistency_ratio': 0.0,
            'is_consistent': True,
            'lambda_max': n,
            'consistency_index': 0.0,
            'matrix_size': n,
            'message': 'Perfect consistency for n ≤ 2'
        }
    
    # Calculate largest eigenvalue
    eigenvalues = np.linalg.eigvals(matrix)
    lambda_max = np.max(eigenvalues.real)
    
    # Consistency Index
    ci = (lambda_max - n) / (n - 1)
    
    # Random Index values (Saaty, 1980)
    random_indices = {
        3: 0.52, 4: 0.89, 5: 1.11, 6: 1.25, 7: 1.35,
        8: 1.40, 9: 1.45, 10: 1.49, 11: 1.52, 12: 1.54
    }
    
    ri = random_indices.get(n, 1.54)  # Use 1.54 for n > 12
    cr = ci / ri if ri > 0 else 0
    
    return {
        'consistency_ratio': cr,
        'is_consistent': cr <= threshold,
        'lambda_max': lambda_max,
        'consistency_index': ci,
        'random_index': ri,
        'matrix_size': n,
        'message': f"{'Acceptable' if cr <= threshold else 'Poor'} consistency"
    }


def validate_weight_vector(weights: List[float], name: str = "weights") -> Dict:
    """
    Validate a TOPSIS weight vector for mathematical correctness.
    
    Ensures weight vectors meet TOPSIS requirements:
    - Non-negative values
    - Non-zero sum
    - Reasonable distribution
    
    Args:
        weights: Weight vector to validate
        name: Name for error messages
        
    Returns:
        Dict containing validation results and warnings
    """
    validation = {
        'is_valid': True,
        'errors': [],
        'warnings': [],
        'weight_sum': sum(weights),
        'zero_weights': sum(1 for w in weights if w == 0),
        'weight_count': len(weights)
    }
    
    # Check non-negative
    if any(w < 0 for w in weights):
        validation['is_valid'] = False
        validation['errors'].append(f"{name} contains negative values")
    
    # Check non-zero sum
    weight_sum = sum(weights)
    if weight_sum == 0:
        validation['is_valid'] = False
        validation['errors'].append(f"{name} sum is zero")
    
    # Check normalization (with tolerance)
    if weight_sum > 0 and abs(weight_sum - 1.0) > 1e-6:
        validation['warnings'].append(
            f"{name} not normalized (sum = {weight_sum:.6f})"
        )
    
    # Check for zero weights
    zero_count = sum(1 for w in weights if w == 0)
    if zero_count > 0:
        validation['warnings'].append(
            f"{zero_count} out of {len(weights)} weights are zero"
        )
    
    return validation


def compute_group_ahp_priorities(matrices: Dict[str, np.ndarray]) -> Dict:
    """
    Complete AHP group decision process: aggregate matrices and compute priorities.
    
    This is a high-level function that combines matrix aggregation with
    priority vector calculation and consistency checking.
    
    Args:
        matrices: Dictionary of individual comparison matrices
        
    Returns:
        Dict containing:
        - aggregated_matrix: Group consensus matrix
        - priority_weights: Group priority vector
        - consistency_info: Consistency validation results
        - individual_consistency: Per-participant consistency
        
    Example:
        >>> matrices = {'user1': matrix1, 'user2': matrix2}
        >>> result = compute_group_ahp_priorities(matrices)
        >>> print(f"Group weights: {result['priority_weights']}")
    """
    logger.info("Computing complete AHP group priorities")
    
    # Check individual consistency first
    individual_consistency = {}
    for participant, matrix in matrices.items():
        consistency = validate_ahp_matrix_consistency(matrix)
        individual_consistency[participant] = consistency
        
        if not consistency['is_consistent']:
            logger.warning(
                f"Participant {participant} has poor consistency "
                f"(CR = {consistency['consistency_ratio']:.3f})"
            )
    
    # Aggregate matrices
    aggregated_matrix = aggregate_ahp_matrices(matrices)
    
    # Calculate group priorities using eigenvalue method
    eigenvalues, eigenvectors = np.linalg.eig(aggregated_matrix)
    max_eigenvalue_index = np.argmax(eigenvalues.real)
    priority_vector = eigenvectors[:, max_eigenvalue_index].real
    
    # Normalize to positive values summing to 1
    priority_vector = np.abs(priority_vector)
    priority_weights = priority_vector / np.sum(priority_vector)
    
    # Check group consistency
    group_consistency = validate_ahp_matrix_consistency(aggregated_matrix)
    
    return {
        'aggregated_matrix': aggregated_matrix,
        'priority_weights': priority_weights.tolist(),
        'consistency_info': group_consistency,
        'individual_consistency': individual_consistency,
        'participants': list(matrices.keys()),
        'method': 'AHP_Geometric_Mean_Aggregation'
    }


def compute_group_topsis_weights(weights: Dict[str, List[float]]) -> Dict:
    """
    Complete TOPSIS weight aggregation with validation.
    
    This is a high-level function that combines weight aggregation with
    comprehensive validation and quality assessment.
    
    Args:
        weights: Dictionary of individual weight vectors
        
    Returns:
        Dict containing:
        - aggregated_weights: Group consensus weights
        - validation_info: Weight validation results
        - individual_validation: Per-participant validation
        - quality_metrics: Distribution and consistency metrics
        
    Example:
        >>> weights = {'user1': [0.5, 0.3, 0.2], 'user2': [0.4, 0.4, 0.2]}
        >>> result = compute_group_topsis_weights(weights)
        >>> print(f"Group weights: {result['aggregated_weights']}")
    """
    logger.info("Computing complete TOPSIS group weights")
    
    # Validate individual weight vectors
    individual_validation = {}
    for participant, weight_vector in weights.items():
        validation = validate_weight_vector(weight_vector, f"{participant}_weights")
        individual_validation[participant] = validation
        
        if not validation['is_valid']:
            logger.warning(f"Invalid weights from {participant}: {validation['errors']}")
    
    # Aggregate weights
    aggregated_weights = aggregate_topsis_weights(weights)
    
    # Validate group weights
    group_validation = validate_weight_vector(aggregated_weights, "group_weights")
    
    # Calculate quality metrics
    weight_array = np.array(aggregated_weights)
    quality_metrics = {
        'weight_variance': np.var(weight_array),
        'weight_std': np.std(weight_array),
        'max_weight': np.max(weight_array),
        'min_weight': np.min(weight_array),
        'weight_range': np.max(weight_array) - np.min(weight_array),
        'effective_criteria': np.sum(weight_array > 1e-6)  # Non-negligible weights
    }
    
    return {
        'aggregated_weights': aggregated_weights,
        'validation_info': group_validation,
        'individual_validation': individual_validation,
        'quality_metrics': quality_metrics,
        'participants': list(weights.keys()),
        'method': 'TOPSIS_Arithmetic_Mean_Aggregation'
    }


# Convenience functions for backward compatibility
def aggregate_matrices(matrices: Dict[str, np.ndarray]) -> np.ndarray:
    """Alias for aggregate_ahp_matrices for backward compatibility"""
    return aggregate_ahp_matrices(matrices)


def aggregate_weights(weights: Dict[str, List[float]]) -> List[float]:
    """Alias for aggregate_topsis_weights for backward compatibility"""
    return aggregate_topsis_weights(weights)