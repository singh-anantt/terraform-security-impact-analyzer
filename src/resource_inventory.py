
from pathlib import Path
import hcl2


def inspect_directory(directory):
    records = []

    for file_path in sorted(Path(directory).rglob("*.tf")):
        with open(file_path, "r") as file:
            data = hcl2.load(file)

        for resource in data.get("resource", []):
            for resource_type, instances in resource.items():
                resource_type = resource_type.strip('"')

                for label, config in instances.items():
                    label = label.strip('"')

                    if resource_type in {
                        "aws_iam_policy",
                        "aws_iam_role",
                        "aws_iam_role_policy_attachment",
                    }:
                        records.append({
                            "file": str(file_path),
                            "type": resource_type,
                            "label": label,
                            "name": config.get("name", "").strip('"'),
                            "has_policy": "policy" in config,
                            "has_trust_policy": (
                                "assume_role_policy" in config
                            ),
                            "role": str(config.get("role", "")),
                            "policy_arn": str(
                                config.get("policy_arn", "")
                            ),
                        })

    return records


if __name__ == "__main__":
    for version in ["fixtures/v1", "fixtures/v2"]:
        print(f"\n=== {version} ===")

        for record in inspect_directory(version):
            print(record)
