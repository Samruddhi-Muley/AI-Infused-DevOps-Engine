# test_pipeline.py
# This script intentionally has an error to trigger AIDE via GitHub Actions

import sys


def run_tests():
    print("Running test suite...")
    print("Test 1: Checking environment...")

    # This will fail — numpy may not be installed on GitHub Actions runner
    import numpy as np

    print("Test 2: Checking data processing...")
    data = [1, 2, 3, 4, 5]
    result = np.mean(data)
    print(f"Mean: {result}")

    print("All tests passed!")


if __name__ == "__main__":
    run_tests()