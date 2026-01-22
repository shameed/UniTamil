import sys
import os
import pytest

# Add src to the beginning of the python path
src_path = os.path.abspath("src")
print(f"Adding {src_path} to sys.path")
sys.path.insert(0, src_path)

if __name__ == "__main__":
    sys.exit(pytest.main(["tests", "-v"]))
