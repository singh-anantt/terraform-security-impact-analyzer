
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from role_permission_mapper import map_role_policy_actions, map_role_permissions


REQUIRED_ACTIONS = {
    "iam:CreatePolicyVersion",
    "iam:SetDefaultPolicyVersion",
}


def check_policy_version_risk(directory):
    findings = []
    mappings = map_role_policy_actions(directory)
    permissions_by_role = map_role_permissions(directory)

    for role, actions in permissions_by_role.items():
        if not REQUIRED_ACTIONS.issubset(actions):
            continue

        policies = sorted({
            mapping["policy"]
            for mapping in mappings
            if mapping["role"] == role
            and set(mapping["actions"]) & REQUIRED_ACTIONS
        })

        findings.append({
            "role": role,
            "policy": policies[0] if len(policies) == 1 else ", ".join(policies),
            "finding": "Potential managed-policy version modification",
            "evidence": sorted(REQUIRED_ACTIONS),
            "confidence": (
                "Candidate only; resource scope and AWS controls "
                "remain unverified"
            ),
        })

    return findings


if __name__ == "__main__":
    for version in ["fixtures/v1", "fixtures/v2"]:
        print(f"\n=== {version} ===")

        findings = check_policy_version_risk(version)

        if not findings:
            print("No candidate found by this rule.")

        for finding in findings:
            print(f"Role: {finding['role']}")
            print(f"Policy: {finding['policy']}")
            print(f"Finding: {finding['finding']}")
            print(f"Evidence: {finding['evidence']}")
