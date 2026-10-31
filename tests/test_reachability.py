
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from graph_builder import find_path, compare_graphs


def test_new_path():
    # Before upgrade: Developer cannot reach AdminAccess.
    old_graph = [
        ("Developer", "ReadOnlyRole"),
        ("ReadOnlyRole", "ReadS3"),
    ]

    # After upgrade: a new route appears.
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

    print("Before upgrade:", old_path)
    print("After upgrade:", " -> ".join(new_path))
    print("Result: NEW REACHABLE PATH")


if __name__ == "__main__":
    test_new_path()
