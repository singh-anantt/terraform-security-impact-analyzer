
import re
import hcl2


def extract_trust_edges(file_path):
    """Extract simple AWS principal -> trusted role relationships."""
    with open(file_path, "r", encoding="utf-8") as file:
        data = hcl2.load(file)

    edges = set()

    for resource in data.get("resource", []):
        for resource_type, instances in resource.items():
            if resource_type.strip('"') != "aws_iam_role":
                continue

            for label, config in instances.items():
                role_name = config.get("name", label)

                if isinstance(role_name, list):
                    role_name = role_name[0] if role_name else label
                if not isinstance(role_name, str):
                    role_name = label
                role_name = role_name.strip('"')

                policy = config.get("assume_role_policy", "")

                # Convert parsed HCL values into searchable text.
                if not isinstance(policy, str):
                    policy = str(policy)

                principals = re.findall(
                    r'["\']AWS["\']\s*[:=]\s*["\']([^"\']+)["\']',
                    policy
                )

                for principal in principals:
                    edges.add((principal, f"role:{role_name}"))

    return edges


def compare_trust_edges(old_edges, new_edges):
    """Return trust relationships added or removed by an upgrade."""
    return {
        "added": sorted(new_edges - old_edges),
        "removed": sorted(old_edges - new_edges),
    }


if __name__ == "__main__":
    old_edges = extract_trust_edges("fixtures/v1/roles.tf")
    new_edges = extract_trust_edges("fixtures/v2/roles.tf")

    changes = compare_trust_edges(old_edges, new_edges)

    print("Old trust relationships:")
    for source, target in sorted(old_edges):
        print(f"  {source} -> {target}")

    print("\nNew trust relationships:")
    for source, target in sorted(new_edges):
        print(f"  {source} -> {target}")

    print("\nAdded relationships:")
    for source, target in changes["added"]:
        print(f"  {source} -> {target}")

    print("\nRemoved relationships:")
    for source, target in changes["removed"]:
        print(f"  {source} -> {target}")
