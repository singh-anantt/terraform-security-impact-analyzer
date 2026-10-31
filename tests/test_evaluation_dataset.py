from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from graph_builder import find_path, compare_graphs


def evaluate_scenario(name, old_graph, new_graph, start, target,
                      expected_new_path):
    old_path = find_path(old_graph, start, target)
    new_path = find_path(new_graph, start, target)

    actual_new_path = old_path is None and new_path is not None

    passed = actual_new_path == expected_new_path

    print(
        f"{'PASS' if passed else 'FAIL'}: {name} "
        f"(expected={expected_new_path}, actual={actual_new_path})"
    )

    return passed


def main():
    scenarios = [
        {
            "name": "Harmless graph change",
            "old": [("Developer", "ReadOnlyRole")],
            "new": [
                ("Developer", "ReadOnlyRole"),
                ("Auditor", "ReadOnlyRole"),
            ],
            "start": "Developer",
            "target": "AdminAccess",
            "expected": False,
        },
        {
            "name": "New admin path",
            "old": [("Developer", "ReadOnlyRole")],
            "new": [
                ("Developer", "ReadOnlyRole"),
                ("Developer", "AdminRole"),
                ("AdminRole", "AdminAccess"),
            ],
            "start": "Developer",
            "target": "AdminAccess",
            "expected": True,
        },
        {
            "name": "Existing admin path",
            "old": [
                ("Developer", "AdminRole"),
                ("AdminRole", "AdminAccess"),
            ],
            "new": [
                ("Developer", "AdminRole"),
                ("AdminRole", "AdminAccess"),
                ("Auditor", "ReadOnlyRole"),
            ],
            "start": "Developer",
            "target": "AdminAccess",
            "expected": False,
        },
        {
            "name": "Path removed by upgrade",
            "old": [
                ("Developer", "AdminRole"),
                ("AdminRole", "AdminAccess"),
            ],
            "new": [("Developer", "ReadOnlyRole")],
            "start": "Developer",
            "target": "AdminAccess",
            "expected": False,
        },
    ]

    passed_count = 0

    for scenario in scenarios:
        if evaluate_scenario(
            scenario["name"],
            scenario["old"],
            scenario["new"],
            scenario["start"],
            scenario["target"],
            scenario["expected"],
        ):
            passed_count += 1

    print(f"\nResults: {passed_count}/{len(scenarios)} scenarios passed.")

    if passed_count != len(scenarios):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
