
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from policy_version_checker import check_policy_version_risk


def main():
    baseline = check_policy_version_risk(
        ROOT / "fixtures" / "risk_v1"
    )
    upgraded = check_policy_version_risk(
        ROOT / "fixtures" / "risk_v2"
    )

    assert not baseline, (
        "Baseline should not trigger the policy-version rule."
    )
    assert upgraded, (
        "The risky policy should trigger the policy-version rule."
    )

    for finding in upgraded:
        assert finding["policy"] == "example"
        assert finding["role"] == "app_role"

    print("PASS: Baseline has no candidate finding.")
    print("PASS: Risky policy is identified by policy.")
    print("PASS: Finding is associated with the expected role.")


if __name__ == "__main__":
    main()
