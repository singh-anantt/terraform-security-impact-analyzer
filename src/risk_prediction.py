from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))

from policy_version_checker import check_policy_version_risk


def predict_introduced_policy_risk(old_directory, new_directory):
    old_findings = {
        (item["role"], item["policy"], item["finding"])
        for item in check_policy_version_risk(old_directory)
    }

    new_findings = {
        (item["role"], item["policy"], item["finding"])
        for item in check_policy_version_risk(new_directory)
    }

    return bool(new_findings - old_findings)


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]

    old_dir = root / "fixtures" / "risk_v1"
    new_dir = root / "fixtures" / "risk_v2"

    prediction = predict_introduced_policy_risk(old_dir, new_dir)

    print("E03 predicted new risk:", prediction)
