def permission_diff(old_actions, new_actions):
    return new_actions - old_actions


def newly_reachable(old_graph, new_graph, start, target):
    from pathlib import Path
    import sys

    root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(root / "src"))

    from graph_builder import find_path

    old_path = find_path(old_graph, start, target)
    new_path = find_path(new_graph, start, target)

    return old_path is None and new_path is not None


def main():
    old_actions = {"s3:GetObject"}
    new_actions = {"s3:GetObject", "iam:CreatePolicyVersion"}

    old_graph = [
        ("Developer", "ReadOnlyRole"),
    ]

    new_graph = old_graph + [
        ("Developer", "AdminRole"),
        ("AdminRole", "AdminAccess"),
    ]

    baseline_result = permission_diff(old_actions, new_actions)
    graph_result = newly_reachable(
        old_graph,
        new_graph,
        "Developer",
        "AdminAccess",
    )

    print("=== Baseline vs Graph Analysis ===")
    print("Baseline — added permissions:", sorted(baseline_result))
    print("Graph analysis — newly reachable admin path:", graph_result)

    assert baseline_result == {"iam:CreatePolicyVersion"}
    assert graph_result is True

    print("\nPASS: Both approaches detect their respective change types.")


if __name__ == "__main__":
    main()