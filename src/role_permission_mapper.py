
from pathlib import Path
import re
import sys
import hcl2

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from resource_action_extractor import extract_resource_actions


def load_resources(directory):
    resources = {}

    for file_path in sorted(Path(directory).rglob("*.tf")):
        with open(file_path, "r") as file:
            data = hcl2.load(file)

        for resource in data.get("resource", []):
            for resource_type, instances in resource.items():
                resource_type = resource_type.strip('"')

                for label, config in instances.items():
                    resources[(resource_type, label.strip('"'))] = {
                        "config": config,
                        "file": str(file_path),
                    }

    return resources


def map_role_policy_actions(directory):
    resources = load_resources(directory)
    action_records = extract_resource_actions(directory)

    actions_by_policy = {
        (record["resource_type"], record["resource_label"]): {
            action
            for statement in record["statements"]
            if statement["effect"] == "Allow"
            for action in statement["actions"]
        }
        for record in action_records
    }

    mappings = []

    for (resource_type, label), resource in resources.items():
        if resource_type != "aws_iam_role_policy_attachment":
            continue

        config = resource["config"]
        role_ref = str(config.get("role", ""))
        policy_ref = str(config.get("policy_arn", ""))

        role_match = re.search(
            r"aws_iam_role\.([A-Za-z0-9_-]+)", role_ref
        )
        policy_match = re.search(
            r"aws_iam_policy\.([A-Za-z0-9_-]+)", policy_ref
        )

        if not role_match or not policy_match:
            continue

        role_label = role_match.group(1)
        policy_label = policy_match.group(1)
        policy_key = ("aws_iam_policy", policy_label)

        mappings.append({
            "role": role_label,
            "policy": policy_label,
            "actions": sorted(actions_by_policy.get(policy_key, set())),
            "attachment": label,
            "file": resource["file"],
        })

    return mappings


def map_role_permissions(directory):
    permissions = {}

    for mapping in map_role_policy_actions(directory):
        permissions.setdefault(mapping["role"], set()).update(
            mapping["actions"]
        )

    return permissions


if __name__ == "__main__":
    for version in ["fixtures/v1", "fixtures/v2"]:
        print(f"\n=== {version}: role-policy mappings ===")

        for mapping in map_role_policy_actions(version):
            print(mapping)
