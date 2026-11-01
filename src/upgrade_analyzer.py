
from pathlib import Path
import argparse
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from directory_analyzer import analyze_directory
from regression_detector import resource_map, compare_resource_scopes
from upgrade_risk_comparator import compare_upgrade


def main():
    parser = argparse.ArgumentParser(
        description="Compare Terraform upgrade security changes."
    )
    parser.add_argument("--old", default="fixtures/v1", help="Old Terraform directory")
    parser.add_argument("--new", default="fixtures/v2", help="New Terraform directory")
    args = parser.parse_args()

    old_dir = (ROOT / args.old).resolve()
    new_dir = (ROOT / args.new).resolve()

    if not old_dir.is_dir() or not new_dir.is_dir():
        parser.error("Both --old and --new must point to existing directories")

    old_actions, old_trust = analyze_directory(old_dir)
    new_actions, new_trust = analyze_directory(new_dir)

    print("=" * 55)
    print(" CONSOLIDATED TERRAFORM UPGRADE SECURITY REPORT")
    print("=" * 55)

    print("\n[1] IAM action changes")
    print("Added:", sorted(new_actions - old_actions))
    print("Removed:", sorted(old_actions - new_actions))

    print("\n[2] Trust relationship changes")
    print("Added:", sorted(new_trust - old_trust))
    print("Removed:", sorted(old_trust - new_trust))

    print("\n[3] Resource-level IAM changes")
    old_resources = resource_map(old_dir)
    new_resources = resource_map(new_dir)

    changes_found = False

    for key in sorted(set(old_resources) | set(new_resources)):
        old_record = old_resources.get(key)
        new_record = new_resources.get(key)

        old_set = old_record["actions"] if old_record else set()
        new_set = new_record["actions"] if new_record else set()

        added = sorted(new_set - old_set)
        removed = sorted(old_set - new_set)

        if added or removed:
            changes_found = True
            print(f"Resource: {key[0]}.{key[1]}")
            print("  Added actions:", added)
            print("  Removed actions:", removed)

            evidence = new_record or old_record
            print("  Evidence file:", evidence["file"])

            for statement in (new_record or {}).get("statements", []):
                if set(statement.get("actions", [])) & set(added):
                    print("  Resource scope:", statement.get("resource"))
                    print("  Condition present:", statement.get("condition_present"))

        scope_changes = compare_resource_scopes(old_record, new_record)

        for change in scope_changes:
            changes_found = True
            print(f"Resource: {key[0]}.{key[1]}")
            print("  Change:", change["change_type"])
            print("  Actions:", change["actions"])
            print("  Old Resource:", change["old_resource"])
            print("  New Resource:", change["new_resource"])

    if not changes_found:
        print("No resource-level IAM changes detected.")

    print("\n[4] Policy-version risk comparison")
    risk_result = compare_upgrade(old_dir, new_dir)

    for category in ("introduced", "removed", "unchanged"):
        print(f"{category.title()} findings:")

        if not risk_result[category]:
            print("  None")

        for finding in risk_result[category]:
            print(
                f"  Role: {finding['role']}, "
                f"Policy: {finding['policy']}, "
                f"Finding: {finding['finding']}"
            )

    print("\n[Limitations]")
    print("- Findings are static-analysis candidates, not proof of exploitability.")
    print("- Policy parsing supports only the documented simple fixture format.")
    print("- Policy-version risk uses a heuristic rule.")
    print("- Attack-path graph tests use synthetic fixtures.")


if __name__ == "__main__":
    main()

