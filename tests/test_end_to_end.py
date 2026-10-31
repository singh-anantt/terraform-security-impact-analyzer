
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from resource_action_extractor import extract_resource_actions
from trust_graph import extract_trust_edges


def action_map(directory):
    result = {}

    for record in extract_resource_actions(directory):
        key = (
            record["resource_type"],
            record["resource_label"],
        )
        result[key] = {
            action
            for statement in record["statements"]
            if statement["effect"] == "Allow"
            for action in statement["actions"]
        }

    return result


def test_real_fixture_comparison():
    old_actions = action_map(ROOT / "fixtures/v1")
    new_actions = action_map(ROOT / "fixtures/v2")

    key = ("aws_iam_policy", "example")

    assert key in old_actions
    assert key in new_actions
    assert old_actions[key] == {"s3:GetObject"}
    assert new_actions[key] == {
        "s3:GetObject",
        "iam:CreatePolicyVersion",
    }

    old_trust = extract_trust_edges(str(ROOT / "fixtures/v1/roles.tf"))
    new_trust = extract_trust_edges(str(ROOT / "fixtures/v2/roles.tf"))

    assert (
        "arn:aws:iam::111122223333:user/developer",
        "role:app-role",
    ) in old_trust

    assert (
        "arn:aws:iam::111122223333:role/admin-role",
        "role:app-role",
    ) in new_trust

    print("PASS: Real Terraform fixtures parsed correctly.")
    print("PASS: Added IAM action identified.")
    print("PASS: Trust relationship change identified.")


if __name__ == "__main__":
    test_real_fixture_comparison()
