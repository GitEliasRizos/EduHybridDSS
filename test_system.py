#!/usr/bin/env python3
"""
Test script to validate PyMOO GUI functionality
This script tests core functionality without launching the GUI
"""

import sys
import json
from pathlib import Path

def test_imports():
    """Test if all required modules can be imported"""
    try:
        import PyQt6.QtCore
        import PyQt6.QtWidgets
        import PyQt6.QtGui
        import pymoo
        import numpy
        import matplotlib
        print("✓ All dependencies imported successfully")
        print(f"  - Python: {sys.version.split()[0]}")
        print(f"  - PyQt6: {PyQt6.QtCore.qVersion()}")
        print(f"  - PyMOO: {pymoo.__version__}")
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

def test_gui_components():
    """Test GUI component creation without showing windows"""
    try:
        from PyQt6.QtWidgets import QApplication
        from ui.main_window import MainWindow
        
        app = QApplication(sys.argv)
        window = MainWindow()
        print("✓ GUI components created successfully")
        app.quit()
        return True
    except Exception as e:
        print(f"✗ GUI component error: {e}")
        return False

def test_configuration_loading():
    """Test configuration file loading"""
    try:
        from utils.helpers import load_complete_config
        
        # Test all example files
        examples_dir = Path("examples")
        success_count = 0
        
        for config_file in examples_dir.glob("*.json"):
            try:
                config = load_complete_config(str(config_file))
                if 'problem' in config and ('algorithm' in config or 'variables' in config):
                    success_count += 1
                    print(f"  ✓ {config_file.name}")
                else:
                    print(f"  ✗ {config_file.name} - Missing sections")
            except Exception as e:
                print(f"  ✗ {config_file.name} - Error: {e}")
        
        print(f"✓ Configuration loading: {success_count} files loaded successfully")
        return success_count > 0
    except Exception as e:
        print(f"✗ Configuration loading error: {e}")
        return False

def test_optimization_components():
    """Test core optimization components"""
    try:
        from core.problem_manager import ProblemManager
        from core.algorithm_manager import AlgorithmManager
        from core.optimizer import Optimizer
        
        # Test basic component creation
        problem_mgr = ProblemManager()
        algorithm_mgr = AlgorithmManager()
        optimizer = Optimizer()
        
        print("✓ Core optimization components created successfully")
        return True
    except Exception as e:
        print(f"✗ Optimization components error: {e}")
        return False

def main():
    """Run all tests"""
    print("PyMOO GUI - System Validation Test")
    print("=" * 50)
    
    tests = [
        ("Dependencies", test_imports),
        ("GUI Components", test_gui_components),
        ("Configuration Loading", test_configuration_loading),
        ("Optimization Components", test_optimization_components),
    ]
    
    passed = 0
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        if test_func():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"Test Results: {passed}/{len(tests)} passed")
    
    if passed == len(tests):
        print("✓ All systems operational - PyMOO GUI is ready to use!")
        return 0
    else:
        print("✗ Some tests failed - please check the errors above")
        return 1

if __name__ == "__main__":
    sys.exit(main())
