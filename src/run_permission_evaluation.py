import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from iam_extractor import extract_iam_actions
from trust_graph import extract_trust_edges, compare_trust_edges
from graph_builder import find_path, compare_graphs
from risk_prediction import predict_introduced_policy_risk
from policy_version_checker import check_policy_version_risk
from regression_detector import resource_map, compare_resource_scopes

DATASET = ROOT / "evaluation_dataset.csv"


def load_graph(file_path):
    edges = []

    with open(file_path, encoding="utf-8") as file:
        for line in file:
            line = line.strip()

            if " -> " in line:
                source, destination = line.split(" -> ", 1)
                edges.append((source.strip(), destination.strip()))

    return edges


def check_expected_change(detected, expected):
    """Compare a detected change with the dataset's expected value."""
    return detected == (expected.strip().upper() == "TRUE")


def main():
    with open(DATASET, newline="", encoding="utf-8") as file:
        scenarios = list(csv.DictReader(file))

    fixture_map = {
        "E01": ("evaluation/harmless", "evaluation/harmless_v2"),
        "E02": ("evaluation/permission_v1", "evaluation/permission_v2"),
        "E03": ("risk_v1", "risk_v2"),
        "E04": ("evaluation/trust_v1", "evaluation/trust_v2"),
        "E07": ("evaluation/removal_v1", "evaluation/removal_v2"),
        "E09": (
            "evaluation/split_policy_v1",
            "evaluation/split_policy_v2",
        ),
    }

    graph_map = {
        "E05": (
            "evaluation/graph_v1/graph.txt",
            "evaluation/graph_v2/graph.txt",
        ),
        "E06": (
            "evaluation/existing_path_v1/graph.txt",
            "evaluation/existing_path_v2/graph.txt",
        ),
    }

    evaluated = 0
    passed = 0
    failed = 0

    print("=== Terraform Upgrade Evaluation ===")

    for scenario in scenarios:
        scenario_id = scenario["scenario_id"]
        scenario_name = scenario["scenario_name"]

        print(f"\n{scenario_id}: {scenario_name}")

        # E05 and E06: Graph-based scenarios
        if scenario_id in graph_map:
            old_rel, new_rel = graph_map[scenario_id]
            old_file = ROOT / "fixtures" / old_rel
            new_file = ROOT / "fixtures" / new_rel

            if not old_file.is_file() or not new_file.is_file():
                print("  PENDING: graph fixture missing")
                continue

            old_graph = load_graph(old_file)
            new_graph = load_graph(new_file)

            old_path = find_path(old_graph, "Developer", "AdminAccess")
            new_path = find_path(new_graph, "Developer", "AdminAccess")
            changes = compare_graphs(old_graph, new_graph)

            is_new_path = old_path is None and new_path is not None

            print("  Old admin path:", old_path)
            print("  New admin path:", new_path)
            print("  Added edges:", changes["added_edges"])
            print("  New admin path detected:", is_new_path)

            expected_new_risk = (
                scenario["expected_new_risk"].strip().upper() == "TRUE"
            )

            result = is_new_path == expected_new_risk

            print("  Expected new risk:", expected_new_risk)
            print("  Scenario result:", "PASS" if result else "FAIL")

            passed += int(result)
            failed += int(not result)
            evaluated += 1
            continue

        # E10: Resource-scope expansion
        if scenario_id == "E10":
            old_dir = ROOT / "fixtures" / "resource_scope_v1"
            new_dir = ROOT / "fixtures" / "resource_scope_v2"

            if not old_dir.is_dir() or not new_dir.is_dir():
                print("  PENDING: resource-scope fixture directory missing")
                continue

            old_resources = resource_map(old_dir)
            new_resources = resource_map(new_dir)

            scope_changes = []

            for key in sorted(set(old_resources) | set(new_resources)):
                scope_changes.extend(
                    compare_resource_scopes(
                        old_resources.get(key),
                        new_resources.get(key),
                    )
                )

            scope_expansion_detected = any(
                item["change_type"] == "POTENTIAL SCOPE EXPANSION"
                for item in scope_changes
            )

            expected_risk = (
                scenario["expected_new_risk"].strip().upper() == "TRUE"
            )

            result = scope_expansion_detected == expected_risk

            print("  Resource-scope changes:", scope_changes)
            print("  Potential scope expansion detected:", scope_expansion_detected)
            print("  Expected new risk:", expected_risk)
            print("  Resource-scope check:", "PASS" if result else "FAIL")

            passed += int(result)
            failed += int(not result)
            evaluated += 1
            continue

        # E11: Harmless IAM policy tag change
        if scenario_id == "E11":
            old_file = ROOT / "fixtures" / "evaluation" / "E11_v1" / "main.tf"
            new_file = ROOT / "fixtures" / "evaluation" / "E11_v2" / "main.tf"

            if not old_file.is_file() or not new_file.is_file():
                print("  PENDING: E11 fixture file missing")
                continue

            old_actions = extract_iam_actions(str(old_file))
            new_actions = extract_iam_actions(str(new_file))

            old_resources = resource_map(old_file.parent)
            new_resources = resource_map(new_file.parent)

            action_changed = old_actions != new_actions

            scope_changes = []

            for key in sorted(set(old_resources) | set(new_resources)):
                scope_changes.extend(
                    compare_resource_scopes(
                        old_resources.get(key),
                        new_resources.get(key),
                    )
                )

            authorization_change_detected = (
                action_changed or bool(scope_changes)
            )

            expected_risk = (
                scenario["expected_new_risk"].strip().upper() == "TRUE"
            )

            expected_permission = (
                scenario["expected_permission_change"].strip().upper()
                == "TRUE"
            )

            risk_check = authorization_change_detected == expected_risk
            permission_check = action_changed == expected_permission

            print("  IAM action change detected:", action_changed)
            print("  Resource-scope changes:", scope_changes)
            print("  Authorization change detected:", authorization_change_detected)
            print("  Expected new risk:", expected_risk)
            print("  Harmless-change check:", "PASS" if risk_check else "FAIL")
            print("  Permission-change check:", "PASS" if permission_check else "FAIL")

            passed += int(risk_check) + int(permission_check)
            failed += int(not risk_check) + int(not permission_check)
            evaluated += 1
            continue

        # E08: Combined permission and trust changes
        if scenario_id == "E08":
            old_dir = ROOT / "fixtures/evaluation/combined_v1"
            new_dir = ROOT / "fixtures/evaluation/combined_v2"

            old_main = old_dir / "main.tf"
            new_main = new_dir / "main.tf"
            old_roles = old_dir / "roles.tf"
            new_roles = new_dir / "roles.tf"

            if not all(
                p.is_file()
                for p in (old_main, new_main, old_roles, new_roles)
            ):
                print("  PENDING: combined fixture file missing")
                continue

            old_actions = extract_iam_actions(str(old_main))
            new_actions = extract_iam_actions(str(new_main))
            old_trust = extract_trust_edges(str(old_roles))
            new_trust = extract_trust_edges(str(new_roles))

            added_actions = new_actions - old_actions
            removed_actions = old_actions - new_actions
            trust_changes = compare_trust_edges(old_trust, new_trust)

            permission_changed = bool(added_actions or removed_actions)
            trust_changed = bool(
                trust_changes["added"] or trust_changes["removed"]
            )

            expected_permission = (
                scenario["expected_permission_change"].strip().upper()
                == "TRUE"
            )

            expected_trust = (
                scenario["expected_trust_change"].strip().upper() == "TRUE"
            )

            print("  Added actions:", sorted(added_actions))
            print("  Removed actions:", sorted(removed_actions))
            print("  Added trust relationships:", trust_changes["added"])
            print("  Removed trust relationships:", trust_changes["removed"])

            permission_check = permission_changed == expected_permission
            trust_check = trust_changed == expected_trust

            print(
                "  Permission-change check:",
                "PASS" if permission_check else "FAIL",
            )
            print("  Trust-change check:", "PASS" if trust_check else "FAIL")

            passed += int(permission_check) + int(trust_check)
            failed += int(not permission_check) + int(not trust_check)

            evaluated += 1
            continue

        # Remaining scenarios
        if scenario_id not in fixture_map:
            print("  PENDING: fixtures not yet mapped")
            continue

        old_name, new_name = fixture_map[scenario_id]

        if scenario_id == "E04":
            old_file = ROOT / "fixtures" / old_name / "roles.tf"
            new_file = ROOT / "fixtures" / new_name / "roles.tf"
        else:
            old_file = ROOT / "fixtures" / old_name / "main.tf"
            new_file = ROOT / "fixtures" / new_name / "main.tf"

        if not old_file.is_file() or not new_file.is_file():
            print("  PENDING: fixture file missing")
            continue

        expected_permission = (
            scenario["expected_permission_change"].strip().upper()
            == "TRUE"
        )

        expected_trust = (
            scenario["expected_trust_change"].strip().upper() == "TRUE"
        )

        if scenario_id == "E04":
            old_trust = extract_trust_edges(str(old_file))
            new_trust = extract_trust_edges(str(new_file))
            changes = compare_trust_edges(old_trust, new_trust)

            trust_changed = bool(
                changes["added"] or changes["removed"]
            )

            print("  Added trust relationships:", changes["added"])
            print("  Removed trust relationships:", changes["removed"])

            trust_check = check_expected_change(
                trust_changed, scenario["expected_trust_change"]
            )

            print(
                "  Trust-change check:",
                "PASS" if trust_check else "FAIL",
            )
            print(
                "  Permission-change check: N/A "
                "(not checked for this scenario)"
            )

            passed += int(trust_check)
            failed += int(not trust_check)

        else:
            old_actions = extract_iam_actions(str(old_file))
            new_actions = extract_iam_actions(str(new_file))

            added_actions = new_actions - old_actions
            removed_actions = old_actions - new_actions
            permission_changed = bool(added_actions or removed_actions)

            print("  Added actions:", sorted(added_actions))
            print("  Removed actions:", sorted(removed_actions))

            permission_check = check_expected_change(
                permission_changed,
                scenario["expected_permission_change"],
            )

            print(
                "  Permission-change check:",
                "PASS" if permission_check else "FAIL",
            )

            passed += int(permission_check)
            failed += int(not permission_check)

            if scenario_id == "E03":
                risk_prediction = predict_introduced_policy_risk(
                    ROOT / "fixtures" / "risk_v1",
                    ROOT / "fixtures" / "risk_v2",
                )

                expected_risk = (
                    scenario["expected_new_risk"].strip().upper() == "TRUE"
                )

                risk_check = risk_prediction == expected_risk

                print("  Policy-version risk predicted:", risk_prediction)
                print(
                    "  Policy-risk check:",
                    "PASS" if risk_check else "FAIL",
                )

                passed += int(risk_check)
                failed += int(not risk_check)

            elif scenario_id == "E09":
                old_dir = (
                    ROOT / "fixtures" / "evaluation" / "split_policy_v1"
                )
                new_dir = (
                    ROOT / "fixtures" / "evaluation" / "split_policy_v2"
                )

                old_findings = check_policy_version_risk(old_dir)
                new_findings = check_policy_version_risk(new_dir)

                old_keys = {
                    (item["role"], item["finding"])
                    for item in old_findings
                }

                new_keys = {
                    (item["role"], item["finding"])
                    for item in new_findings
                }

                risk_prediction = bool(new_keys - old_keys)

                expected_risk = (
                    scenario["expected_new_risk"].strip().upper() == "TRUE"
                )

                risk_check = risk_prediction == expected_risk

                print("  Old-version findings:", old_findings)
                print("  New-version findings:", new_findings)
                print("  Split-policy risk predicted:", risk_prediction)
                print(
                    "  Split-policy risk check:",
                    "PASS" if risk_check else "FAIL",
                )

                passed += int(risk_check)
                failed += int(not risk_check)

            print(
                "  Trust-change check: N/A "
                "(not checked for this scenario)"
            )

        evaluated += 1

    print(f"\nScenarios evaluated: {evaluated}/{len(scenarios)}")
    print(f"Checks passed: {passed}")
    print(f"Checks failed: {failed}")
    print("E05/E06 use synthetic graph fixtures, not Terraform-derived graphs.")
    print(
        "PASS/FAIL checks cover implemented permission, trust, "
        "policy-version, resource-scope, harmless-change, "
        "and graph-fixture scenarios."
    )
    print("Overall accuracy, precision, and recall are not calculated.")


if __name__ == "__main__":
    main()
