from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from policy_version_checker import check_policy_version_risk


def test_safe_permissions_are_not_flagged():
    assert check_policy_version_risk(ROOT / "fixtures" / "v1") == []


def test_incomplete_action_pair_is_not_flagged():
    assert check_policy_version_risk(ROOT / "fixtures" / "v2") == []


def test_both_required_actions_produce_candidate_finding():
    findings = check_policy_version_risk(ROOT / "fixtures" / "risk_v2")

    assert len(findings) == 1
    assert findings[0]["role"] == "app_role"
    assert findings[0]["policy"] == "example"


def test_actions_split_across_policies_trigger_role_level_candidate():
    findings = check_policy_version_risk(
        ROOT / "fixtures" / "split_policy_test"
    )

    assert len(findings) == 1
    assert findings[0]["role"] == "app_role"
    assert findings[0]["policy"] == "create_version, set_default"
    assert set(findings[0]["evidence"]) == {
        "iam:CreatePolicyVersion",
        "iam:SetDefaultPolicyVersion",
    }
