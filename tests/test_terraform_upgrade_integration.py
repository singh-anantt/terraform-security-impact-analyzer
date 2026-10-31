from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from role_permission_mapper import map_role_permissions
from graph_builder import find_path, compare_graphs
from trust_graph import extract_trust_edges, compare_trust_edges


def test_terraform_upgrade_changes():
    old_dir = ROOT / "fixtures" / "v1"
    new_dir = ROOT / "fixtures" / "v2"

    old_permissions = map_role_permissions(str(old_dir))
    new_permissions = map_role_permissions(str(new_dir))

    assert old_permissions["app_role"] == {"s3:GetObject"}
    assert new_permissions["app_role"] == {
        "s3:GetObject",
        "iam:CreatePolicyVersion",
    }

    added_permissions = (
        new_permissions["app_role"] - old_permissions["app_role"]
    )
    assert added_permissions == {"iam:CreatePolicyVersion"}

    old_trust = extract_trust_edges(str(old_dir / "roles.tf"))
    new_trust = extract_trust_edges(str(new_dir / "roles.tf"))
    trust_changes = compare_trust_edges(old_trust, new_trust)

    assert trust_changes["added"] == [
        (
            "arn:aws:iam::111122223333:role/admin-role",
            "role:app-role",
        )
    ]
    assert trust_changes["removed"] == [
        (
            "arn:aws:iam::111122223333:user/developer",
            "role:app-role",
        )
    ]


def test_terraform_trust_edges_work_with_graph_analysis():
    old_dir = ROOT / "fixtures" / "v1"
    new_dir = ROOT / "fixtures" / "v2"

    old_edges = extract_trust_edges(str(old_dir / "roles.tf"))
    new_edges = extract_trust_edges(str(new_dir / "roles.tf"))

    changes = compare_graphs(old_edges, new_edges)

    admin_trust = (
        "arn:aws:iam::111122223333:role/admin-role",
        "role:app-role",
    )
    developer_trust = (
        "arn:aws:iam::111122223333:user/developer",
        "role:app-role",
    )

    assert admin_trust in changes["added_edges"]
    assert developer_trust in changes["removed_edges"]

    assert find_path(
        new_edges,
        "arn:aws:iam::111122223333:role/admin-role",
        "role:app-role",
    ) == [
        "arn:aws:iam::111122223333:role/admin-role",
        "role:app-role",
    ]

    assert find_path(
        old_edges,
        "arn:aws:iam::111122223333:role/admin-role",
        "role:app-role",
    ) is None
