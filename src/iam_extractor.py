
import re
from pathlib import Path
import hcl2


def extract_iam_actions(file_path):
    with open(file_path, "r") as file:
        data = hcl2.load(file)

    actions = set()

    for resource in data.get("resource", []):
        for resource_type, instances in resource.items():
            if resource_type.strip('"') != "aws_iam_policy":
                continue

            for resource_name, config in instances.items():
                policy = config.get("policy", "")

                # Handle policy values returned as strings or dictionaries
                if isinstance(policy, str):
                    matches = re.findall(r'"([^"]+:[^"]+)"', policy)
                    actions.update(
                        action for action in matches
                        if not action.startswith("${")
                    )
                elif isinstance(policy, (dict, list)):
                    text = str(policy)
                    matches = re.findall(r'["\']([^"\']+:[^"\']+)["\']', text)
                    actions.update(
                        action for action in matches
                        if not action.startswith("${")
                    )

    return actions


if __name__ == "__main__":
    old_actions = extract_iam_actions("fixtures/v1/main.tf")
    new_actions = extract_iam_actions("fixtures/v2/main.tf")

    print("Old IAM actions:", sorted(old_actions))
    print("New IAM actions:", sorted(new_actions))
    print("Added IAM actions:", sorted(new_actions - old_actions))
    print("Removed IAM actions:", sorted(old_actions - new_actions))
