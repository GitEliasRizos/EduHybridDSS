"""
ELI5: Multi-Criteria Decision Analysis (MCDA) - Like a Smart Decision Helper! 🤔

Think of this like having a really smart friend who helps you make tough decisions
when you have lots of good options and can't pick just one.

Imagine you're trying to choose the best apartment to rent. You have 10 apartments
and you care about: price, location, size, and safety. But some are cheap but far,
others are expensive but perfect location. How do you choose?

This is exactly what MCDA does for optimization results! After the optimizer
finds many good solutions, MCDA helps you pick THE BEST ONE based on what
you care about most.

Two Smart Decision Methods:

🏆 AHP (Analytic Hierarchy Process):
   Like asking "How much more important is X than Y?"
   - You compare things pair by pair: "Is price 3x more important than size?"
   - The computer figures out the perfect weights for everything
   - Then ranks all solutions based on your preferences

🎯 TOPSIS (Technique for Order Preference):
   Like finding what's closest to your "perfect world" solution
   - Imagines the absolute best possible solution (ideal)
   - Imagines the absolute worst possible solution (anti-ideal)
   - Picks solutions closest to perfect and far from terrible

It's like having a wise advisor who listens to what you want and points
to the best choice: "Based on what you told me matters most, THIS is your answer!"

Author: Elias Rizos [it21490]
Version: 1.0.0
"""

# ELI5: Import our decision-making tools
import numpy as np  # Advanced math for calculations (like a smart calculator)
import pandas as pd  # Data tables for organizing results (like a smart spreadsheet)
from typing import List, Dict, Tuple, Optional, Union  # Type labels
import math  # Basic math functions


class AHPAnalyzer:
    """
    ELI5: AHP Analyzer - Like a Wise Judge Comparing Things! ⚖️
    
    This is like having a judge who's really good at comparing different things.
    
    Imagine you're a judge in a cooking contest with 3 categories:
    - Taste (how delicious?)
    - Presentation (how pretty?)  
    - Creativity (how original?)
    
    But taste is 5x more important to you than looks, and creativity is 2x more
    important than looks. AHP helps you:
    1. Compare everything pair by pair
    2. Calculate the perfect importance weights
    3. Score each dish fairly
    4. Crown the winner!
    
    It's math magic that turns your preferences into fair, consistent rankings!
    """
    
    def __init__(self):
        """ELI5: Set up our wise judge (initialize the AHP analyzer)"""
        self.criteria_weights = None
        self.consistency_ratio = None
        self.pairwise_matrix = None
        
    def create_pairwise_matrix(self, criteria_comparisons: Dict[Tuple[str, str], float]) -> np.ndarray:
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
                                 
        Returns:
            Pairwise comparison matrix
        """
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
        
        Args:
            matrix: Pairwise comparison matrix
            
        Returns:
            Priority weights vector
        """
        # Calculate eigenvalues and eigenvectors
        eigenvalues, eigenvectors = np.linalg.eig(matrix)
        
        # Find the largest eigenvalue and corresponding eigenvector
        max_eigenvalue_idx = np.argmax(eigenvalues.real)
        max_eigenvalue = eigenvalues[max_eigenvalue_idx].real
        principal_eigenvector = eigenvectors[:, max_eigenvalue_idx].real
        
        # Normalize the eigenvector to get weights
        weights = principal_eigenvector / np.sum(principal_eigenvector)
        
        # Ensure positive weights
        weights = np.abs(weights)
        weights = weights / np.sum(weights)
        
        self.criteria_weights = weights
        self.max_eigenvalue = max_eigenvalue
        
        return weights
        
    def calculate_consistency_ratio(self, matrix: np.ndarray, weights: np.ndarray) -> float:
        """
        Calculate Consistency Ratio (CR) to check matrix consistency
        
        Args:
            matrix: Pairwise comparison matrix
            weights: Priority weights
            
        Returns:
            Consistency ratio (should be < 0.1 for acceptable consistency)
        """
        n = matrix.shape[0]
        
        # Calculate Consistency Index (CI)
        lambda_max = self.max_eigenvalue
        ci = (lambda_max - n) / (n - 1)
        
        # Random Index (RI) values for different matrix sizes
        ri_values = {1: 0, 2: 0, 3: 0.58, 4: 0.90, 5: 1.12, 6: 1.24, 7: 1.32, 8: 1.41, 9: 1.45, 10: 1.49}
        ri = ri_values.get(n, 1.49)
        
        # Consistency Ratio
        cr = ci / ri if ri > 0 else 0
        
        self.consistency_ratio = cr
        return cr
        
    def score_alternatives(self, alternatives: np.ndarray, weights: np.ndarray) -> np.ndarray:
        """
        Score alternatives using calculated weights
        
        Args:
            alternatives: Matrix of alternatives (rows) vs criteria (columns)
            weights: Criteria weights from AHP
            
        Returns:
            AHP scores for each alternative
        """
        # Normalize alternatives matrix (higher is better for all criteria)
        normalized = alternatives.copy()
        for j in range(alternatives.shape[1]):
            col_max = np.max(alternatives[:, j])
            col_min = np.min(alternatives[:, j])
            if col_max != col_min:
                normalized[:, j] = (alternatives[:, j] - col_min) / (col_max - col_min)
            else:
                normalized[:, j] = 1.0
        
        # Calculate weighted scores
        scores = np.dot(normalized, weights)
        return scores
        
    def analyze(self, alternatives: np.ndarray, criteria_comparisons: Dict[Tuple[str, str], float]) -> Dict:
        """
        Complete AHP analysis
        
        Args:
            alternatives: Matrix of alternatives vs criteria
            criteria_comparisons: Pairwise comparison preferences
            
        Returns:
            Analysis results dictionary
        """
        # Create pairwise matrix
        matrix = self.create_pairwise_matrix(criteria_comparisons)
        
        # Calculate weights
        weights = self.calculate_weights(matrix)
        
        # Check consistency
        cr = self.calculate_consistency_ratio(matrix, weights)
        
        # Score alternatives
        scores = self.score_alternatives(alternatives, weights)
        
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
        
        Args:
            normalized_matrix: Normalized decision matrix
            weights: Criteria weights
            
        Returns:
            Weighted normalized matrix
        """
        return normalized_matrix * weights
        
    def identify_ideal_solutions(self, weighted_matrix: np.ndarray, 
                               benefit_criteria: List[int], 
                               cost_criteria: List[int]) -> Tuple[np.ndarray, np.ndarray]:
        """
        Identify ideal and anti-ideal solutions
        
        Args:
            weighted_matrix: Weighted normalized matrix
            benefit_criteria: Indices of benefit criteria (higher is better)
            cost_criteria: Indices of cost criteria (lower is better)
            
        Returns:
            Tuple of (ideal_solution, anti_ideal_solution)
        """
        ideal = np.zeros(weighted_matrix.shape[1])
        anti_ideal = np.zeros(weighted_matrix.shape[1])
        
        # For benefit criteria: ideal = max, anti-ideal = min
        for j in benefit_criteria:
            ideal[j] = np.max(weighted_matrix[:, j])
            anti_ideal[j] = np.min(weighted_matrix[:, j])
            
        # For cost criteria: ideal = min, anti-ideal = max
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
        
        Args:
            d_plus: Distances to ideal solution
            d_minus: Distances to anti-ideal solution
            
        Returns:
            Closeness coefficients (0-1, higher is better)
        """
        # Avoid division by zero
        denominator = d_plus + d_minus
        denominator[denominator == 0] = 1e-10
        
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
            objectives_info: Objective information
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
            
        # Perform AHP analysis
        results = self.ahp.analyze(alternatives, criteria_comparisons)
        
        # Add additional information
        results['alternatives_count'] = alternatives.shape[0]
        results['criteria_count'] = alternatives.shape[1]
        results['alternatives_matrix'] = alternatives
        
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
    """Demonstrate AHP with example data"""
    print("=== AHP Demo ===")
    
    # Example alternatives matrix (3 alternatives, 3 criteria)
    alternatives = np.array([
        [7, 8, 6],   # Alternative 1
        [8, 6, 9],   # Alternative 2  
        [6, 9, 7]    # Alternative 3
    ])
    
    # Example pairwise comparisons (price vs performance vs reliability)
    criteria_comparisons = {
        ('price', 'performance'): 0.5,      # Performance is twice as important as price
        ('price', 'reliability'): 0.33,     # Reliability is 3x more important than price
        ('performance', 'reliability'): 0.5 # Reliability is twice as important as performance
    }
    
    ahp = AHPAnalyzer()
    results = ahp.analyze(alternatives, criteria_comparisons)
    
    print(f"Criteria weights: {results['weights']}")
    print(f"Consistency ratio: {results['consistency_ratio']:.4f}")
    print(f"Is consistent: {results['is_consistent']}")
    print(f"Alternative scores: {results['scores']}")
    print(f"Rankings: {results['rankings']}")
    
    
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


if __name__ == "__main__":
    # Run demos
    demo_ahp_example()
    demo_topsis_example()
