import numpy as np
from core.mcda import AHPAnalyzer

# Let's trace the EXACT execution path
alternatives = np.array([
    [100, 8, 2],   # Alt 1
    [80,  6, 3],   # Alt 2  
    [120, 9, 1]    # Alt 3
])

objectives_info = [
    {'name': 'Cost', 'direction': 'Minimize'},
    {'name': 'Quality', 'direction': 'Maximize'},
    {'name': 'Time', 'direction': 'Minimize'}
]

criteria_comparisons = {
    ('Cost', 'Quality'): 0.5,
    ('Cost', 'Time'): 2.0,
    ('Quality', 'Time'): 3.0
}

print("=== TRACING THE EXACT EXECUTION ===")

ahp = AHPAnalyzer()

# Step 1: Create pairwise matrix
matrix = ahp.create_pairwise_matrix(criteria_comparisons, ['Cost', 'Quality', 'Time'])
print(f"1. Pairwise matrix:\n{matrix}")

# Step 2: Calculate weights
weights = ahp.calculate_weights(matrix)
print(f"2. Weights: {weights}")

# Step 3: Calculate consistency
cr = ahp.calculate_consistency_ratio(matrix, weights)
print(f"3. Consistency ratio: {cr}")

# Step 4: Score alternatives - THIS IS WHERE THE ISSUE MIGHT BE
scores = ahp.score_alternatives(alternatives, weights, objectives_info)
print(f"4. Scores: {scores}")

# Step 5: Rankings
rankings = np.argsort(-scores) + 1
print(f"5. Rankings: {rankings}")

# Compare with the full analyze method
print("\n=== FULL ANALYZE METHOD ===")
results = ahp.analyze(alternatives, criteria_comparisons, 
                     criteria_names=['Cost', 'Quality', 'Time'],
                     objectives_info=objectives_info)

print(f"Full analyze scores: {results['scores']}")
print(f"Full analyze rankings: {results['rankings']}")

# Let's look at the score differences
print(f"\n=== SCORE COMPARISON ===")
print(f"Manual step-by-step scores: {scores}")
print(f"Full analyze scores:        {results['scores']}")
print(f"Are they equal? {np.allclose(scores, results['scores'])}")

# Check if it's a display issue in the demo
print(f"\n=== DEMO DISPLAY CHECK ===")
for i, score in enumerate(results['scores']):
    rank = results['rankings'][i]
    print(f"  Alt {i+1}: {score:.4f} (Rank: {rank})")
    
# The issue might be in the demo formatting - let's check
print(f"\n=== CHECKING DEMO FORMATTING ===")
for i, score in enumerate(results['scores']):
    print(f"  Alt {i+1}: {score:.4f} -> formatted as {score:.0f}")