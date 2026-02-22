"""
Test runner for week2 tests.

Runs pytest from the correct parent directory so that relative imports
(e.g. `from ..app.services.extract`) and patch paths
(e.g. `week2.app.services.extract.chat`) resolve properly.
"""

import sys
import os

# Ensure the parent of week2/ is on sys.path so `week2` is importable as a package
WEEK2_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(WEEK2_DIR)

if PARENT_DIR not in sys.path:
    sys.path.insert(0, PARENT_DIR)

import pytest

if __name__ == "__main__":
    exit_code = pytest.main([
        os.path.join(WEEK2_DIR, "tests", "test_extract.py"),
        "-v",           # verbose: show each test name + PASSED/FAILED
        "--tb=short",   # shorter tracebacks on failure
    ])
    sys.exit(exit_code)
