"""
Algorithm Manager - Core functionality for managing optimization algorithms

This module provides the AlgorithmManager class which handles the creation and
configuration of multi-objective optimization algorithms from PyMOO. It serves
as the bridge between GUI algorithm configuration and PyMOO algorithm instances.

Key Features:
- Support for multiple Multi-Objective Optimization algorithms (NSGA-II, NS        if n_objectives == 2:
            recommendations = [
                ("NSGA-II", "Excellent for bi-objective problems"),
                ("MOEA/D", "Effective for regular Pareto fronts")
            ], MOEA/D)
- Crossover operator configuration (SBX, PCX, UX)
- Mutation operator configuration (Polynomial, Gaussian)
- Reference direction generation for many-objective problems
- Population sampling strategies
- Repair operators for integer/binary variable constraints  | # TODO: Needs work, fixes and testing
- Termination criteria configuration

The AlgorithmManager automatically selects appropriate operators and configurations
based on the problem characteristics (number of objectives, variable types) and
user preferences specified through the GUI.

Supported Algorithms:
    - NSGA-II: Fast Non-dominated Sorting Genetic Algorithm II
    - NSGA-III: NSGA-II extension for many-objective problems
    - MOEA/D: Multi-Objective Evolutionary Algorithm based on Decomposition

Classes:
    AlgorithmManager: Main interface for algorithm creation and management
    IntegerBinaryRepair: Repair operator for discrete variable constraints | # TODO: Needs work, fixes and testing

Author: Elias Rizos [it21490]
Version: 1.3.2
"""

from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.algorithms.moo.nsga3 import NSGA3
from pymoo.algorithms.moo.moead import MOEAD
from pymoo.operators.crossover.sbx import SBX
from pymoo.operators.crossover.pcx import PCX
from pymoo.operators.crossover.ux import UX
from pymoo.operators.mutation.pm import PM
from pymoo.operators.mutation.bitflip import BitflipMutation
# Note: GM (Gaussian Mutation) might not be available in all PyMOO versions
# We handle this gracefully with a try-except block
# TODO: DO I NEED GAUSSIAN MUTATION? Or SHOULD I REMOVE IT 
try:
    from pymoo.operators.mutation.gm import GM
except ImportError:
    GM = None  # Will be handled in mutation operator creation
from pymoo.operators.sampling.rnd import FloatRandomSampling
from pymoo.util.ref_dirs import get_reference_directions
from pymoo.termination import get_termination
import numpy as np


class AlgorithmManager:
    """
    Manages optimization algorithm configurations and instantiation
    
    This class serves as the central hub for algorithm management, converting
    GUI-based algorithm configurations into fully configured PyMOO algorithm
    instances. It handles the complexity of operator selection, parameter
    configuration, and constraint enforcement.
    
    Key Responsibilities:
    - Create algorithm instances from GUI configuration
    - Configure crossover and mutation operators
    - Set up repair operators for discrete variables
    - Generate reference directions for many-objective algorithms
    - Configure termination criteria
    - Handle algorithm-specific parameter validation
    
    The AlgorithmManager ensures that all algorithm components work together
    properly, especially for mixed-variable problems requiring repair operators.
    
    Attributes:
        current_algorithm: The active PyMOO algorithm instance
        algorithm_config: Dictionary containing the current algorithm configuration
    """
    
    def __init__(self):
        """
        Initialize the AlgorithmManager
        
        Sets up empty algorithm state. Algorithms are created dynamically
        when create_algorithm_from_config is called.
        """
        self.current_algorithm = None  # Active PyMOO algorithm instance
        self.algorithm_config = None   # Current algorithm configuration dict
        
    def create_algorithm_from_config(self, config, n_objectives=2, problem_config=None):
        """
        Create a PyMOO algorithm instance from GUI configuration
        
        This is the main interface for algorithm creation. It analyzes the
        configuration and problem characteristics to create a fully configured
        algorithm instance with appropriate operators and parameters.
        
        Args:
            config (dict): Algorithm configuration containing:
                - name: Algorithm name (NSGA-II, NSGA-III, etc.)
                - parameters: Algorithm-specific parameters
                - crossover: Crossover operator configuration
                - mutation: Mutation operator configuration
            n_objectives (int): Number of objectives in the problem
            problem_config (dict, optional): Problem configuration for repair operators
        
        Returns:
            Algorithm: A fully configured PyMOO algorithm instance
            
        Raises:
            ValueError: If algorithm name is not supported
            KeyError: If required configuration parameters are missing
        """
        self.algorithm_config = config
        algorithm_name = config.get('name', 'NSGA-II')
        
        # Extract common algorithm parameters
        pop_size = config.get('parameters', {}).get('population_size', 100)
        seed = config.get('parameters', {}).get('seed', 42)
        
        # Create repair operator for mixed-variable problems
        # This ensures integer/binary variables maintain their discrete nature
        repair = self._create_repair_operator(problem_config)
        
        # Create crossover operator with repair capabilities
        crossover_config = config.get('crossover', {})
        crossover = self._create_crossover_operator(crossover_config, repair)
        
        # Create mutation operator with repair capabilities  
        mutation_config = config.get('mutation', {})
        mutation = self._create_mutation_operator(mutation_config, repair)
        
        # Create sampling
        sampling = self._create_mixed_sampling(problem_config)
        
        # Create algorithm based on name
        if algorithm_name == "NSGA-II":
            self.current_algorithm = NSGA2(
                pop_size=pop_size,
                crossover=crossover,
                mutation=mutation,
                sampling=sampling,
                repair=repair,
                eliminate_duplicates=True
            )
            
        elif algorithm_name == "NSGA-III":
            # NSGA-III: Extension of NSGA-II for many-objective optimization
            # Uses reference directions to maintain diversity in high-dimensional objective space
            ref_dirs = self._create_reference_directions(config, n_objectives)
            self.current_algorithm = NSGA3(
                ref_dirs=ref_dirs,          # Reference directions for objective space partitioning
                pop_size=pop_size,          # Population size (should be close to # ref directions)
                crossover=crossover,        # Crossover operator for creating offspring
                mutation=mutation,          # Mutation operator for introducing variation
                sampling=sampling,          # Initial population sampling strategy
                repair=repair,              # Repair operator for constraint handling
                eliminate_duplicates=True   # Remove duplicate solutions to maintain diversity
            )
            
        elif algorithm_name == "MOEA/D":
            # MOEA/D: Decomposes multi-objective problem into scalar subproblems
            # Each subproblem optimizes a weighted combination of objectives
            ref_dirs = self._create_reference_directions(config, n_objectives)
            
            # Extract MOEA/D specific parameters from configuration
            algorithm_params = config.get('parameters', {})
            n_neighbors = algorithm_params.get('n_neighbors', 20)      # Number of neighboring subproblems for mating
            prob_neighbor = 0.9   # Probability of selecting parents from neighborhood
            decomposition = algorithm_params.get('decomposition', 'Tchebycheff')  # Decomposition method
            
            self.current_algorithm = MOEAD(
                ref_dirs=ref_dirs,                    # Weight vectors for decomposition
                n_neighbors=n_neighbors,              # Neighborhood size for each subproblem
                prob_neighbor_mating=prob_neighbor,   # Probability of local vs global mating
                crossover=crossover,                  # Crossover operator
                mutation=mutation,                    # Mutation operator
                sampling=sampling                     # Initial population sampling
            )
            
        else:
            # Default fallback to NSGA-II (most robust and widely applicable)
            # NSGA-II: Non-dominated sorting + crowding distance for diversity
            self.current_algorithm = NSGA2(
                pop_size=pop_size,          # Size of population maintained each generation
                crossover=crossover,        # Crossover operator for recombination
                mutation=mutation,          # Mutation operator for exploration
                sampling=sampling,          # Strategy for generating initial population
                eliminate_duplicates=True   # Remove duplicate solutions automatically
            )
            
        return self.current_algorithm
        
    def _create_crossover_operator(self, crossover_config, repair=None):
        """
        Create a crossover operator from GUI configuration
        
        Crossover operators combine parent solutions to create offspring.
        This method handles the different crossover types supported by PyMOO
        and applies repair operators when needed for discrete variables.
        
        Args:
            crossover_config: Dict with operator type, probability, and parameters
            repair: Optional repair operator for integer/binary constraints
            
        Returns:
            PyMOO crossover operator instance configured with user parameters
        """
        operator_name = crossover_config.get('operator', 'SBX (Simulated Binary Crossover)')
        prob = crossover_config.get('probability', 0.9)  # Probability of applying crossover
        eta = crossover_config.get('eta', 15.0)  # Distribution index (controls spread)
        
        # SBX: Good for real-valued variables, creates offspring near parents
        if 'SBX' in operator_name:
            return SBX(prob=prob, eta=eta, repair=repair)
        # PCX: Parent-centric crossover, good for exploration
        elif 'PCX' in operator_name:
            return PCX(prob=prob, eta=eta, zeta=0.1)
        # UX: Uniform crossover, each gene has equal chance from either parent
        elif 'UX' in operator_name or 'Uniform' in operator_name:
            return UX(prob=prob)
        else:
            # Default fallback to SBX if unknown operator specified
            return SBX(prob=prob, eta=eta, repair=repair)
            
    def _create_mutation_operator(self, mutation_config, repair=None):
        """
        Create a mutation operator from GUI configuration
        
        Mutation operators introduce variation in offspring solutions.
        Different mutation types are appropriate for different variable types
        (real, integer, binary).
        
        Args:
            mutation_config: Dict with operator type, probability, and parameters
            repair: Optional repair operator for integer/binary constraints
            
        Returns:
            PyMOO mutation operator instance configured with user parameters
        """
        operator_name = mutation_config.get('operator', 'Polynomial Mutation')
        prob = mutation_config.get('probability', 0.1)  # Per-variable mutation probability
        eta = mutation_config.get('eta', 20.0)  # Distribution index (higher = less spread)
        
        # Select appropriate mutation operator based on variable types
        if 'Bitflip' in operator_name:
            # For binary optimization problems - flips bits randomly
            return BitflipMutation(prob=prob, repair=repair)
        elif 'Polynomial' in operator_name:
            # For real-valued problems - polynomial distribution mutation
            return PM(prob=prob, eta=eta, repair=repair)
        elif 'Gaussian' in operator_name and GM is not None:
            # Gaussian mutation - adds normal distributed noise
            return GM(prob=prob, sigma=0.1)
        else:
            # Default fallback to Polynomial Mutation for real variables
            return PM(prob=prob, eta=eta, repair=repair)
            
    def _create_reference_directions(self, config, n_objectives):
        """
        Create reference directions for many-objective optimization algorithms
        
        Reference directions guide the search in many-objective problems by
        providing preferred regions in the objective space. They're essential
        for algorithms like NSGA-III and MOEA/D.
        
        Args:
            config: Algorithm configuration dict with reference_directions settings
            n_objectives: Number of objectives in the optimization problem
            
        Returns:
            numpy.ndarray: Reference direction vectors normalized to unit simplex
        """
        ref_dirs_config = config.get('reference_directions', {})
        # Support both 'type' (from JSON) and 'method' (legacy compatibility)
        method = ref_dirs_config.get('type', ref_dirs_config.get('method', 'Das-Dennis'))
        n_partitions = ref_dirs_config.get('n_partitions', 12)  # Discretization level
        scaling = ref_dirs_config.get('scaling', 1.0)  # Optional scaling factor
        
        # Das-Dennis: Creates evenly distributed directions on unit simplex
        if method == 'Das-Dennis':
            ref_dirs = get_reference_directions("das-dennis", n_objectives, n_partitions=n_partitions)
        # Multi-layer: Combines different discretization levels for better coverage
        elif method == 'Multi-layer Das-Dennis':
            if n_objectives <= 3:
                # For low dimensions, single-layer is sufficient
                ref_dirs = get_reference_directions("das-dennis", n_objectives, n_partitions=n_partitions)
            else:
                # For high dimensions, use multi-layer approach for better distribution
                ref_dirs = get_reference_directions(
                    "multi-layer",
                    get_reference_directions("das-dennis", n_objectives, n_partitions=n_partitions//2),
                    get_reference_directions("das-dennis", n_objectives, n_partitions=n_partitions)
                )
        # Uniform Random: Randomly distributed directions (less structured)
        elif method == 'Uniform Random':
            n_dirs = ref_dirs_config.get('n_directions', 91)  # Number of random directions
            ref_dirs = np.random.random((n_dirs, n_objectives))
            # Normalize to unit simplex (sum of components = 1)
            ref_dirs = ref_dirs / ref_dirs.sum(axis=1, keepdims=True)
        else:
            # Default to Das-Dennis
            ref_dirs = get_reference_directions("das-dennis", n_objectives, n_partitions=n_partitions)
            
        # Apply scaling if specified
        if scaling != 1.0:
            ref_dirs *= scaling
            
        # Ensure no reference directions have zero norm (causes division warnings)
        norms = np.linalg.norm(ref_dirs, axis=1)
        zero_norm_mask = norms < 1e-10
        if np.any(zero_norm_mask):
            # Add small positive values to zero-norm directions
            ref_dirs[zero_norm_mask] += 1e-8
            # Renormalize
            ref_dirs = ref_dirs / np.linalg.norm(ref_dirs, axis=1, keepdims=True)
            
        return ref_dirs
        
    def create_termination_criterion(self, config):
        """Create termination criterion from configuration"""
        termination_config = config.get('termination', {})
        max_evals = termination_config.get('max_evaluations', 25000)
        
        # For now, use function evaluations as the main criterion
        termination = get_termination("n_eval", max_evals)
        
        # TODO: Add support for convergence-based termination
        # if termination_config.get('enable_convergence', False):
        #     conv_tol = termination_config.get('convergence_tolerance', 1e-6)
        #     Add convergence termination
        
        return termination
        
    def _create_repair_operator(self, problem_config):
        """Create repair operator for integer/binary variables"""
        from pymoo.core.repair import Repair
        import numpy as np
        
        if not problem_config or 'variables' not in problem_config:
            return None
            
        var_types = [var.get('type', 'Real').lower() for var in problem_config['variables']]
        has_discrete = any(t in ['integer', 'int', 'binary', 'bool'] for t in var_types)
        
        if not has_discrete:
            return None
            
        class IntegerBinaryRepair(Repair):
            def __init__(self, var_types, xl, xu):
                super().__init__()
                self.var_types = var_types
                self.xl = xl
                self.xu = xu
                
            def _do(self, problem, X, **kwargs):
                if X.ndim == 1:
                    X = X.reshape(1, -1)
                    
                X_repaired = X.copy()
                
                for i, vtype in enumerate(self.var_types):
                    vtype_lower = vtype.lower()
                    if vtype_lower in ['integer', 'int']:
                        # Round to nearest integer and clip to bounds
                        X_repaired[:, i] = np.round(X_repaired[:, i])
                        X_repaired[:, i] = np.clip(X_repaired[:, i], self.xl[i], self.xu[i])
                    elif vtype_lower in ['binary', 'bool']:
                        # Round to 0 or 1
                        X_repaired[:, i] = np.round(X_repaired[:, i])
                        X_repaired[:, i] = np.clip(X_repaired[:, i], 0, 1)
                
                return X_repaired
        
        # Get bounds from problem config
        xl = np.array([var['lower_bound'] for var in problem_config['variables']])
        xu = np.array([var['upper_bound'] for var in problem_config['variables']])
        
        return IntegerBinaryRepair(var_types, xl, xu)
        
    def _create_mixed_sampling(self, problem_config):
        """Create sampling for problems with mixed variables (uses regular sampling + repair)"""
        from pymoo.operators.sampling.rnd import FloatRandomSampling
        
        # For mixed variables, we'll use regular float sampling and let repair handle discretization
        return FloatRandomSampling()
        
    def validate_algorithm_config(self, config, n_objectives=2):
        """Validate algorithm configuration"""
        errors = []
        
        # Check if algorithm name is provided
        if 'name' not in config or not config['name']:
            errors.append("Algorithm name must be specified")
            
        # Check population size
        params = config.get('parameters', {})
        pop_size = params.get('population_size', 100)
        if pop_size < 10:
            errors.append("Population size must be at least 10")
        elif pop_size > 10000:
            errors.append("Population size should not exceed 10,000")
            
        # Check generations
        n_gen = params.get('n_generations', 250)
        if n_gen < 1:
            errors.append("Number of generations must be at least 1")
            
        # Check crossover probability
        crossover = config.get('crossover', {})
        cross_prob = crossover.get('probability', 0.9)
        if not 0 <= cross_prob <= 1:
            errors.append("Crossover probability must be between 0 and 1")
            
        # Check mutation probability
        mutation = config.get('mutation', {})
        mut_prob = mutation.get('probability', 0.1)
        if not 0 <= mut_prob <= 1:
            errors.append("Mutation probability must be between 0 and 1")
            
        # Algorithm-specific validations
        algorithm_name = config.get('name', '')
        
        if algorithm_name in ['NSGA-III', 'MOEA/D']:
            ref_dirs = config.get('reference_directions', {})
            if n_objectives > 3:
                n_partitions = ref_dirs.get('n_partitions', 12)
                if n_partitions < 1:
                    errors.append("Number of partitions must be at least 1")
                    
        return errors
        
    def get_algorithm_info(self, algorithm_name):
        """Get information about a specific algorithm"""
        algorithm_info = {
            "NSGA-II": {
                "name": "NSGA-II",
                "full_name": "Non-dominated Sorting Genetic Algorithm II",
                "description": "Fast and elitist multi-objective genetic algorithm",
                "suitable_for": "2-3 objectives",
                "requires_ref_dirs": False,
                "paper": "Deb et al. (2002)"
            },
            "NSGA-III": {
                "name": "NSGA-III",
                "full_name": "Non-dominated Sorting Genetic Algorithm III",
                "description": "Extension of NSGA-II for many-objective optimization",
                "suitable_for": "3+ objectives",
                "requires_ref_dirs": True,
                "paper": "Deb & Jain (2014)"
            },
            "MOEA/D": {
                "name": "MOEA/D",
                "full_name": "Multi-Objective Evolutionary Algorithm based on Decomposition",
                "description": "Decomposes MOP into scalar optimization subproblems",
                "suitable_for": "2+ objectives",
                "requires_ref_dirs": True,
                "paper": "Zhang & Li (2007)"
            }
        }
        
        return algorithm_info.get(algorithm_name, {
            "name": algorithm_name,
            "full_name": algorithm_name,
            "description": "No description available",
            "suitable_for": "Unknown",
            "requires_ref_dirs": False,
            "paper": "Unknown"
        })
        
    def get_recommended_algorithms(self, n_objectives, has_constraints=False):
        """Get recommended algorithms based on problem characteristics"""
        recommendations = []
        
        if n_objectives <= 2:
            recommendations = [
                ("NSGA-II", "Excellent for bi-objective problems"),
                ("SPEA2", "Good alternative with archive mechanism"),
                ("MOEA/D", "Effective for regular Pareto fronts")
            ]
        elif n_objectives == 3:
            recommendations = [
                ("NSGA-II", "Still effective for 3 objectives"),
                ("NSGA-III", "Designed for many-objective optimization"),
                ("MOEA/D", "Good for decomposable problems")
            ]
        else:  # n_objectives > 3
            recommendations = [
                ("NSGA-III", "Best for many-objective problems"),
                ("MOEA/D", "Good for decomposable problems")
            ]
            
        if has_constraints:
            recommendations.append(("CTAEA", "Specialized for constrained problems"))
            
        return recommendations
        
    def get_algorithm_summary(self):
        """Get a summary of the current algorithm configuration"""
        if not self.algorithm_config:
            return "No algorithm configured"
            
        config = self.algorithm_config
        summary = f"""
Algorithm: {config.get('name', 'Unknown')}
Population Size: {config.get('parameters', {}).get('population_size', 100)}
Generations: {config.get('parameters', {}).get('n_generations', 250)}
Crossover: {config.get('crossover', {}).get('operator', 'SBX')} (p={config.get('crossover', {}).get('probability', 0.9)})
Mutation: {config.get('mutation', {}).get('operator', 'PM')} (p={config.get('mutation', {}).get('probability', 0.1)})
"""
        
        if 'reference_directions' in config:
            ref_config = config['reference_directions']
            summary += f"Reference Directions: {ref_config.get('method', 'Das-Dennis')} ({ref_config.get('n_partitions', 12)} partitions)\n"
            
        return summary.strip()
