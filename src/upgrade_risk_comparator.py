
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from policy_version_checker import check_policy_version_risk


def finding_key(finding):
    return (
        finding["role"],
        finding["policy"],
        finding["finding"],
    )


def compare_upgrade(old_directory, new_directory):
    old_findings = {
        finding_key(item): item
        for item in check_policy_version_risk(old_directory)
    }

    new_findings = {
        finding_key(item): item
        for item in check_policy_version_risk(new_directory)
    }

    return {
        "introduced": [
            new_findings[key]
            for key in sorted(new_findings.keys() - old_findings.keys())
        ],
        "removed": [
            old_findings[key]
            for key in sorted(old_findings.keys() - new_findings.keys())
        ],
        "unchanged": [
            new_findings[key]
            for key in sorted(new_findings.keys() & old_findings.keys())
        ],
    }


if __name__ == "__main__":
    result = compare_upgrade(
        ROOT / "fixtures" / "risk_v1",
        ROOT / "fixtures" / "risk_v2",
    )

    print("=== UPGRADE RISK COMPARISON ===")

    for category in ("introduced", "removed", "unchanged"):
        print(f"\n{category.title()} findings:")

        if not result[category]:
            print("  None")

        for finding in result[category]:
            print(
                f"  Role: {finding['role']}, "
                f"Policy: {finding['policy']}, "
                f"Finding: {finding['finding']}"
            )

    print(
        "\nNote: These are heuristic candidate findings, "
        "not confirmed exploitable paths."
    )

