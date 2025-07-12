#!/usr/bin/env python3
"""
Release preparation script.

This script helps prepare a new release by:
1. Checking that all tests pass
2. Validating version consistency
3. Building and testing the package
4. Providing release instructions
"""

import re
import subprocess
import sys
from pathlib import Path

# Get the project root directory
project_root = Path(__file__).parent.parent


def get_version_from_file(file_path, pattern):
    """Extract version from a file using regex pattern."""
    try:
        content = file_path.read_text(encoding='utf-8')
        match = re.search(pattern, content)
        if match:
            return match.group(1)
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
    return None


def main():
    """Prepare for release."""
    print("🚀 Preparing for release...")
    
    # Check version consistency
    pyproject_file = project_root / "pyproject.toml"
    init_file = project_root / "swimrankings" / "__init__.py"
    
    pyproject_version = get_version_from_file(
        pyproject_file, 
        r'version\s*=\s*["\']([^"\']+)["\']'
    )
    init_version = get_version_from_file(
        init_file, 
        r'__version__\s*=\s*["\']([^"\']+)["\']'
    )
    
    print(f"📦 Version in pyproject.toml: {pyproject_version}")
    print(f"📦 Version in __init__.py: {init_version}")
    
    if pyproject_version != init_version:
        print("❌ Version mismatch! Please update both files to the same version.")
        sys.exit(1)
    
    current_version = pyproject_version
    print(f"✅ Version consistency check passed: {current_version}")
    
    # Run tests
    print("\n🧪 Running tests...")
    result = subprocess.run(
        ["python", "-m", "pytest", "--cov=swimrankings"],
        cwd=project_root
    )
    
    if result.returncode != 0:
        print("❌ Tests failed! Please fix before releasing.")
        sys.exit(1)
    
    print("✅ All tests passed!")
    
    # Build package
    print("\n📦 Building package...")
    result = subprocess.run(
        ["python", "-m", "build"],
        cwd=project_root
    )
    
    if result.returncode != 0:
        print("❌ Package build failed!")
        sys.exit(1)
    
    # Check package
    print("\n🔍 Validating package...")
    result = subprocess.run(
        ["python", "-m", "twine", "check", "dist/*"],
        cwd=project_root
    )
    
    if result.returncode != 0:
        print("❌ Package validation failed!")
        sys.exit(1)
    
    print("✅ Package validation passed!")
    
    # Release instructions
    print(f"\n🎉 Ready to release version {current_version}!")
    print("\nTo create the release:")
    print(f"1. git tag v{current_version}")
    print(f"2. git push origin v{current_version}")
    print("3. Create a GitHub release with tag v{} on GitHub".format(current_version))
    print("4. The GitHub Actions will automatically:")
    print("   - Build the package")
    print("   - Test on Test PyPI")
    print("   - Publish to PyPI")
    print("   - Update documentation")
    
    print(f"\n📋 Or use this command:")
    print(f"git tag v{current_version} && git push origin v{current_version}")


if __name__ == "__main__":
    main()
