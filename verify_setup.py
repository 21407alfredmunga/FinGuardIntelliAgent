#!/usr/bin/env python3
"""
FinGuard IntelliAgent - Setup Verification Script
=================================================

This script verifies that Milestone 1 setup is complete and correct.

Run this after installation to ensure everything is properly configured.

Author: Alfred Munga
License: MIT
"""

import os
import sys
from pathlib import Path


def print_header(text):
    """Print a formatted header."""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)


def print_success(text):
    """Print a success message."""
    print(f"✅ {text}")


def print_error(text):
    """Print an error message."""
    print(f"❌ {text}")


def print_info(text):
    """Print an info message."""
    print(f"ℹ️  {text}")


def check_directory_structure():
    """Verify all required directories exist."""
    print_header("Checking Directory Structure")
    
    required_dirs = [
        "backend",
        "backend/routers",
        "backend/models",
        "backend/services",
        "backend/utils",
        "agent",
        "agent/planning",
        "tools",
        "notebooks",
        "data",
        "data/synthetic",
        "data/sample_inputs",
        "docs",
    ]
    
    all_exist = True
    for directory in required_dirs:
        if os.path.isdir(directory):
            print_success(f"Directory exists: {directory}/")
        else:
            print_error(f"Directory missing: {directory}/")
            all_exist = False
    
    return all_exist


def check_files():
    """Verify all required files exist."""
    print_header("Checking Required Files")
    
    required_files = [
        "README.md",
        "LICENSE",
        "requirements.txt",
        ".gitignore",
        ".env.example",
        "CONTRIBUTING.md",
        "backend/app.py",
        "backend/__init__.py",
        "agent/orchestrator.py",
        "agent/__init__.py",
        "tools/sms_parser_tool.py",
        "tools/insights_tool.py",
        "tools/invoice_collection_tool.py",
        "tools/__init__.py",
        "docs/PROJECT_DOCUMENTATION.md",
        "docs/MILESTONE_1_SUMMARY.md",
    ]
    
    all_exist = True
    for file_path in required_files:
        if os.path.isfile(file_path):
            print_success(f"File exists: {file_path}")
        else:
            print_error(f"File missing: {file_path}")
            all_exist = False
    
    return all_exist


def check_python_syntax():
    """Check Python files for syntax errors."""
    print_header("Checking Python Syntax")
    
    python_files = [
        "backend/app.py",
        "agent/orchestrator.py",
        "tools/sms_parser_tool.py",
        "tools/insights_tool.py",
        "tools/invoice_collection_tool.py",
    ]
    
    all_valid = True
    for file_path in python_files:
        try:
            with open(file_path, 'r') as f:
                compile(f.read(), file_path, 'exec')
            print_success(f"Valid syntax: {file_path}")
        except SyntaxError as e:
            print_error(f"Syntax error in {file_path}: {e}")
            all_valid = False
        except Exception as e:
            print_error(f"Error checking {file_path}: {e}")
            all_valid = False
    
    return all_valid


def check_imports():
    """Check if Python files can be imported."""
    print_header("Checking Module Imports")
    
    modules = [
        ("backend", "backend"),
        ("agent", "agent"),
        ("tools", "tools"),
    ]
    
    all_importable = True
    original_path = sys.path.copy()
    
    # Add current directory to path
    sys.path.insert(0, os.getcwd())
    
    for display_name, module_name in modules:
        try:
            __import__(module_name)
            print_success(f"Module imports successfully: {display_name}")
        except ImportError as e:
            print_info(f"Import note for {display_name}: {e}")
            print_info("  (This is expected if dependencies aren't installed)")
        except Exception as e:
            print_error(f"Error importing {display_name}: {e}")
            all_importable = False
    
    # Restore original path
    sys.path = original_path
    
    return all_importable


def check_documentation():
    """Check that documentation files have content."""
    print_header("Checking Documentation")
    
    doc_files = [
        ("README.md", 100),
        ("LICENSE", 10),  # MIT License is typically ~21 lines
        ("CONTRIBUTING.md", 50),
        ("docs/PROJECT_DOCUMENTATION.md", 100),
    ]
    
    all_valid = True
    for file_path, min_lines in doc_files:
        try:
            with open(file_path, 'r') as f:
                lines = f.readlines()
                if len(lines) >= min_lines:
                    print_success(f"Documentation complete: {file_path} ({len(lines)} lines)")
                else:
                    print_error(f"Documentation too short: {file_path} ({len(lines)} lines, expected {min_lines}+)")
                    all_valid = False
        except Exception as e:
            print_error(f"Error reading {file_path}: {e}")
            all_valid = False
    
    return all_valid


def main():
    """Run all verification checks."""
    print_header("FinGuard IntelliAgent - Milestone 1 Setup Verification")
    print("Version: 0.1.0")
    print("Author: Alfred Munga")
    
    # Change to script directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    print_info(f"Working directory: {os.getcwd()}")
    
    # Run all checks
    results = {
        "Directory Structure": check_directory_structure(),
        "Required Files": check_files(),
        "Python Syntax": check_python_syntax(),
        "Module Imports": check_imports(),
        "Documentation": check_documentation(),
    }
    
    # Summary
    print_header("Verification Summary")
    
    all_passed = True
    for check_name, passed in results.items():
        if passed:
            print_success(f"{check_name}: PASSED")
        else:
            print_error(f"{check_name}: FAILED")
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 All checks passed! Milestone 1 setup is complete.")
        print("=" * 60)
        print("\nNext steps:")
        print("1. Copy .env.example to .env and add your API keys")
        print("2. Install dependencies: pip install -r requirements.txt")
        print("3. Test the backend: python backend/app.py")
        print("4. Review docs/MILESTONE_1_SUMMARY.md for details")
        print("5. Ready to start Milestone 2 implementation!")
        return 0
    else:
        print("⚠️  Some checks failed. Please review the errors above.")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(main())
