from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]

TEST_FILES = [
    "test_comparison.py",
    "test_end_to_end.py",
    "test_graph_regression.py",
    "test_harmless_change.py",
    "test_iam_relationships.py",
    "test_integrated_analysis.py",
    "test_policy_resource_scope.py",
    "test_policy_version_checker.py",
    "test_regression_cases.py",
    "test_role_permission_mapper.py",
    "test_upgrade_risk_scenario.py",
    "test_reachability.py",
    "test_evaluation_dataset.py",
    "test_security_evaluation.py",
    "test_baseline_comparison.py",
    "test_harmless_upgrade.py",
    "test_permission_expansion.py",
    "test_trust_upgrade.py",
]


def main():
    results = []

    for filename in TEST_FILES:
        test_path = ROOT / "tests" / filename

        if not test_path.exists():
            results.append((filename, "SKIPPED — file not found"))
            continue

        result = subprocess.run(
            [sys.executable, str(test_path)],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )

        status = "PASS" if result.returncode == 0 else "FAIL"
        results.append((filename, status))

        print(f"\n=== {filename}: {status} ===")
        if result.stdout:
            print(result.stdout.strip())
        if result.stderr:
            print(result.stderr.strip())

    print("\n=== EVALUATION SUMMARY ===")
    for filename, status in results:
        print(f"{status}: {filename}")

    passed = sum(status == "PASS" for _, status in results)
    failed = sum(status == "FAIL" for _, status in results)
    skipped = sum(status.startswith("SKIPPED") for _, status in results)

    print(f"\nPassed: {passed} | Failed: {failed} | Skipped: {skipped}")

    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()