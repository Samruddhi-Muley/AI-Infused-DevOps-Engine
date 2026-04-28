# test_pipeline.py

def run_tests():
    print("Starting test suite...")
    print("Importing required packages...")

    import fake_package_that_does_not_exist  # This will always fail

    print("All tests passed!")


if __name__ == "__main__":
    run_tests()