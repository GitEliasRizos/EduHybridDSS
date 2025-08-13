"""
Algorithm Manager - Core functionality for managing optimization algorithms
"""

from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.algorithms.moo.nsga3 import NSGA3
from pymoo.algorithms.moo.spea2 import SPEA2
from pymoo.algorithms.moo.moead import MOEAD
from pymoo.algorithms.moo.rvea import RVEA
from pymoo.operators.crossover.sbx import SBX
from pymoo.operators.crossover.pcx import PCX
from pymoo.operators.crossover.ux import UX
from pymoo.operators.mutation.pm import PM
# Note: GM (Gaussian Mutation) might not be available in all PyMOO versions
try:
    from pymoo.operators.mutation.gm import GM
except ImportError:
    GM = None
from pymoo.operators.sampling.rnd import FloatRandomSampling
from pymoo.util.ref_dirs import get_reference_directions
from pymoo.termination import get_termination
import numpy as np


class AlgorithmManager:
    """Manages optimization algorithm configurations and instantiation"""
    
    def __init__(self):
        self.current_algorithm = None
        self.algorithm_config = None
        
    def create_algorithm_from_config(self, config, n_objectives=2):
        """Create a PyMOO algorithm from configuration"""
        self.algorithm_config = config
        algorithm_name = config.get('name', 'NSGA-II')
        
        # Get common parameters
        pop_size = config.get('parameters', {}).get('population_size', 100)
        seed = config.get('parameters', {}).get('seed', 42)
        
        # Create crossover operator
        crossover = self._create_crossover_operator(config.get('crossover', {}))
        
        # Create mutation operator
        mutation = self._create_mutation_operator(config.get('mutation', {}))
        
        # Create sampling
        sampling = FloatRandomSampling()
        
        # Create algorithm based on name
        if algorithm_name == "NSGA-II":
            self.current_algorithm = NSGA2(
                pop_size=pop_size,
                crossover=crossover,
                mutation=mutation,
                sampling=sampling,
                eliminate_duplicates=True
            )
            
        elif algorithm_name == "NSGA-III":
            # Create reference directions
            ref_dirs = self._create_reference_directions(config, n_objectives)
            self.current_algorithm = NSGA3(
                ref_dirs=ref_dirs,
                pop_size=pop_size,
                crossover=crossover,
                mutation=mutation,
                sampling=sampling,
                eliminate_duplicates=True
            )
            
        elif algorithm_name == "SPEA2":
            archive_size = pop_size  # Default archive size
            self.current_algorithm = SPEA2(
                pop_size=pop_size,
                archive_size=archive_size,
                crossover=crossover,
                mutation=mutation,
                sampling=sampling,
                eliminate_duplicates=True
            )
            
        elif algorithm_name == "MOEA/D":
            # Create reference directions for decomposition
            ref_dirs = self._create_reference_directions(config, n_objectives)
            n_neighbors = 20  # Default neighborhood size
            prob_neighbor = 0.9  # Default neighbor probability
            
            self.current_algorithm = MOEAD(
                ref_dirs=ref_dirs,
                n_neighbors=n_neighbors,
                prob_neighbor_mating=prob_neighbor,
                crossover=crossover,
                mutation=mutation,
                sampling=sampling
            )
            
        elif algorithm_name == "RVEA":
            # Create reference directions
            ref_dirs = self._create_reference_directions(config, n_objectives)
            self.current_algorithm = RVEA(
                ref_dirs=ref_dirs,
                pop_size=pop_size,
                crossover=crossover,
                mutation=mutation,
                sampling=sampling,
                eliminate_duplicates=True
            )
            
        else:
            # Default to NSGA-II
            self.current_algorithm = NSGA2(
                pop_size=pop_size,
                crossover=crossover,
                mutation=mutation,
                sampling=sampling,
                eliminate_duplicates=True
            )
            
        return self.current_algorithm
        
    def _create_crossover_operator(self, crossover_config):
        """Create crossover operator from configuration"""
        operator_name = crossover_config.get('operator', 'SBX (Simulated Binary Crossover)')
        prob = crossover_config.get('probability', 0.9)
        eta = crossover_config.get('eta', 15.0)
        
        if 'SBX' in operator_name:
            return SBX(prob=prob, eta=eta)
        elif 'PCX' in operator_name:
            return PCX(prob=prob, eta=eta, zeta=0.1)
        elif 'UX' in operator_name or 'Uniform' in operator_name:
            return UX(prob=prob)
        else:
            # Default to SBX
            return SBX(prob=prob, eta=eta)
            
    def _create_mutation_operator(self, mutation_config):
        """Create mutation operator from configuration"""
        operator_name = mutation_config.get('operator', 'Polynomial Mutation')
        prob = mutation_config.get('probability', 0.1)
        eta = mutation_config.get('eta', 20.0)
        
        if 'Polynomial' in operator_name:
            return PM(prob=prob, eta=eta)
        elif 'Gaussian' in operator_name and GM is not None:
            return GM(prob=prob, sigma=0.1)
        else:
            # Default to Polynomial Mutation
            return PM(prob=prob, eta=eta)
            
    def _create_reference_directions(self, config, n_objectives):
        """Create reference directions for many-objective algorithms"""
        ref_dirs_config = config.get('reference_directions', {})
        method = ref_dirs_config.get('method', 'Das-Dennis')
        n_partitions = ref_dirs_config.get('n_partitions', 12)
        scaling = ref_dirs_config.get('scaling', 1.0)
        
        if method == 'Das-Dennis':
            ref_dirs = get_reference_directions("das-dennis", n_objectives, n_partitions=n_partitions)
        elif method == 'Multi-layer Das-Dennis':
            if n_objectives <= 3:
                ref_dirs = get_reference_directions("das-dennis", n_objectives, n_partitions=n_partitions)
            else:
                # Use multi-layer approach for high dimensions
                ref_dirs = get_reference_directions(
                    "multi-layer",
                    get_reference_directions("das-dennis", n_objectives, n_partitions=n_partitions//2),
                    get_reference_directions("das-dennis", n_objectives, n_partitions=n_partitions)
                )
        elif method == 'Uniform Random':
            n_dirs = ref_dirs_config.get('n_directions', 91)
            ref_dirs = np.random.random((n_dirs, n_objectives))
            # Normalize to unit simplex
            ref_dirs = ref_dirs / ref_dirs.sum(axis=1, keepdims=True)
        else:
            # Default to Das-Dennis
            ref_dirs = get_reference_directions("das-dennis", n_objectives, n_partitions=n_partitions)
            
        # Apply scaling if specified
        if scaling != 1.0:
            ref_dirs *= scaling
            
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
        
        if algorithm_name in ['NSGA-III', 'RVEA', 'MOEA/D']:
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
            "SPEA2": {
                "name": "SPEA2",
                "full_name": "Strength Pareto Evolutionary Algorithm 2",
                "description": "Archive-based algorithm with fine-grained fitness",
                "suitable_for": "2-3 objectives",
                "requires_ref_dirs": False,
                "paper": "Zitzler et al. (2001)"
            },
            "MOEA/D": {
                "name": "MOEA/D",
                "full_name": "Multi-Objective Evolutionary Algorithm based on Decomposition",
                "description": "Decomposes MOP into scalar optimization subproblems",
                "suitable_for": "2+ objectives",
                "requires_ref_dirs": True,
                "paper": "Zhang & Li (2007)"
            },
            "RVEA": {
                "name": "RVEA",
                "full_name": "Reference Vector Guided Evolutionary Algorithm",
                "description": "Uses reference vectors to guide search",
                "suitable_for": "3+ objectives",
                "requires_ref_dirs": True,
                "paper": "Cheng et al. (2016)"
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
                ("RVEA", "Good performance on irregular fronts")
            ]
        else:  # n_objectives > 3
            recommendations = [
                ("NSGA-III", "Best for many-objective problems"),
                ("RVEA", "Excellent for many objectives"),
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
