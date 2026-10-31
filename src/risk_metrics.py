
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from risk_prediction import predict_introduced_policy_risk


TESTS = [
    {
        "name": "Policy-version risk introduced",
        "old": "risk_v1",
        "new": "risk_v2",
        "expected": True,
    },
    {
        "name": "Harmless variable addition",
        "old": "harmless_v1",
        "new": "harmless_v2",
        "expected": False,
    },
    {
        "name": "Risk removed",
        "old": "removal_v1",
        "new": "removal_v2",
        "expected": False,
    },
    {
        "name": "Permission-only upgrade",
        "old": "evaluation/permission_v1",
        "new": "evaluation/permission_v2",
        "expected": False,
    },
    {
        "name": "Risk introduced across split attached policies",
        "old": "evaluation/split_policy_v1",
        "new": "evaluation/split_policy_v2",
        "expected": True,
    },
]


def main():
    tp = fp = fn = tn = 0

    print("=== Risk Prediction Metrics ===")

    for test in TESTS:
        old_dir = ROOT / "fixtures" / test["old"]
        new_dir = ROOT / "fixtures" / test["new"]

        expected = test["expected"]
        predicted = predict_introduced_policy_risk(old_dir, new_dir)

        if expected and predicted:
            tp += 1
        elif not expected and predicted:
            fp += 1
        elif expected and not predicted:
            fn += 1
        else:
            tn += 1

        status = "PASS" if expected == predicted else "FAIL"

        print(
            f'{test["name"]}: expected={expected}, '
            f'predicted={predicted}, {status}'
        )

    total = tp + fp + fn + tn

    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    accuracy = (tp + tn) / total if total else 0.0
    f1 = (
        2 * precision * recall / (precision + recall)
        if (precision + recall)
        else 0.0
    )

    print("\nConfusion Matrix Counts")
    print(f"TP={tp}, FP={fp}, FN={fn}, TN={tn}")
    print(f"Accuracy:  {accuracy:.3f}")
    print(f"Precision: {precision:.3f}")
    print(f"Recall:    {recall:.3f}")
    print(f"F1-score:  {f1:.3f}")
    print(f"Test cases: {total}")
    print("Note: preliminary results on five controlled fixture pairs only.")

    if tp + fp + fn + tn != len(TESTS):
        raise RuntimeError("Metric counts do not match the number of test cases.")


if __name__ == "__main__":
    main()

