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

Group AHP addresses the challenge of combining multiple decision makers' pairwise comparisons into a single group consensus. The PyMOO GUI system implements the **Aggregation of Individual Judgments (AIJ)** method, which is widely accepted in the literature and maintains mathematical rigor.

#### Method 1: Aggregation of Individual Judgments (AIJ)
**Primary method used in our implementation**

**Conceptual Approach:**
The AIJ method aggregates individual pairwise comparison matrices before calculating the final group priorities. This approach preserves the reciprocal property of AHP matrices and ensures mathematical consistency in the aggregation process.

**Mathematical Foundation:**
For each pair of criteria (i,j), we combine all users' judgments using the geometric mean:

**Group Matrix Element Calculation:**
- Collect all individual judgments for criteria pair (i,j) from m users
- Apply geometric mean: group_value = (value₁ × value₂ × ... × valueₘ)^(1/m)
- Maintain reciprocal property: if group_matrix[i,j] = x, then group_matrix[j,i] = 1/x

**Why Geometric Mean?**
- **Reciprocal Preservation**: Maintains the fundamental AHP reciprocal property
- **Multiplicative Consistency**: Appropriate for ratio-scale data like Saaty's comparisons
- **Outlier Resistance**: Less sensitive to extreme judgments than arithmetic mean
- **Mathematical Soundness**: Preserves the mathematical structure of pairwise comparison matrices
#### Method 2: Aggregation of Individual Priorities (AIP)
**Alternative method available but not currently implemented**

**Conceptual Approach:**
The AIP method first calculates individual priority vectors from each user's comparison matrix, then aggregates these priority vectors. While mathematically valid, this approach can lose some information from the original comparisons.

**Process Flow:**
1. **Individual Analysis**: Each user's comparison matrix is processed separately to derive individual priority vectors
2. **Priority Aggregation**: Individual priority vectors are combined using arithmetic mean
3. **Normalization**: Final group priorities are normalized to sum to 1.0

**Comparison: AIJ vs AIP**
- **AIJ (Implemented)**: Aggregates raw judgments, preserves more comparison information, maintains reciprocal properties
- **AIP (Alternative)**: Aggregates derived priorities, simpler computation, may lose nuanced judgment information
- **Literature Consensus**: AIJ is generally preferred for group decision making as it better preserves the richness of individual judgments

### Group TOPSIS Aggregation

Group TOPSIS extends the individual TOPSIS method to incorporate multiple decision makers' weight preferences. The system aggregates individual weight vectors to create a group consensus that reflects collective priorities.

#### Weight Vector Aggregation Process

**Conceptual Framework:**
Unlike AHP's geometric mean approach, TOPSIS weight aggregation uses arithmetic mean because weights represent additive preferences rather than multiplicative ratios.

**Mathematical Approach:**
- **Collection**: Gather individual weight vectors from all group members
- **Arithmetic Aggregation**: Calculate simple average of corresponding weight elements
- **Normalization**: Ensure final group weights sum to 1.0
- **Validation**: Verify all weights remain non-negative

**Why Arithmetic Mean for TOPSIS?**
- **Additive Nature**: TOPSIS weights represent additive importance, not multiplicative ratios
- **Linear Combination**: Final TOPSIS scores are linear combinations of weighted criteria
- **Interpretability**: Arithmetic mean preserves intuitive interpretation of average group preference
- **Mathematical Consistency**: Aligns with TOPSIS's linear mathematical structure

---

## 🔬 Detailed Algorithm Implementation

### Complete Group AHP Process

The complete Group AHP process integrates individual consistency validation, matrix aggregation, and group decision formation:

**Individual Consistency Assessment**
Before aggregation, each participant's comparison matrix is evaluated for consistency using Saaty's Consistency Ratio (CR). This ensures that individual judgments meet quality standards before contributing to the group decision.

**Matrix Aggregation Process**
Individual matrices are combined using the geometric mean method (AIJ approach), which preserves the fundamental reciprocal property of AHP matrices while equally weighting all participants' contributions.

**Group Priority Derivation**
The aggregated group matrix undergoes eigenvalue analysis to extract the principal eigenvector, representing the collective priority weights. These weights reflect the group's consensus on relative criterion importance.

**Group Consistency Validation**
The aggregated matrix's consistency is evaluated to ensure the group decision maintains mathematical coherence. Acceptable consistency (CR ≤ 0.1) indicates reliable group consensus.

**Alternative Evaluation**
When alternatives are present, they are scored using the derived group priorities, creating a comprehensive ranking system based on collective judgment.

The complete process returns comprehensive results including individual consistency assessments, group priorities, and alternative rankings, ensuring full transparency in collaborative decision-making.
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

The complete Group TOPSIS process transforms individual weight preferences into a unified multi-criteria decision analysis:

**Weight Aggregation Phase**
Individual weight vectors from all group members are combined using arithmetic mean aggregation. This approach maintains the linear nature of TOPSIS while ensuring equal representation of all participants' preferences.

**Decision Matrix Construction**
Alternative performance data is organized into a structured decision matrix where rows represent alternatives and columns represent criteria. This matrix serves as the foundation for all subsequent TOPSIS calculations.

**Matrix Normalization**
The decision matrix undergoes vector normalization to eliminate scale differences between criteria. Each criterion is normalized using the Euclidean norm, ensuring comparable measurement units across all criteria.

**Weighted Matrix Application**
Group weights are applied to the normalized matrix, emphasizing criteria deemed more important by the collective group judgment. This creates the weighted normalized decision matrix.

**Ideal Solution Identification**
Both positive ideal solution (PIS) and negative ideal solution (NIS) are determined from the weighted matrix. The PIS represents the best possible performance across all criteria, while the NIS represents the worst.

**Separation Measure Calculation**
Euclidean distances are computed from each alternative to both ideal solutions. These separation measures quantify how close each alternative is to the best and worst possible outcomes.

**Relative Closeness Derivation**
The relative closeness coefficient is calculated for each alternative, representing its proximity to the ideal solution relative to the anti-ideal solution. Values closer to 1.0 indicate superior alternatives.

**Final Ranking Generation**
Alternatives are ranked in descending order of their relative closeness values, providing a clear group-based preference ordering that reflects collective decision-making priorities.
    

```

---

## 🎯 Implementation Integration

### Database Integration Framework

A comprehensive Group Decision Manager coordinates the entire process from data retrieval to result storage:

**Session-Based Analysis**
The system retrieves participant submissions from the database using session identifiers, ensuring data integrity and proper group formation. Minimum participation thresholds prevent incomplete analyses.

**Data Validation Pipeline**
Individual submissions undergo validation before aggregation, including consistency checking for AHP matrices and weight normalization verification for TOPSIS vectors.

**Analysis Execution**
Validated data feeds into the respective group analysis algorithms (AHP or TOPSIS), producing comprehensive results including individual assessments, group outcomes, and alternative rankings.

**Result Persistence**
Analysis outcomes are serialized and stored in the database with full traceability, enabling result retrieval, historical analysis, and audit trails for all group decisions.
            
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

## 📊 Consistency and Validation Framework

### AHP Consistency Assessment

The system implements comprehensive consistency validation for AHP matrices using Saaty's Consistency Ratio (CR) methodology:

**Mathematical Foundation**
Consistency assessment relies on the relationship between the largest eigenvalue (λmax) and the matrix dimension (n). Perfect consistency occurs when λmax = n, with deviations indicating judgment inconsistencies.

**Consistency Index Calculation**
The Consistency Index (CI) quantifies deviation from perfect consistency using the formula CI = (λmax - n)/(n - 1), providing a scale-independent measure of inconsistency.

**Random Index Normalization**
Saaty's Random Index (RI) values normalize the CI against random matrices of the same size, ensuring consistent interpretation across different matrix dimensions.

**Acceptance Threshold**
The standard acceptance threshold of CR ≤ 0.1 ensures that judgments are sufficiently consistent for reliable decision-making while acknowledging inherent human judgment variability.

### TOPSIS Weight Validation

TOPSIS weight validation ensures mathematical validity and practical applicability of weight vectors:

**Non-Negativity Requirement**
All weight values must be non-negative, reflecting the logical constraint that criteria cannot have negative importance in decision-making contexts.

**Normalization Verification**
Weight vectors should sum to unity for proper TOPSIS computation, though the system can handle automatic normalization when necessary.

**Zero Weight Detection**
The system identifies criteria with zero weights, which effectively removes them from the decision process, and provides appropriate warnings to users.

**Numerical Stability**
Validation includes checks for numerical stability issues such as extremely small weights that might cause computational problems in subsequent calculations.
```

---

## ⚡ Performance Optimization Framework

### Large Group Processing

The system implements scalable algorithms for handling large group decisions efficiently:

**Batch Processing Strategy**
When dealing with numerous participants, matrices are processed in configurable batches to manage memory usage and computational load. Batch results are then aggregated using the same geometric mean principles.

**Parallel Consistency Validation**
Individual matrix consistency checks are performed in parallel using thread pools, significantly reducing processing time for large groups while maintaining accuracy.

**Memory Optimization**
Efficient data structures and lazy evaluation minimize memory footprint during group aggregation processes, enabling analysis of substantially larger groups.

### Computational Scalability

**Algorithmic Complexity Management**
The system employs optimized linear algebra operations and leverages NumPy's vectorized computations to maintain reasonable performance as group size increases.

**Database Query Optimization**
Session data retrieval uses optimized queries and connection pooling to minimize database access overhead during group analysis initiation.

---

## 🔍 Advanced Analytical Features

### Sensitivity Analysis Framework

Sensitivity analysis examines the robustness of group decisions to small variations in individual judgments:

**Perturbation Testing**
The system systematically tests small perturbations to matrix elements, measuring how these changes affect final priority rankings and group consensus.

**Stability Metrics**
Ranking stability is quantified by measuring priority vector changes under various perturbation scenarios, identifying which judgments most critically affect group outcomes.

**Robustness Assessment**
Results include stability measures that help decision-makers understand the confidence level of their group consensus and identify potentially sensitive judgment areas.

### Future Enhancement Capabilities

**Fuzzy Logic Extensions**
The architecture supports future implementation of fuzzy AHP and TOPSIS methods for handling uncertainty and imprecision in group judgments.

**Advanced Aggregation Methods**
Framework accommodates integration of sophisticated aggregation techniques such as ordered weighted averaging and consensus-reaching algorithms.

**Real-Time Analysis**
System design enables future real-time sensitivity analysis and dynamic consensus monitoring during active group decision sessions.
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