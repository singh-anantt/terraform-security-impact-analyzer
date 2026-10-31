
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))

from iam_extractor import extract_iam_actions
from trust_graph import extract_trust_edges


def analyze_directory(directory):
    directory = Path(directory)

    actions = set()
    trust_edges = set()

    for file_path in sorted(directory.rglob("*.tf")):
        actions.update(extract_iam_actions(str(file_path)))
        trust_edges.update(extract_trust_edges(str(file_path)))

    return actions, trust_edges


def main():
    old_actions, old_trust = analyze_directory("fixtures/v1")
    new_actions, new_trust = analyze_directory("fixtures/v2")

    print("=== DIRECTORY-LEVEL UPGRADE ANALYSIS ===")

    print("\nAdded IAM actions:")
    for action in sorted(new_actions - old_actions):
        print(" ", action)

    print("\nRemoved IAM actions:")
    for action in sorted(old_actions - new_actions):
        print(" ", action)

    print("\nAdded trust relationships:")
    for edge in sorted(new_trust - old_trust):
        print(" ", edge[0], "->", edge[1])

    print("\nRemoved trust relationships:")
    for edge in sorted(old_trust - new_trust):
        print(" ", edge[0], "->", edge[1])


if __name__ == "__main__":
    main()
