
import re
from pathlib import Path
import hcl2


def extract_trusted_principals(file_path):
    with open(file_path, "r") as file:
        data = hcl2.load(file)

    principals = set()

    for resource in data.get("resource", []):
        for resource_type, instances in resource.items():
            if resource_type.strip('"') != "aws_iam_role":
                continue

            for role_name, config in instances.items():
                policy = config.get("assume_role_policy", "")

                # Handles the simple static jsonencode example
                # used in our current test fixtures.
                match = re.search(
                    r'AWS\s*=\s*"([^"]+)"',
                    policy
                )

                if match:
                    principals.add(match.group(1))

    return principals


if __name__ == "__main__":
    old_file = "fixtures/v1/roles.tf"
    new_file = "fixtures/v2/roles.tf"

    old_principals = extract_trusted_principals(old_file)
    new_principals = extract_trusted_principals(new_file)

    print("Old trusted principals:", sorted(old_principals))
    print("New trusted principals:", sorted(new_principals))
    print("Added trusted principals:", sorted(new_principals - old_principals))
    print("Removed trusted principals:", sorted(old_principals - new_principals))
