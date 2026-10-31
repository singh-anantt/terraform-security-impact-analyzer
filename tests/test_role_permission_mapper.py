
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from role_permission_mapper import map_role_permissions


def main():
    old = map_role_permissions(str(ROOT / "fixtures/v1"))
    new = map_role_permissions(str(ROOT / "fixtures/v2"))

    assert old["app_role"] == {"s3:GetObject"}
    assert new["app_role"] == {
        "s3:GetObject",
        "iam:CreatePolicyVersion",
    }

    added = new["app_role"] - old["app_role"]
    removed = old["app_role"] - new["app_role"]

    assert added == {"iam:CreatePolicyVersion"}
    assert removed == set()

    print("PASS: Baseline role permissions verified.")
    print("PASS: New role permission identified.")
    print("PASS: No false removal of existing permissions.")


if __name__ == "__main__":
    main()
