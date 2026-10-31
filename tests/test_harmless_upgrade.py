from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from iam_extractor import extract_iam_actions
from trust_graph import extract_trust_edges, compare_trust_edges


def main():
    old_dir = ROOT / "fixtures" / "evaluation" / "harmless"
    new_dir = ROOT / "fixtures" / "evaluation" / "harmless_v2"

    old_actions = extract_iam_actions(str(old_dir / "main.tf"))
    new_actions = extract_iam_actions(str(new_dir / "main.tf"))

    old_trust = extract_trust_edges(str(old_dir / "main.tf"))
    new_trust = extract_trust_edges(str(new_dir / "main.tf"))

    added_actions = new_actions - old_actions
    removed_actions = old_actions - new_actions
    trust_changes = compare_trust_edges(old_trust, new_trust)

    print("Added IAM actions:", sorted(added_actions))
    print("Removed IAM actions:", sorted(removed_actions))
    print("Added trust relationships:", trust_changes["added"])
    print("Removed trust relationships:", trust_changes["removed"])

    assert not added_actions
    assert not removed_actions
    assert not trust_changes["added"]
    assert not trust_changes["removed"]

    print("PASS: Harmless variable addition introduces no IAM changes.")


if __name__ == "__main__":
    main()