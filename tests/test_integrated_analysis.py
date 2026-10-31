from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from iam_extractor import extract_iam_actions
from trust_graph import extract_trust_edges, compare_trust_edges


def main():
    old_actions = extract_iam_actions("fixtures/v1/main.tf")
    new_actions = extract_iam_actions("fixtures/v2/main.tf")

    old_trust = extract_trust_edges("fixtures/v1/roles.tf")
    new_trust = extract_trust_edges("fixtures/v2/roles.tf")

    print("=== Integrated Terraform Upgrade Analysis ===")

    print("\nAdded IAM actions:")
    for action in sorted(new_actions - old_actions):
        print(" ", action)

    print("\nRemoved IAM actions:")
    for action in sorted(old_actions - new_actions):
        print(" ", action)

    changes = compare_trust_edges(old_trust, new_trust)

    print("\nAdded trust relationships:")
    for source, target in changes["added"]:
        print(f"  {source} -> {target}")

    print("\nRemoved trust relationships:")
    for source, target in changes["removed"]:
        print(f"  {source} -> {target}")


if __name__ == "__main__":
    main()