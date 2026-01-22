import sys
import os

# Add src to path to allow imports
sys.path.append(os.path.abspath("src"))

from app.core.dependency_checker import DependencyChecker

def test_checker():
    print("Testing Dependency Checker...")
    checker = DependencyChecker()
    status = checker.get_status()
    print("Status Result:")
    for key, value in status.items():
        print(f"  {key}: {value}")

if __name__ == "__main__":
    test_checker()
