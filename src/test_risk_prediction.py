from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from risk_prediction import predict_introduced_policy_risk

TESTS = [
    ("E03 risk introduced", "risk_v1", "risk_v2", True),
    ("Harmless change", "harmless_v1", "harmless_v2", False),
    ("Risk removed", "removal_v1", "removal_v2", False),
]

def main():
    passed = 0

    for name, old_name, new_name, expected in TESTS:
        old_dir = ROOT / "fixtures" / old_name
        new_dir = ROOT / "fixtures" / new_name
        predicted = predict_introduced_policy_risk(old_dir, new_dir)
        result = predicted == expected
        passed += result

        print(
            f"{name}: expected={expected}, predicted={predicted}, "
            f"{'PASS' if result else 'FAIL'}"
        )

    print(f"\nPassed: {passed}/{len(TESTS)}")
    return 0 if passed == len(TESTS) else 1

if __name__ == "__main__":
    sys.exit(main())
