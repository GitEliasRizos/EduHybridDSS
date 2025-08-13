<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->
- [x] Verify that the copilot-instructions.md file in the .github directory is created.

- [x] Clarify Project Requirements
	PyMOO UI project using PyQt6 for multi-objective optimization with comprehensive interface for problem definition, algorithm configuration, and results visualization.

- [x] Scaffold the Project
	Project structure created manually with all necessary directories and core files:
	- Main application entry point (main.py)
	- UI components (main_window.py, problem_tab.py, algorithm_tab.py, results_tab.py)
	- Core functionality (problem_manager.py, algorithm_manager.py, optimizer.py)
	- Utilities (validators.py, helpers.py)
	- Example problems (JSON configurations)

- [x] Customize the Project
	Complete PyMOO GUI implementation with:
	- Problem definition interface for variables, objectives, and constraints
	- Algorithm selection and configuration (NSGA-II, NSGA-III, SPEA2, MOEA/D, RVEA)
	- Crossover and mutation operator configuration
	- Reference directions setup for many-objective algorithms
	- Results visualization with plots and tables
	- Export functionality for results

- [x] Install Required Extensions
	No specific extensions required by project setup info.

- [x] Compile the Project
	Dependencies defined in requirements.txt. Python environment setup required before running.

- [x] Create and Run Task
	No build tasks required for Python application. Direct execution via python main.py.

- [x] Launch the Project
	Application ready to launch. Install dependencies first, then run python main.py.

- [x] Ensure Documentation is Complete
	README.md and copilot-instructions.md completed with comprehensive project information.
