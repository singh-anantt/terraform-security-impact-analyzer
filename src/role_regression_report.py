
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from role_permission_mapper import map_role_permissions


def compare_role_permissions(old_directory, new_directory):
    old_roles = map_role_permissions(str(old_directory))
    new_roles = map_role_permissions(str(new_directory))

    report = []

    for role in sorted(set(old_roles) | set(new_roles)):
        old_actions = old_roles.get(role, set())
        new_actions = new_roles.get(role, set())

        added = sorted(new_actions - old_actions)
        removed = sorted(old_actions - new_actions)

        if added or removed:
            report.append({
                "role": role,
                "added_actions": added,
                "removed_actions": removed,
            })

    return report


if __name__ == "__main__":
    old_dir = ROOT / "fixtures" / "v1"
    new_dir = ROOT / "fixtures" / "v2"

    results = compare_role_permissions(old_dir, new_dir)

    print("=== ROLE-LEVEL IAM REGRESSION REPORT ===")

    if not results:
        print("No role permission changes detected.")

    for result in results:
        print(f"\nRole: {result['role']}")
        print(f"Added actions: {result['added_actions']}")
        print(f"Removed actions: {result['removed_actions']}")

    print(
        "\nNote: Permission changes require security analysis; "
        "they do not by themselves prove privilege escalation."
    )
