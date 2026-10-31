from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from iam_extractor import extract_iam_actions


def main():
    old_file = ROOT / "fixtures" / "evaluation" / "permission_v1" / "main.tf"
    new_file = ROOT / "fixtures" / "evaluation" / "permission_v2" / "main.tf"

    old_actions = extract_iam_actions(str(old_file))
    new_actions = extract_iam_actions(str(new_file))

    added = new_actions - old_actions
    removed = old_actions - new_actions

    print("Old IAM actions:", sorted(old_actions))
    print("New IAM actions:", sorted(new_actions))
    print("Added IAM actions:", sorted(added))
    print("Removed IAM actions:", sorted(removed))

    assert added == {"s3:PutObject"}, (
        f"Expected only s3:PutObject to be added, got {added}"
    )
    assert not removed, f"Unexpected removed actions: {removed}"

    print("PASS: Permission expansion detected correctly.")


if __name__ == "__main__":
    main()