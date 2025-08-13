# Example Problems for PyMOO GUI

This directory contains example problem configurations that can be loaded into the PyMOO GUI for testing and demonstration purposes.

## Available Examples

### 1. Simple Bi-objective Problem
**File:** `simple_biobjective.json`
- 2 variables (x1, x2)
- 2 objectives to minimize
- Simple quadratic functions
- No constraints
- Good for beginners

### 2. ZDT1 Test Problem
**File:** `zdt1.json`
- 30 variables
- 2 objectives
- Classic test problem from literature
- Convex Pareto front

### 3. DTLZ2 Test Problem
**File:** `dtlz2.json`
- 12 variables
- 3 objectives
- Many-objective test problem
- Spherical Pareto front

### 4. Constrained Engineering Problem
**File:** `constrained_engineering.json`
- 4 variables
- 2 objectives
- 3 constraints
- Representative of real engineering problems

### 5. Rosenbrock Multi-objective
**File:** `rosenbrock_mo.json`
- 2 variables
- 2 objectives based on Rosenbrock function
- Challenging optimization landscape

## How to Use

1. Launch the PyMOO GUI
2. Go to File → Open Problem
3. Navigate to the examples directory
4. Select the desired JSON file
5. The problem configuration will be loaded automatically

## Creating Custom Examples

You can create your own example problems by:

1. Configuring a problem in the GUI
2. Saving it using File → Save Problem
3. Placing the JSON file in this directory
4. Adding documentation here

## Problem Configuration Format

Each example file contains:
- Problem metadata (name, description, type)
- Variable definitions (bounds, types, names)
- Objective function definitions
- Constraint definitions (if any)

See the existing examples for the complete JSON structure.
