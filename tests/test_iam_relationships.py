
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from graph_builder import compare_graphs, find_path


def test_role_trust_upgrade():
    # Simplified model: a principal can assume a role
    # only when the trust relationship permits it.
    old_graph = [
        ("Developer", "ReadOnlyRole"),
        ("ReadOnlyRole", "ReadS3"),
    ]

    new_graph = old_graph + [
        ("Developer", "AdminRole"),
        ("AdminRole", "AdminAccess"),
    ]

    old_path = find_path(old_graph, "Developer", "AdminAccess")
    new_path = find_path(new_graph, "Developer", "AdminAccess")

    changes = compare_graphs(old_graph, new_graph)

    assert old_path is None
    assert new_path is not None
    assert ("Developer", "AdminRole") in changes["added_edges"]

    print("Old path:", old_path)
    print("New path:", " -> ".join(new_path))
    print("Added trust relationship detected.")


if __name__ == "__main__":
    test_role_trust_upgrade()
