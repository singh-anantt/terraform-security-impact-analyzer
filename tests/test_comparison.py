
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from compare_iam import extract_actions


def compare(old_actions, new_actions):
    return {
        "added": sorted(new_actions - old_actions),
        "removed": sorted(old_actions - new_actions),
    }


def test_no_change():
    old = {"s3:GetObject"}
    new = {"s3:GetObject"}
    assert compare(old, new) == {"added": [], "removed": []}


def test_permission_added():
    old = {"s3:GetObject"}
    new = {"s3:GetObject", "iam:CreatePolicyVersion"}
    assert compare(old, new)["added"] == ["iam:CreatePolicyVersion"]


def test_permission_removed():
    old = {"s3:GetObject", "s3:PutObject"}
    new = {"s3:GetObject"}
    assert compare(old, new)["removed"] == ["s3:PutObject"]


if __name__ == "__main__":
    test_no_change()
    test_permission_added()
    test_permission_removed()
    print("All 3 comparison tests passed!")
