# Group AHP and TOPSIS Technical Documentation

## Overview

This document provides a comprehensive technical explanation of how Group Analytic Hierarchy Process (AHP) and Group TOPSIS methods are implemented in the PyMOO GUI system. It covers the mathematical foundations, aggregation techniques, computational algorithms, and implementation details.

---

## 📐 Mathematical Foundations

### Individual AHP Process

#### 1. Pairwise Comparison Matrix
For n criteria, each user creates an n×n pairwise comparison matrix A where:

```
A = [a_ij] where a_ij represents the relative importance of criterion i over criterion j

Properties:
- a_ii = 1 (diagonal elements)
- a_ji = 1/a_ij (reciprocal property)
- a_ij > 0 for all i,j
```

#### 2. Saaty's 9-Point Scale
```
Scale | Meaning
------|--------
1     | Equal importance
3     | Moderate importance of one over another
5     | Strong importance of one over another
7     | Very strong importance of one over another
9     | Extreme importance of one over another
2,4,6,8 | Intermediate values
```

#### 3. Priority Vector Calculation
From matrix A, compute the priority vector w using the eigenvalue method:

```
A * w = λ_max * w

Where:
- w = priority vector (weights)
- λ_max = largest eigenvalue
- Consistency Index (CI) = (λ_max - n)/(n-1)
- Consistency Ratio (CR) = CI/RI (Random Index)
```

### Individual TOPSIS Process

#### 1. Weight Vector Assignment
Each user assigns weights w = [w_1, w_2, ..., w_n] where:

```
w_i ≥ 0 for all i
Σw_i = 1 (normalized)
```

#### 2. TOPSIS Algorithm Steps
```
Step 1: Normalize decision matrix
Step 2: Calculate weighted normalized matrix
Step 3: Determine ideal and anti-ideal solutions
Step 4: Calculate separation measures
Step 5: Compute relative closeness to ideal solution
```

---

## 🔄 Group Aggregation Methods

### Group AHP Aggregation

#### Method 1: Aggregation of Individual Judgments (AIJ)
**Used in our implementation**

```python
def aggregate_ahp_matrices(matrices: Dict[str, np.ndarray]) -> np.ndarray:
    """
    Aggregate multiple AHP matrices using geometric mean
    
    Mathematical Formula:
    group_matrix[i,j] = (∏(k=1 to m) user_matrix_k[i,j])^(1/m)
    
    Where:
    - m = number of users
    - user_matrix_k = pairwise comparison matrix from user k
    """
    
    if not matrices:
        raise ValueError("No matrices to aggregate")
    
    # Get matrix dimensions
    users = list(matrices.keys())
    n = matrices[users[0]].shape[0]
    
    # Initialize group matrix
    group_matrix = np.ones((n, n))
    
    # Apply geometric mean aggregation
    for i in range(n):
        for j in range(n):
            if i != j:
                # Collect all user judgments for this pair
                values = [matrices[user][i, j] for user in users]
                
                # Geometric mean calculation
                product = np.prod(values)
                group_matrix[i, j] = product ** (1.0 / len(values))
                
                # Maintain reciprocal property
                group_matrix[j, i] = 1.0 / group_matrix[i, j]
    
    return group_matrix
```

#### Method 2: Aggregation of Individual Priorities (AIP)
**Alternative method (not currently implemented)**

```python
def aggregate_ahp_priorities(priority_vectors: Dict[str, np.ndarray]) -> np.ndarray:
    """
    Aggregate individual priority vectors using arithmetic mean
    
    Mathematical Formula:
    group_priority[i] = (1/m) * Σ(k=1 to m) user_priority_k[i]
    """
    
    if not priority_vectors:
        raise ValueError("No priority vectors to aggregate")
    
    # Stack all priority vectors
    vectors = np.array(list(priority_vectors.values()))
    
    # Arithmetic mean aggregation
    group_priority = np.mean(vectors, axis=0)
    
    # Ensure normalization
    group_priority = group_priority / np.sum(group_priority)
    
    return group_priority
```

### Group TOPSIS Aggregation

#### Weight Vector Aggregation

```python
def aggregate_topsis_weights(weight_vectors: Dict[str, List[float]]) -> np.ndarray:
    """
    Aggregate multiple TOPSIS weight vectors using arithmetic mean
    
    Mathematical Formula:
    group_weight[i] = (1/m) * Σ(k=1 to m) user_weight_k[i]
    
    Where:
    - m = number of users
    - user_weight_k = weight vector from user k
    """
    
    if not weight_vectors:
        raise ValueError("No weight vectors to aggregate")
    
    # Convert to numpy arrays
    weights_array = np.array(list(weight_vectors.values()))
    
    # Arithmetic mean aggregation
    group_weights = np.mean(weights_array, axis=0)
    
    # Normalize to ensure sum = 1
    group_weights = group_weights / np.sum(group_weights)
    
    return group_weights
```

---

## 🔬 Detailed Algorithm Implementation

### Complete Group AHP Process

```python
class GroupAHPAnalyzer:
    """
    Complete Group AHP implementation with consistency checking
    """
    
    def __init__(self, matrices: Dict[str, np.ndarray]):
        self.user_matrices = matrices
        self.group_matrix = None
        self.group_priorities = None
        self.consistency_results = {}
    
    def analyze(self) -> Dict:
        """
        Perform complete group AHP analysis
        """
        # Step 1: Check individual consistency
        self._check_individual_consistency()
        
        # Step 2: Aggregate matrices
        self.group_matrix = self._aggregate_matrices()
        
        # Step 3: Calculate group priorities
        self.group_priorities = self._calculate_priorities(self.group_matrix)
        
        # Step 4: Check group consistency
        group_cr = self._calculate_consistency_ratio(self.group_matrix)
        
        # Step 5: Apply to alternatives (if available)
        alternative_scores = self._score_alternatives()
        
        return {
            'group_matrix': self.group_matrix,
            'group_priorities': self.group_priorities,
            'group_consistency_ratio': group_cr,
            'individual_consistency': self.consistency_results,
            'alternative_scores': alternative_scores,
            'ranking': self._rank_alternatives(alternative_scores)
        }
    
    def _check_individual_consistency(self):
        """Check consistency of each user's matrix"""
        for user, matrix in self.user_matrices.items():
            cr = self._calculate_consistency_ratio(matrix)
            self.consistency_results[user] = {
                'consistency_ratio': cr,
                'is_consistent': cr < 0.1  # Saaty's threshold
            }
    
    def _calculate_priorities(self, matrix: np.ndarray) -> np.ndarray:
        """Calculate priority vector using eigenvalue method"""
        # Find largest eigenvalue and corresponding eigenvector
        eigenvalues, eigenvectors = np.linalg.eig(matrix)
        
        # Get index of largest eigenvalue
        max_index = np.argmax(eigenvalues.real)
        
        # Extract corresponding eigenvector
        priority_vector = eigenvectors[:, max_index].real
        
        # Normalize to positive values
        priority_vector = np.abs(priority_vector)
        priority_vector = priority_vector / np.sum(priority_vector)
        
        return priority_vector
    
    def _calculate_consistency_ratio(self, matrix: np.ndarray) -> float:
        """Calculate consistency ratio for AHP matrix"""
        n = matrix.shape[0]
        
        if n <= 2:
            return 0.0  # Always consistent for n <= 2
        
        # Random Index values (Saaty)
        random_index = {
            3: 0.52, 4: 0.89, 5: 1.11, 6: 1.25, 7: 1.35,
            8: 1.40, 9: 1.45, 10: 1.49, 11: 1.52, 12: 1.54
        }
        
        # Calculate largest eigenvalue
        eigenvalues = np.linalg.eigvals(matrix)
        lambda_max = np.max(eigenvalues.real)
        
        # Consistency Index
        ci = (lambda_max - n) / (n - 1)
        
        # Consistency Ratio
        ri = random_index.get(n, 1.54)  # Use 1.54 for n > 12
        cr = ci / ri if ri > 0 else 0
        
        return cr
    
    def _aggregate_matrices(self) -> np.ndarray:
        """Aggregate individual matrices using geometric mean"""
        return aggregate_ahp_matrices(self.user_matrices)
    
    def _score_alternatives(self) -> np.ndarray:
        """Score alternatives using group priorities"""
        # This would integrate with the optimization results
        # For now, return placeholder
        return np.array([])
    
    def _rank_alternatives(self, scores: np.ndarray) -> List[int]:
        """Rank alternatives by scores (descending order)"""
        if len(scores) == 0:
            return []
        return np.argsort(-scores).tolist()
```

### Complete Group TOPSIS Process

```python
class GroupTOPSISAnalyzer:
    """
    Complete Group TOPSIS implementation
    """
    
    def __init__(self, weight_vectors: Dict[str, List[float]], 
                 alternatives_data: List[Dict]):
        self.user_weights = weight_vectors
        self.alternatives = alternatives_data
        self.group_weights = None
        self.decision_matrix = None
    
    def analyze(self) -> Dict:
        """
        Perform complete group TOPSIS analysis
        """
        # Step 1: Aggregate weight vectors
        self.group_weights = self._aggregate_weights()
        
        # Step 2: Build decision matrix from alternatives
        self.decision_matrix = self._build_decision_matrix()
        
        # Step 3: Normalize decision matrix
        normalized_matrix = self._normalize_matrix(self.decision_matrix)
        
        # Step 4: Calculate weighted normalized matrix
        weighted_matrix = self._apply_weights(normalized_matrix)
        
        # Step 5: Determine ideal and anti-ideal solutions
        ideal_solution, anti_ideal_solution = self._find_ideal_solutions(weighted_matrix)
        
        # Step 6: Calculate separation measures
        separation_positive, separation_negative = self._calculate_separations(
            weighted_matrix, ideal_solution, anti_ideal_solution
        )
        
        # Step 7: Calculate relative closeness
        relative_closeness = self._calculate_relative_closeness(
            separation_positive, separation_negative
        )
        
        # Step 8: Rank alternatives
        ranking = self._rank_alternatives(relative_closeness)
        
        return {
            'group_weights': self.group_weights,
            'decision_matrix': self.decision_matrix,
            'normalized_matrix': normalized_matrix,
            'weighted_matrix': weighted_matrix,
            'ideal_solution': ideal_solution,
            'anti_ideal_solution': anti_ideal_solution,
            'relative_closeness': relative_closeness,
            'ranking': ranking,
            'scores': relative_closeness
        }
    
    def _aggregate_weights(self) -> np.ndarray:
        """Aggregate user weights using arithmetic mean"""
        return aggregate_topsis_weights(self.user_weights)
    
    def _build_decision_matrix(self) -> np.ndarray:
        """Build decision matrix from alternatives data"""
        if not self.alternatives:
            return np.array([])
        
        # Extract values from alternatives
        matrix_data = []
        for alt in self.alternatives:
            values = alt.get('values', [])
            matrix_data.append(values)
        
        return np.array(matrix_data)
    
    def _normalize_matrix(self, matrix: np.ndarray) -> np.ndarray:
        """Normalize decision matrix using vector normalization"""
        if matrix.size == 0:
            return matrix
        
        normalized = np.zeros_like(matrix)
        
        for j in range(matrix.shape[1]):
            column_norm = np.sqrt(np.sum(matrix[:, j] ** 2))
            if column_norm > 0:
                normalized[:, j] = matrix[:, j] / column_norm
        
        return normalized
    
    def _apply_weights(self, normalized_matrix: np.ndarray) -> np.ndarray:
        """Apply group weights to normalized matrix"""
        if normalized_matrix.size == 0:
            return normalized_matrix
        
        return normalized_matrix * self.group_weights
    
    def _find_ideal_solutions(self, weighted_matrix: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Find ideal and anti-ideal solutions"""
        if weighted_matrix.size == 0:
            return np.array([]), np.array([])
        
        # For this implementation, assume all criteria are "larger is better"
        # In practice, this should be configurable per criterion
        ideal_solution = np.max(weighted_matrix, axis=0)
        anti_ideal_solution = np.min(weighted_matrix, axis=0)
        
        return ideal_solution, anti_ideal_solution
    
    def _calculate_separations(self, weighted_matrix: np.ndarray,
                             ideal: np.ndarray, anti_ideal: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Calculate separation measures from ideal and anti-ideal solutions"""
        if weighted_matrix.size == 0:
            return np.array([]), np.array([])
        
        # Euclidean distance to ideal solution
        separation_positive = np.sqrt(np.sum((weighted_matrix - ideal) ** 2, axis=1))
        
        # Euclidean distance to anti-ideal solution
        separation_negative = np.sqrt(np.sum((weighted_matrix - anti_ideal) ** 2, axis=1))
        
        return separation_positive, separation_negative
    
    def _calculate_relative_closeness(self, sep_pos: np.ndarray, 
                                    sep_neg: np.ndarray) -> np.ndarray:
        """Calculate relative closeness to ideal solution"""
        if len(sep_pos) == 0:
            return np.array([])
        
        # Avoid division by zero
        denominator = sep_pos + sep_neg
        denominator[denominator == 0] = 1e-10
        
        relative_closeness = sep_neg / denominator
        
        return relative_closeness
    
    def _rank_alternatives(self, closeness: np.ndarray) -> List[int]:
        """Rank alternatives by relative closeness (descending order)"""
        if len(closeness) == 0:
            return []
        
        return np.argsort(-closeness).tolist()
```

---

## 🎯 Implementation Integration

### Database Integration

```python
class GroupDecisionManager:
    """
    Manages group decision analysis with database integration
    """
    
    def __init__(self, db_manager: UserDatabaseManager):
        self.db_manager = db_manager
    
    def run_group_ahp_analysis(self, session_id: int) -> Dict:
        """
        Execute complete group AHP analysis for a session
        """
        try:
            # 1. Retrieve user matrices from database
            user_matrices = self.db_manager.get_session_ahp_comparisons(session_id)
            
            if len(user_matrices) < 2:
                raise ValueError("Need at least 2 user submissions for group analysis")
            
            # 2. Convert to numpy arrays
            matrices_np = {}
            for user, matrix_json in user_matrices.items():
                matrices_np[user] = np.array(matrix_json)
            
            # 3. Perform group AHP analysis
            analyzer = GroupAHPAnalyzer(matrices_np)
            results = analyzer.analyze()
            
            # 4. Save results to database
            self._save_group_results(session_id, 'ahp', results)
            
            return results
            
        except Exception as e:
            raise Exception(f"Group AHP analysis failed: {str(e)}")
    
    def run_group_topsis_analysis(self, session_id: int) -> Dict:
        """
        Execute complete group TOPSIS analysis for a session
        """
        try:
            # 1. Retrieve user weights from database
            user_weights = self.db_manager.get_session_topsis_weights(session_id)
            
            if len(user_weights) < 2:
                raise ValueError("Need at least 2 user submissions for group analysis")
            
            # 2. Get alternatives data
            _, alternatives_data = self.db_manager.get_session_optimization_results(session_id)
            
            # 3. Perform group TOPSIS analysis
            analyzer = GroupTOPSISAnalyzer(user_weights, alternatives_data)
            results = analyzer.analyze()
            
            # 4. Save results to database
            self._save_group_results(session_id, 'topsis', results)
            
            return results
            
        except Exception as e:
            raise Exception(f"Group TOPSIS analysis failed: {str(e)}")
    
    def _save_group_results(self, session_id: int, method: str, results: Dict):
        """Save group analysis results to database"""
        # Convert numpy arrays to lists for JSON serialization
        serializable_results = self._make_json_serializable(results)
        
        # Save to group_results table
        with sqlite3.connect(self.db_manager.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO group_results 
                (session_id, method, aggregated_data, final_scores, final_rankings, computed_by)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                session_id,
                method,
                json.dumps(serializable_results),
                json.dumps(results.get('scores', [])),
                json.dumps(results.get('ranking', [])),
                1  # Admin user ID - should be dynamic
            ))
            conn.commit()
    
    def _make_json_serializable(self, obj):
        """Convert numpy arrays and other non-serializable objects to JSON-compatible format"""
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, dict):
            return {key: self._make_json_serializable(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._make_json_serializable(item) for item in obj]
        elif isinstance(obj, (np.int64, np.int32)):
            return int(obj)
        elif isinstance(obj, (np.float64, np.float32)):
            return float(obj)
        else:
            return obj
```

---

## 📊 Consistency and Validation

### AHP Consistency Checking

```python
def validate_ahp_consistency(matrix: np.ndarray, threshold: float = 0.1) -> Dict:
    """
    Comprehensive AHP consistency validation
    
    Returns:
    - consistency_ratio: CR value
    - is_consistent: Boolean (CR < threshold)
    - lambda_max: Largest eigenvalue
    - consistency_index: CI value
    """
    
    n = matrix.shape[0]
    
    # Calculate eigenvalues
    eigenvalues = np.linalg.eigvals(matrix)
    lambda_max = np.max(eigenvalues.real)
    
    # Consistency Index
    ci = (lambda_max - n) / (n - 1) if n > 1 else 0
    
    # Random Index (Saaty's values)
    random_indices = {
        1: 0, 2: 0, 3: 0.52, 4: 0.89, 5: 1.11, 6: 1.25,
        7: 1.35, 8: 1.40, 9: 1.45, 10: 1.49
    }
    
    ri = random_indices.get(n, 1.54)
    cr = ci / ri if ri > 0 else 0
    
    return {
        'consistency_ratio': cr,
        'is_consistent': cr < threshold,
        'lambda_max': lambda_max,
        'consistency_index': ci,
        'random_index': ri,
        'matrix_size': n
    }
```

### TOPSIS Weight Validation

```python
def validate_topsis_weights(weights: np.ndarray) -> Dict:
    """
    Validate TOPSIS weight vector
    
    Checks:
    - Non-negative weights
    - Proper normalization
    - Non-zero sum
    """
    
    validation = {
        'is_valid': True,
        'errors': [],
        'warnings': []
    }
    
    # Check non-negative
    if np.any(weights < 0):
        validation['is_valid'] = False
        validation['errors'].append("Weights must be non-negative")
    
    # Check non-zero sum
    weight_sum = np.sum(weights)
    if weight_sum == 0:
        validation['is_valid'] = False
        validation['errors'].append("Weight sum cannot be zero")
    
    # Check normalization (with tolerance)
    if abs(weight_sum - 1.0) > 1e-10:
        validation['warnings'].append(f"Weights not normalized (sum = {weight_sum:.6f})")
    
    # Check for zero weights
    zero_count = np.sum(weights == 0)
    if zero_count > 0:
        validation['warnings'].append(f"{zero_count} criteria have zero weight")
    
    return validation
```

---

## ⚡ Performance Optimization

### Large Group Handling

```python
class OptimizedGroupAnalysis:
    """
    Performance-optimized group analysis for large groups
    """
    
    @staticmethod
    def batch_process_matrices(matrices: Dict, batch_size: int = 10) -> np.ndarray:
        """Process large number of matrices in batches"""
        users = list(matrices.keys())
        n_users = len(users)
        
        if n_users <= batch_size:
            return aggregate_ahp_matrices(matrices)
        
        # Process in batches
        batch_results = []
        for i in range(0, n_users, batch_size):
            batch_users = users[i:i + batch_size]
            batch_matrices = {user: matrices[user] for user in batch_users}
            batch_result = aggregate_ahp_matrices(batch_matrices)
            batch_results.append(batch_result)
        
        # Aggregate batch results
        final_matrices = {f"batch_{i}": matrix for i, matrix in enumerate(batch_results)}
        return aggregate_ahp_matrices(final_matrices)
    
    @staticmethod
    def parallel_consistency_check(matrices: Dict) -> Dict:
        """Check consistency of multiple matrices in parallel"""
        from concurrent.futures import ThreadPoolExecutor
        
        def check_single_consistency(user_matrix_pair):
            user, matrix = user_matrix_pair
            return user, validate_ahp_consistency(matrix)
        
        with ThreadPoolExecutor() as executor:
            results = executor.map(check_single_consistency, matrices.items())
        
        return dict(results)
```

---

## 🔍 Advanced Features

### Sensitivity Analysis

```python
def ahp_sensitivity_analysis(group_matrix: np.ndarray, 
                           perturbation_range: float = 0.1) -> Dict:
    """
    Perform sensitivity analysis on group AHP results
    
    Tests how robust the rankings are to small changes in judgments
    """
    
    base_priorities = calculate_priorities(group_matrix)
    n = len(base_priorities)
    
    sensitivity_results = {
        'base_priorities': base_priorities,
        'perturbation_results': [],
        'ranking_stability': {}
    }
    
    # Test perturbations
    for i in range(n):
        for j in range(i + 1, n):
            # Perturb matrix element
            perturbed_matrix = group_matrix.copy()
            original_value = perturbed_matrix[i, j]
            
            # Test positive and negative perturbations
            for direction in [-1, 1]:
                perturbation = direction * perturbation_range * original_value
                perturbed_matrix[i, j] = original_value + perturbation
                perturbed_matrix[j, i] = 1.0 / perturbed_matrix[i, j]
                
                # Calculate new priorities
                new_priorities = calculate_priorities(perturbed_matrix)
                
                # Store result
                sensitivity_results['perturbation_results'].append({
                    'element': (i, j),
                    'direction': direction,
                    'perturbation': perturbation,
                    'new_priorities': new_priorities,
                    'priority_change': new_priorities - base_priorities
                })
    
    return sensitivity_results
```

### Fuzzy Extensions

```python
def fuzzy_ahp_aggregation(fuzzy_matrices: Dict) -> Dict:
    """
    Aggregate fuzzy AHP matrices using triangular fuzzy numbers
    
    Each matrix element is a triangular fuzzy number (l, m, u)
    where l ≤ m ≤ u
    """
    
    # This would implement fuzzy arithmetic for AHP
    # Placeholder for future enhancement
    pass

def interval_topsis(interval_weights: Dict) -> Dict:
    """
    TOPSIS with interval weights for handling uncertainty
    
    Each weight is an interval [w_min, w_max]
    """
    
    # This would implement interval TOPSIS
    # Placeholder for future enhancement
    pass
```

---

## 📋 Summary

### Key Algorithms Implemented

1. **Group AHP**: Geometric mean aggregation of pairwise comparison matrices
2. **Group TOPSIS**: Arithmetic mean aggregation of weight vectors
3. **Consistency Checking**: Saaty's consistency ratio with random index
4. **Alternative Ranking**: Eigenvalue method for AHP, relative closeness for TOPSIS

### Computational Complexity

- **AHP Aggregation**: O(n² × m) where n = criteria, m = users
- **TOPSIS Aggregation**: O(n × m × a) where a = alternatives
- **Eigenvalue Calculation**: O(n³) for priority vector computation
- **Consistency Check**: O(n³) for eigenvalue computation

### Quality Assurance

- Input validation for all user data
- Consistency checking with configurable thresholds
- Error handling for edge cases (zero matrices, single user, etc.)
- JSON serialization for database storage

### Future Enhancements

- Fuzzy AHP and TOPSIS implementations
- Advanced aggregation methods (ordered weighted averaging)
- Real-time sensitivity analysis
- Parallel processing for large groups
- Integration with optimization uncertainty analysis

---

**Author:** Elias Rizos [it21490]  
**Version:** 2.0.0  
**Last Updated:** September 19, 2025

*This technical documentation provides the mathematical and computational foundation for group decision-making methods in the PyMOO GUI system.*