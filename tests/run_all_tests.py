#!/usr/bin/env python3
"""Run all tests for Aurora Agent."""

import sys
import subprocess
from pathlib import Path

TEST_DIR = Path(__file__).parent

def run_test_file(test_file: str) -> bool:
    """Run a single test file."""
    filepath = TEST_DIR / test_file
    if not filepath.exists():
        print(f"  [SKIP] {test_file} - file not found")
        return True
    
    print(f"\n{'='*60}")
    print(f"Running: {test_file}")
    print('='*60)
    
    result = subprocess.run(
        [sys.executable, str(filepath)],
        capture_output=False,
        text=True
    )
    return result.returncode == 0

def main():
    print("="*60)
    print("Aurora Agent - Full Test Suite")
    print("="*60)
    
    # Core module tests
    core_tests = [
        "test_agent.py",
        "test_competition.py",
        "test_business_plan.py",
        "test_evaluation.py",
        "test_presentation.py",
    ]
    
    # New module tests
    new_tests = [
        "dachuang/test_application.py",
        "finance/test_forecast.py",
        "market/test_competitor.py",
        "pptx/test_generator.py",
        "project_mgmt/test_gantt.py",
        "ip/test_patent.py",
        "visualization/test_charts.py",
    ]
    
    all_tests = core_tests + new_tests
    results = {}
    
    for test_file in all_tests:
        results[test_file] = run_test_file(test_file)
    
    # Summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_file, success in results.items():
        status = "PASS" if success else "FAIL"
        print(f"  [{status}] {test_file}")
    
    print(f"\nTotal: {passed}/{total} passed")
    
    return 0 if passed == total else 1

if __name__ == "__main__":
    sys.exit(main())
