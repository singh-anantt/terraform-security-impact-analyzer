import re
import hcl2


def extract_iam_actions(file_path):
    with open(file_path, "r") as file:
        data = hcl2.load(file)

    actions = set()

    for resource in data.get("resource", []):
        for resource_type, instances in resource.items():
            if resource_type.strip('"') != "aws_iam_policy":
                continue

            for config in instances.values():
                policy = config.get("policy", "")

                if isinstance(policy, list):
                    policy = " ".join(str(item) for item in policy)

                if not isinstance(policy, str):
                    continue

                match = re.search(
                    r"'Action'\s*:\s*\[(.*?)\]",
                    policy,
                    re.DOTALL
                )

                if match:
                    matches = re.findall(
                        r"'([^']+:[^']+)'",
                        match.group(1)
                    )
                    actions.update(matches)

    return actions


if __name__ == "__main__":
    old_actions = extract_iam_actions("fixtures/v1/main.tf")
    new_actions = extract_iam_actions("fixtures/v2/main.tf")

    print("Old IAM actions:", sorted(old_actions))
    print("New IAM actions:", sorted(new_actions))
    print("Added IAM actions:", sorted(new_actions - old_actions))
    print("Removed IAM actions:", sorted(old_actions - new_actions))             
                           
