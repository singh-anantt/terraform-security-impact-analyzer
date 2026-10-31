
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from iam_extractor import extract_iam_actions
from trust_graph import extract_trust_edges, compare_trust_edges


def main():
    old_actions = extract_iam_actions("fixtures/v1/main.tf")
    new_actions = extract_iam_actions("fixtures/v2/main.tf")

    old_trust = extract_trust_edges("fixtures/v1/roles.tf")
    new_trust = extract_trust_edges("fixtures/v2/roles.tf")

    # The harmless.tf file contains no IAM resources.
    # It should not add IAM actions or trust relationships.
    harmless_actions = extract_iam_actions("fixtures/v2/harmless.tf")
    harmless_trust = extract_trust_edges("fixtures/v2/harmless.tf")

    assert harmless_actions == set()
    assert harmless_trust == set()

    print("Harmless file IAM actions:", sorted(harmless_actions))
    print("Harmless file trust edges:", sorted(harmless_trust))
    print("PASS: Harmless file introduces no IAM actions or trust edges.")

    print("\nExisting upgrade changes (for reference):")
    print("Added IAM actions:", sorted(new_actions - old_actions))
    changes = compare_trust_edges(old_trust, new_trust)
    print("Added trust relationships:", changes["added"])


if __name__ == "__main__":
    main()
