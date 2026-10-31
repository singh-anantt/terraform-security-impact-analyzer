from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from iam_extractor import extract_iam_actions
from trust_graph import extract_trust_edges, compare_trust_edges


def main():
    baseline = ROOT / "fixtures" / "v1"
    upgraded = ROOT / "fixtures" / "v2"

    old_actions = extract_iam_actions(str(baseline / "main.tf"))
    new_actions = extract_iam_actions(str(upgraded / "main.tf"))

    old_trust = extract_trust_edges(str(baseline / "roles.tf"))
    new_trust = extract_trust_edges(str(upgraded / "roles.tf"))

    added_actions = new_actions - old_actions
    removed_actions = old_actions - new_actions
    trust_changes = compare_trust_edges(old_trust, new_trust)

    checks = [
        (
            "Detect added IAM action",
            "iam:CreatePolicyVersion" in added_actions,
        ),
        (
            "Preserve existing S3 permission",
            "s3:GetObject" in new_actions and "s3:GetObject" not in removed_actions,
        ),
        (
            "Detect added trust relationship",
            (
                "arn:aws:iam::111122223333:role/admin-role",
                "role:app-role",
            ) in trust_changes["added"],
        ),
        (
            "Detect removed trust relationship",
            (
                "arn:aws:iam::111122223333:user/developer",
                "role:app-role",
            ) in trust_changes["removed"],
        ),
    ]

    passed = 0

    for name, result in checks:
        print(f"{'PASS' if result else 'FAIL'}: {name}")
        passed += bool(result)

    print(f"\nResults: {passed}/{len(checks)} checks passed.")

    if passed != len(checks):
        raise SystemExit(1)


if __name__ == "__main__":
    main()