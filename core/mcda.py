"""
Multi-Criteria Decision Analysis (MCDA) Module

This module provides AHP (Analytic Hierarchy Process) and TOPSIS (Technique for 
Order of Preference by Similarity to Ideal Solution) methods to analyze and rank
PyMOO optimization results based on multiple criteria.

Key Features:
- AHP implementation with pairwise comparison matrices and eigenvalue-based weighting
- TOPSIS implementation with ideal/anti-ideal solutions and distance-based ranking
- Automatic normalization and weight calculation
- Comprehensive ranking and scoring
- Integration with PyMOO results
- Interactive GUI for method selection and parameter configuration

MCDA Weighting Methodology:
============================

AHP (Analytic Hierarchy Process):
---------------------------------
AHP uses pairwise comparisons to derive criteria weights through eigenvalue decomposition.
The process involves:
1. Constructing a reciprocal pairwise comparison matrix from expert judgments
2. Computing the principal eigenvector to obtain criteria weights
3. Checking consistency using the Consistency Ratio (CR < 0.1)
4. Applying weights to normalized alternative scores

Weighting Formula: w = principal_eigenvector / sum(principal_eigenvector)
Where the principal eigenvector corresponds to the largest eigenvalue of the comparison matrix.

TOPSIS (Technique for Order of Preference by Similarity to Ideal Solution):
---------------------------------------------------------------------------
TOPSIS can use any weighting scheme (equal, AHP-derived, or expert-assigned weights).
The method focuses on distance-based ranking rather than weight derivation:
1. Normalizes the decision matrix (vector or linear normalization)
2. Applies predetermined weights to create weighted normalized matrix
3. Identifies ideal (best) and anti-ideal (worst) solutions
4. Calculates relative closeness to ideal solution: CC = d⁻/(d⁺ + d⁻)

Where d⁺ = distance to ideal, d⁻ = distance to anti-ideal solution.

References:
-----------
Saaty, T. L. (1980). The Analytic Hierarchy Process: Planning, Priority Setting, 
    Resource Allocation. McGraw-Hill.

Hwang, C. L., & Yoon, K. (1981). Multiple Attribute Decision Making: Methods and 
    Applications. Springer-Verlag.

Triantaphyllou, E. (2000). Multi-criteria decision making methods: A comparative study. 
    Applied Optimization, 44. Springer.

Classes:
    AHPAnalyzer: Implements Analytic Hierarchy Process with eigenvalue weighting
    TOPSISAnalyzer: Implements TOPSIS method with flexible weighting schemes
    MCDAManager: Main interface for MCDA analysis

Author: Elias Rizos [it21490]
MCDA Version: 1.0.0
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Tuple, Optional, Union
import math


class AHPAnalyzer:
    """
    Analytic Hierarchy Process (AHP) Implementation
    
    AHP is a structured technique for organizing and analyzing complex decisions,
    based on mathematics and psychology. It helps decision makers find the choice
    that best suits their goal and understanding of the problem.
    
    AHP WEIGHTING METHODOLOGY:
    =========================
    
    1. Pairwise Comparison Matrix Construction:
       - Decision makers provide pairwise comparisons using Saaty's 1-9 scale
       - Scale: 1=Equal, 3=Moderate, 5=Strong, 7=Very Strong, 9=Extreme importance
       - Matrix A where a_ij represents importance of criterion i over criterion j
       - Reciprocal property: a_ji = 1/a_ij ensures mathematical consistency
    
    2. Weight Derivation through Eigenvalue Method:
       - Weights are computed as the normalized principal eigenvector of matrix A
       - Principal eigenvector corresponds to the largest eigenvalue (λ_max)
       - Mathematical foundation: A·w = λ_max·w (eigenvalue equation)
       - Normalization ensures sum of weights equals 1: w_i = v_i / Σv_i
    
    3. Consistency Verification:
       - Consistency Index: CI = (λ_max - n)/(n-1)
       - Consistency Ratio: CR = CI/RI (where RI is Random Index)
       - Acceptable consistency: CR < 0.10 (Saaty, 1980)
       - If CR ≥ 0.10, pairwise comparisons should be revised
    
    4. Alternative Scoring:
       - Alternatives normalized to [0,1] scale for each criterion
       - Final score: S_i = Σ(w_j × normalized_score_ij)
       - Higher scores indicate better alternatives
    
    Reference: Saaty, T. L. (1980). The Analytic Hierarchy Process. McGraw-Hill.
    
    Key Steps:
    1. Create pairwise comparison matrix
    2. Calculate priority weights
    3. Check consistency ratio
    4. Score alternatives based on weights
    """
    
    def __init__(self):
        """Initialize AHP analyzer"""
        self.criteria_weights = None
        self.consistency_ratio = None
        self.pairwise_matrix = None
        
    def create_pairwise_matrix(self, criteria_comparisons: Dict[Tuple[str, str], float], criteria_names: List[str] = None) -> np.ndarray:
        """
        Create pairwise comparison matrix from user preferences
        
        Args:
            criteria_comparisons: Dict with (criterion1, criterion2) -> preference_value
                                 Values: 1-9 scale where:
                                 1 = Equal importance
                                 3 = Moderate importance  
                                 5 = Strong importance
                                 7 = Very strong importance
                                 9 = Extreme importance
            criteria_names: Optional list to preserve order of criteria (if None, extracted from comparisons)
                                 
        Returns:
            Pairwise comparison matrix
        """
        # Use provided criteria names or extract from comparisons
        if criteria_names is None:
            criteria_names = list(set([item for pair in criteria_comparisons.keys() for item in pair]))
        
        n = len(criteria_names)
        matrix = np.ones((n, n))
        
        for i, crit_i in enumerate(criteria_names):
            for j, crit_j in enumerate(criteria_names):
                if i != j:
                    if (crit_i, crit_j) in criteria_comparisons:
                        matrix[i, j] = criteria_comparisons[(crit_i, crit_j)]
                    elif (crit_j, crit_i) in criteria_comparisons:
                        matrix[i, j] = 1.0 / criteria_comparisons[(crit_j, crit_i)]
                        
        self.pairwise_matrix = matrix
        self.criteria_names = criteria_names
        return matrix
        
    def calculate_weights(self, matrix: np.ndarray) -> np.ndarray:
        """
        Calculate priority weights using eigenvalue method
        
        EIGENVALUE-BASED WEIGHT CALCULATION:
        ===================================
        
        The AHP weight calculation is based on the Perron-Frobenius theorem for positive 
        reciprocal matrices. The principal eigenvector of the pairwise comparison matrix
        represents the relative importance (weights) of criteria.
        
        Mathematical Process:
        1. Solve eigenvalue equation: A·w = λ_max·w
        2. Find largest eigenvalue (λ_max) and corresponding eigenvector
        3. Normalize eigenvector to sum to 1.0
        4. Resulting vector represents criteria weights
        
        Theoretical Justification:
        - For consistent matrices: λ_max = n (number of criteria)
        - For inconsistent matrices: λ_max > n (used for consistency checking)
        - Principal eigenvector provides the best approximation of true weights
        - Method is robust to small inconsistencies in human judgment
        
        Reference: Saaty, T. L. (1980). The Analytic Hierarchy Process, Chapter 3.
        
        Args:
            matrix: Pairwise comparison matrix (n×n reciprocal matrix)
            
        Returns:
            Priority weights vector (normalized principal eigenvector)
        """
        # Calculate eigenvalues and eigenvectors using numpy's linear algebra solver
        eigenvalues, eigenvectors = np.linalg.eig(matrix)
        
        # Find the largest eigenvalue and corresponding eigenvector
        # The largest eigenvalue corresponds to the principal eigenvector
        max_eigenvalue_idx = np.argmax(np.abs(eigenvalues.real))
        max_eigenvalue = eigenvalues[max_eigenvalue_idx].real
        principal_eigenvector = eigenvectors[:, max_eigenvalue_idx].real
        
        # Normalize the eigenvector to get weights that sum to 1.0
        # This transforms the eigenvector into priority weights
        weights = principal_eigenvector / np.sum(principal_eigenvector)
        
        # Ensure positive weights (eigenvectors can have negative components)
        # Take absolute value and renormalize to maintain mathematical validity
        weights = np.abs(weights)
        weights = weights / np.sum(weights)
        
        # Store for consistency calculation
        self.criteria_weights = weights
        self.max_eigenvalue = max_eigenvalue
        
        return weights
        
    def calculate_consistency_ratio(self, matrix: np.ndarray, weights: np.ndarray) -> float:
        """
        Calculate Consistency Ratio (CR) to check matrix consistency
        
        CONSISTENCY VERIFICATION IN AHP:
        ================================
        
        Consistency checking is crucial in AHP because human judgments are inherently
        prone to inconsistencies. The Consistency Ratio measures how consistent the
        pairwise comparisons are with each other.
        
        Mathematical Foundation:
        1. Consistency Index (CI) = (λ_max - n)/(n-1)
           - For perfectly consistent matrix: λ_max = n, so CI = 0
           - Larger CI indicates greater inconsistency
        
        2. Random Index (RI) = Average CI of randomly generated matrices
           - Accounts for inconsistency due to matrix size
           - Values empirically determined by Saaty (1980)
        
        3. Consistency Ratio (CR) = CI/RI
           - Normalizes CI by expected random inconsistency
           - CR < 0.10: Acceptable consistency (Saaty's threshold)
           - CR ≥ 0.10: Judgments should be revised
        
        Practical Implications:
        - CR provides quality control for decision-making process
        - Helps identify and correct inconsistent judgments
        - Ensures reliability of derived weights
        
        Reference: Saaty, T. L. (1980). The Analytic Hierarchy Process, Chapter 4.
        
        Args:
            matrix: Pairwise comparison matrix
            weights: Priority weights from eigenvalue calculation
            
        Returns:
            Consistency ratio (should be < 0.1 for acceptable consistency)
        """
        n = matrix.shape[0]
        
        # Calculate Consistency Index (CI)
        # CI measures deviation from perfect consistency
        lambda_max = self.max_eigenvalue
        ci = (lambda_max - n) / (n - 1)
        
        # Random Index (RI) values for different matrix sizes
        # These are empirically determined average consistency indices
        # for randomly generated reciprocal matrices (Saaty, 1980)
        ri_values = {1: 0, 2: 0, 3: 0.58, 4: 0.90, 5: 1.12, 6: 1.24, 7: 1.32, 8: 1.41, 9: 1.45, 10: 1.49}
        ri = ri_values.get(n, 1.49)  # Use 1.49 for matrices larger than 10×10
        
        # Consistency Ratio = CI normalized by expected random inconsistency
        cr = ci / ri if ri > 0 else 0
        
        self.consistency_ratio = cr
        return cr
        
    def score_alternatives(self, alternatives: np.ndarray, weights: np.ndarray, 
                          objectives_info: List[Dict] = None) -> np.ndarray:
        """
        Score alternatives using calculated weights with intuitive objective handling
        
        ALTERNATIVE SCORING IN AHP WITH PYMOO INTEGRATION:
        =================================================
        
        This scoring method directly respects PyMOO objective directions:
        - Minimize objectives: Lower values are better → get higher AHP scores
        - Maximize objectives: Higher values are better → get higher AHP scores
        
        This creates an intuitive mapping where the AHP scoring aligns with the
        optimization intent rather than forcing all criteria into "benefit" format.
        
        Scoring Process:
        1. Normalize alternative performance matrix respecting PyMOO directions
           - For MINIMIZE objectives: Lower actual values → Higher normalized scores
           - For MAXIMIZE objectives: Higher actual values → Higher normalized scores
           - All normalized values in [0,1] where 1 = best according to objective
        
        2. Apply weighted linear combination
           - Final score: S_i = Σ(w_j × normalized_performance_ij)
           - Higher final scores indicate better alternatives overall
        
        3. Ranking interpretation
           - Higher AHP scores = better alternatives
           - Scoring directly reflects optimization objectives
           - No conceptual transformation needed
        
        Normalization Logic:
        - MINIMIZE: score = (max_value - actual_value) / (max_value - min_value)
          → Lower actual values get scores closer to 1.0
        - MAXIMIZE: score = (actual_value - min_value) / (max_value - min_value)  
          → Higher actual values get scores closer to 1.0
        
        Example:
        Cost objective (MINIMIZE): [100, 80, 120] → [0.5, 1.0, 0.0]
        Quality objective (MAXIMIZE): [6, 8, 9] → [0.0, 0.67, 1.0]
        
        Args:
            alternatives: Matrix of alternatives (rows) vs criteria (columns)
            weights: Criteria weights from AHP eigenvalue calculation
            objectives_info: List of objective info dicts with 'direction' key
            
        Returns:
            AHP scores for each alternative (higher = better overall performance)
        """

        # Normalize alternatives matrix respecting PyMOO objective directions
        normalized = alternatives.copy().astype(float)
        
        for j in range(alternatives.shape[1]):
            col_max = np.max(alternatives[:, j])
            col_min = np.min(alternatives[:, j])
            
            if col_max != col_min:
                # Determine objective direction from PyMOO
                if objectives_info and j < len(objectives_info):
                    direction = objectives_info[j].get('direction', 'Minimize')
                else:
                    direction = 'Minimize'  # Default assumption for PyMOO
                
                if direction == 'Minimize':
                    # MINIMIZE: Lower values are better
                    # Invert scale so lower actual values get higher scores
                    normalized[:, j] = (col_max - alternatives[:, j]) / (col_max - col_min)
                else:  # Maximize
                    # MAXIMIZE: Higher values are better  
                    # Standard scale so higher actual values get higher scores
                    normalized[:, j] = (alternatives[:, j] - col_min) / (col_max - col_min)
            else:
                # Handle case where all alternatives have same value for criterion j
                normalized[:, j] = 1.0
        
        # Calculate weighted scores using linear additive model
        # Final AHP score = weighted sum of normalized criterion scores
        # Higher scores indicate better alternatives according to their PyMOO objectives
        scores = np.dot(normalized, weights)
        return scores
        
    def analyze(self, alternatives: np.ndarray, criteria_comparisons: Dict[Tuple[str, str], float], 
                criteria_names: List[str] = None, objectives_info: List[Dict] = None) -> Dict:
        """
        Complete AHP analysis
        
        Args:
            alternatives: Matrix of alternatives vs criteria
            criteria_comparisons: Pairwise comparison preferences
            criteria_names: Optional list to preserve order of criteria
            objectives_info: Optional list of objective info dicts with 'direction' key
            
        Returns:
            Analysis results dictionary
        """
        # Create pairwise matrix
        matrix = self.create_pairwise_matrix(criteria_comparisons, criteria_names)
        
        # Calculate weights
        weights = self.calculate_weights(matrix)
        
        # Check consistency
        cr = self.calculate_consistency_ratio(matrix, weights)
        
        # Score alternatives with proper objective handling
        scores = self.score_alternatives(alternatives, weights, objectives_info)
        
        # Rank alternatives
        rankings = np.argsort(-scores) + 1  # +1 for 1-based ranking
        
        return {
            'method': 'AHP',
            'weights': weights,
            'criteria_names': self.criteria_names,
            'scores': scores,
            'rankings': rankings,
            'consistency_ratio': cr,
            'pairwise_matrix': matrix,
            'is_consistent': cr < 0.1
        }


class TOPSISAnalyzer:
    """
    TOPSIS (Technique for Order of Preference by Similarity to Ideal Solution)
    
    TOPSIS is based on the concept that the chosen alternative should have the
    shortest geometric distance from the ideal solution and the longest geometric
    distance from the anti-ideal solution.
    
    TOPSIS METHODOLOGY AND WEIGHTING:
    =================================
    
    Unlike AHP, TOPSIS does not derive weights from comparisons. Instead, it accepts
    any weighting scheme (equal weights, AHP-derived weights, expert weights, etc.)
    and focuses on ranking alternatives based on their similarity to ideal solutions.
    
    Core Principle:
    - Best alternative = closest to ideal solution + farthest from anti-ideal solution
    - Uses geometric distance in multi-dimensional criterion space
    - Provides relative closeness coefficient (0 ≤ CC ≤ 1, higher is better)
    
    WEIGHTING IN TOPSIS:
    ===================
    
    1. Weight Application:
       - Weights are applied after normalization: V = W × R
       - Where V = weighted normalized matrix, W = weights, R = normalized matrix
       - Each criterion value is multiplied by its respective weight
       - Weights represent relative importance of criteria
    
    2. Weight Sources:
       - Equal weights: w_i = 1/n (simple but may not reflect true importance)
       - AHP-derived weights: w from eigenvalue decomposition of pairwise comparisons
       - Expert weights: directly assigned by domain experts
       - Objective weights: derived from data (e.g., entropy method)
    
    3. Impact on Results:
       - Higher weights amplify differences in criterion performance
       - Lower weights reduce criterion influence on final ranking
       - Weight distribution directly affects ideal/anti-ideal solution identification
    
    Mathematical Foundation:
    - Euclidean distance in weighted criterion space
    - Closeness coefficient: CC_i = d_i⁻ / (d_i⁺ + d_i⁻)
    - Where d_i⁺ = distance to ideal, d_i⁻ = distance to anti-ideal
    
    References:
    Hwang, C. L., & Yoon, K. (1981). Multiple Attribute Decision Making. Springer-Verlag.
    Chen, C. T. (2000). Extensions of the TOPSIS for group decision-making under fuzzy environment. 
        Fuzzy Sets and Systems, 114(1), 1-9.
    
    Key Steps:
    1. Normalize the decision matrix
    2. Calculate weighted normalized matrix
    3. Identify ideal and anti-ideal solutions
    4. Calculate distances to ideal and anti-ideal solutions
    5. Calculate closeness coefficient
    6. Rank alternatives
    """
    
    def __init__(self):
        """Initialize TOPSIS analyzer"""
        self.weights = None
        self.ideal_solution = None
        self.anti_ideal_solution = None
        
    def normalize_matrix(self, matrix: np.ndarray, method: str = 'vector') -> np.ndarray:
        """
        Normalize decision matrix
        
        Args:
            matrix: Decision matrix (alternatives x criteria)
            method: Normalization method ('vector' or 'linear')
            
        Returns:
            Normalized matrix
        """
        if method == 'vector':
            # Vector normalization (default for TOPSIS)
            norms = np.sqrt(np.sum(matrix**2, axis=0))
            norms[norms == 0] = 1  # Avoid division by zero
            normalized = matrix / norms
        elif method == 'linear':
            # Linear normalization
            normalized = matrix.copy()
            for j in range(matrix.shape[1]):
                col_max = np.max(matrix[:, j])
                col_min = np.min(matrix[:, j])
                if col_max != col_min:
                    normalized[:, j] = (matrix[:, j] - col_min) / (col_max - col_min)
                else:
                    normalized[:, j] = 1.0
        else:
            raise ValueError("Method must be 'vector' or 'linear'")
            
        return normalized
        
    def calculate_weighted_matrix(self, normalized_matrix: np.ndarray, weights: np.ndarray) -> np.ndarray:
        """
        Calculate weighted normalized decision matrix
        
        WEIGHT APPLICATION IN TOPSIS:
        =============================
        
        This step applies criteria weights to the normalized decision matrix, creating
        the weighted normalized matrix that will be used for ideal solution identification
        and distance calculations.
        
        Mathematical Process:
        V_ij = w_j × r_ij
        
        Where:
        - V_ij = weighted normalized value for alternative i, criterion j
        - w_j = weight of criterion j (Σw_j = 1)
        - r_ij = normalized value for alternative i, criterion j
        
        Weight Impact:
        - High weights (w_j → 1): Criterion j dominates the decision
        - Low weights (w_j → 0): Criterion j has minimal influence
        - Equal weights (w_j = 1/n): All criteria contribute equally
        
        The weighted matrix preserves the relative performance relationships while
        incorporating the decision maker's preferences about criterion importance.
        
        Args:
            normalized_matrix: Normalized decision matrix (alternatives × criteria)
            weights: Criteria weights vector (must sum to 1.0)
            
        Returns:
            Weighted normalized matrix (V = W × R)
        """
        # Element-wise multiplication: each column j multiplied by weight w_j
        # Broadcasting ensures weight w_j applies to entire column j
        return normalized_matrix * weights
        
    def identify_ideal_solutions(self, weighted_matrix: np.ndarray, 
                               benefit_criteria: List[int], 
                               cost_criteria: List[int]) -> Tuple[np.ndarray, np.ndarray]:
        """
        Identify ideal and anti-ideal solutions
        
        IDEAL SOLUTION IDENTIFICATION IN TOPSIS:
        ========================================
        
        The ideal and anti-ideal solutions represent the best and worst possible
        performance across all criteria, considering their benefit/cost nature.
        
        Ideal Solution (A⁺):
        - For benefit criteria: A⁺_j = max(V_ij) for all i
        - For cost criteria: A⁺_j = min(V_ij) for all i
        - Represents the "perfect" alternative (best on all criteria)
        
        Anti-Ideal Solution (A⁻):
        - For benefit criteria: A⁻_j = min(V_ij) for all i  
        - For cost criteria: A⁻_j = max(V_ij) for all i
        - Represents the "worst" alternative (worst on all criteria)
        
        Criterion Types:
        1. Benefit criteria (higher is better):
           - Examples: profit, quality, efficiency, customer satisfaction
           - Ideal = maximum value, Anti-ideal = minimum value
        
        2. Cost criteria (lower is better):
           - Examples: cost, time, defects, environmental impact
           - Ideal = minimum value, Anti-ideal = maximum value
        
        Weight Influence:
        The weighted matrix values (V_ij) already incorporate criterion importance,
        so ideal solutions reflect both performance and weight significance.
        Higher weights amplify the range between ideal and anti-ideal values.
        
        Reference: Hwang, C. L., & Yoon, K. (1981). Multiple Attribute Decision Making, Chapter 4.
        
        Args:
            weighted_matrix: Weighted normalized matrix (V)
            benefit_criteria: Indices of benefit criteria (higher is better)
            cost_criteria: Indices of cost criteria (lower is better)
            
        Returns:
            Tuple of (ideal_solution, anti_ideal_solution)
        """
        ideal = np.zeros(weighted_matrix.shape[1])
        anti_ideal = np.zeros(weighted_matrix.shape[1])
        
        # For benefit criteria: ideal = max, anti-ideal = min
        # Higher values are preferred, so best case = maximum value
        for j in benefit_criteria:
            ideal[j] = np.max(weighted_matrix[:, j])
            anti_ideal[j] = np.min(weighted_matrix[:, j])
            
        # For cost criteria: ideal = min, anti-ideal = max  
        # Lower values are preferred, so best case = minimum value
        for j in cost_criteria:
            ideal[j] = np.min(weighted_matrix[:, j])
            anti_ideal[j] = np.max(weighted_matrix[:, j])
            
        self.ideal_solution = ideal
        self.anti_ideal_solution = anti_ideal
        
        return ideal, anti_ideal
        
    def calculate_distances(self, weighted_matrix: np.ndarray, 
                          ideal: np.ndarray, 
                          anti_ideal: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Calculate Euclidean distances to ideal and anti-ideal solutions
        
        Args:
            weighted_matrix: Weighted normalized matrix
            ideal: Ideal solution vector
            anti_ideal: Anti-ideal solution vector
            
        Returns:
            Tuple of (distances_to_ideal, distances_to_anti_ideal)
        """
        # Distance to ideal solution
        d_plus = np.sqrt(np.sum((weighted_matrix - ideal)**2, axis=1))
        
        # Distance to anti-ideal solution  
        d_minus = np.sqrt(np.sum((weighted_matrix - anti_ideal)**2, axis=1))
        
        return d_plus, d_minus
        
    def calculate_closeness_coefficient(self, d_plus: np.ndarray, d_minus: np.ndarray) -> np.ndarray:
        """
        Calculate closeness coefficient (relative closeness to ideal solution)
        
        CLOSENESS COEFFICIENT IN TOPSIS:
        ================================
        
        The closeness coefficient (CC) represents the relative closeness of each
        alternative to the ideal solution. It provides the final ranking metric
        in TOPSIS methodology.
        
        Mathematical Formula:
        CC_i = d_i⁻ / (d_i⁺ + d_i⁻)
        
        Where:
        - CC_i = closeness coefficient for alternative i
        - d_i⁺ = Euclidean distance from alternative i to ideal solution
        - d_i⁻ = Euclidean distance from alternative i to anti-ideal solution
        
        Interpretation:
        - CC_i = 1: Alternative is identical to ideal solution (best possible)
        - CC_i = 0: Alternative is identical to anti-ideal solution (worst possible)
        - 0 < CC_i < 1: Alternative is between ideal and anti-ideal solutions
        - Higher CC_i values indicate better alternatives
        
        Geometric Interpretation:
        The closeness coefficient represents the relative position of an alternative
        in the line segment connecting the ideal and anti-ideal solutions. It
        measures how much closer the alternative is to the ideal versus anti-ideal.
        
        Weight Influence:
        Since distances are calculated in weighted criterion space, the closeness
        coefficient inherently reflects the importance weights assigned to criteria.
        Alternatives performing well on highly weighted criteria will have higher CC values.
        
        Reference: Hwang, C. L., & Yoon, K. (1981). Multiple Attribute Decision Making, pp. 128-135.
        
        Args:
            d_plus: Distances to ideal solution for each alternative
            d_minus: Distances to anti-ideal solution for each alternative
            
        Returns:
            Closeness coefficients (0-1, higher is better)
        """
        # Avoid division by zero in degenerate cases
        # If both distances are zero, alternative equals both ideal and anti-ideal
        denominator = d_plus + d_minus
        denominator[denominator == 0] = 1e-10  # Small epsilon to prevent numerical issues
        
        # Calculate relative closeness to ideal solution
        # CC = 1 when d_plus = 0 (at ideal), CC = 0 when d_minus = 0 (at anti-ideal)
        closeness = d_minus / denominator
        return closeness
        
    def analyze(self, alternatives: np.ndarray, 
                weights: np.ndarray,
                benefit_criteria: List[int] = None,
                cost_criteria: List[int] = None,
                normalization_method: str = 'vector') -> Dict:
        """
        Complete TOPSIS analysis
        
        Args:
            alternatives: Decision matrix (alternatives x criteria)
            weights: Criteria weights
            benefit_criteria: Indices of benefit criteria (default: all)
            cost_criteria: Indices of cost criteria (default: none)
            normalization_method: 'vector' or 'linear'
            
        Returns:
            Analysis results dictionary
        """
        n_criteria = alternatives.shape[1]
        
        # Set default criteria types
        if benefit_criteria is None and cost_criteria is None:
            benefit_criteria = list(range(n_criteria))
            cost_criteria = []
        elif benefit_criteria is None:
            benefit_criteria = [i for i in range(n_criteria) if i not in cost_criteria]
        elif cost_criteria is None:
            cost_criteria = [i for i in range(n_criteria) if i not in benefit_criteria]
            
        self.weights = weights
        
        # Step 1: Normalize decision matrix
        normalized = self.normalize_matrix(alternatives, normalization_method)
        
        # Step 2: Calculate weighted normalized matrix
        weighted = self.calculate_weighted_matrix(normalized, weights)
        
        # Step 3: Identify ideal and anti-ideal solutions
        ideal, anti_ideal = self.identify_ideal_solutions(weighted, benefit_criteria, cost_criteria)
        
        # Step 4: Calculate distances
        d_plus, d_minus = self.calculate_distances(weighted, ideal, anti_ideal)
        
        # Step 5: Calculate closeness coefficient
        closeness = self.calculate_closeness_coefficient(d_plus, d_minus)
        
        # Step 6: Rank alternatives
        rankings = np.argsort(-closeness) + 1  # +1 for 1-based ranking
        
        return {
            'method': 'TOPSIS',
            'weights': weights,
            'scores': closeness,
            'rankings': rankings,
            'normalized_matrix': normalized,
            'weighted_matrix': weighted,
            'ideal_solution': ideal,
            'anti_ideal_solution': anti_ideal,
            'distances_to_ideal': d_plus,
            'distances_to_anti_ideal': d_minus,
            'benefit_criteria': benefit_criteria,
            'cost_criteria': cost_criteria
        }


class MCDAManager:
    """
    Multi-Criteria Decision Analysis Manager
    
    Main interface for performing MCDA analysis on PyMOO optimization results.
    Provides methods to convert PyMOO results to MCDA format and apply different
    analysis methods.
    """
    
    def __init__(self):
        """Initialize MCDA manager"""
        self.ahp = AHPAnalyzer()
        self.topsis = TOPSISAnalyzer()
        self.last_analysis = None
        
    def prepare_pymoo_results(self, result, objectives_info: List[Dict]) -> Tuple[np.ndarray, List[str], List[int], List[int]]:
        """
        Convert PyMOO optimization results to MCDA format
        
        Args:
            result: PyMOO optimization result object
            objectives_info: List of objective information dicts with 'name' and 'direction'
            
        Returns:
            Tuple of (alternatives_matrix, criteria_names, benefit_criteria, cost_criteria)
        """
        # Extract objective values (F matrix)
        objectives_matrix = result.F
        
        # Handle single solution case
        if objectives_matrix.ndim == 1:
            objectives_matrix = objectives_matrix.reshape(1, -1)
            
        # Process objectives based on their intended direction
        processed_matrix = objectives_matrix.copy()
        criteria_names = []
        benefit_criteria = []
        cost_criteria = []
        
        for i, obj_info in enumerate(objectives_info):
            criteria_names.append(obj_info.get('name', f'Objective_{i+1}'))
            direction = obj_info.get('direction', 'Minimize')
            
            if direction == 'Maximize':
                # For maximization objectives, higher values are better (benefit criteria)
                # No negation needed - use values as they come from PyMOO
                benefit_criteria.append(i)
            else:  # Minimize
                # For minimization objectives, lower values are better (cost criteria)
                cost_criteria.append(i)
                
        return processed_matrix, criteria_names, benefit_criteria, cost_criteria
        
    def create_default_weights(self, n_criteria: int) -> np.ndarray:
        """Create equal weights for all criteria"""
        return np.ones(n_criteria) / n_criteria
        
    def create_pairwise_comparisons_equal(self, criteria_names: List[str]) -> Dict[Tuple[str, str], float]:
        """
        Create pairwise comparisons matrix with equal importance for all criteria
        
        Args:
            criteria_names: List of criteria names
            
        Returns:
            Dictionary of pairwise comparisons (all equal = 1.0)
        """
        comparisons = {}
        for i, crit1 in enumerate(criteria_names):
            for j, crit2 in enumerate(criteria_names):
                if i < j:  # Only upper triangle needed
                    comparisons[(crit1, crit2)] = 1.0  # Equal importance
        return comparisons
        
    def analyze_with_ahp(self, pymoo_result, objectives_info: List[Dict], 
                        criteria_comparisons: Dict[Tuple[str, str], float] = None) -> Dict:
        """
        Perform AHP analysis on PyMOO results
        
        Args:
            pymoo_result: PyMOO optimization result
            objectives_info: Objective information with 'name' and 'direction' keys
            criteria_comparisons: Pairwise comparison preferences
            
        Returns:
            AHP analysis results
        """
        # Prepare data
        alternatives, criteria_names, benefit_criteria, cost_criteria = self.prepare_pymoo_results(
            pymoo_result, objectives_info
        )
        
        # Use equal comparisons if none provided
        if criteria_comparisons is None:
            criteria_comparisons = self.create_pairwise_comparisons_equal(criteria_names)
            
        # Perform AHP analysis with criteria names and objectives info to preserve order and handle directions
        results = self.ahp.analyze(alternatives, criteria_comparisons, criteria_names, objectives_info)
        
        # Add additional information
        results['alternatives_count'] = alternatives.shape[0]
        results['criteria_count'] = alternatives.shape[1]
        results['alternatives_matrix'] = alternatives
        results['benefit_criteria'] = benefit_criteria
        results['cost_criteria'] = cost_criteria
        
        self.last_analysis = results
        return results
        
    def analyze_with_topsis(self, pymoo_result, objectives_info: List[Dict],
                          weights: np.ndarray = None,
                          normalization_method: str = 'vector') -> Dict:
        """
        Perform TOPSIS analysis on PyMOO results
        
        Args:
            pymoo_result: PyMOO optimization result
            objectives_info: Objective information
            weights: Criteria weights (default: equal weights)
            normalization_method: 'vector' or 'linear'
            
        Returns:
            TOPSIS analysis results
        """
        # Prepare data
        alternatives, criteria_names, benefit_criteria, cost_criteria = self.prepare_pymoo_results(
            pymoo_result, objectives_info
        )
        
        # Use equal weights if none provided
        if weights is None:
            weights = self.create_default_weights(len(criteria_names))
            
        # Perform TOPSIS analysis
        results = self.topsis.analyze(
            alternatives, weights, benefit_criteria, cost_criteria, normalization_method
        )
        
        # Add additional information
        results['alternatives_count'] = alternatives.shape[0]
        results['criteria_count'] = alternatives.shape[1]
        results['criteria_names'] = criteria_names
        results['alternatives_matrix'] = alternatives
        
        self.last_analysis = results
        return results
        
    def get_ranking_summary(self, analysis_results: Dict, top_n: int = 10) -> pd.DataFrame:
        """
        Get a summary of the top-ranked alternatives
        
        Args:
            analysis_results: Results from AHP or TOPSIS analysis
            top_n: Number of top alternatives to include
            
        Returns:
            DataFrame with ranking summary
        """
        scores = analysis_results['scores']
        rankings = analysis_results['rankings']
        alternatives_matrix = analysis_results['alternatives_matrix']
        criteria_names = analysis_results.get('criteria_names', [f'Criterion_{i+1}' for i in range(alternatives_matrix.shape[1])])
        
        # Create summary dataframe
        n_alternatives = len(scores)
        top_n = min(top_n, n_alternatives)
        
        # Get indices of top alternatives
        top_indices = np.argsort(-scores)[:top_n]
        
        summary_data = []
        for idx in top_indices:
            row_data = {
                'Alternative': f'Alt_{idx+1}',
                'Rank': int(np.where(np.argsort(-scores) == idx)[0][0] + 1),
                'Score': scores[idx]
            }
            
            # Add criteria values
            for j, crit_name in enumerate(criteria_names):
                row_data[crit_name] = alternatives_matrix[idx, j]
                
            summary_data.append(row_data)
            
        return pd.DataFrame(summary_data)
        
    def compare_methods(self, pymoo_result, objectives_info: List[Dict],
                       ahp_comparisons: Dict[Tuple[str, str], float] = None,
                       topsis_weights: np.ndarray = None) -> Dict:
        """
        Compare AHP and TOPSIS results side by side
        
        Args:
            pymoo_result: PyMOO optimization result
            objectives_info: Objective information
            ahp_comparisons: AHP pairwise comparisons
            topsis_weights: TOPSIS weights
            
        Returns:
            Comparison results
        """
        # Perform both analyses
        ahp_results = self.analyze_with_ahp(pymoo_result, objectives_info, ahp_comparisons)
        topsis_results = self.analyze_with_topsis(pymoo_result, objectives_info, topsis_weights)
        
        # Create comparison summary
        comparison = {
            'ahp_results': ahp_results,
            'topsis_results': topsis_results,
            'ranking_correlation': self._calculate_ranking_correlation(
                ahp_results['rankings'], topsis_results['rankings']
            ),
            'top_10_ahp': self.get_ranking_summary(ahp_results, 10),
            'top_10_topsis': self.get_ranking_summary(topsis_results, 10)
        }
        
        return comparison
        
    def _calculate_ranking_correlation(self, rankings1: np.ndarray, rankings2: np.ndarray) -> float:
        """Calculate Spearman correlation between two ranking arrays"""
        from scipy.stats import spearmanr
        correlation, _ = spearmanr(rankings1, rankings2)
        return correlation


# Example usage and testing functions
def demo_ahp_example():
    """Demonstrate AHP with example data showing PyMOO-style mixed objectives"""
    print("=== AHP Demo with Mixed PyMOO Objectives ===")
    
    # Example alternatives matrix (3 alternatives, 3 criteria)
    # Alternative 1: Cost=$100, Quality=8/10, Time=2hrs
    # Alternative 2: Cost=$80,  Quality=6/10, Time=3hrs  
    # Alternative 3: Cost=$120, Quality=9/10, Time=1hr
    alternatives = np.array([
        [100, 8, 2],   # Alternative 1
        [80,  6, 3],   # Alternative 2  
        [120, 9, 1]    # Alternative 3
    ])
    
    # PyMOO-style objectives info
    objectives_info = [
        {'name': 'Cost', 'direction': 'Minimize'},      # Lower cost is better
        {'name': 'Quality', 'direction': 'Maximize'},   # Higher quality is better
        {'name': 'Time', 'direction': 'Minimize'}       # Lower time is better
    ]
    
    # Example pairwise comparisons
    criteria_comparisons = {
        ('Cost', 'Quality'): 0.5,      # Quality is twice as important as Cost
        ('Cost', 'Time'): 2.0,         # Cost is twice as important as Time
        ('Quality', 'Time'): 3.0       # Quality is 3x more important than Time
    }
    
    ahp = AHPAnalyzer()
    results = ahp.analyze(alternatives, criteria_comparisons, 
                         criteria_names=['Cost', 'Quality', 'Time'],
                         objectives_info=objectives_info)
    
    print(f"Criteria weights: {results['weights']}")
    print(f"Consistency ratio: {results['consistency_ratio']:.4f}")
    print(f"Is consistent: {results['is_consistent']}")
    
    print("\nAlternative Performance:")
    for i, alt in enumerate(alternatives):
        print(f"  Alt {i+1}: Cost=${alt[0]}, Quality={alt[1]}/10, Time={alt[2]}hrs")
    
    print(f"\nAHP Scores (higher = better overall):")
    for i, score in enumerate(results['scores']):
        print(f"  Alt {i+1}: {score:.4f} (Rank: {results['rankings'][i]})")
    
    print(f"\nInterpretation:")
    print(f"- Cost minimization: Lower cost gets higher score")
    print(f"- Quality maximization: Higher quality gets higher score") 
    print(f"- Time minimization: Lower time gets higher score")
    print(f"- Final AHP score reflects overall performance considering all objectives")
    
    
def demo_topsis_example():
    """Demonstrate TOPSIS with example data"""
    print("\n=== TOPSIS Demo ===")
    
    # Same alternatives matrix
    alternatives = np.array([
        [7, 8, 6],   # Alternative 1
        [8, 6, 9],   # Alternative 2
        [6, 9, 7]    # Alternative 3
    ])
    
    # Equal weights
    weights = np.array([0.33, 0.33, 0.34])
    
    # All criteria are benefits (higher is better)
    benefit_criteria = [0, 1, 2]
    cost_criteria = []
    
    topsis = TOPSISAnalyzer()
    results = topsis.analyze(alternatives, weights, benefit_criteria, cost_criteria)
    
    print(f"Weights: {results['weights']}")
    print(f"Alternative scores: {results['scores']}")
    print(f"Rankings: {results['rankings']}")
    print(f"Ideal solution: {results['ideal_solution']}")
    print(f"Anti-ideal solution: {results['anti_ideal_solution']}")


"""
COMPARATIVE ANALYSIS: AHP vs TOPSIS WEIGHTING APPROACHES
========================================================

AHP (Analytic Hierarchy Process) WEIGHTING:
===========================================

Advantages:
- Derives weights from systematic pairwise comparisons
- Provides consistency checking mechanism (CR < 0.10)
- Theoretical foundation in eigenvalue decomposition
- Captures relative importance through ratio scale
- Well-established methodology with extensive validation

Disadvantages:
- Requires numerous pairwise comparisons (n(n-1)/2 for n criteria)
- Susceptible to rank reversal problem
- May be time-consuming for many criteria
- Assumes ratio scale preferences (may not always be realistic)

When to Use AHP Weighting:
- When criteria importance is uncertain and needs systematic derivation
- When decision makers can provide meaningful pairwise comparisons
- When consistency verification is important
- For strategic decisions requiring careful weight justification

TOPSIS WEIGHTING FLEXIBILITY:
============================

Weight Sources for TOPSIS:
1. Equal Weights (w_i = 1/n):
   - Simple, unbiased approach
   - Appropriate when no clear criteria preferences exist
   - Baseline for comparing other weighting schemes

2. AHP-Derived Weights:
   - Combines AHP's systematic weight derivation with TOPSIS ranking
   - Leverages strengths of both methods
   - Provides consistency checking for weights

3. Expert Weights:
   - Direct assignment by domain experts
   - Faster than pairwise comparisons
   - Requires high expertise and experience

4. Objective Weights (e.g., Entropy Method):
   - Data-driven weight determination
   - Based on information content of criteria
   - Reduces subjective bias but may not reflect preferences

INTEGRATION STRATEGY:
====================

Recommended Approach:
1. Use AHP to derive weights when criteria importance is uncertain
2. Apply both AHP and TOPSIS to same problem for validation
3. Compare rankings for consistency check
4. Use TOPSIS with various weighting schemes for sensitivity analysis

Mathematical Relationship:
- AHP provides theoretically sound weight derivation
- TOPSIS provides geometrically intuitive distance-based ranking
- Combined approach leverages strengths of both methodologies

PRACTICAL IMPLEMENTATION GUIDELINES:
===================================

For Decision Support Systems:
1. Offer multiple weighting options (equal, AHP, expert, objective)
2. Provide sensitivity analysis showing impact of weight changes
3. Allow interactive weight adjustment with real-time ranking updates
4. Display consistency measures when using AHP weights
5. Show correlation between different methods for validation

Quality Assurance:
- Always check AHP consistency (CR < 0.10)
- Perform sensitivity analysis on weight variations
- Compare results across different methods
- Validate results with domain experts
- Document weight derivation methodology

References for Further Reading:
==============================

Foundational Papers:
- Saaty, T. L. (1980). The Analytic Hierarchy Process: Planning, Priority Setting, Resource Allocation. McGraw-Hill.
- Hwang, C. L., & Yoon, K. (1981). Multiple Attribute Decision Making: Methods and Applications. Springer-Verlag.

Comparative Studies:
- Triantaphyllou, E. (2000). Multi-criteria decision making methods: A comparative study. Applied Optimization, 44.
- Behzadian, M., et al. (2012). A state-of the-art survey of TOPSIS applications. Expert Systems with Applications, 39(17), 13051-13069.

Weight Determination Methods:
- Roszkowska, E. (2013). Rank ordering criteria weighting methods – a comparative overview. Optimum Studia Ekonomiczne, 5(65), 14-33.
- Odu, G. O. (2019). Weighting methods for multi-criteria decision making technique. Journal of Applied Sciences and Environmental Management, 23(8), 1449-1457.

"""


if __name__ == "__main__":
    # Run demos
    demo_ahp_example()
    demo_topsis_example()
