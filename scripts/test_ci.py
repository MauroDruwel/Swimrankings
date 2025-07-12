#!/usr/bin/env python3
"""
Local CI/CD testing script to verify workflows will pass.

This script runs the same checks that GitHub Actions will run,
allowing you to test locally before pushing.
"""

import subprocess
import sys
from pathlib import Path

# Get the project root directory
project_root = Path(__file__).parent.parent
print(f"Testing in: {project_root}")


def run_command(cmd, description):
    """Run a command and return success status."""
    print(f"\n🔍 {description}")
    print(f"Running: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, cwd=project_root, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} - PASSED")
            return True
        else:
            print(f"❌ {description} - FAILED")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            return False
    except Exception as e:
        print(f"❌ {description} - ERROR: {e}")
        return False


def main():
    """Run all CI checks locally."""
    print("🚀 Running local CI/CD checks...")
    
    all_passed = True
    
    # 1. Lint with flake8
    if not run_command(
        ["python", "-m", "flake8", ".", "--count", "--select=E9,F63,F7,F82", "--show-source", "--statistics"],
        "Flake8 syntax check"
    ):
        all_passed = False
    
    if not run_command(
        ["python", "-m", "flake8", ".", "--count", "--exit-zero", "--max-complexity=10", "--max-line-length=127", "--statistics"],
        "Flake8 style check"
    ):
        all_passed = False
    
    # 2. Type check with mypy
    if not run_command(
        ["python", "-m", "mypy", "swimrankings"],
        "MyPy type checking"
    ):
        all_passed = False
    
    # 3. Run tests
    if not run_command(
        ["python", "-m", "pytest", "--cov=swimrankings", "--cov-report=term"],
        "Pytest with coverage"
    ):
        all_passed = False
    
    # 4. Build package
    if not run_command(
        ["python", "-m", "build"],
        "Package build"
    ):
        all_passed = False
    
    # 5. Check package
    if not run_command(
        ["python", "-m", "twine", "check", "dist/*"],
        "Package validation"
    ):
        all_passed = False
    
    # 6. Build documentation (if docs directory exists)
    docs_dir = project_root / "docs"
    if docs_dir.exists():
        print(f"\n🔍 Building documentation")
        try:
            result = subprocess.run(
                ["npm", "run", "build"], 
                cwd=docs_dir, 
                capture_output=True, 
                text=True
            )
            if result.returncode == 0:
                print("✅ Documentation build - PASSED")
            else:
                print("❌ Documentation build - FAILED")
                print("STDOUT:", result.stdout)
                print("STDERR:", result.stderr)
                all_passed = False
        except Exception as e:
            print(f"❌ Documentation build - ERROR: {e}")
            all_passed = False
    
    # Summary
    print("\n" + "="*50)
    if all_passed:
        print("✅ All checks PASSED! Ready to push to GitHub.")
    else:
        print("❌ Some checks FAILED. Please fix before pushing.")
        sys.exit(1)


if __name__ == "__main__":
    main()
