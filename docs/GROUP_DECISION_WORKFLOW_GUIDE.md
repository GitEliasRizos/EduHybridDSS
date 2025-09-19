# Group Decision Workflow Guide

## Overview

The PyMOO GUI now supports a complete 3-stage group decision-making workflow that allows administrators to run optimization problems and collect user preferences for multi-criteria decision analysis. This guide explains how the entire system works from start to finish.

## 🔄 The 3-Stage Workflow

### Stage 1: Admin Runs Multi-Objective Optimization
### Stage 2: Users Review Results and Provide Preferences  
### Stage 3: Admin Performs Group Decision Analysis

---

## 📋 Prerequisites

### System Requirements
- Python 3.8+
- PyQt6 installed
- All dependencies from `requirements.txt`

### User Setup
- Admin account created with full access
- Regular user accounts created for group participants
- Database initialized (`databases/pymoo.db`)

---

## 🎯 Stage 1: Admin Optimization Setup

### Step 1.1: Admin Login
```
1. Run: python main.py
2. Login with admin credentials
3. Admin interface opens with full PyMOO functionality
```

### Step 1.2: Problem Definition
```
1. Go to "Problem Definition" tab
2. Define optimization problem:
   - Variables (decision variables)
   - Objectives (what to optimize)
   - Constraints (limitations)
3. Save problem configuration if desired
```

### Step 1.3: Algorithm Configuration  
```
1. Go to "Algorithm" tab
2. Select optimization algorithm:
   - NSGA-II (most common)
   - NSGA-III (many objectives)
   - SPEA2, MOEA/D, etc.
3. Configure parameters:
   - Population size
   - Number of generations
   - Crossover/mutation settings
```

### Step 1.4: Run Optimization
```
1. Go to "Results" tab
2. Click "Run Optimization"
3. Monitor progress bar
4. Wait for completion
```

### Step 1.5: Create Group Session
```
When optimization completes:

1. Dialog appears: "Create Group Decision Session?"
2. Click "Yes" to proceed
3. Enter session name (e.g., "Product Design Session 1")
4. Click OK

✅ Session created with optimization results stored
✅ Users can now access this session
✅ Alternatives (solutions) ready for evaluation
```

---

## 👥 Stage 2: User Participation

### Step 2.1: User Login
```
1. Run: python main.py
2. Login with regular user credentials
3. User interface opens (simplified for decision-making)
```

### Step 2.2: Session Selection
```
1. Select session from dropdown menu
2. Session loads with:
   - Problem information
   - Criteria (objectives) list
   - Number of alternatives available
```

### Step 2.3: Review Optimization Results
```
📊 "Optimization Results" Tab:

1. Click on "📊 Optimization Results" tab (first tab)
2. Review the alternatives table:
   - Each row = one solution
   - Each column = one objective
   - Values show trade-offs between objectives
3. Understand what you're comparing before making preferences
```

### Step 2.4: AHP Pairwise Comparisons
```
🔄 "AHP Comparisons" Tab:

1. Click on "AHP Comparisons" tab
2. Compare criteria pairwise:
   - 1 = Equal importance
   - 3 = Moderate importance
   - 5 = Strong importance  
   - 7 = Very strong importance
   - 9 = Extreme importance
3. Fill all comparisons in upper triangle
4. Matrix automatically updates lower triangle
5. Click "Submit AHP Comparisons"
```

### Step 2.5: TOPSIS Weight Assignment
```
⚖️ "TOPSIS Weights" Tab:

1. Click on "TOPSIS Weights" tab
2. Assign importance weights to each criterion:
   - Higher values = more important
   - Weights automatically normalized to sum to 1.0
3. Use sliders or input boxes
4. Click "Submit TOPSIS Weights"
```

### Step 2.6: Submission Confirmation
```
✅ After submission:
- Status shows "Submitted successfully"
- Submissions are saved to database
- Admin can see participation progress
```

---

## 📊 Stage 3: Admin Group Analysis

### Step 3.1: Monitor Participation
```
Admin can check participation status:

1. Menu: "Group Decision" → "View Active Sessions"
2. See session table with:
   - Session name and details
   - Participation counts
   - Ready indicators (✅/❌)
   - AHP: X/Y users ✅ or ❌
   - TOPSIS: X/Y users ✅ or ❌
```

### Step 3.2: Check Ready Sessions
```
1. Menu: "Group Decision" → "Check Ready Sessions"
2. System shows which sessions have enough participants
3. Minimum 2 users needed for group analysis
```

### Step 3.3: Run Group AHP Analysis
```
1. Menu: "Group Decision" → "Run Group AHP Analysis"
2. Select session from dropdown
3. Click "Run AHP Analysis"
4. System aggregates all user AHP matrices
5. Computes group preferences and final rankings
6. Results displayed and saved to database
```

### Step 3.4: Run Group TOPSIS Analysis
```
1. Menu: "Group Decision" → "Run Group TOPSIS Analysis"  
2. Select session from dropdown
3. Click "Run TOPSIS Analysis"
4. System aggregates all user weight vectors
5. Computes group TOPSIS scores and rankings
6. Results displayed and saved to database
```

---

## 🔧 Technical Details

### Database Schema
```sql
-- Sessions store optimization results and metadata
sessions:
- optimization_results (JSON)
- alternatives_data (JSON) 
- criteria_names (JSON)
- objectives_info (JSON)

-- User inputs stored separately
ahp_comparisons:
- comparison_matrix (JSON)
- user_id, session_id

topsis_weights:
- weights (JSON)
- user_id, session_id

-- Group results computed and stored
group_results:
- aggregated_data (JSON)
- final_scores (JSON)
- final_rankings (JSON)
```

### Group Aggregation Methods

#### AHP Aggregation
```
1. Collect all user pairwise comparison matrices
2. Apply geometric mean aggregation:
   Group_matrix[i,j] = (∏ User_matrix[i,j])^(1/n)
3. Compute group priority vector using eigenvalue method
4. Rank alternatives based on group priorities
```

#### TOPSIS Aggregation  
```
1. Collect all user weight vectors
2. Apply arithmetic mean aggregation:
   Group_weights[i] = (Σ User_weights[i]) / n
3. Apply group weights to TOPSIS algorithm
4. Compute group ideal/anti-ideal solutions
5. Rank alternatives by similarity to ideal
```

---

## 📈 Usage Examples

### Example 1: Product Design Decision
```
Problem: Optimize smartphone design
Objectives: Minimize cost, maximize performance, minimize weight
Alternatives: 50 design solutions from optimization

Workflow:
1. Admin runs optimization → 50 solutions generated
2. Create session "Smartphone Design V1"
3. 5 engineers login and provide preferences
4. Admin runs group AHP → Final ranking produced
5. Top 3 solutions selected for further development
```

### Example 2: Supply Chain Optimization
```
Problem: Optimize supply chain network
Objectives: Minimize cost, minimize delivery time, maximize reliability
Alternatives: 100 network configurations

Workflow:
1. Admin optimizes supply chain → 100 configurations
2. Create session "Supply Chain Q4"
3. 8 stakeholders provide preferences
4. Admin runs both AHP and TOPSIS for comparison
5. Consensus solution selected for implementation
```

---

## 🚨 Troubleshooting

### Common Issues

#### "No optimization results available"
```
Cause: Session created without optimization results
Solution: Admin must run optimization before creating session
```

#### "Session not found"
```
Cause: Database connection or session deletion
Solution: Refresh sessions, check database integrity
```

#### "Not enough participants"
```
Cause: Less than 2 users submitted preferences
Solution: Wait for more users or reduce minimum requirement
```

#### "Analysis failed"
```
Cause: Inconsistent comparison matrices or weight vectors
Solution: Check user inputs for validity, re-run with corrected data
```

### Performance Tips

#### For Large Problems
```
- Limit alternatives to top 20-50 solutions
- Use problem-specific aggregation methods
- Consider clustering similar solutions
```

#### For Many Users
```
- Monitor database performance
- Consider batch processing for large groups
- Implement user notification system
```

---

## 🔮 Future Enhancements

### Planned Features
- Real-time collaboration
- Advanced aggregation methods (fuzzy AHP, interval TOPSIS)
- Sensitivity analysis for group decisions
- Export to Excel/PDF reports
- Email notifications for session participation
- Mobile-friendly user interface

### API Extensions
- REST API for external integration
- Webhook support for workflow automation
- Integration with enterprise systems

---

## 📚 References

### Academic Sources
- Saaty, T.L. (1980). The Analytic Hierarchy Process
- Hwang, C.L. & Yoon, K. (1981). TOPSIS method
- Forman, E. & Peniwati, K. (1998). Aggregating individual judgments

### Technical Documentation
- PyMOO Documentation: https://pymoo.org/
- PyQt6 Documentation: https://www.riverbankcomputing.com/
- Multi-Criteria Decision Analysis: Belton & Stewart (2002)

---

## 📞 Support

For technical support or questions about the group decision workflow:

1. Check this documentation first
2. Review error messages and logs
3. Test with simple examples
4. Contact system administrator

**Author:** Elias Rizos [it21490]  
**Version:** 2.0.0  
**Last Updated:** September 19, 2025

---

*This guide covers the complete group decision-making workflow from optimization to final group rankings. Follow the stages sequentially for best results.*