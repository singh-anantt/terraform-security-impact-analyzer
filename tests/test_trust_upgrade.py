from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from trust_graph import extract_trust_edges, compare_trust_edges


def main():
    old_file = ROOT / "fixtures" / "evaluation" / "trust_v1" / "roles.tf"
    new_file = ROOT / "fixtures" / "evaluation" / "trust_v2" / "roles.tf"

    old_trust = extract_trust_edges(str(old_file))
    new_trust = extract_trust_edges(str(new_file))

    changes = compare_trust_edges(old_trust, new_trust)

    print("Old trust relationships:", sorted(old_trust))
    print("New trust relationships:", sorted(new_trust))
    print("Added trust relationships:", changes["added"])
    print("Removed trust relationships:", changes["removed"])

    expected_added = (
        "arn:aws:iam::111122223333:role/admin-role",
        "role:app-role",
    )
    expected_removed = (
        "arn:aws:iam::111122223333:user/developer",
        "role:app-role",
    )

    assert expected_added in changes["added"]
    assert expected_removed in changes["removed"]

    print("PASS: Trust relationship upgrade detected correctly.")


if __name__ == "__main__":
    main()