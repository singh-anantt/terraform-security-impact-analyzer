from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from graph_builder import compare_graphs, find_path


def test_new_escalation_path():
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

    assert old_path is None
    assert new_path == ["Developer", "AdminRole", "AdminAccess"]

    result = compare_graphs(old_graph, new_graph)
    assert ("Developer", "AdminRole") in result["added_edges"]
    assert ("AdminRole", "AdminAccess") in result["added_edges"]


def test_existing_path_is_not_new():
    old_graph = [
        ("Developer", "AdminRole"),
        ("AdminRole", "AdminAccess"),
    ]

    new_graph = old_graph + [
        ("Developer", "ReadOnlyRole"),
    ]

    old_path = find_path(old_graph, "Developer", "AdminAccess")
    new_path = find_path(new_graph, "Developer", "AdminAccess")

    assert old_path == new_path
    assert find_path(old_graph, "Developer", "AdminAccess") is not None
def test_harmless_graph_change_does_not_create_admin_path():
    old_graph = [("Developer", "ReadOnlyRole")]
    new_graph = old_graph + [("Auditor", "ReadOnlyRole")]

    assert find_path(old_graph, "Developer", "AdminAccess") is None
    assert find_path(new_graph, "Developer", "AdminAccess") is None


def test_removed_admin_path_is_no_longer_reachable():
    old_graph = [
        ("Developer", "AdminRole"),
        ("AdminRole", "AdminAccess"),
    ]
    new_graph = [("Developer", "ReadOnlyRole")]

    assert find_path(old_graph, "Developer", "AdminAccess") is not None
    assert find_path(new_graph, "Developer", "AdminAccess") is None

    result = compare_graphs(old_graph, new_graph)
    assert ("Developer", "AdminRole") in result["removed_edges"]
    assert ("AdminRole", "AdminAccess") in result["removed_edges"]


if __name__ == "__main__":
    test_new_escalation_path()
    test_existing_path_is_not_new()
    print("PASS: Newly reachable path detected.")
    print("PASS: Existing path remains correctly identified.")