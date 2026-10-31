
import re
from pathlib import Path
import hcl2


ACTION_PATTERN = re.compile(
    r"""['"]([A-Za-z0-9*]+:[A-Za-z0-9*]+)['"]"""
)


def extract_resource_actions(directory):
    records = []

    for file_path in sorted(Path(directory).rglob("*.tf")):
        with open(file_path, "r") as file:
            data = hcl2.load(file)

        for resource in data.get("resource", []):
            for resource_type, instances in resource.items():
                if resource_type.strip('"') != "aws_iam_policy":
                    continue

                for label, config in instances.items():
                    policy_value = config.get("policy", "")
                    if isinstance(policy_value, list):
                        policy = " ".join(map(str, policy_value))
                    else:
                        policy = str(policy_value)

                    statement_match = re.search(
                        r"""['"]Statement['"]\s*:\s*\[(.*)\]\s*\}\s*\)\s*\}*""",
                        policy,
                        re.DOTALL,
                    )

                    statements = []

                    if statement_match:
                        statement_text = statement_match.group(1)
                        blocks = re.findall(
                            r"\{([^{}]*)\}",
                            statement_text,
                            re.DOTALL,
                        )

                        for block in blocks:
                            effect_match = re.search(
                                r"""['"]Effect['"]\s*:\s*['"]([^'"]+)['"]""",
                                block,
                            )
                            resource_match = re.search(
                                r"""['"]Resource['"]\s*:\s*['"]([^'"]+)['"]""",
                                block,
                            )
                            action_match = re.search(
                                r"""['"]Action['"]\s*:\s*\[(.*?)\]""",
                                block,
                                re.DOTALL,
                            )

                            actions = (
                                sorted(set(ACTION_PATTERN.findall(
                                    action_match.group(1)
                                )))
                                if action_match else []
                            )

                            statements.append({
                                "effect": effect_match.group(1)
                                if effect_match else None,
                                "actions": actions,
                                "resource": resource_match.group(1)
                                if resource_match else None,
                                "condition_present": (
                                    re.search(
                                        r"""['"]Condition['"]\s*:""",
                                        block,
                                    ) is not None
                                ),
                            })

                    records.append({
                        "file": str(file_path),
                        "resource_type": "aws_iam_policy",
                        "resource_label": label.strip('"'),
                        "resource_name": str(
                            config.get("name", "")
                        ).strip("[]'\""),
                        "statements": statements,
                        "parser_scope": (
                            "simple jsonencode fixture parser; "
                            "not a complete IAM evaluator"
                        ),
                    })

    return records


if __name__ == "__main__":
    for version in ["fixtures/v1", "fixtures/v2"]:
        print(f"\n=== {version} ===")
        for record in extract_resource_actions(version):
            print(record)
