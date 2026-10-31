
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

    baseline_keys = {
        (item["role"], item["policy"], item["finding"])
        for item in baseline
    }
    upgraded_keys = {
        (item["role"], item["policy"], item["finding"])
        for item in upgraded
    }

    introduced = upgraded_keys - baseline_keys

    assert not baseline, "Baseline should have no candidate finding."
    assert upgraded, "Expected the risky fixture to trigger a finding."
    assert introduced, "Expected a candidate finding introduced by upgrade."

    print("PASS: Baseline has no candidate finding.")
    print("PASS: Risky policy triggers the candidate rule.")
    print("PASS: Candidate is introduced by the upgrade.")


if __name__ == "__main__":
    main()
